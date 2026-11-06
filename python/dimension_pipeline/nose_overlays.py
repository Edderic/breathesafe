"""Read-only source-photo diagnostics in the original registered cameras."""
import copy
import hashlib
import json
import threading
from collections import OrderedDict
from pathlib import Path

import numpy as np

from .depth_experiments import digest, contained
from .mesh_comparison import read_inspection_mesh
from .regional_inspection import _sources, define_regions, capsule_distance

VERSION = 'webcam-nose-photo-overlays-v1'
ALGORITHM_SHA256 = digest(Path(__file__))
MAX_EDGES = 300
MESHES = OrderedDict()
REPORTS = OrderedDict()
LOCK = threading.RLock()


def project_pixels(camera, points):
    q = np.asarray(points)@np.asarray(camera['R']).T+np.asarray(camera['t'])
    if np.any(q[:,2] <= 0): raise ValueError('Nose region is behind the registered camera.')
    xy = q[:,:2]/q[:,2,None]
    factor = 1+camera.get('k',0)*np.sum(xy*xy,axis=1)
    if np.any(factor<=0):raise ValueError('Noninvertible source-camera distortion.')
    return xy*factor[:,None]*[camera['fx'],camera['fy']]+[camera['cx'],camera['cy']]


def load_sources(folder, state, variant):
    stages=[]
    for key,label,path,_,_ in _sources(folder,state,variant):
        if path is None:continue
        sha=digest(path)
        if sha not in MESHES:
            MESHES[sha]=read_inspection_mesh(path)[0]
            while len(MESHES)>2:MESHES.popitem(last=False)
        stages.append((key,label,sha,MESHES[sha]))
    return stages


def context(folder,state,variant):
    stages=load_sources(folder,state,variant)
    result=state['result'];front=result['cameras'][result['frontal_camera_key']]
    if result['surface']['units']!='reconstruction_unit' or front.get('units')!='reconstruction_unit' or front.get('mirrored') is not False or front.get('k',0)!=0:
        raise ValueError('An original unscaled surface and undistorted frontal camera are required.')
    anchors,span,regions=define_regions(stages[0][3],front,result['raw_predictions'])
    if span is None or regions['nose']['status']!='ok':raise ValueError('Nose region unavailable: missing raw detector-proxy ray hit.')
    return stages,anchors,span,regions['nose'],front


def catalog(folder,state,variant='raw'):
    with LOCK:
        stages,anchors,span,region,front=context(folder,state,variant)
        tip=np.asarray(anchors[4]['point']);views=[]
        for capture in sorted(state['captures'],key=lambda c:c['slot']):
            if capture['role']=='frontal':continue
            camera=state['result']['cameras'].get('registered:'+capture['slot']+'.png')
            if camera is None:continue
            if camera.get('mirrored') is not False or camera.get('units')!='reconstruction_unit' or (camera['width'],camera['height'])!=(capture['width'],capture['height']):
                raise ValueError('Source camera dimensions, mirroring or units do not match capture.')
            origin=-np.asarray(camera['R']).T@np.asarray(camera['t']);direction=np.asarray(front['R'])@(origin-tip)
            yaw=float(np.rad2deg(np.arctan2(direction[0],-direction[2])))
            elevation=float(np.rad2deg(np.arctan2(-direction[1],np.hypot(direction[0],direction[2]))))
            sequence=capture.get('capture_sequence') or {}
            views.append({'slot':capture['slot'],'camera':camera,'photo_sha256':capture['sha256'],
                          'photo_url':f"/sessions/{state['id']}/captures/{capture['slot']}/image",'yaw':yaw,'elevation':elevation,
                          'declared_height':sequence.get('pass_height','single arc'),'pass_index':sequence.get('pass_index'),
                          'quality_flags':capture.get('capture_quality',{}).get('flags',[])})
        if not views:raise ValueError('No registered turn-photo cameras remain in this session.')
        groups={v['declared_height'] for v in views};chosen=[]
        for group in sorted(groups):
            candidates=[v for v in views if v['declared_height']==group]
            targets=[-35,0,35] if len(groups)>1 else [-60,-30,0,30,60]
            for target in targets:
                row=min(candidates,key=lambda v:abs(v['yaw']-target))
                if row['slot'] not in chosen:chosen.append(row['slot'])
        return {'version':VERSION,'session_id':state['id'],'variant_id':variant,'units':'reconstruction_unit',
                'stages':[{'id':key,'label':label,'sha256':sha} for key,label,sha,_ in stages],
                'views':views,'default_slots':chosen[:6],'region':region,'eye_proxy_span':span,
                'basis':'Original registered cameras and original unmirrored captured pixels; fixed raw detector-proxy nose volume; no alignment fit or calibration transfer.'}


