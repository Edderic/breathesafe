"""Immutable regional geometry diagnostics. No anatomical equivalence or scale transfer."""
import copy
import hashlib
import json
import struct
import threading
from collections import OrderedDict
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from .depth_experiments import contained, digest
from .depth_metrics import distances, summary
from .depth_variants import experiment_variants
from .mesh_comparison import checked_mesh, mesh_identity, read_inspection_mesh
from .webcam_geometry import ray

POLICY = json.loads(Path(__file__).with_name('regional_policy.json').read_text())
LEGACY = json.loads(Path(__file__).with_name('legacy_arkit_paths.json').read_text())
CODE_SHA256 = digest(Path(__file__))
LOCK = threading.Lock()
CACHE = OrderedDict()


def point_segment_distance(points, a, b):
    points = np.asarray(points); a = np.asarray(a); delta = np.asarray(b)-a
    length = float(delta@delta)
    t = np.clip((points-a)@delta/length,0,1) if length else np.zeros(len(points))
    return np.linalg.norm(points-a-t[:,None]*delta,axis=1)


def capsule_distance(points, chains):
    return np.min([point_segment_distance(points,a,b) for chain in chains for a,b in zip(chain,chain[1:])],axis=0)


def segment_capsule_distance(start, end, chains):
    """Exact segment-to-segment distance: interior solution or endpoint minimum."""
    start=np.asarray(start);end=np.asarray(end);u=end-start;A=np.einsum('ij,ij->i',u,u)
    result=np.full(len(start),np.inf)
    for chain in chains:
        for a,b in zip(chain,chain[1:]):
            a=np.asarray(a);b=np.asarray(b);v=b-a;w=start-a;B=u@v;C=float(v@v);D=np.einsum('ij,ij->i',u,w);E=w@v
            denom=A*C-B*B;valid=denom>1e-20
            s=np.divide(B*E-C*D,denom,out=np.zeros(len(start)),where=valid)
            t=np.divide(A*E-B*D,denom,out=np.zeros(len(start)),where=valid)
            inside=valid & (s>=0)&(s<=1)&(t>=0)&(t<=1)
            interior=np.where(inside,np.linalg.norm(w+s[:,None]*u-t[:,None]*v,axis=1),np.inf)
            def to_edges(p):
                q=np.divide(np.einsum('ij,ij->i',p-start,u),A,out=np.zeros(len(start)),where=A>0)
                return np.linalg.norm(p-start-np.clip(q,0,1)[:,None]*u,axis=1)
            result=np.minimum(result,np.minimum.reduce([interior,point_segment_distance(start,a,b),point_segment_distance(end,a,b),to_edges(a),to_edges(b)]))
    return result


def ray_hits(mesh, camera, predictions, indices):
    rows={};valid=[];origins=[];directions=[]
    for index in indices:
        if index>=len(predictions): rows[index]={'status':'missing_prediction'};continue
        p=predictions[index]
        if any(type(p.get(k)) not in (int,float) or not np.isfinite(p[k]) or not 0<=p[k]<=1 for k in ('x','y')):
            rows[index]={'status':'invalid_prediction'};continue
        origin,direction=ray(camera,[p['x']*camera['width'],p['y']*camera['height']])
        valid.append(index);origins.append(origin);directions.append(direction);rows[index]={'status':'missed_surface'}
    if not valid:return rows
    points,rays,faces=mesh.ray.intersects_location(np.asarray(origins),np.asarray(directions),multiple_hits=True)
    best={}
    for point,r,face in zip(points,rays,faces):
        d=float(np.linalg.norm(point-origins[r]))
        if r in best and d>=best[r]:continue
        best[r]=d;tri=mesh.triangles[face]
        weights=trimesh.triangles.points_to_barycentric(tri[None,:,:],point[None,:])[0]
        rows[valid[r]]={'status':'ok','point':point.tolist(),'attachment':{'kind':'barycentric','triangle_index':int(face),'weights':weights.tolist()}}
    return rows


def define_regions(raw, camera, predictions):
    indices=sorted(set(POLICY['normalizer_indices']+[i for region in POLICY['regions'].values() for chain in region['chains'] for i in chain]))
    anchors=ray_hits(raw,camera,predictions,indices)
    if any(anchors[i]['status']!='ok' for i in POLICY['normalizer_indices']):return anchors,None,{}
    a,b=[np.asarray(anchors[i]['point']) for i in POLICY['normalizer_indices']];span=float(np.linalg.norm(a-b))
    if not np.isfinite(span) or span<=0:return anchors,None,{}
    regions={}
    for name,policy in POLICY['regions'].items():
        ids=set(i for chain in policy['chains'] for i in chain)
        missing=[i for i in ids if anchors[i]['status']!='ok']
        regions[name]={'label':policy['label'],'status':'missing_proxy_anchor' if missing else 'ok','missing_indices':missing,
                       'chains':[[anchors[i]['point'] for i in chain] for chain in policy['chains']] if not missing else [],
                       'radius':span*policy['radius_fraction'],'detector_chains':policy['chains']}
    return anchors,span,regions


