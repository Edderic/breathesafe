"""Pinned CPU reconstruction adapter. No synthetic or statistical fallback."""
import hashlib
import json
import math
import platform
import re
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from .webcam_geometry import camera_pixel, project

REPO = Path(__file__).resolve().parents[2]
TOOLS = {'colmap': '4.2.1', 'InterfaceCOLMAP': '2.4.0', 'DensifyPointCloud': '2.4.0', 'ReconstructMesh': '2.4.0'}
MODEL_HASH = '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff'


def executable(tool):
    local = REPO/'tmp/webcam-tools/bin'/tool
    return str(local) if local.is_file() else shutil.which(tool)


def diagnostics():
    rows = {}
    diagnostic_folder = REPO/'tmp/webcam-tool-diagnostics'
    diagnostic_folder.mkdir(parents=True, exist_ok=True)
    for tool, version in TOOLS.items():
        path = executable(tool)
        output = ''
        if path:
            try:
                p = subprocess.run([path, '-h'], cwd=diagnostic_folder, capture_output=True, text=True, timeout=10)
                output = p.stdout+p.stderr
            except (OSError, subprocess.TimeoutExpired) as error:
                output = str(error)
        arch = subprocess.run(['file', '-b', str(Path(path).resolve())], capture_output=True, text=True).stdout.strip() if path else ''
        rows[tool] = {'path': path, 'required': version, 'architecture': arch,
                      'ok': 'arm64' in arch and bool(re.search(r'(?<![\d.])'+re.escape(version)+r'(?![\d.])', output)), 'banner': output[:500]}
    supported = platform.system() == 'Darwin' and platform.machine() == 'arm64'
    return {'platform': platform.platform(), 'native_macos_arm64': supported, 'tools': rows,
            'ready': supported and all(r['ok'] for r in rows.values())}


