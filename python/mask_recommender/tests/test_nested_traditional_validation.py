import numpy as np
from scipy import sparse

from mask_recommender.scripts import nested_traditional_validation as nested
from mask_recommender.scripts.audit_traditional_scaling import AuditClassifier
from mask_recommender.tests.test_traditional_scaling_audit import sample


def test_no_square_additive_design_is_actually_linear():
    frame, people = sample()
    fitting = frame.loc[frame.user_id != 7]
    model = AuditClassifier('traditional_direct', squared=False, mask_squared=False,
                            interactions=False).fit(fitting, people)
    expected = sparse.hstack([
        model.categories.transform(model._categories(frame)),
        model.perimeter_scaler.transform(frame[['mask_perimeter_mm']]),
        model.geometry(frame, people),
    ]).toarray()
    np.testing.assert_allclose(model.design(frame, people).toarray(), expected)


def test_nested_fits_exclude_outer_person_and_refit_on_six(monkeypatch):
    frame, people = sample()
    frame['id'] = np.arange(len(frame))
    calls = []
    original = nested.fit_model

    def fit(arm, config, fitting, training_people):
        model = original(arm, config, fitting, training_people)
        calls.append((arm, set(fitting.user_id), set(training_people.user_id), model.pca.n_samples_ if model.pca else None))
        assert set(fitting.user_id) == set(training_people.user_id)
        return model

    monkeypatch.setattr(nested, 'fit_model', fit)
    grid = [nested.GRID[0], nested.GRID[-1]]
    results, private = nested.evaluate(frame, people, grid)
    # Per outer fold: two configs × six inner folds, then two objective refits.
    assert len(calls) == 2*7*14
    for arm_index in range(2):
        for outer in range(7):
            group = calls[(arm_index*7+outer)*14:(arm_index*7+outer+1)*14]
            held_out = outer+1
            for _, training, _, pca_n in group[:12]:
                assert held_out not in training
                assert len(training) == 5
                assert pca_n is None or pca_n == 5
            for _, training, _, pca_n in group[12:]:
                assert training == set(range(1, 8))-{held_out}
                assert pca_n is None or pca_n == 6
    assert len(results) == 4
    keys = [[(r['user_id'], r['fit_test_id'], r['label']) for r in rows] for rows in private.values()]
    assert all(k == keys[0] for k in keys)
    assert len(keys[0]) == len(frame)
    linear, predictions = nested.linear_results(frame, people, results)
    assert len(linear) == 4
    for result in linear:
        assert result['candidate_family'] == 'no_squares'
        assert all(not f['selected']['squared'] and not f['selected']['mask_squared'] for f in result['folds'])
    assert all([(r['user_id'], r['fit_test_id'], r['label']) for r in rows] == keys[0]
               for rows in predictions.values())