def sample_region(mesh, chains, radius, count, seed):
    centers=mesh.triangles_center
    face_radius=np.linalg.norm(mesh.triangles-centers[:,None,:],axis=2).max(axis=1)
    ids=np.flatnonzero(capsule_distance(centers,chains)<=radius+face_radius)
    if not len(ids):return np.empty((0,3)),np.empty(0,dtype=int),[]
    area=mesh.area_faces[ids];rng=np.random.default_rng(seed);points=[];faces=[];accepted=0;attempted=0
    for _ in range(16):
        size=max(1024,(count-accepted)*3);chosen=rng.choice(ids,size=size,p=area/area.sum())
        uv=rng.random((size,2));flip=uv.sum(axis=1)>1;uv[flip]=1-uv[flip]
        tri=mesh.triangles[chosen];p=tri[:,0]+uv[:,0,None]*(tri[:,1]-tri[:,0])+uv[:,1,None]*(tri[:,2]-tri[:,0])
        keep=capsule_distance(p,chains)<=radius;points.append(p[keep]);faces.append(chosen[keep]);accepted+=int(keep.sum());attempted+=size
        if accepted>=count:break
    points=np.concatenate(points)[:count];faces=np.concatenate(faces)[:count]
    return points,faces,ids.tolist()


def local_roughness(mesh, region, span):
    points,_,display=sample_region(mesh,region['chains'],region['radius'],POLICY['samples'],POLICY['seed'])
    if len(points)<POLICY['minimum_samples']:return {'status':'insufficient_surface_samples','sample_count':len(points),'face_indices':display},points
    radius=span*POLICY['roughness_radius_fraction']
    cloud,_,_=sample_region(mesh,region['chains'],region['radius']+radius,POLICY['cloud_samples'],POLICY['cloud_seed'])
    neighborhoods=cKDTree(cloud).query_ball_point(points,radius);residuals=[]
    for ids in neighborhoods:
        if len(ids)<POLICY['minimum_neighbors']:continue
        p=cloud[ids];p=p-p.mean(axis=0);residuals.append(np.sqrt(max(0,float(np.linalg.eigvalsh(p.T@p/len(p))[0]))))
    counts=np.bincount(mesh.edges_unique_inverse,minlength=len(mesh.edges_unique));edges=mesh.edges_unique[counts!=2]
    if len(edges):
        touched=segment_capsule_distance(mesh.vertices[edges[:,0]],mesh.vertices[edges[:,1]],region['chains'])<=region['radius']
        edge_counts=counts[counts!=2][touched]
    else:edge_counts=np.empty(0)
    return {'status':'ok' if len(residuals)>=POLICY['minimum_samples'] else 'insufficient_neighborhoods',
            'sample_count':len(points),'cloud_count':len(cloud),'face_indices':display,
            'roughness':summary(residuals),'roughness_fraction_eye_proxy_span':summary(np.asarray(residuals)/span),
            'neighborhood_radius':radius,'original_boundary_edges':int(np.count_nonzero(edge_counts==1)),
            'original_nonmanifold_edges':int(np.count_nonzero(edge_counts>2)),
            'boundary_method':'original_mesh_edges_intersecting_fixed_capsules; crop_edges_not_counted_as_holes',
            'hole_count':None},points


def nose_profile(mesh, region, camera, origin):
    segments=trimesh.intersections.mesh_plane(mesh,np.asarray(camera['R'])[0],origin)
    if not len(segments):return {'status':'missing_section','segments':[]}
    keep=segment_capsule_distance(segments[:,0],segments[:,1],region['chains'])<=region['radius'];segments=segments[keep]
    if len(segments)>3000:return {'status':'section_limit_exceeded','segments':[]}
    R=np.asarray(camera['R']);t=np.asarray(camera['t']);o=R@origin+t
    view=segments@R.T+t;profile=np.stack([-(view[:,:,2]-o[2]),-(view[:,:,1]-o[1])],axis=2)
    return {'status':'ok' if len(profile) else 'missing_section','segments':profile.tolist(),
            'basis':'camera-X plane through raw index-4 ray hit; depth toward camera and up relative to raw tip proxy; not verified anatomical midsagittal plane',
            'ordered_surface_arc':False}


