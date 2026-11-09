# Selected Gaussian surface validation

This follow-up checks the visually preferred sigma 0.03 candidate against the original raw reconstruction, fine zero-filter remeshing, and the coarse sigma 0.03 candidate. It runs locally with the same webcam experiment environment. It does not modify source meshes, accepted annotations, or scale.

```
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m dimension_pipeline.gaussian_validation \
  --session .private-webcam-runs/c79e26de178a434aa3f20682fdb087ed \
  --trial .private-webcam-runs/photogrammetry/c79e26de-auto-smoothing-v1 \
  --sweep .private-webcam-runs/gaussian-volume/c79e26de-sweep-v1 \
  --predictions .private-webcam-runs/realdenseface-local/c79e26de-mps-multiphoto \
  --measurements /path/to/flame-direct-style-specific.json \
  --model /path/to/FLAME2023Open.zip \
  --out .private-webcam-runs/gaussian-validation/NEW_RUN
```

The output directory must be new. Mesh, guide, model/topology, original-photo and prediction hashes are checked. Current camera records are stored in the report; they remain fixed across candidate checks. No camera or model fit is performed.

## Point rechecking

Start with the previously raw-supported guide candidates. Reattach their fixed raw surface locations to each candidate mesh within 0.04 eye-proxy spans. Require at least three original registered photos with reprojection disagreement at most six pixels and unoccluded surface visibility. Check the attachment triangle for long/skinny geometry and proximity to quality raw surface samples. Unsupported raw candidates are never promoted merely because smoothing closes a gap.

The source observations are barycentrically interpolated RealDenseFace image predictions. They are not independent anatomical labels. Reported inlier errors have selection bias because failed observations are excluded. Lower error or higher pass count is not an accuracy verdict.

## Matched measurement support

Restrict the surface graph to triangles with maximum edge 0.12 eye-proxy spans, longest-edge-squared / double-area at most 12, and all vertices within 0.02 eye-proxy spans of the sampled quality raw surface. These are geometric checks, not proof of photographic support along the whole path.

A route edge contributes only if its endpoints pass on **all four surfaces** and the path is connected on every eligible graph. Report mesh-edge lengths and control-chord sums over those identical edges. Incomplete routes retain null complete lengths. Mesh-edge path changes can reflect triangulation differences; control-chord sums isolate a different part of the positional sensitivity but are not surface arcs or tape lengths.

Named nose and bridge chords require passing endpoint candidates separately on each surface. Signed forward displacement uses the original frontal-camera axis and is positive toward the camera. These diagnostic locations remain model-derived; no review status or millimeter calibration transfers.

## Visual review

`review.html` contains matched-support tables, candidate displacement, two fixed-camera-plane sections, and six registered source-photo close-ups. Toggle raw and selected contours off to inspect the original image. Profiles use unchanged world coordinates with no independent alignment. The section planes are not asserted to be an anatomical midline. Keep disconnected curve segments disconnected.

The photos were used for reconstruction, and the landmark observations came from a learned detector. This workflow can detect disagreement and smoothing sensitivity, but independent measurements or another reference are still required to establish accuracy. Source-topology defects can survive the checks.

## Per-view threshold audit

Run `python -m dimension_pipeline.gaussian_point_audit` with the same session, trial, sweep, prediction, measurement and model arguments, replacing `--out` with `--validation VALIDATION_FOLDER`. It reads the completed report, verifies mesh/camera/prediction/guide provenance, writes `point-audit.json`, and refreshes the local review page.

For each model-derived named point, the audit evaluates the attempted nearest surface location in all original photos. It reports visibility, native-pixel reprojection disagreement, and the third-smallest error among visible original inliers. This is the minimum pixel tolerance that would give three qualifying views, before the other attachment and quality gates. It does not relax the six-pixel production experiment gate or accept failed landmarks. Compare thresholds to understand how sensitive a binary pass/fail result is to the exploratory cutoff.

## Triangle-interior route audit

Run `python -m dimension_pipeline.gaussian_arc_audit` with `--validation`, `--session`, `--sweep`, and `--measurements`. It verifies input hashes, rebuilds the same eligible graphs and attachments, and asserts that common-edge counts match the earlier validation. It invokes the established `flame_measurements_ui.js` routing implementation through Node, preserving barycentric controls and explicit mesh-edge fallback counts. It writes `surface-arcs.json` and refreshes the local page, retaining the named-point audit if present.

This extra calculation helps distinguish mesh-edge discretization effects from surface sensitivity. It shortcuts bounded local triangle strips along an edge-path corridor; it is not an exact global geodesic algorithm. Across different mesh topologies, corridor selection may still differ. All source candidates and partial-coverage limitations remain in force. No complete arc is synthesized across missing controls or disconnected components.

Local UI check: `node scripts/tests/gaussian_validation_smoke.cjs /absolute/path/to/review.html`.
