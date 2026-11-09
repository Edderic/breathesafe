"""Recheck a visually selected Gaussian surface against fixed photos and guides.

No physical accuracy verdict. Matching support is required before comparing
partial route lengths; the detector observations are not anatomical ground truth.
"""
import argparse
import copy
import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from scipy.spatial import cKDTree

from .flame_open import load_model
from .flame_mapping import topology_id
from .gaussian_volume import source_samples
from .nose_overlays import project_pixels, visible_points
from .photogrammetry_routes import edge_lengths
from .photogrammetry_trial import attach, digest


VARIANTS = ['grid-224-sigma-0', 'grid-224-sigma-0.03', 'grid-160-sigma-0.03']
COLORS = {'raw':'#52616b', 'grid-224-sigma-0':'#2374ba',
          'grid-224-sigma-0.03':'#df6d12', 'grid-160-sigma-0.03':'#9650b4'}


def recipe(draft):
    points, named, routes = [], {}, []
    for p in draft['points']:
        if p.get('attachment'):
            named[p['name']] = len(points)
            points.append(p['attachment'])
    for name in ('scale', 'check'):
        order = draft['routes'][name]
        if all(n in named for n in order):
            ids = [named[n] for n in order]
            routes.append({'name':name, 'pairs':list(zip(ids, ids[1:]))})
    for p in draft['perimeters']:
        if not p['closed']:
            continue
        pairs = []
        for stroke in p['strokes']:
            ids = list(range(len(points),len(points)+len(stroke)))
            points.extend(stroke);pairs.extend(zip(ids,ids[1:]))
            if len(p['strokes'])==1:
                pairs.append((ids[-1],ids[0]))
        routes.append({'name':p['style'],'pairs':pairs})
    return points,named,routes


def eligible_faces(mesh, span, tree):
    t = mesh.triangles
    longest = np.linalg.norm(t-np.roll(t,1,axis=1),axis=2).max(axis=1)
    area2 = 2*mesh.area_faces
    nearby = tree.query(mesh.vertices, workers=2)[0] <= .02*span
    return (longest<=.12*span)&(area2>1e-15)&(longest**2/np.maximum(area2,1e-15)<=12)&nearby[mesh.faces].all(axis=1)


def qualified_attachments(mesh, mask, records):
    # Face indices change only in this graph copy; the exported mesh stays intact.
    mapping = np.full(len(mesh.faces),-1,dtype=int)
    mapping[mask] = np.arange(mask.sum())
    attachments = {}
    for i,r in enumerate(records):
        if r['status']!='supported':
            continue
        a = r['attachment']
        if mapping[a['triangle_index']]<0:
            r['status']='rejected_triangle_quality_or_proximity'
            continue
        attachments[i]={'triangle_index':int(mapping[a['triangle_index']]),'weights':a['weights']}
    return trimesh.Trimesh(vertices=mesh.vertices,faces=mesh.faces[mask],process=False),attachments


def forward_shift(delta, camera):
    """Positive means toward the original frontal camera, independent of world axes."""
    return -np.asarray(camera['R'])[2] @ np.asarray(delta)


def matched_routes(meshes, attachments, routes):
    pairs = [p for r in routes for p in r['pairs']]
    values = {name:edge_lengths(mesh,attachments[name],pairs) for name,mesh in meshes.items()}
    common = np.array([all(v[i] is not None for v in values.values()) for i in range(len(pairs))])
    output=[];offset=0
    for route in routes:
        count=len(route['pairs']);keep=common[offset:offset+count]
        row={'name':route['name'],'total_control_edges':count,'common_supported_edges':int(keep.sum()),'variants':{}}
        for name,mesh in meshes.items():
            subset=values[name][offset:offset+count]
            length=sum(v for v,yes in zip(subset,keep) if yes)
            chords=0.
            for (a,b),yes in zip(route['pairs'],keep):
                if yes:
                    ps=[np.array(attachments[name][i]['weights'])@mesh.triangles[attachments[name][i]['triangle_index']] for i in (a,b)]
                    chords+=float(np.linalg.norm(ps[1]-ps[0]))
            row['variants'][name]={'matched_partial_mesh_edge_length':length if keep.any() else None,
                                   'matched_partial_control_chord_sum':chords if keep.any() else None,
                                   'complete_mesh_edge_length':length if keep.all() and count else None}
        base=row['variants']['raw']['matched_partial_mesh_edge_length']
        for item in row['variants'].values():
            item['mesh_edge_change_percent_vs_raw']=100*(item['matched_partial_mesh_edge_length']/base-1) if base else None
        output.append(row);offset+=count
    return output


