# BRE-18 image-guided refinement

The November 5 screening trial reduced local-plane roughness, but did not resolve
the visible facial grain or establish better anatomy. Keep the raw pipeline as the
default. Weight 0.20 is a candidate for further testing; 0.50 trades more movement
for lower roughness, with a lost ray hit on the second capture. No variant is
promoted to a calibrated measurement surface.

## Run and inspect

Run `python3 scripts/setup_webcam_native.py` to link the optional pinned OpenMVS
2.4.0 `RefineMesh` from the same checksum-verified arm64 archive. Existing raw
reconstruction diagnostics do not require this optional tool. Its version and
architecture are checked before refinement; `/diagnostics/refinement` exposes
the expanded diagnostics through the existing exact-origin/Host protections.

Resume a locally reconstructed session with 61 approved captures and select
**Run image refinement experiments**. The original reconstruction work directory,
turn images, approved masks, camera models and feature database must exist. A ZIP
can reload completed variants and projections for inspection; it does not contain
the original feature database needed to rerun held-out registration. Missing local
prerequisites fail explicitly. There is no synthetic fallback.

The three profiles in `refinement_policy.json` (`webcam_image_refinement_v1`)
vary only regularity weight: 0.05, 0.20 and 0.50. Fixed settings use native image
resolution, up to four neighboring views, one scale, eight optimization iterations,
initial gradient step 0.5 with native 0.98 decay, rigidity/elasticity ratio 0.9,
and four CPU threads. The CLI encodes iterations and step in `--gradient-step
8.05`. This is a bounded screening trial, not a convergence study.

