NASEM presentation — November 17, 2026

Canonical deck: prompts/2026-11-17-nasem on main. The former
nasem-prototype-update worktree has been consolidated; edit this deck only.
34 slides: 20 main slides (600 seconds), plus 14 optional backups.

Open presentation.html directly for offline use. presentation.pdf is the PDF
export; speaker-notes.txt contains the timed script. Arrow keys, Home/End,
visible controls and All slides are supported.

Build HTML and notes:
  python3 prompts/2026-11-17-nasem/build_presentation.py
Validate frozen metrics, offline assets, desktop/mobile layouts, navigation and
print bounds, then export PDF:
  node scripts/presentations/render_nasem_prototype.cjs
Local Chrome and Playwright required; NASEM_PLAYWRIGHT_ROOT can locate another
installation. Preview images go to ignored tmp/nasem-preview/.

Main slides:
1: Introduction.
2: General-public goal; adults and children, NIOSH-approved and international
   options. Family photo: Flo Mask, via New Atlas (July 27, 2022); source and hash in goal-photo-source.json.
3–4: MasqFit ARKit capture and historical personal recommendations.
5: Convenience-sample community context: 55 unique users in the October 29
   demographic snapshot; overlapping, unquantified community groups.
6: Demographic breakdown (October 29 snapshot): count and percentage of all
   55 participants, including privacy-pooled/nonresponse groups.
7: Fit-label definitions and varying access to tools: direct N95, N99-derived,
   qualitative and seal checks. Nov 13 snapshot: 1,157 fit tests and 769 unique
   user-mask pairs, with counts and
   record shares; these do not describe participant access rates.
8: Mask coverage: 30 most-tested entries, counts and shares; 77 entries,
   1,157 records, 57 people and 769 user-mask pairs in the same Nov 13 public
   snapshot as slide 7. Counts include repeat tests and mixed evidence sources.
9: The 49-person mixed-input perimeter vs added nose-deviation experiment,
   with the a/b/c family-style decomposition, curvature, peak and baseline explained.
   NPV 85.7% vs 86.6%, fixed 50% cutoff, mean of three initializations.
   Measured-only training did not reproduce the gain; imputation predates CV.
10: Seven paired people: production ARKit vs traditional dimensions vs PCA-3.
    Test-weighted, 421 observations, train six/test one; two supply 70.3%.
11: Simplified traditional/PCA feature sets and child false-positive rates vs ARKit.
12: Fixed-range traditional/PCA sensitivity comparison with full-refit bootstrap.
13–15: Neck-inclusive photogrammetry, attached landmarks/routes, caliper checks.
16: Proposed pipeline validation plan, drawing on the Blueprint discussion draft.
17: Acknowledgements and contact.
18–20: Capture approaches, one-person ARKit/caliper check, anatomical definitions.

Appendix:
21: Complementary scope alongside NIOSH facial-measurement work.
22: Synthetic-face/CNN development plan, not a working detector.
23: Physical scale and projection.
24: Separate 49-person Top-1/3/5 comparison, including Top-1 tradeoff.
25: Six traditional predictors, mask inputs, preprocessing and fitting recipe.
26: Traditional/PCA linear and squared terms, interactions, unconstrained signs.
27: Historical N99→N95 conversion scatter with censored Bayesian trend and
    distinct 95% credible and predictive intervals. One wearer, 24 mask aggregates;
    12 aggregates containing assigned values excluded. Not a recommender test.
28: N99→N95 conversion equations, implementation adjustments and credit to
    Aaron Collins’s MaskNerd spreadsheet for normal-breathing filtration data.
29: Seal-check questionnaire decision rules: failures, not-a-fail, incomplete
    answers and their asymmetric training-label mapping.
30: Per-test vs equal person–mask-pair rates and equal-family style means.
    Local DB snapshot: 1,142 tests, 756 pairs, 54 people; 25.7% vs 16.8%.
