"""Geometry screening, not anatomical accuracy or a smoothing objective."""
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from .depth_quality import POLICY


def summary(values):
    values = np.asarray(values)
    return {'count': len(values), 'mean': float(values.mean()), 'rms': float(np.sqrt(np.mean(values**2))),
            'median': float(np.median(values)), 'p95': float(np.quantile(values, .95)), 'sampled_max': float(values.max())} if len(values) else {'count': 0}


def distances(target, points):
    result = []
    for i in range(0, len(points), 128):
        result.extend(trimesh.proximity.closest_point(target, points[i:i+128])[1])
    return np.asarray(result)


def topology(mesh):
    counts = np.bincount(mesh.edges_unique_inverse)
    adjacent = mesh.face_adjacency
    graph = coo_matrix((np.ones(len(adjacent)), (adjacent[:, 0], adjacent[:, 1])), shape=(len(mesh.faces),)*2)
    count, labels = connected_components(graph, directed=False)
    sizes = np.bincount(labels)
    return {'connected_face_components': int(count), 'largest_component_faces': int(sizes.max()),
            'boundary_edges': int(np.count_nonzero(counts == 1)), 'nonmanifold_edges': int(np.count_nonzero(counts > 2)),
            'watertight': bool(mesh.is_watertight), 'hole_count': None,
            'hole_status': 'boundary_edges_reported_exact_hole_count_not_inferred_for_open_nonmanifold_surfaces'}


def roughness(mesh, head_height):
    policy = POLICY['roughness']
    points, _ = trimesh.sample.sample_surface(mesh, policy['samples'], seed=policy['seed'])
    cloud, _ = trimesh.sample.sample_surface(mesh, policy['cloud_samples'], seed=policy['cloud_seed'])
    radius = head_height*policy['radius_fraction_of_raw_head_height']
    neighborhoods = cKDTree(cloud).query_ball_point(points, radius)
    residuals = []
    for indices in neighborhoods:
        if len(indices) < policy['minimum_neighbors']:
            continue
        local = cloud[indices]; centered = local-local.mean(axis=0)
        values = np.linalg.eigvalsh(centered.T@centered/len(local))
        residuals.append(np.sqrt(max(0., values[0])))
    return {**policy, 'radius_reconstruction_units': radius, 'plane_rms': summary(residuals),
            'plane_rms_fraction_of_raw_head_height': summary(np.asarray(residuals)/head_height),
            'limitations': 'Curvature, density, missing coverage and true detail affect local-plane residuals. Lower roughness alone is not a quality improvement.'}


def geometry_metrics(raw, candidate, camera, predictions):
    transform = lambda p: np.asarray(p)@np.asarray(camera['R']).T+np.asarray(camera['t'])
    view = transform(raw.vertices); height = float(np.ptp(view[:, 1]))
    if not np.isfinite(height) or height <= 0:
        raise ValueError('Invalid reference head extent.')
    policy = POLICY['coverage']; source, _ = trimesh.sample.sample_surface(raw, policy['samples'], seed=policy['seed'])
    target, _ = trimesh.sample.sample_surface(candidate, policy['samples'], seed=1)
    deviation = distances(candidate, source); reverse = distances(raw, target)
    tolerance = height*policy['distance_tolerance_fraction_of_raw_head_height']
    probes = {p['index']: p['point'] for p in predictions if p.get('status') == 'ok' and p.get('point')}
    regions = {}
    for label, index in [('nose_detector_proxy', 4), ('chin_detector_proxy', 152)]:
        chosen = np.linalg.norm(source-np.asarray(probes[index]), axis=1) < height*.10 if index in probes else np.zeros(len(source), dtype=bool)
        regions[label] = chosen
    projected = transform(source); lo = view.min(axis=0); extent = np.ptp(view, axis=0)
    middle = (projected[:, 1] > lo[1]+.3*extent[1]) & (projected[:, 1] < lo[1]+.8*extent[1])
    regions['image_left_lateral_head_proxy'] = middle & (projected[:, 0] < lo[0]+.15*extent[0])
    regions['image_right_lateral_head_proxy'] = middle & (projected[:, 0] > lo[0]+.85*extent[0])
    region_report = {}
    for name, chosen in regions.items():
        values = deviation[chosen]
        region_report[name] = {'source_samples': len(values), 'retention_within_tolerance': float(np.mean(values <= tolerance)) if len(values) else None,
                               'displacement': summary(values), 'status': 'screened_proxy' if len(values) >= 10 else 'insufficient_samples'}
    retained = float(np.mean(deviation <= tolerance))
    missing = [name for name, data in region_report.items() if data['retention_within_tolerance'] is not None and data['retention_within_tolerance'] < policy['minimum_region_retention']]
    return {'version': 'webcam_depth_geometry_metrics_v1', 'units': 'reconstruction_unit',
            'raw_head_height': height, 'vertices': len(candidate.vertices), 'faces': len(candidate.faces),
            'face_retention_fraction': len(candidate.faces)/len(raw.faces), 'topology': topology(candidate),
            'roughness': roughness(candidate, height),
            'displacement': {'method': 'area_weighted_surface_samples_to_nearest_triangle_surface', 'samples_per_direction': len(source),
                             'seeds': [0, 1], 'raw_to_variant': summary(deviation), 'variant_to_raw': summary(reverse), 'is_hausdorff_bound': False},
            'coverage': {**policy, 'tolerance_reconstruction_units': tolerance, 'global_retention_within_tolerance': retained,
                         'regions': region_report, 'flagged_regions': missing,
                         'outcome': 'inadequate_coverage' if retained < policy['minimum_global_retention'] or missing else 'manual_review_required',
                         'manual_ear_nose_chin_review': 'pending', 'limitations': 'Detector/lateral-head proxies do not establish anatomical landmarks or complete ear coverage.'}}