def sampled_edges(mesh, region, camera):
    centers=mesh.triangles_center;radii=np.linalg.norm(mesh.triangles-centers[:,None,:],axis=2).max(axis=1)
    faces=np.flatnonzero(capsule_distance(centers,region['chains'])<=region['radius']+radii)
    if not len(faces):return np.empty((0,2),dtype=int),np.empty(0,dtype=bool)
    ids=np.unique(mesh.edges_unique_inverse.reshape((-1,3))[faces])
    origin=-np.asarray(camera['R']).T@np.asarray(camera['t'])
    facing=np.einsum('ij,ij->i',mesh.face_normals,origin-centers)>0
    counts=np.bincount(mesh.edges_unique_inverse,minlength=len(mesh.edges_unique))
    front=np.bincount(mesh.edges_unique_inverse,weights=np.repeat(facing,3),minlength=len(mesh.edges_unique))
    contour=((front>0)&(front<counts))|(counts==1)
    outline=ids[contour[ids]];other=ids[~contour[ids]]
    # Prefer connected contour edges; retain context wireframe within the same budget.
    if len(outline)>240:outline=outline[np.linspace(0,len(outline)-1,240,dtype=int)]
    remaining=MAX_EDGES-len(outline)
    if len(other)>remaining:other=other[np.linspace(0,len(other)-1,remaining,dtype=int)]
    chosen=np.concatenate([outline,other])
    return mesh.edges_unique[chosen],contour[chosen]


def visible_points(mesh, camera, points, tolerance):
    origin=-np.asarray(camera['R']).T@np.asarray(camera['t']);vectors=points-origin
    lengths=np.linalg.norm(vectors,axis=1);directions=vectors/lengths[:,None]
    visible=np.zeros(len(points),dtype=bool)
    for offset in range(0,len(points),128):
        directions_part=directions[offset:offset+128];origins=np.repeat(origin[None,:],len(directions_part),axis=0)
        faces=mesh.ray.intersects_first(origins,directions_part)
        nearest=np.full(len(directions_part),np.inf)
        hit=faces>=0
        if hit.any():
            normals=mesh.face_normals[faces[hit]];tri=mesh.triangles[faces[hit],0]
            numerator=np.einsum('ij,ij->i',tri-origin,normals);denominator=np.einsum('ij,ij->i',directions_part[hit],normals)
            nearest[hit]=np.divide(numerator,denominator,out=np.full(hit.sum(),np.inf),where=np.abs(denominator)>1e-12)
        visible[offset:offset+len(directions_part)]=np.abs(nearest-lengths[offset:offset+len(directions_part)])<=tolerance
    return visible


