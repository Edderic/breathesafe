"""Matched, person-held-out models for ARKit, direct traditional inputs and PCA.

Local snapshots only; no conversion into estimated ARKit paths. All arms use the
same regularized mask-aware logistic classifier and the same paired participants.
"""
import argparse
import hashlib
import json
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from mask_recommender import train
from mask_recommender.predict_arkit_from_traditional import FEATURE_COLUMNS, TARGET_COLUMNS
from mask_recommender.scripts.compare_measurement_sources import paired_summary, score_rows

ARMS = ['measured_arkit', 'traditional_direct', 'traditional_pca3']


class FaceMaskClassifier:
    def __init__(self, arm, c=1.0):
        if arm not in ARMS:
            raise ValueError('Unknown measurement arm')
        self.arm = arm
        self.columns = TARGET_COLUMNS if arm == 'measured_arkit' else FEATURE_COLUMNS
        self.face_scaler = StandardScaler()
        self.perimeter_scaler = StandardScaler()
        self.categories = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
        self.pca = PCA(n_components=3, svd_solver='full') if arm == 'traditional_pca3' else None
        self.classifier = LogisticRegression(C=c, solver='lbfgs', max_iter=2000, tol=1e-8)

    def _categories(self, frame):
        return np.column_stack([train._fit_family_key_series(frame).astype(str),
                                frame['style'].fillna('unknown').astype(str),
                                frame['strap_type'].fillna('unknown').astype(str)])

    def geometry(self, frame, people):
        values = people.set_index('user_id').loc[frame.user_id, self.columns].to_numpy(dtype=float)
        scaled = self.face_scaler.transform(values)
        return self.pca.transform(scaled) if self.pca is not None else scaled

    def design(self, frame, people):
        geometry = self.geometry(frame, people)
        basis = np.column_stack([geometry, geometry ** 2])
        mask = self.categories.transform(self._categories(frame))
        perimeter = self.perimeter_scaler.transform(frame[['mask_perimeter_mm']])
        blocks = [mask, sparse.csr_matrix(perimeter), sparse.csr_matrix(perimeter ** 2),
                  sparse.csr_matrix(basis), sparse.csr_matrix(basis * perimeter)]
        blocks.extend(mask.multiply(basis[:, [column]]) for column in range(basis.shape[1]))
        return sparse.hstack(blocks, format='csr')

    def fit(self, frame, people):
        training_people = people.loc[people.user_id.isin(frame.user_id)].copy()
        self.training_people = set(training_people.user_id)
        # Fit geometry preprocessing once per person, not once per fit-test row.
        scaled = self.face_scaler.fit_transform(training_people[self.columns].to_numpy(dtype=float))
        if self.pca is not None:
            self.pca.fit(scaled)
        self.perimeter_scaler.fit(frame[['mask_id', 'mask_perimeter_mm']].drop_duplicates()[['mask_perimeter_mm']])
        self.categories.fit(self._categories(frame))
        counts = frame.user_id.value_counts()
        weights = frame.user_id.map(lambda user: len(frame) / (len(counts) * counts[user])).to_numpy()
        self.classifier.fit(self.design(frame, people), frame.qlft_pass_normalized.to_numpy(), sample_weight=weights)
        return self

    def predict(self, frame, people):
        return self.classifier.predict_proba(self.design(frame, people))[:, 1]


def paired_frame(frame, summary):
    people = paired_summary(summary)
    people = people.loc[people.user_id.isin(frame.user_id)].sort_values('user_id').reset_index(drop=True)
    frame = frame.loc[frame.user_id.isin(people.user_id)].copy()
    frame['mask_perimeter_mm'] = frame.apply(train._mask_perimeter_mm_from_training_row, axis=1)
    if len(people) < 4:
        raise ValueError('PCA-3 requires at least four paired people')
    return frame.reset_index(drop=True), people


def evaluate(frame, summary):
    frame, people = paired_frame(frame, summary)
    arms = {arm: [] for arm in ARMS}
    folds = []
    for fold, user in enumerate(people.user_id, 1):
        fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
        testing = frame.loc[frame.user_id == user].reset_index(drop=True)
        training_people = people.loc[people.user_id != user]
        assert user not in set(fitting.user_id) | set(training_people.user_id)
        record = {'fold': fold, 'training_people': len(training_people), 'test_rows': len(testing), 'arms': {}}
        keys = []
        for arm in ARMS:
            model = FaceMaskClassifier(arm).fit(fitting, training_people)
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
            record['arms'][arm] = {
                'feature_count': len(model.columns) if model.pca is None else model.pca.n_components_,
                'design_columns': model.classifier.n_features_in_,
                'optimizer_iterations': int(model.classifier.n_iter_[0]),
                'pca_retained_variance': float(model.pca.explained_variance_ratio_.sum()) if model.pca is not None else None,
            }
        assert keys[0] == keys[1] == keys[2]
        folds.append(record)
    return {'paired_people': len(people), 'test_rows': len(frame),
            'test_counts_per_person_sorted': sorted(frame.groupby('user_id').size().tolist()),
            'folds': folds, 'arms': {arm: score_rows(rows) for arm, rows in arms.items()}}, arms


