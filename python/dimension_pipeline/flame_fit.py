"""Offline, immutable FLAME Open fits to a webcam session's analysis surface.

Run with --help. No Pixel3DMM code, network access, full-mesh fitting, camera
updates, anatomical landmark transfer, calibration, or session writes.
"""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np
import trimesh
from scipy.optimize import lsq_linear

from .flame_open import load_model, DOWNLOAD_URL, LICENSE_URL
from .mesh_comparison import checked_mesh, mesh_identity
from .regional_inspection import ray_hits

VERSION = 'webcam-flame-analysis-fit-v1'


def similarity(source, target, weights=None):
    """Proper (no reflection) similarity, row-vector convention y=s*x@R.T+t."""
    source, target = np.asarray(source), np.asarray(target)
    w = np.ones(len(source)) if weights is None else np.asarray(weights)
    w = w / w.sum()
    a, b = w @ source, w @ target
    x, y = source-a, target-b
    u, d, vt = np.linalg.svd((x*w[:, None]).T @ y)
    sign = np.ones(3); sign[-1] = np.sign(np.linalg.det(vt.T @ u.T))
    rotation = vt.T @ np.diag(sign) @ u.T
    scale = float(d @ sign / np.sum(w[:, None]*x*x))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Degenerate similarity alignment.')
    return scale, rotation, b-scale*(rotation @ a)


def outside(points, exclusions):
    keep = np.ones(len(points), dtype=bool)
    for patch in exclusions:
        keep &= np.linalg.norm(points-np.asarray(patch['center']), axis=1) > patch['radius']
    return keep


def nearest(mesh, points):
    rows = [trimesh.proximity.closest_point(mesh, points[i:i+128])
            for i in range(0, len(points), 128)]
    return tuple(np.concatenate([r[j] for r in rows]) for j in range(3))


