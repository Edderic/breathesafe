import unittest
import numpy as np
import trimesh

from dimension_pipeline.photogrammetry_trial import triangulate, smooth
from dimension_pipeline.nose_overlays import project_pixels


class PhotogrammetryTrialTest(unittest.TestCase):
    def cameras(self, baseline=1.):
        return [dict(R=np.eye(3).tolist(), t=[x*baseline, 0, 4], fx=800., fy=800., cx=500., cy=400.,
                     k=-.06, width=1000, height=800) for x in (-1., -.35, .35, 1.)]

    def test_distorted_triangulation_rejects_outlier(self):
        cameras = self.cameras()
        point = np.array([[.1, -.2, .3]])
        xy = np.array([project_pixels(c, point) for c in cameras])
        xy[-1] += [70, -40]
        result = triangulate(cameras, xy)[0]
        self.assertEqual(result['status'], 'consistent')
        self.assertEqual(result['inlier_views'], [0, 1, 2])
        np.testing.assert_allclose(result['point'], point[0], atol=1e-7)

    def test_low_parallax_is_rejected(self):
        cameras = self.cameras(1e-5)
        xy = np.array([project_pixels(c, np.array([[.1, -.2, .3]])) for c in cameras])
        self.assertEqual(triangulate(cameras, xy)[0]['status'], 'insufficient_parallax_or_consensus')

    def test_open_boundary_is_fixed_and_raw_unchanged(self):
        mesh = trimesh.Trimesh(vertices=[[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], [0, 0, .2]],
                               faces=[[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]], process=False)
        original = mesh.vertices.copy()
        result, pinned = smooth(mesh, 3)
        np.testing.assert_array_equal(mesh.vertices, original)
        np.testing.assert_array_equal(result.faces, mesh.faces)
        np.testing.assert_array_equal(result.vertices[pinned], original[pinned])
        self.assertLess(abs(result.vertices[4, 2]), .2)

    def test_route_does_not_bridge_missing_control(self):
        from dimension_pipeline.photogrammetry_routes import edge_lengths
        mesh = trimesh.Trimesh(vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]], faces=[[0, 1, 2]], process=False)
        attachments = {0: {'triangle_index': 0, 'weights': [1, 0, 0]},
                       1: {'triangle_index': 0, 'weights': [0, 1, 0]}}
        self.assertEqual(edge_lengths(mesh, attachments, [(0, 1), (1, 2)]), [1., None])

    def test_long_meshing_skirt_is_not_quality_support(self):
        from dimension_pipeline.photogrammetry_review import triangle_quality
        mesh = trimesh.Trimesh(vertices=[[0, 0, 0], [1, 0, 0], [0, .001, 0]], faces=[[0, 1, 2]], process=False)
        self.assertFalse(triangle_quality(mesh, {'triangle_index': 0}, 1.))
