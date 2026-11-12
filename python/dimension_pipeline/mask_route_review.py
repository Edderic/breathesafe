"""Project a saved mask-style loop onto a neck surface and audit its full path.

Geometry-derived proposals never promote model correspondences or inherit review
or calibration. Camera registration maps the old draft's coordinate frame only.
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image
from scipy.spatial import cKDTree

from .gaussian_validation import eligible_faces, recipe
from .gaussian_volume import display_mesh, source_samples
from .nose_overlays import project_pixels
from .photogrammetry_trial import digest


NODE=r'''
const fs=require('fs'),M=require(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8')),g=M.graph(d.mesh),result=[];
for(let i=0;i<d.attachments.length;i++){
 const a=d.attachments[i],b=d.attachments[(i+1)%d.attachments.length];
 if(!a||!b){result.push({status:'missing_control',points:[],length:null});continue}
 const chord=M.distance(M.location(d.mesh,a).point,M.location(d.mesh,b).point);
 try{
  const r=chord<1e-10?{length:0,points:[M.location(d.mesh,a).point],surface_segments:0,edge_fallback_segments:0}:
    M.route(d.mesh,g,[{name:'a',attachment:a},{name:'b',attachment:b}],['a','b'],'surface');
  const detour=chord>1e-10?r.length/chord:1;
  const bad=detour>2||r.length>Math.max(d.original_steps[i]*3,d.span*.15);
  result.push({status:bad?'excessive_detour':'routed',length:r.length,points:r.points,chord_length:chord,
    path_over_chord:detour,surface_segments:r.surface_segments,edge_fallback_segments:r.edge_fallback_segments});
 }catch(e){result.push({status:'disconnected_surface',points:[],length:null,error:e.message})}
}
process.stdout.write(JSON.stringify(result));
'''


def similarity(source,target):
    source=np.asarray(source);target=np.asarray(target)
    x=source-source.mean(0);y=target-target.mean(0)
    u,_,vt=np.linalg.svd(x.T@y);rotation=vt.T@u.T
    if np.linalg.det(rotation)<0:
        vt[-1]*=-1;rotation=vt.T@u.T
    scale=float(np.sum((x@rotation.T)*y)/np.sum(x*x))
    translation=target.mean(0)-scale*(rotation@source.mean(0))
    error=np.linalg.norm(scale*source@rotation.T+translation-target,axis=1)
    return scale,rotation,translation,error


def sample_polyline(points, spacing):
    """Midpoint samples and exact represented lengths, never connect separate paths."""
    samples=[];lengths=[]
    for a,b in zip(points,points[1:]):
        a=np.array(a);b=np.array(b);distance=float(np.linalg.norm(b-a))
        if distance<1e-12:continue
        count=max(1,int(np.ceil(distance/spacing)))
        samples.extend(a+(b-a)*((np.arange(count)+.5)/count)[:,None])
        lengths.extend([distance/count]*count)
    return np.array(samples).reshape(-1,3),np.array(lengths)


def visible_hits(mesh, camera, points, tolerance):
    center=-np.asarray(camera['R']).T@camera['t']
    rays=points-center;distance=np.linalg.norm(rays,axis=1)
    hit,indices,_=mesh.ray.intersects_location(np.tile(center,(len(points),1)),rays/np.maximum(distance[:,None],1e-12),multiple_hits=False)
    visible=np.zeros(len(points),bool)
    visible[indices]=np.abs(np.linalg.norm(hit-center,axis=1)-distance[indices])<=tolerance
    return visible


def source_coverage(points, cameras, masks, candidate, raw, tree, span):
    near=tree.query(points)[0]<=span*.02
    witnesses=[[] for _ in points];directions=[[] for _ in points];angles=np.zeros(len(points))
    done=np.zeros(len(points),bool)
    for v,camera in enumerate(cameras):
        ids=np.flatnonzero(near&~done)
        if not len(ids):break
        q=points[ids];view=q@np.array(camera['R']).T+np.array(camera['t'])
        positive=view[:,2]>0
        ids=ids[positive];q=q[positive]
        if not len(ids):continue
        xy=project_pixels(camera,q);width,height=camera['width'],camera['height']
        inside=(xy[:,0]>=0)&(xy[:,0]<width)&(xy[:,1]>=0)&(xy[:,1]<height)
        pixel=xy.clip([0,0],[width-1,height-1]).astype(int)
        inside &= masks[v][pixel[:,1],pixel[:,0]]
        ids=ids[inside];q=q[inside]
        if not len(ids):continue
        visible=visible_hits(candidate,camera,q,span*1e-4)
        ids=ids[visible];q=q[visible]
        if not len(ids):continue
        visible=visible_hits(raw,camera,q,span*.02)
        center=-np.array(camera['R']).T@camera['t']
        for i,p in zip(ids[visible],q[visible]):
            direction=p-center;direction/=np.linalg.norm(direction)
            if directions[i]:
                angles[i]=max(angles[i],float(np.degrees(np.arccos(np.clip(np.array(directions[i])@direction,-1,1))).max()))
            witnesses[i].append(v);directions[i].append(direction)
            done[i]=len(witnesses[i])>=3 and angles[i]>=3
    return [{'supported':bool(done[i]),'near_quality_source':bool(near[i]),'witness_views':witnesses[i],
             'maximum_witness_angle_degrees':float(angles[i])} for i in range(len(points))]


def run(args):
    folder,source_folder,neck,coverage_folder,out=map(Path,(args.session,args.source_session,args.neck,args.coverage,args.out))
    state=json.loads((folder/'session.json').read_text());source_state=json.loads((source_folder/'session.json').read_text())
    volume=json.loads((neck/'report.json').read_text());photo_report=json.loads((coverage_folder/'report.json').read_text())
    draft=json.loads(Path(args.measurements).read_text());fit=trimesh.load(args.source_fit,process=False)
    if digest(args.source_fit)!=draft['mesh_sha256']:raise ValueError('Source fitted mesh differs from the saved draft')
    if digest(args.measurements)!=photo_report['guide_sha256'] or draft['session_id']!=source_state['id']:raise ValueError('Guide/session changed')
    choices=[p for p in draft['perimeters'] if p['style']==args.style and p['closed']]
    if len(choices)!=1 or len(choices[0]['strokes'])!=1:raise ValueError('Select a unique closed single-stroke style')
    perimeter=choices[0];controls=perimeter['strokes'][0]
    old_centers=[];new_centers=[];alignment_slots=[];input_images={}
    source_captures={c['slot']:c for c in source_state['captures']}
    for capture in state['captures']:
        slot=capture['slot']
        if slot=='front':continue
        key='registered:'+slot+'.png'
        if key not in source_state['result']['cameras'] or key not in state['result']['cameras']:continue
        original=source_captures[slot]
        if capture['sha256']!=original['sha256'] or digest(folder/capture['image'])!=capture['sha256'] or digest(source_folder/original['image'])!=original['sha256']:
            raise ValueError('Camera-pair source photos differ')
        a=source_state['result']['cameras'][key];b=state['result']['cameras'][key]
        old_centers.append(-np.array(a['R']).T@a['t']);new_centers.append(-np.array(b['R']).T@b['t']);alignment_slots.append(slot);input_images[slot]=capture['sha256']
    if len(old_centers)<10:raise ValueError('Insufficient matched cameras')
    scale,rotation,translation,alignment_error=similarity(old_centers,new_centers)
    span=volume['eye_proxy_span'];raw_path=folder/state['result']['full_mesh']
    if digest(raw_path)!=volume['source_sha256'] or digest(raw_path)!=photo_report['source_sha256']:raise ValueError('Raw source changed')
    selected=next(v for v in volume['variants'] if v['sigma_over_eye_span']==.03);mesh_path=neck/(selected['id']+'.ply')
    if digest(mesh_path)!=photo_report['selected_sha256'] or digest(mesh_path)!=selected['mesh_sha256']:raise ValueError('Selected surface changed')
    raw=trimesh.load(raw_path,process=False);candidate=trimesh.load(mesh_path,process=False)
    samples,_,_=source_samples(raw,span);tree=cKDTree(samples)
    eligible=eligible_faces(candidate,span,tree);face_ids=np.flatnonzero(eligible)
    graph_mesh=trimesh.Trimesh(vertices=candidate.vertices,faces=candidate.faces[eligible],process=False)
    original=np.array([np.array(a['weights'])@fit.triangles[a['triangle_index']] for a in controls])
    mapped=scale*original@rotation.T+translation
    q,distance,triangles=trimesh.proximity.closest_point(graph_mesh,mapped)
    attachments=[]
    for p,d,triangle in zip(q,distance,triangles):
        if d>span*.15:attachments.append(None);continue
        w=trimesh.triangles.points_to_barycentric(graph_mesh.triangles[triangle][None],p[None])[0];w=np.clip(w,0,1);w/=w.sum()
        attachments.append({'kind':'barycentric','triangle_index':int(triangle),'weights':w.tolist()})
    print('Routing',len(controls),'projected controls; maximum displacement / eye',float(distance.max()/span),flush=True)
    module=Path(__file__).with_name('flame_measurements_ui.js').resolve()
    payload={'mesh':{'vertices':graph_mesh.vertices.tolist(),'triangles':graph_mesh.faces.tolist()},'attachments':attachments,'span':span,
             'original_steps':np.linalg.norm(np.roll(mapped,-1,axis=0)-mapped,axis=1).tolist()}
    routed=subprocess.run(['node','-e',NODE,str(module)],input=json.dumps(payload),text=True,capture_output=True,check=True,timeout=240)
    paths=json.loads(routed.stdout)
    points=[];weights=[];path_ids=[]
    for i,path in enumerate(paths):
        if path['status']!='routed':continue
        p,w=sample_polyline(path['points'],span*.01);points.extend(p);weights.extend(w);path_ids.extend([i]*len(p))
    points=np.array(points).reshape(-1,3);weights=np.array(weights)
    cameras=[];masks=[];slots=[]
    for view in photo_report['input_views']:
        slot=view['slot'];capture=next(c for c in state['captures'] if c['slot']==slot)
        mask_path=folder/capture['mask']
        if digest(mask_path)!=view['mask_sha256'] or digest(folder/capture['image'])!=view['image_sha256']:raise ValueError('Photo/mask audit source changed')
        cameras.append(state['result']['cameras']['registered:'+slot+'.png']);slots.append(slot)
        mask=np.asarray(Image.open(mask_path).convert('L'))>=128
        masks.append(cv2.dilate(mask.astype(np.uint8),np.ones((7,7),np.uint8))>0)
    out.mkdir(parents=True,exist_ok=False)
    print('Checking',len(points),'path samples against',len(cameras),'source views',flush=True)
    evidence=source_coverage(points,cameras,masks,candidate,raw,tree,span)
    for path in paths:path['sample_count']=0;path['source_supported_length']=0.
    for i,w,e in zip(path_ids,weights,evidence):
        paths[i]['sample_count']+=1
        if e['supported']:paths[i]['source_supported_length']+=float(w)
    for path in paths:
        path['source_supported_fraction']=path['source_supported_length']/path['length'] if path.get('length',0) else None
    proposed_length=sum(p['length'] for p in paths if p['status']=='routed')
    all_routed=all(p['status']=='routed' for p in paths)
    all_observed=all(e['supported'] for e in evidence) and bool(evidence)
    _,_,route_defs=recipe(draft);offset=0
    for route in route_defs:
        ids=list(dict.fromkeys(i for pair in route['pairs'] for i in pair))
        if route['name']==args.style:control_indices=ids;break
    neural=photo_report['runs']['all_views']['smoothed_points']
    control_report=[]
    for j,(p,d,t) in enumerate(zip(q,distance,triangles)):
        control_report.append({'index':j,'source_attachment':controls[j],'projected_point':p.tolist(),'projection_distance_over_eye_span':float(d/span),
            'projection_triangle_in_selected_mesh':int(face_ids[t]),'barycentric_weights':attachments[j]['weights'] if attachments[j] else None,
            'proposal_status':'geometry_only_pending_review' if attachments[j] else 'projection_too_far',
            'automatic_correspondence_status':neural[control_indices[j]]['status'],
            'automatic_correspondence_point':neural[control_indices[j]].get('surface_point')})
    report={'version':'mask_route_projection_v1','session_id':state['id'],'style':args.style,'source_perimeter_id':perimeter['id'],
        'units':'reconstruction_unit','selected_mesh_sha256':digest(mesh_path),'source_fit_sha256':digest(args.source_fit),
        'guide_sha256':digest(args.measurements),'coverage_report_sha256':digest(coverage_folder/'report.json'),
        'alignment':{'method':'proper similarity from matched turn-camera centers; no per-route alignment',
            'scale':scale,'rotation':rotation.tolist(),'translation':translation.tolist(),'matched_slots':alignment_slots,
            'camera_center_rms_over_eye_span':float(np.sqrt(np.mean(alignment_error**2))/span)},
        'policy':{'maximum_proposal_projection_distance_over_eye_span':.15,'low_shift_reference_over_eye_span':.04,
            'maximum_source_sample_distance_over_eye_span':.02,'sample_spacing_over_eye_span':.01,
            'minimum_photo_witnesses':3,'minimum_witness_angle_degrees':3,'raw_depth_agreement_over_eye_span':.02,
            'maximum_path_over_chord':2,'source_mask_dilation_pixels':3},
        'controls':control_report,'paths':paths,'sample_points':points.tolist(),'sample_path_indices':path_ids,'sample_evidence':evidence,
        'summary':{'controls':len(controls),'automatic_correspondence_supported_controls':sum(p['automatic_correspondence_status']=='supported' for p in control_report),
            'routed_edges':sum(p['status']=='routed' for p in paths),'total_edges':len(paths),'routed_portion_length':proposed_length,
            'complete_geometry_proposal_length':proposed_length if all_routed else None,
            'source_supported_sampled_length':float(sum(w for w,e in zip(weights,evidence) if e['supported'])),
            'source_supported_fraction_of_routed_length':float(sum(w for w,e in zip(weights,evidence) if e['supported'])/proposed_length) if proposed_length else None,
            'full_loop_passes_sampled_source_checks':all_routed and all_observed,
            'complete_source_supported_proposal_length':proposed_length if all_routed and all_observed else None,
            'accepted_measurement':None,'review_status':'pending_on_this_surface','millimeter_scale':None},
        'interpretation':'geometry-derived contact-route proposal, not verified anatomical correspondence, mask seal or physical tape length',
        'source_images':input_images,'routing_code_sha256':digest(module),'algorithm_sha256':digest(__file__)}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    front=state['result']['cameras'][state['result']['frontal_camera_key']]
    display=display_mesh(candidate,front);R=np.array(front['R'])
    transform=lambda p:(np.asarray(p)@R.T*np.array([1,-1,-1])).tolist()
    display_paths=[]
    for path in paths:
        color='#24c98b' if path['status']=='routed' and path['source_supported_fraction'] is not None and path['source_supported_fraction']>.999999 else '#ef9f35' if path['status']=='routed' else '#eb5162'
        if path['points']:display_paths.append({'color':color,'points':transform(path['points'])})
    data={'report':report,'mesh':display,'paths':display_paths,'source_guide':transform(np.vstack([mapped,mapped[0]])),
          'controls':transform(q),'neck_viewer':os.path.relpath(neck/'comparison.html',out)}
    template=Path(__file__).with_suffix('.html').read_text()
    if args.style=='bifold':template=template.replace('Trifold / duckbill','Bifold')
    (out/'review.html').write_text(template.replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(json.dumps(report['summary'],indent=2),flush=True)
    print(out/'review.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('session','source-session','source-fit','neck','coverage','measurements','out'):p.add_argument('--'+key,required=True)
    p.add_argument('--style',default='trifold')
    run(p.parse_args())
