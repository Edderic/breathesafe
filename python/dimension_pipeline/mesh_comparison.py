"""Read-only, sampled comparisons in the reconstruction's existing coordinates."""
import hashlib
import io
import json
import re
from pathlib import Path

import numpy as np
import trimesh

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_VERTICES = 1_000_000
MAX_TRIANGLES = 2_000_000


def mesh_identity(mesh):
    """Order-sensitive identity: barycentric indices are meaningful only here."""
    payload = json.dumps(mesh, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return 'sha256:' + hashlib.sha256(payload.encode()).hexdigest()


def checked_mesh(mesh):
    if (not 3 <= len(mesh.vertices) <= MAX_VERTICES or
            not 1 <= len(mesh.faces) <= MAX_TRIANGLES or
            mesh.faces.ndim != 2 or mesh.faces.shape[1] != 3 or
            np.any(mesh.faces < 0) or np.any(mesh.faces >= len(mesh.vertices)) or
            not np.isfinite(mesh.vertices).all() or not np.isfinite(mesh.area_faces).all() or
            np.any(mesh.area_faces <= 0)):
        raise ValueError('Inspection mesh is empty, nonfinite, degenerate or exceeds resource limits.')
    return mesh


def sampled_deviation(source, target, count, seed, scale):
    points, _ = trimesh.sample.sample_surface(source, count, seed=seed)
    distances = []
    # Bound the temporary nearest-triangle query allocations on detailed meshes.
    for offset in range(0, count, 128):
        _, distance, _ = trimesh.proximity.closest_point(target, points[offset:offset+128])
        distances.extend(distance * scale)
    values = np.asarray(distances)
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite surface-deviation result.')
    return {'sample_count': count, 'seed': seed, 'mean': float(values.mean()),
            'rms': float(np.sqrt(np.mean(values ** 2))), 'median': float(np.median(values)),
            'p95': float(np.quantile(values, .95)), 'sampled_max': float(values.max())}


def compare_session(folder, state, count=5000, variant='raw'):
    # Future filtered/refined providers must register artifacts and provenance here;
    # a requested variant is never interpreted as a filesystem path.
    if variant != 'raw':
        raise ValueError('Unknown inspection variant.')
    if type(count) is not int or not 1 <= count <= 10000:
        raise ValueError('Invalid deviation sample count.')
    result = state.get('result')
    if not result:
        raise ValueError('Reconstruct a surface before comparing meshes.')
    folder = Path(folder).resolve()
    path = (folder / result['full_mesh']).resolve()
    path.relative_to(folder)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('Full mesh exceeds the 64 MiB inspection limit. Original file is retained for download.')
    full_bytes = path.read_bytes()
    full_hash = hashlib.sha256(full_bytes).hexdigest()
    header_end = full_bytes.find(b'end_header', 0, 65536)
    if header_end < 0 or not full_bytes.startswith(b'ply\n'):
        raise ValueError('Missing or oversized full PLY header.')
    header = full_bytes[:header_end]
    counts = {}
    for name, limit in [('vertex', MAX_VERTICES), ('face', MAX_TRIANGLES)]:
        match = re.search(rb'(?:^|\n)element ' + name.encode() + rb' ([0-9]+)\r?\n', header)
        if not match or not 1 <= int(match[1]) <= limit:
            raise ValueError('Full PLY exceeds vertex/triangle inspection limits or is empty.')
        counts[name] = int(match[1])
    if b'format ascii ' in header and len(full_bytes) > 8 * 1024 * 1024:
        raise ValueError('ASCII PLY exceeds the 8 MiB inspection limit.')
    # Read the same bytes we hashed, with no processing/welding/repair.
    full = checked_mesh(trimesh.load(io.BytesIO(full_bytes), file_type='ply', force='mesh', process=False))
    if len(full.vertices) != counts['vertex'] or len(full.faces) != counts['face']:
        raise ValueError('Full PLY is not an unchanged triangular mesh; inspection will not triangulate or repair it.')
    raw = result['surface']['mesh']
    if not np.issubdtype(np.asarray(raw['triangles']).dtype, np.integer):
        raise ValueError('Analysis triangle indices must be integers.')
    analysis = checked_mesh(trimesh.Trimesh(vertices=raw['vertices'], faces=raw['triangles'], process=False))
    calibration = state.get('calibrated')
    scale = calibration['report']['mm_per_reconstruction_unit'] if calibration else 1.
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Invalid calibration scale.')
    units = 'mm' if calibration else result['surface']['units']
    if units not in ('mm', 'reconstruction_unit'):
        raise ValueError('Unknown mesh units.')
    settings = result.get('diagnostics', {}).get('mesh', {})
    analysis_id = mesh_identity(raw)
    return {
        'version': 'webcam_mesh_comparison_v1', 'session_id': state['id'], 'comparison_source_id': variant,
        'units': units, 'display_scale': scale, 'coordinate_alignment': 'shared_original_coordinates_no_registration_or_fit',
        'coordinate_frame': result['surface'].get('coordinate_frame'),
        'display_camera_key': result.get('frontal_camera_key'),
        'display_camera': (calibration or result).get('cameras', {}).get(result.get('frontal_camera_key')),
        'annotation_mesh_id': analysis_id, 'accuracy_status': 'not_independently_validated',
        'variants': [
            {'id': 'raw', 'kind': 'raw', 'label': 'Full reconstruction', 'mesh_id': 'sha256:' + full_hash,
             'sha256': full_hash, 'byte_length': len(full_bytes), 'vertices': len(full.vertices), 'triangles': len(full.faces),
             'mesh_url': f"/sessions/{state['id']}/mesh", 'storage_units': result['surface']['units'],
             'read_only': True, 'provenance': {'source': result['full_mesh'], 'operation': 'original_reconstruction',
                                             'smoothing': settings.get('smoothing'), 'hole_filling': settings.get('hole_filling')}},
            {'id': 'analysis', 'kind': 'analysis', 'label': 'Bounded analysis mesh', 'mesh_id': analysis_id,
             'vertices': len(analysis.vertices), 'triangles': len(analysis.faces),
             'storage_units': result['surface']['units'], 'read_only': True,
             'provenance': {'source': 'result.surface.mesh', 'parent_mesh_id': 'sha256:' + full_hash,
                            'method': settings.get('method', 'unknown'), 'target_faces': settings.get('target_faces'),
                            'smoothing': settings.get('smoothing'), 'hole_filling': settings.get('hole_filling')}}],
        'deviation': {
            'method': 'area_weighted_uniform_triangle_surface_samples_to_nearest_triangle_surface',
            'units': units, 'alignment': 'none', 'is_hausdorff_bound': False,
            'full_to_analysis': sampled_deviation(full, analysis, count, 0, scale),
            'analysis_to_full': sampled_deviation(analysis, full, count, 1, scale),
            'limitations': 'Sampled values can miss localized defects. Distances are simplification disagreement, not reconstruction or anatomical error.'},
    }
