"""Opt-in photo-consistency trials on immutable, turn-only reconstruction inputs."""
import copy
import json
import re
import time
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

from .depth_experiments import clone_private, contained, digest
from .depth_metrics import geometry_metrics
from .mesh_comparison import checked_mesh, mesh_identity, sampled_deviation
from .webcam_geometry import project, camera_pixel
from .webcam_reconstruction import diagnostics, executable, read_model, detect

POLICY = json.loads(Path(__file__).with_name('refinement_policy.json').read_text())
ITERATION_POLICY = json.loads(Path(__file__).with_name('refinement_iterations_policy.json').read_text())
SUITES = {'regularity': POLICY, 'iterations': ITERATION_POLICY}
POLICIES = {policy['version']:policy for policy in SUITES.values()}


def selected_profiles(suite='regularity', profiles=None):
    if suite not in SUITES: raise ValueError('Unknown versioned refinement suite.')
    if profiles is None: return list(SUITES[suite]['profiles'])
    if not isinstance(profiles,list) or not profiles or any(not isinstance(p,str) or p not in SUITES[suite]['profiles'] for p in profiles) or len(set(profiles))!=len(profiles):
        raise ValueError('Choose a nonempty, unique list of versioned refinement profiles.')
    return [p for p in SUITES[suite]['profiles'] if p in profiles]


def settings(profile, suite='regularity'):
    if suite not in SUITES or profile not in SUITES[suite]['profiles']:
        raise ValueError('Unknown versioned refinement suite/profile.')
    policy = SUITES[suite]; parameters = policy['profiles'][profile]
    fixed = {**policy['fixed'], **({'gradient-step':parameters['gradient-step']} if 'gradient-step' in parameters else {})}
    optimization = {**policy['optimization'], 'iterations':int(fixed['gradient-step'])}
    return fixed, optimization


def options(profile, suite='regularity'):
    fixed, _ = settings(profile,suite)
    return [s for k, v in {**fixed, 'regularity-weight': SUITES[suite]['profiles'][profile]['regularity-weight']}.items()
            for s in ('--'+k, str(v))]


def save_masked_turn(image_path, mask_path, camera, destination):
    image = Image.open(image_path).convert('RGB'); mask = Image.open(mask_path).convert('L')
    if image.size != mask.size or image.size != (camera['width'],camera['height']):
        raise ValueError('Turn image/mask/camera dimensions disagree.')
    if not set(np.unique(np.asarray(mask))).issubset({0,255}): raise ValueError('Expected binary approved mask.')
    destination.parent.mkdir(exist_ok=True)
    Image.composite(image,Image.new('RGB',image.size),mask).save(destination)


def frozen_inputs(folder, state, cancelled):
    result = state['result']; source = contained(folder, result['full_mesh']).parent
    if result['surface']['units'] != 'reconstruction_unit':
        raise ValueError('Refinement requires the original unscaled reconstruction.')
    turns = [c for c in state['captures'] if c['role'] == 'reconstruction']
    names = {c['slot']+'.png' for c in turns}
    cameras = read_model(source/'dense/sparse')
    if names != {f'turn_{i:02}.png' for i in range(60)} or not set(cameras).issubset(names) or len(cameras) < 54:
        raise ValueError('Refinement requires >=90% registered turn-only images; frontal must be held out.')
    if len({c['camera_id'] for c in cameras.values()}) != 1 or any(c.get('k',0)!=0 for c in cameras.values()):
        raise ValueError('Refinement requires one shared undistorted camera model.')
    if not (source/'database.db').is_file():
        raise ValueError('Refinement reruns require the original local feature database. An inspection export can reload variants, but cannot recreate missing registration features; reconstruct locally first.')
    paths = [contained(folder, result['full_mesh'])]
    for capture in turns:
        if capture.get('mask_approved') is not True or capture.get('mirrored') is not False:
            raise ValueError('Refinement requires approved masks and unmirrored turn images.')
        for key, sha in [('image', 'sha256'), ('mask', 'mask_sha256')]:
            path = contained(folder, capture[key])
            if digest(path) != capture[sha]: raise ValueError('Approved capture/mask hash changed.')
            paths.append(path)
    for name in cameras:
        paths += [source/'dense/images'/name, source/'dense_masks'/(Path(name).stem+'.mask.png')]
    paths += list((source/'dense/sparse').glob('*.txt'))
    hashes = {}
    for path in paths:
        if cancelled(): raise InterruptedError('Cancelled while freezing inputs.')
        path = contained(folder, path.relative_to(folder).as_posix())
        hashes[path.relative_to(folder).as_posix()] = digest(path)
    return source, cameras, {'version': 'webcam_refinement_inputs_v1', 'files': hashes,
        'registered_turn_images': sorted(cameras), 'excluded_capture_slots': ['front'],
        'mask_method': 'approved undistorted binary head masks; RGB outside mask composited black',
        'mask_limitation': 'RefineMesh 2.4.0 has no semantic-mask option. Black compositing does not remove boundary gradients from its objective.',
        'reload_capability': 'geometry/projection inspection; rerunning registration requires original local feature database',
        'camera_transform': 'identity; fixed shared reconstruction coordinates'}


