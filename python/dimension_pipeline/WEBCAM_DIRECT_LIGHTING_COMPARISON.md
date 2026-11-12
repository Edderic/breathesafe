# November 5 direct-light webcam comparison

This small development study compares two direct soft-orange-light captures with
two subsequent iPhone 16 flashlight captures. All four raw reconstructions used
60/60 registered turns, native 1920×1080 images, approximately 20-second sweeps,
the designated held-out frontal, and the same pinned unrefined pipeline. No
provisional capture-quality flags fired; those flags do not validate anatomy.

## Actual lighting and order

The orange light was reported about nine inches from the face, above the camera,
with brightness unknown. The second capture was originally labeled as a planned
phone capture; the participant explicitly corrected it to another orange-light
capture. Its session context was corrected with the previous context retained
in history. Image/mask bytes, cameras and reconstructed results were preserved.

The actual order is **orange / orange / phone / phone**, rather than the initially
planned orange / phone / phone / orange. The first phone capture began about four
hours and 24 minutes after the second orange capture. Phone source placement and
brightness have not been confirmed by the participant; matching the orange setup
was the target, not a verified measurement. Automatic exposure, focus and white
balance are unavailable as controllable/readable values through this camera/browser.
Consequently this is a comparison of recorded practical setups, with condition,
time/order, possible ambient changes, framing and automatic-camera confounders.
It does not isolate light spectrum, device hardware or equal illumination.

Median mask-derived head-height fractions were 0.671 / 0.719 / 0.747 / 0.735 of
image height. Framing/mask extent therefore also varied; this does not by itself
prove a change in physical camera distance.

## Raw comparison

| Capture | Source label | Start (America/New_York) | Median sharpness proxy | Normalized plane RMS | Frontal sparse reprojection RMS (px) | Analysis ray hits / 478 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Orange | 11:34:47 | 750.3 | 0.001585 | 3.158 | 465 |
| 2 | Orange, participant-corrected | 11:41:55 | 1254.7 | 0.001564 | 2.101 | 459 |
| 3 | Phone, planned source | 16:06:15 | 816.5 | 0.001755 | 2.251 | 473 |
| 4 | Phone, planned source | 16:21:10 | 735.1 | 0.001674 | 2.784 | 467 |