def profile_segments(mesh, origin, camera, axis, span):
    segments=trimesh.intersections.mesh_plane(mesh,np.asarray(camera['R'])[axis],origin)
    if not len(segments):
        return []
    center=segments.mean(axis=1)
    segments=segments[np.linalg.norm(center-origin,axis=1)<span*.75]
    view=(segments-origin)@np.asarray(camera['R']).T/span
    return np.stack([-view[:,:,2],-view[:,:,1] if axis==0 else view[:,:,0]],axis=2).tolist()


def photo_contours(mesh,camera,origin,span,crop,size):
    edges=mesh.face_adjacency_edges;adjacent=mesh.face_adjacency
    mid=mesh.vertices[edges].mean(axis=1)
    camera_center=-np.asarray(camera['R']).T@camera['t']
    facing=np.sum(mesh.face_normals*(camera_center-mesh.triangles_center),axis=1)>0
    candidates=np.flatnonzero((np.linalg.norm(mid-origin,axis=1)<span*.65)&(facing[adjacent[:,0]]!=facing[adjacent[:,1]]))
    if len(candidates)>500:
        candidates=candidates[np.linspace(0,len(candidates)-1,500,dtype=int)]
    if not len(candidates):
        return []
    candidates=candidates[visible_points(mesh,camera,mid[candidates],span*1e-4)]
    result=[]
    for i in candidates:
        try:
            xy=project_pixels(camera,mesh.vertices[edges[i]])
        except ValueError:
            continue
        result.append(((xy-np.array(crop[:2]))*size/(crop[2]-crop[0])).tolist())
    return result


