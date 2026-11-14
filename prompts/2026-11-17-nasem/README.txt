NASEM presentation — November 17, 2026

Canonical deck: prompts/2026-11-17-nasem on main. The former
nasem-prototype-update worktree has been consolidated; edit this deck only.
31 slides: 17 main slides (600 seconds), plus 14 optional backups.

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
   options. Generated fit illustration is not measured leakage evidence.
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
9: The 49-person mixed-input perimeter vs added nose-deviation experiment.
   NPV 85.7% vs 86.6%, fixed 50% cutoff, mean of three initializations.
   Measured-only training did not reproduce the gain; imputation predates CV.
10: Seven paired people: production ARKit vs traditional dimensions vs PCA-3.
    Test-weighted, 421 observations, train six/test one; two supply 70.3%.
11–13: Neck-inclusive photogrammetry, attached landmarks/routes, caliper checks.
14: Acknowledgements and contact.
15–17: Capture approaches, one-person ARKit/caliper check, anatomical definitions.

Appendix:
18: Complementary scope alongside NIOSH facial-measurement work.
19: Synthetic-face/CNN development plan, not a working detector.
20: Physical scale and projection.
21: Separate 49-person Top-1/3/5 comparison, including Top-1 tradeoff.
22: Six traditional predictors, mask inputs, preprocessing and fitting recipe.
23: Learned perimeter coefficients: family/style decomposition, curvature, peak.
24: Traditional/PCA linear and squared terms, interactions, unconstrained signs.
25: Historical N99→N95 conversion scatter with censored Bayesian trend and
    distinct 95% credible and predictive intervals. One wearer, 24 mask aggregates;
    12 aggregates containing assigned values excluded. Not a recommender test.
26: N99→N95 conversion equations, implementation adjustments and credit to
    Aaron Collins’s MaskNerd spreadsheet for normal-breathing filtration data.
27: Seal-check questionnaire decision rules: failures, not-a-fail, incomplete
    answers and their asymmetric training-label mapping.
28: Per-test vs equal person–mask-pair rates and equal-family style means.
    Local DB snapshot: 1,142 tests, 756 pairs, 54 people; 25.7% vs 16.8%.
29: Automated landmarking and style-curve projection walkthrough.
30: Paired person-cluster bootstrap differences and method.
31: Sources and limitations.

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
The former main pass-rate comparison now appears only in appendix slide 28.
Main talk remains 600 seconds.

Slide 8 shows the top 30 mask entries in three columns (ranks 1–10, 11–20 and 21–30), with counts and shares from the same frozen public snapshot.

Slide 11 includes four original source photos (frontal, oblique and lower camera views), captured with a MacBook Pro camera. Paths and SHA-256 hashes are in prototype-source-photos.json.

Slide 12 shows width chords, the proposed bifold/cup arc (orange), and an under-chin route. Bifold route capture provenance is in prototype-bifold-route-source.json.

Slide 9 reports point estimates and pointwise 95% person-cluster percentile intervals, from 10,000 paired resamples of 49 people using fixed held-out scores. Appendix slide 30 reports nose-minus-perimeter differences. No retraining; global pre-CV imputation and overlapping training sets remain limitations. Frozen aggregate evidence: recommender-bootstrap-evidence.json.

Appendix slide 30 also gives strict nose-model superiority frequencies over the same 10,000 paired bootstrap samples, with win counts. Recall has 93 ties; ties count as neither wins nor losses. These are bootstrap frequencies, not posterior probabilities or p-values.

Slide 9 sorts held-out metrics by descending strict-win bootstrap frequency and shows that frequency next to the estimates / confidence intervals. Interpretation: lower log loss establishes better probability scoring, not calibration alone; higher precision means a higher positive-label fraction among predicted fits. Recall improvement remains uncertain.
