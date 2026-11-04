# BRE-15 local development comparison — 2026-11-04

Retain the 10-second default. This bounded, consented local comparison did not
establish a consistent visible benefit from extending the 60-frame sweep to
20 or 30 seconds. It does not establish that the durations are equivalent.

## Method and recorded exceptions

One participant completed two sweeps at each duration, in the order
10/20/30/30/20/10 seconds, each with a separate held-out frontal photo. All six
trials contain 61 native, unmirrored 1920 × 1080 images and approved masks.
All six timing records identify one continuous 60-frame sequence. No frames were
automatically excluded. Original image/mask hashes were verified and rescored
with `webcam_capture_quality_v1`.

The first 10-second trial was restored from its original export after the live
session was reused for an extra 20-second sweep. The extra sweep's export is
preserved separately; the fresh-session 20-second trial is repeat 1 in this table.
This selection was recorded before reconstruction results were available.

The same pinned COLMAP 4.2.1 / OpenMVS 2.4.0 CPU pipeline, temporal matching
window, shared SIMPLE_RADIAL model and meshing settings were used for all trials.
Normalized reconstruction-command fingerprints match. The held-out photo was
registered after meshing, without changing fixed reconstruction geometry.
Hole filling and geometry smoothing were disabled. Full meshes are retained.

Head size/framing varied between trials; camera-to-head distance was not
independently fixed or measured. Frontal pose was sometimes reached after the
midpoint. Condition text contains stale timestamps
and duration labels; it is preserved, not silently corrected. Actual sequence
timing determines duration. Manual focus, exposure and white balance are not
exposed by this browser/camera. Matching reported resolution/frame rate cannot
rule out automatic setting changes. Lighting conditions were described by the
participant, not independently measured. Most masks were bulk accepted; sampled
mask edges contain thin fragments near the back of the head/neck.

## Results

| Sweep | Repeat | Median sharpness | Registered views | Processing (s) | Frontal reprojection RMS (px) | Full mesh triangles |
| --- | --- | --- | --- | --- | --- | --- |
| 10s | 1 | 508.3 | 60/60 | 200.6 | 2.57 | 465,960 |
| 10s | 2 | 647.1 | 60/60 | 216.4 | 3.39 | 554,793 |
| 20s | 1 | 563.7 | 60/60 | 208.9 | 1.83 | 532,359 |
| 20s | 2 | 605.6 | 60/60 | 198.8 | 2.09 | 504,895 |
| 30s | 1 | 805.5 | 60/60 | 230.3 | 3.31 | 633,918 |
| 30s | 2 | 636.4 | 60/60 | 200.7 | 3.14 | 532,375 |

All 366 image/mask pairs passed artifact checks. None of the 360 turn frames
triggered the provisional sharpness/framing thresholds. No reconstruction failed.
All 360 turn images registered. These are screening and reconstruction results,
not validation of the masks, surface coverage or anatomical accuracy.

## Surface inspection and repeatability limits

The private comparison figure shows frontal and 35-degree inspection views of
the bounded analysis meshes, using matched smooth lighting and independently
fitted display framing. Lighting does not change geometry. These orthographic
views are not camera-alignment checks or dimensional comparisons. Analysis
meshes have approximately 18,000 triangles; simplification can contribute to
their appearance. This comparison does not isolate full-mesh versus analysis-mesh
detail loss (BRE-16).

Central face, nose and chin surfaces are represented in the inspection views.
Facial roughness, poorly resolved eye/ear detail and jagged or triangular artifacts
near the lower/outer boundaries remain. Ear regions are represented, but complete
ear and underside coverage is not established by these views. Visible artifacts
vary between repeated captures, without a consistent duration-dependent improvement.

Median image sharpness varies across repeats; it does not improve monotonically
with duration in the second round. Hair/skin texture, masks, framing and camera
automation affect this whole-head metric. Camera reprojection statistics measure
alignment to image observations, not physical surface or landmark error.

No similarity-aligned 3D repeatability measurement, tape calibration, independent
tape check or paired reference scan was collected. Geometry remains unscaled;
no millimeter or ARKit-equivalence claim follows from these results. Retain the
10-second quick workflow. Motion blur has not been demonstrated as the dominant
failure here, so stop-and-hold capture was not added to this experiment.

## Private evidence

Participant images, meshes, original source archives, session selection/provenance,
per-frame quality records and the surface comparison PNG remain under the ignored
`.private-webcam-runs/capture-comparisons/` directory. The detailed report is
`bre15-six-session-comparison.json`; the figure is
`bre15-analysis-surface-comparison.png`. Original condition labels and limitations
remain in the report. No experimental records enter the recommender or ARKit data.
