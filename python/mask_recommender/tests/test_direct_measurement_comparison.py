import numpy as np
import pandas as pd
import pytest

from mask_recommender.scripts import compare_direct_measurements as comparison


def sample():
    people = pd.DataFrame([dict(user_id=user,
        **{key: 20 + user * (i + 1) + (user % (i + 2)) for i, key in enumerate(
            comparison.FEATURE_COLUMNS + comparison.TARGET_COLUMNS)}) for user in range(1, 8)])
    frame = pd.DataFrame([dict(user_id=user, id=user*10+label, mask_id=label+1,
        fit_family_id=label+1, style='Bifold', strap_type='Headstrap',
        qlft_pass_normalized=label, mask_perimeter_mm=300+label*20)
        for user in range(1, 8) for label in [0,1]])
    return frame, people


def test_preprocessing_fits_unique_training_people_not_test_outliers_or_repeats():
    frame, people = sample()
    training = frame.loc[frame.user_id != 7]
    training = pd.concat([training, training.loc[training.user_id == 1]] * 2, ignore_index=True)
    model = comparison.FaceMaskClassifier('traditional_pca3').fit(training, people)
    expected = people.loc[people.user_id != 7, comparison.FEATURE_COLUMNS].mean().to_numpy()
    assert np.allclose(model.face_scaler.mean_, expected)
    assert model.pca.n_samples_ == 6
    assert model.pca.n_components_ == 3
    assert model.training_people == set(range(1,7))
    scaler_before = model.face_scaler.mean_.copy()
    people.loc[people.user_id == 7, comparison.FEATURE_COLUMNS] = 10000.
    scores = model.predict(frame.loc[frame.user_id == 7], people)
    assert np.isfinite(scores).all()
    assert np.array_equal(model.face_scaler.mean_, scaler_before)


def test_all_input_arms_use_correct_direct_columns_and_unknown_mask_fallback():
    frame, people = sample()
    training = frame.loc[frame.user_id != 7]
    testing = frame.loc[frame.user_id == 7].copy()
    testing['fit_family_id'] = 999
    for arm in comparison.ARMS:
        model = comparison.FaceMaskClassifier(arm).fit(training, people)
        assert model.columns == (comparison.TARGET_COLUMNS if arm == 'measured_arkit' else comparison.FEATURE_COLUMNS)
        assert np.isfinite(model.predict(testing, people)).all()


def test_evaluation_trains_exact_same_six_people_per_arm(monkeypatch):
    frame, people = sample()
    # paired_frame derives the known mask perimeter from original ARKit paths.
    for column in comparison.TARGET_COLUMNS:
        frame[column] = frame.user_id.map(people.set_index('user_id')[column])
    frame['perimeter_diff'] = (frame[comparison.train.FACIAL_MEASUREMENTS].sum(axis=1)-frame.mask_perimeter_mm)/10
    calls = []
    original = comparison.FaceMaskClassifier.fit
    def fit(self, fitting, training_people):
        calls.append((self.arm, set(fitting.user_id), set(training_people.user_id)))
        return original(self, fitting, training_people)
    monkeypatch.setattr(comparison.FaceMaskClassifier, 'fit', fit)
    report, predictions = comparison.evaluate(frame, people.to_dict('records'))
    assert len(calls) == 21
    for fold in range(7):
        group = calls[fold*3:fold*3+3]
        expected = set(range(1,8)) - {fold+1}
        assert all(fitting == training == expected for _, fitting, training in group)
    keys = [[(r['user_id'],r['fit_test_id'],r['label']) for r in rows] for rows in predictions.values()]
    assert keys[0] == keys[1] == keys[2]
    assert report['paired_people'] == 7
    assert report['test_rows'] == 14


def test_rejects_too_few_paired_people():
    frame, people = sample()
    for column in comparison.TARGET_COLUMNS:
        frame[column] = 40.
    frame['perimeter_diff'] = 0.
    with pytest.raises(ValueError, match='at least four'):
        comparison.paired_frame(frame.loc[frame.user_id <= 3], people.to_dict('records'))
