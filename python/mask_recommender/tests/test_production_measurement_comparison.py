import numpy as np
import pytest

from mask_recommender.scripts import compare_production_measurements as comparison
from mask_recommender.tests.test_direct_measurement_comparison import sample


def test_production_inputs_recompute_both_mismatches_and_preserve_mask():
    frame, people = sample()
    frame['perimeter_diff'] = 999.
    result = comparison.arkit_inputs(frame, people)
    expected = people.set_index('user_id').loc[frame.user_id, comparison.TARGET_COLUMNS]
    assert np.allclose(result.nose_mm, expected.nose_mm)
    assert np.allclose(result.perimeter_mm, frame.mask_perimeter_mm)
    assert np.allclose(result.perimeter_diff, (result[comparison.train.FACIAL_MEASUREMENTS].sum(axis=1)-result.perimeter_mm)/10)
    assert np.allclose(result.perimeter_diff_sq, result.perimeter_diff**2)
    assert (frame.perimeter_diff == 999).all()


def test_real_production_trainer_and_predictor_are_reused(monkeypatch):
    frame, people = sample()
    fitting = frame.loc[frame.user_id != 7]
    testing = frame.loc[frame.user_id == 7]
    seen = []
    original = comparison.train.train_custom_lr_with_split
    def train(fitting, training_idx, validation_idx, metadata, **kwargs):
        seen.append((set(fitting.user_id), metadata, kwargs))
        return original(fitting, training_idx, validation_idx, metadata, **kwargs)
    monkeypatch.setattr(comparison.train, 'train_custom_lr_with_split', train)
    model = comparison.ProductionArkit(seed=42, epochs=2).fit(fitting, people.loc[people.user_id != 7])
    assert seen[0][0] == set(range(1,7))
    assert seen[0][1]['nose_model'] == 'latent_nose_v1'
    assert seen[0][2] == {'epochs': 2, 'learning_rate': .01, 'class_weighting': False}
    assert {'nose_center_log_cm', 'nose_strength_raw', 'alpha_mask_raw'} <= set(model.params)
    direct = comparison.train._predict_custom_lr_probabilities(
        comparison.arkit_inputs(testing, people), model.params, model.metadata)
    assert np.array_equal(model.predict(testing, people), direct)
    with pytest.raises(ValueError, match='overlaps'):
        model.predict(fitting, people)


def test_seven_people_same_observations_with_production_arm(monkeypatch):
    frame, people = sample()
    for column in comparison.TARGET_COLUMNS:
        frame[column] = frame.user_id.map(people.set_index('user_id')[column])
    frame['perimeter_diff'] = (frame[comparison.train.FACIAL_MEASUREMENTS].sum(axis=1)-frame.mask_perimeter_mm)/10
    calls = []
    original = comparison.ProductionArkit.fit
    def fit(self, fitting, training_people):
        calls.append((set(fitting.user_id), set(training_people.user_id)))
        return original(self, fitting, training_people)
    monkeypatch.setattr(comparison.ProductionArkit, 'fit', fit)
    report, private = comparison.evaluate(frame, people.to_dict('records'), seeds=[42], epochs=1)
    assert len(calls) == 7
    for i, (fitting, training_people) in enumerate(calls):
        assert fitting == training_people == set(range(1,8))-{i+1}
    predictions = private[0]['arms']
    keys = [[(r['user_id'],r['fit_test_id'],r['label']) for r in rows] for rows in predictions.values()]
    assert keys[0] == keys[1] == keys[2]
    assert report['paired_people'] == 7
    assert report['test_rows'] == 14
    assert all(f['arms']['production_arkit']['architecture'] == 'custom_lr + latent_nose_v1'
               for f in report['runs'][0]['folds'])
