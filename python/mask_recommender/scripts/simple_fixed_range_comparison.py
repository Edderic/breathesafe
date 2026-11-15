"""Exploratory fixed-range feature ablation; local snapshots, no deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
from scipy import sparse
from sklearn.exceptions import ConvergenceWarning

from mask_recommender import train
from mask_recommender.scripts.bootstrap_fixed_range_comparison import prepare, stats, metric_values
from mask_recommender.scripts.fixed_range_models import FixedRangeClassifier, CONFIG_PATH

RECIPES = ('linear_additive', 'quadratic_additive', 'shared_perimeter_interactions', 'full_interactions')
ARMS = ('traditional_direct', 'traditional_pca3')
METRICS = ('log_loss', 'precision', 'recall', 'negative_predictive_value', 'f1')


class SimpleFixedRangeClassifier(FixedRangeClassifier):
    def __init__(self, arm, recipe):
        if recipe not in RECIPES:
            raise ValueError('Unknown feature recipe')
        super().__init__(arm)
        self.recipe = recipe

    def design(self, frame, people):
        if self.recipe == 'full_interactions':
            return super().design(frame, people)
        geometry = self.geometry(frame, people)
        categories = self.categories.transform(self._categories(frame))
        perimeter = self.perimeter_scaler.transform(frame[['mask_perimeter_mm']])
        if self.recipe == 'linear_additive':
            return sparse.hstack([categories, sparse.csr_matrix(perimeter), sparse.csr_matrix(geometry)], format='csr')
        basis = np.column_stack([geometry, geometry**2])
        blocks = [categories, sparse.csr_matrix(perimeter), sparse.csr_matrix(perimeter**2), sparse.csr_matrix(basis)]
        if self.recipe == 'shared_perimeter_interactions':
            blocks.append(sparse.csr_matrix(basis*perimeter))
        return sparse.hstack(blocks, format='csr')


def metric_record(totals):
    return {m: float(v) if np.isfinite(v) else None for m, v in zip(METRICS, metric_values(totals))}


def evaluate(frame, people):
    results = []
    for arm in ARMS:
        for recipe in RECIPES:
            total, equal = np.zeros(6), np.zeros(6)
            dimensions = []
            child_counts = None
            # The previously documented extrapolation case is identified by its
            # frozen all-negative 130-test fold, not by a public database ID.
            for user in people.user_id:
                fitting = frame.loc[frame.user_id != user].reset_index(drop=True)
                testing = frame.loc[frame.user_id == user].reset_index(drop=True)
                model = SimpleFixedRangeClassifier(arm, recipe)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always', ConvergenceWarning)
                    model.fit(fitting, people.loc[people.user_id != user])
                if any(isinstance(w.message, ConvergenceWarning) for w in caught):
                    raise RuntimeError('Classifier did not converge')
                assert user not in model.training_people
                p = model.predict(testing, people)
                deduped, p, y = train._dedupe_prediction_rows(testing, p, testing.qlft_pass_normalized.to_numpy())
                assert len(deduped) == len(testing)
                values = stats(y, p)
                total += values
                equal += values/values[-1]
                dimensions.append(int(model.classifier.n_features_in_))
                if len(y) == 130 and y.sum() == 0:
                    child_counts = dict(tests=130, false_positives=int(values[1]), true_negatives=int(values[2]))
            results.append(dict(arm=arm, recipe=recipe, predictors_min=min(dimensions), predictors_max=max(dimensions),
                intercept_parameters=1, test_weighted=metric_record(total), equal_person=metric_record(equal),
                child_extrapolation_case=child_counts))
    return results


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(args):
    frame, people = prepare(args.frame, args.summary)
    results = evaluate(frame, people)
    reference = json.loads(Path('prompts/2026-11-17-nasem/fixed-range-bootstrap-evidence.json').read_text())
    for row in results:
        if row['recipe'] == 'full_interactions':
            for metric, value in row['test_weighted'].items():
                expected = reference['results']['test_weighted'][metric]['arms'][row['arm']]['estimate']
                assert abs(value-expected) < 1e-12
    report = dict(people=len(people), tests=len(frame), threshold=.5, c=1., recipes=list(RECIPES), results=results,
        source_hashes=dict(frame=digest(args.frame), summary=digest(args.summary), config=digest(CONFIG_PATH),
            experiment=digest(__file__), scaler=digest(Path(__file__).with_name('fixed_range_models.py')),
            base_classifier=digest(Path(__file__).with_name('compare_direct_measurements.py'))),
        protocol='Seven leave-one-person-out folds. Refit PCA and category encoding on the six training people. Same fixed physical ranges, C=1, equal-person training weights and 50% threshold. No hyperparameter or threshold tuning.',
        limitations=[
            'Exploratory ablation on the same seven-person cohort; no new independent participants. Choosing the best recipe from these outer scores would be optimistic.',
            'No new bootstrap or nested selection in this initial feature comparison. Earlier bootstrap intervals do not apply to these new recipes.',
            'Additive logits f(face)+g(mask) have identical mask rankings for every face within one fitted model; they cannot personalize relative mask ordering.',
            'Shared face-by-perimeter products preserve some mask-size-dependent personalization with far fewer coefficients than category-specific interactions.',
            'Fixed C does not imply equal effective model complexity across feature sets. L2 strength and complexity should be selected within training people in a later nested comparison.',
            'The child case has no positive labels, so child-specific recall is undefined.'],
        production_arkit_reference={m: reference['results']['test_weighted'][m]['arms']['production_arkit']['estimate'] for m in METRICS})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args())
