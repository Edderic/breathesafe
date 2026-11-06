# Local webcam surface pilot

This is a research workspace, separate from recommender measurements, ARKit
records, and synthetic-head annotation. Open it from **3D webcam pilot** in the
existing webcam panel or use the standalone preview below. No captures are sent
to Rails or a remote reconstruction service.

For read-only full-resolution versus analysis inspection, see
[mesh comparison and pilot findings](WEBCAM_MESH_COMPARISON.md).
For the frozen-depth filtering workflow and bounded results, see
[depth experiments](WEBCAM_DEPTH_EXPERIMENTS.md).
For optional CPU image-guided refinement and the two-capture screening results,
see [refinement experiments](WEBCAM_REFINEMENT_EXPERIMENTS.md).
For fixed nose/cheek/chin close-ups and measurement diagnostics on saved captures,
see [regional inspection and initial findings](WEBCAM_REGIONAL_INSPECTION.md).

## Setup on this Mac

Use native macOS arm64 and Python 3.12. From the repository root:

```sh
python3.12 -m venv tmp/webcam-pilot-venv
tmp/webcam-pilot-venv/bin/pip install -r python/dimension_pipeline/requirements-webcam.txt
node scripts/setup_face_landmarker.cjs
node scripts/setup_webcam_segmenter.cjs
python3 scripts/setup_webcam_native.py
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.webcam_pilot --diagnostics
```