def run(args):
    folder,trial,sweep,out=map(Path,(args.session,args.trial,args.sweep,args.out))
    state=json.loads((folder/'session.json').read_text())
    base=json.loads((trial/'report.json').read_text())
    source=json.loads((trial/'automatic-routes.json').read_text())
    volume=json.loads((sweep/'report.json').read_text())
    draft=json.loads(Path(args.measurements).read_text())
    _,_,faces,model=load_model(args.model)
    if model['model_sha256']!=draft['model_sha256'] or topology_id(faces)!=draft['topology_id']:
        raise ValueError('Guide model or topology changed')
    raw_path=folder/state['result']['full_mesh']
    if digest(raw_path)!=volume['source_sha256'] or digest(raw_path)!=source['raw_sha256']:
        raise ValueError('Raw reconstruction changed')
    if digest(args.measurements)!=source['measurements_sha256']:
        raise ValueError('Guide changed')
    points,named,routes=recipe(draft)
    if len(points)!=len(source['points']):
        raise ValueError('Guide recipe changed')
    if not state['id']==base['session_id']==volume['session_id']==source['session_id']:
        raise ValueError('Sessions differ')
    cameras=[];observations=[]
    for slot in base['slots']:
        pred=Path(args.predictions)/(slot+'.npz')
        if digest(pred)!=base['predictions'][slot]['prediction'] or digest(folder/(slot+'.png'))!=base['predictions'][slot]['image']:
            raise ValueError('Source image/prediction changed')
        cameras.append(state['result']['cameras']['registered:'+slot+'.png'])
        xy=np.load(pred,allow_pickle=False)['vertex_coord']
        observations.append([np.asarray(a['weights'])@xy[faces[a['triangle_index']]] for a in points])
    observations=np.asarray(observations);span=base['eye_proxy_span']
    front=state['result']['cameras'][state['result']['frontal_camera_key']]
    out.mkdir(parents=True,exist_ok=False)
    raw=trimesh.load(raw_path,process=False)
    samples,_,_=source_samples(raw,span)
    tree=cKDTree(samples)
    meshes={'raw':raw};hashes={'raw':digest(raw_path)}
    for name in VARIANTS:
        path=sweep/(name+'.ply');expected=next(v['mesh_sha256'] for v in volume['variants'] if v['id']==name)
        if digest(path)!=expected:
            raise ValueError('Sweep candidate changed')
        meshes[name]=trimesh.load(path,process=False);hashes[name]=expected
    report={'version':'gaussian_validation_v1','session_id':state['id'],'units':'reconstruction_unit',
            'eye_proxy_span':span,'input_mesh_hashes':hashes,'session_sha256':digest(folder/'session.json'),
            'guide_sha256':digest(args.measurements),'source_route_report_sha256':digest(trial/'automatic-routes.json'),
            'prediction_hashes':base['predictions'],'fixed_cameras':dict(zip(base['slots'],cameras)),
            'selected':'grid-224-sigma-0.03','reference':'raw','variants':{},
            'interpretation':'detector/photo consistency and smoothing sensitivity; not anatomical or physical accuracy',
            'thresholds':{'reprojection_pixels':6,'minimum_visible_views':3,'maximum_attachment_shift_over_eye_span':.04,
                          'maximum_source_sample_distance_over_eye_span':.02,'maximum_triangle_edge_over_eye_span':.12},
            'camera_policy':'original fixed COLMAP SIMPLE_RADIAL cameras; no alignment fit',
            'geometry_policy':'no new points in unsupported raw regions; reviews and scale do not transfer'}
    all_records={};graphs={};all_attachments={}
    for name,mesh in meshes.items():
        print('Rechecking',name,flush=True)
        records=[]
        for original in source['points']:
            if original['status']=='supported':
                records.append({'status':'consistent','point':original['surface_point'],
                                'inlier_views':original['inlier_views']})
            else:
                records.append({'status':'raw_candidate_unsupported'})
        attach(mesh,records,cameras,observations,span)
        quality=eligible_faces(mesh,span,tree)
        graph,attachments=qualified_attachments(mesh,quality,records)
        graphs[name]=graph;all_attachments[name]=attachments;all_records[name]=records
        candidates={};errors=[]
        for label,i in named.items():
            if 'surface_point' not in records[i]:
                candidates[label]={'status':records[i]['status']};continue
            q=np.array(records[i]['surface_point']);p=np.array(source['points'][i]['surface_point']);delta=q-p
            candidate={'status':records[i]['status'],'point':q.tolist(),
                       'shift_over_eye_span':float(np.linalg.norm(delta)/span),
                       'forward_shift_over_eye_span':float(forward_shift(delta,front)/span)}
            candidates[label]=candidate
        for i,r in enumerate(records):
            if r['status']!='supported':continue
            for v in r['visible_surface_views']:
                errors.append(float(np.linalg.norm(project_pixels(cameras[v],np.array(r['surface_point'])[None])[0]-observations[v,i])))
        report['variants'][name]={'status_counts':dict(Counter(r['status'] for r in records)),
            'eligible_graph_faces':int(quality.sum()),'named_points':candidates,
            'visible_inlier_reprojection_median_pixels':float(np.median(errors)) if errors else None,
            'points':records}
        (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print('Matched route comparison',flush=True)
    report['matched_routes']=matched_routes(graphs,all_attachments,routes)
    report['chords']={}
    for label,ends in [('nose',['subnasale','pronasale']),('bridge',['sellion','pronasale'])]:
        row={}
        for name in meshes:
            r=[report['variants'][name]['named_points'][n] for n in ends]
            row[name]=float(np.linalg.norm(np.array(r[1]['point'])-r[0]['point'])) if all(p['status']=='supported' for p in r) else None
        report['chords'][label]=row
    anchor=np.array(source['points'][named['pronasale']]['surface_point'])
    sellion=np.array(source['points'][named['sellion']]['surface_point'])
    sections=[]
    for label,origin,axis in [('Nose profile',anchor,0),('Mid-bridge cross-section',(anchor+sellion)/2,1)]:
        sections.append({'label':label,'axis':axis,'origin':origin.tolist(),
                         'curves':{name:profile_segments(mesh,origin,front,axis,span) for name,mesh in meshes.items()}})
    report['sections']=sections
    report['section_policy']='fixed registered camera planes, not an anatomical midline; depth toward camera on x; height/camera right on y'
    photos=[]
    for slot in ('turn_11','turn_17','turn_22','turn_35','turn_48','turn_55'):
        c=state['result']['cameras']['registered:'+slot+'.png']
        center=project_pixels(c,anchor[None])[0]
        depth=(np.asarray(c['R'])@anchor+np.asarray(c['t']))[2]
        half=span*c['fx']/depth*.65
        crop=[int(np.floor(center[0]-half)),int(np.floor(center[1]-half)),int(np.ceil(center[0]+half)),int(np.ceil(center[1]+half))]
        side=max(crop[2]-crop[0],crop[3]-crop[1]);crop[2]=crop[0]+side;crop[3]=crop[1]+side
        image=Image.open(folder/(slot+'.png')).convert('RGB').crop(crop).resize((700,700))
        filename=slot+'.jpg';image.save(out/filename,quality=92)
        print('Photo overlays',slot,flush=True)
        photo={'slot':slot,'image':filename,'source_image_sha256':digest(folder/(slot+'.png')),'crop_pixels':crop,'curves':{}}
        for name in ('raw','grid-224-sigma-0.03'):
            photo['curves'][name]=photo_contours(meshes[name],c,anchor,span,crop,700)
        photos.append(photo)
    report['photos']=photos
    report['algorithm_sha256']=digest(__file__)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    viewer={'report':report,'colors':COLORS,'viewer':os.path.relpath(sweep/'comparison.html',out)}
    (out/'review.html').write_text(Path(__file__).with_suffix('.html').read_text().replace('__DATA__',json.dumps(viewer).replace('</','<\\/')))
    print(json.dumps({'counts':{n:r['status_counts'] for n,r in report['variants'].items()},'chords':report['chords'],
                      'routes':report['matched_routes']},indent=2),flush=True)
    print(out/'review.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('session','trial','sweep','predictions','measurements','model','out'):
        p.add_argument('--'+key,required=True)
    run(p.parse_args())
