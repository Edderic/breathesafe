"""Paired leave-person-out comparison: measured ARKit vs traditional-to-ARKit inputs.

Reads private local snapshots only. Fits the same downstream recommender for both
arms; the traditional conversion is refit without each held-out person. This is
not a direct traditional-feature model or a physical measurement-accuracy study.
"""
import argparse
import hashlib
import json
from html import escape
from pathlib import Path
from statistics import mean

import numpy as np
import pandas as pd
import torch

from mask_recommender import train
from mask_recommender.predict_arkit_from_traditional import (
    FEATURE_COLUMNS, TARGET_COLUMNS, prepare_dataframe, train_model,
)
from mask_recommender.probability_evaluation import evaluate_probabilities


def paired_summary(payload):
    frame = prepare_dataframe(payload, FEATURE_COLUMNS, TARGET_COLUMNS)
    if frame['user_id'].isna().any() or frame['user_id'].duplicated().any():
        raise ValueError('Expected one summary row per known person')
    return frame.dropna(subset=FEATURE_COLUMNS + TARGET_COLUMNS).copy()


def with_measurements(frame, values):
    """Replace face inputs and recompute mismatch while preserving mask geometry."""
    result = frame.copy()
    perimeter = result.apply(train._mask_perimeter_mm_from_training_row, axis=1)
    for column, value in zip(TARGET_COLUMNS, values):
        result[column] = float(value)
    result['perimeter_mm'] = perimeter
    result['perimeter_diff'] = (result[train.FACIAL_MEASUREMENTS].sum(axis=1) - perimeter) / 10
    result['perimeter_diff_sq'] = result['perimeter_diff'].pow(2)
    return result


def score_rows(rows):
    if not rows:
        return None
    frame = pd.DataFrame(rows)
    return {
        'probability_evaluation': evaluate_probabilities(
            frame.label.tolist(), frame.probability.tolist(), user_ids=frame.user_id.tolist(),
            baseline_probabilities=frame.training_positive_rate.tolist()),
        'top_k': train._compute_top_k_hit_rates(frame, frame.label, frame.probability),
    }


