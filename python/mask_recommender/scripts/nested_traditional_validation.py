"""Local nested person-held-out selection of traditional model complexity and L2."""
import argparse
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning

from mask_recommender import train
from mask_recommender.scripts.audit_traditional_scaling import AuditClassifier, summarize
from mask_recommender.scripts.compare_direct_measurements import paired_frame

RECIPES = {
    'linear_additive': dict(squared=False, mask_squared=False, interactions=False),
    'linear_interactions': dict(squared=False, mask_squared=False, interactions=True),
    'quadratic_additive': dict(squared=True, mask_squared=True, interactions=False),
    'quadratic_interactions': dict(squared=True, mask_squared=True, interactions=True),
}
GRID = [dict(recipe=name, c=c, **settings) for name, settings in RECIPES.items()
        for c in [.001, .01, .1, 1.]]
OBJECTIVES = ('test_weighted', 'equal_person')


def fit_model(arm, config, frame, people):
    settings = {k: v for k, v in config.items() if k != 'recipe'}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', ConvergenceWarning)
        model = AuditClassifier(arm, **settings).fit(frame, people)
    if any(isinstance(w.message, ConvergenceWarning) for w in caught):
        raise RuntimeError('Nested fit failed convergence check')
    return model


def select(arm, frame, people, grid=GRID):
    scores = []
    for config in grid:
        losses, person_means = [], []
        for user in people.user_id:
            fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
            testing = frame.loc[frame.user_id == user].reset_index(drop=True)
            training_people = people.loc[people.user_id != user]
            model = fit_model(arm, config, fitting, training_people)
            assert user not in model.training_people
            p = model.predict(testing, people)
            _, p, y = train._dedupe_prediction_rows(testing, p, testing.qlft_pass_normalized.to_numpy())
            loss = -np.log(np.clip(np.where(y == 1, p, 1-p), 1e-15, 1-1e-15))
            losses.extend(loss.tolist())
            person_means.append(float(loss.mean()))
        scores.append(dict(config=config, test_weighted=float(np.mean(losses)),
                           equal_person=float(np.mean(person_means))))
    # Grid order breaks exact ties deterministically: simpler recipe, smaller C.
    return {objective: min(scores, key=lambda r: r[objective]) for objective in OBJECTIVES}, scores


def evaluate(frame, people, grid=GRID):
    results, private = [], {}
    for arm in ['traditional_direct', 'traditional_pca3']:
        rows = {objective: [] for objective in OBJECTIVES}
        folds = {objective: [] for objective in OBJECTIVES}
        for fold, user in enumerate(people.user_id, 1):
            fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
            testing = frame.loc[frame.user_id == user].reset_index(drop=True)
            training_people = people.loc[people.user_id != user]
            selected, scores = select(arm, fitting, training_people, grid)
            for objective in OBJECTIVES:
                chosen = selected[objective]
                model = fit_model(arm, chosen['config'], fitting, training_people)
                assert user not in model.training_people
                p = model.predict(testing, people)
                deduped, p, y = train._dedupe_prediction_rows(testing, p, testing.qlft_pass_normalized.to_numpy())
                for (_, row), probability, label in zip(deduped.iterrows(), p, y):
                    identity = row.get('source_fit_test_id', row.get('id'))
                    if pd.isna(identity):
                        identity = row.get('id')
                    rows[objective].append(dict(fold=fold, user_id=int(user), mask_id=int(row.mask_id),
                                                fit_test_id=int(identity), label=int(label), probability=float(probability),
                                                training_positive_rate=float(fitting.qlft_pass_normalized.mean())))
                pred = p >= .5
                folds[objective].append(dict(fold=fold, selected=chosen['config'],
                    inner_log_loss=chosen[objective], inner_grid_scores=scores,
                    outer_tests=len(y), outer_positive_labels=int(y.sum()),
                    outer_true_positives=int(((y == 1) & pred).sum()),
                    outer_false_positives=int(((y == 0) & pred).sum()),
                    design_columns=model.classifier.n_features_in_))
                print(arm, 'outer fold', fold, objective, chosen['config']['recipe'],
                      'C', chosen['config']['c'], flush=True)
        for objective in OBJECTIVES:
            results.append(dict(arm=arm, selection_objective=objective, folds=folds[objective],
                                metrics=summarize(rows[objective])))
            private[arm+'/'+objective] = rows[objective]
    return results, private


