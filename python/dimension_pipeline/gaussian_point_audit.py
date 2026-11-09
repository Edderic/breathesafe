"""Per-view threshold sensitivity for model-derived Gaussian point candidates."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import trimesh

from .flame_open import load_model
from .flame_mapping import topology_id
from .gaussian_validation import COLORS, recipe
from .nose_overlays import project_pixels, visible_points
from .photogrammetry_trial import digest


def third_visible_error(errors, visible, inliers, required=3):
    eligible=sorted(float(e) for e,v,i in zip(errors,visible,inliers) if v and i and np.isfinite(e))
    return eligible[required-1] if len(eligible)>=required else None


def run(args):
    root,folder,trial,sweep=map(Path,(args.validation,args.session,args.trial,args.sweep))
    report=json.loads((root/'report.json').read_text())
    state=json.loads((folder/'session.json').read_text())
    source=json.loads((trial/'automatic-routes.json').read_text())
    base=json.loads((trial/'report.json').read_text())
    draft=json.loads(Path(args.measurements).read_text())
    _,_,faces,model=load_model(args.model)
    if digest(args.measurements)!=report['guide_sha256'] or model['model_sha256']!=draft['model_sha256'] or topology_id(faces)!=draft['topology_id']:
        raise ValueError('Guide/model changed')
    if digest(trial/'automatic-routes.json')!=report['source_route_report_sha256']:
        raise ValueError('Source candidates changed')
    _,named,_=recipe(draft)
    point_lookup={p['name']:p for p in draft['points']}
    names=[name for name,i in named.items() if source['points'][i]['status']=='supported']
    raw_points=np.array([source['points'][named[n]]['surface_point'] for n in names])
    cameras=[];targets=[]
    for slot in base['slots']:
        c=state['result']['cameras']['registered:'+slot+'.png']
        if c!=report['fixed_cameras'][slot]:
            raise ValueError('Camera changed')
        path=Path(args.predictions)/(slot+'.npz')
        if digest(path)!=report['prediction_hashes'][slot]['prediction']:
            raise ValueError('Prediction changed')
        xy=np.load(path,allow_pickle=False)['vertex_coord']
        targets.append([np.array(point_lookup[n]['attachment']['weights'])@xy[faces[point_lookup[n]['attachment']['triangle_index']]] for n in names])
        cameras.append(c)
    targets=np.array(targets)
    result={'version':'gaussian_named_point_audit_v1','validation_report_sha256':digest(root/'report.json'),
            'interpretation':'threshold sensitivity of learned correspondence agreement; not physical accuracy',
            'pixel_units':'original 1920x1080 source image pixels','required_views':3,'variants':{}}
    for name in report['variants']:
        path=folder/state['result']['full_mesh'] if name=='raw' else sweep/(name+'.ply')
        if digest(path)!=report['input_mesh_hashes'][name]:
            raise ValueError('Surface changed')
        mesh=trimesh.load(path,process=False)
        q,distance,_=trimesh.proximity.closest_point(mesh,raw_points)
        visible=[];errors=[]
        for v,camera in enumerate(cameras):
            visible.append(visible_points(mesh,camera,q,report['eye_proxy_span']*1e-4))
            errors.append(np.linalg.norm(project_pixels(camera,q)-targets[v],axis=1))
        visible=np.array(visible);errors=np.array(errors);rows={}
        for j,label in enumerate(names):
            inliers=[v in source['points'][named[label]]['inlier_views'] for v in range(len(cameras))]
            threshold=third_visible_error(errors[:,j],visible[:,j],inliers)
            rows[label]={'attempted_surface_point':q[j].tolist(),
                'attachment_shift_over_eye_span':float(distance[j]/report['eye_proxy_span']),
                'minimum_tolerance_for_three_visible_original_inliers_pixels':threshold,
                'visible_original_inlier_counts_by_pixel_tolerance':{str(t):int(np.sum((errors[:,j]<=t)&visible[:,j]&inliers)) for t in (3,6,9,12)},
                'views':[{'slot':slot,'error_pixels':float(errors[v,j]),'visible':bool(visible[v,j]),'original_inlier':inliers[v]} for v,slot in enumerate(base['slots'])],
                'existing_status':report['variants'][name]['named_points'][label]['status']}
        result['variants'][name]=rows
        print(name,'tip minimum tolerance',rows['pronasale']['minimum_tolerance_for_three_visible_original_inliers_pixels'],flush=True)
    result['algorithm_sha256']=digest(__file__)
    (root/'point-audit.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    data={'report':report,'audit':result,'colors':COLORS,'viewer':os.path.relpath(sweep/'comparison.html',root)}
    template=Path(__file__).with_name('gaussian_validation.html').read_text()
    (root/'review.html').write_text(template.replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(root/'review.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('validation','session','trial','sweep','predictions','measurements','model'):
        p.add_argument('--'+key,required=True)
    run(p.parse_args())
