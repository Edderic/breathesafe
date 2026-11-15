# Nested validation of traditional/PCA complexity

November 14, 2026. This local analysis preserves the original seven-person snapshot and frozen slide metrics.

## Method

- Outer folds: train on six people; evaluate the seventh. Inner folds: train on five of the six; validate the sixth. Each outer person is excluded from all its inner model selection, scaling and PCA fits.
- Four recipes: strictly linear additive; linear with geometry-by-mask interactions; quadratic additive; quadratic with interactions. Linear recipes remove face/PC squares **and** the mask-perimeter square. Linear interaction models still have bilinear geometry-by-mask products, so they are not globally linear in all inputs jointly.
- L2 logistic regression C grid: 0.001, 0.01, 0.1, 1. Smaller C means stronger regularization. Keep equal-person training weights, z-scoring on unique training people, PCA-3 without whitening, and a fixed 0.5 cutoff. No threshold tuning.
- Select minimum inner held-out log loss. Report both pooled test-weighted and equal-person selection objectives; neither is chosen based on outer performance.
- Compare an unrestricted choice among the four recipes with a separate no-squares choice among the two linear recipes, reusing the same inner scores.
- 1,344 inner fits plus 56 selected outer refits; no convergence warnings. Nine tests pass, including original model reproduction, no-square design construction, preprocessing, and inner/outer person separation.

## Test-weighted outer results

The nested rows below use the test-weighted **inner selection** objective. The JSON also contains all equal-person-selection and equal-person-evaluation results.

| Model / selection | Precision | Recall | F1 | Log loss ↓ |
|---|---:|---:|---:|---:|
| traditional_direct · original fixed model | 20.9% | 15.7% | 0.179 | 3.074 |
| traditional_direct · nested all_recipes | 8.6% | 11.3% | 0.098 | 1.646 |
| traditional_direct · nested no_squares | 0.0% | 0.0% | 0.000 | 1.555 |
| traditional_pca3 · original fixed model | 26.3% | 22.6% | 0.243 | 4.319 |
| traditional_pca3 · nested all_recipes | 18.8% | 15.7% | 0.171 | 3.680 |
| traditional_pca3 · nested no_squares | 1.4% | 1.7% | 0.015 | 2.574 |
| Production ARKit reference · mean 3 seeds | 55.9% | 46.7% | 0.509 | 0.948 |

## What this says

**Stronger regularization / simpler recipes reduced log loss, but did not improve precision or recall at the fixed cutoff.** The inner-selected unrestricted traditional recipe reduced log loss from 3.074 to 1.646; PCA reduced it from 4.319 to 3.680. Classification metrics deteriorated. Log-loss optimization is not precision/recall optimization.
**No squares is not an extrapolation safeguard.** In the held-out child fold, no-squares selection chooses linear-additive C=1 for both traditional and PCA models, with either selection objective. Both then classify all 130 negative-label tests as fitting. Their linear scores can still become extreme outside the training population. The unrestricted traditional selector also chooses that linear model for this fold.
**Removing interactions was often selected, but this restricts personalization.** Under pooled-log-loss selection, the unrestricted traditional model selects quadratic-additive in 5/7 outer folds, linear-additive in 1/7 and linear-interactions in 1/7; PCA selects quadratic-additive in 6/7. Additive face terms shift all mask logits for one face equally, rather than learning face-dependent mask rankings. Reduced capacity is not automatically a better recommendation model.
**A held-out child remains a domain gap.** When that child is the outer person, the inner folds contain only the larger remaining faces. There is no child example to inform the hyperparameter choice. Repeated adult fit-test rows cannot supply the missing child-face variation.
**Zero precision/recall in the no-squares traditional result means zero true-positive predictions, not zero positive predictions.** It still produces false positives, notably for the child. This distinction matters when interpreting a degenerate classifier.

## Recommended next work

1. Add a mask-only, strongly regularized baseline to determine how much predictive value six-dimensional face inputs add in this tiny cohort.
2. Test a low-capacity, constrained face-to-mask compatibility model using traditional dimensions, with partial pooling across mask families. Constrained squared mismatch terms are different from unconstrained polynomial terms: a nonpositive mismatch penalty encodes a preferred range rather than allowing arbitrarily favorable scores at an extrapolated extreme. Constraining all squares away removes that useful shape as well.
3. For an operational precision/recall target, choose a threshold using inner held-out predictions only and report outer precision, recall and log loss together. Avoid selecting a recipe or threshold from these outer results.
4. Collect more paired people, particularly children and smaller faces, and test a new cohort. These seven participants cannot establish generalization across age/face-size ranges.

## Limits and reproducibility

Nested CV protects the outer person within each fit/selection step, but this grid was proposed after earlier exploration of the same cohort. Treat results as exploratory, not a fresh confirmatory validation. Only five people train each inner model; recipe selection is unstable. Production ARKit uses a different architecture and original test-weighted training loss; its saved reference is not a controlled modality-only comparison. No models, physical measurements, slide results or production defaults were replaced.

Aggregate results and all inner-grid scores: `traditional-nested-validation.json`. Individual predictions stay in ignored tmp files. Run with the existing local scientific environment:

```sh
PYTHONPATH=python OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m mask_recommender.scripts.nested_traditional_validation \
  --frame tmp/retired-nasem-worktree-cache/recommender-nose-review/models/20261112155020/training_frame.json \
  --summary tmp/retired-nasem-worktree-cache/recommender-metrics-review/facial-summary.json \
  --output tmp/traditional-nested-validation
```

The completed local run reused identical, hash-checked inner scores when adding the no-squares comparison. A fresh run without --reuse-inner reproduces both model families from the same inputs.
