"""Prepare local crop inputs for all approved registered photos, including neck views."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from .photogrammetry_trial import digest


def prepare(args):
    from .webcam_reconstruction import detect
    folder,out,face_folder=map(Path,(args.session,args.out,args.face_session))
    state=json.loads((folder/'session.json').read_text())
    original=json.loads((face_folder/'session.json').read_text())
    original_captures={c['slot']:c for c in original['captures']}
    cache=json.loads(Path(args.cache).read_text())
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must be new or empty')
    out.mkdir(parents=True,exist_ok=True)
    manifest={'version':'all_registered_crop_inputs_v1','session_id':state['id'],'source_session_sha256':digest(folder/'session.json'),
              'source_face_session':original['id'],'views':[],'excluded':[]}
    for capture in sorted(state['captures'],key=lambda c:c['slot']):
        slot=capture['slot'];path=folder/capture['image']
        if not capture.get('mask_approved') or capture.get('mirrored') is not False:
            raise ValueError('Expected approved unmirrored source captures')
        if 'registered:'+slot+'.png' not in state['result']['cameras']:
            manifest['excluded'].append({'slot':slot,'reason':'no_original_registered_camera'});continue
        if path.resolve().parent!=folder.resolve() or digest(path)!=capture['sha256']:
            raise ValueError('Capture path/hash changed')
        sha=capture['sha256']
        if slot in cache and cache[slot]['sha256']==sha:
            record=cache[slot];record['crop_source']='cached_mediapipe'
        else:
            try:
                landmarks,provenance=detect(path)
                record={'sha256':sha,'landmarks':landmarks,'detector':provenance,'crop_source':'mediapipe_original_photo'}
            except ValueError as error:
                source=original_captures[slot]
                if source['sha256']!=sha or not source.get('mask_approved'):
                    raise ValueError('Fallback head-mask source differs') from error
                mask_path=face_folder/source['mask']
                if digest(mask_path)!=source['mask_sha256']:
                    raise ValueError('Fallback head mask changed')
                mask=np.asarray(Image.open(mask_path).convert('L'))>=128
                y,x=np.nonzero(mask)
                if not len(x):raise ValueError('Empty fallback head mask')
                record={'sha256':sha,'initial_bbox_pixels':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],
                        'crop_source':'approved_original_head_mask_fallback','fallback_reason':str(error),
                        'source_mask_sha256':source['mask_sha256']}
        cache[slot]=record
        with Image.open(path) as im:size=im.size
        manifest['views'].append({'slot':slot,'sha256':sha,'image_size':list(size),'crop_source':record['crop_source'],
                                  'capture_height':capture.get('capture_height'),
                                  'neck_mask_sha256':capture['mask_sha256']})
        (out/'landmarks.json').write_text(json.dumps(cache,indent=2))
        (out/'report.json').write_text(json.dumps(manifest,indent=2))
        print(slot,record['crop_source'],flush=True)
    manifest['algorithm_sha256']=digest(__file__)
    (out/'report.json').write_text(json.dumps(manifest,indent=2))
    print('Prepared',len(manifest['views']),'registered photos;',len(manifest['excluded']),'excluded',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('session','face-session','cache','out'):p.add_argument('--'+key,required=True)
    prepare(p.parse_args())
