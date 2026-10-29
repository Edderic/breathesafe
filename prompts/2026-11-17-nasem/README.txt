NASEM presentation — November 17, 2026

Local review draft for NPPTL researchers building iOS and Android apps.
Fourteen main slides with a 10-minute speaking budget, followed by two backups.

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
scale, landmarking, and cross-platform development lessons. October 29 top-1/3/5 conditional hit rates are included with
their evaluation population. The quadratic perimeter-difference slide explains
the learned optimum using a schematic with invented coefficients. The 45-second processing figure is presenter-reported,
not a controlled benchmark. The Android pipeline is work in progress.
Slide 4 proposes a separate face-to-mask nose perimeter feature for future
held-out evaluation, motivated by Yu and Griffin's 2024 FFR-specific face
anthropometry study. That study does not validate this particular feature.
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
Slide 10 shows focused views of the current FLAME face generator and 3D landmark
labeling research tools, with the full October 29 screenshots preserved in
assets/android-flame-generator.png and assets/android-landmark-labeling.png.
These are development tools for the Android pipeline, not Android app screens.
The slide's CNN icon marks a planned detector for local facial features in 2D
views; the screenshots do not show a trained detector or its accuracy.
Slides 11 and 12 show the October 29 Breathesafe dashboard snapshot in
data/dashboard-2026-10-29.json: observed fit-test pass rates by strap type and
mask style, plus unique participant counts by demographic category. Rates are
descriptive and test-level; participants may contribute multiple tests.
Small demographic groups may be pooled into "Prefer not to say". Groups with
fewer than 10 tests are omitted from the pass-rate chart. The current October
25 recommender model's top-k figures are also shown on slide 5. These results
are a point-in-time dashboard snapshot, not a prospective validation study.
Slide 13 explains how the project complements NIOSH's facial-measurement work:
KN95 and FFP2/FFP3 options alongside NIOSH-approved respirators, contributed
data that include children and child-sized masks, and GPLv3 code for inspectable
methods. Pediatric prediction accuracy is unvalidated, and this is a scope
comparison rather than a claim about the final features of NIOSH's apps.
Slide 14 is the acknowledgements page. Community contributor names and roles
come from prompts/kanro/2026-10-camera-only-masqfit-proposal.html; the Nukit
fit-testing probe credit is supplied by the presenter. Ten seconds each were
reallocated from the geometry, recommender, and Android segments to keep the
talk at 10:00.
The final slide also invites research funding and work or consulting inquiries,
with the presenter's email and LinkedIn link.

Validation:
Checked all 16 slides at 1366x768 for viewport fit, mobile width at 390px for
horizontal overflow, next-slide navigation, all-slides mode, and print layout.
All print slides fit their 16:9 pages. Visually inspected the dashboard and
complementary-scope slides.

Publication:
No production files, public/ copies, routes, or existing September artifacts changed.
This folder is the review draft; publication is a separate step after review.