31: Automated landmarking and style-curve projection walkthrough.
32: Paired person-cluster bootstrap differences and method.
33: Fixed engineering ranges, PCA bounding and full-refit bootstrap method.
34: Sources and limitations.

Paired comparison: paired-measurement-evidence.json freezes only aggregates,
feature lists, training recipes, limitations and source hashes. No participant
IDs or individual audit scores. Production ARKit retrains the actual perimeter
quadratic plus shared latent-nose architecture (Adam, 200 epochs, lr .01,
row-weighted BCE) in each fold. Traditional/PCA use L2 logistic regression C=1,
equal-person training weights, six standardized dimensions or three PCs, with
linear/squared geometry terms and mask interactions. Preprocessing fits on six
training people only. No ARKit conversion, imputation or outside training people.
Architectures and training weights differ: this compares pipelines, not an
isolated causal effect of measurement modality. ARKit averages seeds 42/43/44;
traditional/PCA fits are deterministic. All score identical held-out observations.

Test-weighted and equal-person aggregates remain in frozen evidence; the main
talk shows test weighting. Repeat tests inform a face's response but do not add
independent faces. Seven people remain seven people. Precision/recall/NPV/F1 use
50%; log loss uses scores directly. Scores are not validated calibrated
population probabilities. Dates may differ; labels mix sources; repeated
user-mask observations can remain. Three initializations are not confidence
intervals. Equal-person slide remains removed as requested.

recommender-evidence.json freezes the separate 49-person experiment.
prototype-evidence.json retains one-person/one-capture physical-scale evidence
and hashes; assets/prototype holds the actual headform screenshots. Caliper
checks are exploratory, not blinded or repeatability evidence. The unresolved
bifold-perimeter discrepancy remains omitted pending a worn-mask/contact-arc
experiment. No private captures or prediction audit files are copied here.

fit-outcome-methods.txt details label construction and historical plot caveats.
n95-conversion-evidence.json freezes anonymous score pairs, source hashes,
Bayesian priors and diagnostics. scripts/presentations/analyze_n95_conversion.py
rebuilds the SVG/PNG and evidence from saved notebook output without DB access.
The four-chain fit handles measured scores at 200 as right-censored. It does not
model predictor error, filtration uncertainty, correlated tests or selection.
The interval is conditional on this one-person dataset, not population accuracy.

The AI goal illustration and its exact image-generation prompt are in assets/.
No model, service, public/ copy, September deck or deployment is changed by this
presentation build. The main talk remains 600 seconds after the added definition.

fit-evidence-source-counts.json freezes Nov 13 source-category counts and the
public response hash: direct N95 136 (11.8%), N99-derived 150 (13.0%), qualitative
119 (10.3%), seal checks 752 (65.0%). Counts sum to 1,157; rounded shares sum to
100.1%. This snapshot differs from the older, explicitly dated descriptive slides
and from both CV cohorts. The appendix averages sealed ratios, not efficiencies;
shows the conditional reference adjustment; and distinguishes the derived mixture
equation from the project-specific factor 2. Source spreadsheet is linked.

Ordering update: former slides 15, 16 and 14 now follow slide 4 in exactly that
order (community context, demographics, observed pass rates). Appendix numbering
and the 600-second main-talk budget are unchanged.

Slides 7 and 8 swapped: fit is defined before observed pass rates are shown.

Slide 7 includes four existing onboarding photographs: respirator under a DIY
bag hood, hood opening, nebulizer at the opening, and 8020A + N95 Companion.
Images are local and embedded for offline use; original public URLs, hashes and
captions are in fit-testing-photo-sources.json. This equipment illustration is
not a complete procedural guide or a claim of protocol compliance.

observed-pass-rate-evidence.json and observed-pass-rate-methods.txt document the
repeat-balanced comparison. The shared DashboardPassRatesService also powers the
new dashboard panel and retains the original per-test statistics. Mixed pair
outcomes are averaged; families are averaged after balancing people and variants.

mask-coverage-evidence.json freezes all public mask-entry counts for slide 8.
The former main pass-rate comparison now appears only in appendix slide 29.
Main talk remains 600 seconds.