The installer checks SHA-256 hashes of the official [COLMAP 4.2.1 arm64
release](https://github.com/colmap/colmap/releases/tag/4.2.1) and [OpenMVS 2.4.0
arm64 release](https://github.com/cdcseacave/openMVS/releases/tag/v2.4.0), including
the nested COLMAP app archive, and installs only under ignored `tmp/webcam-tools`.
It does not change Gatekeeper settings. Local cached binaries take precedence over
PATH. Diagnostics require the exact versions and Mach-O arm64 binaries; missing
libraries, version mismatches and startup errors prevent processing.

Start two terminals:

```sh
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.webcam_pilot
```

```sh
node_modules/.bin/vite --config scripts/face_landmarks.vite.config.mjs
```

Open <http://127.0.0.1:5178/scripts/webcam_pilot.html>. Alternatively, the Rails
app route is `/#/research/webcam-3d`. The processor binds only `127.0.0.1:5182`.
Its allowed browser origins are precisely HTTP localhost/127.0.0.1 on ports 3000,
5173, and 5178, with an exact processor Host check. Writes require JSON except ZIP
session reloads. Participant
files live under ignored `.private-webcam-runs`, mode 0700. Both Vite configs deny
this directory, including `/@fs/` access. Only processor endpoints serve artifacts;
requests use session IDs and fixed artifact names, never filesystem paths.

MediaPipe browser runtime is pinned to 0.10.18. The person-feature segmentation
model is version 1, hash checked before use. Hair and face-skin categories form a
starting mask; these categories can miss ears or include neck. Face detection uses
MediaPipe Python 0.10.32 and the same hash-pinned version-1 face-landmarker task as
the synthetic experiment. CPU inference still requires macOS graphics access for
image preprocessing; launching the processor in a graphics-restricted sandbox can
fail explicitly. Model setup downloads assets; processing uses cached assets only.

## Capture and review

See [capture-quality checks and the BRE-15 comparison protocol](WEBCAM_CAPTURE_QUALITY.md)
for advisory sharpness/framing checks, verified camera controls and the private
10/20/30-second comparison report. The 10-second default is unchanged.

1. Connect, create a session, give local-storage consent and enable the camera.
   The preview is mirrored; captured PNG pixels are unmirrored. The request prefers
   1920×1080; actual video dimensions are used without resizing or upscaling.
2. Capture the designated frontal image with a three-second countdown. Maintain
   a neutral expression and closed mouth. Keep the camera and torso fixed under
   diffuse light with a plain background.
3. Choose **Capture all 60 frames**. Start at your right profile during the
   three-second preparation countdown, then make one smooth right-to-left sweep
   during the ten-second capture countdown. At five seconds, face directly toward
   the camera; finish at your left profile when the countdown reaches zero. Keep
   your chin level. The designated frontal photo remains a separate capture.
   **Sweep duration** defaults to 10 seconds, with 20- and 30-second options; face
   the camera halfway through whichever duration you select.
   Use **Test audio** first. Speech announces seconds, says **Face camera** at the
   midpoint, and **Left profile. Done.** at completion. Individual frame numbers
   appear on screen; six frames per second are too fast to speak each number.
   The 60 frame deadlines span the full sweep, including the first and last poses.
   Capture timestamps, intended/actual elapsed time, sequence ID and protocol are
   saved with approved frames. If the browser falls behind, capture fails explicitly
   rather than collecting a burst of late frames; retry with a longer duration.
   Stop a sweep at any time. Individual frames can also be captured or retaken
   with their own three-second countdown and spoken frame number (1–60).
   Audio uses a local English system voice; missing voices are reported. The
   audio toggle mutes cues, and stopping capture or leaving cancels speech.
4. Review all 61 images individually. Generate the starting segmentation, paint
   include/exclude corrections, include both ears, and remove neck, shoulders and
   background. Approve each mask. Only approved image/mask pairs are uploaded to
   the processor. Unsaved frames remain in browser memory and are lost on reload.
   Saved approvals persist; resuming a session can reload and correct their masks.
   A retake replaces its own slot after approval and preserves all other slots.
   Use **← / →** to review the previous/next frame, or the adjacent navigation
   buttons. Switching frames loads or generates its mask automatically. Press
   **A** to approve, save and advance. Shortcuts pause in input fields and dropdowns,
   during capture/loading/saving, and while painting; held keys do not repeat approvals.
   **Accept all frames** saves every pending captured frame with its current mask,
   generating masks where needed, without individual review. Brush edits are
   preserved, saved slots are skipped, and missing captures are not invented.
   Progress and **Stop accepting** are available; an in-flight save may complete
   after stopping. A failure stops at the affected frame and retains earlier saves;
   correct that mask and run acceptance again to continue. Bulk acceptance is
   recorded separately from individual acceptance in mask provenance. It does not
   establish that automatic masks include the ears or exclude the neck correctly.
5. Submit reconstruction. Capture roles, timestamps, dimensions, actual camera
   settings, SHA-256 hashes and segmentation provenance accompany the PNGs.

Movement, specular skin, weak texture, motion blur, insufficient overlap and
expression changes may prevent reconstruction. No estimated FLAME head or missing
surface is substituted. A failed session retains images and logs for inspection.

## Reconstruction and camera conventions

The adapter runs masked CPU SIFT extraction, explicit temporal overlap
matching, shared `SIMPLE_RADIAL` incremental mapping, undistortion, OpenMVS dense
reconstruction and meshing. Background pixels are also masked out for dense
processing. Approved masks are also warped into each dense camera with binary
nearest-neighbor sampling and supplied to OpenMVS with background label 0 ignored.
Tower/cylinder augmentation, coordinate normalization and automatic ROI cropping
are disabled. A connected sparse model must register at least 90% of the 60 turn
frames. Smaller initialization candidates are ignored only when their image sets
are strict subsets of that selected model; selection and discarded candidate counts
are recorded in diagnostics. Disconnected image sets, equal-coverage competing
models and inadequate registration fail explicitly. Geometry is never merged across
independent coordinate systems.

The designated frontal is excluded from surface reconstruction. After meshing it
is matched against the fixed sparse model and registered with the shared camera
held constant, without bundle adjustment. Existing camera parameters/poses and
point coordinates are checked for changes. The original frontal image is then
undistorted using that registration and its actual output dimensions/intrinsics.
Detection and perspective ray intersection use that undistorted image.

The coordinate contract is COLMAP's arbitrary right-handed world frame:
`X_camera = R * X_world + t`, camera x right, y down, z forward. No anatomical
coordinate frame is inferred. `SIMPLE_RADIAL` distortion is `1 + k*(x²+y²)`;
undistorted cameras have k=0. Rays originate at `-Rᵀt` with direction
`Rᵀ[(u-cx)/fx, (v-cy)/fy, 1]`. Intersections retain the nearest positive ray hit
and its barycentric attachment; missed rays stay missing. Viewer rotation is only
for inspection and does not supply the detector camera.

The full unscaled PLY is retained. Analysis meshes are bounded to 20,000 vertices
and 40,000 faces, with QEM targeting 18,000 faces when reduction is needed. Hole
closing, spike removal, spurious-face cleaning and cosmetic smoothing are disabled
in meshing. Simplification records counts and deterministic sampled one-way surface
deviation in reconstruction units. This sampled deviation is not a Hausdorff bound
or proof of anatomical fidelity; meshing itself can bridge unsupported regions.
Review completeness before tracing either tape route.

## Calibration, projection and session artifacts

Trace ordered left tragion → subnasale → right tragion controls along the tape's
contact route, including intermediate points. Independently trace left tragion →
menton → right tragion. Ctrl-click the visible mesh to place controls, or enable
tap placement. Save draft routes to persist work before calibration.

Each segment follows a mesh-edge Dijkstra path with exact barycentric endpoints.
This respects disconnected topology but can overestimate a smooth surface arc;
route choice and mesh tessellation affect the result. Missing/disconnected route
coverage fails. A visually bridged hole must be rejected during coverage review.
These are tape-contact routes, not any of the four future ARKit-style paths.

Enter three tape readings in millimeters per arc. Calibration uses
`median(scale readings) / unscaled scale-route length`. It scales mesh coordinates
and all exported camera translations uniformly, preserving projection. Original
geometry/cameras remain explicitly unscaled. The check arc reports its own spread,
mesh length, signed mesh-minus-tape error and percent error; it never adjusts scale.

Inspect the undistorted frontal overlay next to the rotatable surface. Click a
detection or choose its MediaPipe index to inspect raw predictions, hit/miss,
barycentric attachment and pending/accepted/rejected decision. Decisions are
experimental review only and are separate from the original predictions. A ray hit
does not establish anatomical correctness. Recalibration recomputes projections
and resets their review decisions.

The surface viewer uses directional lighting calculated in consistent model units.
Adjust **Light direction**, toggle **Smooth lighting** (averaged normals for display)
or **Show mesh edges**, and use the quarter-view buttons to inspect contours.
**Reset view / fit surface** restores the frontal view and fits the entire surface;
zoom has a separate slider and Shift-scroll gesture, so ordinary page scrolling
does not enlarge the mesh accidentally. Display lighting does not modify vertex
coordinates, triangle indices, ray attachments or route lengths. Roughness and
missing geometry in the reconstruction still require review.

Session ZIP exports use `webcam-session-1.0.0` and a per-file SHA-256 manifest.
They contain approved images/masks, segmentation provenance, native tool logs and
text camera models, unscaled full geometry, bounded geometry, calibration drafts
and reports, detector provenance, raw predictions and reviewed projected points.
Reload verifies archive paths, sizes, hashes and artifact references and assigns
a fresh session ID. Separate full PLY downloads are labeled **unscaled** and
**calibrated mm**; the calibrated bounded mesh is also in `session.json`. The
original full PLY is preserved unchanged. Intermediate depth maps and MVS work files
remain in the local attempt directories rather than bloating the portable bundle.
Reload accepts ZIPs up to 1 GB and rejects expanded bundles over 8 GB. Exports are
private participant data too.

One job runs at a time. Cancellation stops subprocess groups and leaves an
explicit cancelled status. Restarting the service marks unfinished work interrupted
and retires its recorded subprocess, with process-start fingerprints to avoid PID
reuse. Restart reconstruction explicitly; each attempt uses a new directory.
Stop the job before deletion. Deletion removes the local session and its attempts;
it does not delete ZIPs already downloaded elsewhere.

## Verification and research acceptance

```sh
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m unittest python/dimension_pipeline/tests/test_webcam_pilot.py
node --test scripts/tests/*.test.cjs
node_modules/.bin/vite build --config scripts/face_landmarks.vite.config.mjs
```

For the browser smoke test, start both services, install Playwright under ignored
`tmp/webcam-browser` (`npm install --prefix tmp/webcam-browser playwright`), then run
`node scripts/tests/webcam_browser_smoke.cjs`. It uses installed Chrome with a fake
webcam, performs local mask inference/painting/approval, retakes a frame, verifies
Vite private-path denial, and exports/deletes/reloads its synthetic capture session.
It does not access a participant camera or validate reconstruction accuracy.

`node scripts/tests/webcam_bulk_accept_smoke.cjs` checks bulk acceptance using a
fake webcam and deterministic test masks, including brush preservation, partial
saves, cancellation and retry after a simulated save failure.

Implementation verification on this Mac: pinned native binaries install and pass
version/architecture diagnostics; the CPU detector initializes and returns an
explicit no-face error on a blank image. Analytic geometry/session tests and the
fake-camera browser flow pass. A consented participant reconstruction and repeated
capture evaluation have **not** been performed.

For research acceptance, capture one consenting participant and three readings of
each tape arc, then repeat the capture without reusing calibration controls. Record
processing time, registered fraction, sparse and frontal reprojection diagnostics,
ear/nose/chin completeness, simplification deviation, scale factor, both reading
spreads, and the independent check's absolute/percent error. Compare the same
reviewed points across repeats with an explicitly documented alignment method.
Until paired ARKit/reference scans exist, report repeatability and disagreement,
without validated 3D landmark accuracy or ARKit equivalence claims.
