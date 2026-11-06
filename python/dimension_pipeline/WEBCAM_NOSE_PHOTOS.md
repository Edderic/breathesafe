# Nose close-ups on registered source photos

Resume a reconstructed session and click **Inspect nose on source photos**.
The panel defaults to the latest completed image-refinement variant, or raw only
when no refinement exists. It uses the saved source images; no new capture or
reconstruction is required.

Use **Show overlay** to switch between Photo only, Raw full, Refined full and
both. Contours are shown by default; enable **Include fine wireframe** for context.
Cyan lines belong to the raw full mesh and pink lines to the refined full
mesh. Change opacity or close-up zoom without recomputing geometry. Inspect the
tip, columella, alar contours and nearby skin in several views. Repeated mismatch
across views is more informative than a single smooth-looking rendering; camera
alignment, motion, lighting and reconstruction error remain possible contributors.

Up to six source views load initially. For two-pass captures the selector picks
views near camera yaw −35°, 0° and +35° separately for each declared capture
height. Single-arc captures target −60°, −30°, 0°, +30° and +60°. Selection uses
registered camera position relative to the raw tip proxy in the original frontal
camera frame; these are not anatomical yaw or pitch measurements. Timing alone
does not determine view selection. Duplicate choices are removed. Remove a view
and use **Registered source view → Add view** to inspect another registered frame.
Height labels are capture-protocol declarations, not measured camera heights.

## Select and inspect a suspected dent

Enable **Select suspected dent on 3D surface**. A separate magnified GPU viewer
loads the selected raw or refined full mesh. It initially uses the detector-4 ray
hit as an explicitly labelled seed. Click the actual suspected depression to
replace it with a manual diagnostic selection. Drag to rotate, use the profile
or below presets, adjust light or zoom, and **Center selected point** as needed.
Smooth diagnostic lighting changes normals used for lighting only, not vertices.
Clearing the point removes its linked markers and sections. Switching diagnostic
mesh starts a new source-specific selection; it never transfers an attachment.

The selection is a validated source triangle plus barycentric weights and exact
full-PLY SHA-256. Picking uses the same orthographic camera-space signs, rotations,
scale and clipping volume as the full-mesh renderer, selecting the nearest visible
positive ray hit. Background misses retain the previous point. This display ray
is distinct from the perspective cameras used for projecting into source photos.

The gold marker projects the **same world point** into every selected photo using
that photo's original radial camera. An additional nearest-full-source-surface
ray test labels it visible or occluded; behind-camera and outside-image statuses
are explicit. Occluded points use hollow/dashed markers, rather than suggesting
they lie on visible skin. The marker is not snapped to a photo feature or to the
other mesh. **Center photos on selected diagnostic point** centers each close-up
on that point's projected pixels; turn it off to retain the original nose framing.
The 3D viewer's screen marker itself can be hidden behind geometry after rotation;
its overlay visibility is not the source-photo occlusion diagnostic.

The local section plot compares both full meshes in their original shared world
coordinates. Vertical sections have normal equal to original frontal camera X;
horizontal sections use camera Y. Each plane passes through the selected point.
The X axis is depth toward the frontal camera; Y is height up or camera right.
Axes have equal physical display scales, with the exact selected point at zero.
Small/medium/large neighborhoods use radii 0.06/0.12/0.20 of the raw eye proxy span.
Intersection segments touching the local sphere are retained without stitching,
interpolation or hole filling; the plot clips their display to its local window.
Missing or over-3,000-segment sections have explicit unavailable statuses. These
camera-based sections are not anatomical sagittal planes, ordered surface arcs,
clinical protrusion measurements or proof of recovered anatomy.

The read-only GET/POST `nose-probe` endpoints take a session ID, completed variant,
source ID/hash, validated attachment or picking view, section parameters and up to
six registered photo slots. They do not write session files or landmark reviews.
Selection is ephemeral: **Download point inspection** saves source identity,
attachment/world coordinates, cameras/photo hashes, visibility, section geometry
and limitations. The main overlay report also includes the current diagnostic
selection. Neither JSON is a standalone full-mesh/photo archive or an import UI.

## Camera and visibility contract

The source is each original unmirrored native PNG, verified against its recorded
SHA-256 and registered camera dimensions. A reconstruction photo's original
`registered:turn_NN.png` camera supplies `R`, `t`, focal lengths, principal point
and SIMPLE_RADIAL distortion. Projection is `Xc = R Xw + t`, normalized
`x = Xc.x/Xc.z`, `y = Xc.y/Xc.z`, multiplied by `1 + k(x²+y²)` before applying
focal lengths and principal point. This avoids overlaying undistorted coordinates
on original distorted pixels. There is no preview mirroring or viewer-derived
orthographic camera.