def read_model(folder):
    """Read COLMAP text models, preserving blank observation lines."""
    import numpy as np
    cameras = {}
    for line in (folder/'cameras.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        i, model, w, h, *p = line.split(); p = list(map(float, p))
        if model == 'SIMPLE_RADIAL':
            f, cx, cy, k = p; fx = fy = f
        elif model == 'PINHOLE':
            fx, fy, cx, cy = p; k = 0
        elif model == 'SIMPLE_PINHOLE':
            fx, cx, cy = p; fy = fx; k = 0
        else:
            raise ValueError('Unsupported COLMAP camera: '+model)
        cameras[int(i)] = {'model': model, 'width': int(w), 'height': int(h), 'fx': fx, 'fy': fy,
                           'cx': cx, 'cy': cy, 'k': k, 'units': 'reconstruction_unit', 'mirrored': False}
    lines = iter((folder/'images.txt').read_text().splitlines()); images = {}
    for line in lines:
        if not line or line.startswith('#'):
            continue
        fields = line.split(); i = int(fields[0]); qw, qx, qy, qz = map(float, fields[1:5])
        q = np.array([qw, qx, qy, qz]); q /= np.linalg.norm(q); w, x, y, z = q
        R = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
             [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
             [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
        obs = next(lines, '').split()
        images[fields[9]] = {**cameras[int(fields[8])], 'camera_id': int(fields[8]), 'image_id': i,
                            'R': R, 't': list(map(float, fields[5:8])), 'observations': len(obs)//3}
    return images


def detect(image_path):
    import mediapipe as mp
    if mp.__version__ != '0.10.32':
        raise ValueError('Expected pinned mediapipe-python 0.10.32.')
    model = REPO/'public/mediapipe/experiment/face_landmarker.task'
    if not model.is_file() or hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_HASH:
        raise ValueError('Cache the pinned face model: node scripts/setup_face_landmarker.cjs')
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model), delegate=mp.tasks.BaseOptions.Delegate.CPU),
        running_mode=mp.tasks.vision.RunningMode.IMAGE, num_faces=1)
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
        result = detector.detect(mp.Image.create_from_file(str(image_path)))
    if len(result.face_landmarks) != 1:
        raise ValueError('No frontal face detected.')
    return [{'x': p.x, 'y': p.y, 'z': p.z} for p in result.face_landmarks[0]], {
        'sdk': 'mediapipe-python', 'version': mp.__version__, 'model_sha256': MODEL_HASH,
        'delegate': 'CPU', 'image': 'undistorted frontal', 'running_mode': 'IMAGE'}


def reconstruct(folder, state, run, update, cancelled):
    import numpy as np
    import trimesh
    from PIL import Image
    started = time.monotonic()
    diag = diagnostics()
    if not diag['ready']:
        raise ValueError('Pinned native tools unavailable. Run diagnostics; see WEBCAM_PILOT.md.')
    frames = sorted(state['captures'], key=lambda c: c['slot'])
    reconstruction = [c for c in frames if c['role'] != 'frontal']
    frontal = next(c for c in frames if c['role'] == 'frontal')
    # Each attempt is immutable. Interrupted/retried work never consumes stale outputs.
    work = folder/('attempt-'+str(time.time_ns())); work.mkdir(mode=0o700)
    images, masks = work/'images', work/'masks'; images.mkdir(); masks.mkdir()
    for c in frames:
        # Dense processing sees head pixels only as well as masked sparse features.
        source = Image.open(folder/c['image']).convert('RGB')
        mask = Image.open(folder/c['mask']).convert('L')
        Image.composite(source, Image.new('RGB', source.size), mask).save(images/(c['slot']+'.png'))
        shutil.copyfile(folder/c['mask'], masks/(c['slot']+'.png.png'))
    names = [c['slot']+'.png' for c in reconstruction]
    (work/'reconstruction.txt').write_text('\n'.join(names)+'\n')
    (work/'frontal.txt').write_text(frontal['slot']+'.png\n')
    db = work/'database.db'; sparse = work/'sparse'; sparse.mkdir()
    def colmap(stage, command, *args):
        run(stage, [executable('colmap'), command, *map(str, args)], work)
    colmap('masked_features', 'feature_extractor', '--database_path', db, '--image_path', images,
           '--image_list_path', work/'reconstruction.txt', '--ImageReader.mask_path', masks,
           '--ImageReader.single_camera', '1', '--ImageReader.camera_model', 'SIMPLE_RADIAL',
           '--FeatureExtraction.use_gpu', '0', '--FeatureExtraction.max_image_size', '4096')
    # Explicit overlapping temporal pairs plus cross-pass pairs at matching head positions.
    pairs = {(a, b) for i, a in enumerate(names) for b in names[i+1:i+7]}
    for i in range(30):
        for j in range(max(0, i-2), min(30, i+3)):
            pairs.add((names[i], names[30+j]))
    (work/'pairs.txt').write_text('\n'.join(a+' '+b for a, b in sorted(pairs))+'\n')
    colmap('overlap_matching', 'matches_importer', '--database_path', db, '--match_list_path', work/'pairs.txt',
           '--match_type', 'pairs', '--FeatureMatching.use_gpu', '0')
    colmap('sparse_reconstruction', 'mapper', '--database_path', db, '--image_path', images, '--output_path', sparse,
           '--Mapper.ba_use_gpu', '0')
    models = []
    for candidate in sorted(sparse.iterdir()):
        if candidate.is_dir():
            colmap('inspect_sparse', 'model_converter', '--input_path', candidate, '--output_path', candidate, '--output_type', 'TXT')
            models.append((len(read_model(candidate)), candidate))
    if len(models) != 1:
        raise ValueError('Partial/disconnected reconstruction: expected one connected sparse model.')
    count, model = models[0]; before = read_model(model)
    if count < math.ceil(.9*len(names)) or frontal['slot']+'.png' in before or len({c['camera_id'] for c in before.values()}) != 1:
        raise ValueError('Insufficient reconstruction: require >=90% registered turn frames with one shared camera and no designated frontal.')
    dense = work/'dense'
    colmap('undistort_surface_images', 'image_undistorter', '--image_path', images, '--input_path', model,
           '--output_path', dense, '--output_type', 'COLMAP')
    colmap('read_dense_cameras', 'model_converter', '--input_path', dense/'sparse', '--output_path', dense/'sparse', '--output_type', 'TXT')
    dense_cameras = read_model(dense/'sparse')
    dense_masks = work/'dense_masks'; dense_masks.mkdir()
    for name, c in dense_cameras.items():
        source_mask = np.asarray(Image.open(masks/(name+'.png')).convert('L'))
        warped = Image.fromarray(undistort_mask(source_mask, before[name], c))
        # OpenMVS basenames exclude the image extension.
        warped.save(dense_masks/(Path(name).stem+'.mask.png'))
    run('openmvs_import', [executable('InterfaceCOLMAP'), '-i', str(dense), '-o', str(work/'scene.mvs'), '--image-folder', str(dense/'images')], work)
    # Native arm64 build has CUDA disabled. No patch_match_stereo GPU dependency.
    run('dense_reconstruction', [executable('DensifyPointCloud'), '-i', str(work/'scene.mvs'), '-o', str(work/'dense.mvs'),
                                 '--resolution-level', '0', '--max-resolution', '4096', '--min-resolution', '64',
                                 '--mask-path', str(dense_masks), '--ignore-mask-label', '0', '--tower-mode', '0',
                                 '--normalize-coordinates', '0', '--estimate-roi', '0', '--crop-to-roi', '0'], work)
    run('meshing', [executable('ReconstructMesh'), '-i', str(work/'dense.mvs'), '-o', str(work/'full.mvs'),
                    '--close-holes', '0', '--smooth', '0', '--remove-spurious', '0', '--remove-spikes', '0', '--decimate', '1', '--crop-to-roi', '0'], work)
    full = trimesh.load(work/'full.ply', force='mesh', process=False)
    if not len(full.faces) or not np.isfinite(full.vertices).all():
        raise ValueError('Meshing produced no finite surface.')
    # Keep full.ply byte-for-byte. QEM does not fill holes or smooth the analysis mesh.
    update('analysis_mesh')
    analysis = full
    if len(full.faces) > 18000 or len(full.vertices) > 20000:
        analysis = full.simplify_quadric_decimation(face_count=18000)
    if len(analysis.vertices) > 20000 or len(analysis.faces) > 40000:
        raise ValueError('Analysis mesh exceeds viewer limits.')
    if not len(analysis.faces) or not np.isfinite(analysis.vertices).all() or np.any(analysis.area_faces <= 0):
        raise ValueError('Analysis mesh contains empty, nonfinite or degenerate geometry.')
    rng = np.random.default_rng(0)
    sample = full.vertices[rng.choice(len(full.vertices), min(10000, len(full.vertices)), replace=False)]
    _, distances, _ = trimesh.proximity.closest_point(analysis, sample)
    mesh_report = {'full_vertices': len(full.vertices), 'full_triangles': len(full.faces),
                   'analysis_vertices': len(analysis.vertices), 'analysis_triangles': len(analysis.faces),
                   'method': 'quadric_decimation' if analysis is not full else 'identity', 'target_faces': 18000,
                   'hole_filling': False, 'smoothing': False, 'deviation_method': 'sampled_full_vertices_to_analysis_surface',
                   'deviation_sample_count': len(sample), 'deviation_max_reconstruction_units': float(max(distances)),
                   'deviation_rms_reconstruction_units': float(np.sqrt(np.mean(distances**2))),
                   'completeness': 'requires_manual_ear_nose_chin_coverage_review'}
    surface = {'surface_record_version': 'webcam-1.0.0', 'record_id': state['id'], 'units': 'reconstruction_unit',
               'coordinate_frame': {'handedness': 'right', 'convention': 'COLMAP arbitrary world; no anatomical alignment'},
               'source': {'domain': 'human', 'capture': 'local_webcam', 'synthetic': False},
               'scale': {'status': 'uncalibrated'}, 'accuracy_status': 'not_independently_validated',
               'mesh': {'vertices': analysis.vertices.tolist(), 'triangles': analysis.faces.tolist()}}
    # Register the held-out image only after the geometry is final. No bundle adjustment.
    with sqlite3.connect(db) as conn:
        camera_id = conn.execute('SELECT camera_id FROM cameras').fetchone()[0]
    colmap('frontal_features', 'feature_extractor', '--database_path', db, '--image_path', images,
           '--image_list_path', work/'frontal.txt', '--ImageReader.existing_camera_id', camera_id,
           '--ImageReader.mask_path', masks, '--FeatureExtraction.use_gpu', '0')
    (work/'frontal_pairs.txt').write_text('\n'.join(frontal['slot']+'.png '+n for n in names)+'\n')
    colmap('frontal_matching', 'matches_importer', '--database_path', db, '--match_list_path', work/'frontal_pairs.txt',
           '--match_type', 'pairs', '--FeatureMatching.use_gpu', '0')
    registered = work/'registered'; registered.mkdir()
    (work/'fixed_cameras.txt').write_text(str(camera_id)+'\n')
    colmap('frontal_registration', 'image_registrator', '--database_path', db, '--input_path', model, '--output_path', registered,
           '--Mapper.image_list_path', work/'frontal.txt', '--Mapper.constant_camera_list_path', work/'fixed_cameras.txt')
    colmap('inspect_registration', 'model_converter', '--input_path', registered, '--output_path', registered, '--output_type', 'TXT')
    after = read_model(registered)
    if frontal['slot']+'.png' not in after:
        raise ValueError('Designated frontal camera registration failed.')
    for name, camera in before.items():
        for key in ('R', 't', 'fx', 'fy', 'cx', 'cy', 'k'):
            if not np.allclose(camera[key], after[name][key], rtol=1e-8, atol=1e-8):
                raise ValueError('Registration changed the fixed reconstruction camera geometry.')
    # points3D IDs, positions and reprojection errors must remain unchanged.
    def positions(path):
        return {s[0]: s[1:4] for l in (path/'points3D.txt').read_text().splitlines() if l and not l.startswith('#') for s in [l.split()]}
    if positions(model) != positions(registered):
        raise ValueError('Registration changed fixed sparse geometry.')
    front_dense = work/'frontal_undistorted'
    # Detector receives the original held-out photo, undistorted with the registered camera.
    shutil.copyfile(folder/frontal['image'], images/(frontal['slot']+'.png'))
    colmap('undistort_frontal', 'image_undistorter', '--image_path', images, '--input_path', registered,
           '--output_path', front_dense, '--output_type', 'COLMAP', '--image_list_path', work/'frontal.txt')
    colmap('read_undistorted_cameras', 'model_converter', '--input_path', front_dense/'sparse', '--output_path', front_dense/'sparse', '--output_type', 'TXT')
    undistorted_cameras = read_model(front_dense/'sparse')
    camera_key = 'undistorted:'+frontal['slot']+'.png'
    cameras = {**{'registered:'+name: c for name, c in after.items()},
               **{'surface_undistorted:'+name: c for name, c in dense_cameras.items()},
               **{'undistorted:'+name: c for name, c in undistorted_cameras.items()}}
    camera = cameras[camera_key]
    image_path = front_dense/'images'/(frontal['slot']+'.png')
    if Image.open(image_path).size != (camera['width'], camera['height']):
        raise ValueError('Undistorted camera/image dimensions disagree.')
    update('frontal_detection')
    raw, provenance = detect(image_path)
    if cancelled():
        raise InterruptedError('Cancelled.')
    projected = project(surface['mesh'], camera, raw)
    errors = [float(l.split()[7]) for l in (model/'points3D.txt').read_text().splitlines() if l and not l.startswith('#')]
    points = {s[0]: list(map(float, s[1:4])) for l in (registered/'points3D.txt').read_text().splitlines() if l and not l.startswith('#') for s in [l.split()]}
    lines = iter((registered/'images.txt').read_text().splitlines()); frontal_errors = []
    for line in lines:
        if not line or line.startswith('#'):
            continue
        fields = line.split(); obs = next(lines, '').split()
        if fields[9] == frontal['slot']+'.png':
            for i in range(0, len(obs), 3):
                if obs[i+2] in points:
                    pixel = camera_pixel(after[fields[9]], points[obs[i+2]])
                    frontal_errors.append(math.dist(pixel, list(map(float, obs[i:i+2]))))
    result = {'surface': surface, 'cameras': cameras, 'frontal_camera_key': camera_key,
              'frontal_undistorted': image_path.relative_to(folder).as_posix(), 'full_mesh': (work/'full.ply').relative_to(folder).as_posix(),
              'detector': provenance, 'raw_predictions': raw, 'projected_points': projected,
              'diagnostics': {'tools': diag, 'processing_seconds': time.monotonic()-started,
                              'registered_images': count, 'submitted_turn_images': len(names), 'registered_fraction': count/len(names),
                              'sparse_point_error_mean_px': statistics_mean(errors),
                              'frontal_observations': camera['observations'], 'mesh': mesh_report,
                              'frontal_reprojection': {'observations': len(frontal_errors), 'mean_px': statistics_mean(frontal_errors),
                                                       'rms_px': math.sqrt(statistics_mean([e*e for e in frontal_errors])) if frontal_errors else None,
                                                       'max_px': max(frontal_errors) if frontal_errors else None},
                              'camera_alignment': 'manual_overlay_review_required',
                              'landmark_accuracy': 'ray_hits_are_not_anatomical_validation'}}
    return result


def statistics_mean(values):
    return sum(values)/len(values) if values else None


def undistort_mask(mask, source, target):
    """Nearest-neighbor inverse image warp, retaining a binary head mask."""
    import numpy as np
    # COLMAP pixel centers start at (0.5, 0.5); arrays start at index (0, 0).
    u, v = np.meshgrid(np.arange(target['width'])+.5, np.arange(target['height'])+.5)
    x, y = (u-target['cx'])/target['fx'], (v-target['cy'])/target['fy']
    factor = 1+source.get('k', 0)*(x*x+y*y)
    sx = np.floor(source['fx']*x*factor+source['cx']).astype(int)
    sy = np.floor(source['fy']*y*factor+source['cy']).astype(int)
    valid = (sx >= 0) & (sx < mask.shape[1]) & (sy >= 0) & (sy < mask.shape[0])
    output = np.zeros((target['height'], target['width']), dtype=np.uint8)
    output[valid] = mask[sy[valid], sx[valid]]
    return output
