"""Paired person-cluster bootstrap of frozen OOF scores; no training or network."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

METRICS = ('precision', 'recall', 'negative_predictive_value', 'f1', 'log_loss')
VARIANTS = ('none', 'latent_nose_v1')


def metrics(totals):
    """Last axis: TP, FP, TN, FN, summed log loss, test count."""
    tp, fp, tn, fn, loss, count = np.moveaxis(totals, -1, 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.stack((tp/(tp+fp), tp/(tp+fn), tn/(tn+fn),
                         2*tp/(2*tp+fp+fn), loss/count), axis=-1)


def sufficient(rows, users):
    result = np.zeros((len(users), 6))
    positions = {user: i for i, user in enumerate(users)}
    for row in rows:
        y, p = row['label'], row['probability']
        if y not in (0, 1) or not np.isfinite(p) or not 0 <= p <= 1:
            raise ValueError('Invalid label or score')
        positive = p >= .5
        cell = (0 if positive else 3) if y else (1 if positive else 2)
        index = positions[row['user_id']]
        result[index, cell] += 1
        result[index, 4] -= np.log(np.clip(p if y else 1-p, 1e-15, 1-1e-15))
        result[index, 5] += 1
    return result


def resample(stats, replicates=10000, seed=20261114):
    """Same participant multiplicities for all model/initialization pairs."""
    rng = np.random.default_rng(seed)
    n = stats.shape[-2]
    weights = rng.multinomial(n, np.full(n, 1/n), size=replicates)
    totals = np.einsum('bu,vsuc->bvsc', weights, stats)
    # Mean of per-initialization ratios, not predictions pooled across seeds.
    return metrics(totals).mean(axis=2)


def interval(values, estimate):
    valid = np.isfinite(values)
    if valid.sum() < .99*len(values):
        raise ValueError('Too many undefined bootstrap statistics')
    low, high = np.quantile(values[valid], [.025, .975], method='linear')
    return dict(estimate=float(estimate), low=float(low), high=float(high),
                valid_replicates=int(valid.sum()))


def superiority(values, lower_is_better=False):
    """Strict directional wins; exact ties and undefined replicates stay explicit."""
    valid = values[np.isfinite(values)]
    if not len(valid):
        raise ValueError('No valid paired differences')
    wins = int(np.count_nonzero(valid < 0 if lower_is_better else valid > 0))
    ties = int(np.count_nonzero(valid == 0))
    return dict(better_replicates=wins, tied_replicates=ties,
                worse_replicates=len(valid)-wins-ties,
                valid_replicates=len(valid), undefined_replicates=len(values)-len(valid),
                better_frequency=wins/len(valid))


def run(source, evidence_path, output, replicates=10000, seed=20261114):
    evidence = json.loads(evidence_path.read_text())
    files, stats, canonical = [], [], None
    users = None
    for variant in VARIANTS:
        seeds = []
        for initialization in evidence['seeds']:
            folder = source/f'seed-{initialization}'
            report = folder/'comparison.json'
            expected = next(r['sha256'] for r in evidence['source_report_hashes']
                            if r['seed'] == initialization)
            assert hashlib.sha256(report.read_bytes()).hexdigest() == expected
            path = folder/variant/'out_of_fold_predictions.json'
            rows = json.loads(path.read_text())
            # Fold assignment may vary between initializations; pair actual tests.
            rows.sort(key=lambda r: (r['user_id'], r['fit_test_id'], r['mask_id']))
            keys = [(r['user_id'], r['fit_test_id'], r['mask_id'], r['label']) for r in rows]
            assert len(set(keys)) == len(keys), 'Duplicate OOF test identity'
            if canonical is None:
                canonical = keys
                users = sorted({r['user_id'] for r in rows})
            assert keys == canonical, 'Unpaired OOF observations'
            assert all(len({r['fold'] for r in rows if r['user_id'] == u}) == 1 for u in users)
            seeds.append(sufficient(rows, users))
            files.append(dict(variant=variant, initialization=initialization,
                              sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        stats.append(seeds)
    stats = np.asarray(stats)
    assert len(users) == evidence['population']['people'] == 49
    assert len(canonical) == evidence['population']['tests'] == 1086
    estimates = metrics(stats.sum(axis=2)).mean(axis=1)
    for v, variant in enumerate(VARIANTS):
        for m, metric in enumerate(METRICS):
            assert np.isclose(estimates[v, m], evidence['variants'][variant][metric], atol=1e-12)
    draws = resample(stats, replicates, seed)
    result = dict(
        method='Paired person-cluster percentile bootstrap of fixed held-out predictions',
        people=len(users), tests=len(canonical), replicates=replicates, random_seed=seed,
        confidence_level=.95, quantiles=[.025, .975], quantile_method='linear',
        sampling='Draw 49 people with replacement; retain every test for each selected person, including multiplicity. Same draw for both models and all initializations.',
        estimand='Test-weighted pooled held-out metric per initialization, then arithmetic mean over seeds 42/43/44; no averaging probabilities first.',
        threshold=.5, log_loss_epsilon=1e-15,
        initializations=evidence['seeds'], source_prediction_hashes=files,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitations=[
            'Conditional on saved trained models, folds and preprocessing; models are not retrained in bootstrap samples.',
            'Cross-validation training sets overlap; intervals are not full-pipeline generalization intervals.',
            'Global pre-CV imputation, convenience sampling and mixed outcome sources remain limitations.',
            'Participants are the resampling unit; masks are held as observed, not resampled as a second clustering dimension.',
            'Pointwise 95% percentile intervals, without multiplicity adjustment across metrics.',
            'Undefined ratio replicates are excluded per metric and their valid counts reported; any nonfinite seed makes that replicate undefined.',
        ], variants={}, differences={})
    for v, variant in enumerate(VARIANTS):
        result['variants'][variant] = {metric: interval(draws[:, v, m], estimates[v, m])
                                       for m, metric in enumerate(METRICS)}
    result['difference_definition'] = 'Nose model minus perimeter-only model; negative log-loss difference is favorable.'
    result['differences'] = {metric: interval(draws[:, 1, m]-draws[:, 0, m], estimates[1, m]-estimates[0, m])
                             for m, metric in enumerate(METRICS)}
    result['superiority_definition'] = ('Strictly better in a paired bootstrap sample: higher precision/recall/NPV/F1 or lower log loss. '
                                       'Frequency = better / valid paired replicates; ties count as neither wins nor losses. '
                                       'Bootstrap frequency is not a Bayesian probability of population superiority or a calibrated p-value.')
    result['superiority'] = {metric: superiority(draws[:, 1, m]-draws[:, 0, m], metric == 'log_loss')
                            for m, metric in enumerate(METRICS)}
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result['superiority'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--evidence', type=Path, default=Path('prompts/2026-11-17-nasem/recommender-evidence.json'))
    parser.add_argument('--output', type=Path, default=Path('prompts/2026-11-17-nasem/recommender-fixed-prediction-bootstrap-evidence.json'))
    args = parser.parse_args()
    run(args.source, args.evidence, args.output)
