# BRE-15 capture quality and duration comparison

The 10-second sweep stays the default. Quality checks are development screening,
not a validated blur detector or anatomical-accuracy assessment. They flag frames
for inspection and retakes; they never drop images automatically.

See [the November 4 local comparison results](WEBCAM_CAPTURE_QUALITY_RESULTS.md)
for the six completed development captures and their limitations.

## Controls and provenance

After enabling the camera, the workspace checks its actual capabilities and
settings. Focus, exposure and white balance can be locked only when the browser
exposes manual mode and a readable current numeric value. **Lock selected camera
settings** requests those values and checks the reported settings afterward.
Ignored requests are **unverified**, rejected requests are **failed**, and absent
controls are **unavailable**. None is displayed as successfully locked.

**Restore initial camera settings** requests and verifies the original modes.
Resolution constraints and other controls are preserved. Configure these controls
before the first photo: changes are disabled once the session contains captures,
because all turn views and the held-out frontal should share the camera model.
Camera snapshots record capabilities, actual settings, requests and verification
per frame; an externally changed setting loses its verified status in that snapshot.

The dashed preview guide is a positioning aid, not live head detection. Keep ears,
chin and both profiles inside it. The mask-based framing measurement becomes
available when a captured frame's mask is loaded or generated.

## Quality metric

The canonical settings are in `capture_quality_policy.json`, version
`webcam_capture_quality_v1`:

- Find the foreground bounding box in the approved/current binary mask.
- Sample that rectangle with its longest side at most 256 pixels, without
  upsampling. Use deterministic bilinear sampling of 8-bit luma
  `0.2126 R + 0.7152 G + 0.0722 B` and nearest-neighbor mask sampling.
- Compute the population variance of the four-neighbor Laplacian, using only
  stencils entirely inside the foreground mask. This avoids treating the mask's
  cutout boundary as image sharpness. Require at least 64 interior stencils.
- Flag variance below 40 as **low sharpness or low texture**. Flag masked-head
  height below 55% of image height, or a mask within 2% of any image edge.

These thresholds are provisional and must not be described as validated acceptance
limits. Hair, beard, skin texture, lighting, noise and mask errors affect the score.
A mask bounding box cannot establish that ears or chin are actually complete.
No flags means only that these screening rules did not fire; it does not establish
good reconstruction or physical measurement accuracy. Preserve policy/version
when comparing results; changing thresholds requires a new policy version.

The browser computes checks after segmentation, when brush editing ends and before
acceptance. Python independently computes the same values from accepted image/mask
bytes and stores them in `capture_quality`. Original PNG pixels are preserved.
The schema also retains `camera_controls`, the original camera settings and timing.
These fields and optional comparison labels round-trip in session ZIPs. Legacy
sessions remain loadable; offline reports can score their original PNGs without
rewriting them. Quality computation does not run in the timed sweep callback.

## Six-capture development protocol

Use the same consenting participant, camera, browser origin, lighting and camera
position throughout this small comparison. Keep the camera fixed. Use diffuse
light across the face, avoid a bright window behind you and strong reflections,
and keep expression neutral with mouth closed. Do not add a forehead/poster texture
pattern to the moving subject for this experiment; this is a camera-capture test.

1. Choose a new group label, e.g. `bre15-desk-a`. Describe the lighting, distance,
   framing and intended camera settings in **Conditions**. Avoid participant names.
2. Make six **separate sessions**, setting the labels before **New session**:

   | Capture | Sweep | Repeat |
   | --- | --- | --- |
   | 1 | 10 seconds | 1 |
   | 2 | 20 seconds | 1 |
   | 3 | 30 seconds | 1 |
   | 4 | 30 seconds | 2 |
   | 5 | 20 seconds | 2 |
   | 6 | 10 seconds | 2 |

   The reversed second round reduces a simple duration/order confound. It does not
   make this one-person development experiment a population validation study.
3. Enable the camera, settle into the same position and apply supported locks.
   Verify the labels, and record unsupported/changed settings rather than assuming
   a lock. If settings, lighting or position change, document it or begin another
   comparison group; do not relabel different conditions as identical afterward.
4. Take the separate designated frontal photo, then the full 60-frame sweep at
   the listed duration. Follow the midpoint camera-facing cue. The same 60 views
   over more seconds tests movement/sharpness; it does not add geometric viewpoints.
5. Inspect screening flags, image blur and ear/chin mask boundaries. Retake as
   necessary; record exceptions. Manual retakes or mixed sweeps are not silently
   counted as a clean continuous-duration trial. Save all 61 captures and export
   the session before leaving the page. Keep originals for all failed attempts.
6. Reconstruct using the same pinned pipeline/configuration for each session.
   One job runs at a time. Review ear/nose/chin surface coverage, visible detail
   and artifacts. Where available, collect the existing calibration and independent
   check arcs; the check must not tune scale. Do not change reconstruction quality
   settings halfway through the duration experiment.

The earlier scan remains an exploratory baseline. Its inferred 10-second timing
does not establish that its lighting/camera conditions match this new comparison.
Stop-and-hold capture is a follow-up only if motion blur remains demonstrated.

## Private comparison report

From the repository root:

```sh
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.capture_quality_report \
  --group bre15-desk-a \
  --output .private-webcam-runs/capture-comparisons/bre15-desk-a.json
```

Or pass explicit session IDs with `--sessions ID1 ID2 ...`. An optional
`--conditions-manifest` JSON maps IDs to `{ "group": "...", "conditions": "...",
"repeat": 1 }` for retrospective annotations. Such labels are explicitly marked
retrospective; they are not proof that historical conditions were controlled.

The command verifies hashes and recomputes per-frame quality from original PNGs.
It reports duration/sequence provenance, per-duration repeated-capture summaries,
registration coverage, processing time, mesh counts and recorded completeness
limitations, available independent-check measurements, and failures. It compares
recorded camera configurations and normalized reconstruction commands/matching
windows. Unknown/different settings, incomplete captures and missing repeats are
listed explicitly. The output remains in the private run directory and no session
or capture artifact is rewritten.

Matching reported resolution/frame rate does not establish fixed focus, exposure
or white balance. The report explicitly notes when all three manual locks were
not verified, since automatic changes may be absent from browser-reported settings.

The initial recommendation retains the 10-second default pending controlled data
and human review. Image/check-arc summaries do not measure aligned 3D repeatability.
Surface completeness and detail retention require inspection; anatomical accuracy
needs independent reference data. Do not conclude that a higher sharpness score,
more registered images or a smoother-looking mesh validates dimensions.

## Verification

```sh
node --test scripts/tests/webcam_camera_controls.test.cjs scripts/tests/webcam_capture_quality.test.cjs
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m unittest python/dimension_pipeline/tests/test_capture_quality.py
```

For the fake-camera integration test, run Vite, then start an isolated API:

```sh
PYTHONPATH=python tmp/webcam-pilot-venv/bin/python scripts/tests/webcam_test_processor.py
```

Run `node scripts/tests/webcam_capture_quality_smoke.cjs`. It forwards requests to
the isolated API on 5183, never opening participant sessions. It exercises
supported/ignored/unsupported controls, restoring settings, quality warnings,
metadata persistence and retaking an existing slot. Mock camera controls and
deterministic masks do not establish compatibility or quality gains on real hardware.