Automatic decimation, edge-size adjustment, face subdivision, planar-vertex
removal and hole closing are explicitly disabled. There is no cosmetic smoothing
after optimization. **Regularization is part of refinement** and can smooth away
real detail. Native behavior was checked against the pinned
[CLI](https://github.com/cdcseacave/openMVS/blob/v2.4.0/apps/RefineMesh/RefineMesh.cpp)
and [optimizer](https://github.com/cdcseacave/openMVS/blob/v2.4.0/libs/MVS/SceneRefine.cpp).

The isolated scene contains only registered reconstruction turns (at least 54 of
60), never the designated frontal image. Approved images/masks are hash-checked;
undistorted binary masks are reapplied without resizing, compositing excluded
pixels black. RefineMesh 2.4.0 has no semantic-mask CLI: black compositing does
**not** exclude mask-boundary gradients from its objective. That limitation is
recorded in each input manifest and must be considered near the neck/ears.

Original full-mesh bytes, captures, cameras, annotations and calibration remain
unchanged. Each variant uses its own mesh copy and directory, command log, input
manifest, binary hashes, settings, timing and geometry metrics. Cancellation uses
the existing native process-group termination. Completed variants survive;
unfinished jobs become interrupted on restart. Starting another trial creates
fresh isolated work rather than consuming a partial native output. Only one
reconstruction/experiment runs at a time.

Open **Compare full and analysis meshes**, select a refined variant, and use the
original full mesh as reference. The same selector retains BRE-17 filtered variants
for comparison. Both inspection views share framing, rotation, lighting and units.
Refinement comparisons use unscaled original coordinates even if the original
session has tape calibration. The original calibrated annotation view keeps its
own frame in that case. No old tape scale is silently applied to a refined mesh.

Each refined full mesh gets a fresh bounded analysis topology (QEM target 18,000
faces), sampled simplification deviation and order-sensitive mesh ID. After final
geometry is fixed, the frontal is registered against the immutable original sparse
model with fixed intrinsics and no bundle adjustment. Camera poses/intrinsics and
sparse point positions are checked for changes. The original held-out image is
undistorted, the pinned CPU MediaPipe detector reruns, and nearest-ray intersections
are rebuilt on the variant's analysis topology. Raw predictions, missed statuses,
barycentric attachments, detector/camera provenance and all-pending decisions are
stored separately. No original routes, decisions or calibration are transferred.
**Download fresh projections** exports this per-variant record. Current variant
inspection is read-only; it does not offer variant route tracing or point approval.

The versioned session ZIP includes variant geometry, fresh analysis/projections,
frontal images/cameras, frozen masked turn inputs, settings, logs and hashes.
References/hashes are validated on reload; active experiment bundles are rejected.
The binary upload limit is 2 GB, with the existing 8 GB expanded/20,000-file bounds.
Captures/outputs remain in the ignored private run directory, outside Vite serving.

## Two saved 20-second captures

Both development captures registered 60/60 turns and declare the same comparison
group/conditions and nominal duration. Their image hashes differ. Both labels
say repeat 1, so they are reported as distinct saved captures A and B rather than
assuming the repeat labels are reliable. They are one participant and one setting;
this is a limited stability check, not population validation or paired 3D accuracy.

Metrics use the unchanged BRE-17 area-sampled local-plane, nearest-surface and
proximity definitions; see [definitions](WEBCAM_DEPTH_EXPERIMENTS.md#defined-screening-metrics).
Displacements are in arbitrary reconstruction units. Cross-capture raw coordinates
are not aligned or scaled, so compare normalized effects rather than treating
their absolute coordinate differences as anatomical errors.

| Capture | Regularity | Roughness change vs its raw mesh | Raw proximity | Raw → refined RMS | Refined → raw RMS | Fresh hits / 478 | Seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 0.05 | −1.77% | 99.94% | 0.001912 | 0.001373 | 469 | 67.7 |
| A | 0.20 | −16.11% | 99.66% | 0.004479 | 0.002390 | 469 | 66.0 |
| A | 0.50 | −23.03% | 99.54% | 0.005951 | 0.003395 | 469 | 66.5 |
| B | 0.05 | −10.76% | 99.72% | 0.002891 | 0.001422 | 472 | 73.3 |
| B | 0.20 | −20.59% | 98.18% | 0.007266 | 0.002488 | 472 | 106.3 |
| B | 0.50 | −30.85% | 97.40% | 0.009580 | 0.003441 | 471 | 73.0 |

Times include import, refinement, geometry metrics, fresh registration/detection,
analysis building and projection. Shared input freezing and the original SfM/dense
run are excluded. B's 0.20 trial overlapped a large archive export/browser checks,
so these are observed elapsed times, not controlled CPU benchmarks.

A keeps 266,827 vertices / 532,359 faces / 191 boundary edges; B keeps 317,490 /
633,918 / 136. Face-connected components and boundary counts match their raw
sources; zero counted nonmanifold edges remain. Unchanged topology counts do not
establish complete ears/chin. All variants remain open and retain boundary debris.

Post-refinement fixed-model frontal registration has 741 matched observations,
RMS 1.833 px (A), and 210 observations, RMS 3.308 px (B), for all three settings.
Sparse reprojection measures camera alignment to sparse features, not dense-surface
or anatomical accuracy. Ray hits similarly establish an intersection only.

Front and ±35° inspection shows a consistent reduction of fine grain as regularity
increases, but substantial facial noise, uncertain eye/lip detail and jaw/neck
artifacts remain. Nose shape and visible lateral outlines remain recognizable;
tragion/ear and underside coverage still require manual inspection. Weight 0.50
has greater displacement and loses one additional ray hit in B. The roughness
direction repeats, but its magnitude varies substantially across the two captures.

Recommendations: reject automatic promotion of 0.05 (small/inconsistent benefit)
and 0.50 (larger displacement without verified detail preservation). Keep 0.20 as
**adjust / further test**, with raw reconstruction retained. The next useful test
is controlled diffuse lighting and sharper input images, followed by a longer
0.20 optimization trial with the same detail checks. Do not increase regularity
solely to make the rendering look smoother.

No tape calibration, independent check arc or paired reference scan was available
for either capture. Millimeter accuracy, calibrated-arc stability and ARKit
equivalence are therefore **not measured**. Outputs do not enter the recommender
or existing ARKit records.

## Verification and private evidence

Python tests cover mask compositing/dimensions, fixed safe profiles, optional tool
diagnostics, held-out exclusion, fixed-geometry registration, analytical fresh
ray intersections/misses, calibration/attachment isolation, native failure,
cancellation, single-job operation, interrupted recovery and hashed export/reload.
All 72 Python tests, 63 JS tests, the production preview build and viewer regression checks pass. Live Chrome checks inspect all
six raw/refined comparisons in front/side views, verify fresh projection downloads
and confirm inspection never edits original annotations.

The actual A archive (1,019,046,815 bytes) was uploaded through a temporary loopback
HTTP server and restored into a temporary private Store: 194 experiment artifacts,
three refined meshes/projections, unchanged raw result and valid comparisons.
The temporary reload copy was removed afterward; no extra session was added to
the user's processor. Private run manifests, execution reports, numerical review,
front/side screenshots, original snapshots and the archive remain under
`.private-webcam-runs/`. Source captures are not committed.

## Iteration-budget comparison

**Run 8 vs 24 iterations · weight 0.20** selects the separate versioned suite
`webcam_image_refinement_iterations_v1` in `refinement_iterations_policy.json`.
The API accepts `{"suite":"iterations"}`; arbitrary numeric overrides are rejected.
The original regularity suite and historical records remain unchanged/loadable.
Both suites share existing progress, cancellation, recovery, comparison,
uncalibrated variant projection and artifact export/reload behavior.

Both iteration trials start independently from the original full mesh. The
native CLI differs only in `--gradient-step 8.05` versus `24.05`, encoding eight
or 24 iterations with initial step 0.5. Regularity weight remains 0.20; step decay
0.98, one scale, four neighboring views, four CPU threads, image/mask/camera
inputs and geometry-operation flags are held fixed. Input manifests, profile
versions and effective optimization settings are recorded per variant.

The pinned optimizer switches rigidity/elasticity to 1 after its integer
70-percent-of-budget cutoff: after iteration index 5 for eight iterations,
after index 16 for 24. Consequently, the first eight vertex updates need not
match. This compares two native iteration budgets, not a continuation of an
eight-iteration trajectory or proof of convergence. Evaluate detail, coverage
and displacement alongside roughness. A smoother appearance alone does not
justify promotion.

The first two captures in the subsequent
[lighting comparison](WEBCAM_LIGHTING_COMPARISON.md) supply two saved input sets
for this test. No additional captures or calibration transfer are required.

### November 5 iteration results

Both saved room-lighting captures completed the two budgets with 60/60 registered
turn inputs and identical per-capture input-manifest hashes. Native command logs
record the actual iteration counts. Both start mesh copies match their raw PLY
hashes. Source captures, camera/measurement fields and unrelated sessions remain
unchanged. Both variants receive fresh held-out registration/detection and
analysis-topology-specific projections with pending decisions and no calibration.

| Capture | Iterations | Roughness change vs raw | Raw proximity | Raw → refined RMS (reconstruction units) | Fresh hits / 478 | Seconds |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 8 | −13.68% | 96.90% | 0.020851 | 469 | 68.9 |
| 1 | 24 | −26.15% | 95.04% | 0.035675 | 469 | 119.2 |
| 2 | 8 | −12.02% | 99.02% | 0.005965 | 470 | 71.0 |
| 2 | 24 | −24.49% | 98.34% | 0.008091 | 470 | 127.6 |

Relative to eight iterations, 24 lowers the plane-residual roughness metric by
14.45% and 14.17%, at 1.73× and 1.80× observed elapsed time. Timings include native
import/refinement and geometry/registration/detection/analysis/projection, not
original reconstruction or shared input freezing. Development checks ran during
processing, so these are observed timings rather than controlled CPU benchmarks.

The direct comparison now supports any artifact-validated completed variant as
the reference. Select **24 iterations · regularity 0.20** as comparison variant
and **8 iterations · regularity 0.20** as reference. Both full meshes use one
shared frame and rendering controls, with no alignment fit. Any comparison
containing a refined source **or reference** uses unscaled reconstruction units
and the original unscaled camera, even when the base session was calibrated.

At 5,000 area-weighted samples per direction, direct 24→8 RMS is 0.002064 / 0.002225
and 8→24 RMS is 0.008330 / 0.003130 for captures 1 / 2. These arbitrary units
cannot be compared as physical errors across captures. The first capture's
8→24 sampled maximum is 0.2576, showing localized movement outliers despite low
typical disagreement; sampled maxima are not exact bounds. Geometry movement and
raw proximity both warrant inspection rather than inferring accuracy from lower
roughness. Full-mesh face/component/boundary counts remain those of each raw mesh;
that does not establish complete anatomy.

Direct front/±35° full-mesh inspection shows a modest reduction of grain at 24,
with substantial facial grain, uncertain fine eye/lip/ear detail, crown gaps and
boundary debris still present. Nose/lip and lateral outlines remain recognizable;
their anatomical fidelity is not independently established. The raw jaw sheet in
capture 2 persists rather than being repaired. Both budgets have identical fixed
frontal camera poses/intrinsics within each capture; sparse reprojection RMS is
3.596 px and 2.638 px respectively, unchanged by the budget. Unchanged hit counts
do not imply unchanged landmark positions: matched analysis-ray point disagreement
RMS is 0.009852 / 0.006759 reconstruction units, including both geometry change and
fresh QEM topology effects. None of these values measures anatomical accuracy.

Retain eight iterations as an experimental screening control. Keep 24 as
**adjust / further test**, not an automatic default or calibrated measurement
surface. The consistent numerical benefit justifies considering 24 in the later
direct-light comparison; additional iterations alone have not resolved the noise.
Independent tape checks and a paired reference remain unavailable.

Validation passed: 76 Python tests, 63 JS tests, preview build, viewer error/scale
regressions, all four live variant inspections and both direct budget comparisons.
Both actual iteration-session ZIPs reloaded into temporary private Stores with
matching raw/capture fields, new-profile provenance, fresh projections and direct
comparison support. Private execution reports, archives, review notes and screenshots
remain under the lighting study's `iterations-study/` and private comparison folder.
