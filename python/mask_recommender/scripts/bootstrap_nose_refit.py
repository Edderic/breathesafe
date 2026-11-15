"""Paired participant bootstrap with independent, batched production-model refits.

Fixed original five person-grouped folds, category catalog and prepared inputs.
Batching shares computation only: parameters, Adam states and losses are independent.
No network, deployment, or public participant-level output.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time

import numpy as np
import pandas as pd
import torch

from mask_recommender import train

METRICS = ('precision', 'recall', 'negative_predictive_value', 'f1', 'log_loss')
VARIANTS = ('none', 'latent_nose_v1')
SEEDS = (42, 43, 44)
STATE = {}


def metrics(totals):
    tp, fp, tn, fn, loss, count = np.moveaxis(totals, -1, 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.stack((tp/(tp+fp), tp/(tp+fn), tn/(tn+fn),
                         2*tp/(2*tp+fp+fn), loss/count), axis=-1)


def initialize(frame_path):
    torch.set_num_threads(1)
    frame = pd.read_json(frame_path, orient='table')
    metadata = train._custom_lr_category_metadata(frame)
    users = sorted(frame.user_id.unique())
    positions = {u: i for i, u in enumerate(users)}
    indices = frame.user_id.map(positions).to_numpy(dtype=int)
    data = train.prep_data_in_torch_with_categories(frame,
        metadata['fit_family_categories'], metadata['style_categories'], metadata['strap_type_categories'])
    STATE.update(frame=frame, metadata=metadata, users=users, indices=indices, data=data,
                 folds=train._group_k_fold_indices_by_user(frame),
                 y=torch.tensor(frame.qlft_pass_normalized.to_numpy(dtype=np.float32)))


def independent_parameters(metadata, variant, seed, count):
    metadata = dict(metadata, nose_model=variant)
    torch.manual_seed(seed)
    return {k: v.detach().unsqueeze(0).repeat(count, *([1]*v.ndim)).requires_grad_()
            for k, v in train._initialize_custom_lr_parameters(metadata).items()}


def batched_probs(data, params):
    """Gather categorical rows; algebraically the production one-hot products."""
    mask = data['fit_tests_by_masks'].argmax(dim=1)
    style = data['fit_tests_by_styles'].argmax(dim=1)
    strap = data['fit_tests_by_strap_types'].argmax(dim=1)
    coefficients = torch.cat((-params['alpha_mask_raw'].exp(), params['beta_gamma_mask']), dim=2)[:, mask]
    coefficients = coefficients + torch.cat((-params['alpha_style_raw'].exp(), params['beta_gamma_style']), dim=2)[:, style]
    logits = (coefficients * data['perimeter_diffs'][None]).sum(dim=2)
    logits = logits + params['strap_specific_parameters'][:, strap, 0]
    if 'nose_center_log_cm' in params:
        center = (params['nose_center_log_cm'] + params['nose_mask_offset'][:, mask] +
                  params['nose_style_offset'][:, style]).exp().squeeze(2)
        strength = torch.nn.functional.softplus(params['nose_strength_raw']).squeeze(2)
        logits = logits-strength*(data['nose_cm'][:, 0][None]-center).square()
    return logits.sigmoid()


def refit(data, y, weights, metadata, variant, seed, epochs=200):
    params = independent_parameters(metadata, variant, seed, len(weights))
    optimizer = torch.optim.Adam(list(params.values()), lr=.01)
    weights = torch.as_tensor(weights, dtype=torch.float32)
    denominator = weights.sum(dim=1)
    if not (denominator > 0).all():
        raise ValueError('Empty bootstrap training fold')
    for _ in range(epochs):
        optimizer.zero_grad()
        probabilities = batched_probs(data, params)
        losses = torch.nn.functional.binary_cross_entropy(probabilities, y[None].expand_as(probabilities), reduction='none')
        objective = (losses*weights).sum(dim=1)/denominator
        if variant != 'none':
            objective = objective+.01*(params['nose_mask_offset'].square().mean(dim=(1, 2))+
                                       params['nose_style_offset'].square().mean(dim=(1, 2)))
        # Sum independent objectives, never average over the batch: unchanged Adam epsilon.
        objective.sum().backward()
        optimizer.step()
    return params


def stats(y, probabilities, weights):
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(y, dtype=float)[None]
    positive = p >= .5
    return np.stack([(((y == 1) & positive)*weights).sum(axis=1),
                     (((y == 0) & positive)*weights).sum(axis=1),
                     (((y == 0) & ~positive)*weights).sum(axis=1),
                     (((y == 1) & ~positive)*weights).sum(axis=1),
                     (-np.log(np.clip(np.where(y == 1, p, 1-p), 1e-15, 1-1e-15))*weights).sum(axis=1),
                     weights.sum(axis=1)], axis=-1)


def compute(weights, epochs=200):
    data, metadata, indices, y = (STATE[k] for k in ('data', 'metadata', 'indices', 'y'))
    total = np.zeros((len(weights), 2, 3, 6))
    for fold, (training, testing) in enumerate(STATE['folds'], 1):
        training, testing = training.numpy(), testing.numpy()
        train_data = {k: v[training] for k, v in data.items()}
        test_data = {k: v[testing] for k, v in data.items()}
        # All observations and sampled copies of one original person stay together.
        assert not set(indices[training]) & set(indices[testing])
        training_weights = weights[:, indices[training]]
        test_weights = weights[:, indices[testing]]
        for v, variant in enumerate(VARIANTS):
            for s, seed in enumerate(SEEDS):
                params = refit(train_data, y[training], training_weights, metadata, variant, seed+fold, epochs)
                with torch.no_grad():
                    p = batched_probs(test_data, params).numpy()
                total[:, v, s] += stats(y[testing].numpy(), p, test_weights)
    return metrics(total).mean(axis=2)


def task(spec):
    path, weights, epochs = spec
    result = compute(weights, epochs)
    np.save(path, result)
    return len(weights)


def summarize(draws, points):
    result = dict(variants={}, differences={}, superiority={})
    for m, name in enumerate(METRICS):
        values = draws[:, :, m]
        valid = np.isfinite(values).all(axis=1)
        values = values[valid]
        if not len(values):
            raise ValueError('No valid paired draws for '+name)
        for v, variant in enumerate(VARIANTS):
            lo, hi = np.quantile(values[:, v], [.025, .975])
            result['variants'].setdefault(variant, {})[name] = dict(
                estimate=float(points[v, m]), low=float(lo), high=float(hi), valid_replicates=int(valid.sum()))
        delta = values[:, 1]-values[:, 0]
        lo, hi = np.quantile(delta, [.025, .975])
        result['differences'][name] = dict(estimate=float(points[1, m]-points[0, m]), low=float(lo), high=float(hi), valid_replicates=len(delta))
        ties = np.isclose(delta, 0, rtol=0, atol=1e-12)
        wins = ((delta < 0) if name == 'log_loss' else (delta > 0)) & ~ties
        result['superiority'][name] = dict(better_replicates=int(wins.sum()), tied_replicates=int(ties.sum()),
            worse_replicates=int((~wins & ~ties).sum()), valid_replicates=len(delta),
            undefined_replicates=int((~valid).sum()), better_frequency=float(wins.mean()))
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(args):
    started = time.monotonic()
    initialize(args.frame)
    assert len(STATE['users']) == 49 and len(STATE['frame']) == 1086
    source_hashes = dict(frame=digest(args.frame), trainer=digest(train.__file__), bootstrap=digest(__file__))
    signature = hashlib.sha256(json.dumps(dict(hashes=source_hashes, seed=args.seed, epochs=args.epochs,
        replicates=args.replicates, batch=args.batch), sort_keys=True).encode()).hexdigest()
    directory = args.output/signature[:16]
    directory.mkdir(parents=True, exist_ok=True)
    weights = np.random.default_rng(args.seed).multinomial(49, np.full(49, 1/49), size=args.replicates)
    point_path = directory/'point.npy'
    if not point_path.exists():
        np.save(point_path, compute(np.ones((1, 49), dtype=int), args.epochs)[0])
    points = np.load(point_path)
    paths, pending = [], []
    for offset in range(0, args.replicates, args.batch):
        path = directory/f'{offset:05d}.npy'
        paths.append(path)
        if not path.exists():
            pending.append((path, weights[offset:offset+args.batch], args.epochs))
    print(json.dumps(dict(replicates=args.replicates, independent_model_fits=args.replicates*30,
                         pending_batches=len(pending), workers=args.workers)), flush=True)
    completed = 0
    with mp.get_context('spawn').Pool(args.workers, initializer=initialize, initargs=(args.frame,)) as pool:
        for count in pool.imap_unordered(task, pending):
            completed += count
            print(f'Refitted {completed} pending draws; elapsed {time.monotonic()-started:.1f}s', flush=True)
    draws = np.concatenate([np.load(path) for path in paths])
    result = dict(method='Paired person-cluster percentile bootstrap with independent model retraining in every resample',
        people=49, tests=1086, replicates=args.replicates, random_seed=args.seed,
        confidence_level=.95, quantiles=[.025, .975], quantile_method='linear',
        initializations=list(SEEDS), threshold=.5, log_loss_epsilon=1e-15,
        epochs=args.epochs, learning_rate=.01, optimizer='Adam', class_weighting=False,
        independent_bootstrap_model_fits=args.replicates*30, point_model_fits=30,
        sampling='Draw 49 people with replacement. Copies of each person remain in their original held-out fold; multiplicities weight training BCE and held-out metrics. Same draws for both models and all seeds.',
        estimand='Test-weighted pooled held-out metric per initialization, then mean of seeds 42/43/44; no probability ensembling.',
        source_hashes=source_hashes, elapsed_seconds=time.monotonic()-started,
        difference_definition='Nose model minus perimeter-only model; negative log-loss difference is favorable.',
        superiority_definition='Strict paired wins, ties within absolute 1e-12 reported separately; bootstrap frequencies are not posterior probabilities or p-values.',
        limitations=[
            'Prepared mixed measured/imputed facial inputs remain frozen; the inherited pre-CV imputation regression is not refitted. This is full classifier retraining, not end-to-end imputation refitting.',
            'Original five person-grouped fold assignments and category catalog remain fixed. Training participant multiplicities vary; fold-selection variability is not included.',
            'Fixed architecture, epochs, learning rate, threshold and initialization bank; no hyperparameter selection.',
            'Convenience sampling, mixed outcome sources, repeated person-mask observations and overlapping CV training sets remain limitations.',
            'People are resampled; mask families are not independently resampled. Pointwise percentile intervals have no multiplicity adjustment.',
        ], **summarize(draws, points))
    (args.output/'report.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result['superiority'], indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--replicates', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=20261114)
    parser.add_argument('--epochs', type=int, default=200)
    parser.add_argument('--batch', type=int, default=64)
    parser.add_argument('--workers', type=int, default=4)
    main(parser.parse_args())
