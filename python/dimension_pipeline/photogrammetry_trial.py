"""Bounded raw/smoothed surface and automatic multi-view correspondence experiment.

Uses fixed original registered cameras, never fitted FLAME camera poses or depths.
Outputs native reconstruction units; no calibration or anatomical acceptance.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image, ImageDraw

from .flame_open import load_model
from .nose_overlays import project_pixels


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def camera_arrays(cameras, observations):
    normalized = []
    for camera, xy in zip(cameras, observations):
        k = np.array([[camera['fx'], 0, camera['cx']], [0, camera['fy'], camera['cy']], [0, 0, 1.]])
        normalized.append(cv2.undistortPoints(np.asarray(xy, dtype=float)[:, None], k,
                          np.array([camera.get('k', 0), 0., 0., 0.]))[:, 0])
    projection = np.array([np.c_[c['R'], c['t']] for c in cameras])
    centers = np.array([-np.array(c['R']).T @ c['t'] for c in cameras])
    return np.asarray(normalized), projection, centers


def dlt(projection, normalized):
    rows = np.concatenate([xy[:, None]*p[2]-p[:2] for p, xy in zip(projection, normalized)])
    _, _, vh = np.linalg.svd(rows)
    h = vh[-1]
    return h[:3]/h[3] if abs(h[3]) > 1e-12 else np.full(3, np.nan)


def triangulate(cameras, observations, threshold=6., minimum_views=3, minimum_angle=3.):
    """Deterministic pair consensus followed by inlier-only multi-view DLT."""
    normalized, projections, centers = camera_arrays(cameras, observations)
    points = []
    for index in range(observations.shape[1]):
        obs = observations[:, index]
        valid = np.array([np.isfinite(xy).all() and 0 <= xy[0] < c['width'] and 0 <= xy[1] < c['height']
                          for c, xy in zip(cameras, obs)])
        def errors(point):
            if not np.isfinite(point).all():
                return np.full(len(cameras), np.inf)
            result = []
            for c, xy, good in zip(cameras, obs, valid):
                z = (np.array(c['R']) @ point+np.array(c['t']))[2]
                result.append(np.linalg.norm(project_pixels(c, point[None])[0]-xy) if good and z > 0 else np.inf)
            return np.array(result)
        best = None
        for pair in itertools.combinations(np.flatnonzero(valid), 2):
            ids = list(pair)
            point = dlt(projections[ids], normalized[ids, index])
            error = errors(point)
            keep = error <= threshold
            score = (int(keep.sum()), -float(np.minimum(error, threshold).sum()))
            if best is None or score > best[0]:
                best = (score, point, keep)
        if best is None or best[2].sum() < minimum_views:
            points.append({'status': 'insufficient_consensus'})
            continue
        point, keep = best[1:]
        for _ in range(3):
            point = dlt(projections[keep], normalized[keep, index])
            error = errors(point)
            updated = error <= threshold
            if updated.sum() < minimum_views:
                keep = updated
                break
            if np.array_equal(updated, keep):
                break
            keep = updated
        rays = point-centers[keep]
        rays /= np.linalg.norm(rays, axis=1)[:, None]
        angle = float(np.degrees(np.arccos(np.clip(rays @ rays.T, -1, 1))).max()) if len(rays) else 0.
        status = 'consistent' if keep.sum() >= minimum_views and angle >= minimum_angle else 'insufficient_parallax_or_consensus'
        points.append({'status': status, 'point': point.tolist(), 'inlier_views': np.flatnonzero(keep).tolist(),
                       'reprojection_rms_pixels': float(np.sqrt(np.mean(error[keep]**2))) if keep.any() else None,
                       'maximum_ray_angle_degrees': angle})
    return points


def smooth(mesh, cycles):
    """Alternating Taubin passes with open-boundary vertices fixed each pass."""
    result = mesh.copy()
    edges = mesh.edges_sorted
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    pinned = np.unique(unique[counts == 1])
    laplacian = trimesh.smoothing.laplacian_calculation(mesh, pinned_vertices=pinned)
    trimesh.smoothing.filter_taubin(result, lamb=.5, nu=.53, iterations=cycles*2, laplacian_operator=laplacian)
    return result, pinned


def attach(mesh, records, cameras, observations, span, threshold=6.):
    ids = [i for i, p in enumerate(records) if p['status'] == 'consistent']
    if not ids:
        return
    points = np.array([records[i]['point'] for i in ids])
    closest, distance, triangles = trimesh.proximity.closest_point(mesh, points)
    for j, i in enumerate(ids):
        record = records[i]
        record['surface_distance_over_eye_span'] = float(distance[j]/span)
        if distance[j] > .04*span:
            record['status'] = 'too_far_from_surface'
            continue
        q = closest[j]
        visible = []
        for v in record['inlier_views']:
            c = cameras[v]
            if np.linalg.norm(project_pixels(c, q[None])[0]-observations[v, i]) > threshold:
                continue
            center = -np.array(c['R']).T @ c['t']
            ray = q-center
            length = np.linalg.norm(ray)
            hit, _, _ = mesh.ray.intersects_location(center[None], (ray/length)[None], multiple_hits=False)
            if len(hit) and abs(np.linalg.norm(hit[0]-center)-length) < span*1e-4:
                visible.append(v)
        record['visible_surface_views'] = visible
        if len(visible) < 3:
            record['status'] = 'insufficient_visible_surface_views'
            continue
        record.update(status='supported', attachment={'kind': 'barycentric', 'triangle_index': int(triangles[j]),
                      'weights': trimesh.triangles.points_to_barycentric(mesh.triangles[triangles[j]][None], q[None])[0].tolist()},
                      surface_point=q.tolist())


def preview(mesh, camera, path, points=(), yaw=0., reference=None):
    # Display only: decimation does not affect the tested/exported full surface.
    display = mesh.simplify_quadric_decimation(face_count=18000) if len(mesh.faces) > 18000 else mesh
    rotation = np.array(camera['R'])
    q = np.asarray(display.vertices) @ rotation.T
    reference_q = np.asarray((reference if reference is not None else mesh).vertices) @ rotation.T
    center = np.median(reference_q, axis=0)
    yrot = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
    q = (q-center) @ yrot.T
    scale = 480/np.ptp(reference_q, axis=0)[:2].max()
    xy = q[:, :2]*scale+[300, 300]
    image = Image.new('RGB', (600, 600), '#192e3b')
    draw = ImageDraw.Draw(image)
    tris = q[display.faces]
    normals = np.cross(tris[:, 1]-tris[:, 0], tris[:, 2]-tris[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-15)
    for f in np.argsort(tris[:, :, 2].mean(axis=1))[::-1]:
        shade = int(85+150*abs(normals[f] @ np.array([-.3, -.4, -.866])))
        draw.polygon([tuple(p) for p in xy[display.faces[f]]], fill=(shade, int(shade*.98), int(shade*.92)))
    for p in points:
        a = ((np.array(p) @ rotation.T-center) @ yrot.T)[:2]*scale+[300, 300]
        draw.ellipse((a[0]-2, a[1]-2, a[0]+2, a[1]+2), fill='#ffd34c')
    image.save(path)


def run(args):
    if args.reference_trial and not args.reference_session:
        raise ValueError('A reference trial requires its reference session')
    folder, predictions, out = Path(args.session), Path(args.predictions), Path(args.out)
    state = json.loads((folder/'session.json').read_text())
    pred_report = json.loads((predictions/'report.json').read_text())
    template, _, faces, model = load_model(args.model)
    # Geometric sampling regions only: not validated anatomical labels.
    menton_y = -.055
    lower = np.flatnonzero((template[:, 1] < menton_y) & (template[:, 2] > -.045))
    other = np.setdiff1d(np.arange(len(template)), lower)
    ids = np.unique(np.r_[lower[np.linspace(0, len(lower)-1, min(300, len(lower)), dtype=int)],
                         other[np.linspace(0, len(other)-1, min(300, len(other)), dtype=int)]])
    slots, cameras, observations = [], [], []
    input_hashes = {}
    for view in pred_report['views']:
        slot = view['slot']
        camera = state['result']['cameras'].get('registered:'+slot+'.png')
        if camera is None:
            continue
        path = folder/(slot+'.png')
        if digest(path) != view['image_sha256']:
            raise ValueError('Prediction/photo hash mismatch')
        if camera.get('mirrored') is not False or camera['model'] != 'SIMPLE_RADIAL':
            raise ValueError('Expected original unmirrored SIMPLE_RADIAL cameras')
        slots.append(slot); cameras.append(camera)
        observations.append(np.load(predictions/(slot+'.npz'), allow_pickle=False)['vertex_coord'][ids])
        input_hashes[slot] = {'image': digest(path), 'prediction': digest(predictions/(slot+'.npz'))}
    observations = np.array(observations)
    out.mkdir(parents=True, exist_ok=False)
    raw_path = folder/state['result']['full_mesh']
    raw = trimesh.load(raw_path, process=False)
    from .regional_inspection import define_regions
    front = state['result']['cameras'][state['result']['frontal_camera_key']]
    _, span, _ = define_regions(raw, front, state['result']['raw_predictions'])
    if span is None or span <= 0:
        raise ValueError('Missing eye proxy normalizer')
    normalizer = {'method': 'raw detector eye-proxy ray hits'}
    if args.reference_session:
        reference_folder = Path(args.reference_session)
        reference = json.loads((reference_folder/'session.json').read_text())
        reference_mesh = trimesh.load(reference_folder/reference['result']['full_mesh'], process=False)
        reference_camera = reference['result']['cameras'][reference['result']['frontal_camera_key']]
        _, reference_span, _ = define_regions(reference_mesh, reference_camera, reference['result']['raw_predictions'])
        reference_cameras = [reference['result']['cameras']['registered:'+slot+'.png'] for slot in slots]
        centers = np.array([-np.array(c['R']).T @ c['t'] for c in cameras])
        reference_centers = np.array([-np.array(c['R']).T @ c['t'] for c in reference_cameras])
        ratios = [np.linalg.norm(centers[a]-centers[b])/np.linalg.norm(reference_centers[a]-reference_centers[b])
                  for a, b in itertools.combinations(range(len(slots)), 2)
                  if np.linalg.norm(reference_centers[a]-reference_centers[b]) > reference_span*.3]
        if args.reference_trial:
            reference_trial = json.loads(Path(args.reference_trial).read_text())
            if reference_trial['session_id'] != reference['id'] or reference_trial['raw_sha256'] != digest(reference_folder/reference['result']['full_mesh']):
                raise ValueError('Reference trial source differs')
            reference_span = reference_trial['eye_proxy_span']
        ratio = float(np.median(ratios))
        span = reference_span*ratio
        normalizer = {'method': 'reference eye proxy transferred by median matched camera baseline ratio',
                      'reference_session': reference['id'], 'reference_span': reference_span,
                      'camera_baseline_scale_ratio': ratio, 'ratio_p05_p95': np.percentile(ratios, [5,95]).tolist()}
    print('Triangulating', len(ids), 'sampled vertices across', slots, flush=True)
    records = triangulate(cameras, observations)
    for vertex, record in zip(ids, records):
        record.update(vertex_id=int(vertex), region='lower_template' if vertex in lower else 'other_template')
    print('Attaching', sum(r['status'] == 'consistent' for r in records), 'consensus points', flush=True)
    attach(raw, records, cameras, observations, span)
    supported = [r for r in records if r['status'] == 'supported']
    from collections import Counter
    report = {'version': 'photogrammetry_trial_v1', 'session_id': state['id'], 'units': 'reconstruction_unit',
              'raw_sha256': digest(raw_path), 'session_sha256': digest(folder/'session.json'), 'prediction_report_sha256': digest(predictions/'report.json'), 'model': model, 'predictions': input_hashes,
              'camera_source': 'fixed original COLMAP; no FLAME poses or relative depths', 'slots': slots,
              'thresholds': {'reprojection_pixels': 6, 'minimum_views': 3, 'minimum_angle_degrees': 3,
                             'surface_distance_over_eye_span': .04},
              'lower_region_definition': 'neutral template y < -0.055 and z > -0.045; sampling region, not anatomical labels',
              'eye_proxy_span': span, 'normalizer': normalizer, 'status_counts': dict(Counter(r['status'] for r in records)),
              'region_counts': {region: dict(Counter(r['status'] for r in records if r['region'] == region))
                                for region in ('lower_template', 'other_template')},
              'points': records, 'variants': [], 'interpretation': 'exploratory consistency, not anatomical accuracy; thresholds not validated'}
    front = state['result']['cameras'][state['result']['frontal_camera_key']]
    meshes = [('raw', raw)]
    for cycles in (1, 3, 5):
        mesh, pinned = smooth(raw, cycles)
        mesh.export(out/f'taubin-{cycles}.ply')
        displacement = np.linalg.norm(mesh.vertices-raw.vertices, axis=1)/span
        n0 = raw.face_normals; n1 = mesh.face_normals
        report['variants'].append({'name': f'taubin-{cycles}', 'cycles': cycles, 'lambda': .5, 'nu': .53,
            'pinned_boundary_vertices': len(pinned), 'rms_displacement_over_eye_span': float(np.sqrt(np.mean(displacement**2))),
            'p95_displacement_over_eye_span': float(np.percentile(displacement, 95)),
            'maximum_displacement_over_eye_span': float(displacement.max()),
            'normal_direction_changes': int((np.sum(n0*n1, axis=1) < 0).sum()),
            'degenerate_faces': int((mesh.area_faces < 1e-15).sum()),
            'topology_unchanged': bool(np.array_equal(mesh.faces, raw.faces)),
            'self_intersections': 'not_checked'})
        meshes.append((f'taubin-{cycles}', mesh))
    for name, mesh in meshes:
        print('Preview', name, flush=True)
        for label, angle in [('front', 0), ('profile', np.pi/2)]:
            preview(mesh, front, out/f'{name}-{label}.png', yaw=angle, reference=raw)
    # Photo markers: green supported, orange consensus rejected by surface, red no consensus.
    for v, slot in enumerate(slots):
        image = Image.open(folder/(slot+'.png')).convert('RGB')
        draw = ImageDraw.Draw(image)
        for j, record in enumerate(records):
            if record['region'] != 'lower_template':
                continue
            x, y = observations[v, j]
            if not np.isfinite([x, y]).all():
                continue
            color = '#20d97f' if record['status'] == 'supported' and v in record['visible_surface_views'] else '#ffb347' if record.get('inlier_views') and v in record['inlier_views'] else '#f04455'
            draw.ellipse((x-2, y-2, x+2, y+2), fill=color)
        image.thumbnail((960, 540)); image.save(out/f'{slot}-lower.jpg')
    report['algorithm_sha256'] = digest(__file__)
    (out/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    cards = ''.join(f'<article><h3>{name}</h3><img src="{name}-front.png"><img src="{name}-profile.png"></article>' for name, _ in meshes)
    photos = ''.join(f'<article><h3>{slot}</h3><img src="{slot}-lower.jpg"></article>' for slot in slots)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Photogrammetry experiment</title>'
        '<style>body{font:17px system-ui;max-width:1500px;margin:25px auto;color:#243b46}main{display:grid;grid-template-columns:1fr 1fr;gap:15px}img{max-width:100%}article>img{width:49%}#photos img{width:100%}pre{white-space:pre-wrap}</style>'
        '<h1>Photogrammetry smoothing and automatic correspondence trial</h1><p>Fixed reconstruction coordinates; identical framing. Display meshes are decimated only for rendering. Full exported variants retain original topology. No hole filling.</p>'
        '<p><a href="report.json">Download report and supported point attachments</a></p><h2>Automatic correspondence results</h2><pre>'+json.dumps(report['region_counts'], indent=2)+'</pre>'
        '<p>Lower-template sampling is a geometric region, not a validated under-chin landmark set. Green: supported in this view; orange: triangulation inlier but not supported here; red: rejected observation. Agreement does not prove anatomical accuracy. No physical scale or perimeter measurements accepted.</p>'
        '<h2>Raw and Taubin variants</h2><pre>'+json.dumps(report['variants'], indent=2)+'</pre><main>'+cards+'</main><h2>Lower-region predictions on original photos</h2><main id="photos">'+photos+'</main>')
    print(json.dumps(report['region_counts'], indent=2), flush=True)
    print(out/'review.html', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('session', 'predictions', 'model', 'out'):
        p.add_argument('--'+key, required=True)
    p.add_argument('--reference-session')
    p.add_argument('--reference-trial')
    run(p.parse_args())


if __name__ == '__main__':
    main()
