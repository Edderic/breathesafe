# Photogrammetry and automatic correspondence experiments

Run these offline modules with the existing webcam pilot Python environment. They do not modify source sessions, model assets, annotations, or calibration.

`python -m dimension_pipeline.photogrammetry_trial --session SESSION --predictions PREDICTION_FOLDER --model FLAME_OPEN_ZIP --out NEW_FOLDER`

The prediction folder is an existing `realdenseface_local` output. Original image hashes must match. The trial uses fixed COLMAP SIMPLE_RADIAL cameras, including lens distortion. It does not use FLAME fitted shape, fitted cameras, or predicted relative depth to estimate points. The neutral FLAME model supplies vertex identities and a geometric sampling region only.

For a reconstruction of the same photos with different masks, add `--reference-session ORIGINAL_SESSION`. This transfers the reference eye-proxy normalizer using matched camera baseline ratios. Add `--reference-trial ORIGINAL_REPORT_JSON` to retain the exact recorded reference span used in an earlier trial. Independently ray-cast eye spans can differ markedly when eye geometry is noisy. Check the reported ratio spread before interpreting paired results.

Outputs include a local `review.html`, nine original-photo overlays, raw/smoothed front and profile previews, three full-topology PLY variants, and `report.json` with input hashes and point attachments. New output directories must not exist.

## Settings and interpretation

- Up to 300 lower-template and 300 other vertices, deterministically sampled. The lower region is template y < -0.055, z > -0.045. These coordinates do not define validated anatomical landmarks.
- Pair-consensus triangulation, inlier-only multi-view DLT, 6-pixel reprojection tolerance, at least three agreeing views, and maximum ray angle at least 3 degrees.
- Surface attachment within 0.04 reference eye-proxy spans and at least three unoccluded surface observations consistent with the original image predictions.
- Thresholds are exploratory, not calibrated confidence probabilities. Correlated neural bias can pass these checks. Out-of-view points and back-facing/occluded predictions must not be treated as measurements merely because the network outputs coordinates.
- Taubin lambda 0.5 / nu 0.53, one, three, and five shrink/dilate cycles. Boundary vertices are pinned. All variants start independently from the raw full mesh. No hole filling. Normals can change direction in noisy folded regions; self-intersections are not checked.
- Preview decimation is display-only. Geometry experiments and exported PLY files retain the full original topology. Raw and variant preview framing is shared.

## Measurement guide experiment

`python -m dimension_pipeline.photogrammetry_routes --session SESSION --trial TRIAL_FOLDER --predictions PREDICTION_FOLDER --measurements STYLE_SPECIFIC_JSON --model FLAME_OPEN_ZIP`

This reads the existing direct-measurement file as a reusable recipe. It interpolates the three corresponding dense vertex image predictions for each saved barycentric point. These are approximate candidate image correspondences, not accepted anatomical placements. It triangulates and checks each candidate against the reconstruction.

`automatic-routes.json` reports nose/bridge chords and fixed-control smoothing sensitivity. Arc lengths use mesh-edge shortest paths between nearest face vertices plus endpoint offsets. This approximation can overestimate smooth surface lengths, and a tape may bridge concavities. Missing controls, failed visibility, and disconnected components leave complete lengths null. Partial lengths do not estimate a complete perimeter. Saved reviews and scale do not transfer.

The same raw attachments are evaluated on each smoothing variant to isolate smoothing effects; point support is not re-certified on each variant. The route support measure counts edges between saved controls, unlike the older FLAME arc report's densely resampled edge counts. Those percentages are not directly comparable.

Before accepting measurements, inspect long or skinny triangles, multi-view correspondence overlays, and independent repeat captures. A ray hit on an artificial meshing skirt is not reliable anatomical support. This trial does not establish millimeter accuracy or an automatic production measurement workflow.

## Paired review and quality audit

`python -m dimension_pipeline.photogrammetry_review --trials ORIGINAL_TRIAL EXPANDED_TRIAL --out PARENT_FOLDER --model FLAME_OPEN_ZIP`

Builds `comparison.html` and `comparison.json`. An additional triangle-quality audit rejects supported sample/guide candidates on edges longer than 0.12 reference eye spans or aspect proxy (longest edge squared divided by double area) above 12. This targets artificial meshing skirts. The original trial and route reports remain available as earlier diagnostic stages, and their lengths are not certified by this audit. The final paired counts supersede their simpler support counts.
