from itertools import product

import numpy as np
import pandas as pd
import pytest
from sklearn.decomposition import PCA

from mask_recommender.scripts.fixed_range_models import FixedPhysicalScaler, bounded_pc_scores
from mask_recommender.scripts.bootstrap_fixed_range_comparison import (
    cloned_training, tasks_for_draw, stats, metric_values, summarize, FEATURE_COLUMNS,
)
from mask_recommender.probability_evaluation import evaluate_probabilities


def test_fixed_ranges_do_not_use_training_extrema_or_silently_clip():
    scaler = FixedPhysicalScaler(['face_length'])
    scaler.fit([[112], [127]])
    assert scaler.transform([[77]])[0, 0] == pytest.approx((77-40)/(180-40))
    np.testing.assert_allclose(scaler.transform([[40], [180]]), [[0], [1]])
    with pytest.raises(ValueError, match='outside'):
        scaler.transform([[181]])


def test_pca_bound_is_valid_on_every_corner_not_just_training_scores():
    x = np.random.default_rng(4).uniform(.3, .6, (8, 6))
    pca = PCA(3).fit(x)
    corners = np.array(list(product([0., 1.], repeat=6)))
    values = bounded_pc_scores(pca, corners)
    np.testing.assert_allclose(values.min(axis=0), 0, atol=1e-12)
    np.testing.assert_allclose(values.max(axis=0), 1, atol=1e-12)
    assert np.max(values**2) <= 1+1e-12


def test_bootstrap_copies_keep_person_weight_and_pca_multiplicity():
    people = pd.DataFrame({'user_id': list(range(10, 17)), 'example': range(7)})
    frame = pd.DataFrame({'user_id': [10, 10, 11, 12], 'row': [1, 2, 3, 4]})
    rows, members = cloned_training(frame, people, [2, 1, 0, 0, 0, 0, 0])
    assert len(rows) == 5 and len(members) == 3
    assert rows.user_id.nunique() == 3
    assert members.example.tolist().count(0) == 2
    assert set(members.example) == {0, 1}
    assert rows.row.value_counts().to_dict() == {1: 2, 2: 2, 3: 1}


def test_fixed_pca3_rejects_rank_deficient_bootstrap_groups():
    people = pd.DataFrame(np.random.default_rng(7).normal(size=(7, 6)), columns=FEATURE_COLUMNS)
    assert tasks_for_draw(np.array([2, 2, 2, 1, 0, 0, 0]), people, 'fixed') is None
    tasks = tasks_for_draw(np.array([2, 2, 1, 1, 1, 0, 0]), people, 'fixed')
    assert len(tasks) == 5
    assert all(t[1][t[0]] == 0 and t[2] == 3 for t in tasks)
    adaptive = tasks_for_draw(np.array([2, 2, 2, 1, 0, 0, 0]), people, 'adaptive')
    assert all(t[2] == 2 for t in adaptive)


def test_sufficient_metrics_match_existing_evaluator_and_best_counts_handle_ties():
    y, p = [0, 1, 1, 0], [.1, .7, .3, .8]
    actual = metric_values(stats(y, p))
    expected = evaluate_probabilities(y, p)
    np.testing.assert_allclose(actual, [expected['quality']['log_loss'],
        expected['at_0_5']['precision'], expected['at_0_5']['recall'],
        expected['at_0_5']['negative_predictive_value'], expected['at_0_5']['f1']])
    points = np.ones((2, 3, 5))
    draws = np.ones((2, 2, 3, 5))
    draws[0, :, 0, 0] = .5  # ARKit uniquely best loss; second draw all tied.
    report = summarize(draws, points, 2)['test_weighted']
    assert report['log_loss']['arms']['production_arkit']['strict_best_count'] == 1
    assert report['log_loss']['tie_count'] == 1
    assert report['precision']['tie_count'] == 2
