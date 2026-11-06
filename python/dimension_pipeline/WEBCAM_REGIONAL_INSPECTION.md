# Regional inspection and measurement report

Resume an existing surface-ready session and choose **Inspect nose and mask-contact
regions**. The panel defaults to the latest completed image-refinement variant;
choose **Raw stages only** to inspect a session without refinement. No new capture
or reconstruction is needed. The processor must be running with the updated code.

The four synchronized views compare raw full, raw analysis, refined full and refined
analysis geometry. Select Nose, Top cheeks, Mid cheeks or Chin, then drag to rotate
or use the regional yaw, tilt, zoom and light controls. Smooth lighting changes
lighting only. These views never place, transfer or accept annotations. Their
orientation and controls are separate from the original annotation viewer.

The frontal image shows numbered detector cues and illustrative region bands.
The section plot always shows the nose: unjoined mesh/plane intersection segments
retain gaps, alongside sampled saved dense points when available. This is a
camera-X plane through the original raw index-4 hit, not a reviewed anatomical
midsagittal plane. Axes are camera depth toward the camera and height up, relative
to the raw tip proxy, divided by the fixed eye-corner surface-proxy span.

## What the numbers mean

All measurements remain in **unscaled reconstruction units**, even if the parent
session has a tape calibration. No calibration is transferred to refinement.

- Regions are unions of 3D capsules around nearest positive frontal detector-ray
  hits on the original full mesh. The normalizer is the distance between raw hits
  for indices 33 and 263; this is not anatomical calibration. Fixed volumes are
  reused across all stages without alignment fitting or following moved geometry.
- Nose uses chain 168–4–2 with radius 0.20 of that span. Top cheeks use 50–101
  and 280–330, mid cheeks 205–187 and 425–411, each with radius 0.16. Chin uses
  148–152–377 with radius 0.20. Missing anchors make that region unavailable;
  missing normalizer hits prevent the regional report. There is no fallback head.
- Each region targets 384 area-weighted surface samples, seed 37, using bounded
  rejection sampling inside the exact volume. A separate expanded cloud targets
  3,072 samples, seed 38. Plane RMS is the smallest covariance eigenvalue's square
  root in neighborhoods of radius 0.04 of the fixed span, with at least ten
  neighbors. At least 30 assessed neighborhoods are required. Curvature, true
  detail and tessellation affect this quantity: a lower value does not prove
  better anatomy.
- Raw→stage and stage→raw distances use nearest triangle surfaces in unchanged
  reconstruction coordinates. Proximity is the fraction of fixed raw samples
  within 0.02 of the span from the stage surface. These are sampled geometry
  disagreements, not accuracy estimates or exact Hausdorff bounds. Reverse
  statistics and sampling provenance are included in the JSON.
- Boundary and nonmanifold counts refer to original source edges intersecting
  the fixed volume (incidence one or greater than two). Artificial display crop
  edges are excluded. A hole count is deliberately unavailable: these edge
  counts cannot establish anatomical completeness.
- Frontal support uses a 13×13 image grid, filtered by exact finite ray-segment /
  capsule intersection; the nearest positive hit must lie inside the volume.
  This is view-specific support, not proof of complete ears, nose or chin.
- The nose chord joins detector-ray hits 4 and 2. The forward offset is the
  camera-depth difference from hit 168 to hit 4. These are unreviewed proxies,
  not verified pronasale/subnasale/sellion measurements. Anatomical protrusion,
  surface arcs and the four exact ARKit path lengths remain null until landmark,
  route and cross-topology correspondence review. Legacy path segments and
  topology provenance are exposed without inventing a mapping or mask seal line.

Display crops use conservative whole source triangles; they do not clip, repair,
smooth or fill geometry. Metrics sample the exact capsule volume, rather than
these conservative display crops. Each displayed face retains its source index.
The display limit is 200,000 faces per region; exceeding it is explicit.

