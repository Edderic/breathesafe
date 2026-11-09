# Gaussian volume experiment

This is a local CPU experiment for BRE-20. It preserves source sessions, annotations and calibration. New candidate meshes have different topology; old triangle attachments and reviews must not be transferred.

Install the optional extractor in the webcam experiment environment:

```
uv pip install --python tmp/webcam-pilot-venv/bin/python scikit-image==0.25.2
```

Run:

```
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m dimension_pipeline.gaussian_volume \
  --session .private-webcam-runs/c79e26de178a434aa3f20682fdb087ed \
  --trial .private-webcam-runs/photogrammetry/c79e26de-auto-smoothing-v1 \
  --measurements /path/to/flame-direct-style-specific.json \
  --out .private-webcam-runs/gaussian-volume/NEW_RUN
```

The input recipe must hash-match the earlier automatic route experiment. The raw mesh must hash-match the trial report. The output directory must be new. The source mesh is never overwritten.

## Representation and sweep

The source is not watertight. We therefore avoid assigning a global inside/outside label or treating unsigned distances as signed distances. Instead, 250,000 deterministic area-weighted samples carry the source triangle normals. Long or skinny source triangles are excluded (edge >0.12 eye-proxy spans or longest-edge-squared / double-area >12).

Each grid point blends the signed point-to-plane offsets of its four nearest samples. This is a local oriented implicit field, not a true signed Euclidean distance field. Normal errors or folds in the reconstruction can still create incorrect zero sets.

The field is evaluated only with proximity support within 0.1 eye-proxy spans. Gaussian convolution uses normalized weights: G(field × weight) / G(weight). This prevents unknown voxels from being treated as known zero-distance values. Marching cubes uses the zero level, a minimum filtered weight of 0.25, and the original proximity band. Extracted triangles touching unknown interpolated support are removed.

The longest grid axis targets 160 or 224 voxels; rounding can add one boundary layer, and the report records the actual shape. Each grid has a zero-filter baseline and sigma 0.015, 0.03, or 0.06 eye-proxy spans. Sigma in voxels differs by resolution; physical smoothing width in reconstruction units is shared. A 14-million-voxel guard bounds allocation; queries run in chunks. All variants start independently from the same field for their resolution.

Proximity is not photographic evidence. The output may join nearby surfaces, close small holes, create components, or alter the nose. New geometry remains inferred even if it passes the proximity mask. No claim of anatomical accuracy follows from smoother appearance.

## Review and metrics

`comparison.html` is self-contained except for adjacent local report, photo and mesh files. It provides synchronized rotation, shared framing, flat versus interpolated-normal shading, front/profile/underside views, original registered-photo contour overlays, and PLY downloads. Display meshes are reduced to at most 50,000 faces; the exported candidates retain their full extracted topology.

`report.json` records grid parameters, source hashes, software versions, input-quality filtering, bidirectional sampled surface disagreement, topology and boundary diagnostics, source-proximity gaps, and fixed-anchor displacement. Source-to-candidate distances sample quality source triangles; reverse distances use the original full mesh. Median adjacent-normal angle is topology-dependent and is not an absolute roughness or accuracy measure.

Nose/bridge chords and route lengths are sensitivity diagnostics: only previously supported raw guide candidates are reattached within 0.04 eye-proxy spans. Their review and photographic visibility are not re-certified. Unsupported controls stay unavailable; incomplete lengths remain null. Mesh-edge routes can overestimate smooth geodesics and do not simulate a physical tape. Partial lengths cannot estimate a full perimeter.

Synthetic tests check masked convolution normalization, planar surface error below 5% of voxel size, zero-filter independence, and bounded grid allocation. Human facial accuracy still needs photo review and independent measurements.
