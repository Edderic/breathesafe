NASEM presentation — November 17, 2026

Review draft for NPPTL researchers building iOS and Android apps.
Updated November 12: 23 slides, comprising 16 main slides within the same
10-minute speaking budget and seven optional backups.

Open presentation.html directly for offline use, or start a local preview:
  python3 -m http.server 8765 --bind 127.0.0.1 --directory prompts/2026-11-17-nasem
  http://127.0.0.1:8765/presentation.html

Arrow keys, Home/End, visible controls and All slides are supported.
presentation.pdf is the PDF export; speaker-notes.txt contains the timed script.

Rebuild HTML and notes:
  python3 prompts/2026-11-17-nasem/build_presentation.py
Validate layout, frozen metrics, navigation and print bounds; export PDF:
  node scripts/presentations/render_nasem_prototype.cjs
The renderer uses local Chrome and Playwright. Set NASEM_PLAYWRIGHT_ROOT if its
installation lives in another repository. Screenshots go to tmp/nasem-preview/.

Main slides:
1: Introduction.
2: Project goal: help the general public find better-fitting respirators. Our
intended scope includes adults and children, NIOSH-approved and international
options (N95, KN95, FFP2/FFP3). Published NIOSH app targets emphasize NIOSH-approved
respirators and worker fit panels. This does not assert that NIOSH excludes all
children or describe unannounced final app features. Our pediatric prediction
accuracy still needs validation. A generated illustration contrasts a loose blue
surgical mask with a closer-fitting respirator; it is not measured leakage evidence.
Sources: CDC/NIOSH 2024-107 app targets, CDC/NIOSH 2021 ASTM fit-panel description,
and CDC Community Respirators and Masks. Links appear in the slide footer.
3–4: MasqFit measurement capture and an October 29 personal recommendation
screenshot. The screenshot uses the October 25 model; its scores are not presented
as calibrated probabilities or new held-out results.
5: The 49-person mixed-input perimeter-only vs. added nose-deviation experiment.
Frozen aggregates and private-report hashes: recommender-evidence.json. Fixed
50% cutoff; three initializations on identical five user-grouped folds. The
measured-only experiment did not reproduce the gain. Global imputation was not
refit within folds. The NPV row uses TN/(TN+FN), the negative-label fraction among predicted
negatives; it is 85.7% vs. 86.6% averaged across the three initializations.
This is separate from the paired comparison on slide 6.
6: Test-weighted results for production ARKit vs direct traditional dimensions
and PCA-3. Every held-out test counts equally. Seven complete paired people,
421 observations, train six/test one. Two people supplied 296/421 tests (70.3%).
NPV is included alongside precision, recall, F1 and log loss, using the same test
weights and fixed 50% cutoff; ratios are averaged across initializations.
7–9: Camera approach comparison, exploratory ARKit/caliper self-check, and the
need to map mesh vertices to anatomical definitions. The self-check is one person;
the cited ARKit eye-to-phone study does not validate these facial paths.
10–12: Working photogrammetry prototype: raw/smoothed neck-inclusive digital
headforms, attached landmarks and routes, and three independent caliper checks
at tape-derived scale. One person/one capture; endpoint and method choices were
inspected during development. These are not blinded or repeatability results.
The unresolved bifold-perimeter discrepancy remains omitted. A worn-mask capture
and contact-arc tracing experiment remains future work in the speaker notes.
13: October 29 descriptive dashboard pass rates.
14: Convenience-sample community context.
15: Participant demographics.
16: Acknowledgements and research funding/work/consulting contact information.

The former slide 7 (equal-person comparison) was removed at the presenter's
request. Its aggregate data remain in paired-measurement-evidence.json for audit,
but the slide and its timed speaker notes are not included. Freed time is allocated
to explaining NPV on slide 5 and the test-weighted comparison on slide 6.

Backups:
17: Detailed complementary scope alongside NIOSH's facial-measurement work.
Moved out of the main talk because slide 2 now establishes the project goal.
18: Complementary synthetic-face/CNN development tools, not the working Android
app or a trained custom detector.
19: Scale and camera projection details.
20: The separate 49-person Top-1/3/5 perimeter vs nose-deviation comparison,
including the Top-1 decrease. It remains separate from the seven-person result.
21: Q&A predictor details: all six traditional dimensions, shared mask inputs,
direct standardized vs. PCA-3 inputs, regularization, nonlinear interactions,
training-person-only preprocessing and equal-person training weights. This is
project-specific PCA, not the NIOSH PCA panel. The feature list is frozen from
the actual FEATURE_COLUMNS used by the comparison implementation.
22: Learned perimeter-coefficient definitions and interpretation.
23: Sources and boundaries of the claims.

Paired model comparison provenance:
paired-measurement-evidence.json contains only frozen aggregates, model/training
recipes, limitations and source hashes. No participant IDs or individual scores.
The ARKit arm calls the actual production total-perimeter quadratic plus shared
nose-mismatch training/inference code, retrained on six paired people per fold.
It does not reuse deployed weights. Adam 200 epochs, lr .01, row-weighted BCE.
Traditional/PCA classifiers predict fit directly from six traditional dimensions
or three components, with L2 logistic regression and equal-person training weights.
Scaling/PCA fit only on training people. No imputation or ARKit conversion is used.
Thus architectures and training recipes differ; this is a pipeline comparison,
not an isolated causal measurement-modality experiment. ARKit averages three
initializations on the same folds; traditional/PCA fits are deterministic.

Both evaluation weightings are retained in the frozen aggregate evidence; the
main talk now displays test weighting only for the paired comparison. Test weighting describes the collected
test mix; equal-person weighting limits prolific testers' influence. The geometry
constraint is a useful inductive bias, and repeat tests inform a person's response,
but additional tests on the same face do not add independent faces or prove new-
person generalization. Seven people remain seven independent participants.
Precision/recall/F1 use the fixed 50% cutoff; log loss uses the scores directly.
Latest measurement/test dates may differ, labels mix evidence sources, and repeated
user-mask observations may remain. The models' scores are not validated calibrated
population fit probabilities. Three initializations are not confidence intervals.

The goal illustration is in assets/public-fit-goal-illustration.png. Its exact
built-in image_gen prompt is in assets/public-fit-goal-prompt.txt.

Prototype source views are retained in assets/prototype/ and embedded for offline
use. Frozen single-capture numbers and source hashes are in prototype-evidence.json.
No private source captures or individual prediction audit files are copied here.

Validation:
23 slides checked at 1366x768; mobile width 390px; paired table values and traditional predictor keys checked
against frozen evidence; next/end/home/all-slides navigation; offline assets;
NPV values checked against the frozen evidence; 16:9 print bounds and PDF
export. Main talk remains 600 seconds.

Publication:
This change edits the November review deck. No production routes, public/ copies,
existing September artifacts or deployed models are changed by the deck build.

Community context update: 23 slides, 16 main slides and 7 backups. The new convenience-sample slide precedes the demographic counts. Its groups overlap and are presenter-described, not quantified health-status categories. Main talk remains 600 seconds.

Appendix slide 22 defines the learned perimeter coefficients, family/style decomposition, negative-curvature transform and preferred difference −b/(2a). Sources move to slide 23. Main talk remains 600 seconds.

Canonical deck: prompts/2026-11-17-nasem on main. The nasem-prototype-update worktree is retired; edit and render this deck only. The expanded perimeter logit from its former slide 4 is retained on main slide 5.