Saved `dense.ply` support is optional. The bounded reader accepts the OpenMVS binary
little-endian point format, including skipped visibility lists, up to 256 MiB and
three million points. It reports per-region point counts and up to 512 sampled
point-to-raw distances. Profile scatter is separately sampled in a camera-X slab
with halfwidth 0.02 of the span. Missing, oversized or unsupported caches are
reported explicitly. Points are not triangulated into a substitute surface.

## Persistence and isolation

**Download regional report JSON** saves `webcam_regional_inspection_v1`, containing
the policy, source hashes, algorithm hash, input fingerprint, camera, proxy hits
and barycentric attachments, face selections, inline analysis geometry, metrics,
profiles and bounded dense samples. Full PLYs remain referenced by hash and
session-scoped artifact URL; this JSON alone is not a full offline mesh archive.
Reload the existing session ZIP into the pilot and recompute the report to inspect
it again. There is no standalone regional-JSON import UI. Original session ZIPs
may omit the dense processing cache, so dense support can be unavailable on reload.

The endpoint accepts only a session ID and a completed variant ID, with existing
exact Origin/Host checks and contained artifact paths. Full-mesh downloads verify
SHA-256 before display. Report fingerprints cover session/variant, source geometry,
raw detector output, camera, policy, legacy paths and algorithm. A four-entry
in-memory cache is isolated by session and variant. Only one bounded report
calculation runs at a time; a competing request receives an explicit retry error.
Cancellation aborts browser loads, workers and rendering; an already-running
read-only server calculation may finish and populate the cache. It never writes
session geometry, calibration, landmark decisions, ARKit records or recommender data.

## Existing-capture findings, November 5, 2026

Inspected the four saved direct-light captures in their corrected order:
orange, orange, phone, phone. All used the existing matched 24-iteration,
regularity-weight-0.20 refinement. Private source IDs, complete reports,
fingerprints, screenshots and a summary live under ignored
`.private-webcam-runs/capture-comparisons/regional-inspection/`.

Percent changes below are within each capture, relative to its raw full mesh.
They measure changes in unreviewed detector proxies and regional plane residuals.

| Capture | Refined full nose plane RMS | Refined full nose chord | Original analysis nose chord |
| --- | ---: | ---: | ---: |
| Orange 1 | −9.67% | +0.02% | +0.18% |
| Orange 2 | −8.77% | −1.13% | −1.53% |
| Phone 1 | −11.06% | +0.94% | +2.23% |
| Phone 2 | −11.05% | +0.63% | +1.43% |

The nose residual fell only about 9–11%, while cheek residuals fell about 15–34%.
Whole-head smoothness improvements therefore overstate the change in the most
important nose region. Simplification changes the nose chord as well as refinement;
its effect should be inspected before using the bounded analysis topology for
measurement. Original analysis meshes have 8–16 nonmanifold edges in these nose
regions, versus zero in the full raw and full refined nose regions. Refined
analysis meshes retain 1–6. These are source topology diagnostics, not crop edges.

Orange 2 has a missing raw chin proxy anchor, so its chin metrics and crop are
explicitly unavailable. The other three chin regions are available. All four
retain dense support. No anatomical measurement or physical accuracy ranking is
established by these results. Lighting order, the several-hour capture gap,
ambient light and unconfirmed phone brightness/placement remain confounds.

The next measurement step is reviewed nose landmarks and mask-contact path
correspondence on the full surfaces, checking stability against analysis
simplification. This report provides the evidence to choose those regions without
claiming that automatic detector cues already supply anatomical truth.

## Verification

The dimension-pipeline suite passed 85 tests and the mesh/capture Node suite passed
65 tests; the standalone Vite production build passed. Analytic regional tests
cover plane offsets, nose sections, rigid coordinate transforms, proxy changes,
missing hits, exact capsule distances, original-versus-crop boundaries, dense
visibility lists, source provenance, cache isolation and HTTP origin checks.
Live browser checks passed on all four captures: all region selections, shared
rotation, raw/refined selection, cancellation/retry, JSON downloads and unchanged
saved session bytes. The existing full/analysis browser comparison regression also
passed, including source/hash failures, context loss and calibrated-parent isolation.
