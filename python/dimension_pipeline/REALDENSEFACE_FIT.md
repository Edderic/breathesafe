# Local dense-prior FLAME surface and measurement comparison

This experiment converts the cached RealDenseFace ViT-S predictions into a
neutral FLAME Open surface using SciPy on CPU. It does not require CUDA or cloud
resources. It is a separate experimental optimizer, not a port validated against
the official RealDenseFace CUDA solver.

## Fitting

```bash
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 \
  tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.realdenseface_fit \
  --model ~/Downloads/FLAME2023Open.zip \
  --predictions .private-webcam-runs/realdenseface-local/c79e26de-mps-multiphoto \
  --assets tmp/realdenseface-flame-assets.npz \
  --baseline-report .private-webcam-runs/flame-fits/c79e26de-direct-photo-100-prior100/report.json \
  --out .private-webcam-runs/flame-fits/NEW-dense-prior-fit \
  --components 100 --depth-weight 2 --prior 10000
```

The input predictions must match the hashes and nine training slots of the
existing photo baseline. Four validation photos never enter shared shape or
focal fitting. The direct-photo result initializes the identity and cameras;
there is no reconstructed-surface target. The resulting `flame-dense.ply`
retains all 5,023 original FLAME vertex indices and 9,976 triangles.

One shared shape and focal length are optimized with a rigid camera per photo.
Expressions and articulated poses remain zero, as in the direct-photo baseline.
The objective has:

- Dense image correspondences on the published key-region vertex subset.
- Camera-z depth relative to FLAME's neck joint, index 1. Translation cancels;
  this is not camera-distance depth and has no additional fitted depth offset.
- Published uncertainty weighting `.018 * exp(-.5 * log_variance)`.
- A quadratic shape prior and coefficient bounds ±3. Dense, correlated samples
  need stronger regularization than the sparse 105-landmark baseline.

Both data blocks are multiplied by native image width; image coordinates are
normalized by their own image axis. The depth-weight parameter controls the
relative contribution of model-native neck-relative depth. Soft-L1 applies to
data; the coefficient prior remains quadratic. Analytic projection and shape
Jacobians are used, with a small finite difference for the relative-depth
rotation derivative. SciPy trust-region least squares uses sparse LSMR.

CPU ray/triangle intersections reject self-occluded vertices and back-facing
normals. Visibility is recomputed between three outer rounds and frozen during
each solve. This is not upstream predicted-depth raster visibility filtering.
An otherwise matched `--depth-weight 0` run isolates the influence of depth.
The cost values between depth settings are different objectives; do not rank
anatomical accuracy by their raw costs.

The Open release has the same topology as the released prediction assets, but
its basis can differ from the FLAME model used for network training. Eye, mouth,
expression, crop and camera biases can still influence inferred identity.
Normal reversals relative to neutral, degeneracies, active coefficient bounds,
optimizer stops and runtime are reported. A normal-direction change alone does
not prove triangle inversion; self-intersections are not checked.

## Comparison and measurements

```bash
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 \
  tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.realdenseface_compare \
  --baseline .private-webcam-runs/flame-fits/c79e26de-direct-photo-100-prior100 \
  --dense /path/to/depth-2-fit /path/to/depth-0-fit \
  --measurements ~/Downloads/flame-direct-c79e26de178a434aa3f20682fdb087ed-100-style-specific.json \
  --embedding ~/Downloads/mediapipe_landmark_embedding/mediapipe_landmark_embedding.npz \
  --out .private-webcam-runs/flame-fits/NEW-dense-comparison
```

Open the resulting `comparison.html` locally. Both meshes share orientation,
lighting, framing and a common model-native coordinate system; their sizes are
not independently normalized for display. Select the depth ablation, rotate
either canvas, and use profile/from-below views. Draft guide overlays are not
depth-tested. The viewer includes native mesh and report downloads.

The earlier named-point attachments and full bifold/trifold perimeter controls
are reused only after verifying model, topology and session. They remain
**pending review on each surface**; prior review/scale decisions are not
transferred. The established local JS surface-route implementation recomputes
arcs and chord lengths on each new mesh, including explicit edge fallbacks.
There is no arc-length fitting term: saved guide lengths are not targets.
The calibration route and independent check route use surface smoothing;
reported lengths therefore need not equal older mesh-edge-only exports.

Six measurements are displayed: bitragion–subnasale and bitragion–menton arcs,
subnasale–pronasale and sellion–pronasale chords, and closed bifold/trifold
perimeters. A chord is a straight 3D distance; it is not a surface arc or a
camera-axis projection. Neck/ear portions remain heavily influenced by the
model prior and need particular review.

### Millimeter conversion

Before a scale is supplied, the lengths and meshes are explicitly uncalibrated.
The conversion is simply:

```
length_mm = length_native * millimeters_per_native_unit
```

Enter independent scale factors directly, or enter a measured
bitragion–subnasale tape arc. The latter calculates **a separate factor for each
surface** as `tape_mm / predicted_arc_native`. One reading in this comparison is
an exploratory conversion, not an accepted clinical calibration. The existing
annotation editor's three-reading/review procedure remains separate.

The viewer exports a measurement JSON and an ASCII PLY scaled uniformly into
millimeters for either model. Negative, zero, blank and non-finite factors cannot
produce a scaled mesh. Downloading a comparison without a scale retains null
millimeter lengths. These operations do not change native fits or original
annotation files. Scaling cannot correct an incorrect nose, jaw or arc route.

With `--embedding`, the report also compares the four validation photos using
fixed identity/focal length and cameras estimated from non-nose MediaPipe
landmarks. These residuals describe agreement with a different detector, not
physical measurement accuracy. They are validation diagnostics, not a new
independent test set after hyperparameter selection.

## Verification

```bash
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m unittest dimension_pipeline.tests.test_realdenseface_fit
node scripts/tests/realdenseface_compare_smoke.cjs /path/to/comparison-folder
```

The derivative test checks shape, camera and focal Jacobians against central
finite differences; other tests verify neck-relative translation invariance and
occlusion rejection. The browser test checks shared views, guide measurements,
scale derivation, JSON export, actual scaled PLY coordinates, invalid input
rejection, and absence of network requests.

## Initial session result

For session `c79e26de178a434aa3f20682fdb087ed`, the review candidate uses
100 shape components, depth weight 2 and prior 10000; the alternative uses the
same settings with depth disabled. Each ended with a relative-cost termination
condition after earlier rounds sometimes exhausted their evaluation budgets.
That stop is not a global-optimum certificate. The depth-enabled fit took about
142 seconds in the concurrent local trial, has no degenerate triangles or
coefficients at their bounds, and one normal-direction change on ear triangle
751 relative to neutral. The zero-depth fit has two such changes. No anatomical
accuracy claim follows from these diagnostics.

Matched four-photo validation detector RMS was 4.85 px for the direct-photo
baseline, 5.77 px for dense+depth, and 5.90 px for dense without depth. The
corresponding nose-subset RMS values were 4.80, 6.73 and 7.23 px. This diagnostic
favors the sparse detector fit when measured against that same detector; it
does not establish which method gives more accurate physical dimensions.

The review is `.private-webcam-runs/flame-fits/c79e26de-dense-vs-direct-photo/comparison.html`.
All lengths are initially uncalibrated; no real tape reading was supplied or
saved. Weaker-prior diagnostic runs remain separate and are not the initial
viewer candidates. These hyperparameters are exploratory for one session,
not validated defaults for other faces or cameras.