def fit(template, basis, faces, vertex_ids, target, initial, span, exclusions,
        components=50, iterations=25, regularity=0.0001, progress=None, importance=None,
        arc_constraints=None, arc_weight=0.):
    """Alternating trimmed robust surface ICP and bounded linear shape fitting.

    Fixed source vertex quadrature is weighted by neutral incident face area.
    Correspondences are nearest *triangles*, not target vertices. Excluded
    target triangles are removed before this function; queries inside the same
    exclusion sphere are also rejected so they cannot pull onto its rim.
    """
    if components not in (50, 100, 300) or basis.shape[2] < components:
        raise ValueError('Choose 50, 100 or 300 available shape components.')
    if not np.isfinite(span) or span <= 0 or not 1 <= iterations <= 100 or not 0 < regularity <= 1:
        raise ValueError('Invalid fit settings.')
    if not np.isfinite(arc_weight) or not 0<=arc_weight<=1:
        raise ValueError('Arc loss weight must be between zero and one.')
    # Normalize the optimizer, not the stored geometry, so fixed numerical
    # tolerances and nearest-triangle queries behave across arbitrary SfM units.
    unit = span
    target = trimesh.Trimesh(np.asarray(target.vertices)/unit, target.faces, process=False)
    exclusions = [{**p, 'center': (np.asarray(p['center'])/unit).tolist(), 'radius': p['radius']/unit} for p in exclusions]
    initial = (initial[0]/unit, initial[1], np.asarray(initial[2])/unit)
    span = 1.
    constraints=[]
    for c in (arc_constraints or []):
        points=np.asarray(c['template'],dtype=float);modes=np.asarray(c['basis'],dtype=float)
        edges=np.asarray(c['edges'])
        if (points.ndim!=2 or points.shape[1]!=3 or modes.shape[:2]!=points.shape or
            modes.ndim!=3 or modes.shape[2]<components or not np.isfinite(points).all() or
            not np.isfinite(modes).all() or edges.ndim!=2 or edges.shape[1]!=2 or not len(edges) or
            not np.issubdtype(edges.dtype,np.integer) or np.any(edges<0) or np.any(edges>=len(points)) or
            not np.isfinite(c['target_length']) or c['target_length']<=0):
            raise ValueError('Invalid fixed arc geometry or target length.')
        constraints.append({**c,'template':points,'basis':modes,'edges':edges,'target_length':c['target_length']/unit})
    if arc_weight and not constraints: raise ValueError('Arc loss needs covered reconstruction-derived targets.')
    if constraints:
        from .flame_arc_loss import length_jacobian
    v = np.asarray(template)[vertex_ids]; b = np.asarray(basis)[vertex_ids, :, :components]
    neutral = trimesh.Trimesh(template, faces, process=False)
    areas = np.zeros(len(template))
    np.add.at(areas, faces.ravel(), np.repeat(neutral.area_faces/3, 3))
    area = areas[vertex_ids]; area /= area.mean()
    importance = np.ones(len(vertex_ids)) if importance is None else np.asarray(importance,dtype=float)
    if importance.shape!=(len(vertex_ids),) or not np.isfinite(importance).all() or np.any(importance<1) or np.any(importance>10):
        raise ValueError('Regional importance must contain one finite weight 1–10 per fitting vertex.')
    beta = np.zeros(components); scale, rotation, translation = initial
    history = []
    for step in range(iterations):
        shaped = v + np.einsum('vck,k->vc', b, beta)
        world = scale*shaped @ rotation.T + translation
        closest, distance, _ = nearest(target, world)
        valid = outside(world, exclusions) & outside(closest, exclusions) & np.isfinite(distance)
        if valid.sum() < max(100, len(v)//3):
            raise ValueError('Insufficient facial overlap outside excluded patches.')
        threshold = min(float(np.quantile(distance[valid], .9)), span*.15)
        # Do not let global trimming silently discard a consistently displaced
        # high-priority bridge patch. The hard gate and Cauchy loss still apply.
        valid &= (distance <= threshold) | ((importance > 1) & (distance <= span*.15))
        if valid.sum() < 100:
            raise ValueError('Insufficient inlier surface coverage.')
        # Cauchy weights with a fixed, eye-span-relative influence scale.
        base_weight = area[valid]/(1+(distance[valid]/(span*.025))**2)
        weight = base_weight*importance[valid]
        scale, rotation, translation = similarity(shaped[valid], closest[valid], weight)
        if arc_weight:
            # Optimize global scale under the same surface and arc objective;
            # translation remains the weighted centroid alignment at that scale.
            w=weight/weight.sum();a=w@shaped[valid];center=w@closest[valid]
            x=(shaped[valid]-a)@rotation.T;y=closest[valid]-center
            numerator=float(np.sum(weight[:,None]*x*y));denominator=float(np.sum(weight[:,None]*x*x))
            strength=arc_weight*base_weight.sum()/len(constraints)
            for c in constraints:
                length,_=length_jacobian(c['template'],c['basis'],c['edges'],beta,1.)
                numerator+=strength*length/c['target_length'];denominator+=strength*(length/c['target_length'])**2
            scale=numerator/denominator;translation=center-scale*(rotation@a)
        if not 0.5*initial[0] < scale < 2*initial[0]:
            raise ValueError('Alignment scale diverged from eye-based initialization.')
        transformed_basis = scale*np.einsum('ij,vjk->vik', rotation, b[valid])
        rhs = closest[valid]-(scale*v[valid] @ rotation.T+translation)
        root = np.sqrt(weight)
        design = (transformed_basis*root[:, None, None]).reshape(-1, components)
        residual = (rhs*root[:, None]).ravel()
        penalty = np.sqrt(regularity*base_weight.sum())*span
        if arc_weight:
            extra=[];targets=[]
            for c in constraints:
                length,gradient=length_jacobian(c['template'],c['basis'],c['edges'],beta,scale)
                strength=np.sqrt(arc_weight*base_weight.sum()/len(constraints))/c['target_length']
                extra.append(strength*gradient);targets.append(strength*(c['target_length']-length+gradient@beta))
            design=np.vstack([design,extra]);residual=np.r_[residual,targets]
        solution = lsq_linear(np.vstack([design, penalty*np.eye(components)]),
                              np.r_[residual, np.zeros(components)], bounds=(-3., 3.),
                              method='bvls', tol=1e-7, max_iter=100)
        if not solution.success or not np.isfinite(solution.x).all():
            raise ValueError('Bounded FLAME coefficient solve failed.')
        delta = float(np.linalg.norm(solution.x-beta)); beta = solution.x
        history.append({'iteration': step+1, 'inliers': int(valid.sum()),
                        'trim_threshold': threshold*unit, 'rms_before_update': float(np.sqrt(np.mean(distance[valid]**2)))*unit,
                        'coefficient_step_l2': delta})
        if progress: progress(history[-1])
        if step >= 7 and delta < 1e-4: break
    coefficients = np.zeros(300); coefficients[:components] = beta
    vertices = scale*(template+np.einsum('vck,k->vc', basis, coefficients)) @ rotation.T+translation
    _, distances, _ = nearest(target, vertices[vertex_ids])
    valid = outside(vertices[vertex_ids], exclusions)
    values = distances[valid]
    if not len(values): raise ValueError('No evaluable fitted facial vertices.')
    return vertices*unit, {'components': components, 'shape_coefficients': coefficients.tolist(),
                      'expression': 'zero', 'articulated_pose': 'zero',
                      'transform': {'equation': 'X_reconstruction = scale * R * X_model + t',
                                    'scale_reconstruction_units_per_model_unit': scale*unit,
                                    'R': rotation.tolist(), 't': (translation*unit).tolist()},
                      'history': history, 'coefficient_bound': 3., 'regularity': regularity,
                      'optimization_stop': 'coefficient_step_tolerance' if delta < 1e-4 and step >= 7 else 'iteration_budget',
                      'fit_sample_count': len(vertex_ids), 'evaluated_vertices_outside_exclusion': int(valid.sum()),
                      'residual': {'direction': 'FLAME_face_vertices_to_fitting_target_triangles',
                                   'rms': float(np.sqrt(np.mean(values**2)))*unit,
                                   'median': float(np.median(values))*unit, 'p95': float(np.quantile(values, .95))*unit,
                                   'rms_fraction_eye_proxy_span': float(np.sqrt(np.mean(values**2))/span)},
                      'status': 'completed_requires_visual_review'}


def prepare(state, template, faces, probe):
    result = state['result']; surface = result['surface']; raw = surface['mesh']
    if surface['units'] != 'reconstruction_unit':
        raise ValueError('This experiment requires the original unscaled analysis mesh.')
    target = checked_mesh(trimesh.Trimesh(raw['vertices'], raw['triangles'], process=False))
    if len(target.faces) > 40000:
        raise ValueError('Use the bounded analysis mesh (at most 40,000 triangles).')
    camera = result['cameras'][result['frontal_camera_key']]
    # Fresh intersections on this exact topology, never full-mesh attachments.
    anchors = ray_hits(target, camera, result['raw_predictions'], [33, 133, 362, 263, 10, 152, 4])
    if any(a['status'] != 'ok' for a in anchors.values()):
        raise ValueError('Missing eye/forehead/chin/nose proxy coverage; cannot initialize fit.')
    eye_a = (np.asarray(anchors[33]['point'])+anchors[133]['point'])/2
    eye_b = (np.asarray(anchors[362]['point'])+anchors[263]['point'])/2
    span = float(np.linalg.norm(eye_a-eye_b))
    model = trimesh.Trimesh(template, faces, process=False)
    components = sorted(trimesh.graph.connected_components(model.edges_unique, min_len=3), key=len, reverse=True)
    if len(components) != 3 or not all(300 <= len(c) <= 800 for c in components[1:]):
        raise ValueError('Expected Open FLAME head and two separate eyeball components.')
    eyes = np.array([template[c][np.argmax(template[c, 2])] for c in components[1:]])
    eyes = eyes[np.argsort(eyes[:, 0])]
    model_span = float(np.linalg.norm(eyes[1]-eyes[0])); eye_center = eyes.mean(axis=0)
    rotation = np.asarray(camera['R']).T @ np.diag([1., -1., -1.])
    scale = span/model_span; translation = (eye_a+eye_b)/2-scale*(rotation@eye_center)
    # Deterministic geometric face crop, recorded verbatim; no semantic labels
    # are inferred from these thresholds. Ears, scalp, neck and eyeballs not fit.
    keep = np.zeros(len(template), bool); keep[components[0]] = True
    keep &= (template[:, 1] > eye_center[1]-1.55*model_span)
    keep &= (template[:, 1] < eye_center[1]+.9*model_span)
    keep &= (np.abs(template[:, 0]-eye_center[0]) < 1.25*model_span)
    keep &= (template[:, 2] > eye_center[2]-.35*model_span)
    facial_faces = np.flatnonzero(keep[faces].all(axis=1))
    ids = np.unique(faces[facial_faces])
    # Crop target to the projected face envelope and its nearest frontal layer.
    from scipy.spatial import ConvexHull
    oval = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,
            148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
    predictions = result['raw_predictions']
    polygon = np.array([[predictions[i]['x']*camera['width'], predictions[i]['y']*camera['height']] for i in oval])
    hull = ConvexHull(polygon)
    centers = target.triangles_center
    view = centers @ np.asarray(camera['R']).T+camera['t']
    pixels = view[:, :2]/view[:, 2, None]*[camera['fx'], camera['fy']]+[camera['cx'], camera['cy']]
    inside = (pixels @ hull.equations[:, :2].T+hull.equations[:, 2] <= 0).all(axis=1) & (view[:, 2] > 0)
    origin = -np.asarray(camera['R']).T @ np.asarray(camera['t'])
    candidate = np.flatnonzero(inside)
    directions = centers[candidate]-origin
    first = target.ray.intersects_first(np.repeat(origin[None], len(candidate), axis=0), directions)
    visible = first == candidate
    exclusions = []
    if probe:
        if probe.get('version') != 'webcam-nose-probe-v1' or probe.get('session_id') != state['id'] or probe.get('source_id') != 'raw_full':
            raise ValueError('Use a raw-full diagnostic point from this session.')
        from .depth_experiments import contained, digest
        full = contained(Path(probe['_session_folder']), result['full_mesh'])
        if digest(full) != probe.get('source_sha256'):
            raise ValueError('Diagnostic point source hash differs from this session.')
        center = np.asarray(probe['point'], dtype=float)
        if center.shape != (3,) or not np.isfinite(center).all(): raise ValueError('Invalid exclusion point.')
        exclusions = [{'center': center.tolist(), 'radius': .12*span,
                       'method': 'sphere_at_user_diagnostic_point', 'radius_fraction_eye_proxy_span': .12,
                       'source_sha256': probe['source_sha256'], 'source_attachment': probe['attachment']}]
    else:
        exclusions = [{'center': anchors[4]['point'], 'radius': .15*span,
                       'method': 'unreviewed_detector_index_4_sphere', 'radius_fraction_eye_proxy_span': .15}]
    selected = candidate[visible]
    # Conservative triangle/sphere exclusion includes triangles crossing the
    # sphere even when their vertices lie outside it (bounding sphere test).
    radii = np.linalg.norm(target.triangles-centers[:, None], axis=2).max(axis=1)
    for patch in exclusions:
        selected = selected[np.linalg.norm(centers[selected]-patch['center'], axis=1) > patch['radius']+radii[selected]]
    if len(selected) < 500: raise ValueError('Insufficient visible facial target coverage.')
    return target, target.submesh([selected], append=True, repair=False), ids, facial_faces, (scale, rotation, translation), span, exclusions, camera


def run(session_folder, model_path, out, probe_path=None, counts=(50, 100, 300), iterations=25, mapping_path=None):
    if not counts or len(set(counts)) != len(counts) or any(c not in (50,100,300) for c in counts) or not 1 <= iterations <= 100:
        raise ValueError('Use distinct component counts 50/100/300 and 1–100 iterations.')
    folder = Path(session_folder).resolve(); out = Path(out).resolve()
    if out == folder or folder in out.parents:
        raise ValueError('Write fits outside the source session directory.')
    if out.exists(): raise ValueError('Output already exists; use a fresh experiment directory.')
    original = (folder/'session.json').read_bytes(); state = json.loads(original)
    if not re.fullmatch('[a-f0-9]{32}', state['id']): raise ValueError('Invalid session identity.')
    template, basis, faces, provenance = load_model(model_path)
    probe = json.loads(Path(probe_path).read_text()) if probe_path else None
    if probe: probe['_session_folder'] = str(folder)
    source, target, ids, facial_faces, initial, span, exclusions, camera = prepare(state, template, faces, probe)
    from .flame_mapping import validate, regions, topology_id, catalog
    mapping = None; importance = None; region_report = []
    if mapping_path:
        mapping = json.loads(Path(mapping_path).read_text())
        validate(mapping, provenance['model_sha256'], faces, template, state['id'], mesh_identity(state['result']['surface']['mesh']))
        # prepare initializes scale from target/model eye spans, so their ratio
        # recovers the exact neutral model eye span used for fitting.
        importance, region_report = regions(mapping, template, faces, ids, span/initial[0])
    report = {'version': VERSION, 'session_id': state['id'], 'source_session_sha256': hashlib.sha256(original).hexdigest(),
              'source_mesh_id': mesh_identity(state['result']['surface']['mesh']),
              'fitting_source': 'result.surface.mesh', 'source_units': 'reconstruction_unit',
              'model': {**provenance, 'license': 'CC-BY-4.0', 'license_url': LICENSE_URL, 'download_url': DOWNLOAD_URL,
                        'attribution': 'Li et al., Learning a model of facial shape and expression from 4D scans, SIGGRAPH Asia 2017; Max Planck Institute for Intelligent Systems.'},
              'algorithm_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'mapping_algorithm_sha256': hashlib.sha256(Path(__file__).with_name('flame_mapping.py').read_bytes()).hexdigest(),
              'flame_topology_id': topology_id(faces), 'flame_vertex_count':len(template), 'flame_triangle_count':len(faces),
              'arkit_analog_catalog':catalog(), 'regional_mapping':mapping,
              'regional_mapping_sha256':hashlib.sha256(Path(mapping_path).read_bytes()).hexdigest() if mapping_path else None,
              'regional_policy':{'distance':'neutral_FLAME_edge_geodesic', 'falloff':'1+(multiplier-1)*(1-(d/r)^2)^2; d<r',
                                 'overlap':'maximum_not_sum', 'shape_prior':'same_base_weight_normalization',
                                 'inliers':'priority vertices bypass global 90% trim; same 0.15-span hard gate and Cauchy influence',
                                 'exclusions':'unchanged; exclusions override regional weights', 'regions':region_report},
              'eye_proxy_span': span, 'exclusions': exclusions, 'target_triangles': len(target.faces),
              'face_crop': {'model': 'head component; y in eye_center_y+[-1.55,0.9]*eye_span; abs(x-eye_center_x)<1.25*eye_span; z>eye_center_z-0.35*eye_span',
                            'target': 'detector face-oval convex hull; nearest frontal layer; conservative exclusion spheres'},
              'method': 'independent_neutral_shape_fits_area_weighted_trimmed_cauchy_point_to_triangle_ICP',
              'maximum_iterations': iterations, 'variants': [], 'calibration_transferred': False,
              'limitations': ['No ear, scalp, back-of-head or neck fitting.', 'Excluded nose patch is inferred from FLAME shape prior and surrounding fit.',
                             'Detector proxies initialize alignment; they are not reviewed landmarks.',
                             'Analysis decimation can change anatomy; lower residual does not establish accuracy.',
                             'New topology: no annotation or tape-route transfer. Model scale is fitted, not measured.',
                             'No expression fit, photo loss, self-intersection repair, smoothing or local blending.']}
    out.mkdir(parents=True)
    def save(): (out/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    source.export(out/'analysis.ply'); target.export(out/'fitting-target.ply')
    (out/'face-topology.json').write_text(json.dumps({'topology_id':topology_id(faces),
                                                    'original_vertex_ids':ids.tolist(),
                                                    'original_triangle_ids':facial_faces.tolist(),
                                                    'original_triangles':faces[facial_faces].tolist()}))
    save()
    trials=[(count,weighted) for count in counts for weighted in ([False,True] if mapping else [False])]
    for count, weighted in trials:
        started = time.monotonic()
        key=f'{count}-regional' if weighted else str(count)
        print(f'Fitting {key} components to {len(target.faces)} analysis triangles', flush=True)
        vertices, row = fit(template, basis, faces, ids, target, initial, span, exclusions, count, iterations,
                            progress=lambda h: print(f"  iteration {h['iteration']}: {h['inliers']} inliers, RMS {h['rms_before_update']:.6f}", flush=True),
                            importance=importance if weighted else None)
        row.update(id=key, weighting='regional' if weighted else 'ordinary')
        fitted = trimesh.Trimesh(vertices, faces, process=False)
        face = fitted.submesh([facial_faces], append=True, repair=False)
        neutral_normals = np.cross(template[faces[:,1]]-template[faces[:,0]], template[faces[:,2]]-template[faces[:,0]])
        fitted_normals = np.cross(vertices[faces[:,1]]-vertices[faces[:,0]], vertices[faces[:,2]]-vertices[faces[:,0]])
        rotated = neutral_normals @ np.asarray(row['transform']['R']).T
        row['geometry_checks'] = {'degenerate_triangles': int(np.count_nonzero(fitted.area_faces <= 1e-14*span**2)),
                                  'normal_reversals_vs_transformed_neutral': int(np.count_nonzero(np.einsum('ij,ij->i',rotated,fitted_normals)<0)),
                                  'self_intersections': 'not_checked'}
        if row['geometry_checks']['degenerate_triangles']: raise ValueError('Fit creates degenerate triangles.')
        points, _ = trimesh.sample.sample_surface(target, 2000, seed=41)
        points = points[outside(points, exclusions)]
        _, reverse_distance, _ = nearest(face, points)
        row['target_to_flame_face'] = {'method':'area_weighted_triangle_samples_to_nearest_triangles', 'samples':len(points), 'seed':41,
                                        'rms':float(np.sqrt(np.mean(reverse_distance**2))), 'p95':float(np.quantile(reverse_distance,.95))}
        row['regional_metrics']=[]
        for region in region_report:
            selected=np.asarray(region['vertex_ids'],dtype=int)
            selected=selected[outside(vertices[selected],exclusions)]
            if not len(selected):
                row['regional_metrics'].append({'arkit_index':region['arkit_index'], 'status':'excluded_or_outside_crop','vertices':0})
                continue
            _,dist,_=nearest(target,vertices[selected])
            row['regional_metrics'].append({'arkit_index':region['arkit_index'], 'status':'ok','vertices':len(selected),
                                            'rms':float(np.sqrt(np.mean(dist**2))), 'p95':float(np.quantile(dist,.95)),
                                            'rms_fraction_eye_proxy_span':float(np.sqrt(np.mean(dist**2))/span)})
        fitted.export(out/f'flame-{key}.ply'); face.export(out/f'flame-{key}-face.ply')
        row.update(seconds=time.monotonic()-started, full_mesh=f'flame-{key}.ply', face_mesh=f'flame-{key}-face.ply')
        row['full_mesh_sha256'] = hashlib.sha256((out/row['full_mesh']).read_bytes()).hexdigest()
        row['face_mesh_sha256'] = hashlib.sha256((out/row['face_mesh']).read_bytes()).hexdigest()
        report['variants'].append(row); save()
    if (folder/'session.json').read_bytes() != original: raise ValueError('Source session changed during fitting; review provenance.')
    from .flame_fit_view import write_view
    write_view(out, report, source, target, camera)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True, help='FLAME2023Open.zip or flame2023_Open.pkl')
    parser.add_argument('--out', type=Path, required=True, help='Fresh private experiment directory outside source session')
    parser.add_argument('--exclude-probe', type=Path, help='Exported nose-point JSON for this session')
    parser.add_argument('--components', type=int, nargs='+', choices=[50,100,300], default=[50,100,300])
    parser.add_argument('--iterations', type=int, default=25)
    parser.add_argument('--mapping', type=Path, help='Reviewed FLAME analog mapping JSON; run matched ordinary/regional fits')
    args = parser.parse_args()
    try: run(args.session, args.model, args.out, args.exclude_probe, tuple(args.components), args.iterations, args.mapping)
    except (ValueError, OSError, KeyError) as exc: parser.exit(1, f'FLAME fit failed: {exc}\n')
