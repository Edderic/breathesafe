"""Isolated frozen-depth experiments. Raw session geometry is never replaced."""
import copy
import hashlib
import json
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path

import trimesh

from .depth_quality import POLICY, dense_options, mesh_options
from .depth_metrics import geometry_metrics
from .mesh_comparison import checked_mesh
from .webcam_reconstruction import diagnostics, executable, read_model


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(4*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def contained(folder, name):
    path = (Path(folder)/name).resolve(); path.relative_to(Path(folder).resolve())
    if not path.is_file():
        raise ValueError('Missing experiment input/artifact: '+name)
    return path


def frozen_inputs(folder, state, cancelled):
    result = state['result']; work = contained(folder, result['full_mesh']).parent
    turns = {c['slot']+'.png' for c in state['captures'] if c['role'] == 'reconstruction'}
    cameras = read_model(work/'dense/sparse')
    if turns != {f'turn_{i:02}.png' for i in range(60)} or not set(cameras).issubset(turns) or len(cameras) < .9*len(turns):
        raise ValueError('Frozen model has insufficient turn coverage or includes held-out images.')
    if any(c.get('mask_approved') is not True or c.get('mirrored') is not False for c in state['captures'] if c['role']=='reconstruction'):
        raise ValueError('Use approved masks and unmirrored reconstruction turn captures.')
    if not any(p.name.startswith('depth') for p in work.glob('*.dmap')):
        raise ValueError('Frozen depth cache is missing. Exported inspection bundles do not contain this cache; reconstruct locally before experimenting.')
    commands = []
    for line in (work/'processing.log').read_text().splitlines():
        if line.startswith('['):
            try: commands.append(json.loads(line))
            except ValueError: pass
    command = next((c for c in commands if isinstance(c, list) and Path(c[0]).name == 'DensifyPointCloud'), None)
    if command is None:
        raise ValueError('Missing raw densification command provenance.')
    def option(name, default):
        return int(command[command.index(name)+1]) if name in command else default
    if option('--geometric-iters', 2) != 2 or option('--postprocess-dmaps', 0) != 0 or option('--number-views-fuse', 2) != 2:
        raise ValueError('Experiment requires the pinned unfiltered two-view baseline with two geometric passes.')
    paths = [contained(folder, result['full_mesh']), work/'processing.log']
    for capture in state['captures']:
        if capture['role'] != 'reconstruction': continue
        for key, sha in [('image', 'sha256'), ('mask', 'mask_sha256')]:
            path = contained(folder, capture[key])
            if digest(path) != capture[sha]: raise ValueError('Approved turn image/mask hash changed.')
            paths.append(path)
    for name in cameras:
        paths.extend([work/'dense/images'/name, work/'dense_masks'/(Path(name).stem+'.mask.png'),
                      work/f"depth{cameras[name]['image_id']:04}.dmap"])
    paths.extend(p for p in (work/'dense/sparse').glob('*.txt'))
    hashes = {}
    for path in paths:
        if cancelled(): raise InterruptedError('Cancelled while hashing frozen inputs.')
        path = contained(folder, path.relative_to(folder).as_posix())
        hashes[path.relative_to(folder).as_posix()] = digest(path)
    return work, cameras, {'version': 'webcam_frozen_depth_inputs_v1', 'files': hashes,
        'camera_models_sha256': hashlib.sha256(json.dumps(result['cameras'], sort_keys=True).encode()).hexdigest(),
        'excluded_capture_slots': ['front'], 'registered_turn_images': sorted(cameras),
        'source_depth_geometric_iters': 2, 'source_postprocess_dmaps': 0,
        'depth_cache_bundle_status': 'hashes_recorded_cache_not_in_inspection_export'}


def clone_private(source, destination):
    """APFS copy-on-write clone, never a hard link; portable copy fallback."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if platform.system() == 'Darwin':
        result = subprocess.run(['/bin/cp', '-c', str(source), str(destination)], capture_output=True)
        if result.returncode == 0: return 'apfs_copy_on_write'
    shutil.copy2(source, destination); return 'independent_copy'


def dense_point_count(path):
    # OpenMVS point PLY has variable-length per-vertex visibility lists, which
    # generic trimesh PLY loading does not support. Count the native header.
    with Path(path).open('rb') as source:
        header = source.read(65536).split(b'end_header')[0]
    match = re.search(rb'(?:^|\n)element vertex ([0-9]+)\r?\n', header)
    if not header.startswith(b'ply\n') or match is None:
        raise ValueError('Missing dense point-cloud PLY count.')
    count = int(match[1])
    if count < 1 or Path(path).stat().st_size < count*12:
        raise ValueError('Empty or truncated dense point-cloud PLY.')
    return count


def run_depth_experiments(folder, state, run_id, run, update, publish, cancelled, resume_record=None):
    folder = Path(folder).resolve()
    diag = diagnostics()
    if not diag['ready']: raise ValueError('Pinned native CPU tools unavailable.')
    update('hash_frozen_inputs')
    source, cameras, manifest = frozen_inputs(folder, state, cancelled)
    run_folder = folder/'experiments'/run_id; run_folder.mkdir(parents=True, exist_ok=False)
    (run_folder/'input-manifest.json').write_text(json.dumps(manifest, indent=2))
    raw = checked_mesh(trimesh.load(contained(folder, state['result']['full_mesh']), force='mesh', process=False))
    camera = state['result']['cameras'][state['result']['frontal_camera_key']]
    predictions = state['result']['projected_points']
    tool_hashes = {name: digest(Path(row['path']).resolve()) for name, row in diag['tools'].items()}
    for profile, parameters in POLICY['profiles'].items():
        if cancelled(): raise InterruptedError('Cancelled between variants.')
        if shutil.disk_usage(folder).free < 6*1024**3:
            raise ValueError('At least 6 GiB free space is required for isolated depth-cache scratch. Raw artifacts retained.')
        checkpoint = None
        if resume_record:
            prior = next((v for v in resume_record['variants'] if v['profile_id']==profile), None)
            if prior and prior.get('quality') == parameters and prior.get('fixed_options') == POLICY['fixed'] and prior.get('tool_sha256') == tool_hashes:
                previous_manifest = contained(folder, prior['input_manifest'])
                previous_inputs = json.loads(previous_manifest.read_text())
                if digest(previous_manifest) != prior['input_manifest_sha256'] or previous_inputs['files'] != manifest['files']:
                    raise ValueError('Checkpoint input provenance differs from frozen inputs.')
                cloud = next((a for a in prior.get('artifacts', []) if a['path'].endswith('/dense.ply')), None)
                log = next((a for a in prior.get('artifacts', []) if a['path'].endswith('/processing.log')), None)
                if cloud and log:
                    log_text = contained(folder, log['path']).read_text()
                    if "Point-cloud 'dense.ply' saved:" in log_text and 'Densifying point-cloud completed:' in log_text:
                        if digest(contained(folder, cloud['path'])) != cloud['sha256']:
                            raise ValueError('Checkpoint point-cloud hash changed.')
                        checkpoint = (prior, cloud)
        started = time.monotonic(); work = run_folder/profile; work.mkdir()
        row = {'id': 'q'+run_id[:16]+'-'+profile, 'profile_id': profile, 'label': parameters['label'], 'status': 'processing',
               'version': POLICY['version'], 'kind': 'depth_filtered', 'quality': copy.deepcopy(parameters),
               'fixed_options': POLICY['fixed'], 'meshing': POLICY['meshing'], 'tools': diag, 'tool_sha256': tool_hashes,
               'input_manifest': (run_folder/'input-manifest.json').relative_to(folder).as_posix(),
               'input_manifest_sha256': digest(run_folder/'input-manifest.json'),
               'source_full_mesh_sha256': digest(contained(folder, state['result']['full_mesh'])),
               'source_geometric_iters': 2, 'added_geometric_iters': parameters['geometric-iters'],
               'coordinate_transform': 'identity', 'units': 'reconstruction_unit',
               'attachment_status': 'raw_attachments_invalid_on_variant_topology_no_transfer',
               'scale_check': {'status': 'requires_variant_route_retrace' if state.get('calibrated') else 'uncalibrated_no_independent_tape_check',
                               'raw_scale': (state.get('calibrated') or {}).get('report', {}).get('mm_per_reconstruction_unit'),
                               'raw_independent_check': (state.get('calibrated') or {}).get('report', {}).get('independent_check'),
               'variant_route_transfer': False}, 'artifacts': [{'path': (run_folder/'input-manifest.json').relative_to(folder).as_posix(), 'sha256': digest(run_folder/'input-manifest.json')}]}
        publish(row); scratch = []
        try:
            update(profile+':copy_frozen_inputs')
            model = work/'inputs/sparse'; model.mkdir(parents=True)
            for path in (source/'dense/sparse').glob('*.txt'):
                clone_private(path, model/path.name)
            copies = set()
            for name, c in cameras.items():
                if cancelled(): raise InterruptedError('Cancelled while copying inputs.')
                inputs = [(source/'dense/images'/name, work/'inputs/images'/name),
                          (source/'dense_masks'/(Path(name).stem+'.mask.png'), work/'masks'/(Path(name).stem+'.mask.png'))]
                if not checkpoint: inputs.append((source/f"depth{c['image_id']:04}.dmap", work/f"depth{c['image_id']:04}.dmap"))
                for source_path, destination in inputs:
                    copies.add(clone_private(source_path, destination))
                    if digest(destination) != manifest['files'][source_path.relative_to(folder).as_posix()]:
                        raise ValueError('Frozen input copy hash mismatch.')
                    if destination.suffix == '.dmap': scratch.append(destination)
            row['copy_methods'] = sorted(copies)
            # Generate binary COLMAP files only from validated, turn-only text.
            run(profile+':freeze_model', [executable('colmap'), 'model_converter', '--input_path', str(model), '--output_path', str(model), '--output_type', 'BIN'], work)
            run(profile+':import', [executable('InterfaceCOLMAP'), '-i', str(work/'inputs'), '-o', str(work/'scene.mvs'), '--image-folder', str(work/'inputs/images')], work)
            (work/'cli.cfg').write_text('# Explicit options are supplied on the command line.\n')
            if checkpoint:
                prior, cloud = checkpoint
                clone_private(contained(folder, cloud['path']), work/'dense.ply')
                if digest(work/'dense.ply') != cloud['sha256']: raise ValueError('Checkpoint copy hash changed.')
                row['checkpoint_source'] = {'run_id': resume_record['id'], 'variant_id': prior['id'], 'pointcloud_sha256': cloud['sha256'],
                                            'processing_seconds': prior['processing_seconds']}
                row['dense_command'] = prior['dense_command']
                config = next((a for a in prior['artifacts'] if a['path'].endswith('/dense-options.cfg')), None)
                if config:
                    path = contained(folder, config['path'])
                    if digest(path) != config['sha256']: raise ValueError('Checkpoint dense options changed.')
                    clone_private(path, work/'dense-options.cfg')
            else:
                command = [executable('DensifyPointCloud'), '-i', str(work/'scene.mvs'), '-o', str(work/'dense.mvs'),
                           '--mask-path', str(work/'masks'), '--config-file', str(work/'cli.cfg'), '--dense-config-file', str(work/'dense-options.cfg'),
                           '--remove-dmaps', '1', *dense_options(profile)]
                row['dense_command'] = command
                run(profile+':depth_fusion', command, work)
            row['retained_points'] = dense_point_count(work/'dense.ply')
            config_text = (work/'dense-options.cfg').read_text()
            speckle_size = re.search(r'^Speckle Size\s*=\s*(\d+)', config_text, re.MULTILINE)
            row['effective_speckle_size_pixels'] = int(speckle_size[1]) if speckle_size else None
            if parameters['postprocess-dmaps'] == 1 and row['effective_speckle_size_pixels'] != 100:
                raise ValueError('Speckle size differs from the pinned 100-pixel experiment setting.')
            if row['retained_points'] < 1000: raise ValueError('Insufficient retained dense points (<1000).')
            row['mesh_command'] = [executable('ReconstructMesh'), '-i', str(work/'scene.mvs'), '--pointcloud-file', str(work/'dense.ply'), '-o', str(work/'full.mvs'), *mesh_options()]
            run(profile+':meshing', row['mesh_command'], work)
            candidate = checked_mesh(trimesh.load(work/'full.ply', force='mesh', process=False))
            row['full_mesh'] = (work/'full.ply').relative_to(folder).as_posix(); row['sha256'] = digest(work/'full.ply')
            update(profile+':geometry_metrics')
            row['metrics'] = geometry_metrics(raw, candidate, camera, predictions)
            row['status'] = 'completed'; row['coverage_status'] = row['metrics']['coverage']['outcome']
            row['recommendation'] = {'decision': 'pending_manual_review', 'reason': 'Review coverage/detail with roughness and displacement before retaining any setting.'}
        except InterruptedError:
            row.update(status='cancelled', error='Cancelled. Raw baseline and completed variants retained.'); raise
        except Exception as error:
            row.update(status='failed', error=str(error))
        finally:
            # Only this run's generated cache copies are disposable. Source maps stay intact.
            for path in scratch:
                path.unlink(missing_ok=True)
            for path in work.glob('*.geo.dmap'):
                path.unlink()
            row['resume_seconds'] = time.monotonic()-started
            row['processing_seconds'] = row['resume_seconds']+(row.get('checkpoint_source') or {}).get('processing_seconds', 0)
            if (work/'dense-options.cfg').exists():
                row['effective_dense_config_sha256'] = digest(work/'dense-options.cfg')
            (work/'report.json').write_text(json.dumps(row, indent=2, allow_nan=False))
            artifacts = [work/'report.json', run_folder/'input-manifest.json']
            artifacts += [p for p in work.iterdir() if p.is_file() and p.name in ('full.ply', 'dense.ply', 'processing.log', 'cli.cfg', 'dense-options.cfg', 'neighbors.json')]
            row['artifacts'] = [{'path': p.relative_to(folder).as_posix(), 'sha256': digest(p)} for p in artifacts]
            publish(row)
    update('verify_raw_input_hashes')
    for name, expected in manifest['files'].items():
        if digest(contained(folder, name)) != expected:
            raise ValueError('Raw input changed during experiment: '+name)
