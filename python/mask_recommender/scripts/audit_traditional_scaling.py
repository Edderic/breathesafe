"""Local sensitivity audit; outer held-out results are exploratory, not tuning CV."""
import argparse
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler

from mask_recommender import train
from mask_recommender.scripts.compare_direct_measurements import FaceMaskClassifier, paired_frame
from mask_recommender.scripts.compare_measurement_sources import score_rows

CONFIGS = {
    'original': {},
    'test_weighted': {'test_weighted': True},
    'expanded_zscore': {'expanded_zscore': True},
    'expanded_zscore_test_weighted': {'expanded_zscore': True, 'test_weighted': True},
    'C_0.1': {'c': .1},
    'C_0.01': {'c': .01},
    'C_0.001': {'c': .001},
    'C_0.01_test_weighted': {'c': .01, 'test_weighted': True},
    'additive': {'interactions': False},
    'additive_C_0.01': {'interactions': False, 'c': .01},
    'linear_interactions': {'squared': False},
    'pca_whiten': {'whiten': True},
}


class AuditClassifier(FaceMaskClassifier):
    def __init__(self, arm, c=1., test_weighted=False, expanded_zscore=False,
                 interactions=True, squared=True, whiten=False, mask_squared=True):
        super().__init__(arm, c)
        self.test_weighted = test_weighted
        self.expanded_zscore = expanded_zscore
        self.interactions = interactions
        self.squared = squared
        self.mask_squared = mask_squared
        self.design_scaler = None
        if self.pca is not None:
            self.pca.set_params(whiten=whiten)

    def raw_design(self, frame, people):
        geometry = self.geometry(frame, people)
        basis = np.column_stack([geometry, geometry**2]) if self.squared else geometry
        mask = self.categories.transform(self._categories(frame))
        perimeter = self.perimeter_scaler.transform(frame[['mask_perimeter_mm']])
        blocks = [mask, sparse.csr_matrix(perimeter), sparse.csr_matrix(basis)]
        if self.mask_squared:
            # Preserve the original feature ordering for reproduction checks.
            blocks.insert(2, sparse.csr_matrix(perimeter**2))
        if self.interactions:
            blocks.append(sparse.csr_matrix(basis*perimeter))
            blocks.extend(mask.multiply(basis[:, [i]]) for i in range(basis.shape[1]))
        return sparse.hstack(blocks, format='csr')

    def design(self, frame, people):
        design = self.raw_design(frame, people)
        return self.design_scaler.transform(design) if self.design_scaler else design

    def fit(self, frame, people):
        training = people.loc[people.user_id.isin(frame.user_id)]
        self.training_people = set(training.user_id)
        scaled = self.face_scaler.fit_transform(training[self.columns].to_numpy(dtype=float))
        if self.pca is not None:
            self.pca.fit(scaled)
        self.perimeter_scaler.fit(frame[['mask_id', 'mask_perimeter_mm']].drop_duplicates()[['mask_perimeter_mm']])
        self.categories.fit(self._categories(frame))
        counts = frame.user_id.value_counts()
        weights = (np.ones(len(frame)) if self.test_weighted else
                   frame.user_id.map(lambda u: len(frame)/(len(counts)*counts[u])).to_numpy())
        design = self.raw_design(frame, people)
        if self.expanded_zscore:
            # Sparse centering is unnecessary with a free intercept; scale every
            # expanded column to weighted unit variance using training rows only.
            self.design_scaler = StandardScaler(with_mean=False).fit(design, sample_weight=weights)
            design = self.design_scaler.transform(design)
        self.classifier.fit(design, frame.qlft_pass_normalized.to_numpy(), sample_weight=weights)
        return self


def summarize(rows):
    result = score_rows(rows)
    e = result['probability_evaluation']
    return {weighting: dict(**quality, **{k: fixed[k] for k in ['precision', 'recall', 'f1', 'negative_predictive_value']},
                            **{f'top_{k}': result['top_k']['top_k_hit_rate'][str(k)] for k in [1, 3, 5]})
            for weighting, quality, fixed in [('test_weighted', e['quality'], e['at_0_5']),
                                               ('equal_person', e['user_equal']['quality'], e['user_equal']['at_0_5'])]}


