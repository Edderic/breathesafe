import numpy as np
import pandas as pd

from mask_recommender.scripts.audit_traditional_scaling import AuditClassifier
from mask_recommender.scripts.compare_direct_measurements import FaceMaskClassifier, FEATURE_COLUMNS


def sample():
    people = pd.DataFrame([dict(user_id=u, **{k: 20+u*(i+1)+u % (i+2)
                                           for i, k in enumerate(FEATURE_COLUMNS)}) for u in range(1, 8)])
    frame = pd.DataFrame([dict(user_id=u, mask_id=y+1, fit_family_id=y+1,
                               style='Bifold', strap_type='Headstrap',
                               qlft_pass_normalized=y, mask_perimeter_mm=300+20*y)
                          for u in range(1, 8) for y in (0, 1)])
    return frame, people


def test_original_design_and_scores_are_preserved():
    frame, people = sample()
    fitting = frame.loc[frame.user_id != 7]
    for arm in ('traditional_direct', 'traditional_pca3'):
        old = FaceMaskClassifier(arm).fit(fitting, people)
        audit = AuditClassifier(arm).fit(fitting, people)
        np.testing.assert_allclose(audit.design(frame, people).toarray(), old.design(frame, people).toarray())
        np.testing.assert_allclose(audit.predict(frame, people), old.predict(frame, people))


def test_expanded_scaling_uses_training_only_and_weights():
    frame, people = sample()
    fitting = pd.concat([frame.loc[frame.user_id != 7], frame.loc[frame.user_id == 1]]*2)
    model = AuditClassifier('traditional_direct', expanded_zscore=True).fit(fitting, people)
    x = model.design(fitting, people).toarray()
    counts = fitting.user_id.value_counts()
    w = fitting.user_id.map(lambda u: 1/counts[u]).to_numpy()
    means = np.average(x, weights=w, axis=0)
    variance = np.average((x-means)**2, weights=w, axis=0)
    np.testing.assert_allclose(variance[variance > 1e-10], 1., atol=1e-9)
    before = model.design_scaler.scale_.copy()
    people.loc[people.user_id == 7, FEATURE_COLUMNS] = 1e6
    assert np.isfinite(model.predict(frame.loc[frame.user_id == 7], people)).all()
    np.testing.assert_array_equal(before, model.design_scaler.scale_)
    np.testing.assert_allclose(model.face_scaler.mean_, people.loc[people.user_id != 7, FEATURE_COLUMNS].mean())


def test_pca_whitening_and_additive_capacity():
    frame, people = sample()
    fitting = frame.loc[frame.user_id != 7]
    model = AuditClassifier('traditional_pca3', whiten=True).fit(fitting, people)
    unique = fitting.drop_duplicates('user_id')
    np.testing.assert_allclose(model.geometry(unique, people).var(axis=0, ddof=1), 1.)
    additive = AuditClassifier('traditional_direct', interactions=False).fit(fitting, people)
    full = AuditClassifier('traditional_direct').fit(fitting, people)
    assert additive.classifier.n_features_in_ < full.classifier.n_features_in_
