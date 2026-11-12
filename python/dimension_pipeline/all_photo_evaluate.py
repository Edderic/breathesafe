"""All-photo automatic guide/neck coverage with explicit network-crop support.

Fixed photogrammetry cameras; bounded deterministic pair consensus. Learned
correspondences and geometric support are diagnostics, not anatomical acceptance.
"""
import argparse
import copy
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree

from .flame_open import load_model
from .flame_mapping import topology_id
from .flame_photo_fit import TRAIN
from .gaussian_validation import eligible_faces, recipe
from .gaussian_volume import source_samples
from .photogrammetry_trial import camera_arrays, dlt, digest


def project_all(cameras, point):
    p=np.array([np.asarray(c['R'])@point+np.asarray(c['t']) for c in cameras])
    xy=p[:,:2]/np.maximum(p[:,2,None],1e-12)
    factor=1+np.array([c.get('k',0) for c in cameras])*np.sum(xy*xy,axis=1)
    return xy*factor[:,None]*np.array([[c['fx'],c['fy']] for c in cameras])+np.array([[c['cx'],c['cy']] for c in cameras]),p[:,2]


def triangulate_bounded(cameras, observations, maximum_pairs=96, threshold=6.):
    normalized,projections,centers=camera_arrays(cameras,observations)
    output=[]
    for j in range(observations.shape[1]):
        obs=observations[:,j]
        valid=np.isfinite(obs).all(axis=1)
        pairs=list(__import__('itertools').combinations(np.flatnonzero(valid),2))
        if len(pairs)>maximum_pairs:
            rng=np.random.default_rng(20+j)
            pairs=[pairs[i] for i in sorted(rng.choice(len(pairs),maximum_pairs,replace=False))]
        best=None
        def errors(point):
            if not np.isfinite(point).all():return np.full(len(cameras),np.inf)
            xy,z=project_all(cameras,point)
            error=np.linalg.norm(xy-obs,axis=1)
            return np.where(valid&(z>0),error,np.inf)
        for pair in pairs:
            ids=list(pair);q=dlt(projections[ids],normalized[ids,j]);error=errors(q);keep=error<=threshold
            score=(int(keep.sum()),-float(np.minimum(error,threshold).sum()))
            if best is None or score>best[0]:best=(score,q,keep)
        if best is None or best[2].sum()<3:
            output.append({'status':'insufficient_consensus','valid_input_views':int(valid.sum())});continue
        q,keep=best[1:]
        for _ in range(3):
            q=dlt(projections[keep],normalized[keep,j]);error=errors(q);updated=error<=threshold
            if updated.sum()<3 or np.array_equal(updated,keep):keep=updated;break
            keep=updated
        rays=q-centers[keep];rays/=np.maximum(np.linalg.norm(rays,axis=1)[:,None],1e-12)
        angle=float(np.degrees(np.arccos(np.clip(rays@rays.T,-1,1))).max()) if len(rays) else 0.
        output.append({'status':'consistent' if keep.sum()>=3 and angle>=3 else 'insufficient_parallax_or_consensus',
            'point':q.tolist(),'inlier_views':np.flatnonzero(keep).tolist(),'valid_input_views':int(valid.sum()),
            'maximum_ray_angle_degrees':angle,'reprojection_rms_pixels':float(np.sqrt(np.mean(error[keep]**2))) if keep.any() else None})
    return output


def attach_batched(mesh, records, cameras, observations, span, quality):
    ids=[i for i,r in enumerate(records) if r['status']=='consistent']
    if not ids:return
    q,distance,tri=trimesh.proximity.closest_point(mesh,np.array([records[i]['point'] for i in ids]))
    counts={i:[] for i in ids};eligible=[]
    for j,i in enumerate(ids):
        r=records[i];r['surface_distance_over_eye_span']=float(distance[j]/span)
        if distance[j]>.04*span:r['status']='too_far_from_surface'
        elif not quality[tri[j]]:r['status']='rejected_triangle_quality_or_proximity'
        else:eligible.append((j,i))
    for v,camera in enumerate(cameras):
        selected=[]
        for j,i in eligible:
            if v not in records[i]['inlier_views']:continue
            xy,z=project_all([camera],q[j])
            if z[0]>0 and np.linalg.norm(xy[0]-observations[v,i])<=6:selected.append((j,i))
        if not selected:continue
        center=-np.asarray(camera['R']).T@camera['t']
        xyz=q[[j for j,i in selected]];rays=xyz-center;length=np.linalg.norm(rays,axis=1)
        hit,ray,_=mesh.ray.intersects_location(np.tile(center,(len(xyz),1)),rays/length[:,None],multiple_hits=False)
        hit_distance=np.linalg.norm(hit-center,axis=1)
        visible=np.abs(hit_distance-length[ray])<span*1e-4
        for index in ray[visible]:counts[selected[index][1]].append(v)
    for j,i in eligible:
        r=records[i];r['visible_surface_views']=counts[i]
        if len(counts[i])<3:r['status']='insufficient_visible_surface_views';continue
        r.update(status='supported',surface_point=q[j].tolist(),attachment={'kind':'barycentric','triangle_index':int(tri[j]),
            'weights':trimesh.triangles.points_to_barycentric(mesh.triangles[tri[j]][None],q[j][None])[0].tolist()})