def nose_proxies(hits, camera, span):
    if any(hits.get(i,{}).get('status')!='ok' for i in (168,4,2)):
        return {'status':'missing_proxy_hit','chord':None,'forward_offset':None}
    root,tip,base=[np.asarray(hits[i]['point']) for i in (168,4,2)]
    chord=float(np.linalg.norm(tip-base));depth=float(np.asarray(camera['R'])[2]@(root-tip))
    return {'status':'unreviewed_detector_proxy','chord':chord,'chord_fraction_eye_proxy_span':chord/span,
            'forward_offset':depth,'forward_offset_fraction_eye_proxy_span':depth/span,
            'definition':'index 4-to-2 chord; index 168-to-4 camera-depth difference; not reviewed pronasale/subnasale/sellion',
            'anatomical_nose_protrusion':None,'surface_arc':None,'surface_arc_status':'requires_reviewed_landmarks_and_route'}


def region_rays(region,camera):
    points=np.asarray([p for chain in region['chains'] for p in chain]);view=points@np.asarray(camera['R']).T+np.asarray(camera['t']);r=region['radius']
    lo=view.min(axis=0)-r;hi=view.max(axis=0)+r
    if lo[2]<=0:return []
    corners=np.asarray([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])
    pixels=np.column_stack([camera['fx']*corners[:,0]/corners[:,2]+camera['cx'],camera['fy']*corners[:,1]/corners[:,2]+camera['cy']])
    left,top=np.maximum(pixels.min(axis=0),[0,0]);right,bottom=np.minimum(pixels.max(axis=0),[camera['width'],camera['height']])
    if right<=left or bottom<=top:return []
    predictions=[{'x':float(x/camera['width']),'y':float(y/camera['height'])} for y in np.linspace(top,bottom,13) for x in np.linspace(left,right,13)]
    rays=[ray(camera,[p['x']*camera['width'],p['y']*camera['height']]) for p in predictions];a=np.asarray([p[0] for p in rays]);b=a+np.asarray([p[1] for p in rays])*(hi[2]+r)
    keep=segment_capsule_distance(a,b,region['chains'])<=r
    return [p for p,k in zip(predictions,keep) if k]


def frontal_support(mesh,region,camera):
    predictions=region_rays(region,camera);hits=ray_hits(mesh,camera,predictions,range(len(predictions)))
    count=sum(h['status']=='ok' and capsule_distance(np.asarray([h['point']]),region['chains'])[0]<=region['radius']*(1+1e-8) for h in hits.values())
    return {'rays':len(predictions),'nearest_hits_in_fixed_region':int(count),'fraction':count/len(predictions) if predictions else None,
            'method':'13x13 frontal grid filtered by exact ray-segment/capsule intersection; nearest hit inside volume; not anatomical completeness'}


def read_dense_points(path):
    """Bounded OpenMVS binary vertex reader; visibility lists are skipped, never triangulated."""
    if path.stat().st_size>256*1024**2:raise ValueError('Dense cloud exceeds 256 MiB regional inspection limit.')
    data=path.read_bytes();end=data.find(b'end_header\n',0,65536)
    if end<0:raise ValueError('Missing dense PLY header.')
    lines=data[:end].decode('ascii').splitlines()
    if lines[:2]!=['ply','format binary_little_endian 1.0']:raise ValueError('Unsupported dense PLY format.')
    types={'float32':'f','float':'f','float64':'d','double':'d','uint8':'B','uchar':'B','uint32':'I','uint':'I','int32':'i','int':'i'}
    count=None;props=[]
    for line in lines[2:]:
        p=line.split()
        if not p or p[0]=='comment':continue
        if p[0]=='element':
            if p[1]!='vertex' or count is not None:raise ValueError('Unsupported dense elements.')
            count=int(p[2])
        elif p[0]=='property':
            if p[1]=='list':props.append((p[4],p[2],p[3]))
            else:props.append((p[2],None,p[1]))
    if count is None or not 0<count<=3000000 or not all(any(p[0]==axis and p[1] is None for p in props) for axis in ('x','y','z')):raise ValueError('Invalid dense point count/coordinates.')
    offset=end+len(b'end_header\n');points=np.empty((count,3));xyz={'x':0,'y':1,'z':2}
    try:
        for i in range(count):
            for name,list_type,value_type in props:
                fmt='<'+types[value_type];size=struct.calcsize(fmt)
                if list_type:
                    nfmt='<'+types[list_type];n=struct.unpack_from(nfmt,data,offset)[0];offset+=struct.calcsize(nfmt)
                    if not 0<=n<=10000:raise ValueError('Invalid dense visibility-list count.')
                    offset+=n*size
                    if offset>len(data):raise ValueError('Truncated dense visibility list.')
                else:
                    value=struct.unpack_from(fmt,data,offset)[0];offset+=size
                    if name in xyz:points[i,xyz[name]]=value
    except (KeyError,struct.error) as error:raise ValueError('Unsupported or truncated dense PLY.') from error
    if not np.isfinite(points).all():raise ValueError('Nonfinite dense points.')
    if data[offset:].strip(b'\r\n'):raise ValueError('Unexpected trailing dense PLY data.')
    return points


