"""CPU experiment: Gaussian convolution of an oriented-point implicit field.

The field is a local point-to-plane approximation, not a watertight signed
Euclidean distance field. Its zero set and proximity mask are experimental.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import scipy
import trimesh
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.spatial import cKDTree
from skimage import __version__ as skimage_version
from skimage.measure import marching_cubes

from .photogrammetry_trial import digest


def source_samples(mesh, span, count=250000, seed=20):
    triangles = mesh.triangles
    lengths = np.linalg.norm(triangles-np.roll(triangles, 1, axis=1), axis=2).max(axis=1)
    area2 = 2*mesh.area_faces
    keep = (lengths <= span*.12) & (area2 > 1e-15) & (lengths**2/np.maximum(area2, 1e-15) <= 12)
    good = np.flatnonzero(keep)
    if len(good) < 10:
        raise ValueError('Too few quality triangles')
    rng = np.random.default_rng(seed)
    ids = rng.choice(good, count, p=mesh.area_faces[good]/mesh.area_faces[good].sum())
    uv = rng.random((count, 2)); uv[uv.sum(axis=1)>1] = 1-uv[uv.sum(axis=1)>1]
    q = triangles[ids]
    points = q[:, 0]+uv[:, :1]*(q[:, 1]-q[:, 0])+uv[:, 1:]*(q[:, 2]-q[:, 0])
    return points, np.asarray(mesh.face_normals)[ids], keep


def implicit_grid(points, normals, span, resolution, sigma_max, max_voxels=14000000):
    band = .1*span
    pad = band+4*sigma_max
    low, high = points.min(axis=0)-pad, points.max(axis=0)+pad
    step = float((high-low).max()/(resolution-1))
    shape = np.ceil((high-low)/step).astype(int)+1
    if np.prod(shape) > max_voxels:
        raise ValueError('Grid exceeds bounded voxel budget')
    field = np.zeros(tuple(shape), dtype=np.float32)
    weight = np.zeros_like(field)
    nearest = np.zeros_like(field)
    tree = cKDTree(points)
    total = int(np.prod(shape))
    for start in range(0, total, 100000):
        stop = min(start+100000, total)
        indices = np.array(np.unravel_index(np.arange(start, stop), shape)).T
        q = low+indices*step
        distances, ids = tree.query(q, k=4, workers=2)
        local = np.exp(-.5*(distances/step)**2)
        delta = q[:, None]-points[ids]
        signed = np.sum(delta*normals[ids], axis=2)
        values = np.sum(signed*local, axis=1)/np.maximum(local.sum(axis=1), 1e-30)
        w = np.exp(-(distances[:, 0]/band)**2)*(distances[:, 0] <= band)
        field.ravel()[start:stop] = np.clip(values, -band, band)
        weight.ravel()[start:stop] = w
        nearest.ravel()[start:stop] = distances[:, 0]
    return field, weight, nearest, low, step


def filtered_field(field, weight, sigma_voxels):
    if sigma_voxels == 0:
        return field.copy(), weight.copy()
    numerator = gaussian_filter(field*weight, sigma_voxels, mode='constant', cval=0., truncate=4.)
    denominator = gaussian_filter(weight, sigma_voxels, mode='constant', cval=0., truncate=4.)
    return numerator/np.maximum(denominator, 1e-12), denominator


def extract(field, mask, origin, step):
    vertices, faces, _, _ = marching_cubes(field, level=0., spacing=(step,)*3,
                                          mask=mask, allow_degenerate=False, gradient_direction='ascent')
    # Marching-cubes mask selects cells, not every extracted corner. Reject
    # triangles whose interpolated vertices touch unknown grid support.
    valid=map_coordinates(mask.astype(np.float32), (vertices/step).T, order=1, mode='constant', cval=0.)>.999
    faces=faces[np.all(valid[faces],axis=1)]
    if not len(faces):
        raise ValueError('No fully supported extracted triangles')
    mesh=trimesh.Trimesh(vertices=vertices+origin, faces=faces, process=False)
    mesh.remove_unreferenced_vertices()
    return mesh


def percentiles(values):
    return {'rms': float(np.sqrt(np.mean(values**2))), 'median':float(np.median(values)),
            'p95':float(np.percentile(values,95)), 'maximum':float(np.max(values))}


def surface_metrics(raw, mesh, source_points, tree, span):
    rng = np.random.default_rng(20)
    # Same area-weighted raw samples and deterministic candidate sampling for every variant.
    candidate_points, _ = trimesh.sample.sample_surface(mesh, 6000, seed=20)
    _, forward, _ = trimesh.proximity.closest_point(mesh, source_points[:6000])
    ids = rng.choice(len(mesh.vertices), min(6000,len(mesh.vertices)), replace=False)
    _, reverse, _ = trimesh.proximity.closest_point(raw, mesh.vertices[ids])
    proximity, _ = tree.query(candidate_points)
    return {'source_to_variant_over_eye_span':percentiles(forward/span),
            'variant_to_raw_over_eye_span':percentiles(reverse/span),
            'candidate_area_sample_fraction_farther_than_0_02_span_from_quality_samples':float(np.mean(proximity>span*.02)),
            'median_adjacent_normal_angle_degrees':float(np.degrees(np.median(mesh.face_adjacency_angles))),
            'vertices':len(mesh.vertices), 'faces':len(mesh.faces),
            'boundary_edges':int(np.sum(np.bincount(mesh.edges_unique_inverse)==1)),
            'euler_number':int(mesh.euler_number), 'watertight':bool(mesh.is_watertight),
            'self_intersections':'not_checked', 'support':'proximity only; not visibility or anatomical validation'}


def measurement_sensitivity(mesh, source_report, draft, span):
    from .photogrammetry_routes import edge_lengths
    records=source_report['points']
    ids=[i for i,p in enumerate(records) if p['status']=='supported']
    locations=np.array([records[i]['surface_point'] for i in ids])
    q,distance,tri=trimesh.proximity.closest_point(mesh,locations)
    attachments={i:{'triangle_index':int(t),'weights':trimesh.triangles.points_to_barycentric(mesh.triangles[t][None],p[None])[0].tolist()}
                 for i,p,t,d in zip(ids,q,tri,distance) if d<=span*.04}
    named={p['name']:i for i,p in enumerate(p for p in draft['points'] if p.get('attachment'))}
    offset=len(named);routes=[]
    for key in ('scale','check'):
        order=draft['routes'][key]
        if all(n in named for n in order):
            a=[named[n] for n in order];routes.append((key,list(zip(a,a[1:]))))
    for perimeter in draft['perimeters']:
        if not perimeter['closed']:continue
        pairs=[]
        for stroke in perimeter['strokes']:
            indices=list(range(offset,offset+len(stroke)));offset+=len(stroke)
            pairs.extend(zip(indices,indices[1:]))
            if len(perimeter['strokes'])==1:pairs.append((indices[-1],indices[0]))
        routes.append((perimeter['style'],pairs))
    pairs=[p for _,items in routes for p in items]
    lengths=edge_lengths(mesh,attachments,pairs);result=[];offset=0
    for name,items in routes:
        values=lengths[offset:offset+len(items)];offset+=len(items)
        valid=[v for v in values if v is not None]
        result.append({'name':name,'supported_edges':len(valid),'total_edges':len(values),
                       'partial_mesh_edge_length':sum(valid),
                       'complete_length':sum(valid) if valid and len(valid)==len(values) else None})
    chords={}
    for name,ends in [('nose',['subnasale','pronasale']),('bridge',['sellion','pronasale'])]:
        a=[named.get(n) for n in ends]
        if all(i in attachments for i in a):
            ps=[np.array(attachments[i]['weights'])@mesh.triangles[attachments[i]['triangle_index']] for i in a]
            chords[name]=float(np.linalg.norm(ps[1]-ps[0]))
        else:chords[name]=None
    return {'routes':result,'chords':chords,'status':'fixed raw candidate sensitivity only; support/reviews not recertified',
            'method':'raw supported anchors reattached within 0.04 eye proxy spans; approximate mesh-edge paths, not tape simulation'}


def display_mesh(mesh, camera):
    display = mesh.simplify_quadric_decimation(face_count=50000) if len(mesh.faces)>50000 else mesh
    q = np.asarray(display.vertices) @ np.array(camera['R']).T
    # Camera axes: x right, y down, z away. Viewer axes: x right, y up, z toward viewer.
    q *= [1,-1,-1]
    return {'vertices':q.tolist(), 'faces':display.faces.tolist()}


def photo_overlay(folder, slots, cameras, mesh, raw, out, label):
    from PIL import Image, ImageDraw
    from .nose_overlays import project_pixels, visible_points
    # Local nose silhouettes via existing camera registration. View-facing edges, visibility tested at midpoints.
    edges = mesh.face_adjacency_edges
    adjacent = mesh.face_adjacency
    mid = mesh.vertices[edges].mean(axis=1)
    front_camera = cameras[0]
    nose = np.asarray(raw['nose_point'])
    selected = np.linalg.norm(mid-nose,axis=1)<raw['span']*.45
    cards=[]
    for slot, camera in zip(slots,cameras):
        center = -np.array(camera['R']).T @ camera['t']
        facing = np.sum(mesh.face_normals*(center-mesh.triangles_center),axis=1)>0
        take = selected & (facing[adjacent[:,0]] != facing[adjacent[:,1]])
        candidates = np.flatnonzero(take)
        candidates = candidates[np.linspace(0,len(candidates)-1,min(400,len(candidates)),dtype=int)] if len(candidates) else candidates
        if len(candidates):
            visible = visible_points(mesh,camera,mid[candidates],raw['span']*1e-4)
            candidates=candidates[visible]
        image=Image.open(folder/(slot+'.png')).convert('RGB');draw=ImageDraw.Draw(image)
        for i in candidates:
            try:
                q=project_pixels(camera,np.asarray(mesh.vertices[edges[i]]))
                draw.line([tuple(p) for p in q],fill='#13dcd1',width=2)
            except ValueError:
                continue
        try:
            xy=project_pixels(camera,nose[None])[0];size=raw['span']*camera['fx']/(np.array(camera['R'])@nose+camera['t'])[2]*.65
            image=image.crop((xy[0]-size,xy[1]-size,xy[0]+size,xy[1]+size))
        except ValueError:
            pass
        image.thumbnail((650,650));file=f'{label}-{slot}.jpg';image.save(out/file)
        cards.append({'slot':slot,'file':file})
    return cards


def run(args):
    folder, trial, out=Path(args.session),Path(args.trial),Path(args.out)
    state=json.loads((folder/'session.json').read_text());baseline=json.loads((trial/'report.json').read_text())
    raw_path=folder/state['result']['full_mesh']
    if digest(raw_path)!=baseline['raw_sha256']:
        raise ValueError('Raw trial input changed')
    out.mkdir(parents=True,exist_ok=False)
    raw=trimesh.load(raw_path,process=False);span=baseline['eye_proxy_span']
    samples,normals,quality=source_samples(raw,span)
    tree=cKDTree(samples)
    report={'version':'gaussian_oriented_volume_v1','session_id':state['id'],'units':'reconstruction_unit',
            'source_sha256':digest(raw_path),'trial_report_sha256':digest(trial/'report.json'),
            'field':'nearest-four oriented point-to-plane approximation; NOT a true signed Euclidean distance field',
            'quality_source_faces':int(quality.sum()),'excluded_source_faces':int((~quality).sum()),'sample_count':len(samples),
            'eye_proxy_span':span,'sigmas_over_eye_span':[0,.015,.03,.06],
            'numpy':np.__version__,'scipy':scipy.__version__,'skimage':skimage_version,
            'support_policy':'source proximity band 0.1 eye spans; filtered weight >0.25; newly extracted geometry is inferred, not observed',
            'variants':[]}
    front=state['result']['cameras'][state['result']['frontal_camera_key']]
    viewer={'raw':display_mesh(raw,front),'variants':[],'report':report}
    supported=json.loads((trial/'automatic-routes.json').read_text())
    draft=json.loads(Path(args.measurements).read_text())
    if digest(args.measurements)!=supported['measurements_sha256']:
        raise ValueError('Guide recipe changed')
    report['measurements_sha256']=digest(args.measurements)
    candidates=[p for p in supported['points'] if p['status']=='supported']
    source_anchors=np.array([p['surface_point'] for p in candidates])
    slots=['turn_11','turn_22','turn_48']
    cameras=[state['result']['cameras']['registered:'+slot+'.png'] for slot in slots]
    predictions=state['result']['projected_points']
    nose=next(p['point'] for p in predictions if p['index']==4 and p['status']=='ok')
    report['raw_photos']=photo_overlay(folder,slots,cameras,raw,{'nose_point':nose,'span':span},out,'raw')
    for resolution in (160,224):
        print('Building grid',resolution,flush=True);started=time.monotonic()
        field,weight,nearest,origin,step=implicit_grid(samples,normals,span,resolution,.06*span)
        print('Grid',field.shape,'voxel/eye',step/span,'seconds',time.monotonic()-started,flush=True)
        for fraction in (0.,.015,.03,.06):
            start=time.monotonic();label=f'grid-{resolution}-sigma-{fraction:g}'
            blurred,density=filtered_field(field,weight,fraction*span/step)
            mask=(density>.25)&(nearest<span*.1)
            mesh=extract(blurred,mask,origin,step)
            mesh.export(out/(label+'.ply'))
            record={'id':label,'resolution_longest_axis':resolution,'grid_shape':list(field.shape),
                    'voxel_over_eye_span':step/span,'sigma_over_eye_span':fraction,'sigma_voxels':fraction*span/step,
                    'mesh_sha256':digest(out/(label+'.ply')),'metrics':surface_metrics(raw,mesh,samples,tree,span)}
            # Reattach only to quantify movement of fixed raw candidate locations, never to transfer review status.
            closest,distance,tri=trimesh.proximity.closest_point(mesh,source_anchors)
            record['fixed_candidate_anchor_displacement_over_eye_span']=percentiles(distance/span)
            record['measurements']=measurement_sensitivity(mesh,supported,draft,span)
            record['photos']=photo_overlay(folder,slots,cameras,mesh,{'nose_point':nose,'span':span},out,label)
            record['seconds']=time.monotonic()-start
            report['variants'].append(record)
            viewer['variants'].append({'label':label,'mesh_file':label+'.ply',**display_mesh(mesh,front)})
            (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
            print(label,record['metrics']['faces'],'faces',round(record['seconds'],1),'s',flush=True)
    report['algorithm_sha256']=digest(__file__)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    html=Path(__file__).with_name('gaussian_volume.html').read_text()
    (out/'comparison.html').write_text(html.replace('__DATA__',json.dumps(viewer).replace('</','<\\/')))
    print(out/'comparison.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('session','trial','measurements','out'):p.add_argument('--'+key,required=True)
    run(p.parse_args())
