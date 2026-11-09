"""Apply the selected Gaussian smoothing to approved neck-inclusive reconstruction."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree

from .gaussian_volume import source_samples, implicit_grid, filtered_field, extract, surface_metrics, display_mesh, photo_overlay
from .photogrammetry_trial import digest


def coverage(mesh, camera, menton, span):
    axis=np.array(camera['R'])[1]
    below=mesh.triangles_center@axis > np.array(menton)@axis+.03*span
    return {'definition':'triangle center below fixed menton camera height plus 0.03 eye proxy; geometric slab, not anatomical segmentation',
            'triangles':int(below.sum()),'area_reconstruction_units_squared':float(mesh.area_faces[below].sum())}


def run(args):
    folder,trial,reference,out=map(Path,(args.session,args.trial,args.reference,args.out))
    state=json.loads((folder/'session.json').read_text());base=json.loads((trial/'report.json').read_text())
    source=json.loads((trial/'automatic-routes.json').read_text());old=json.loads((reference/'report.json').read_text())
    raw_path=folder/state['result']['full_mesh']
    if digest(raw_path)!=base['raw_sha256'] or not all(c.get('mask_approved') for c in state['captures']):
        raise ValueError('Expected unchanged approved expanded-neck reconstruction')
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must be new or empty')
    out.mkdir(parents=True,exist_ok=True)
    raw=trimesh.load(raw_path,process=False);span=base['eye_proxy_span'];front=state['result']['cameras'][state['result']['frontal_camera_key']]
    samples,normals,quality=source_samples(raw,span);tree=cKDTree(samples)
    # Source order matches the existing checked style-specific guide recipe.
    menton=source['points'][3]['surface_point']
    raw_coverage=coverage(raw,front,menton,span)
    below=raw.triangles_center@np.array(front['R'])[1] > np.array(menton)@np.array(front['R'])[1]+.03*span
    proof=[];tiles=[]
    selected={'front','turn_11','turn_22','turn_35','turn_48','turn_55'}
    for i,capture in enumerate(sorted(state['captures'],key=lambda c:c['slot'])):
        image_path=folder/capture['image'];mask_path=folder/capture['mask']
        if digest(image_path)!=capture['sha256'] or digest(mask_path)!=capture['mask_sha256']:
            raise ValueError('Capture/mask changed')
        image=np.array(Image.open(image_path).convert('RGB'));mask=np.array(Image.open(mask_path).convert('L'))>=128
        tinted=image.copy();tinted[mask]=(tinted[mask]*.65+np.array([0,220,100])*.35).astype(np.uint8)
        tile=Image.fromarray(tinted);tile.thumbnail((320,180));card=Image.new('RGB',(320,205),'white');card.paste(tile,(0,22));ImageDraw.Draw(card).text((4,4),capture['slot'],fill='black');tiles.append(card)
        if capture['slot'] in selected:
            filename=capture['slot']+'-neck-input.jpg';card.save(out/filename)
            proof.append({'slot':capture['slot'],'file':filename})
    sheet=Image.new('RGB',(1600,205*((len(tiles)+4)//5)),'white')
    for i,tile in enumerate(tiles):sheet.paste(tile,((i%5)*320,(i//5)*205))
    sheet.save(out/'all-neck-masks.jpg')
    target_step=next(v['voxel_over_eye_span'] for v in old['variants'] if v['id']=='grid-224-sigma-0.03')
    max_extent=(samples.max(axis=0)-samples.min(axis=0)).max()+2*(.1+.06*4)*span
    resolution=int(round(max_extent/(target_step*span)))+1
    report={'version':'neck_gaussian_volume_v1','session_id':state['id'],'units':'reconstruction_unit',
            'source_sha256':digest(raw_path),'session_sha256':digest(folder/'session.json'),
            'reference_report_sha256':digest(reference/'report.json'),'eye_proxy_span':span,
            'raw_label':'Raw reconstruction with upper-neck masks',
            'source_capture_count':len(state['captures']),'input_photos':proof,'contact_sheet':'all-neck-masks.jpg',
            'neck_coverage':{'raw':raw_coverage,'quality_source_triangles_below_menton':int((quality&below).sum()),'variants':{}},
            'target_voxel_over_eye_span':target_step,'field':'local oriented point-to-plane approximation, not a watertight signed distance',
            'support_policy':'source proximity only; smoothing does not establish anatomical or photographic support',
            'variants':[]}
    data={'raw':display_mesh(raw,front),'variants':[],'report':report}
    slots=['turn_11','turn_22','turn_48'];cameras=[state['result']['cameras']['registered:'+slot+'.png'] for slot in slots]
    nose=next(p['point'] for p in state['result']['projected_points'] if p['index']==4 and p['status']=='ok')
    report['raw_photos']=photo_overlay(folder,slots,cameras,raw,{'nose_point':nose,'span':span},out,'raw')
    print('Neck source',raw_coverage,'quality triangles',int((quality&below).sum()),'target grid',resolution,flush=True)
    start=time.monotonic();field,weight,nearest,origin,step=implicit_grid(samples,normals,span,resolution,.06*span)
    print('Grid built',field.shape,'in',round(time.monotonic()-start,1),'s',flush=True)
    for sigma in (0.,.03):
        label=f'neck-grid-{resolution}-sigma-{sigma:g}'
        blurred,density=filtered_field(field,weight,sigma*span/step)
        mesh=extract(blurred,(density>.25)&(nearest<span*.1),origin,step)
        mesh.export(out/(label+'.ply'))
        record={'id':label,'sigma_over_eye_span':sigma,'voxel_over_eye_span':step/span,'grid_shape':list(field.shape),
                'sigma_voxels':sigma*span/step,'mesh_sha256':digest(out/(label+'.ply')),
                'metrics':surface_metrics(raw,mesh,samples,tree,span),
                'measurements':{'status':'not accepted; all-photo correspondence review is separate'},
                'photos':photo_overlay(folder,slots,cameras,mesh,{'nose_point':nose,'span':span},out,label)}
        record['neck_coverage']=coverage(mesh,front,menton,span)
        report['neck_coverage']['variants'][label]=record['neck_coverage']
        report['variants'].append(record);data['variants'].append({'label':label,'mesh_file':label+'.ply',**display_mesh(mesh,front)})
        (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
        print(label,'neck',record['neck_coverage'],flush=True)
    report['algorithm_sha256']=digest(__file__);report['volume_implementation_sha256']=digest(Path(__file__).with_name('gaussian_volume.py'))
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    (out/'comparison.html').write_text(Path(__file__).with_name('gaussian_volume.html').read_text().replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(out/'comparison.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('session','trial','reference','out'):p.add_argument('--'+key,required=True)
    run(p.parse_args())