def _sources(folder,state,variant):
    result=state['result'];raw_path=contained(folder,result['full_mesh']);sources=[('raw_full','Raw full mesh',raw_path,None,f"/sessions/{state['id']}/mesh")]
    sources.append(('raw_analysis','Raw analysis mesh',None,result['surface']['mesh'],None))
    if variant!='raw':
        row=next((r for r in experiment_variants(state) if r['id']==variant and r['kind']=='image_refined'),None)
        if row is None:raise ValueError('Choose a completed refined variant or raw.')
        path=contained(folder,row['full_mesh'])
        if digest(path)!=row['sha256']:raise ValueError('Refined full-mesh hash changed.')
        artifact=next((a for a in row['artifacts'] if a['path']==row['projection']),None)
        p=contained(folder,row['projection'])
        if artifact is None or digest(p)!=artifact['sha256']:raise ValueError('Refined projection hash changed.')
        projection=json.loads(p.read_text());surface=projection['surface']
        if surface['units']!='reconstruction_unit' or mesh_identity(surface['mesh'])!=row['analysis_mesh_id']:raise ValueError('Refined analysis provenance mismatch.')
        sources += [('refined_full',row['label']+' full',path,None,f"/sessions/{state['id']}/mesh-variant/{variant}"),
                    ('refined_analysis','Refined analysis mesh',None,surface['mesh'],None)]
    return sources


