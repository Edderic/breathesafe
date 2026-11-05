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