def fixed_registration(source, destination, run, stage):
    """Register held-out features AFTER dense geometry is fixed, without BA."""
    model_name = json.loads((source.parent/'session.json').read_text())['result']['diagnostics']['sparse_model_selection']['selected_model']
    if not isinstance(model_name, str) or not re.fullmatch(r'[0-9]+',model_name):
        raise ValueError('Invalid fixed sparse model ID.')
    model = source/'sparse'/model_name
    before = read_model(model)
    if 'front.png' in before: raise ValueError('Fixed registration input contains the held-out frontal.')
    clone_private(source/'database.db', destination/'evaluation.db')
    (destination/'frontal.txt').write_text('front.png\n')
    ids = {c['camera_id'] for c in before.values()}
    if len(ids) != 1: raise ValueError('Expected shared fixed camera.')
    (destination/'fixed-cameras.txt').write_text(str(next(iter(ids)))+'\n')
    registered = destination/'registered'; registered.mkdir()
    run(stage+':register_heldout', [executable('colmap'), 'image_registrator', '--database_path', str(destination/'evaluation.db'),
        '--input_path', str(model), '--output_path', str(registered), '--Mapper.image_list_path', str(destination/'frontal.txt'),
        '--Mapper.constant_camera_list_path', str(destination/'fixed-cameras.txt')], destination)
    run(stage+':read_registration', [executable('colmap'), 'model_converter', '--input_path', str(registered),
        '--output_path', str(registered), '--output_type', 'TXT'], destination)
    after = read_model(registered)
    if 'front.png' not in after: raise ValueError('Held-out frontal registration failed.')
    for name, camera in before.items():
        if name not in after or any(not np.allclose(camera[k], after[name][k], rtol=1e-8, atol=1e-8) for k in ('R','t','fx','fy','cx','cy','k')):
            raise ValueError('Held-out registration changed fixed cameras.')
    def positions(path):
        return {s[0]: s[1:4] for l in (path/'points3D.txt').read_text().splitlines() if l and not l.startswith('#') for s in [l.split()]}
    if positions(model) != positions(registered): raise ValueError('Held-out registration changed sparse geometry.')
    return registered, after['front.png']


def registration_diagnostics(model, camera):
    points = {s[0]:list(map(float,s[1:4])) for line in (model/'points3D.txt').read_text().splitlines()
              if line and not line.startswith('#') for s in [line.split()]}
    errors = []; lines = iter((model/'images.txt').read_text().splitlines())
    for line in lines:
        if not line or line.startswith('#'): continue
        fields = line.split(); observations = next(lines,'').split()
        if fields[9] != 'front.png': continue
        for i in range(0,len(observations),3):
            if observations[i+2] in points:
                pixel = camera_pixel(camera,points[observations[i+2]])
                errors.append(float(np.linalg.norm(np.asarray(pixel)-np.asarray(observations[i:i+2],dtype=float))))
    return {'observations':len(errors), 'rms_px':float(np.sqrt(np.mean(np.square(errors)))) if errors else None,
            'mean_px':float(np.mean(errors)) if errors else None,'max_px':max(errors) if errors else None,
            'camera_alignment':'manual_image_overlay_review_required', 'accuracy_status':'sparse_reprojection_is_not_anatomical_validation'}