The nose volume is the same fixed raw-full-surface detector-proxy capsule region
as the regional report. Missing raw proxy/normalizer hits fail explicitly. Source
mesh coordinates remain unscaled, and the original registration stays fixed for
both raw and refined geometry; no per-view alignment is fitted to improve the
display. Refined frontal re-registration is not used for these original turn
photos. Missing registered photos are excluded from the catalog.

This is a sparse wireframe diagnostic rather than a filled pixel-perfect depth
render. For each full source mesh, conservative nose triangles supply at most 300
deterministically selected unique source edges. Edges separating front/back-facing
source triangles, plus original boundary edges, take priority (up to 240); remaining
slots provide evenly sampled context edges. These are source-facing transitions,
not boundaries introduced by the crop. Each edge is split into three
subsegments. A subsegment is drawn only when its midpoint is inside the fixed
volume, projects in front of the camera and agrees with the nearest ray hit on
the entire source mesh within `1e-5 × raw eye-proxy span`. Visibility queries are
batched in groups of 128. Endpoints can cross occlusion boundaries: midpoint
testing is deliberately not claimed as exact per-pixel clipping. Each displayed
line retains its original vertex IDs and third index. Distortion is evaluated at
both endpoints and midpoint to approximate curved image-space edges.

**Absent lines do not establish a hole or absent geometry.** Source images guided
reconstruction/refinement and are not an independent reference scan. An overlay
can reveal disagreement without identifying which underlying estimate is wrong.

Close-up framing uses projected corners of the raw-volume bounding box plus a
20-pixel margin, clipped to the original image bounds. It is approximate framing,
not a measurement or segmentation. Zoom changes the SVG view box around its
center; photos and lines retain the same original pixel coordinates.

## Isolation, export and limits

Read-only endpoints accept session IDs, fixed capture slots and completed variant
IDs: `GET /sessions/:id/nose-views?variant=:variant` and
`GET /sessions/:id/nose-overlay/turn_NN?variant=:variant`. Existing exact local
Origin/Host validation applies. No filesystem path comes from the client.
Full mesh resource limits remain 64 MiB, one million vertices and two million
triangles. Original browser photo downloads are limited to 16 MB and hash checked
before display. Missing files, hash/camera mismatches and insufficient visible
source edges are explicit failures/statuses.

Server work is serialized by a module lock and retains at most two source meshes
and twelve overlay reports in memory. Reports are keyed by session, variant,
camera/photo provenance, full-mesh hashes, region, version and algorithm hash.
The first six-view calculation on a detailed mesh can take several minutes;
completed views appear progressively and repeated views use cached reports.
Browser cancellation aborts pending loads; an already-running read-only server
calculation may finish and populate the cache. Loaded views remain visible when
cancelled. Reload starts a fresh panel load, clearing previous views. Photo blob
URLs are revoked on removal, reload and unmount. Stale asynchronous results are
discarded.

**Download nose overlay report** exports the versioned catalog and currently
loaded overlays, including camera models, photo hashes/URLs, mesh hashes, crop,
sampled projected edges, visibility method and limitations. It references source
photos by session URL/hash; it does not embed their pixels or full PLY files and
has no standalone JSON import UI. Reload the original session ZIP and reopen this
panel to recompute. The original session bundle already contains source captures
and cameras. No geometry, images, landmark reviews, calibration, detector output,
ARKit data or recommender records are modified by inspection or download.

## Verification

102 Python tests passed, covering analytic distorted projection/back-projection,
rigid world-frame invariance, visibility with overlapping front/back surfaces,
bounded edge sampling, missing nose anchors, camera/dimension guards, photo hash
tampering, cache isolation and read-only HTTP Origin enforcement. The standalone
Vite production build passed. The browser smoke script exercises the existing
consented two-pass capture, overlay toggles, zoom, add/remove view, report download,
cancellation and unchanged saved session bytes; it saves private screenshots and
reports under ignored `.private-webcam-runs/capture-comparisons/nose-photo-overlays`.
Linked-point tests additionally cover exact barycentric attachment, unchanged
inputs, GPU picking coordinates and misses, perspective visibility statuses,
analytic offset sections and read-only POST origin checks. Two Node tests check
viewer signs, marker placement and equal-scale section plotting. A live browser
test verified full-mesh picks, all six photo projections, plane changes, exports,
clearing, source switching and unchanged session bytes. That focused point test
uses previously verified cached contour responses while exercising the new
point/section endpoints, meshes, cameras and photos live.
