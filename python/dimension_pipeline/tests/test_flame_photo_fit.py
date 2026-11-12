import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from dimension_pipeline.flame_photo_fit import (
    HOLDOUT, TRAIN, embed, fit_identity, fit_pose_only, load_embedding, photo_loss, project, visible,
)


class PhotoFitTest(unittest.TestCase):
    def test_prior_remains_quadratic_when_image_errors_are_robustified(self):
        rho = photo_loss(np.array([100., 100.]), 1)
        self.assertLess(rho[0, 0], 20.)
        np.testing.assert_allclose(rho[:, 1], [100., 1., 0.])

    def test_embedding_preserves_linear_shape_directions(self):
        vertices = np.arange(36.).reshape(4, 3, 3)
        faces = np.array([[0, 1, 2], [1, 2, 3]])
        weights = np.array([[.2, .3, .5]])
        result = embed(vertices, faces, np.array([1]), weights)
        np.testing.assert_allclose(result[0], .2*vertices[1]+.3*vertices[2]+.5*vertices[3])

    def test_reject_negative_or_out_of_topology_embedding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'embedding.npz'
            for weights, triangles in [(np.tile([-1., 1., 1.], (20, 1)), np.zeros(20, dtype=int)),
                                       (np.tile([1., 0., 0.], (20, 1)), np.full(20, 3, dtype=int))]:
                np.savez(path, landmark_indices=np.arange(20), lmk_face_idx=triangles, lmk_b_coords=weights)
                with self.assertRaises(ValueError):
                    load_embedding(path, np.array([[0, 1, 2]]))

    def test_positive_depth_and_facing(self):
        v = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
        f = np.array([[0, 1, 2]])
        pose = np.array([np.pi, 0., 0., 0., 0., 4.])
        self.assertTrue(visible(v, f, np.array([0]), np.array([[1/3]*3]), pose)[0])
        self.assertFalse(visible(v, f[:, ::-1], np.array([0]), np.array([[1/3]*3]), pose)[0])
        np.testing.assert_allclose(project(np.array([[0., 0., 0.]]), pose, 800., (1000, 600)), [[500, 300]])

    def test_holdout_pose_ignores_excluded_points(self):
        rng = np.random.default_rng(42)
        points = rng.uniform(-.1, .1, (30, 3))
        pose = np.array([3.0, .1, .05, .02, -.01, .8])
        observed = project(points, pose, 1000., (1200, 900))
        keep = np.arange(30) >= 10
        corrupted = observed.copy()
        corrupted[~keep] += 200
        estimate = fit_pose_only(points, corrupted, 1000., (1200, 900), keep)
        np.testing.assert_allclose(project(points, estimate, 1000., (1200, 900))[keep], observed[keep], atol=1e-4)

    def test_shared_shape_reduces_two_camera_residual(self):
        rng = np.random.default_rng(11)
        centers = rng.uniform(-.08, .08, (24, 3))
        vertices = np.concatenate([p+np.array([[0, 0, 0], [.001, 0, 0], [0, .001, 0]]) for p in centers])
        faces = np.arange(len(vertices)).reshape(-1, 3)
        weights = np.tile([1., 0., 0.], (24, 1))
        embedding = (np.arange(24), np.arange(24), weights)
        basis = np.zeros((len(vertices), 3, 1))
        basis[:, 2, 0] = np.repeat(rng.uniform(-.02, .02, 24), 3)
        truth = vertices+basis[:, :, 0]*.7
        views = []
        for pose in [np.array([np.pi, 0., 0., 0., 0., .8]), np.array([2.9, .5, .1, .01, 0., .9])]:
            views.append({'size': (1000, 750), 'observations': project(embed(truth, faces, embedding[1], weights), pose, 1200., (1000, 750))})
        shape, beta, focal, poses, history = fit_identity(vertices, basis, faces, embedding, views, components=1, prior=.001, rounds=2)
        self.assertAlmostEqual(beta[0], .7, delta=.02)
        for view, pose in zip(views, poses):
            np.testing.assert_allclose(project(embed(shape, faces, embedding[1], weights), pose, focal, view['size']), view['observations'], atol=.02)
        self.assertTrue(history)

    def test_split_is_fixed_and_disjoint(self):
        self.assertFalse(set(TRAIN) & set(HOLDOUT))
        self.assertEqual(len(set(TRAIN+HOLDOUT)), 13)


if __name__ == '__main__':
    unittest.main()
