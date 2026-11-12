# Neck-inclusive surfaces and all-photo correspondence review

Use the previously reconstructed, individually approved expanded upper-neck mask session `14ff5d878cf748558e6406b4d07b639a`. Its 61 photos are the same pixels as source session `c79e26de178a434aa3f20682fdb087ed`; the reconstruction masks retain additional skin below the jaw. No new image capture, mask approval, or cloud upload is performed by these tools.

## Neck geometry

```
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m dimension_pipeline.neck_volume \
  --session .private-webcam-runs/14ff5d878cf748558e6406b4d07b639a \
  --trial .private-webcam-runs/photogrammetry/expanded-neck-auto-smoothing-v3 \
  --reference .private-webcam-runs/gaussian-volume/c79e26de-sweep-v1 \
  --out .private-webcam-runs/gaussian-volume/NEW_NECK_RUN
```

This preserves the existing raw neck reconstruction and creates zero-filter and sigma 0.03 candidates. Grid resolution targets the original fine-grid voxel size relative to the shared reference eye-proxy span, rather than keeping a fixed grid dimension as the neck extends the bounding box. Record the actual voxel size and shape. The same oriented-field and support limitations from `GAUSSIAN_VOLUME.md` apply.

The review includes selected masked source photographs and a contact sheet of all 61 approved masks. Green pixels show retained source regions. Counts below a fixed menton camera-height plane are geometric coverage proxies, not anatomical neck segmentation or validation of every triangle. The upper neck is reconstructed only where the source supports it; the lower boundary can remain fragmented. Reference menton uses index 3 in this source's checked style-specific candidate recipe.

## All-photo neural inputs

`python -m dimension_pipeline.all_photo_prepare` requires `--session`, `--face-session` (original face-only masks), `--cache` (existing landmark JSON), and `--out` (new or empty directory). It verifies approved unmirrored image hashes and registration, reuses hash-matched MediaPipe detections, and computes missing detections. If face detection fails, an explicitly marked fallback can use the original approved head-mask bounding box. It never uses an expanded-neck mask as a face box or fabricates MediaPipe landmarks.

On macOS the MediaPipe backend may need native graphics access even for CPU operation. The existing `realdenseface_local` adapter accepts the resulting `report.json`/`landmarks.json` as crop inputs and `--slots all`. Its published weights, assets and source revision checks remain unchanged. Use the local Metal environment for MPS or its CPU option; no CUDA solver is involved.

## All-photo support evaluation

```
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 tmp/webcam-pilot-venv/bin/python \
  -m dimension_pipeline.all_photo_evaluate \
  --session .private-webcam-runs/14ff5d878cf748558e6406b4d07b639a \
  --predictions .private-webcam-runs/realdenseface-local/expanded-neck-all61 \
  --trial .private-webcam-runs/photogrammetry/expanded-neck-auto-smoothing-v3 \
  --neck .private-webcam-runs/gaussian-volume/expanded-neck-selected-003-v1 \
  --measurements /path/to/flame-direct-style-specific.json \
  --model /path/to/FLAME2023Open.zip \
  --out .private-webcam-runs/all-photo-coverage/NEW_RUN
```

The evaluation compares nine versus all registered photos using identical gates. An observation must be inside the original image, inside the network's refined crop, and within the approved neck mask plus a three-pixel boundary allowance. Predictions outside the crop are not observations of neck skin, even if that skin is visible in the full photograph.

Triangulation uses at most 96 deterministic pair hypotheses per candidate, followed by inlier-only DLT, the same six-pixel reprojection tolerance, at least three views, and at least three degrees of parallax. Batched first-hit ray tests reject occluded surface attachments. Original photogrammetry cameras remain fixed; no fitted FLAME shape or camera enters the geometric estimate. The FLAME model supplies only correspondence identities and the below-menton sampling region.

Each candidate must be within 0.04 eye-proxy spans of the raw surface and pass triangle quality and raw-source proximity checks. A smoothed point can qualify only if its raw counterpart qualifies. Newly closed Gaussian holes cannot introduce accepted points. Reported statuses are experimental support diagnostics; no anatomical acceptance, complete-perimeter claim or millimeter scale transfers.

Neck photographs overlay the actual network crop (blue), passing visible smoothed candidates (green), other predicted locations (orange), and crop/image/mask-excluded predictions (gray). Learned correspondences can have correlated bias, and geometric agreement is not independent accuracy validation.
