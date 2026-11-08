import unittest

import numpy as np
from scipy.optimize._numdiff import approx_derivative

from dimension_pipeline.realdenseface_fit import relative_depth, residual_and_jacobian, visibility


class DenseFitTest(unittest.TestCase):
    def test_relative_depth_is_invariant_to_camera_translation(self):
        vertices = np.array([[.1, 0, .2], [0, .1, 0]])
        neck = np.array([0., -.1, -.03])
        pose = np.array([3., .2, .1, 0., 0., .8])
        expected = relative_depth(vertices, neck, pose)
        pose[3:] += [1, 2, 3]
        np.testing.assert_allclose(relative_depth(vertices, neck, pose), expected)
        np.testing.assert_allclose(relative_depth(vertices+1, neck+1, pose), expected)

    def test_jacobian_matches_finite_differences_for_shape_focal_and_cameras(self):
        rng = np.random.default_rng(18)
        template = rng.uniform(-.08, .08, (8, 3))
        basis = rng.normal(0, .002, (8, 3, 3))
        neck = np.array([0., -.1, -.03])
        neck_basis = rng.normal(0, .001, (3, 3))
        poses = np.array([[3., .2, .1, 0., 0., .8], [2.8, -.3, .1, .01, 0, .9]])
        views = [{'size': [1920, 1080], 'ids': np.arange(8), 'xy': rng.uniform(500, 1000, (8, 2)),
                  'depth': rng.uniform(-.1, .1, 8), 'coord_logvar': np.full(8, -7.), 'depth_logvar': np.full(8, -6.)} for _ in poses]
        masks = [np.array([1, 0, 1, 1, 0, 1, 1, 1], dtype=bool) for _ in poses]
        x = np.r_[[.2, -.1, .3], .1, poses.ravel()]
        def evaluate(p, jac=False):
            return residual_and_jacobian(p[:3], p[3], p[4:].reshape(-1, 6), template, basis,
                                         neck, neck_basis, views, masks, 2., 100., jacobian=jac)
        numerical = approx_derivative(evaluate, x, method='3-point')
        np.testing.assert_allclose(evaluate(x, True).toarray(), numerical, rtol=2e-4, atol=2e-4)

    def test_ray_visibility_rejects_intervening_surface(self):
        vertices = np.array([[-1., -1, 1], [0, 1, 1], [1, -1, 1],
                             [0, 0, 2], [.1, .1, 2], [.1, -.1, 2]])
        faces = np.array([[0, 1, 2], [3, 4, 5]])
        keep = visibility(vertices, faces, np.zeros(6), np.array([0, 3]))
        self.assertTrue(keep[0])
        self.assertFalse(keep[1])


if __name__ == '__main__':
    unittest.main()
