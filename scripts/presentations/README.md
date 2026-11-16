# NASEM presentation rendering

The canonical November deck is `prompts/2026-11-17-nasem/presentation.html` on `main`. The former `nasem-prototype-update` worktree is retired. The deck has 31 slides: 19 main slides within 9 minutes 30 seconds, plus twelve backups. The September presentation is unchanged.

Build with `python3 prompts/2026-11-17-nasem/build_presentation.py`. Run `node scripts/presentations/render_nasem_prototype.cjs` to check frozen metrics, definitions, offline assets, desktop/mobile layout, navigation and print bounds, and export the PDF. The renderer uses local Chrome and Playwright; set `NASEM_PLAYWRIGHT_ROOT` if necessary. Screenshots go to ignored `tmp/nasem-preview/`.

Slides 5–6 show community context and demographics. Slide 7 defines mixed-source fit labels, explains varying access to testing tools, and shows Nov 13 record counts/proportions from `fit-evidence-source-counts.json`. Slide 8 shows mask coverage from the same Nov 13 public snapshot as slide 7. The balanced pass-rate comparison has moved to appendix slide 27. Slide 9 retains the separate 49-person nose-feature experiment, including NPV; slide 10 shows the seven-person test-weighted pipeline comparison. The equivalent equal-person evidence is retained but its slide remains removed. Prototype slides 13–15 retain actual raw/smoothed neck-inclusive headforms, landmarks and caliper checks. The unresolved bifold discrepancy remains omitted.

Appendix slides 21–23 cover 49-person top-k results, traditional predictors and the traditional/PCA feature expansion. The perimeter-coefficient explanation is integrated into slide 9. Slide 24 shows the conversion equations and MaskNerd spreadsheet credit; slide 25 revisits the historical N99-to-N95 conversion scatter with a Bayesian censored log-linear trend; slide 26 describes seal-check questionnaire/label rules; slide 27 shows balanced pass rates; slide 28 walks through landmark / curve projection; slide 29 reports paired bootstrap intervals; slide 10 includes the seven-person cohort; slide 30 covers fixed-range bootstrap methods; slide 31 contains sources. See the deck README and speaker notes for methods and limitations.

`analyze_n95_conversion.py` extracts the saved notebook aggregate table, excludes all mask aggregates containing assigned score-1 observations, fits four-chain Metropolis with measured-ceiling censoring, and writes anonymous frozen evidence and standalone SVG/PNG. The plot's prediction means N99-plus-filtration conversion, not a recommender output. Priors, sampling diagnostics and source hashes are in `n95-conversion-evidence.json`; detailed caveats and rebuild commands are in `fit-outcome-methods.txt`. Run `scripts/tests/test_n95_conversion_analysis.py` in the local scientific environment for extraction, censor-likelihood and synthetic recovery checks.

`paired-measurement-evidence.json`, `recommender-evidence.json` and `prototype-evidence.json` freeze the other evidence. Participant-level inputs, source captures and audit predictions remain private. The fit illustration is AI generated and is not fit-test evidence.

To refresh prototype source images, set `NASEM_SOURCE_ROOT` to the checkout containing `.private-webcam-runs` and run the renderer with `--capture-sources`, then rebuild the deck. Source annotations and reconstructions are not modified. No deployment is performed.

The seal-check appendix follows the exact backend evaluation order: sizing failures precede missing-answer checks, and missing sizing precedes the air-movement failure. Questionnaire pass and incomplete both map to NULL, never a positive label. Negative-pressure responses are not read by that service.

Slide 6 shows demographic counts and one-decimal percentages using all 55 participants as each column’s denominator. The renderer checks every displayed count/proportion against the October 29 aggregate snapshot.

Slide 5 states 55 unique users from the October 29 demographic snapshot. Slide 6 is titled “Demographic breakdown.” Slide 7 states 1,157 analyzed fit tests and 769 unique user–mask pairs from the separate, dated November 13 public snapshot. The frozen source-count evidence includes these pair/user totals; the renderer verifies their display.