def overlay_lines(mesh,camera,region,span):
    edges,contour=sampled_edges(mesh,region,camera)
    if not len(edges):return {'status':'no_region_triangles','lines':[]}
    # Three independently visibility-tested subsegments per real source edge.
    ends=mesh.vertices[edges];delta=ends[:,1]-ends[:,0]
    starts=np.concatenate([ends[:,0]+delta*(i/3) for i in range(3)])
    stops=np.concatenate([ends[:,0]+delta*((i+1)/3) for i in range(3)])
    mid=(starts+stops)/2;R=np.asarray(camera['R']);t=np.asarray(camera['t'])
    valid=(mid@R.T+t)[:,2]>0
    valid &= capsule_distance(mid,region['chains'])<=region['radius']
    ids=np.flatnonzero(valid)
    if len(ids):ids=ids[visible_points(mesh,camera,mid[ids],span*1e-5)]
    lines=[]
    for i in ids:
        try:p=project_pixels(camera,np.array([starts[i],mid[i],stops[i]]))
        except ValueError:continue
        if np.any((p[:,0]<0)|(p[:,0]>camera['width'])|(p[:,1]<0)|(p[:,1]>camera['height'])):continue
        lines.append({'vertices':edges[i%len(edges)].tolist(),'kind':'contour' if contour[i%len(edges)] else 'wire','third':int(i//len(edges)),'pixels':p.tolist()})
    return {'status':'ok' if lines else 'no_visible_sampled_edges','sampled_edges':len(edges),'visible_subsegments':len(lines),
            'visible_contour_subsegments':sum(line['kind']=='contour' for line in lines),'lines':lines}


def photo_overlay(folder,state,slot,variant='raw'):
    with LOCK:
        meta=catalog(folder,state,variant);view=next((v for v in meta['views'] if v['slot']==slot),None)
        if view is None:raise ValueError('Photo is not a registered reconstruction capture.')
        capture=next(c for c in state['captures'] if c['slot']==slot);photo=contained(folder,capture['image'])
        if digest(photo)!=view['photo_sha256']:raise ValueError('Original photo hash changed.')
        from PIL import Image
        with Image.open(photo) as img:
            if img.size!=(view['camera']['width'],view['camera']['height']):raise ValueError('Photo and registered camera dimensions differ.')
        stages,anchors,span,region,_=context(folder,state,variant);camera=view['camera']
        key=hashlib.sha256(json.dumps([VERSION,ALGORITHM_SHA256,state['id'],variant,view,meta['stages'],region],sort_keys=True).encode()).hexdigest()
        if key in REPORTS:return copy.deepcopy(REPORTS[key])
        points=np.asarray([p for chain in region['chains'] for p in chain]);lo=points.min(axis=0)-region['radius'];hi=points.max(axis=0)+region['radius']
        corners=np.asarray([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]);pixels=project_pixels(camera,corners)
        lower=np.maximum(0,pixels.min(axis=0)-20);upper=np.minimum([camera['width'],camera['height']],pixels.max(axis=0)+20)
        if np.any(upper<=lower):raise ValueError('Nose volume projects outside this photo.')
        result={'version':VERSION,'session_id':state['id'],'variant_id':variant,'input_fingerprint':key,'view':view,
                'algorithm_sha256':ALGORITHM_SHA256,
                'crop':[float(lower[0]),float(lower[1]),float(upper[0]-lower[0]),float(upper[1]-lower[1])],
                'crop_method':'Projected raw-region bounding-box corners plus 20 pixels, clipped to image; approximate framing, never used for measurement.',
                'units':'reconstruction_unit','calibration_applied':False,
                'visibility_method':'Nearest full-source triangle hit at each subsegment midpoint, tolerance 1e-5 eye proxy span; endpoints may cross occlusion boundaries. Radial distortion evaluated at endpoints and midpoint.',
                'limitations':['Sparse display wireframe; missing lines do not imply missing surface.','Turn photos guided reconstruction/refinement and are not independent accuracy validation.','Shared original registration is held fixed for raw/refined overlays; geometry, registration and photometric errors remain separate.'],
                'stages':[]}
        for stage,label,sha,mesh in stages:result['stages'].append({'id':stage,'label':label,'sha256':sha,**overlay_lines(mesh,camera,region,span)})
        REPORTS[key]=copy.deepcopy(result)
        while len(REPORTS)>12:REPORTS.popitem(last=False)
        return result
