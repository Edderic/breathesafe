import hashlib
import math
import tempfile
import unittest
from pathlib import Path

from dimension_pipeline.generate_heads import generate, load, project, variant_record, view_frame


class HeadGenerationTest(unittest.TestCase):
    def test_deterministic_runs_have_shared_identity_and_no_degenerate_faces(self):
        base = load('makehuman_head.json')
        for control in load('head_variants.json'):
            record = variant_record(base, control)
            self.assertEqual(record['source']['identity_id'], base['source']['identity_id'])
            self.assertEqual(record['mesh']['triangles'], base['mesh']['triangles'])
            vertices = record['mesh']['vertices']
            self.assertTrue(all(math.isfinite(c) for p in vertices for c in p))
            for face in record['mesh']['triangles']:
                a, b, c = [vertices[i] for i in face]
                u, v = [b[i]-a[i] for i in range(3)], [c[i]-a[i] for i in range(3)]
                self.assertGreater(math.hypot(u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]), 0)
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary)/'one', Path(temporary)/'two'
            self.assertEqual(generate(first), generate(second))
            for p in first.iterdir():
                self.assertEqual(hashlib.sha256(p.read_bytes()).digest(), hashlib.sha256((second/p.name).read_bytes()).digest())
            self.assertEqual(len(list(first.glob('*.svg'))), 35)
            with self.assertRaises(FileExistsError):
                generate(first)

    def test_fixed_cameras_keep_every_variant_inside_capture(self):
        base = load('makehuman_head.json')
        for control in load('head_variants.json'):
            record = variant_record(base, control)
            for view in load('head_views.json'):
                camera = {**view_frame(base), **view}
                for vertex in record['mesh']['vertices']:
                    x, y, _ = project(vertex, camera)
                    self.assertTrue(0 < x < 720 and 0 < y < 480)


if __name__ == '__main__':
    unittest.main()
