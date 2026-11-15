# Traditional and PCA model audit

November 14, 2026. The earlier dashboard/deck commit `c991fb4a` was pushed to origin/main. This local investigation does not replace the frozen slide results or production model.

## Findings

1. **The six dimensions already receive z-score scaling.** `FaceMaskClassifier.fit` fits `StandardScaler` once per unique training person, then applies it to the held-out person. Mask perimeter is separately standardized on distinct training mask/perimeter records. PCA-3 is fit after standardization, on the six training people only. No held-out-person leakage was found in these transformations.
2. **The expanded classifier is much less constrained than production ARKit.** Traditional has 767–819 design columns and PCA has 413–441 across folds, including squared geometry and category interactions, learned from only six independent faces per fold. Those columns are not independent effects or a count of independent observations. Production ARKit directly encodes total-perimeter mismatch and a separate squared nose penalty; it has a different parameterization and training objective.
3. **Large held-out extrapolation is real.** One person is 8.77 training standard deviations from the training face-length mean, and outside the training range on four of six dimensions. Squaring that standardized face-length value gives roughly 77 before its interactions. This is not evidence that the measurement is erroneous; measurement endpoints/units should be reviewed before drawing that conclusion.
4. **The busiest people explain much of the test-weighted gap.** Both original traditional classifiers predict no positives for the 166-test participant, missing all 85 positive labels. For the 130-test participant with zero positive labels, traditional produces 58 false positives and PCA 53; production ARKit averages 5.7 across three initializations. The traditional/PCA log losses for that fold are 6.353/12.564, versus production ARKit 0.083. These two people supply 70.3% of tests.
5. **Scaling changes did not rescue this fixed-C model.** Additional weighted unit-variance scaling of every expanded column (without sparse centering) worsened both classifiers at C=1; whitening PCA also worsened it. Scaling changes effective L2 regularization, so this is a fixed-C sensitivity result, not proof no jointly tuned scaling/regularization recipe could improve.
6. **Training-weight differences are not the main explanation in these checks.** Giving each test equal training weight raised PCA precision/recall slightly, but reduced traditional precision/recall. The production comparison is still not a controlled measurement-modality experiment.
7. **Capacity/regularization matters, but the cutoff remains a tradeoff.** An additive traditional model with stronger regularization (C=0.01) reduced log loss to 0.527, while recall at the unchanged 0.5 cutoff was only 6.1%. That is not a blanket classification improvement. Hyperparameters were not chosen by nested CV, so these comparisons are exploratory sensitivity checks.
8. **ARKit measurements alone do not guarantee success.** In the saved earlier matched-classifier control, measured ARKit fed into the same unconstrained logistic interaction recipe had log loss 8.946, precision 32.3%, recall 73.0%; production ARKit has 0.948, 55.9%, 46.7%. Architecture and training recipe clearly matter. This does not isolate architecture from weighting or establish which measurement modality is intrinsically better.
9. **The conclusion changes with evaluation weighting.** Under equal-person evaluation, original PCA F1 is 0.528, versus production ARKit 0.486; original PCA precision/recall are 54.4%/51.2%, versus ARKit 49.8%/47.5%. PCA still has worse log loss (2.298 vs 0.899). Therefore the statement that traditional/PCA precision and recall are uniformly worse is not supported. With seven people, do not call the performance gap statistically significant without an appropriate uncertainty analysis.

## Selected test-weighted comparisons

| Pipeline | Precision | Recall | F1 | Log loss |
|---|---:|---:|---:|---:|
| Production ARKit reference (mean of 3 seeds) | 55.9% | 46.7% | 0.509 | 0.948 |
| traditional_direct · original | 20.9% | 15.7% | 0.179 | 3.074 |
| traditional_direct · test_weighted | 18.9% | 14.8% | 0.166 | 3.141 |
| traditional_direct · expanded_zscore | 14.9% | 15.7% | 0.153 | 4.956 |
| traditional_direct · additive_C_0.01 | 46.7% | 6.1% | 0.108 | 0.527 |
| traditional_pca3 · original | 26.3% | 22.6% | 0.243 | 4.319 |
| traditional_pca3 · test_weighted | 27.8% | 23.5% | 0.255 | 3.635 |
| traditional_pca3 · expanded_zscore | 13.7% | 11.3% | 0.124 | 6.040 |
| traditional_pca3 · additive_C_0.01 | 3.4% | 4.3% | 0.038 | 0.875 |
| traditional_pca3 · pca_whiten | 17.6% | 16.5% | 0.170 | 5.450 |

## Recommended next experiment

Use nested person-grouped cross-validation to select a small regularization/interaction-complexity grid on inner training people only. Evaluate the selected recipe on the untouched outer person. If a decision threshold is tuned, choose it using inner held-out predictions only and state the target objective. Compare test-weighted and equal-person training/evaluation explicitly. Keep a matched-classifier ARKit control alongside production ARKit so architecture is not mistaken for measurement quality. More paired people, with consistent anatomical definitions and wider face-size coverage, are essential; nested folds here would have only five training people, so they will remain unstable.

## Reproducibility

All 23 configurations reuse the original 421 tests and seven people, in identical leave-person-out folds. There are 161 outer fits plus 14 independent original-classifier reproduction checks. Every original prediction was numerically reproduced to 1e-10; all fits finished without convergence warnings. Input hashes match both saved comparison reports. No external data, S3, retraining of production, or changes to physical measurements were involved.

Run locally with the existing scientific Python environment:

```sh
PYTHONPATH=python OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m mask_recommender.scripts.audit_traditional_scaling \
  --frame tmp/retired-nasem-worktree-cache/recommender-nose-review/models/20261112155020/training_frame.json \
  --summary tmp/retired-nasem-worktree-cache/recommender-metrics-review/facial-summary.json \
  --output tmp/traditional-scaling-audit
```

Aggregate metrics and per-fold diagnostics: `traditional-scaling-audit.json`. Participant identities and individual predictions remain in ignored tmp files. Tests cover original-model reproduction, training-only weighted feature scaling, PCA whitening and additive feature capacity.

References: [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html), [feature scaling and regularization](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html).

## Confirmed interpretation of the extrapolation case

The presenter confirmed that the 77 mm held-out face length belongs to a child compared with substantially larger training faces. It is retained as a genuine extrapolation test, not treated as an identified entry error. The observed false-positive advantage is consistent with useful face-to-mask deviation constraints, but does not isolate architecture from training weights or establish generalization to children as a population. This child fold has zero positive labels; child-specific recall is undefined. Measurement age and fit-test dates still merit review.