Slide 8 shows the top 30 mask entries in three columns (ranks 1–10, 11–20 and 21–30), with counts and shares from the same frozen public snapshot.

Slide 13 includes four original source photos (frontal, oblique and lower camera views), captured with a MacBook Pro camera. Paths and SHA-256 hashes are in prototype-source-photos.json.

Slide 14 shows width chords, the proposed bifold/cup arc (orange), and an under-chin route. Bifold route capture provenance is in prototype-bifold-route-source.json.

Slide 9 reports point estimates and pointwise 95% person-cluster percentile intervals, from 10,000 paired resamples of 49 people with independent classifier retraining (300,000 fits). Appendix slide 32 reports nose-minus-perimeter differences. Original folds, category catalog and prepared inputs stay fixed; global pre-CV imputation is not refitted and overlapping training sets remain limitations. Frozen aggregate evidence: recommender-bootstrap-evidence.json.

Appendix slide 32 also gives strict nose-model superiority frequencies over the same 10,000 paired bootstrap samples, with win counts. Ties within 1e-12 count as neither wins nor losses; exact counts and per-metric evaluable denominators are in the evidence JSON. These are bootstrap frequencies, not posterior probabilities or p-values.

Slide 9 sorts held-out metrics by descending strict-win bootstrap frequency and shows that frequency next to the estimates / confidence intervals. Interpretation: lower log loss establishes better probability scoring, not calibration alone; higher precision means a higher positive-label fraction among predicted fits. All five paired 95% difference intervals include zero after classifier refitting. Nose strict-win frequencies: log loss 86.41%, precision 84.71%, F1 60.03%, NPV 50.64%, recall 35.66%.

Slide 10 highlights a confirmed child-face extrapolation case: the traditional/PCA models trained on six larger faces. Production deviation-based ARKit made fewer false positives in that fold. This is consistent with a useful mismatch-model inductive bias, not proof of general robustness; architecture and weighting differ. The child fold has no positive labels, so it cannot establish child-specific recall. No participant identity is displayed.

Slide 10 shows seven random study UUID prefixes, approximate 2026 age bands, broad gender groups, race/ethnicity and exact held-out test/positive/negative counts. The held-out young-child case is highlighted in amber and marked with a star. Names, database IDs, exact birth years and the UUID identity lookup are excluded. These demographics are not predictors. The mismatch-model rationale is explained without claiming confirmed generalization to unseen larger faces.

Slide 16 summarizes the Blueprint Biosecurity November 9 discussion draft: freeze the automated pipeline, complete a 20-adult pilot within a 120-adult geometry benchmark (60 development / 60 untouched test), then a conditional 60-separate-adult prospective fit pilot. Targets are provisional; pediatric validation is separately scoped. Source hashes are in blueprint-validation-plan-source.json. Main-talk time remains 10 minutes by shortening slides 18–20 by 10 seconds each.

Slide 12 compares fixed-range-scaled traditional/PCA models with production ARKit. It reports original-cohort metrics plus strict-best counts/frequencies from full-refit participant bootstrap; 10,000 draws were attempted, 5,588 supported every PCA-3 fold, and 4,412 were explicitly unevaluable. Appendix slide 33 lists the exact provisional ranges and protocol. Frequencies condition on the paired-evaluable denominator, not all 10,000 attempts. Full report: fixed-range-bootstrap-evidence.json and fixed-range-bootstrap-methods.md.

Slide 11 compares linear, squared, shared-perimeter and full-category interaction recipes. Shaded rows identify highest F1 within Traditional/PCA; teal metric cells identify global best values. Child FPR uses 130 negative tests: ARKit 4.36% (5, 6, 6 false positives across seeds), Traditional 60.0–63.8%, PCA 49.2–56.2%. One child case, exploratory point estimates, no new bootstrap intervals. Sources: simple-fixed-range-comparison.json, child-false-positive-evidence.json and arkit-parameter-counts.json.
