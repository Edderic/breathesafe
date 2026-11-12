"""Prepare an isolated, unapproved upper-neck-mask trial from saved captures."""
import argparse
import copy
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

MODEL_HASH='c6748b1253a99067ef71f7e26ca71096cd449baefa8f101900ea23016507e0e0'


def digest(data): return hashlib.sha256(data).hexdigest()


def expand_mask(original, categories):
    """Preserve reviewed pixels; add bounded body-skin connected to the head."""
    original=np.asarray(original)>=128;categories=np.asarray(categories)
    if original.shape!=categories.shape or original.ndim!=2 or not original.any():
        raise ValueError('Matching nonempty two-dimensional head mask and categories required.')
    y,x=np.nonzero(original);left,right=int(x.min()),int(x.max())+1;top,bottom=int(y.min()),int(y.max())+1
    width=right-left;height=bottom-top
    yy,xx=np.indices(original.shape)
    roi=(xx>=left)&(xx<right)&(yy>=top+.4*height)&(yy<min(original.shape[0],bottom+.15*height))
    candidate=(categories==2)&roi
    labels,_=ndimage.label(original|candidate)
    attached=np.unique(labels[original]);attached=attached[attached!=0]
    expanded=original|(candidate&np.isin(labels,attached))
    return (expanded.astype(np.uint8)*255),{
        'head_bbox':[left,top,right,bottom],
        'proposal_roi':[left,int(np.ceil(top+.4*height)),right,min(original.shape[0],int(np.ceil(bottom+.15*height)))],
        'added_pixels':int((expanded&~original).sum()),'original_pixels':int(original.sum()),
        'policy':'preserve_original_union_connected_body_skin_in_lower_60pct_head_bbox_plus_15pct_height_below',
    }


def prepare(source, root, model):
    import mediapipe as mp
    from .capture_quality import capture_quality
    source=Path(source).resolve();root=Path(root).resolve();model=Path(model).resolve()
    if mp.__version__!='0.10.32' or digest(model.read_bytes())!=MODEL_HASH:
        raise ValueError('Use pinned MediaPipe Python 0.10.32 and cached multiclass model.')
    raw=(source/'session.json').read_bytes();old=json.loads(raw)
    if len(old['captures'])!=61 or any(c.get('mask_approved') is not True for c in old['captures']):
        raise ValueError('Source needs all 61 approved original captures.')
    identity=uuid.uuid4().hex;out=root/identity
    if source==root or source in out.parents:raise ValueError('Write the trial outside its source session.')
    state={k:copy.deepcopy(old[k]) for k in ('version','capture_context')}
    state.update(id=identity,created_at=datetime.now(timezone.utc).isoformat(),status='capturing',stage=None,error=None,result=None,captures=[])
    state['capture_context'].update(group='upper-neck-mask-trial',conditions='Same source photos; expanded upper-neck masks; individual review required')
    state['mask_experiment']={'version':'bounded-upper-neck-v1','source_session_id':old['id'],
        'source_session_sha256':digest(raw),'model_sha256':MODEL_HASH,'review_required':True,
        'instructions':'Preserve chin, under-jaw and upper-neck skin; exclude shoulders, clothing, hands and background. Review every frame individually. No new photos needed.'}
    def save():
        temporary=out/'session.json.tmp';temporary.write_text(json.dumps(state,indent=2,allow_nan=False)+'\n');temporary.replace(out/'session.json')
    options=mp.tasks.vision.ImageSegmenterOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(model),delegate=mp.tasks.BaseOptions.Delegate.CPU),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,output_category_mask=True)
    previews=[]
    with mp.tasks.vision.ImageSegmenter.create_from_options(options) as segmenter:
        out.mkdir(mode=0o700,parents=True);save()
        for c in sorted(old['captures'],key=lambda row:row['slot']):
            paths=[]
            for key,hash_key in [('image','sha256'),('mask','mask_sha256')]:
                path=(source/c[key]).resolve()
                if source not in path.parents or digest(path.read_bytes())!=c[hash_key]:raise ValueError('Source capture path or hash changed.')
                paths.append(path)
            image=Image.open(paths[0]).convert('RGB');original=Image.open(paths[1]).convert('L')
            result=segmenter.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.asarray(image)))
            categories=Image.fromarray(result.category_mask.numpy_view().squeeze(axis=2).astype(np.uint8)).resize(image.size,Image.Resampling.NEAREST)
            proposed,info=expand_mask(original,categories);mask=Image.fromarray(proposed)
            (out/(c['slot']+'.png')).write_bytes(paths[0].read_bytes());mask.save(out/(c['slot']+'-mask.png'))
            row=copy.deepcopy(c);row.update(image=c['slot']+'.png',mask=c['slot']+'-mask.png',mask_approved=False,
                mask_sha256=digest((out/(c['slot']+'-mask.png')).read_bytes()),capture_quality=capture_quality(image,mask),
                mask_provenance={'sdk_version':mp.__version__,'model_sha256':MODEL_HASH,'selected_categories':[1,3],
                    'bounded_added_category':2,'delegate':'CPU','review_status':'unreviewed_neck_proposal',
                    'correction':'preserved_source_reviewed_mask_plus_bounded_connected_body_skin',
                    'source_mask_sha256':c['mask_sha256'],'source_image_sha256':c['sha256'],**info})
            state['captures'].append(row);save()
            # Contact sheet: green original mask, orange newly proposed pixels.
            preview=np.asarray(image).copy().astype(float);base=np.asarray(original)>=128;added=(proposed>0)&~base
            preview[base]=preview[base]*.65+np.array([0,220,100])*.35
            preview[added]=preview[added]*.4+np.array([255,150,0])*.6
            thumb=Image.fromarray(preview.astype(np.uint8));thumb.thumbnail((320,180))
            tile=Image.new('RGB',(320,205),'white');tile.paste(thumb,(0,20));ImageDraw.Draw(tile).text((5,3),c['slot']+' +'+str(info['added_pixels'])+' px',fill='black');previews.append(tile)
            print(c['slot'],info['added_pixels'],'added pixels',flush=True)
    sheet=Image.new('RGB',(320*5,205*((len(previews)+4)//5)),'white')
    for i,tile in enumerate(previews):sheet.paste(tile,((i%5)*320,(i//5)*205))
    sheet.save(out/'mask-proposals.jpg')
    if (source/'session.json').read_bytes()!=raw:raise ValueError('Source session changed during preparation.')
    print('Prepared unapproved trial:',identity,flush=True)
    return state


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('source','root','model'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();prepare(args.source,args.root,args.model)
