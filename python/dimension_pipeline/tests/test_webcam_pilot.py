"""Analytic geometry and private session boundaries; no participant images."""
import base64
import copy
import io
import json
import math
import tempfile
import threading
import time
import unittest
import zipfile
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from dimension_pipeline.webcam_geometry import attachment, calibrate, camera_pixel, project, ray, readings, route_length
from dimension_pipeline.webcam_pilot import Handler, Store, digest
from dimension_pipeline.webcam_reconstruction import reconstruct, undistort_mask, select_sparse_model, reconstruction_pairs


def mesh():
    return {'vertices': [[-2., -2., 5.], [2., -2., 5.], [0., 2., 5.], [-2., -2., 7.], [2., -2., 7.], [0., 2., 7.]],
            'triangles': [[0, 1, 2], [3, 4, 5]]}


def camera():
    return {'width': 1920, 'height': 1080, 'fx': 1200., 'fy': 1150., 'cx': 960., 'cy': 540.,
            'R': [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]], 't': [0., 0., 0.], 'k': 0.,
            'mirrored': False, 'units': 'reconstruction_unit'}


def a(label, weights, triangle=0):
    return {'kind': 'barycentric', 'triangle_index': triangle, 'weights': weights, 'label': label}


def route(via):
    return [a('left_tragion', [1, 0, 0]), a(via, [0, 0, 1]), a('right_tragion', [0, 1, 0])]