def linear_results(frame, people, all_results):
    """Reuse training-only inner scores; restrict choice without inspecting outer labels."""
    results, private = [], {}
    for reference in all_results:
        arm, objective = reference['arm'], reference['selection_objective']
        rows, folds = [], []
        for fold, user in enumerate(people.user_id, 1):
            fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
            testing = frame.loc[frame.user_id == user].reset_index(drop=True)
            scores = reference['folds'][fold-1]['inner_grid_scores']
            linear = [s for s in scores if not s['config']['squared'] and not s['config']['mask_squared']]
            chosen = min(linear, key=lambda s: s[objective])
            model = fit_model(arm, chosen['config'], fitting, people.loc[people.user_id != user])
            assert user not in model.training_people
            p = model.predict(testing, people)
            deduped, p, y = train._dedupe_prediction_rows(testing, p, testing.qlft_pass_normalized.to_numpy())
            for (_, row), probability, label in zip(deduped.iterrows(), p, y):
                identity = row.get('source_fit_test_id', row.get('id'))
                if pd.isna(identity):
                    identity = row.get('id')
                rows.append(dict(fold=fold, user_id=int(user), mask_id=int(row.mask_id),
                                 fit_test_id=int(identity), label=int(label), probability=float(probability),
                                 training_positive_rate=float(fitting.qlft_pass_normalized.mean())))
            pred = p >= .5
            folds.append(dict(fold=fold, selected=chosen['config'], inner_log_loss=chosen[objective],
                              outer_tests=len(y), outer_positive_labels=int(y.sum()),
                              outer_true_positives=int(((y == 1) & pred).sum()),
                              outer_false_positives=int(((y == 0) & pred).sum()),
                              design_columns=model.classifier.n_features_in_))
        results.append(dict(arm=arm, candidate_family='no_squares', selection_objective=objective,
                            folds=folds, metrics=summarize(rows)))
        private[arm+'/no_squares/'+objective] = rows
    return results, private


def run(frame_path, summary_path, out, reuse_inner=None):
    frame, people = paired_frame(pd.read_json(frame_path, orient='table'),
                                 json.loads(summary_path.read_text())['facial_measurements'])
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in [('frame', frame_path), ('summary', summary_path)]}
    classifier_hash = hashlib.sha256(Path(__file__).with_name('audit_traditional_scaling.py').read_bytes()).hexdigest()
    if reuse_inner:
        cached = json.loads(reuse_inner.read_text())
        assert cached['source_hashes'] == hashes and cached['grid'] == GRID
        assert cached['classifier_sha256'] == classifier_hash
        results = [r for r in cached['results'] if r.get('candidate_family', 'all_recipes') == 'all_recipes']
        assert len(results) == 4 and all(len(r['folds']) == len(people) for r in results)
        private = json.loads(reuse_inner.with_name('private_predictions.json').read_text())
    else:
        results, private = evaluate(frame, people)
    for result in results:
        result['candidate_family'] = 'all_recipes'
    linear, linear_private = linear_results(frame, people, results)
    results.extend(linear)
    private.update(linear_private)
    report = dict(people=len(people), tests=len(frame), results=results, grid=GRID,
                  method='Outer leave-one-person-out: train six/test one. Inner leave-one-person-out within the six: train five/validate one. Select minimum inner pooled log loss, then refit on six.',
                  selection_objectives=list(OBJECTIVES), training_weighting='Equal total sample weight per training person, matching the original traditional models.',
                  preprocessing='Z-score face dimensions on unique training people; PCA-3 and mask preprocessing refit in every inner/outer training fold. No PCA whitening.',
                  threshold=.5, threshold_tuned=False,
                  squared_definition='No-square recipes remove both face/PC squares and mask-perimeter square. Linear-interaction recipes still contain bilinear geometry-by-mask products.',
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  classifier_sha256=classifier_hash, source_hashes=hashes,
                  reused_inner_report_sha256=hashlib.sha256(reuse_inner.read_bytes()).hexdigest() if reuse_inner else None,
                  limitations=['Only seven independent people; only five train each inner fit.',
                               'Nested validation prevents outer-person tuning, but grid construction follows earlier exploratory analysis of this same cohort; new-person confirmation is needed.',
                               'Selection minimizes log loss, not precision, recall or F1; threshold stays fixed.',
                               'Both selection objectives reported, rather than choosing the winner on outer outcomes.',
                               'Production ARKit differs in architecture/training weights; original slide results remain unchanged.'])
    out.mkdir(parents=True, exist_ok=True)
    (out/'nested-validation.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    (out/'private_predictions.json').write_text(json.dumps(private, allow_nan=False)+'\n')
    for result in results:
        print(result['arm'], result['candidate_family'], result['selection_objective'], json.dumps(result['metrics']), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-inner', type=Path, help='Reuse completed inner-grid scores with identical input hashes, classifier and grid.')
    args = parser.parse_args()
    run(args.frame, args.summary, args.output, args.reuse_inner)
