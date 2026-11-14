"""Scientific checks for the historical conversion figure and censored model."""
import importlib.util
import json
from pathlib import Path

import numpy as np

SOURCE = Path(__file__).resolve().parents[1] / 'presentations/analyze_n95_conversion.py'
spec = importlib.util.spec_from_file_location('n95_conversion_analysis', SOURCE)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def test_assigned_and_contaminated_aggregates_do_not_become_measured_pairs():
    points, excluded, _, _ = analysis.extract_pairs(json.loads(analysis.NOTEBOOK.read_text()))
    assert len(points) == 24 and excluded == 12
    assert min(p['measured_n95'] for p in points) > 15
    assert sum(p['measured_n95'] == 200 for p in points) == 8
    assert sum(p['conversion_estimate'] == 200 for p in points) == 9


def test_censoring_uses_tail_probability_not_density_at_ceiling():
    # Identical prior density at alpha 2 vs 2.5 around its center is accounted for.
    theta = np.array([[2., 0., np.log(.2)], [2.5, 0., np.log(.2)]])
    censored = analysis.log_posterior(theta, np.array([0.]), np.array([2.]), np.array([True]))
    exact = analysis.log_posterior(theta, np.array([0.]), np.array([2.]), np.array([False]))
    assert censored[1] > censored[0]  # Above-ceiling means make >=200 more probable.
    assert exact[1] < exact[0]        # Exact 200 instead penalizes above-ceiling means.


def test_sampler_recovers_known_censored_synthetic_relationship():
    rng = np.random.default_rng(91)
    x = np.linspace(-.8, .5, 120)
    latent_y = 1.8 + .85*x + rng.normal(0, .12, len(x))
    censored = latent_y >= 2
    y = np.minimum(latent_y, 2)
    assert censored.sum() > 10
    posterior, diagnostics = analysis.sample_posterior(x, y, censored, seed=92, warmup=2500, draws=8000)
    assert abs(np.median(posterior[:, 0])-1.8) < .08
    assert abs(np.median(posterior[:, 1])-.85) < .12
    assert max(diagnostics['split_rhat']) < 1.01
