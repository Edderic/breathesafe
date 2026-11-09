# Trifold / duckbill route projection and full-path audit

This experiment distinguishes geometry coverage from automatic point correspondence. The original saved FLAME route is a proposed mask-contact path. Its locations and reviews are not accepted anatomical labels on a Gaussian reconstruction.

```
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m dimension_pipeline.mask_route_review \
  --session .private-webcam-runs/14ff5d878cf748558e6406b4d07b639a \
  --source-session .private-webcam-runs/c79e26de178a434aa3f20682fdb087ed \
  --source-fit .private-webcam-runs/flame-fits/c79e26de-analog-review/flame-100.ply \
  --neck .private-webcam-runs/gaussian-volume/expanded-neck-selected-003-v1 \
  --coverage .private-webcam-runs/all-photo-coverage/expanded-neck-all61-v1 \
  --measurements /path/to/flame-direct-style-specific.json \
  --out .private-webcam-runs/mask-route-review/NEW_RUN
```

The style defaults to the unique closed trifold perimeter, shared here with the duckbill use case. Source fit, guide, candidate mesh, original-photo and mask hashes must agree with the previous experiments. Source sessions and saved annotations remain unchanged. The output directory must be new.

## Two distinct checks

The report retains the strict all-photo correspondence status for each of the 98 original controls. A failed correspondence is never promoted by this projection experiment.

Separately, it creates a geometry-only route proposal. A proper similarity transform from the 60 matched turn-camera centers maps the old fit's coordinate frame into the neck reconstruction. It performs no per-route alignment. Camera alignment residual is recorded. The original fit can have shape bias, especially around the nose and neck; mapping coordinate frames does not correct that bias.

Each control is projected to source-proximate eligible triangles of the selected sigma 0.03 surface. The proposal permits offsets up to 0.15 eye-proxy spans to make the result reviewable. This is explicitly **not** the 0.04 automatic landmark acceptance gate. Larger proposal offsets are reported individually and need scrutiny; none inherit the old review status.

The established surface-routing code shortcuts triangle strips along the graph corridor while preserving projected controls. Disconnected edges remain gaps. Paths exceeding twice the endpoint chord or more than three times the original step (with a 0.15-span short-step allowance) are rejected as detours. Fallback counts are explicit. This is not an exact global geodesic or a physical tape simulation.

## Evidence along the whole route

Every routed polyline is sampled at interval midpoints with spacing at most 0.01 eye-proxy spans. Each sample represents an exact piece of polyline length, so coverage is length-weighted rather than a count of unevenly spaced controls.

A passing sample must be within 0.02 eye-proxy spans of quality raw surface samples and have at least three photo witnesses spanning three degrees. Witnesses require positive camera depth, a pixel inside the approved skin mask plus a three-pixel boundary allowance, visibility on the candidate surface, and a raw first-hit depth within 0.02 eye-proxy spans of the sample. Checks use full source photos; the learned network crop does not constrain geometric source coverage. Witness search stops once a sample qualifies, so successful witness counts are lower bounds.

This is sampled source consistency, not independent accuracy validation. Photogrammetry errors can survive it; small gaps between samples can remain. A newly smooth surface does not establish anatomy or mask contact pressure.

## Outputs and interpretation

`review.html` shows the neck surface and projected loop, optional aligned original guide, automatic correspondence control status, segment support, and projection offsets. Route overlays are drawn on top and may show through the surface; inspect several views. Display mesh decimation does not change the paths or their measured lengths.

`report.json` exports full-mesh triangle attachments, candidate controls, routed segments, sample evidence, input hashes and coordinate transform. It reports a geometry-proposal loop length only when every edge routes, and a source-supported proposal loop length only when all routed samples qualify. Supported portions remain partial; missing sections are never extrapolated. All lengths are reconstruction units. Accepted measurement and millimeter scale remain null pending route review and calibration. This export is not an accepted FLAME editor draft.

## Source-photo overlays

`python -m dimension_pipeline.mask_route_photos --review ROUTE_FOLDER --session NECK_SESSION --coverage ALL_PHOTO_FOLDER --neck NECK_VOLUME_FOLDER` adds six source-photo overlays after checking image, mask, camera and selected-mesh provenance. It writes `photos.json` separately, preserving the numeric route report and its hash. Only candidate-visible samples inside the source skin mask are drawn. Green samples pass the global sampled source checks; orange samples remain incomplete. The photograph toggle preserves a clear original-image view.

The 3D review initially lists only incomplete segments. The highlight selector locates them on the route; the full segment table and all control projection offsets remain available. Automatic correspondence status and geometry-only proposals stay separate throughout.