def run(frame_path, summary_path, out):
    frame, people = paired_frame(pd.read_json(frame_path, orient='table'),
                                 json.loads(summary_path.read_text())['facial_measurements'])
    results = []
    private = {}
    for arm in ['traditional_direct', 'traditional_pca3']:
        for name, config in CONFIGS.items():
            if name == 'pca_whiten' and arm != 'traditional_pca3':
                continue
            rows, folds = [], []
            for fold, user in enumerate(people.user_id, 1):
                fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
                testing = frame.loc[frame.user_id == user].reset_index(drop=True)
                training_people = people.loc[people.user_id != user]
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always', ConvergenceWarning)
                    model = AuditClassifier(arm, **config).fit(fitting, training_people)
                assert user not in model.training_people
                p = model.predict(testing, people)
                # The baseline implementation must be numerically reproduced.
                if name == 'original':
                    reference = FaceMaskClassifier(arm).fit(fitting, training_people)
                    np.testing.assert_allclose(p, reference.predict(testing, people), atol=1e-10)
                deduped, p, y = train._dedupe_prediction_rows(testing, p, testing.qlft_pass_normalized.to_numpy())
                for (_, row), probability, label in zip(deduped.iterrows(), p, y):
                    identity = row.get('source_fit_test_id', row.get('id'))
                    if pd.isna(identity):
                        identity = row.get('id')
                    rows.append(dict(fold=fold, user_id=int(user), mask_id=int(row.mask_id), fit_test_id=int(identity),
                                     label=int(label), probability=float(probability),
                                     training_positive_rate=float(fitting.qlft_pass_normalized.mean())))
                z = model.face_scaler.transform(people.loc[people.user_id == user, model.columns].to_numpy(dtype=float))[0]
                train_z = model.face_scaler.transform(training_people[model.columns].to_numpy(dtype=float))
                family_key = train._fit_family_key_series
                positive = p >= .5
                loss = -np.log(np.clip(np.where(y == 1, p, 1-p), 1e-15, 1-1e-15)).mean()
                folds.append(dict(fold=fold, tests=len(p), positives=int(y.sum()),
                                  true_positives=int(((y == 1) & positive).sum()),
                                  false_positives=int(((y == 0) & positive).sum()),
                                  log_loss=float(loss), mean_score=float(p.mean()),
                                  dimensions_outside_training_range=int(((z < train_z.min(0)) | (z > train_z.max(0))).sum()),
                                  max_abs_test_z=float(abs(z).max()), design_columns=model.classifier.n_features_in_,
                                  optimizer_iterations=int(model.classifier.n_iter_[0]),
                                  convergence_warnings=sum(isinstance(w.message, ConvergenceWarning) for w in caught),
                                  unseen_family_fraction=float((~family_key(testing).isin(set(family_key(fitting)))).mean()),
                                  extreme_score_fraction=float(((p < .01) | (p > .99)).mean()),
                                  pca_variance=float(model.pca.explained_variance_ratio_.sum()) if model.pca else None))
            key = arm+'/'+name
            private[key] = rows
            results.append(dict(arm=arm, configuration=name, settings=config, metrics=summarize(rows), folds=folds))
            print(arm, name, {k: round(v, 4) if v is not None else None
                             for k, v in results[-1]['metrics']['test_weighted'].items()
                             if k in ['precision', 'recall', 'f1', 'log_loss']}, flush=True)
    report = dict(method='Seven leave-person-out folds on the original paired snapshot; all transformations fit inside each training fold.',
                  people=len(people), tests=len(frame), results=results,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  limitations=['Exploratory outer-fold sensitivity checks, not independently validated hyperparameter selection.',
                               'Only seven independent faces; architectures and training weights differ.',
                               'No production models, slide metrics, raw measurements or training inputs changed.'],
                  source_hashes={name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for name, path in [('frame', frame_path), ('summary', summary_path)]})
    out.mkdir(parents=True, exist_ok=True)
    (out/'audit.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    (out/'private_predictions.json').write_text(json.dumps(private, allow_nan=False)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.frame, args.summary, args.output)