def write_review(report, output):
    results = []
    for arm, value in report['arms'].items():
        evaluation = value['probability_evaluation']
        for weighting in ['test_weighted', 'equal_person']:
            quality = evaluation['quality'] if weighting == 'test_weighted' else evaluation['user_equal']['quality']
            metrics = evaluation['at_0_5'] if weighting == 'test_weighted' else evaluation['user_equal']['at_0_5']
            results.append({'arm': arm, 'weighting': weighting, 'precision': metrics['precision'],
                'recall': metrics['recall'], 'f1': metrics['f1'],
                'negative_predictive_value': metrics['negative_predictive_value'], 'log_loss': quality['log_loss'],
                **{f'top_{k}': value['top_k']['top_k_hit_rate'][str(k)] for k in [1,3,5]},
                'top_k_eligible_people': value['top_k']['eligible_users']})
    report['metrics'] = results
    pct = lambda value: f'{value:.1%}' if value is not None else 'N/A'
    rows = ''.join('<tr><td>'+escape(r['arm'])+'</td><td>'+r['weighting']+'</td>'+''.join(
        '<td>'+pct(r[key])+'</td>' for key in ['precision','recall'])+
        f"<td>{r['f1']:.3f}</td><td>{r['log_loss']:.3f}</td>"+''.join(
        '<td>'+pct(r[f'top_{k}'])+'</td>' for k in [1,3,5])+'</tr>' for r in results)
    page = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<title>Three measured-input model comparison</title><style>body{font:17px system-ui;max-width:1250px;margin:40px auto;padding:20px;color:#243b46}table{border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}p{line-height:1.5}</style>'
            '<h1>Measured ARKit vs direct traditional dimensions vs PCA</h1>'
            f"<p>{escape(report['method'])}</p><p>{report['paired_people']} paired people; {report['test_rows']} observations. "
            'Fixed 50% cutoff. Equal-person-weighted rows are the primary comparison; two people contribute about 70% of test rows. Top-k is person-level, conditional on positive labels, and identical in both weighting rows.</p>'
            '<table><tr><th>Predictors</th><th>Weighting</th><th>Precision</th><th>Recall</th><th>F1</th><th>Log loss</th><th>Top-1</th><th>Top-3</th><th>Top-5</th></tr>'+
            rows+'</table><h2>Limitations</h2>'+''.join('<p>'+escape(x)+'</p>' for x in report['limitations'])+
            '<p><a href="comparison.json">Download complete aggregate report</a></p></html>')
    output.mkdir(parents=True, exist_ok=True)
    (output/'comparison.json').write_text(json.dumps(train._json_finite(report),indent=2,allow_nan=False))
    (output/'comparison.html').write_text(page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report, audit = evaluate(pd.read_json(args.frame,orient='table'),json.loads(args.summary.read_text())['facial_measurements'])
    report.update({
        'method': 'Seven leave-person-out folds: train six, test one. Three separately fitted matched L2 logistic classifiers (C=1, lbfgs). Standardization/PCA fit on training people only. No ARKit conversion, no imputation, no tuning on test outcomes. Equal-person training weights; identical mask features and interaction recipe. Deterministic optimization.',
        'predictors': {'measured_arkit': TARGET_COLUMNS, 'traditional_direct': FEATURE_COLUMNS,
                       'traditional_pca3': 'First 3 PCA components of standardized six traditional dimensions, chosen before outcome evaluation.'},
        'mask_features': 'Fit family, style, strap type, standardized observed mask perimeter and squared perimeter. Shared linear/squared face terms, face×perimeter and face×mask-category interactions.',
        'source_hashes': {name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in [('frame',args.frame),('summary',args.summary)]},
        'limitations': [
            'Only seven independent people, despite hundreds of tests. Six positive-label people qualify for top-k. The two busiest testers supply about 70% of observations.',
            'This ARKit arm uses the same matched regularized classifier as the traditional arms, not the production perimeter-plus-nose architecture. Results are not directly comparable to prior 18/49-person pipeline experiments.',
            'The PCA model retains three components chosen in advance; other component counts or regularization strengths could change results. No claim that this is the best model for either modality.',
            'Scaling and PCA see only the six training people. C=1 and the feature recipe were fixed without selecting for these held-out results. Different feature counts still produce different effective capacity.',
            'Traditional and ARKit measurements are latest per-person summaries; collection times may differ from each other and from fit tests.',
            'Top-k ranks existing held-out test observations; repeated user-mask tests may remain. It is not prospective success across the full mask catalog. Labels mix evidence sources.',
            'Model prediction performance does not establish anatomical measurement accuracy. Results remain exploratory; independent paired participants are needed for generalization claims.',
        ]})
    write_review(report,args.output)
    (args.output/'private_predictions.json').write_text(json.dumps(audit,indent=2,allow_nan=False))
    print(args.output/'comparison.html')


if __name__ == '__main__':
    main()
