"""Reviewed landmarks on immutable full meshes, separate from detector decisions."""
import copy
from datetime import datetime, timezone

import numpy as np
import trimesh

from .regional_inspection import _sources, ray_hits
from .mesh_comparison import read_inspection_mesh

VERSION = 'webcam-landmark-review-v1'
LANDMARKS = {
    'pronasale': {'label': 'Nose tip (pronasale)', 'index': 4,
                  'guide': 'Most anterior point of the nasal tip. Check both profile and frontal views.'},
    'subnasale': {'label': 'Nose base (subnasale)', 'index': 2,
                 'guide': 'Midline junction of the nasal columella and upper lip. Inspect from below and in profile.'},
    'sellion': {'label': 'Nasal root (sellion)', 'index': 168,
               'guide': 'Deepest midline depression at the nasal root. Inspect in profile; mark uncertain if unresolved.'},
}


def source(folder, state, variant):
    if not state.get('result'):
        raise ValueError('A reconstructed surface is required.')
    sid = 'raw_full' if variant == 'raw' else 'refined_full'
    row = next(s for s in _sources(folder, state, variant) if s[0] == sid)
    mesh, sha, _ = read_inspection_mesh(row[2])
    camera = state['result']['cameras'][state['result']['frontal_camera_key']]
    if camera.get('units') != 'reconstruction_unit' or camera.get('mirrored') is not False or camera.get('k', 0) != 0:
        raise ValueError('An unscaled, unmirrored, undistorted camera is required.')
    return mesh, sha, camera, row[4]


def attached(mesh, value):
    if not isinstance(value, dict) or value.get('kind') != 'barycentric':
        raise ValueError('Expected a barycentric full-mesh attachment.')
    face = value.get('triangle_index'); weights = value.get('weights')
    if type(face) is not int or not 0 <= face < len(mesh.faces):
        raise ValueError('Attachment triangle is outside the source topology.')
    if not isinstance(weights, list) or len(weights) != 3 or any(type(v) not in (int, float) for v in weights):
        raise ValueError('Invalid barycentric weights.')
    w = np.asarray(weights)
    if not np.isfinite(w).all() or np.any(w < 0) or np.any(w > 1) or abs(w.sum()-1) > 1e-7:
        raise ValueError('Invalid barycentric weights.')
    return (mesh.triangles[face]*w[:, None]).sum(axis=0).tolist()


def metadata(folder, state, variant='raw'):
    mesh, sha, camera, url = source(folder, state, variant)
    saved = state.get('landmark_review', {}).get('sources', {}).get(variant)
    if saved and saved['sha256'] != sha:
        raise ValueError('Saved landmark source hash changed. Review the source before continuing.')
    hits = ray_hits(mesh, camera, state['result']['raw_predictions'], [v['index'] for v in LANDMARKS.values()])
    return {'version': VERSION, 'session_id': state['id'], 'variant_id': variant, 'sha256': sha,
            'mesh_url': url, 'camera': camera, 'units': 'reconstruction_unit', 'landmarks': LANDMARKS,
            'suggestions': {k: hits[v['index']] for k, v in LANDMARKS.items()},
            'review': copy.deepcopy(saved or {'sha256': sha, 'revision': 0, 'points': {}})}


def operate(folder, state, payload):
    variant = payload.get('variant', 'raw'); mesh, sha, camera, _ = source(folder, state, variant)
    if payload.get('sha256') != sha:
        raise ValueError('Landmark source hash changed; reload review.')
    if payload.get('op') == 'pick':
        # The same orthographic transform and clip volume as webcam_mesh_gl.js.
        view = payload['view']; center = np.asarray(view['center'], dtype=float)
        scale, zoom, yaw, pitch, x, y = [view[k] for k in ('scale','zoom','yaw','pitch','x','y')]
        if center.shape != (3,) or not np.isfinite(center).all() or any(type(v) not in (int,float) or not np.isfinite(v) for v in (scale,zoom,yaw,pitch,x,y)):
            raise ValueError('Invalid picking view.')
        if not (0 < scale < 1e9 and .5 <= zoom <= 3 and abs(yaw) <= 180 and abs(pitch) <= 90 and 0 <= x <= 1 and 0 <= y <= 1):
            raise ValueError('Picking view is outside supported bounds.')
        a,b = np.cos(np.deg2rad(yaw)),np.sin(np.deg2rad(yaw)); c,d = np.cos(np.deg2rad(pitch)),np.sin(np.deg2rad(pitch))
        rotation = np.array([[a,0,b],[d*b,c,-d*a],[-c*b,d,c*a]])
        radius = 380/scale; q = np.array([(x*2-1)*360/(scale*zoom),(1-y*2)*240/(scale*zoom),radius])
        flip = np.array([1,-1,-1]); R = np.asarray(camera['R']); t = np.asarray(camera['t'])
        origin = R.T@((rotation.T@q+center)*flip-t)
        direction = R.T@((rotation.T@np.array([0,0,-1]))*flip)
        points, _, faces = mesh.ray.intersects_location(origin[None,:],direction[None,:],multiple_hits=True)
        if not len(points): return {'status':'missed_surface'}, False
        distance = (points-origin)@direction; valid = np.flatnonzero((distance >= 0)&(distance <= 2*radius))
        if not len(valid): return {'status':'missed_surface'}, False
        i = valid[np.argmin(distance[valid])]; face = int(faces[i]); w = trimesh.triangles.points_to_barycentric(mesh.triangles[face][None,:,:],points[i][None,:])[0]
        w = np.clip(w,0,1); w /= w.sum(); attachment = {'kind':'barycentric','triangle_index':face,'weights':w.tolist()}
        return {'status':'ok','attachment':attachment,'point':attached(mesh,attachment),'sha256':sha}, False
    if payload.get('op') != 'review' or payload.get('landmark') not in LANDMARKS:
        raise ValueError('Unknown landmark operation.')
    status = payload.get('status'); note = payload.get('note','')
    if status not in ('pending','accepted','uncertain','unavailable') or not isinstance(note,str) or len(note)>2000:
        raise ValueError('Invalid landmark status or note.')
    attachment = payload.get('attachment')
    if status == 'unavailable': attachment = None
    if status == 'accepted' and attachment is None: raise ValueError('Place a point before accepting it.')
    point = attached(mesh,attachment) if attachment is not None else None
    review = state.setdefault('landmark_review', {'version':VERSION,'sources':{}})
    saved = review['sources'].setdefault(variant, {'sha256':sha,'revision':0,'points':{}})
    if saved['sha256'] != sha or type(payload.get('revision')) is not int or saved['revision'] != payload['revision']:
        raise ValueError('Landmark review changed; reload before saving.')
    old = saved['points'].get(payload['landmark']); stamp = datetime.now(timezone.utc).isoformat()
    row = {'status':status,'attachment':attachment,'point':point,'note':note,'reviewed_at':stamp,
           'provenance':payload.get('provenance') if payload.get('provenance') in ('manual_surface_pick','detector_suggestion') else 'manual_review',
           'units':'reconstruction_unit','history':(old.get('history',[])+[{k:v for k,v in old.items() if k!='history'}]) if old else []}
    saved['points'][payload['landmark']] = row; saved['revision'] += 1
    return saved, True
