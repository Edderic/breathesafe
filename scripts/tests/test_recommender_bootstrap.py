"""Check cluster multiplicity, per-seed ratios and paired differences."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np

spec = importlib.util.spec_from_file_location('bootstrap', Path(__file__).parents[1]/'presentations/bootstrap_recommender.py')
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def test_cluster_multiplicity_matches_explicit_repeated_rows(self):
        rows = [dict(user_id=1, label=1, probability=.8),
                dict(user_id=1, label=0, probability=.7),
                dict(user_id=2, label=0, probability=.1)]
        stats = bootstrap.sufficient(rows, [1, 2])
        repeated = bootstrap.sufficient(rows[:2]*2, [1])
        np.testing.assert_allclose(bootstrap.metrics(stats[0]*2),
                                   bootstrap.metrics(repeated[0]))
        self.assertEqual(stats[0, 5], 2)
        self.assertEqual(stats[1, 5], 1)

    def test_paired_identical_models_have_zero_difference(self):
        stats = np.array([[[[2, 1, 3, 1, 2, 7], [1, 2, 1, 1, 3, 5]],
                           [[1, 2, 3, 1, 4, 7], [2, 1, 1, 1, 3, 5]]]]*2)
        draws = bootstrap.resample(stats, 100, 17)
        np.testing.assert_array_equal(draws[:, 0], draws[:, 1])
        np.testing.assert_array_equal(draws, bootstrap.resample(stats, 100, 17))
        weights = np.random.default_rng(17).multinomial(2, [.5, .5], size=100)
        explicit = []
        for w in weights:
            # Recompute ratios separately for each seed before averaging.
            explicit.append([np.mean([bootstrap.metrics((w[:, None]*seed).sum(axis=0))
                                      for seed in variant], axis=0) for variant in stats])
        np.testing.assert_allclose(draws, explicit)

    def test_undefined_metrics_are_not_fabricated(self):
        values = bootstrap.metrics(np.array([0, 0, 5, 0, 1, 5]))
        self.assertTrue(np.isnan(values[0]))
        self.assertTrue(np.isnan(values[1]))
        self.assertEqual(values[2], 1)
        with self.assertRaises(ValueError):
            bootstrap.interval(np.array([np.nan, 1.]), 1.)

    def test_superiority_direction_ties_and_undefined_draws(self):
        draws = np.array([2., 1., 0., -1., np.nan])
        higher = bootstrap.superiority(draws)
        self.assertEqual(higher['better_replicates'], 2)
        self.assertEqual(higher['tied_replicates'], 1)
        self.assertEqual(higher['worse_replicates'], 1)
        self.assertEqual(higher['undefined_replicates'], 1)
        self.assertEqual(higher['better_frequency'], .5)
        self.assertEqual(bootstrap.superiority(draws, True)['better_frequency'], .25)
        self.assertEqual(bootstrap.superiority(np.zeros(10))['better_frequency'], 0)


if __name__ == '__main__':
    unittest.main()
