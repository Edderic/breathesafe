"""Full-refit paired cluster bootstrap, with deterministic fit caching and no uploads.

Copies of one original person are never split across training/test. Fixed PCA-3
requires four distinct training faces; report insufficient-rank draws explicitly.
"""
import argparse
from collections import Counter
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
import torch

from mask_recommender import train
from mask_recommender.scripts.compare_direct_measurements import paired_frame, FEATURE_COLUMNS
from mask_recommender.scripts.compare_production_measurements import ProductionArkit
from mask_recommender.scripts.fixed_range_models import CONFIG, CONFIG_PATH, FixedRangeClassifier

ARMS = ('production_arkit', 'traditional_direct', 'traditional_pca3')
METRICS = ('log_loss', 'precision', 'recall', 'negative_predictive_value', 'f1')
SEEDS = (42, 43, 44)
STATE = {}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(frame_path, summary_path):
    frame, people = paired_frame(pd.read_json(frame_path, orient='table'),
                                 json.loads(Path(summary_path).read_text())['facial_measurements'])
    assert len(people) == 7 and len(frame) == 421
    # Validate fixed bounds before evaluating any model outcomes.
    check = FixedRangeClassifier('traditional_direct')
    check.face_scaler.fit(people[FEATURE_COLUMNS].to_numpy(dtype=float))
    check.perimeter_scaler.fit(frame[['mask_perimeter_mm']])
    return frame, people


def initializer(frame_path, summary_path):
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    frame, people = prepare(frame_path, summary_path)
    STATE.update(frame=frame, people=people, users=people.user_id.tolist())


def cloned_training(frame, people, weights):
    """Copy participants, not just rows, so equal-person weights retain multiplicity."""
    users = people.user_id.tolist()
    positions = {user: i for i, user in enumerate(users)}
    frames, persons = [], []
    for copy in range(max(weights)):
        selected = [u for i, u in enumerate(users) if weights[i] > copy]
        rows = frame.loc[frame.user_id.isin(selected)].copy()
        members = people.loc[people.user_id.isin(selected)].copy()
        transform = lambda u: -(positions[u]*10+copy+1)
        rows['user_id'] = rows.user_id.map(transform)
        members['user_id'] = members.user_id.map(transform)
        frames.append(rows)
        persons.append(members)
    return pd.concat(frames, ignore_index=True), pd.concat(persons, ignore_index=True)


def stats(labels, probabilities):
    y, p = np.asarray(labels), np.asarray(probabilities)
    assert np.isin(y, [0, 1]).all() and np.isfinite(p).all() and np.all((p >= 0) & (p <= 1))
    positive = p >= .5
    return np.array([((y == 1) & positive).sum(), ((y == 0) & positive).sum(),
                     ((y == 0) & ~positive).sum(), ((y == 1) & ~positive).sum(),
                     -np.log(np.clip(np.where(y == 1, p, 1-p), 1e-15, 1-1e-15)).sum(), len(y)], dtype=float)