def observation_gate(xy,crop,width,height,mask):
    finite=np.isfinite(xy).all(axis=1)
    inside=finite&(xy[:,0]>=0)&(xy[:,0]<width)&(xy[:,1]>=0)&(xy[:,1]<height)
    crop_ok=inside&(xy[:,0]>=crop[0])&(xy[:,0]<crop[2])&(xy[:,1]>=crop[1])&(xy[:,1]<crop[3])
    safe=np.nan_to_num(xy).clip([0,0],[width-1,height-1]).astype(int)
    mask_ok=inside&mask[safe[:,1],safe[:,0]]
    return inside,crop_ok,mask_ok


def run(args):
    folder,predictions,trial,neck,out=map(Path,(args.session,args.predictions,args.trial,args.neck,args.out))
    state=json.loads((folder/'session.json').read_text());base=json.loads((trial/'report.json').read_text())
    neural=json.loads((predictions/'report.json').read_text());neck_report=json.loads((neck/'report.json').read_text())
    draft=json.loads(Path(args.measurements).read_text());template,_,faces,model=load_model(args.model)
    if draft['model_sha256']!=model['model_sha256'] or draft['topology_id']!=topology_id(faces):raise ValueError('Guide model differs')
    raw_path=folder/state['result']['full_mesh']
    if digest(raw_path)!=base['raw_sha256'] or digest(raw_path)!=neck_report['source_sha256']:raise ValueError('Raw mesh changed')
    attachments,named,routes=recipe(draft)
    below=np.flatnonzero((template[:,1]<-.089)&(template[:,2]>-.045))
    descriptors=[{'kind':'guide','name':next((n for n,i in named.items() if i==j),f'route_control_{j}')} for j in range(len(attachments))]
    descriptors += [{'kind':'below_menton_vertex','vertex_id':int(v)} for v in below]
    triangles=faces[[a['triangle_index'] for a in attachments]];weights=np.array([a['weights'] for a in attachments])
    captures={c['slot']:c for c in state['captures']};observations=[];raw_observations=[];cameras=[];slots=[];masks=[];crop_records=[]
    for view in neural['views']:
        slot=view['slot'];capture=captures[slot];path=folder/capture['image'];mask_path=folder/capture['mask']
        if digest(path)!=view['image_sha256'] or digest(path)!=capture['sha256'] or digest(mask_path)!=capture['mask_sha256']:
            raise ValueError('Input pixels or masks changed')
        camera=state['result']['cameras'].get('registered:'+slot+'.png')
        if camera is None:continue
        array=np.load(predictions/(slot+'.npz'),allow_pickle=False);xy=array['vertex_coord']
        predicted=np.vstack([np.einsum('ij,ijk->ik',weights,xy[triangles]),xy[below]])
        mask=np.asarray(Image.open(mask_path).convert('L'))>=128
        expanded=cv2.dilate(mask.astype(np.uint8),np.ones((7,7),np.uint8))>0
        inside,crop_ok,mask_ok=observation_gate(predicted,array['crop'],camera['width'],camera['height'],expanded)
        valid=inside&crop_ok&mask_ok;filtered=predicted.copy();filtered[~valid]=np.nan
        observations.append(filtered);raw_observations.append(predicted);cameras.append(camera);slots.append(slot);masks.append(mask)
        crop_records.append({'slot':slot,'network_crop_pixels':array['crop'].tolist(),'image_sha256':capture['sha256'],
            'prediction_sha256':digest(predictions/(slot+'.npz')),'mask_sha256':capture['mask_sha256'],
            'outside_image_count':int((~inside).sum()),'outside_network_crop_count':int((~crop_ok).sum()),
            'outside_dilated_neck_mask_count':int((~mask_ok).sum()),'valid_candidate_count':int(valid.sum())})
    observations=np.array(observations);raw_observations=np.array(raw_observations)
    out.mkdir(parents=True,exist_ok=False)
    raw=trimesh.load(raw_path,process=False);span=base['eye_proxy_span'];samples,_,_=source_samples(raw,span);tree=cKDTree(samples)
    selected=next(v for v in neck_report['variants'] if v['sigma_over_eye_span']==.03)
    selected_path=neck/(selected['id']+'.ply')
    if digest(selected_path)!=selected['mesh_sha256']:raise ValueError('Selected neck surface changed')
    smoothed=trimesh.load(selected_path,process=False)
    raw_quality=eligible_faces(raw,span,tree);selected_quality=eligible_faces(smoothed,span,tree)
    report={'version':'all_photo_neck_coverage_v1','session_id':state['id'],'image_count':len(slots),'capture_count':len(state['captures']),
        'source_sha256':digest(raw_path),'selected_sha256':digest(selected_path),'selected_surface':selected['id'],
        'guide_sha256':digest(args.measurements),'model':model,'neural_report_sha256':digest(predictions/'report.json'),
        'descriptors':descriptors,'input_views':crop_records,'fixed_cameras':dict(zip(slots,cameras)),'runs':{},
        'policy':{'maximum_pair_hypotheses':96,'pair_seed':20,'reprojection_pixels':6,'minimum_visible_views':3,
                  'minimum_ray_angle_degrees':3,'maximum_surface_distance_over_eye_span':.04,
                  'network_crop_gate':True,'source_neck_mask_dilation_pixels':3},
        'interpretation':'model-derived correspondence and source-support diagnostics, not anatomical or physical accuracy'}
    for label,indices in [('nine_views',[i for i,s in enumerate(slots) if s in TRAIN]),('all_views',list(range(len(slots))))]:
        cams=[cameras[i] for i in indices];obs=observations[indices]
        print(label,len(indices),'photos, triangulating',len(descriptors),'candidates',flush=True)
        records=triangulate_bounded(cams,obs)
        attach_batched(raw,records,cams,obs,span,raw_quality)
        selected_records=[]
        for r in records:
            selected_records.append({'status':'consistent','point':r['surface_point'],'inlier_views':r['inlier_views']} if r['status']=='supported' else {'status':'raw_candidate_unsupported'})
        attach_batched(smoothed,selected_records,cams,obs,span,selected_quality)
        summary={}
        for kind in ('guide','below_menton_vertex'):
            summary[kind]={'count':sum(d['kind']==kind for d in descriptors),
                'raw':dict(Counter(r['status'] for r,d in zip(records,descriptors) if d['kind']==kind)),
                'smoothed':dict(Counter(r['status'] for r,d in zip(selected_records,descriptors) if d['kind']==kind))}
        named_rows={n:{'raw':records[i]['status'],'smoothed':selected_records[i]['status'],
                        'raw_visible_views':len(records[i].get('visible_surface_views',[])),
                        'smoothed_visible_views':len(selected_records[i].get('visible_surface_views',[]))} for n,i in named.items()}
        report['runs'][label]={'slots':[slots[i] for i in indices],'summary':summary,'named':named_rows,'raw_points':records,'smoothed_points':selected_records}
        (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
        print(label,json.dumps(summary),flush=True)
    cards=[]
    for slot in ('turn_00','turn_11','turn_22','turn_35','turn_48','turn_55'):
        v=slots.index(slot);image=Image.open(folder/captures[slot]['image']).convert('RGB');draw=ImageDraw.Draw(image)
        draw.rectangle(crop_records[v]['network_crop_pixels'],outline='#2487ed',width=3)
        runs=report['runs']['all_views'];local=runs['slots'].index(slot)
        for j,d in enumerate(descriptors):
            if d['kind']!='below_menton_vertex':continue
            x,y=raw_observations[v,j]
            if not (0<=x<image.width and 0<=y<image.height):continue
            r=runs['smoothed_points'][j]
            color='#18d680' if r['status']=='supported' and local in r.get('visible_surface_views',[]) else '#f29b30'
            if not np.isfinite(observations[v,j]).all():color='#909090'
            draw.ellipse((x-3,y-3,x+3,y+3),fill=color)
        image.thumbnail((900,510));file=slot+'-neck.jpg';image.save(out/file)
        cards.append({'slot':slot,'file':file})
    report['photos']=cards;report['algorithm_sha256']=digest(__file__)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    data={'report':report,'neck_viewer':'../../gaussian-volume/'+neck.name+'/comparison.html'}
    (out/'review.html').write_text(Path(__file__).with_suffix('.html').read_text().replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(out/'review.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('session','predictions','trial','neck','measurements','model','out'):p.add_argument('--'+key,required=True)
    run(p.parse_args())
