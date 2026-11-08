# Direct multi-photo FLAME baseline

This is a separate CPU experiment from the reconstruction-fitting pipeline.
It fits one neutral FLAME Open identity and one rigid camera per training photo
using 105 official FLAME/MediaPipe surface correspondences. It never reads a
reconstructed mesh, COLMAP camera or saved arc-length target. The approved mask
flag screens the existing capture records; mask pixels do not enter this loss.

```bash
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 \
  MPLCONFIGDIR=/private/tmp/webcam-neck-mpl \
  tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.flame_photo_fit \
  --session .private-webcam-runs/c79e26de178a434aa3f20682fdb087ed \
  --model ~/Downloads/FLAME2023Open.zip \
  --embedding ~/Downloads/mediapipe_landmark_embedding/mediapipe_landmark_embedding.npz \
  --components 100 --prior 100 \
  --out .private-webcam-runs/flame-fits/NEW-private-photo-trial
```

MediaPipe 0.10.32 and the existing pinned face-landmarker asset are required.
On macOS, first-time detector execution requires native graphics access even
with its CPU delegate. Repeated trials in a new folder can reuse `landmarks.json`
from a previous trial; every entry must match the original capture SHA256.
The original model and embedding are user-supplied assets and are not committed.

Open the resulting `comparison.html` directly in a browser. It has no external
requests: original-photo landmark overlays are shown beside a rotatable full
FLAME head. The report, model-native PLY, detector provenance, shape coefficients
and cameras are retained privately. No calibration or annotation decisions
transfer from older fits.

## Objective and evaluation

SciPy bounded trust-region least squares (`trf`, sparse numerical Jacobian,
LSMR subproblem) jointly fits shape coefficients, log focal length shared across
photos, and six rigid pose parameters per photo. Residuals are native image
pixels plus `sqrt(prior) * beta`; soft-L1 with scale 3 applies to the image block; the shape prior remains quadratic.
Coefficients are bounded to ±3. Three outer rounds update a front-facing-normal
landmark gate. This gate is not a full occlusion test. Pose initialization uses
EPNP from the neutral model and detected photo landmarks.

Image center is the fixed principal point. Distortion, expression, jaw pose,
eyelids and neck articulation are fixed. The model-native scale fixes the
similarity gauge, but does **not** determine the person's physical scale.
The current objective has no silhouette, photometric or dense-correspondence
term. In particular, chin, ears and neck have no direct landmark constraints in
this embedding. Improving that coverage is subsequent work.

Nine training slots and four hold-out slots are fixed in code by capture
chronology, before fitting. Held-out photos do not influence shared identity or
focal length. Their cameras are fitted using non-nose detector landmarks; nose
residuals are then reported separately. These are detector-agreement metrics,
not errors against physical ground truth. Selecting a hyperparameter based on
these four photos makes them validation photos; reserve a new capture session
for final testing.

The initial loose-prior fits reached coefficient bounds and had triangle normal
reversals relative to neutral; retain them as rejected diagnostics, not selected
outputs. The recommended review candidate uses 100 components and a quadratic
prior weight of 100. It has zero normal reversals, zero degenerate triangles,
no coefficients at bounds, and roughly 4.85 px pooled per-view validation RMS.
A matched prior-1000 sensitivity trial also has no reversals but roughly 5.78 px
validation RMS. Neither result establishes anatomical accuracy. Self-intersections
are not checked. Geometry quality and held-out detector residuals are reported
separately; selecting the smallest training loss alone would choose a poorer mesh.

Review the nose and jaw, then compare shared shape across repeated captures and
independent physical measurements before making mask-fit claims. Random
initialization alone does not resolve camera/shape ambiguity or detector bias.

[RealDenseFace evaluation and EC2 proposal](REALDENSEFACE_TRIAL.md) describes the
next comparison, including the distinction between neutral identity and
per-photo expression. The local bundle tool copies the exact split and hashes;
it neither provisions infrastructure nor transfers photos.

Validation:

```bash
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m unittest dimension_pipeline.tests.test_flame_photo_fit \
  dimension_pipeline.tests.test_realdenseface_trial
node scripts/tests/webcam_flame_photo_smoke.cjs /absolute/path/to/photo-trial
bash -n scripts/realdenseface_trial_setup.sh
```
