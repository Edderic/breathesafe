"""Aggregate held-out fit scores without exposing participant-level predictions.

The threshold sweep is exploratory: maximizing F1 on the reported observations
is not independent validation of that threshold. Fixed-threshold metrics remain
separate. Each input row is a deduplicated tested observation, not an untested mask.
"""
import math
from collections import Counter
from statistics import fmean

VERSION = 'held_out_probability_evaluation_v1'
EPSILON = 1e-15


def _validated(labels, probabilities):
    labels, probabilities = list(labels), [float(p) for p in probabilities]
    if len(labels) != len(probabilities):
        raise ValueError('Labels and scores must have the same length')
    if any(y not in (0, 1) for y in labels):
        raise ValueError('Labels must be binary, with unknown outcomes excluded')
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities):
        raise ValueError('Scores must be finite probabilities in [0, 1]')
    return [int(y) for y in labels], probabilities


def _ratio(a, b):
    return a / b if b else None


def threshold_metrics(labels, probabilities, threshold=0.5, weights=None):
    labels, probabilities = _validated(labels, probabilities)
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError('Threshold must be between zero and one')
    weights = [1] * len(labels) if weights is None else list(weights)
    if len(weights) != len(labels) or any(not math.isfinite(w) or w <= 0 for w in weights):
        raise ValueError('Weights must be finite, positive and aligned with labels')
    tp = fp = tn = fn = 0
    for y, p, weight in zip(labels, probabilities, weights):
        if p >= threshold:
            if y: tp += weight
            else: fp += weight
        elif y: fn += weight
        else: tn += weight
    return {'threshold': float(threshold), 'sample_count': len(labels),
            'true_positive': tp, 'false_positive': fp, 'true_negative': tn, 'false_negative': fn,
            'precision': _ratio(tp, tp + fp), 'recall': _ratio(tp, tp + fn),
            'specificity': _ratio(tn, tn + fp), 'f1': _ratio(2 * tp, 2 * tp + fp + fn),
            'predicted_positive_count': tp + fp}


def probability_quality(labels, probabilities, weights=None):
    labels, probabilities = _validated(labels, probabilities)
    weights = [1] * len(labels) if weights is None else list(weights)
    if len(weights) != len(labels) or any(not math.isfinite(w) or w <= 0 for w in weights):
        raise ValueError('Weights must be finite, positive and aligned with labels')
    denominator = sum(weights)
    if not labels:
        return {'sample_count': 0, 'log_loss': None, 'brier_score': None,
                'positive_rate': None, 'mean_predicted_probability': None}
    losses = [-math.log(max(EPSILON, min(1 - EPSILON, p if y else 1 - p)))
              for y, p in zip(labels, probabilities)]
    return {'sample_count': len(labels),
            'log_loss': sum(w * loss for w, loss in zip(weights, losses)) / denominator,
            'brier_score': sum(w * (p - y) ** 2 for w, p, y in zip(weights, probabilities, labels)) / denominator,
            'positive_rate': sum(w * y for w, y in zip(weights, labels)) / denominator,
            'mean_predicted_probability': sum(w * p for w, p in zip(weights, probabilities)) / denominator}


def _quantile(values, fraction):
    ordered = sorted(values)
    if not ordered: return None
    position = (len(ordered) - 1) * fraction
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def _score_summary(values):
    return {'sample_count': len(values), 'mean': fmean(values) if values else None,
            'median': _quantile(values, .5), 'p10': _quantile(values, .1), 'p90': _quantile(values, .9)}


def evaluate_probabilities(labels, probabilities, user_ids=None, baseline_probabilities=None):
    labels, probabilities = _validated(labels, probabilities)
    if user_ids is not None and len(user_ids) != len(labels):
        raise ValueError('User groups must align with labels')
    if user_ids is not None and any(u is None for u in user_ids):
        raise ValueError('User groups cannot be missing')
    baseline = None
    if baseline_probabilities is not None:
        baseline = probability_quality(labels, baseline_probabilities)
    curve = [threshold_metrics(labels, probabilities, i / 100) for i in range(101)]
    # Prefer a balanced precision/recall tie, then the higher threshold. No test
    # outcome can affect model fitting here, but it does affect this exploratory choice.
    best = None
    if len(set(labels)) == 2:
        best = max(curve, key=lambda r: (r['f1'] or 0,
                   -abs((r['precision'] or 0) - (r['recall'] or 0)), r['threshold']))
    passing = [p for y, p in zip(labels, probabilities) if y]
    failing = [p for y, p in zip(labels, probabilities) if not y]
    histogram, calibration = [], []
    for i in range(10):
        ids = [j for j, p in enumerate(probabilities) if min(int(p * 10), 9) == i]
        positive = sum(labels[j] for j in ids)
        negative = len(ids) - positive
        histogram.append({'bin_start': i / 10, 'bin_end': (i + 1) / 10,
                          'pass_count': positive, 'fail_count': negative,
                          'pass_fraction': _ratio(positive, len(passing)),
                          'fail_fraction': _ratio(negative, len(failing))})
        calibration.append({'bin_start': i / 10, 'bin_end': (i + 1) / 10,
                            'sample_count': len(ids),
                            'mean_predicted_probability': fmean(probabilities[j] for j in ids) if ids else None,
                            'observed_positive_rate': _ratio(positive, len(ids))})
    user_equal = None
    if user_ids is not None and labels:
        counts = Counter(user_ids)
        weights = [1 / counts[user] for user in user_ids]
        user_equal = {'quality': probability_quality(labels, probabilities, weights),
                      'at_0_5': threshold_metrics(labels, probabilities, .5, weights)}
    return {'version': VERSION, 'available': bool(labels), 'sample_count': len(labels),
            'user_count': len(set(user_ids)) if user_ids is not None else None,
            'positive_count': len(passing), 'negative_count': len(failing),
            'observation_unit': 'deduplicated tested observation; repeated user-mask tests can remain',
            'prediction_source': 'grouped-user held-out predictions; not final-model training-set predictions',
            'quality': probability_quality(labels, probabilities),
            'training_prevalence_baseline': baseline,
            'at_0_5': curve[50], 'threshold_curve': curve,
            'exploratory_f1': best,
            'threshold_selection': 'maximum F1 on these evaluation observations; exploratory, not independently validated',
            'outcome_scores': {'pass': _score_summary(passing), 'fail': _score_summary(failing)},
            'score_histogram': histogram, 'calibration_bins': calibration, 'user_equal': user_equal,
            'limitations': ['Observed labels mix evidence sources; a positive label is not always a direct formal fit-test pass.',
                           'Repeated tests and uneven participant representation affect row-weighted metrics.',
                           'Preprocessing and imputation are inherited from the training pipeline; grouping model fits alone does not validate the entire pipeline.',
                           'Scores are model outputs; calibration must be checked before treating them as individual success probabilities.']}
