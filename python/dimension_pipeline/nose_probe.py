"""Read-only, source-attached diagnostic point and fixed-coordinate sections."""
import numpy as np
import trimesh
from pathlib import Path

from .nose_overlays import LOCK, catalog, context, project_pixels, visible_points
from .regional_inspection import ray_hits, segment_capsule_distance
from .landmark_review import attached, operate as landmark_operation
from .depth_experiments import digest

VERSION = 'webcam-nose-probe-v1'
ALGORITHM_SHA256 = digest(Path(__file__))


def probe_metadata(folder,state,variant='raw'):
    with LOCK:
        stages,anchors,span,region,camera=context(folder,state,variant)
        sources=[]
        for key,label,sha,mesh in stages:
            seed=ray_hits(mesh,camera,state['result']['raw_predictions'],[4])[4]
            sources.append({'id':key,'label':label,'sha256':sha,'seed':seed,
                            'mesh_url':f"/sessions/{state['id']}/mesh" if key=='raw_full' else f"/sessions/{state['id']}/mesh-variant/{variant}"})
        return {'version':VERSION,'session_id':state['id'],'variant_id':variant,'camera':camera,'sources':sources,
                'initial_center':anchors[4]['point'],'eye_proxy_span':span,'units':'reconstruction_unit'}


def section(mesh,point,camera,radius,axis):
    segments=trimesh.intersections.mesh_plane(mesh,np.asarray(camera['R'])[0 if axis=='vertical' else 1],point)
    if len(segments):
        distance=segment_capsule_distance(segments[:,0],segments[:,1],[[point,point]])
        segments=segments[distance<=radius]
    if len(segments)>3000:return {'status':'section_limit_exceeded','segments':[]}
    q=(segments-np.asarray(point))@np.asarray(camera['R']).T
    coordinates=np.stack([-q[:,:,2],-q[:,:,1] if axis=='vertical' else q[:,:,0]],axis=2) if len(q) else np.empty((0,2,2))
    return {'status':'ok' if len(q) else 'no_section_in_local_volume','segments':coordinates.tolist()}


def point_projection(mesh,point,camera,span):
    view=np.asarray(camera['R'])@np.asarray(point)+np.asarray(camera['t'])
    if view[2]<=0:return {'status':'behind_camera','pixel':None}
    pixel=project_pixels(camera,np.asarray([point]))[0].tolist()
    if not (0<=pixel[0]<camera['width'] and 0<=pixel[1]<camera['height']):return {'status':'outside_image','pixel':pixel}
    visible=bool(visible_points(mesh,camera,np.asarray([point]),span*1e-5)[0])
    return {'status':'visible' if visible else 'occluded','pixel':pixel}


def inspect_point(folder,state,payload):
    variant=payload.get('variant','raw');source_id=payload.get('source_id','raw_full')
    if payload.get('op') not in ('pick','inspect'):raise ValueError('Only read-only diagnostic operations are supported.')
    with LOCK:
        stages,anchors,span,region,camera=context(folder,state,variant)
        source=next((s for s in stages if s[0]==source_id),None)
        if source is None or payload.get('sha256')!=source[2]:raise ValueError('Diagnostic source hash or source selection changed.')
        if payload['op']=='pick':
            hit,_=landmark_operation(folder,state,{'op':'pick','variant':'raw' if source_id=='raw_full' else variant,
                                                 'sha256':source[2],'view':payload['view']})
            if hit['status']!='ok':return {'version':VERSION,'session_id':state['id'],'variant_id':variant,'status':'missed_surface'}
            attachment=hit['attachment']
        else:attachment=payload.get('attachment')
        point=attached(source[3],attachment)
        fraction=payload.get('radius_fraction',.12);axis=payload.get('axis','vertical');slots=payload.get('slots')
        if type(fraction) not in (int,float) or fraction not in (.06,.12,.20) or axis not in ('vertical','horizontal'):
            raise ValueError('Choose a supported local radius and section plane.')
        if not isinstance(slots,list) or len(slots)>6 or any(not isinstance(s,str) for s in slots) or len(set(slots))!=len(slots):
            raise ValueError('Choose up to six unique registered source photos.')
        views={v['slot']:v for v in catalog(folder,state,variant)['views']}
        if any(slot not in views for slot in slots):raise ValueError('Diagnostic photo must be a registered reconstruction view.')
        projections={slot:{**point_projection(source[3],point,views[slot]['camera'],span),
                           'camera':views[slot]['camera'],'photo_sha256':views[slot]['photo_sha256']} for slot in slots}
        return {'version':VERSION,'session_id':state['id'],'variant_id':variant,'status':'ok','source_id':source_id,'source_sha256':source[2],
                'algorithm_sha256':ALGORITHM_SHA256,'section_camera':camera,'plane_normal':camera['R'][0 if axis=='vertical' else 1],
                'attachment':attachment,'point':point,'units':'reconstruction_unit','calibration_applied':False,
                'eye_proxy_span':span,'radius_fraction':fraction,'radius':span*fraction,'axis':axis,'projections':projections,
                'sections':[{'id':key,'label':label,'sha256':sha,**section(mesh,point,camera,span*fraction,axis)} for key,label,sha,mesh in stages],
                'section_basis':'Plane through the selected source point; normal is original frontal camera X (vertical) or Y (horizontal). Plot X: depth toward camera; Y: height up or camera right. Unjoined whole segments intersect the local sphere.',
                'limitations':['Diagnostic selection is not an accepted anatomical landmark.','The exact same world point is projected in every view, including occluded/outside statuses; no snapping to image features.','Sections share the original coordinate frame; no correspondence or acceptance transfers to another topology.','These photos guided reconstruction; agreement is not independent accuracy validation.','Selection is ephemeral; download the point/overlay report to retain it.']}
