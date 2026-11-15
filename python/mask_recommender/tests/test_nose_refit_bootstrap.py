"""Batched independent training must agree with explicit production refits."""
import numpy as np
import pandas as pd
import pytest
import torch

from mask_recommender import train
from mask_recommender.scripts import bootstrap_nose_refit as bootstrap


def fixture():
    return pd.DataFrame(dict(
        fit_family_id=[1, 2, 1, 2, 1, 2], style=['Bifold', 'Cup']*3,
        strap_type=['Headstrap', 'Earloop']*3,
        user_id=[1, 1, 2, 2, 3, 3],
        nose_mm=[35., 35., 45., 45., 25., 25.],
        chin_mm=[110.]*6, top_cheek_mm=[100.]*6, mid_cheek_mm=[100.]*6,
        strap_mm=[150.]*6, perimeter_diff=[-2., 1., 3., -1., 0., 2.],
        perimeter_diff_sq=[4., 1., 9., 1., 0., 4.],
        qlft_pass_normalized=[1., 0., 0., 1., 1., 0.]))


@pytest.mark.parametrize('variant', bootstrap.VARIANTS)
def test_independent_batch_matches_explicit_duplicate_production_training(variant):
    torch.set_num_threads(1)
    frame = fixture()
    metadata = dict(train._custom_lr_category_metadata(frame), nose_model=variant)
    data = train.prep_data_in_torch_with_categories(frame, metadata['fit_family_categories'],
        metadata['style_categories'], metadata['strap_type_categories'])
    y = torch.tensor(frame.qlft_pass_normalized.to_numpy(dtype=np.float32))
    # Two different resampled training populations, with some zero-weight people.
    weights = np.array([[2, 2, 0, 0, 1, 1], [0, 0, 1, 1, 2, 2]])
    params = bootstrap.refit(data, y, weights, metadata, variant, 43, epochs=200)
    with torch.no_grad():
        batched = bootstrap.batched_probs(data, params).numpy()
    for i, w in enumerate(weights):
        repeated = frame.iloc[np.repeat(np.arange(len(frame)), w)].reset_index(drop=True)
        torch.manual_seed(43)
        index = torch.arange(len(repeated))
        fitted = train.train_custom_lr_with_split(repeated, index, index, metadata, epochs=200)
        expected = train._predict_custom_lr_probabilities(frame, fitted['params'], metadata)
        np.testing.assert_allclose(batched[i], expected, atol=2e-6, rtol=2e-5)
    # A draw is unaffected by which other independent models share its batch.
    single = bootstrap.refit(data, y, weights[:1], metadata, variant, 43, epochs=200)
    with torch.no_grad():
        np.testing.assert_allclose(bootstrap.batched_probs(data, single).numpy()[0], batched[0], atol=2e-6)


def test_weighted_metrics_match_explicit_observation_copies():
    y = np.array([1., 0., 1.])
    p = np.array([[.9, .8, .2]])
    w = np.array([[2, 1, 3]])
    actual = bootstrap.stats(y, p, w)
    repeated = np.repeat(np.arange(3), w[0])
    explicit = bootstrap.stats(y[repeated], p[:, repeated], np.ones((1, len(repeated))))
    np.testing.assert_allclose(actual, explicit)
    np.testing.assert_allclose(bootstrap.metrics(actual), bootstrap.metrics(explicit))


def test_superiority_counts_direction_ties_and_undefined():
    draws = np.array([[[.2]*5, [.3]*5], [[.3]*5, [.2]*5], [[.2]*5, [.2]*5],
                      [[np.nan]*5, [.2]*5]])
    result = bootstrap.summarize(draws, draws[0])
    for name in bootstrap.METRICS:
        row = result['superiority'][name]
        assert row['better_replicates'] == row['worse_replicates'] == row['tied_replicates'] == 1
        assert row['undefined_replicates'] == 1
        assert row['valid_replicates'] == 3