def fresh_analysis(candidate, state, camera, predictions, variant_id):
    analysis = candidate.simplify_quadric_decimation(face_count=18000) if len(candidate.faces)>18000 or len(candidate.vertices)>20000 else candidate.copy()
    checked_mesh(analysis)
    if len(analysis.vertices)>20000 or len(analysis.faces)>40000: raise ValueError('Refined analysis exceeds viewer limits.')
    mesh = {'vertices': analysis.vertices.tolist(), 'triangles': analysis.faces.tolist()}
    surface = copy.deepcopy(state['result']['surface'])
    surface.update(record_id=variant_id, mesh=mesh, units='reconstruction_unit', scale={'status':'uncalibrated'},
                   topology_id=mesh_identity(mesh), annotation_status='requires_new_review_and_tape_routes')
    return {'version':'webcam_refinement_projection_v1', 'surface':surface, 'camera':camera,
            'analysis_deviation':sampled_deviation(candidate, analysis, 5000, 0, 1.),
            'raw_predictions':predictions, 'projected_points':project(mesh, camera, predictions),
            'calibration':None, 'routes':[], 'decisions':'all_pending_no_transfer',
            'accuracy_status':'not_independently_validated'}


def run_refinement_experiments(folder, state, run_id, run, update, publish, cancelled, suite='regularity', profiles=None):
    if suite not in SUITES: raise ValueError('Unknown versioned refinement suite.')
    policy = SUITES[suite]
    chosen_profiles = selected_profiles(suite,profiles)
    folder = Path(folder).resolve(); diag = diagnostics(include_refinement=True)
    if not diag['ready']: raise ValueError('Pinned macOS arm64 RefineMesh 2.4.0 CPU tools unavailable. Run setup_webcam_native.py.')
    update('freeze_refinement_inputs')
    source, cameras, manifest = frozen_inputs(folder, state, cancelled)
    root = folder/'refinements'/run_id; root.mkdir(parents=True, exist_ok=False)
    manifest_path = root/'input-manifest.json'; manifest_path.write_text(json.dumps(manifest, indent=2))
    inputs = root/'inputs'; model = inputs/'sparse'; model.mkdir(parents=True)
    for path in (source/'dense/sparse').glob('*.txt'): clone_private(path, model/path.name)
    derived = {}
    for name in cameras:
        if cancelled(): raise InterruptedError('Cancelled copying turn images.')
        path = inputs/'images'/name
        save_masked_turn(source/'dense/images'/name,source/'dense_masks'/(Path(name).stem+'.mask.png'),cameras[name],path)
        derived[name] = digest(path)
    manifest['derived_masked_images_sha256'] = derived
    manifest_path.write_text(json.dumps(manifest, indent=2))
    run('freeze_turn_model', [executable('colmap'),'model_converter','--input_path',str(model),'--output_path',str(model),'--output_type','BIN'], root)
    raw = checked_mesh(trimesh.load(contained(folder, state['result']['full_mesh']), force='mesh', process=False))
    raw_sha = digest(contained(folder, state['result']['full_mesh']))
    camera = state['result']['cameras'][state['result']['frontal_camera_key']]
    for profile in chosen_profiles:
        parameters = policy['profiles'][profile]
        if cancelled(): raise InterruptedError('Cancelled between refinement trials.')
        started = time.monotonic(); work = root/profile; work.mkdir()
        fixed, optimization = settings(profile,suite)
        row = {'id':'r'+run_id[:16]+'-'+profile, 'profile_id':profile, 'kind':'image_refined', 'suite':suite,
            'label':parameters['label'], 'version':policy['version'], 'status':'processing', 'quality':parameters,
            'fixed_options':fixed, 'optimization':optimization, 'tools':diag,
            'tool_sha256':{k:digest(v['path']) for k,v in diag['tools'].items()},
            'coordinate_transform':'identity', 'units':'reconstruction_unit', 'source_full_mesh_sha256':raw_sha,
            'input_manifest':manifest_path.relative_to(folder).as_posix(), 'input_manifest_sha256':digest(manifest_path),
            'attachment_status':'fresh_variant_topology_and_projections; original_routes_decisions_calibration_not_transferred',
            'scale_check':{'status':'requires_new_variant_routes_and_calibration', 'calibration_applied':False,
                           'independent_check':'not_measured', 'repeatability':'not_measured'},
            'recommendation':{'decision':'pending_manual_review','reason':'Inspect nose, ears, lips and chin; lower roughness is not anatomical validation.'}, 'artifacts':[]}
        publish(row)
        try:
            run(profile+':import_turns', [executable('InterfaceCOLMAP'),'-i',str(inputs),'-o',str(work/'scene.mvs'),'--image-folder',str(inputs/'images')], work)
            # Native mesh loading/cleanup is allowed only on an independent copy.
            clone_private(contained(folder,state['result']['full_mesh']),work/'input.ply')
            (work/'cli.cfg').write_text('# Versioned explicit CPU refinement options.\n')
            command = [executable('RefineMesh'),'-i',str(work/'scene.mvs'),'-m',str(work/'input.ply'),'-o',str(work/'full.mvs'),
                       '--config-file',str(work/'cli.cfg'), *options(profile,suite)]
            row['refine_command'] = command
            run(profile+':image_refinement', command, work)
            candidate = checked_mesh(trimesh.load(work/'full.ply',force='mesh',process=False))
            row.update(full_mesh=(work/'full.ply').relative_to(folder).as_posix(),sha256=digest(work/'full.ply'))
            update(profile+':geometry_metrics')
            row['metrics'] = geometry_metrics(raw,candidate,camera,state['result']['projected_points'])
            row['coverage_status'] = row['metrics']['coverage']['outcome']
            # Geometry is fixed before any held-out photo/feature access.
            registered, registered_camera = fixed_registration(source, work, run, profile)
            row['frontal_registration'] = registration_diagnostics(registered,registered_camera)
            frontal = next(c for c in state['captures'] if c['role']=='frontal')
            evaluation = work/'evaluation'; (evaluation/'images').mkdir(parents=True)
            clone_private(contained(folder,frontal['image']),evaluation/'images/front.png')
            front = work/'frontal_undistorted'
            run(profile+':undistort_heldout', [executable('colmap'),'image_undistorter','--image_path',str(evaluation/'images'),
                '--input_path',str(registered),'--output_path',str(front),'--output_type','COLMAP','--image_list_path',str(work/'frontal.txt')], work)
            run(profile+':read_heldout_camera', [executable('colmap'),'model_converter','--input_path',str(front/'sparse'),
                '--output_path',str(front/'sparse'),'--output_type','TXT'], work)
            new_camera = read_model(front/'sparse')['front.png']
            image = front/'images/front.png'
            with Image.open(image) as heldout_image:
                if heldout_image.size != (new_camera['width'],new_camera['height']): raise ValueError('Held-out camera/image size mismatch.')
            update(profile+':fresh_detection_and_projection')
            predictions, provenance = detect(image)
            if cancelled(): raise InterruptedError('Cancelled before projection.')
            projection = fresh_analysis(candidate,state,new_camera,predictions,row['id'])
            projection.update(detector=provenance, registration={'method':'fixed_sparse_model_no_BA_after_refinement',
                              'observations':new_camera['observations']})
            path = work/'projection.json'; path.write_text(json.dumps(projection,allow_nan=False))
            row.update(projection=path.relative_to(folder).as_posix(), analysis_mesh_id=projection['surface']['topology_id'],
                       projection_hits=sum(p['status']=='ok' for p in projection['projected_points']), status='completed')
        except InterruptedError:
            row.update(status='cancelled',error='Cancelled; raw inputs and completed trials retained.'); raise
        except Exception as error:
            row.update(status='failed',error=str(error))
        finally:
            row['processing_seconds'] = time.monotonic()-started
            (work/'report.json').write_text(json.dumps(row,indent=2,allow_nan=False))
            files = [manifest_path,root/'processing.log',work/'report.json',work/'processing.log',work/'full.ply',work/'projection.json',work/'cli.cfg']
            files += list(model.glob('*.txt'))+list((inputs/'images').glob('*.png'))
            files += list((work/'registered').glob('*.txt'))+list((work/'frontal_undistorted/sparse').glob('*.txt'))+list((work/'frontal_undistorted/images').glob('*.png'))
            row['artifacts'] = [{'path':p.relative_to(folder).as_posix(),'sha256':digest(p)} for p in files if p.is_file()]
            publish(row)
    update('verify_frozen_refinement_inputs')
    for name, sha in manifest['files'].items():
        if digest(contained(folder,name)) != sha: raise ValueError('Source input changed during refinement: '+name)