Actual sweep durations were 20.0002 / 20.0001 / 19.9993 / 19.9999 seconds. Mean
normalized plane RMS was 0.001574 for orange and 0.001714 for phone labels, an
8.89% increase in the phone-labeled pair. This roughness proxy does not establish
anatomical accuracy or a general causal effect of either light. Definitions and
fixed seeds are in the [depth study](WEBCAM_DEPTH_EXPERIMENTS.md#defined-screening-metrics).

Raw meshes contain 419,055 / 473,942 / 477,879 / 451,087 triangles. Face-connected
component counts are 189 / 146 / 182 / 274 and boundary edges 91 / 118 / 129 / 161;
all are open, with zero counted nonmanifold edges. Full-mesh front/±35° views under
matched renderer controls show grain in every capture, uncertain fine eye/nose/lip
detail and crown/boundary gaps. The phone-labeled meshes have visible jaw/neck
sheets, particularly capture 3. These sheets contribute to the raw-head extent
used for normalization, so the metrics must be interpreted alongside the full mesh.
Neither triangle count, intersection count nor a smoother simplified viewer proves
that anatomy was reconstructed more accurately.

## Matched refinement

The same optional **24 iterations, regularity 0.20** profile is applied independently
to each raw mesh, preserving all originals. The existing versioned `iterations24`
profile fixes image/camera/mask handling, CPU/native tools, step settings and
geometry-operation flags. Hole closing, automatic full-mesh decimation/subdivision
and cosmetic post-smoothing remain disabled. Per-variant bounded analysis topology,
held-out registration/detection and ray attachments are rebuilt without calibration
or annotation transfer. See [refinement methods](WEBCAM_REFINEMENT_EXPERIMENTS.md).

Private native execution reports, input hashes, full meshes and projections are
retained for each capture. The refinement result is assessed against its own raw
mesh; unrelated unscaled reconstructions are not treated as physically aligned.

All four refinements completed and native logs confirm 24 iterations. Each input
mesh copy matches its original raw hash; approved source images/masks and frozen
camera inputs pass hash rechecks. Original raw result/capture/measurement fields
and unrelated sessions are unchanged. The same existing versioned profile was
selected through the bounded subset API, without numeric parameter overrides.

| Capture | Source label | Refined normalized plane RMS | Change vs its raw mesh | Raw proximity | Raw → refined RMS (reconstruction units) | Analysis hits raw → refined | Seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Orange | 0.001240 | −21.74% | 97.08% | 0.021171 | 465 → 465 | 97.4 |
| 2 | Orange | 0.001222 | −21.88% | 99.74% | 0.003940 | 459 → 459 | 115.0 |
| 3 | Phone | 0.001397 | −20.42% | 97.54% | 0.011476 | 473 → 472 | 109.1 |
| 4 | Phone | 0.001278 | −23.64% | 99.54% | 0.005613 | 467 → 467 | 113.5 |

Mean refined normalized plane RMS is 0.001231 for orange and 0.001337 for phone,
8.64% higher in the phone pair. The approximately 20–24% within-capture reduction
repeats across source labels, but does not resolve substantial facial grain or
establish anatomical fidelity. Matched full-mesh front/side views show modest
grain reduction, persistent crown gaps and jaw/neck sheets, and uncertain fine
eye/nose/lip/ear detail. No full-mesh topology counts change. One analysis ray hit
is lost in capture 3; new QEM analysis topology also affects ray results. Hit
counts and provisional coverage gates do not establish complete anatomy.

Fixed held-out cameras match their raw counterparts and sparse reprojection RMS
remains 3.158 / 2.101 / 2.251 / 2.784 px. This separates unchanged sparse camera
alignment from changes in dense surface geometry, without validating either
surface anatomy or landmark placement. Geometry movement is asymmetric: refined
→raw RMS is 0.003131 / 0.003378 / 0.003900 / 0.004321 reconstruction units. Capture
1's raw→refined sampled maximum is 0.2432 despite a p95 of 0.01087, demonstrating
localized outliers. Samples are not exact displacement bounds. Unscaled distances
must not be read as millimeters or compared as physical errors across captures.

**Recommendation:** retain all raw meshes as baselines; keep the 24-iteration
outputs as further-test artifacts, with no automatic default/measurement promotion.
No clear practical lighting winner is established. Orange has lower roughness
scores in this sample, but time/order, framing, unverified phone placement/brightness
and automatic-camera behavior confound a causal comparison. Inspect masks and
unsupported boundary surfaces before attributing residual errors to lighting.
Native timings include processing, metrics, registration, detection, simplification
and projection; development checks ran concurrently, so these are observed times,
not controlled CPU benchmarks. No outputs enter the recommender or ARKit records.

The updated workflow passes 76 Python tests, 63 JS tests, the preview production
build, viewer regression tests and all four live raw/refined browser inspections.
The profile-selection tests cover rejected empty/duplicate/unknown IDs and numeric
overrides, policy-order execution, subset dispatch and actual isolated raw starts.
Existing cancellation, recovery, calibration isolation and export/reload tests remain
passing. All four actual study archives are checked through temporary private reloads
for capture/context history, geometry/projection provenance and raw/refined inspection.

## Limits and private evidence

There are only two captures per label, one participant and no calibrated tape check
or paired reference scan. A lighting winner or validated anatomical accuracy cannot
be inferred from these four captures. Findings are development screening evidence;
no changes enter the recommender or ARKit records.

Source captures remain in the ignored private run directory. Per-capture baseline
JSON, protocol/source corrections, full-resolution screenshots and pre-refinement
snapshots are under `capture-comparisons/bre18-direct-light-20261105/`. Participant
assets are not committed or published.