def regional_report(folder,state,variant='raw'):
    folder=Path(folder).resolve();result=state.get('result')
    if not result or result['surface']['units']!='reconstruction_unit':raise ValueError('Regional inspection requires the original unscaled reconstruction.')
    camera=result['cameras'][result['frontal_camera_key']]
    if camera.get('k',0)!=0 or camera.get('mirrored') is not False or camera.get('units')!='reconstruction_unit':raise ValueError('Regional inspection requires an unscaled, undistorted, unmirrored frontal camera.')
    sources=_sources(folder,state,variant);dense_path=contained(folder,result['full_mesh']).parent/'dense.ply'
    if dense_path.exists():dense_path=contained(folder,dense_path.relative_to(folder).as_posix())
    hashes={sid:digest(path) if path else mesh_identity(mesh) for sid,_,path,mesh,_ in sources}
    dense_hash=digest(dense_path) if dense_path.is_file() and dense_path.stat().st_size<=256*1024**2 else None
    key=hashlib.sha256(json.dumps([state['id'],variant,POLICY,LEGACY,CODE_SHA256,hashes,dense_hash,camera,result['raw_predictions']],sort_keys=True).encode()).hexdigest()
    if not LOCK.acquire(blocking=False):raise ValueError('Another regional report is processing; retry shortly.')
    try:
        if key in CACHE:
            report=copy.deepcopy(CACHE[key]);report['session_id']=state['id'];return report
        meshes={};stages=[]
        for sid,label,path,mesh,url in sources:
            m=read_inspection_mesh(path)[0] if path else checked_mesh(trimesh.Trimesh(vertices=mesh['vertices'],faces=mesh['triangles'],process=False))
            meshes[sid]=m;stages.append({'id':sid,'label':label,'sha256':hashes[sid], 'vertices':len(m.vertices),'faces':len(m.faces),'mesh_url':url,'mesh':mesh if path is None else None,'regions':{}})
        raw=meshes['raw_full'];anchors,span,regions=define_regions(raw,camera,result['raw_predictions'])
        report={'version':POLICY['version'],'session_id':state['id'],'variant_id':variant,'input_fingerprint':key,'units':'reconstruction_unit','display_camera':camera,'policy':POLICY,
                'anchors':{str(k):v for k,v in anchors.items()},'eye_proxy_span':span,'regions':regions,'stages':stages,
                'anatomical_status':POLICY['anatomical_status'],'arkit_paths':{name:{'status':'requires_reviewed_cross_topology_correspondence','length':None,
                    'legacy_segments':LEGACY['segments'][name],'source_topology':LEGACY['topology_id'],'construction':'sum of legacy short chords; no cross-topology mapping or verified seal line'} for name in POLICY['regions']},
                'algorithm_sha256':CODE_SHA256,'display_geometry_method':'unmodified_whole_triangles_from_conservative_centroid_radius_candidates; no clipping/repair; metrics sample the exact volume',
                'accuracy_status':'not_independently_validated','calibration_applied':False,'dense':{'status':'missing_cache' if not dense_path.exists() else 'not_processed'},
                'limitations':['Regions are fixed raw-surface detector-proxy volumes, not actual mask seal lines or ARKit mappings.','Curvature, density, boundary artifacts and true detail affect plane residuals.','Proximity and ray intersections are not anatomical accuracy or completeness.','No calibration, landmark acceptance or annotation is transferred; all values remain unscaled.']}
        report['image_anchors']={str(i):{'x':result['raw_predictions'][i]['x']*camera['width'],'y':result['raw_predictions'][i]['y']*camera['height'],'status':a['status']}
            for i,a in anchors.items() if a['status'] not in ('missing_prediction','invalid_prediction')}
        if span is None:
            report['status']='missing_normalizer_proxy_hits';return report
        raw_samples={}
        for stage in stages:
            mesh=meshes[stage['id']];hits=ray_hits(mesh,camera,result['raw_predictions'],[168,4,2]);stage['nose_proxies']=nose_proxies(hits,camera,span);stage['nose_proxy_hits']={str(k):v for k,v in hits.items()}
            for name,region in regions.items():
                if region['status']!='ok':stage['regions'][name]={'status':region['status'],'face_indices':[]};continue
                metrics,points=local_roughness(mesh,region,span)
                if stage['id']=='raw_full':raw_samples[name]=points
                base=raw_samples.get(name,np.empty((0,3)))
                if len(points)>=POLICY['minimum_samples'] and len(base)>=POLICY['minimum_samples']:
                    forward=distances(mesh,base);reverse=distances(raw,points)
                    metrics.update(raw_to_stage=summary(forward),stage_to_raw=summary(reverse),raw_proximity_fraction=float(np.mean(forward<=span*POLICY['proximity_tolerance_fraction'])))
                metrics['display_status']='ok' if len(metrics['face_indices'])<=POLICY['maximum_display_faces'] else 'region_display_limit_exceeded'
                metrics['frontal_support']=frontal_support(mesh,region,camera)
                if metrics['display_status']!='ok':metrics['face_indices']=[]
                stage['regions'][name]=metrics
            stage['nose_profile']=nose_profile(mesh,regions['nose'],camera,np.asarray(anchors[4]['point'])) if regions.get('nose',{}).get('status')=='ok' else {'status':'missing_proxy_anchor','segments':[]}
        if dense_hash:
            try:
                cloud=read_dense_points(dense_path);dense={'status':'ok','sha256':dense_hash,'point_count':len(cloud),'regions':{}}
                for name,region in regions.items():
                    if region['status']!='ok':dense['regions'][name]={'status':'missing_proxy_anchor'};continue
                    indices=np.flatnonzero(capsule_distance(cloud,region['chains'])<=region['radius']);chosen=indices[np.random.default_rng(39).choice(len(indices),min(512,len(indices)),replace=False)] if len(indices) else []
                    p=cloud[chosen];view=p@np.asarray(camera['R']).T+np.asarray(camera['t']);o=np.asarray(camera['R'])@np.asarray(anchors[4]['point'])+np.asarray(camera['t'])
                    slab=cloud[indices]@np.asarray(camera['R']).T+np.asarray(camera['t'])
                    slab=slab[np.abs(slab[:,0]-o[0])<=span*.02]
                    slab=slab[np.random.default_rng(40).choice(len(slab),min(512,len(slab)),replace=False)] if len(slab) else slab
                    dense['regions'][name]={'status':'ok' if len(p) else 'no_points','point_count':len(indices),'sample_count':len(p),'points':p.tolist(),
                        'profile_scatter':np.column_stack([-(slab[:,2]-o[2]),-(slab[:,1]-o[1])]).tolist(),'profile_slab_halfwidth':span*.02,
                        'sampled_distance_to_raw_full':summary(distances(raw,p)) if len(p) else {'count':0}}
                report['dense']=dense
            except ValueError as error:report['dense']={'status':'unsupported_or_invalid_cache','error':str(error)}
        elif dense_path.exists():report['dense']={'status':'cache_exceeds_256_mib_limit'}
        report['status']='ready';CACHE[key]=copy.deepcopy(report)
        while len(CACHE)>4:CACHE.popitem(last=False)
        return report
    finally:LOCK.release()