class GeometryTests(unittest.TestCase):
    def test_two_pass_matching_connects_corresponding_views_without_frontal(self):
        frames=[{'slot':f'turn_{i:02}'} for i in range(60)]
        ordinary,base=reconstruction_pairs(frames)
        self.assertEqual(len(ordinary),339)
        pairs,policy=reconstruction_pairs(frames,'moving_camera_two_pass')
        self.assertTrue(ordinary.issubset(pairs));self.assertEqual(policy['additional_cross_pass_pairs'],879)
        for i in range(30):self.assertIn((f'turn_{i:02}.png',f'turn_{59-i:02}.png'),pairs)
        self.assertIn(('turn_15.png','turn_43.png'),pairs)
        self.assertIn(('turn_00.png','turn_30.png'),pairs)
        self.assertEqual(sum((f'turn_{i:02}.png',f'turn_{j:02}.png') in pairs for i in range(30) for j in range(30,60)),900)
        self.assertFalse(any('front.png' in p for p in pairs))
        self.assertTrue(all(a<b for a,b in pairs));self.assertEqual(policy['total_pairs'],len(pairs))
        self.assertEqual(reconstruction_pairs(frames,'moving_camera')[0],ordinary)
        with self.assertRaises(ValueError):reconstruction_pairs(frames[:30],'moving_camera_two_pass')

    def test_sparse_selection_ignores_contained_initialization_candidates(self):
        names = [f'turn_{i:02}.png' for i in range(60)]
        full = dict.fromkeys(names, {'camera_id': 1})
        tiny = dict.fromkeys(names[7:9], {'camera_id': 1})
        path, cameras, report = select_sparse_model([(Path('0'), tiny), (Path('1'), full)], names)
        self.assertEqual(path, Path('1')); self.assertEqual(len(cameras), 60)
        self.assertEqual(report['discarded_candidates'][0]['registered_images'], 2)

    def test_sparse_selection_still_rejects_disconnected_competing_and_inadequate_models(self):
        names = [f'turn_{i:02}.png' for i in range(60)]
        def model(folder, images):
            return Path(folder), dict.fromkeys(images, {'camera_id': 1})
        for models, message in [
            ([model('0', names[:58]), model('1', names[58:])], 'disconnected'),
            ([model('0', names), model('1', names)], 'competing'),
            ([model('0', names[:20])], 'Insufficient'),
            ([model('0', names+['front.png'])], 'held-out'),
            ([], 'No sparse'),
        ]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                select_sparse_model(models, names)
    def test_binary_mask_undistortion_preserves_identity_and_pixel_centers(self):
        import numpy as np
        mask = np.zeros((64, 64), dtype=np.uint8); mask[8:50, 10:40] = 255
        c = {**camera(), 'width': 64, 'height': 64, 'cx': 32., 'cy': 32., 'fx': 40., 'fy': 40.}
        np.testing.assert_array_equal(undistort_mask(mask, c, c), mask)
        distorted = undistort_mask(mask, {**c, 'k': .2}, c)
        self.assertTrue(set(np.unique(distorted)).issubset({0, 255}))
        # u=12.5,v=12.5 maps to floor(10.64),floor(10.64) in source coordinates.
        self.assertEqual(distorted[12, 12], mask[10, 10])

    def test_perspective_nearest_intersection_uses_actual_image_dimensions(self):
        c = camera(); point = [.3, -.4, 5.]; pixel = camera_pixel(c, point)
        row = project(mesh(), c, [{'x': pixel[0]/1920, 'y': pixel[1]/1080}])[0]
        self.assertEqual(row['status'], 'ok'); self.assertEqual(row['attachment']['triangle_index'], 0)
        for expected, actual in zip(point, row['point']):
            self.assertAlmostEqual(expected, actual)
        self.assertEqual(row['acceptance'], 'pending')

    def test_rotated_translated_camera_back_projection_and_distortion(self):
        c = camera(); c.update(R=[[0, 0, 1], [0, 1, 0], [-1, 0, 0]], t=[.3, -.2, 7.], k=.12)
        p = [2., .8, .1]; origin, direction = ray(c, camera_pixel(c, p))
        lengths = [(p[i]-origin[i])/direction[i] for i in range(3)]
        self.assertLess(max(lengths)-min(lengths), 1e-8)
        with self.assertRaises(ValueError):
            project(mesh(), c, [{'x': .5, 'y': .5}])

    def test_mirrored_input_rejected_and_missed_rays_stay_missing(self):
        c = camera(); c['mirrored'] = True
        with self.assertRaises(ValueError):
            project(mesh(), c, [])
        rows = project(mesh(), camera(), [{'x': 0., 'y': 0.}, {'x': 2., 'y': .5}, {'x': math.nan, 'y': .5}])
        self.assertEqual([r['status'] for r in rows], ['missed_surface', 'outside_image', 'invalid_coordinates'])
        self.assertTrue(all('point' not in r for r in rows))

    def test_calibration_median_check_independence_and_camera_scaling(self):
        surface = {'mesh': mesh(), 'units': 'reconstruction_unit'}; c = camera(); c['t'] = [1., 2., 3.]
        length = route_length(mesh(), route('subnasale'), 'subnasale')
        payload = {'scale_readings_mm': [length*10, length*11, length*9], 'check_readings_mm': [80., 81., 82.],
                   'scale_route': route('subnasale'), 'check_route': route('menton')}
        result, cameras, report = calibrate(surface, {'front': c}, payload)
        self.assertAlmostEqual(report['mm_per_reconstruction_unit'], 10)
        self.assertEqual(cameras['front']['t'], [10., 20., 30.]); self.assertEqual(result['units'], 'mm')
        self.assertEqual(c['t'], [1., 2., 3.]); self.assertEqual(surface['units'], 'reconstruction_unit')
        self.assertAlmostEqual(report['independent_check']['discrepancy_mm'], length*10-81)
        p = [0., 0., 5.]
        self.assertEqual(camera_pixel(c, p), camera_pixel(cameras['front'], [v*10 for v in p]))
        payload['check_readings_mm'] = [90., 100., 110.]
        self.assertEqual(calibrate(surface, {'front': c}, payload)[2]['mm_per_reconstruction_unit'], report['mm_per_reconstruction_unit'])

    def test_disconnected_routes_and_invalid_controls_fail(self):
        r = route('subnasale'); r[-1]['triangle_index'] = 1
        with self.assertRaisesRegex(ValueError, 'disconnected'):
            route_length(mesh(), r, 'subnasale')
        for bad in ([1, 2], [1, -2, 3], [1, math.inf, 3]):
            with self.assertRaises(ValueError):
                readings(bad)
        with self.assertRaises(ValueError):
            attachment(mesh(), a('bad', [-1, 1, 1]))


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); self.store = Store(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def payload(self, slot='front', color='red'):
        from PIL import Image
        image = Image.new('RGB', (64, 64), color); mask = Image.new('L', (64, 64)); mask.paste(255, (10, 5, 55, 50))
        def data(img):
            out = io.BytesIO(); img.save(out, format='PNG'); return out.getvalue()
        raw = data(image)
        return {'slot': slot, 'image': base64.b64encode(raw).decode(), 'mask': base64.b64encode(data(mask)).decode(),
                'sha256': digest(raw), 'approved': True, 'mirrored': False, 'timestamp': '2026-11-02T10:00:00Z'}

    def test_retakes_replace_one_slot_and_sessions_are_isolated(self):
        first, second = self.store.create(), self.store.create()
        initial = self.store.capture(first['id'], self.payload())
        retake = self.store.capture(first['id'], self.payload(color='blue'))
        self.assertEqual(len(retake['captures']), 1)
        self.assertNotEqual(initial['captures'][0]['sha256'], retake['captures'][0]['sha256'])
        self.assertEqual(self.store.load(second['id'])['captures'], [])
        for bad in ('../outside', '/tmp/run', first['id']+'/..'):
            with self.assertRaises(ValueError):
                self.store.load(bad)
        with self.assertRaises(ValueError):
            self.store.start(first['id'])

    def test_start_rejects_stored_unapproved_mask_proposals(self):
        state=self.store.create()
        for slot in ['front']+['turn_'+str(i).zfill(2) for i in range(60)]:
            state=self.store.capture(state['id'],self.payload(slot))
        state['captures'][0]['mask_approved']=False
        self.store.save(state)
        with self.assertRaisesRegex(ValueError,'Review and approve'):
            self.store.start(state['id'])
        self.assertEqual(self.store.load(state['id'])['status'],'capturing')

    def test_sweep_metadata_survives_capture_save(self):
        context = {'group': 'desk-light-a', 'conditions': 'Same camera and diffuse light', 'repeat': 1}
        state = self.store.create({'capture_context': context})
        sequence = {'id': 'test-sweep', 'protocol': 'right_to_left_sweep_v1', 'frame_index': 1,
                    'duration_ms': 10000, 'intended_elapsed_ms': 0, 'elapsed_ms': 2.5}
        controls = {'version': 'webcam_camera_controls_v1', 'controls': [], 'attempts': []}
        result = self.store.capture(state['id'], {**self.payload('turn_00'), 'capture_sequence': sequence, 'camera_controls': controls})
        self.assertEqual(result['captures'][0]['capture_sequence'], sequence)
        self.assertNotIn('pass', result['captures'][0])
        self.assertEqual(result['capture_context'], context)
        self.assertEqual(result['captures'][0]['camera_controls'], controls)
        self.assertEqual(result['captures'][0]['capture_quality']['policy']['version'], 'webcam_capture_quality_v1')
        restored = self.store.restore(self.store.export(state['id']))
        self.assertEqual(restored['captures'][0]['capture_quality'], result['captures'][0]['capture_quality'])
        self.assertEqual(restored['capture_context'], context)

    def test_export_reload_hashes_and_archive_traversal(self):
        state = self.store.create(); self.store.capture(state['id'], self.payload())
        archive = self.store.export(state['id'])
        restored = self.store.restore(base64.b64encode(archive).decode())
        self.assertNotEqual(restored['id'], state['id']); self.assertEqual(len(restored['captures']), 1)
        self.assertEqual(self.store.load(state['id'])['captures'], restored['captures'])
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as z:
            z.writestr('bundle.json', json.dumps({'version': state['version'], 'files': {'../escape': digest(b'bad')}})); z.writestr('../escape', b'bad')
        with self.assertRaises(ValueError):
            self.store.restore(base64.b64encode(out.getvalue()).decode())
        self.assertFalse((self.root.parent/'escape').exists())

    def test_recovery_marks_interrupted_and_preserves_captures(self):
        state = self.store.create(); state = self.store.capture(state['id'], self.payload())
        state['status'] = 'processing'; self.store.save(state)
        recovered = Store(self.root).load(state['id'])
        self.assertEqual(recovered['status'], 'interrupted'); self.assertEqual(len(recovered['captures']), 1)

    def test_single_job_cancellation_and_no_partial_success(self):
        state = self.store.create(); payload = self.payload()
        for slot in ['front']+['turn_'+str(i).zfill(2) for i in range(60)]:
            self.store.capture(state['id'], {**payload, 'slot': slot})
        entered = threading.Event()
        def fake_reconstruct(folder, state, run, update, cancelled):
            entered.set()
            while not cancelled():
                time.sleep(.01)
            raise InterruptedError('cancelled')
        with patch('dimension_pipeline.webcam_pilot.reconstruct', fake_reconstruct):
            self.store.start(state['id']); self.assertTrue(entered.wait(2))
            with self.assertRaises(ValueError):
                self.store.start(state['id'])
            self.store.cancel(state['id'])
            deadline = time.monotonic()+3
            while self.store.job and time.monotonic() < deadline:
                time.sleep(.01)
        final = self.store.load(state['id'])
        self.assertEqual(final['status'], 'cancelled'); self.assertIsNone(final['result'])

    def test_host_and_exact_origin_validation(self):
        handler = type('TestHandler', (Handler,), {'store': self.store, 'log_message': lambda *args: None})
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            for origin, host, expected in [('http://127.0.0.1:5178', f'127.0.0.1:{server.server_port}', 200),
                                           ('https://evil.test', f'127.0.0.1:{server.server_port}', 403),
                                           ('http://localhost:9999', f'127.0.0.1:{server.server_port}', 403),
                                           ('http://127.0.0.1:5178', 'evil.test', 403)]:
                conn = HTTPConnection('127.0.0.1', server.server_port)
                conn.request('GET', '/sessions', headers={'Origin': origin, 'Host': host})
                response = conn.getresponse(); response.read(); self.assertEqual(response.status, expected); conn.close()
        finally:
            server.shutdown(); server.server_close(); thread.join()

    def test_calibration_reload_keeps_raw_predictions_separate_from_review(self):
        import trimesh
        state = self.store.create(); state['status'] = 'surface_ready'
        trimesh.Trimesh(vertices=mesh()['vertices'], faces=mesh()['triangles'], process=False).export(self.store.folder(state['id'])/'full.ply')
        state['result'] = {'surface': {'mesh': mesh(), 'units': 'reconstruction_unit'}, 'cameras': {'front': camera()},
                           'frontal_camera_key': 'front', 'raw_predictions': [{'x': .5, 'y': .5, 'z': 0.}],
                           'full_mesh': 'full.ply',
                           'projected_points': project(mesh(), camera(), [{'x': .5, 'y': .5, 'z': 0.}])}
        self.store.save(state)
        payload = {'scale_readings_mm': [90., 100., 110.], 'check_readings_mm': [100., 110., 120.],
                   'scale_route': route('subnasale'), 'check_route': route('menton'), 'coverage_reviewed': True}
        self.store.draft(state['id'], payload)
        self.store.calibration(state['id'], payload)
        self.store.decisions(state['id'], {'index': 0, 'decision': 'accepted'})
        reloaded = self.store.load(state['id'])
        self.assertEqual(reloaded['calibrated']['projected_points'][0]['acceptance'], 'accepted')
        self.assertEqual(reloaded['result']['projected_points'][0]['acceptance'], 'pending')
        self.assertEqual(reloaded['result']['surface']['units'], 'reconstruction_unit')
        self.assertEqual(reloaded['draft']['scale_route'], payload['scale_route'])
        full_mm = trimesh.load(self.store.folder(state['id'])/reloaded['calibrated']['full_mesh'], process=False)
        factor = reloaded['calibrated']['report']['mm_per_reconstruction_unit']
        self.assertAlmostEqual(full_mm.vertices[0][2], 5*factor, places=5)
        original = trimesh.load(self.store.folder(state['id'])/'full.ply', process=False)
        self.assertEqual(original.vertices[0][2], 5.)

    def test_pipeline_rejects_partial_models_and_excludes_frontal_from_features(self):
        from PIL import Image
        state = self.store.create(); folder = self.store.folder(state['id']); captures = []
        for index, slot in enumerate(['front']+['turn_'+str(i).zfill(2) for i in range(60)]):
            Image.new('RGB', (64, 64), 'red').save(folder/(slot+'.png'))
            mask = Image.new('L', (64, 64)); mask.paste(255, (10, 10, 50, 50)); mask.save(folder/(slot+'-mask.png'))
            captures.append({'slot': slot, 'role': 'frontal' if index == 0 else 'reconstruction', 'image': slot+'.png', 'mask': slot+'-mask.png'})
        state['captures'] = captures
        def run(stage, command, work):
            if stage == 'masked_features':
                names = (work/'reconstruction.txt').read_text().splitlines()
                self.assertEqual(len(names), 60); self.assertNotIn('front.png', names)
                self.assertIn('--ImageReader.mask_path', command); self.assertIn('--FeatureExtraction.use_gpu', command)
                self.assertEqual(Image.open(work/'images/turn_00.png').getpixel((0, 0)), (0, 0, 0))
            if stage == 'overlap_matching':
                pairs = set((work/'pairs.txt').read_text().splitlines())
                self.assertIn('turn_00.png turn_06.png', pairs)
                self.assertIn('turn_29.png turn_30.png', pairs)
                self.assertNotIn('turn_00.png turn_30.png', pairs)
            if stage == 'sparse_reconstruction':
                (work/'sparse/0').mkdir()
        # An intentionally insufficient analytic test model must fail before meshing/detection.
        with patch('dimension_pipeline.webcam_reconstruction.diagnostics', return_value={'ready': True}), patch(
            'dimension_pipeline.webcam_reconstruction.read_model', return_value={f'turn_{i:02}.png': {'camera_id': 1} for i in range(10)}
        ):
            with self.assertRaisesRegex(ValueError, 'Insufficient reconstruction'):
                reconstruct(folder, state, run, lambda stage: None, lambda: False)


if __name__ == '__main__':
    unittest.main()
