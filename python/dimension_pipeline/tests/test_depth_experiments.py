import copy
import hashlib
import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import trimesh
from PIL import Image

from dimension_pipeline.depth_quality import POLICY, dense_options, mesh_options
from dimension_pipeline.depth_metrics import geometry_metrics
from dimension_pipeline.depth_variants import experiment_artifacts
from dimension_pipeline.depth_experiments import frozen_inputs, dense_point_count, run_depth_experiments
from dimension_pipeline.mesh_comparison import compare_session
from dimension_pipeline.webcam_pilot import Store


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class DepthTests(unittest.TestCase):
    def fixture(self, temp):
        store = Store(temp); state = store.create(); folder = store.folder(state['id'])
        mesh = {'vertices': [[-1., -1., 0.], [1., -1., 0.], [1., 1., 0.], [-1., 1., 0.]], 'triangles': [[0, 1, 2], [0, 2, 3]]}
        camera = {'R': np.eye(3).tolist(), 't': [0., 0., 5.]}
        raw = trimesh.Trimesh(vertices=mesh['vertices'], faces=mesh['triangles'], process=False); raw.export(folder/'full.ply')
        Image.new('RGB', (64, 64)).save(folder/'front.png')
        state.update(status='surface_ready', result={'full_mesh': 'full.ply', 'frontal_undistorted': 'front.png', 'surface': {'mesh': mesh, 'units': 'reconstruction_unit'},
                     'cameras': {'front': camera}, 'frontal_camera_key': 'front', 'projected_points': [], 'raw_predictions': []})
        store.save(state); return store, state, raw, camera

    def variant(self, store, state, raw, camera):
        run_id = 'b'*32; profile = 'fusion3'; folder = store.folder(state['id']); path = folder/'experiments'/run_id/profile/'full.ply'; path.parent.mkdir(parents=True)
        shifted = trimesh.Trimesh(vertices=raw.vertices+[0, 0, 1], faces=raw.faces[:, ::-1], process=False); shifted.export(path)
        row = {'id': 'q'+run_id[:16]+'-'+profile, 'profile_id': profile, 'status': 'completed', 'kind': 'depth_filtered', 'label': 'Analytic offset',
               'version': POLICY['version'], 'quality': POLICY['profiles'][profile], 'full_mesh': path.relative_to(folder).as_posix(),
               'sha256': sha(path), 'source_full_mesh_sha256': sha(folder/'full.ply'), 'input_manifest_sha256': '0'*64,
               'coordinate_transform': 'identity', 'units': 'reconstruction_unit', 'attachment_status': 'invalid_on_variant',
               'metrics': geometry_metrics(raw, shifted, camera, []), 'recommendation': {'decision': 'pending_manual_review'}, 'coverage_status': 'inadequate_coverage',
               'artifacts': [{'path': path.relative_to(folder).as_posix(), 'sha256': sha(path)}]}
        state['depth_experiments'] = {'version': 'webcam_depth_experiments_v1', 'runs': [{'id': run_id, 'status': 'completed', 'variants': [row]}]}
        store.save(state); return row

    def test_one_factor_profiles_and_explicit_pinned_baseline(self):
        def options(profile=None):
            args = dense_options(profile); return dict(zip(args[::2], args[1::2]))
        baseline = options(); self.assertEqual(baseline['--geometric-iters'], '2'); self.assertEqual(baseline['--number-views-fuse'], '2')
        control = options('fusion2')
        for profile, name, value in [('fusion3', '--number-views-fuse', '3'), ('fusion4', '--number-views-fuse', '4'),
                                     ('speckles', '--postprocess-dmaps', '1'), ('extra_geom2', '--geometric-iters', '2')]:
            candidate = options(profile); self.assertEqual(candidate[name], value)
            self.assertEqual({k for k in candidate if candidate[k] != control[k]}, {name})
        for profile in POLICY['profiles']:
            self.assertFalse(int(options(profile)['--postprocess-dmaps']) & 2)
        self.assertEqual(dict(zip(mesh_options()[::2], mesh_options()[1::2]))['--close-holes'], '0')
        with self.assertRaises(ValueError): dense_options('../custom')

    def test_low_roughness_does_not_hide_lost_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            _, _, raw, camera = self.fixture(temp)
            clipped = trimesh.Trimesh(vertices=raw.vertices, faces=raw.faces[:1], process=False)
            result = geometry_metrics(raw, clipped, camera, [])
            self.assertLess(result['roughness']['plane_rms']['rms'], 1e-10)
            self.assertLess(result['coverage']['global_retention_within_tolerance'], .6)
            self.assertEqual(result['coverage']['outcome'], 'inadequate_coverage')
            self.assertGreater(result['topology']['boundary_edges'], 0)
            self.assertIsNone(result['topology']['hole_count'])

    def test_variant_compare_export_reload_and_attachment_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            store, state, raw, camera = self.fixture(temp); baseline = copy.deepcopy(state['result'])
            row = self.variant(store, state, raw, camera); before = sha(store.folder(state['id'])/'full.ply')
            report = compare_session(store.folder(state['id']), state, count=40, variant=row['id'], reference='raw')
            self.assertAlmostEqual(report['deviation']['source_to_reference']['rms'], 1.)
            self.assertEqual(report['comparison_reference_id'], 'raw')
            self.assertNotEqual(report['variants'][-1]['mesh_id'], report['annotation_mesh_id'])
            restored = store.restore(store.export(state['id']))
            self.assertEqual(restored['result'], baseline)
            self.assertEqual(restored['depth_experiments'], state['depth_experiments'])
            self.assertEqual(sha(store.folder(state['id'])/'full.ply'), before)
            reviewed=store.depth_review(state['id'],{'variant_id':row['id'],'decision':'reject','notes':'Analytic offset changes geometry despite a smooth plane.'})
            self.assertEqual(reviewed['result'],baseline)
            self.assertEqual(reviewed['depth_experiments']['runs'][0]['variants'][0]['recommendation']['decision'],'reject')
            changed = copy.deepcopy(state); changed['depth_experiments']['runs'][0]['variants'][0]['artifacts'][0]['path'] = 'full.ply'
            with self.assertRaises(ValueError): experiment_artifacts(changed)
            contained = store.folder(state['id'])/row['full_mesh']; contained.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'changed'): store.export(state['id'])

    def test_single_job_native_cancellation_keeps_raw_surface(self):
        with tempfile.TemporaryDirectory() as temp:
            store, state, _, _ = self.fixture(temp); state['captures'] = [{}]*61; store.save(state); baseline = copy.deepcopy(state['result'])
            entered = threading.Event()
            def fake(folder, snapshot, run_id, run, update, publish, cancelled):
                entered.set(); run('native_sleep', [sys.executable, '-c', 'import time; time.sleep(30)'], folder)
            with patch('dimension_pipeline.webcam_pilot.run_depth_experiments', fake):
                store.start_depth_experiments(state['id'], {}); self.assertTrue(entered.wait(2))
                with self.assertRaisesRegex(ValueError, 'One'): store.start_depth_experiments(state['id'], {})
                deadline = time.monotonic()+3
                while store.process is None and time.monotonic()<deadline: time.sleep(.01)
                store.cancel(state['id'])
                while store.job and time.monotonic()<deadline: time.sleep(.01)
            final = store.load(state['id']); self.assertIsNone(store.job); self.assertIsNone(store.process)
            self.assertEqual(final['status'], 'surface_ready'); self.assertEqual(final['result'], baseline)
            self.assertEqual(final['depth_experiments']['runs'][-1]['status'], 'cancelled')
            self.assertFalse((store.root/'active-process.json').exists())

    def test_restart_recovery_does_not_replace_baseline(self):
        with tempfile.TemporaryDirectory() as temp:
            store, state, _, _ = self.fixture(temp); baseline = copy.deepcopy(state['result'])
            state['depth_experiments'] = {'version': 'webcam_depth_experiments_v1', 'runs': [{'id': 'c'*32, 'status': 'processing', 'variants': []}]}
            store.save(state); recovered = Store(temp).load(state['id'])
            self.assertEqual(recovered['depth_experiments']['runs'][0]['status'], 'interrupted')
            self.assertEqual(recovered['result'], baseline); self.assertEqual(recovered['status'], 'surface_ready')

    def test_frozen_model_rejects_heldout_frontal(self):
        with tempfile.TemporaryDirectory() as temp:
            store, state, _, camera = self.fixture(temp)
            state['captures'] = [{'role': 'reconstruction', 'slot': f'turn_{i:02}'} for i in range(60)]
            with patch('dimension_pipeline.depth_experiments.read_model', return_value={'front.png': camera}), self.assertRaisesRegex(ValueError, 'held-out'):
                frozen_inputs(store.folder(state['id']), state, lambda: False)

    def test_native_point_visibility_lists_and_checkpoint_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            store, state, raw, camera = self.fixture(temp); folder=store.folder(state['id'])
            source=folder/'raw-input';(source/'dense/sparse').mkdir(parents=True)
            manifest={'files':{'full.ply':sha(folder/'full.ply')}}
            old_id='d'*32; previous=folder/'experiments'/old_id/'fusion2';previous.mkdir(parents=True)
            header=b'ply\nformat binary_little_endian 1.0\nelement vertex 1001\nproperty float x\nproperty float y\nproperty float z\nproperty list uchar uint view_indices\nend_header\n'
            (previous/'dense.ply').write_bytes(header+b'\0'*(1001*16))
            self.assertEqual(dense_point_count(previous/'dense.ply'),1001)
            (previous/'dense-options.cfg').write_text('Speckle Size = 100\n')
            (previous/'processing.log').write_text("Densifying point-cloud completed: 1001 points\nPoint-cloud 'dense.ply' saved: 1001 points\n")
            mf=previous.parent/'input-manifest.json';mf.write_text(json.dumps(manifest))
            prior={'id':'q'+old_id[:16]+'-fusion2','profile_id':'fusion2','status':'failed','quality':POLICY['profiles']['fusion2'],
                   'fixed_options':POLICY['fixed'],'tool_sha256':{},'input_manifest':mf.relative_to(folder).as_posix(),
                   'input_manifest_sha256':sha(mf),'processing_seconds':7.,'dense_command':['fixture-native-fusion'],
                   'artifacts':[{'path':p.relative_to(folder).as_posix(),'sha256':sha(p)} for p in previous.iterdir()]}
            stages=[];published=[]
            def native(stage,command,cwd):
                stages.append(stage)
                if stage.endswith(':meshing'): raw.export(cwd/'full.ply')
            with patch('dimension_pipeline.depth_experiments.diagnostics',return_value={'ready':True,'tools':{}}), \
                 patch('dimension_pipeline.depth_experiments.frozen_inputs',return_value=(source,{},manifest)), \
                 patch.dict(POLICY,{'profiles':{'fusion2':POLICY['profiles']['fusion2']}}), \
                 patch('dimension_pipeline.depth_experiments.shutil.disk_usage',return_value=type('Space',(),{'free':20*1024**3})()):
                run_depth_experiments(folder,state,'e'*32,native,lambda stage:None,lambda row:published.append(copy.deepcopy(row)),lambda:False,
                                      resume_record={'id':old_id,'variants':[prior]})
            self.assertFalse(any(stage.endswith(':depth_fusion') for stage in stages))
            row=published[-1];self.assertEqual(row['status'],'completed');self.assertEqual(row['retained_points'],1001)
            self.assertEqual(row['checkpoint_source']['pointcloud_sha256'],sha(previous/'dense.ply'))
            self.assertEqual(row['effective_speckle_size_pixels'],100)
            self.assertGreaterEqual(row['processing_seconds'],7.)


if __name__ == '__main__': unittest.main()
