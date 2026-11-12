NASEM presentation — November 17, 2026

Local review draft for NPPTL researchers building iOS and Android apps.
Updated November 12: fifteen main slides with the same 10-minute speaking budget, followed by three backups.

Preview:
  http://127.0.0.1:8765/presentation.html

To restart the local preview from the repository root:
  python3 -m http.server 8765 --bind 127.0.0.1 --directory prompts/2026-11-17-nasem

presentation.html also opens directly in a browser without a server or internet.
Use arrow keys, Home/End, or the visible controls. All slides provides an overview.
presentation.pdf is the local PDF export. speaker-notes.txt contains the timed script.

Rebuild HTML and notes:
  python3 prompts/2026-11-17-nasem/build_presentation.py

To refresh the PDF after rebuilding, open the HTML and choose Print / PDF.
Use background graphics, the CSS landscape page size, and no browser headers/footers.

Scope:
This draft replaces the September planning-meeting narrative with practical capture,
scale, landmarking, and cross-platform development lessons. Slides 4 and 5 now
compare perimeter-only vs. shared-strength nose-deviation models using the November
12 paired local experiment. Slide 4 shows log loss, precision, recall and F1 at a
fixed 50% cutoff; slide 5 shows the Top-1 decrease and Top-3/Top-5 gains. Results
average three initializations on identical five user-grouped folds. There are
1,086 held-out tests from 49 people in mixed measured/imputed training, and 32
positive-label people eligible for the conditional top-k rates. The smaller
measured-only training experiment did not reproduce the gain. Calibration remains
poor; these are exploratory internal results, not prospective validation. No
individual scores or participant IDs are included in recommender-evidence.json;
it retains aggregate numbers, limitations and hashes of the private source reports.
The nose mismatch compares the input face path with a learned effective mask/style
preference, not a physically measured mask nose perimeter. Shared sensitivity is
the new training default; the style-specific variant remains experimental.
The earlier 45-second raw-reconstruction figure is presenter-reported,
not a benchmark of the updated pipeline. The local ordinary-camera prototype works;
the Android experience still needs validation.
Slide 7 shows the presenter's six ARKit-versus-digital-caliper measurements,
rounded from the supplied notebook screenshot. The original comparison image
is preserved in assets/arkit-caliper-self-check.png. This one-person check is
exploratory. A cited 2023 ARKit/TrueDepth study measured eye-to-phone distance
at different angles; it does not establish accuracy for MasqFit's facial paths.
Technical references are linked on the relevant slides and in the source backup.
Slide 2 enlarges the MasqFit capture and measurement screenshots. Slide 3
shows the presenter’s complete October 29 screenshot of the live Breathesafe
recommendations page, scaled to the available presentation height. The original
is preserved in assets/personal-recommendations-hidden-observed-fit.png. Observed Fit is hidden in the captured page, leaving
model scores and mask details visible. The model timestamp shown is October 25.
The percentages are model outputs and are not presented as calibrated probabilities.

Presenter-supplied images show the current MasqFit capture, five aggregates,
recommendations, and a MediaPipe mesh. Originals are preserved in assets/
and embedded in the HTML for offline use. Occluded-point accuracy from one
viewing angle is identified as an open project validation question.
Slide 8 uses the newer MasqFit MediaPipe screenshot in assets/mediapipe-masqfit-demo.png;
the earlier reference image remains in assets/mediapipe-reference.png.
Slides 9–11 now show the working camera prototype: actual raw and Gaussian-smoothed digital headforms with upper-neck coverage, surface-attached landmarks and chord/arc calculations, and three initial caliper comparisons at fixed tape-derived scale. One person, one capture; three physical readings per dimension. Endpoint/method choices were inspected during development, so these are not blinded accuracy or capture-repeatability results. The exploratory bifold-perimeter difference is omitted for now. A worn-mask capture and contact-arc tracing experiment remains future work in the speaker notes.

The former Android synthetic-face/CNN development slide is retained as backup slide 16. It is complementary research rather than the current prototype implementation. Existing pretrained multi-photo correspondences supply the current point proposals. No trained custom detector or Android app validation is claimed. Actual headform views are in assets/prototype/, and the frozen metrics and private-report hashes are in prototype-evidence.json.

Slides 12 and 13 show the October 29 Breathesafe dashboard snapshot in
data/dashboard-2026-10-29.json: observed fit-test pass rates by strap type and
mask style, plus unique participant counts by demographic category. Rates are
descriptive and test-level; participants may contribute multiple tests.
Small demographic groups may be pooled into "Prefer not to say". Groups with
fewer than 10 tests are omitted from the pass-rate chart. Those charts remain an October 29 descriptive snapshot, separate from the new
November 12 recommender experiment on slides 4 and 5. Neither is a prospective validation study.
Slide 14 explains how the project complements NIOSH's facial-measurement work:
KN95 and FFP2/FFP3 options alongside NIOSH-approved respirators, contributed
data that include children and child-sized masks, and GPLv3 code for inspectable
methods. Pediatric prediction accuracy is unvalidated, and this is a scope
comparison rather than a claim about the final features of NIOSH's apps.
Slide 15 is the acknowledgements page. Community contributor names and roles
come from prompts/kanro/2026-10-camera-only-masqfit-proposal.html; the Nukit
fit-testing probe credit is supplied by the presenter. Ten seconds each were
reallocated from the geometry, recommender, and Android segments to keep the
talk at 10:00.
The acknowledgements slide also invites research funding and work or consulting inquiries,
with the presenter's email and LinkedIn link.

Validation:
Checked all 18 slides at 1366x768 for viewport fit, mobile width at 390px for
horizontal overflow, next-slide navigation, all-slides mode, and print layout.
All print slides fit their 16:9 pages. Visually inspected the new prototype and caliper slides as well as the existing dashboard and scope content.
Render/export helper: node scripts/presentations/render_nasem_prototype.cjs (run from the repository root).

Publication:
No production files, public/ copies, routes, or existing September artifacts changed.
This folder is the review draft; publication is a separate step after review.
