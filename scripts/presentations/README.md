# NASEM presentation rendering

The canonical November deck is `prompts/2026-11-17-nasem/presentation.html` on `main`. The former `nasem-prototype-update` worktree is retired. The deck has 31 slides: 17 main slides within 10 minutes, plus fourteen backups. The September presentation is unchanged.

Build with `python3 prompts/2026-11-17-nasem/build_presentation.py`. Run `node scripts/presentations/render_nasem_prototype.cjs` to check frozen metrics, definitions, offline assets, desktop/mobile layout, navigation and print bounds, and export the PDF. The renderer uses local Chrome and Playwright; set `NASEM_PLAYWRIGHT_ROOT` if necessary. Screenshots go to ignored `tmp/nasem-preview/`.

Slides 5–6 show community context and demographics. Slide 7 defines mixed-source fit labels, explains varying access to testing tools, and shows Nov 13 record counts/proportions from `fit-evidence-source-counts.json`. Slide 8 shows mask coverage from the same Nov 13 public snapshot as slide 7. The balanced pass-rate comparison has moved to appendix slide 28. Slide 9 retains the separate 49-person nose-feature experiment, including NPV; slide 10 shows the seven-person test-weighted pipeline comparison. The equivalent equal-person evidence is retained but its slide remains removed. Prototype slides 11–13 retain actual raw/smoothed neck-inclusive headforms, landmarks and caliper checks. The unresolved bifold discrepancy remains omitted.

Appendix slides 21–24 cover 49-person top-k results, traditional predictors, perimeter coefficients and the traditional/PCA feature expansion. Slide 25 revisits the historical N99-to-N95 conversion scatter with a Bayesian censored log-linear trend. Slide 26 shows the conversion equations and MaskNerd spreadsheet credit; slide 27 describes seal-check questionnaire/label rules; slide 28 shows balanced pass rates; slide 29 walks through landmark / curve projection; slide 30 reports paired bootstrap intervals; slide 31 contains sources. See the deck README and speaker notes for methods and limitations.

`analyze_n95_conversion.py` extracts the saved notebook aggregate table, excludes all mask aggregates containing assigned score-1 observations, fits four-chain Metropolis with measured-ceiling censoring, and writes anonymous frozen evidence and standalone SVG/PNG. The plot's prediction means N99-plus-filtration conversion, not a recommender output. Priors, sampling diagnostics and source hashes are in `n95-conversion-evidence.json`; detailed caveats and rebuild commands are in `fit-outcome-methods.txt`. Run `scripts/tests/test_n95_conversion_analysis.py` in the local scientific environment for extraction, censor-likelihood and synthetic recovery checks.

`paired-measurement-evidence.json`, `recommender-evidence.json` and `prototype-evidence.json` freeze the other evidence. Participant-level inputs, source captures and audit predictions remain private. The fit illustration is AI generated and is not fit-test evidence.

To refresh prototype source images, set `NASEM_SOURCE_ROOT` to the checkout containing `.private-webcam-runs` and run the renderer with `--capture-sources`, then rebuild the deck. Source annotations and reconstructions are not modified. No deployment is performed.

The seal-check appendix follows the exact backend evaluation order: sizing failures precede missing-answer checks, and missing sizing precedes the air-movement failure. Questionnaire pass and incomplete both map to NULL, never a positive label. Negative-pressure responses are not read by that service.

Slide 6 shows demographic counts and one-decimal percentages using all 55 participants as each column’s denominator. The renderer checks every displayed count/proportion against the October 29 aggregate snapshot.

Slide 5 states 55 unique users from the October 29 demographic snapshot. Slide 6 is titled “Demographic breakdown.” Slide 7 states 1,157 analyzed fit tests and 769 unique user–mask pairs from the separate, dated November 13 public snapshot. The frozen source-count evidence includes these pair/user totals; the renderer verifies their display.

Slide 7 pairs its source-count table with four original onboarding photographs. `fit-testing-photo-sources.json` records URLs and file hashes; local assets are embedded, with descriptive alt text, for offline presentation/PDF. The renderer verifies all four captions/images and responsive layout.

`build_pass_rate_evidence.rb` uses the actual `DashboardPassRatesService` on a private labeled-row export. It freezes only aggregates and hashes in `observed-pass-rate-evidence.json`. Appendix slide 28 uses 1,142 local records, separate from the public snapshots. See `observed-pass-rate-methods.txt` for the averaging hierarchy and provenance. The renderer verifies displayed rates against that evidence.

Main slide 8 lists the 30 most-tested mask entries with record counts/shares and global mask/person/pair coverage. It uses `mask-coverage-evidence.json`, matching slide 7’s public-response hash; it does not combine local per-mask participant counts with public test counts.

Slide 8 shows the top 30 mask entries in three columns (ranks 1–10, 11–20 and 21–30), with counts and shares from the same frozen public snapshot.

Slide 9 reports point estimates and pointwise 95% person-cluster percentile intervals, from 10,000 paired resamples of 49 people using fixed held-out scores. Appendix slide 30 reports nose-minus-perimeter differences. No retraining; global pre-CV imputation and overlapping training sets remain limitations. Frozen aggregate evidence: recommender-bootstrap-evidence.json.

Appendix slide 30 also gives strict nose-model superiority frequencies over the same 10,000 paired bootstrap samples, with win counts. Recall has 93 ties; ties count as neither wins nor losses. These are bootstrap frequencies, not posterior probabilities or p-values.
