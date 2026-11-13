import numpy as np
import pandas as pd
import pytest

from mask_recommender.scripts import compare_measurement_sources as comparison


def test_replacing_measurements_preserves_mask_and_updates_deviations():
    frame = pd.DataFrame([dict(nose_mm=40, strap_mm=120, top_cheek_mm=60,
                              mid_cheek_mm=55, chin_mm=50, perimeter_diff=-9.5)])
    result = comparison.with_measurements(frame, [50, 120, 60, 55, 50])
    assert result.perimeter_mm.iloc[0] == 300
    assert result.perimeter_diff.iloc[0] == -8.5
    assert result.perimeter_diff_sq.iloc[0] == 72.25
    assert frame.nose_mm.iloc[0] == 40


def test_pair_selection_rejects_unknown_and_duplicate_people():
    with pytest.raises(ValueError):
        comparison.paired_summary([{'user_id': 1}, {'user_id': 1}])
    with pytest.raises(ValueError):
        comparison.paired_summary([{'user_id': None}])


def _data():
    summary = [dict(user_id=user, **{k: 40. for k in comparison.FEATURE_COLUMNS + comparison.TARGET_COLUMNS})
               for user in [1, 2, 3]]
    frame = pd.DataFrame([dict(user_id=user, id=user*10+label, mask_id=label+1,
        qlft_pass_normalized=label, nose_mm_observed=True, style='Bifold', strap_type='Headstrap',
        fit_family_id=1, **{k: 40. for k in comparison.TARGET_COLUMNS}, perimeter_diff=0.)
        for user in [1, 2, 3] for label in [0, 1]])
    return frame, summary


def test_both_fitting_stages_exclude_held_out_person_and_arms_match(monkeypatch):
    frame, summary = _data()
    converter_users = []
    def mapper(training):
        users = set(training.user_id)
        converter_users.append(users)
        class Model:
            def predict(self, inputs):
                return np.ones((1, 5))*40
        return Model()
    def fit(training, *args, **kwargs):
        return {'params': {'training_users': set(training.user_id)}}
    def predict(testing, params, metadata):
        assert not set(testing.user_id) & params['training_users']
        return np.full(len(testing), .7)
    monkeypatch.setattr(comparison, 'train_model', mapper)
    monkeypatch.setattr(comparison.train, 'train_custom_lr_with_split', fit)
    monkeypatch.setattr(comparison.train, '_predict_custom_lr_probabilities', predict)
    report, _ = comparison.compare(frame, summary, seeds=[42], epochs=1)
    assert converter_users == [{2, 3}, {1, 3}, {1, 2}]
    assert report['paired_people_available'] == 3
    arms = report['runs'][0]['arms']
    assert arms['arkit'] == arms['traditional_via_conversion']
    assert arms['arkit']['probability_evaluation']['sample_count'] == 6


def test_invalid_conversion_excludes_same_people_from_both_arms(monkeypatch):
    frame, summary = _data()
    class InvalidMapper:
        def predict(self, inputs):
            return np.zeros((1, 5))
    monkeypatch.setattr(comparison, 'train_model', lambda _: InvalidMapper())
    report, _ = comparison.compare(frame, summary, seeds=[42], epochs=1)
    assert report['runs'][0]['excluded_people_count'] == 3
    assert report['runs'][0]['arms'] == {'arkit': None, 'traditional_via_conversion': None}
