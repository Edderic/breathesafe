"""Playground persistence and validation use an owned toy model, not FLAME evidence."""
import json
import pickle
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from dimension_pipeline.flame_playground import Handler, Playground, REPO, coefficients
from dimension_pipeline.tests.test_flame_open import toy_model


class PlaygroundTest(unittest.TestCase):
    def setUp(self):
        (REPO/'tmp').mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix='flame-playground-test-', dir=REPO/'tmp')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.model = self.root/'flame2023_Open.pkl'
        self.model.write_bytes(pickle.dumps(toy_model()))
        self.app = Playground(self.model, self.root/'library', 'm')

    def test_mixed_parameters_round_trip_to_immutable_preview_run(self):
        beta = [0.]*300; beta[0] = .5; beta[1] = -.5; beta[299] = .25
        payload = {'name': 'Jaw / nose study', 'shape_coefficients': beta}
        preview = self.app.preview(payload)
        self.assertEqual(preview['record']['mesh']['vertices'][1], [101., 0., 0.])
        self.assertEqual(preview['record']['mesh']['vertices'][2], [0., 98.5, 0.])
        saved = self.app.save(payload)
        self.assertFalse(saved['already_saved'])
        folder = self.app.library/saved['face']['id']
        record = json.loads((folder/'face.json').read_text())
        manifest = json.loads((folder/'manifest.json').read_text())
        self.assertEqual(record['mesh'], preview['record']['mesh'])
        self.assertEqual(record['generation']['shape_coefficients'], beta)
        self.assertEqual(record['generation']['display_name'], payload['name'])
        self.assertEqual(record['record_id'], manifest['variants'][0]['id'])
        self.assertEqual(manifest['variants'][0]['mesh'], 'face.json')
        before = (folder/'face.json').read_bytes()
        again = self.app.save({**payload, 'name': 'Do not overwrite'})
        self.assertTrue(again['already_saved'])
        self.assertEqual(again['face']['name'], payload['name'])
        self.assertEqual((folder/'face.json').read_bytes(), before)
        restarted = Playground(self.model, self.root/'library', 'm')
        self.assertEqual(restarted.list_faces(), [saved['face']])
        self.assertEqual(restarted.preview(payload)['record']['record_id'], record['record_id'])
        beta[0] = -.5
        self.assertNotEqual(self.app.preview(payload)['record']['record_id'], record['record_id'])

    def test_invalid_coefficients_and_names_never_write_faces(self):
        for values in [[], [0]*299, [0]*301, [True]+[0]*299, [None]+[0]*299,
                       [float('nan')]+[0]*299, [float('inf')]+[0]*299, [2.01]+[0]*299]:
            with self.assertRaises(ValueError):
                self.app.save({'name': 'Test', 'shape_coefficients': values})
        for name in [None, '', '   ', 'x'*81]:
            with self.assertRaises(ValueError):
                self.app.save({'name': name, 'shape_coefficients': [0]*300})
        self.assertEqual(list(self.app.library.iterdir()), [])
        self.assertEqual(coefficients({'shape_coefficients': [-0.]+[0]*299}), [0.]*300)

    def test_normal_flags_are_saved_for_review_but_collapses_reject(self):
        data = toy_model(); data['shapedirs'][1, 0, 0] = -.1
        self.model.write_bytes(pickle.dumps(data))
        app = Playground(self.model, self.root/'other-library', 'm')
        beta = [0.]*300; beta[0] = 1
        with self.assertRaisesRegex(ValueError, 'degenerate'):
            app.preview({'shape_coefficients': beta})
        beta[0] = 2
        result = app.preview({'shape_coefficients': beta})
        self.assertGreater(result['geometry_report']['flipped_triangles_vs_neutral'], 0)
        saved = app.save({'name': 'Flagged', 'shape_coefficients': beta})
        record = json.loads((app.library/saved['face']['id']/'face.json').read_text())
        self.assertEqual(record['review']['status'], 'pending')
        self.assertEqual(record['review']['geometry_report'], result['geometry_report'])
        self.assertEqual(saved['face']['geometry_report'], result['geometry_report'])
        self.assertEqual(len(app.list_faces()), 1)

    def test_origin_host_and_library_boundaries(self):
        with self.assertRaises(ValueError):
            Playground(self.model, REPO/'outside-library', 'm')
        request = SimpleNamespace(server=SimpleNamespace(server_port=5181), headers={
            'Host': '127.0.0.1:5181', 'Origin': 'http://127.0.0.1:5178'})
        self.assertTrue(Handler.permitted(request, write=True))
        request.headers['Origin'] = 'https://example.com'
        self.assertFalse(Handler.permitted(request, write=True))
        del request.headers['Origin']
        self.assertFalse(Handler.permitted(request, write=True))
        self.assertTrue(Handler.permitted(request))
        request.headers['Host'] = 'attacker.example:5181'
        self.assertFalse(Handler.permitted(request))
