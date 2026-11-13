"""Seven-person comparison with the actual production perimeter-plus-nose architecture.

Retrains production ARKit from scratch within each six-person training fold.
Direct traditional and PCA models are unchanged from compare_direct_measurements.
No deployed weights, conversion into ARKit, external training people or uploads.
"""
import argparse
import hashlib
import json
from html import escape
from pathlib import Path
from statistics import mean

import pandas as pd
import torch

from mask_recommender import train
from mask_recommender.predict_arkit_from_traditional import TARGET_COLUMNS
from mask_recommender.scripts.compare_direct_measurements import FaceMaskClassifier, paired_frame
from mask_recommender.scripts.compare_measurement_sources import score_rows

ARMS = ['production_arkit', 'traditional_direct', 'traditional_pca3']


def arkit_inputs(frame, people):
    result = frame.copy()
    values = people.set_index('user_id').loc[frame.user_id, TARGET_COLUMNS]
    for column in TARGET_COLUMNS:
        result[column] = values[column].to_numpy(dtype=float)
    result['perimeter_mm'] = result['mask_perimeter_mm']
    result['perimeter_diff'] = (result[train.FACIAL_MEASUREMENTS].sum(axis=1) - result['perimeter_mm']) / 10
    result['perimeter_diff_sq'] = result['perimeter_diff'].pow(2)
    return result


class ProductionArkit:
    def __init__(self, seed=42, epochs=200):
        self.seed, self.epochs = seed, epochs

    def fit(self, frame, people):
        self.training_people = set(frame.user_id)
        fitting = arkit_inputs(frame, people)
        self.metadata = train._custom_lr_category_metadata(fitting)
        self.metadata['nose_model'] = 'latent_nose_v1'
        torch.manual_seed(self.seed)
        index = torch.arange(len(fitting))
        fitted = train.train_custom_lr_with_split(
            fitting, index, index, self.metadata,
            epochs=self.epochs, learning_rate=.01, class_weighting=False)
        self.params = fitted['params']
        return self

    def predict(self, frame, people):
        if set(frame.user_id) & self.training_people:
            raise ValueError('Evaluation person overlaps production training people')
        return train._predict_custom_lr_probabilities(arkit_inputs(frame, people), self.params, self.metadata)


def evaluate(frame, summary, seeds=(42, 43, 44), epochs=200):
    frame, people = paired_frame(frame, summary)
    runs, private = [], []
    for seed in seeds:
        arms = {arm: [] for arm in ARMS}
        folds = []
        for fold, user in enumerate(people.user_id, 1):
            fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
            testing = frame.loc[frame.user_id == user].reset_index(drop=True)
            training_people = people.loc[people.user_id != user]
            assert user not in set(training_people.user_id) | set(fitting.user_id)
            keys = []
            record = {'fold': fold, 'training_people': len(training_people), 'test_rows': len(testing), 'arms': {}}
            for arm in ARMS:
                model = (ProductionArkit(seed + fold - 1, epochs=epochs) if arm == 'production_arkit'
                         else FaceMaskClassifier(arm))
                model.fit(fitting, training_people)
                probabilities = model.predict(testing, people)
                deduped, probabilities, labels = train._dedupe_prediction_rows(
                    testing, probabilities, testing.qlft_pass_normalized.to_numpy())
                observations = []
                for (_, row), probability, label in zip(deduped.iterrows(), probabilities, labels):
                    observation = row.get('source_fit_test_id', row.get('id'))
                    if pd.isna(observation): observation = row.get('id')
                    observations.append((int(observation), int(row.mask_id), int(label)))
                    arms[arm].append({'fold': fold, 'user_id': int(user), 'fit_test_id': int(observation),
                        'mask_id': int(row.mask_id), 'label': int(label), 'probability': float(probability),
                        'training_positive_rate': float(fitting.qlft_pass_normalized.mean())})
                keys.append(observations)
                if arm == 'production_arkit':
                    record['arms'][arm] = {'architecture': 'custom_lr + latent_nose_v1',
                        'seed': seed+fold-1, 'epochs': epochs, 'learning_rate': .01,
                        'class_reweight': False, 'person_reweight': False,
                        'nose_parameter_keys': sorted(k for k in model.params if k.startswith('nose_'))}
                else:
                    record['arms'][arm] = {'architecture': 'unchanged L2 logistic face-mask interactions',
                        'C': 1., 'person_reweight': True,
                        'pca_retained_variance': float(model.pca.explained_variance_ratio_.sum()) if model.pca is not None else None}
            assert keys[0] == keys[1] == keys[2]
            folds.append(record)
        runs.append({'seed': seed, 'folds': folds, 'arms': {arm: score_rows(rows) for arm, rows in arms.items()}})
        private.append({'seed': seed, 'arms': arms})
    metrics = []
    for arm in ARMS:
        values = [run['arms'][arm] for run in runs]
        evaluations = [value['probability_evaluation'] for value in values]
        for weighting in ['equal_person', 'test_weighted']:
            fixed = [e['at_0_5'] if weighting == 'test_weighted' else e['user_equal']['at_0_5'] for e in evaluations]
            quality = [e['quality'] if weighting == 'test_weighted' else e['user_equal']['quality'] for e in evaluations]
            metrics.append({'arm': arm, 'weighting': weighting,
                'tests': evaluations[0]['sample_count'], 'people': evaluations[0]['user_count'],
                'log_loss': mean(q['log_loss'] for q in quality),
                **{key: mean(m[key] for m in fixed) if all(m[key] is not None for m in fixed) else None for key in ['precision','recall','f1','negative_predictive_value']},
                **{f'top_{k}': mean(v['top_k']['top_k_hit_rate'][str(k)] for v in values) for k in [1,3,5]},
                'top_k_eligible_people': values[0]['top_k']['eligible_users']})
    return {'paired_people': len(people), 'test_rows': len(frame), 'seeds': list(seeds),
            'test_counts_per_person_sorted': sorted(frame.groupby('user_id').size().tolist()),
            'runs': runs, 'metrics': metrics}, private