def metric_values(totals):
    tp, fp, tn, fn, loss, count = np.moveaxis(totals, -1, 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.stack([loss/count, tp/(tp+fp), tp/(tp+fn), tn/(tn+fn), 2*tp/(2*tp+fp+fn)], axis=-1)


def fit_task(task):
    held, weights, components = task
    frame, people, users = (STATE[k] for k in ('frame', 'people', 'users'))
    assert weights[held] == 0 and sum(w > 0 for w in weights) >= components+1
    fitting, training_people = cloned_training(frame, people, weights)
    user = users[held]
    assert user not in frame.loc[frame.user_id.isin([users[i] for i, w in enumerate(weights) if w])].user_id.values
    testing = frame.loc[frame.user_id == user].reset_index(drop=True)
    result = np.zeros((3, 3, 6))
    diagnostics = {}
    for arm_index, arm in enumerate(ARMS):
        arm_stats = []
        for seed in SEEDS if arm == 'production_arkit' else (SEEDS[0],):
            model = ProductionArkit(seed+held) if arm == 'production_arkit' else FixedRangeClassifier(arm, components=components)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always', ConvergenceWarning)
                model.fit(fitting, training_people)
            if any(isinstance(w.message, ConvergenceWarning) for w in caught):
                raise RuntimeError('Logistic solver did not converge')
            p = model.predict(testing, people)
            evaluated, p, y = train._dedupe_prediction_rows(testing, p, testing.qlft_pass_normalized.to_numpy())
            assert len(evaluated) == len(testing)
            arm_stats.append(stats(y, p))
            if arm != 'production_arkit':
                x = model.design(testing, people)
                assert x.data.min(initial=0) >= -1e-9 and x.data.max(initial=0) <= 1+1e-9
                diagnostics[arm] = dict(design_columns=model.classifier.n_features_in_, iterations=int(model.classifier.n_iter_[0]))
        result[arm_index] = np.stack(arm_stats if len(arm_stats) == 3 else arm_stats*3)
    return task, dict(stats=result.tolist(), diagnostics=diagnostics)


def tasks_for_draw(draw, people, policy):
    tasks = []
    for held in np.flatnonzero(draw):
        weights = draw.copy()
        weights[held] = 0
        selected = people.loc[np.asarray(weights) > 0, FEATURE_COLUMNS].to_numpy(dtype=float)
        rank = np.linalg.matrix_rank(selected-selected.mean(axis=0)) if len(selected) else 0
        components = 3 if policy == 'fixed' else min(3, rank)
        if rank < components or components == 0:
            return None
        tasks.append((int(held), tuple(int(w) for w in weights), components))
    return tasks


def evaluate_draw(draw, tasks, cache):
    total = np.zeros((2, 3, 3, 6))
    for task in tasks:
        values = np.asarray(cache[task]['stats'])
        copies = draw[task[0]]
        total[0] += copies*values
        total[1] += copies*values/values[..., -1:]
    # Each initialization has its own complete pooled OOF metric before averaging.
    return metric_values(total).mean(axis=2)


def summarize(draw_metrics, points, attempted):
    output = {}
    for weighting_index, weighting in enumerate(('test_weighted', 'equal_person')):
        result = {}
        for m, metric in enumerate(METRICS):
            values = draw_metrics[:, weighting_index, :, m]
            valid = np.isfinite(values).all(axis=1)
            data = values[valid]
            if not len(data):
                raise ValueError('No paired evaluable replicates for '+metric)
            optimum = data.min(axis=1) if metric == 'log_loss' else data.max(axis=1)
            best = np.isclose(data, optimum[:, None], rtol=0, atol=1e-12)
            ties = best.sum(axis=1) > 1
            tie_patterns = Counter('+'.join(np.array(ARMS)[row]) for row in best[ties])
            records = {}
            for a, arm in enumerate(ARMS):
                count = int((best[:, a] & ~ties).sum())
                low, high = np.quantile(data[:, a], [.025, .975], method='linear')
                records[arm] = dict(estimate=float(points[weighting_index, a, m]), low=float(low), high=float(high),
                                   strict_best_count=count, strict_best_fraction=count/len(data),
                                   strict_best_fraction_of_attempts=count/attempted)
            assert sum(r['strict_best_count'] for r in records.values())+int(ties.sum()) == len(data)
            result[metric] = dict(valid_paired_replicates=int(valid.sum()),
                undefined_metric_replicates=int((~valid).sum()), tie_count=int(ties.sum()),
                tie_patterns=dict(tie_patterns), arms=records)
        output[weighting] = result
    return output


def main(args):
    started = time.monotonic()
    frame, people = prepare(args.frame, args.summary)
    rng = np.random.default_rng(args.seed)
    draws = rng.multinomial(7, np.full(7, 1/7), size=args.replicates)
    draw_tasks = [tasks_for_draw(draw, people, args.pca_policy) for draw in draws]
    valid_indices = [i for i, tasks in enumerate(draw_tasks) if tasks is not None]
    point_draw = np.ones(7, dtype=int)
    point_tasks = tasks_for_draw(point_draw, people, args.pca_policy)
    tasks = sorted({t for i in valid_indices for t in draw_tasks[i]} | set(point_tasks))
    sources = dict(frame=digest(args.frame), summary=digest(args.summary), config=digest(CONFIG_PATH),
                   scaler=digest(Path(__file__).with_name('fixed_range_models.py')),
                   trainer=digest(Path(train.__file__)), bootstrap=digest(__file__))
    signature = hashlib.sha256(json.dumps(dict(sources=sources, seeds=SEEDS, policy=args.pca_policy), sort_keys=True).encode()).hexdigest()
    folder = args.output/'fit-cache'/signature[:16]
    folder.mkdir(parents=True, exist_ok=True)
    cache, pending = {}, []
    cache_path = lambda t: folder/(hashlib.sha256(json.dumps(t).encode()).hexdigest()+'.json')
    for task in tasks:
        path = cache_path(task)
        if path.exists():
            cache[task] = json.loads(path.read_text())
        else:
            pending.append(task)
    print(json.dumps(dict(attempted=args.replicates, pca_evaluable=len(valid_indices),
                          unique_fit_tasks=len(tasks), already_cached=len(cache), workers=args.workers)), flush=True)
    if pending:
        with mp.get_context('spawn').Pool(args.workers, initializer=initializer,
                                          initargs=(str(args.frame), str(args.summary))) as pool:
            for task, result in pool.imap_unordered(fit_task, pending, chunksize=1):
                cache_path(task).write_text(json.dumps(result, allow_nan=False))
                cache[task] = result
                if len(cache) % 50 == 0 or len(cache) == len(tasks):
                    print(f'Completed {len(cache)}/{len(tasks)} distinct full-pipeline fits; elapsed {time.monotonic()-started:.0f}s', flush=True)
    points = evaluate_draw(point_draw, point_tasks, cache)
    values = np.stack([evaluate_draw(draws[i], draw_tasks[i], cache) for i in valid_indices])
    report = dict(method='Paired person-cluster bootstrap, full refit of preprocessing and all models inside leave-original-person-out evaluation.',
        attempted_replicates=args.replicates, seed=args.seed, people=7, original_tests=len(frame),
        pca_policy=args.pca_policy, pca_evaluable_replicates=len(valid_indices),
        insufficient_pca_rank_replicates=args.replicates-len(valid_indices),
        participant_support_distribution={str(k): int(v) for k, v in zip(*np.unique((draws > 0).sum(axis=1), return_counts=True))},
        arkit_initializations=list(SEEDS), training_epochs=200, learning_rate=.01,
        unique_training_sets_with_multiplicity=len(tasks), actual_seed_model_fits=len(tasks)*5,
        deterministic_cache='Identical held-person/training-multiplicity/PCA-component inputs reuse exact deterministic fits with the same initialization bank; no reuse of the original fixed OOF predictions.',
        folds='All copies of the same original participant stay in one held-out group. Bootstrap multiplicities affect training rows, PCA people, equal-person weights, and evaluation contributions.',
        ranges=CONFIG, sources=sources, elapsed_seconds=time.monotonic()-started,
        winner_definition='Strict best among all three models for each metric; lower log loss / higher other metrics. Ties within absolute 1e-12 are reported separately; undefined model metrics exclude that paired replicate for the metric.',
        limitations=['Seven original participants; resampling cannot supply missing child/large-face variation.',
                     'Fixed PCA-3 results condition on enough distinct training faces; excluded draws and metric-specific denominators are reported.',
                     'Ranges are provisional engineering assumptions, not validated anthropometric population limits; fixed C=1 is not retuned.',
                     'Full pipeline here includes scaling, PCA and classifier fitting with fixed recipe; no nested hyperparameter or threshold selection is performed.',
                     'Traditional models retain equal-person training weights; ARKit retains original row-weighted loss. This does not isolate modality causally.',
                     'Bootstrap frequencies are not Bayesian posterior probabilities or calibrated p-values.',
                     'The same cohort informed earlier exploratory work; this is not a new confirmatory cohort.'],
        results=summarize(values, points, args.replicates))
    (args.output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(report['results']['test_weighted'], indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replicates', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=20261115)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--pca-policy', choices=['fixed', 'adaptive'], default='fixed')
    main(parser.parse_args())
