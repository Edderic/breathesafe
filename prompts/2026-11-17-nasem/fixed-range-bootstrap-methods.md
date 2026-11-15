# Fixed-range scaling and full-refit bootstrap

Exploratory sensitivity analysis, November 15, 2026. The completed aggregates and provenance hashes are in [fixed-range-bootstrap-evidence.json](fixed-range-bootstrap-evidence.json). Slide 12 reports the results; appendix slide 33 explains the method.

## Scaling

Use `(x − min) / (max − min)` with the following fixed bounds. These are broad, provisional engineering assumptions, **not validated population limits** for children or adults.

| Predictor | Minimum mm | Maximum mm |
|---|---:|---:|
| Face width | 50 | 200 |
| Face length | 40 | 180 |
| Bitragion–subnasale arc | 100 | 450 |
| Nose protrusion | 0 | 50 |
| Nasal root breadth | 0 | 50 |
| Nose bridge height | 0 | 70 |
| Mask perimeter | 100 | 800 |

Values outside the bounds raise an error rather than being clipped. The initially proposed mask maximum of 650 mm was increased to 800 mm before fitting because a predictor-only check found two existing rows at 699 mm. Outcome labels were not used to set these limits.

PCA is fitted without whitening within each training fold. For a component with loadings `v`, the projection over the input unit cube has minimum `sum(min(v, 0))` and width `sum(abs(v))`. Subtracting that minimum and dividing by that width bounds the component score too; the fitted PCA mean cancels in this calculation. No held-out extrema are estimated.

Linear, squared and interaction predictors are consequently bounded for in-range measurements. Learned coefficients and logits are still unbounded. The existing feature recipe and logistic L2 setting C = 1 are retained: changing feature scale also changes the effective regularization penalty, so this does not isolate polynomial growth from regularization effects.

## Full training-pipeline bootstrap

- Same seven original participants and 421 observations as the paired comparison; 115 positive labels.
- Draw seven participant clusters with replacement, 10,000 times, RNG seed 20261115.
- Within each draw, perform leave-original-person-out validation. All copies of a held-out person are excluded from training together. Participant multiplicity affects both fitting and evaluation.
- Refit category vocabulary, PCA and classifiers from the resampled training data. Fixed transforms use the predefined physical bounds. This is **full refitting with a fixed recipe**, not nested hyperparameter selection.
- Traditional/PCA training retains equal-person weighting, including each sampled copy. ARKit retains its production row-weighted objective, 200 Adam epochs, learning rate 0.01, and the original three initialization seeds with held-person offsets. Compute metrics for each initialization and then average metrics; do not ensemble probabilities first.
- Use threshold 0.5. Compare all three models on identical held-out observations in each draw. Report test-weighted and equal-person results in the JSON; the main slide uses test weighting.
- Deterministically identical training multisets and seeds are cached. The run completed 1,834 distinct training tasks, each fitting three ARKit initializations and two traditional classifiers: **9,170 actual fits**, about 462 seconds with four CPU workers. This does not substitute frozen original OOF predictions for refitting.

Three-component PCA needs at least four distinct, rank-sufficient training faces in every held-person fold. Of 10,000 attempts, **5,588 were evaluable and 4,412 were excluded** for insufficient PCA rank. All five reported metrics were defined for all three models in those 5,588 draws. Frequencies below condition on this evaluable subset. The JSON additionally reports winner counts divided by all 10,000 attempts.

## Results

Original-cohort held-out point estimates after fixed-range scaling:

| Metric | Production ARKit | Traditional | Traditional → PCA |
|---|---:|---:|---:|
| Log loss | 0.9482 | 0.9885 | 0.7680 |
| Precision | 55.9% | 23.5% | 30.6% |
| Recall | 46.7% | 27.8% | 38.3% |
| F1 | 0.5087 | 0.2550 | 0.3398 |
| NPV | 81.1% | 70.9% | 74.4% |

With the earlier z-score recipe, traditional/PCA log losses were 3.0736/4.3195, precision 20.9%/26.3%, and recall 15.7%/22.6%. Production ARKit point metrics reproduce the earlier frozen comparison to within 1e-12.

Strict-best counts and proportions, denominator **5,588**:

| Metric | ARKit | Traditional | PCA | Tied draws |
|---|---:|---:|---:|---:|
| Lower log loss | 1,021 (18.27%) | 1,458 (26.09%) | 3,109 (55.64%) | 0 |
| Higher precision | 4,361 (78.04%) | 380 (6.80%) | 663 (11.86%) | 184 |
| Higher F1 | 4,353 (77.90%) | 389 (6.96%) | 663 (11.86%) | 183 |
| Higher NPV | 4,046 (72.41%) | 465 (8.32%) | 894 (16.00%) | 183 |
| Higher recall | 3,351 (59.97%) | 643 (11.51%) | 777 (13.90%) | 817 |

Strict winners exclude ties, using absolute tolerance 1e-12 and zero relative tolerance. No fractional tie credit is assigned. Pointwise percentile 95% intervals are included in the JSON and are conditional on evaluable draws; they are not adjusted for multiple comparisons.

## Interpretation and limits

Fixed ranges substantially reduced probability loss, particularly for PCA. ARKit most often won precision, F1, NPV and recall in these evaluable resamples; PCA most often won log loss. Lower log loss measures overall probability prediction quality and does not, by itself, establish calibration.

Bounding inputs did **not** solve the child extrapolation problem. For the held-out child's 130 negative tests, fixed-range traditional/PCA produced 83/73 false positives, versus 58/53 with the earlier z-score models and an average of 5.67 across the ARKit initializations. Their log losses improved despite those additional threshold errors. Aggregate improvement must not be described as improved child classification.

Only seven independent people underlie the experiment. Bootstrap repetition adds no independent participants, 44.12% of attempts were not PCA-evaluable, and conditioning on the remaining draws changes the comparison's sampling distribution. These are exploratory bootstrap winner frequencies, **not posterior probabilities of model superiority or calibrated p-values**. Earlier investigation of this same cohort further limits confirmatory interpretation. Validation on additional children, large adult faces and independent participants remains necessary.

## Reproduction and checks

From the repository root, using the existing scientific Python environment:

```sh
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
tmp/retired-nasem-worktree-cache/recommender-evaluation-venv/bin/python \
-m mask_recommender.scripts.bootstrap_fixed_range_comparison \
--frame tmp/retired-nasem-worktree-cache/recommender-nose-review/models/20261112155020/training_frame.json \
--summary tmp/retired-nasem-worktree-cache/recommender-metrics-review/facial-summary.json \
--output tmp/fixed-range-full-bootstrap --replicates 10000 --pca-policy fixed --workers 4
```

Five focused pytest checks cover range handling, analytic PCA cube bounds, bootstrap participant multiplicity, PCA rank policy, metric aggregation and strict winner/tie counting. Public evidence contains aggregate metrics and hashes; private input records and cached per-person predictions remain in ignored local storage.