Slide 7 pairs its source-count table with four original onboarding photographs. `fit-testing-photo-sources.json` records URLs and file hashes; local assets are embedded, with descriptive alt text, for offline presentation/PDF. The renderer verifies all four captions/images and responsive layout.

`build_pass_rate_evidence.rb` uses the actual `DashboardPassRatesService` on a private labeled-row export. It freezes only aggregates and hashes in `observed-pass-rate-evidence.json`. Appendix slide 27 uses 1,142 local records, separate from the public snapshots. See `observed-pass-rate-methods.txt` for the averaging hierarchy and provenance. The renderer verifies displayed rates against that evidence.

Main slide 8 lists the 30 most-tested mask entries with record counts/shares and global mask/person/pair coverage. It uses `mask-coverage-evidence.json`, matching slide 7’s public-response hash; it does not combine local per-mask participant counts with public test counts.

Slide 8 shows the top 30 mask entries in three columns (ranks 1–10, 11–20 and 21–30), with counts and shares from the same frozen public snapshot.

Slide 9 reports point estimates and pointwise 95% person-cluster percentile intervals, from 10,000 paired resamples of 49 people with independent classifier retraining (300,000 fits). Appendix slide 29 reports nose-minus-perimeter differences. Original folds, category catalog and prepared inputs stay fixed; global pre-CV imputation is not refitted and overlapping training sets remain limitations. Frozen aggregate evidence: recommender-bootstrap-evidence.json.

Appendix slide 29 also gives strict nose-model superiority frequencies over the same 10,000 paired bootstrap samples, with win counts. Ties within 1e-12 count as neither wins nor losses; exact counts and per-metric evaluable denominators are in the evidence JSON. These are bootstrap frequencies, not posterior probabilities or p-values.

Slide 10 shows seven random study UUID prefixes, approximate 2026 age bands, broad gender groups, race/ethnicity and exact held-out test/positive/negative counts. The held-out young-child case is highlighted in amber and marked with a star. Names, database IDs, exact birth years and the UUID identity lookup are excluded. These demographics are not predictors. The mismatch-model rationale is explained without claiming confirmed generalization to unseen larger faces.

Main slide 16 summarizes the staged Blueprint Biosecurity validation plan. Source: November 9 discussion draft, work-plan and decision-gate sections; hashes in blueprint-validation-plan-source.json. It is a proposed adult-first study, not completed validation or a funding commitment.

Slide 12 compares fixed-range-scaled traditional/PCA models with production ARKit. It reports original-cohort metrics plus strict-best counts/frequencies from full-refit participant bootstrap; 10,000 draws were attempted, 5,588 supported every PCA-3 fold, and 4,412 were explicitly unevaluable. Appendix slide 30 lists the exact provisional ranges and protocol. Frequencies condition on the paired-evaluable denominator, not all 10,000 attempts. Full report: fixed-range-bootstrap-evidence.json and fixed-range-bootstrap-methods.md.

With full classifier retraining, all five paired 95% difference intervals include zero. Nose strict-win frequencies: log loss 86.41%, precision 84.71%, F1 60.03%, NPV 50.64%, recall 35.66%.

Slide 11 compares linear, squared, shared-perimeter and full-category interaction recipes. Shaded rows identify highest F1 within Traditional/PCA; teal metric cells identify global best values. Child FPR uses 130 negative tests: ARKit 4.36% (5, 6, 6 false positives across seeds), Traditional 60.0–63.8%, PCA 49.2–56.2%. One child case, exploratory point estimates, no new bootstrap intervals. Sources: simple-fixed-range-comparison.json, child-false-positive-evidence.json and arkit-parameter-counts.json.

To refresh slide 14’s three headform overlays with thicker presentation strokes, run `node scripts/presentations/render_nasem_prototype.cjs --capture-routes`, then rebuild the deck and run the normal renderer. This uses the local private source viewers; saved meshes and route coordinates stay unchanged. Display settings and asset hashes are recorded in `prototype-route-display-source.json`.