def compare(frame, summary, seeds=(42, 43, 44), epochs=200):
    paired = paired_summary(summary)
    measured = frame.loc[frame['nose_mm_observed']].copy()
    paired = paired.loc[paired.user_id.isin(measured.user_id)].sort_values('user_id')
    if len(paired) < 3:
        raise ValueError('Need at least three paired people with test observations')
    audits, runs = [], []
    for seed in seeds:
        arms = {'arkit': [], 'traditional_via_conversion': []}
        excluded = []
        for position, (_, person) in enumerate(paired.iterrows()):
            user = int(person.user_id)
            converter_training = paired_summary(summary)
            converter_training = converter_training.loc[converter_training.user_id != user]
            fitting = measured.loc[measured.user_id != user].reset_index(drop=True)
            testing = measured.loc[measured.user_id == user].reset_index(drop=True)
            assert user not in set(converter_training.user_id) | set(fitting.user_id)
            mapper = train_model(converter_training)
            converted = mapper.predict(person[FEATURE_COLUMNS].to_frame().T)[0]
            actual = person[TARGET_COLUMNS].to_numpy(dtype=float)
            diagnostic = {
                'seed': seed, 'user_id': user, 'conversion_training_people': len(converter_training),
                'recommender_training_people': int(fitting.user_id.nunique()),
                'converted_inputs_valid': bool(np.isfinite(converted).all() and (converted > 0).all()),
                'input_fields_outside_training_range': int(((person[FEATURE_COLUMNS].to_numpy(dtype=float) < converter_training[FEATURE_COLUMNS].min().to_numpy()) | (person[FEATURE_COLUMNS].to_numpy(dtype=float) > converter_training[FEATURE_COLUMNS].max().to_numpy())).sum()),
                'converted_paths_outside_training_range': int(((converted < converter_training[TARGET_COLUMNS].min().to_numpy()) | (converted > converter_training[TARGET_COLUMNS].max().to_numpy())).sum()),
            }
            audits.append(diagnostic)
            if not diagnostic['converted_inputs_valid']:
                excluded.append(user)
                continue
            metadata = train._custom_lr_category_metadata(fitting)
            metadata['nose_model'] = 'latent_nose_v1'
            torch.manual_seed(seed + position)
            index = torch.arange(len(fitting))
            # Validation arguments repeat training only for the legacy trainer's
            # loss logging. No held-out person enters optimization or selection.
            fitted = train.train_custom_lr_with_split(
                fitting, index, index, metadata, epochs=epochs, learning_rate=.01)
            candidate_frames = {'arkit': with_measurements(testing, actual),
                                'traditional_via_conversion': with_measurements(testing, converted)}
            observation_keys = []
            for arm, candidates in candidate_frames.items():
                probabilities = train._predict_custom_lr_probabilities(candidates, fitted['params'], metadata)
                deduped, probabilities, labels = train._dedupe_prediction_rows(
                    candidates, probabilities, candidates.qlft_pass_normalized.to_numpy())
                keys = []
                for (_, row), probability, label in zip(deduped.iterrows(), probabilities, labels):
                    observation = row.get('source_fit_test_id', row.get('id'))
                    if pd.isna(observation): observation = row.get('id')
                    keys.append((int(observation), int(row.mask_id), int(label)))
                    arms[arm].append({
                        'seed': seed, 'user_id': user, 'fit_test_id': int(observation),
                        'mask_id': int(row.mask_id), 'label': int(label), 'probability': float(probability),
                        'training_positive_rate': float(fitting.qlft_pass_normalized.mean()),
                    })
                observation_keys.append(keys)
            assert observation_keys[0] == observation_keys[1]
        runs.append({'seed': seed, 'excluded_people_count': len(excluded),
                     'arms': {arm: score_rows(rows) for arm, rows in arms.items()}})
        for arm, rows in arms.items():
            for row in rows: row['arm'] = arm
            audits.extend(rows)
    counts = measured.loc[measured.user_id.isin(paired.user_id)].groupby('user_id').size().sort_values().tolist()
    conversion = [row for row in audits if 'converted_inputs_valid' in row]
    return {'paired_people_available': len(paired), 'measured_training_people': int(measured.user_id.nunique()),
            'paired_test_counts_per_person_sorted': counts,
            'conversion_person_runs': len(conversion),
            'valid_conversion_person_runs': sum(row['converted_inputs_valid'] for row in conversion),
            'extrapolated_input_person_runs': sum(row['input_fields_outside_training_range'] > 0 for row in conversion),
            'runs': runs}, audits


