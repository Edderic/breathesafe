# BRE-16 full and analysis mesh inspection

Resume a reconstructed session and select **Compare full and analysis meshes**
below the annotation view. Both read-only panes use indexed WebGL 2 rendering.
Drag either pane to rotate; the existing yaw, tilt, light, smooth-lighting, edge,
zoom and reset controls operate on both panes and the original annotation view.
Shift + scroll zooms. Counts, identities, units and provenance identify each mesh.
Loading is opt-in; closing comparison releases its workers and GPU resources.

## Geometry, coordinates and attachments

Both panes use the same registered frontal-camera transform, uniform calibration
scale, rotation and one shared fit over both meshes. They are not independently
aligned or fitted. The shared fit also applies to the SVG annotation view while
comparison is open. Smooth lighting computes display normals without changing
geometry. GPU buffers use Float32 display coordinates; original file bytes and
stored analysis coordinates retain their originals.

The worker preserves vertex order and topology. It performs no welding,
triangulation, smoothing, hole filling or repair. Unsupported/invalid geometry
fails explicitly. Existing SVG picking limits are unchanged.

Both GPU panes are read-only. Landmark/tape placement stays on the bounded SVG
analysis view. Inspection clicks never emit annotations. An order-sensitive
SHA-256 of canonical analysis JSON identifies the annotation source; the original
full PLY has its separate byte SHA-256. Calibration retains those source identities
and topology, recording uniform scale separately. Full-mesh triangle indices are
never interpreted as analysis attachments.

## Read-only report and future providers

`GET /sessions/<id>/mesh-comparison?variant=raw` uses the processor's exact loopback
Host/origin checks. Requests take session/registered-variant IDs; paths come from
saved session metadata and remain contained in that session. Sampling runs outside
the store lock, keeping cancellation and session reads available. No session,
capture, attachment or mesh files are written.

The versioned `webcam_mesh_comparison_v1` report records units, scale, camera/frame
provenance, identities, counts and two directions of surface disagreement:

- Full → analysis: 5,000 uniform area-weighted triangle-surface samples, seed 0.
- Analysis → full: 5,000 samples, seed 1.
- Nearest triangle-surface distances: mean, RMS, median, 95th percentile and
  **sampled maximum** for each direction, using proximity-query batches of 128.

No alignment/ICP removes differences. Calibration uniformly scales distances into
mm; uncalibrated distances remain reconstruction units. Samples can miss local
defects, so their maximum is not an exact Hausdorff bound. Mesh disagreement does
not measure reconstruction or anatomical error. **Download comparison report**
retains the sampling details. Session exports retain the source geometry and scale
needed to regenerate it; display buffers are disposable.

The presentation takes named variants with explicit kind, hash, identity, counts,
units and provenance. A selected variant must have a report identifying that same
source. Production currently registers the raw full mesh; unknown variants fail.
The analytic browser fixture also tests a separate `depth_filtered` provider and
its own statistics. Future raw/filtered/refined providers can reuse this display
without changing annotation topology. No filtering/refinement is performed here.

## Resource limits and failures

Inspection caps are 64 MiB binary PLY, 8 MiB ASCII PLY, 1,000,000 vertices and
2,000,000 triangles per mesh. Server and worker preflight header counts. Browser
downloads are size/hash verified. GPU buffers are indexed; edge indices allocate
only when requested. Worker preparation has a 60-second timeout and cancellation.
Drawing uses animation frames. Caps do not guarantee sufficient device memory.

Missing WebGL 2, worker/allocation/draw errors, invalid/truncated/hash-mismatched
artifacts and context loss show errors with retry. Retry creates fresh canvases.
Closing comparison/leaving the session aborts downloads, terminates workers and
releases buffers, shaders and GPU contexts. The bounded annotation view and full
mesh download remain available after an inspection failure.

## Original pilot findings

The saved pilot contains **163,297 vertices / 325,959 triangles** in its full mesh
and **9,031 / 17,999** in the analysis mesh. Read-only headless Chrome inspection
exercised load, rotation, lighting, edges, reset and annotation isolation on that
actual PLY. The live API matched the offline report; sampling took approximately
2.3 seconds in that run. Full PLY bytes and all 19 saved session manifests remained
unchanged.

| Direction | RMS (reconstruction units) | 95th percentile | Sampled maximum |
| --- | --- | --- | --- |
| Full → analysis | 0.012979 | 0.016724 | 0.189055 |
| Analysis → full | 0.005285 | 0.011265 | 0.047886 |

Matched-lighting views show fine granular roughness already present across the
full reconstructed face. Simplification removes fine detail and presents larger
facets/bumps; it is not the sole source of observed noise. Eye/ear detail and lower
boundary artifacts remain unresolved. These observations support inspecting dense
reconstruction/filtering next. They do not establish anatomical accuracy or
physical detail loss in millimeters. This session remains unscaled.

Participant assets, JSON reports and `bre16-full-analysis-browser.png` stay in the
ignored `.private-webcam-runs/capture-comparisons/` directory.

## Verification

```sh
node --test scripts/tests/webcam_mesh_buffers.test.cjs
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m unittest python/dimension_pipeline/tests/test_mesh_comparison.py
node scripts/tests/webcam_mesh_comparison_smoke.cjs
```

The browser test uses Vite and intercepted analytic fixtures, including a known
offset/reordered topology, calibration, variant switching and hash/size/worker/GPU/
context-loss/cancellation failures. It never requires a participant camera.
For read-only pilot inspection, set
`WEBCAM_COMPARISON_SESSION=11fd01f7b2614b3888e494a897576d11` after generating its
private `bre16-original-pilot.json` with `compare_session`.
