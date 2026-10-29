"""Adapter plumbing tests use an owned tetrahedron, never a substitute FLAME asset."""

import io
import json
import pickle
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np

from dimension_pipeline.flame_open import ArrayUnpickler, generate, load_model


def toy_model():
    vertices = np.array([[0., 0., 0.], [.1, 0., 0.], [0., .1, 0.], [0., 0., .1]])
    basis = np.zeros((4, 3, 400))
    basis[1, 0, 0] = .002
    basis[2, 1, 1] = .003
    # This expression direction must never enter the neutral shape-only pilot.
    basis[:, :, 300] = 100
    return {'v_template': vertices, 'shapedirs': basis, 'f': np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])}


class FlameOpenTest(unittest.TestCase):
    def test_open_archive_load_and_shape_generation_preserve_scale_and_topology(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root/'FLAME2023Open.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('models/flame2023_Open.pkl', pickle.dumps(toy_model(), protocol=4))
            report = generate(archive, root/'run', 'm')
            neutral = json.loads((root/'run/neutral.json').read_text())
            plus = json.loads((root/'run/pc1-plus.json').read_text())
            self.assertEqual(neutral['mesh']['vertices'][1], [100., 0., 0.])
            self.assertEqual(plus['mesh']['vertices'][1], [102., 0., 0.])
            self.assertEqual(neutral['mesh']['triangles'], plus['mesh']['triangles'])
            self.assertEqual(neutral['source']['identity_id'], plus['source']['identity_id'])
            self.assertEqual(neutral['preview_camera'], plus['preview_camera'])
            self.assertEqual(len(list((root/'run').glob('*.svg'))), 35)
            self.assertEqual(report['meshes'][0]['rms_vertex_change_mm'], 0)
            self.assertEqual(report['meshes'][2]['rms_vertex_change_mm'], 1)
            self.assertEqual(report['decision'], 'pending_visual_and_anatomical_review')
            self.assertTrue(report['source']['archive_sha256'])
            # Explicit units must be checked, never silently normalized to a head size.
            with self.assertRaisesRegex(ValueError, 'source-units'):
                generate(archive, root/'bad-units', 'mm')
            self.assertFalse((root/'bad-units').exists())

    def test_reflection_converts_coordinates_and_winding_together(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root/'flame2023_Open.pkl'
            model.write_bytes(pickle.dumps(toy_model(), protocol=5))
            generate(model, root/'run', 'm', 'subject_right')
            neutral = json.loads((root/'run/neutral.json').read_text())
            self.assertEqual(neutral['mesh']['vertices'][1], [-100., 0., 0.])
            self.assertEqual(neutral['mesh']['triangles'][0], [0, 1, 2])

    def test_coefficient_magnitude_is_explicit_and_degenerate_variants_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root/'flame2023_Open.pkl'
            data = toy_model()
            data['shapedirs'][1, 0, 0] = -.1
            model.write_bytes(pickle.dumps(data))
            # A full coefficient collapses vertex 1 onto vertex 0.
            with self.assertRaisesRegex(ValueError, 'degenerate triangles'):
                generate(model, root/'collapsed', 'm')
            self.assertFalse((root/'collapsed').exists())
            generate(model, root/'bounded', 'm', coefficient=.5)
            plus = json.loads((root/'bounded/pc1-plus.json').read_text())
            self.assertEqual(plus['mesh']['vertices'][1], [50., 0., 0.])
            self.assertEqual(plus['generation']['coefficient_magnitude'], .5)
            for invalid in [0, -1, float('nan'), 3]:
                with self.assertRaisesRegex(ValueError, 'coefficient magnitude'):
                    generate(model, root/'invalid', 'm', coefficient=invalid)

    def test_invalid_models_and_non_open_archives_fail_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with zipfile.ZipFile(root/'older.zip', 'w') as archive:
                archive.writestr('flame2023.pkl', pickle.dumps(toy_model()))
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                load_model(root/'older.zip')
            for mutate in [lambda d: d['v_template'].__setitem__((0, 0), np.nan),
                           lambda d: d.__setitem__('shapedirs', np.zeros((4, 3, 2))),
                           lambda d: d['f'].__setitem__((0, 0), 999)]:
                data = toy_model(); mutate(data)
                model = root/'flame2023_Open.pkl'; model.write_bytes(pickle.dumps(data))
                with self.assertRaises(ValueError):
                    load_model(model)

    def test_pickle_globals_are_restricted(self):
        class NonArrayObject:
            def __reduce__(self):
                return eval, ('1 + 1',)
        with self.assertRaisesRegex(ValueError, 'Unsupported model pickle global'):
            ArrayUnpickler(io.BytesIO(pickle.dumps(NonArrayObject()))).load()


if __name__ == '__main__':
    unittest.main()