def write_review(report, output):
    sections = []
    pct = lambda value: f'{value:.1%}' if value is not None else 'N/A'
    for weighting in ['equal_person', 'test_weighted']:
        rows = []
        for r in report['metrics']:
            if r['weighting'] != weighting: continue
            rows.append('<tr><td>'+escape(r['arm'])+'</td>'+''.join('<td>'+pct(r[key])+'</td>' for key in ['precision','recall'])+
                f"<td>{r['f1']:.3f}</td><td>{r['log_loss']:.3f}</td>"+
                ''.join('<td>'+pct(r[f'top_{k}'])+'</td>' for k in [1,3,5])+'</tr>')
        sections.append('<h2>'+weighting.replace('_',' ').title()+'</h2><table><tr><th>Model</th><th>Precision</th><th>Recall</th><th>F1</th><th>Log loss</th><th>Top-1</th><th>Top-3</th><th>Top-5</th></tr>'+''.join(rows)+'</table>')
    page = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<title>Production ARKit vs traditional and PCA</title><style>body{font:17px system-ui;max-width:1250px;margin:40px auto;padding:20px;color:#243b46}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}table{border-collapse:collapse}p{line-height:1.5}</style>'
            '<h1>Production ARKit architecture vs direct traditional dimensions vs PCA</h1>'
            f"<p>{escape(report['method'])}</p><p>{report['paired_people']} paired people, {report['test_rows']} observations. Fixed 50% cutoff. "
            f"Equal-person metrics are primary. Top-k is conditional on {report['metrics'][0]['top_k_eligible_people']} positive-label people; repeated observations can remain.</p>"+
            ''.join(sections)+'<h2>Limits</h2>'+''.join('<p>'+escape(x)+'</p>' for x in report['limitations'])+
            '<p><a href="comparison.json">Complete aggregate report</a></p></html>')
    output.mkdir(parents=True,exist_ok=True)
    (output/'comparison.json').write_text(json.dumps(train._json_finite(report),indent=2,allow_nan=False))
    (output/'comparison.html').write_text(page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame',required=True,type=Path)
    parser.add_argument('--summary',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    report, private = evaluate(pd.read_json(args.frame,orient='table'),json.loads(args.summary.read_text())['facial_measurements'])
    report.update({
        'method': 'Seven leave-person-out folds, train six/test one. Production ARKit uses actual train_custom_lr_with_split and prediction code: total-perimeter quadratic plus shared-strength latent nose mismatch, Adam 200 epochs, lr .01, original row-weighted loss. Traditional/PCA arms unchanged: equal-person-weighted L2 logistic, C=1. Three ARKit initializations (42/43/44); traditional/PCA fits are deterministic.',
        'source_hashes': {name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in [('frame',args.frame),('summary',args.summary)]},
        'limitations': [
            'Only seven independent people and six positive-label people eligible for top-k. Two people contribute about 70% of test rows.',
            'This compares different architectures and training recipes: production ARKit uses row-weighted BCE; traditional/PCA retains the prior equal-person training weights. It is not an isolated causal effect of measurement modality.',
            'Production architecture is retrained on the six training people in each fold; deployed full-data weights are not used because they could include the evaluation people.',
            'All three arms use identical held-out observations. No traditional-to-ARKit conversion, no imputation, no outside training people, no held-out tuning. Scaling/PCA use training people only.',
            'Traditional/PCA hyperparameters remain fixed from the previous experiment. Three initializations share the same folds and are not confidence intervals or independent participants.',
            'Latest paired measurements and fit-test dates may differ. Labels mix evidence sources; repeated user-mask tests may remain. Top-k is not full-catalog prospective fit success.',
            'Calibration, measurement accuracy and population generalization remain unvalidated. No production model or slide deck was changed by this local experiment.',
        ]})
    write_review(report,args.output)
    (args.output/'private_predictions.json').write_text(json.dumps(private,indent=2,allow_nan=False))
    print(args.output/'comparison.html')


if __name__ == '__main__':
    main()
