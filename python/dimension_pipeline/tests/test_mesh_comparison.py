import copy
import hashlib
import tempfile
import threading
import unittest
import json
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import numpy as np
import trimesh

from dimension_pipeline.mesh_comparison import compare_session, mesh_identity
from dimension_pipeline.webcam_pilot import Handler, Store


class ComparisonTests(unittest.TestCase):
    def fixture(self, folder):
        raw = {'vertices': [[0., 0., 0.], [2., 0., 0.], [0., 2., 0.]], 'triangles': [[0, 1, 2]]}
        # Parallel equal triangles differ only by z=1; no registration may erase it.
        full = trimesh.Trimesh(vertices=np.asarray(raw['vertices'])+[0, 0, 1], faces=raw['triangles'], process=False)
        (folder/'full.ply').write_bytes(full.export(file_type='ply'))
        return {'id': 'a'*32, 'result': {'full_mesh': 'full.ply', 'surface': {'units': 'reconstruction_unit', 'mesh': raw}}}

    def test_known_offset_bidirectional_sampling_and_originals_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); state = self.fixture(folder); before = copy.deepcopy(state)
            digest = hashlib.sha256((folder/'full.ply').read_bytes()).hexdigest()
            report = compare_session(folder, state, count=100)
            self.assertEqual(report, compare_session(folder, state, count=100))
            for direction in ('full_to_analysis', 'analysis_to_full'):
                for key in ('mean', 'rms', 'median', 'p95', 'sampled_max'):
                    self.assertAlmostEqual(report['deviation'][direction][key], 1.)
            self.assertEqual(report['deviation']['full_to_analysis']['seed'], 0)
            self.assertEqual(report['deviation']['analysis_to_full']['seed'], 1)
            self.assertFalse(report['deviation']['is_hausdorff_bound'])
            self.assertEqual(report['units'], 'reconstruction_unit')
            self.assertEqual(report['variants'][0]['sha256'], digest)
            self.assertEqual(hashlib.sha256((folder/'full.ply').read_bytes()).hexdigest(), digest)
            self.assertEqual(state, before)

    def test_calibrated_distances_and_mesh_identity_are_separate_from_topology(self):
        with tempfile.TemporaryDirectory() as temp:
            state = self.fixture(Path(temp)); identity = mesh_identity(state['result']['surface']['mesh'])
            state['calibrated'] = {'report': {'mm_per_reconstruction_unit': 10.}}
            report = compare_session(Path(temp), state, count=30)
            self.assertEqual(report['units'], 'mm')
            self.assertAlmostEqual(report['deviation']['full_to_analysis']['rms'], 10.)
            self.assertEqual(report['annotation_mesh_id'], identity)
            self.assertNotEqual(report['variants'][0]['mesh_id'], identity)
            reordered = copy.deepcopy(state['result']['surface']['mesh'])
            reordered['triangles'] = [[2, 0, 1]]
            self.assertNotEqual(mesh_identity(reordered), identity)

    def test_missing_coverage_is_not_repaired_and_paths_are_session_scoped(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); state = self.fixture(folder)
            state['result']['full_mesh'] = '../outside.ply'
            with self.assertRaises(ValueError): compare_session(folder, state, count=10)
            state['result']['full_mesh'] = 'full.ply'
            state['result']['surface']['mesh']['triangles'] = []
            with self.assertRaises(ValueError): compare_session(folder, state, count=10)

    def test_resource_limits_fail_without_changing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); state = self.fixture(folder); before = (folder/'full.ply').read_bytes()
            with patch('dimension_pipeline.mesh_comparison.MAX_FILE_BYTES', 1), self.assertRaisesRegex(ValueError, '64 MiB'):
                compare_session(folder, state)
            with self.assertRaisesRegex(ValueError, 'Unknown inspection variant'):
                compare_session(folder, state, variant='../full.ply')
            self.assertEqual((folder/'full.ply').read_bytes(), before)
            (folder/'full.ply').write_bytes(before.replace(b'element vertex 3', b'element vertex 999999999999'))
            with self.assertRaisesRegex(ValueError, 'limits'):
                compare_session(folder, state)

    def test_comparison_endpoint_origin_variant_and_memory_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Store(temp); initial = store.create(); folder = store.folder(initial['id'])
            state = self.fixture(folder); state['id'] = initial['id']; store.save(state)
            handler = type('ComparisonHandler', (Handler,), {'store': store, 'log_message': lambda *args: None})
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            def request(suffix='', origin='http://127.0.0.1:5178'):
                conn = HTTPConnection('127.0.0.1', server.server_port)
                conn.request('GET', f"/sessions/{state['id']}/mesh-comparison{suffix}", headers={'Origin': origin})
                response = conn.getresponse(); result = response.status, json.loads(response.read()); conn.close(); return result
            try:
                status, report = request('?variant=raw')
                self.assertEqual(status, 200); self.assertEqual(report['session_id'], state['id'])
                self.assertEqual(request(origin='https://evil.test')[0], 403)
                self.assertEqual(request('?variant=unknown')[0], 422)
                with patch('dimension_pipeline.webcam_pilot.compare_session', side_effect=MemoryError('Insufficient memory')):
                    self.assertEqual(request()[0], 422)
                self.assertEqual(store.load(state['id']), state)
            finally:
                server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
