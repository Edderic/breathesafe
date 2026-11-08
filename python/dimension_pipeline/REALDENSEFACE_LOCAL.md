# RealDenseFace neural predictions on CPU and Apple Silicon

Local evaluation, 2026-11-08, Apple M3 Pro. **No EC2 instance or photo upload.**
The official ViT-S prediction network runs on both PyTorch CPU and MPS (Metal).
The stock end-to-end program does not: its inference wrapper unconditionally
constructs `nvdiffrast.RasterizeCudaContext`, and its FLAME optimization imports
the custom `flame_solver` CUDA extension.

This adapter imports only the prediction network and crop helpers from audited
source commit `7d855a29931c95cc9016f75d49cead60adbcf0a3`. It does not pretend that
`--device cpu` replaces those two CUDA components.

## Observed results

| Backend | First forward | Second forward |
| --- | ---: | ---: |
| CPU, four PyTorch threads | 1.648 s | 1.283 s |
| Apple GPU / MPS | 3.050 s | 0.113 s |

These are neural-forward plus UV-sampling times for the first photo, not
end-to-end reconstruction times. Each photo uses two forwards: one to refine
the initial crop, one to generate retained predictions. Model construction and
checkpoint loading took 1.26 s on CPU and 2.28 s on MPS separately. GPU timing
explicitly synchronizes Metal. Warm timings should not be confused with cold
startup, which can include backend/kernel initialization.

Both produced finite predictions for all 5,023 FLAME vertices. The CPU/MPS
native-image coordinate RMS difference was **0.000086 pixels**; maximum
0.000306 pixels. This tests backend agreement, not anatomical accuracy.
The Metal run also completed on all nine selected training photos, with finite
5,023-vertex outputs for each and a median of 0.122 seconds per forward.

Outputs are 2D dense correspondences, relative depth and learned uncertainty.
They are **not** a fitted FLAME mesh or calibrated physical measurements.

## Local setup and execution

Use an isolated environment so the existing MediaPipe/reconstruction environment
stays unchanged. The tested environment uses Python 3.12.13, torch 2.15.0,
torchvision 0.29.2, timm 1.0.31, PyYAML 6.0.3, roma 1.8.0 and numpy 2.5.4.
The upstream CUDA setup recommends Python 3.11; this neural-only 3.12 execution
was tested separately. A package freeze is stored with the private local run.

```bash
uv venv tmp/realdenseface-local-venv --python 3.12
uv pip install --python tmp/realdenseface-local-venv/bin/python \
  torch torchvision timm PyYAML roma opencv-python scipy trimesh
```

Obtain the official ViT-S checkpoint and `flame_assets.npz` from the
[released model repository](https://huggingface.co/LinzhouLi/RealDenseFace).
The adapter checks the published SHA256s before loading and uses
`torch.load(weights_only=True)` with strict parameter matching. It disables
DINO pretrained downloads because the checkpoint contains the full network.
No FLAME model is required merely to predict the neural priors.

```bash
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 \
  tmp/realdenseface-local-venv/bin/python -m dimension_pipeline.realdenseface_local \
  --source tmp/realdenseface-audit \
  --weights tmp/realdenseface-vits.pth \
  --assets tmp/realdenseface-flame-assets.npz \
  --session .private-webcam-runs/c79e26de178a434aa3f20682fdb087ed \
  --baseline-report .private-webcam-runs/flame-fits/c79e26de-direct-photo-100-prior100/report.json \
  --landmarks .private-webcam-runs/flame-fits/c79e26de-direct-photo-100-prior100/landmarks.json \
  --out .private-webcam-runs/realdenseface-local/NEW-private-trial \
  --device mps --slots front,turn_11,turn_22
```

Use `--device cpu` for CPU execution. The macOS sandbox may conceal the Metal
device; the MPS test needs native device access. No silent CPU fallback is used.

The initial face box comes from the already cached MediaPipe landmarks instead
of upstream FaceBox. Both passes use upstream square cropping/enlargement,
ImageNet normalization, 512px inputs, UV `grid_sample(align_corners=False)` and
original-pixel remapping. Every input image/cache hash must match the existing
photo manifest. Source code, weights and model assets remain outside Git.

**Visibility is unfiltered.** This adapter does not port the CUDA rasterizer.
Far-side/occluded predictions must not be treated as surface observations.
The saved preview shows the published visualization-edge vertex subset, not
necessarily only the visible vertices. No FLAME head-fitting evaluation or
mask measurements can be claimed from these previews.

## Next local stage

The feasible next step is a separately labeled experimental fitter using the
predicted dense correspondences and relative-depth priors, CPU or Metal
optimization, and a CPU visibility test. Preserve uncertainty weighting,
projection/crop conventions, neutral identity vs expression, and the same
train/validation split. Test that port against the official CUDA solver before
claiming numerical equivalence or replacing it for an accuracy comparison.
The current SciPy multi-photo FLAME fitter provides a starting camera/shape
baseline, but swapping its sparse landmarks for all unfiltered predictions
would not reproduce RealDenseFace.

The [EC2 proposal](REALDENSEFACE_TRIAL.md) remains an option for testing the
unmodified CUDA fitting path. Successful local neural inference means CUDA is
not necessary for the neural prediction stage; it does not eliminate the
remaining optimizer and visibility work.