def write_review(report, output):
    results = []
    for arm in ['arkit', 'traditional_via_conversion']:
        values = [run['arms'][arm] for run in report['runs'] if run['arms'][arm]]
        if not values: continue
        evaluations = [v['probability_evaluation'] for v in values]
        for weighting in ['test_weighted', 'equal_person']:
            fixed = [e['at_0_5'] if weighting == 'test_weighted' else e['user_equal']['at_0_5'] for e in evaluations]
            qualities = [e['quality'] if weighting == 'test_weighted' else e['user_equal']['quality'] for e in evaluations]
            results.append({'arm': arm, 'weighting': weighting,
                'tests': evaluations[0]['sample_count'], 'people': evaluations[0]['user_count'],
                'positive_labels': evaluations[0]['positive_count'],
                'log_loss': mean(q['log_loss'] for q in qualities),
                **{metric: mean(m[metric] for m in fixed) if all(m[metric] is not None for m in fixed) else None
                   for metric in ['precision', 'recall', 'f1', 'negative_predictive_value']},
                **{f'top_{k}': mean(v['top_k']['top_k_hit_rate'][str(k)] for v in values)
                   for k in [1, 3, 5]},
                'top_k_eligible_people': values[0]['top_k']['eligible_users'],
            })
    report['mean_metrics'] = results
    rows = []
    for r in results:
        percent = lambda x: f'{x:.1%}' if x is not None else 'N/A'
        rows.append(f"<tr><td>{escape(r['arm'])}</td><td>{r['weighting']}</td>"
                    f"<td>{percent(r['precision'])}</td><td>{percent(r['recall'])}</td><td>{r['f1']:.3f}</td>"
                    f"<td>{r['log_loss']:.3f}</td><td>{percent(r['top_1'])}</td><td>{percent(r['top_3'])}</td><td>{percent(r['top_5'])}</td></tr>")
    if results:
        first = results[0]
        counts = report.get('paired_test_counts_per_person_sorted', [])
        busy_share = sum(sorted(counts)[-2:]) / sum(counts) if counts else 0
        population = (f"{first['tests']} paired observations from {first['people']} people; "
                      f"only {first['top_k_eligible_people']} positive-label people qualify for top-k. "
                      f"The two busiest people contribute {busy_share:.1%} of tests. Top-k is person-level and identical in both weighting rows.")
    else:
        population = 'No valid paired conversions were available for scoring.'
    text = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<title>Paired measurement-source comparison</title><style>body{font:17px system-ui;max-width:1200px;margin:40px auto;padding:20px;color:#243b46}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}table{border-collapse:collapse}p{line-height:1.5}</style>'
            '<h1>Measured ARKit vs tape/caliper → estimated ARKit</h1>'
            f"<p>{escape(report['method'])}</p><p>Paired people available: {report['paired_people_available']}. "
            'Fixed 50% cutoff. Means over three initializations; top-k is conditional on people with a positive label.</p>'
            f'<p>{escape(population)}</p>'
            '<table><tr><th>Input route</th><th>Weighting</th><th>Precision</th><th>Recall</th><th>F1</th>'
            '<th>Log loss</th><th>Top-1</th><th>Top-3</th><th>Top-5</th></tr>' + ''.join(rows) + '</table><h2>Limits</h2>' +
            ''.join(f'<p>{escape(s)}</p>' for s in report['limitations']) +
            '<p><a href="comparison.json">Full aggregate report</a></p></html>')
    output.mkdir(parents=True, exist_ok=True)
    (output/'comparison.json').write_text(json.dumps(train._json_finite(report), indent=2, allow_nan=False))
    (output/'comparison.html').write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', required=True, type=Path)
    parser.add_argument('--summary', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report, audit = compare(pd.read_json(args.frame, orient='table'), json.loads(args.summary.read_text())['facial_measurements'])
    report.update({
        'method': 'Leave one paired person out of conversion and recommender fitting. Same measured-only ARKit-trained fit model for both input arms. Latest paired summary measurements; 200 Adam epochs, lr .01, no class reweighting. Seeds 42/43/44.',
        'source_hashes': {label: hashlib.sha256(path.read_bytes()).hexdigest() for label,path in [('frame',args.frame),('summary',args.summary)]},
        'limitations': [
            'Only seven complete paired people. Each conversion uses six other paired people for six predictors plus intercept: severely underdetermined linear extrapolation.',
            'This compares the current traditional-to-ARKit conversion route with measured ARKit, not a model trained directly on traditional measurements. It does not establish which physical measurement method is more accurate.',
            'Only people with valid positive converted paths contribute to either paired arm; unavailable conversions are excluded symmetrically and coverage is reported.',
            'Latest traditional and ARKit measurements may come from different dates; fit tests may also precede those measurements.',
            'The same small participant cohort is reused over three initializations; ranges are not confidence intervals. Test-count weighting can be dominated by prolific testers; equal-person metrics are included.',
            'Top-k ranks held-out tested observations for positive-label people, not unseen masks from the full catalog. Repeated user-mask tests may remain. Labels mix evidence sources.',
            'Shared nose fit model is trained only on other people with observed ARKit inputs; this differs from the earlier mixed-input default-model evaluation.',
        ],
    })
    write_review(report,args.output)
    (args.output/'private_audit.json').write_text(json.dumps(train._json_finite(audit),indent=2,allow_nan=False))
    print(args.output/'comparison.html')


if __name__ == '__main__':
    main()
