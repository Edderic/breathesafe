# RealDenseFace EC2 trial proposal

Prepared 2026-11-07. **No instance launched and no face photos uploaded.**

Use one Linux `g6.2xlarge` in `us-east-1`: 1 NVIDIA L4 (24 GB), 8 vCPU,
32 GiB RAM. The extra RAM over g6.xlarge gives the CUDA extension build room.
Use a current Ubuntu Deep Learning AMI with NVIDIA driver, CUDA toolkit and an
activated Python 3.11 / compatible CUDA PyTorch environment. Resolve and record
the exact AMI and installed package versions when launching; no unverified AMI
identifier is embedded here. Check the regional G-instance quota first.

## Cost and lifetime

AWS's public Linux On-Demand price feed, publication 2026-11-07T00:28:52Z,
quotes **$0.9776/hour** for g6.2xlarge in N. Virginia. Three hours of compute
cost **$2.9328**. Budget **$5 for the first trial**, allowing small storage,
network and tax charges; this is an estimate, not a billing hard cap. Recheck
prices at launch. No Spot interruption risk for this first build.

Use an encrypted 80 GiB gp3 root volume with DeleteOnTermination. Set a shutdown
timer at launch (`sudo shutdown -h +180`), and configure EC2 instance-initiated
shutdown behavior to **terminate**, not stop. That timer depends on the guest
remaining functional; independently verify termination from the account. Retrieve
results before the deadline. Stopped instances still incur EBS charges.
Prefer SSM access, no inbound public ports, and IMDSv2. Launch, IAM/SSM details,
credentials and transfer of the selected private photos require a separate user
instruction; this proposal does not authorize them.

Sources: [AWS G6 specifications](https://aws.amazon.com/ec2/instance-types/g6/),
[AWS public regional Linux price feed](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json).

## Source, assets and compatibility

Audited source commit: `7d855a29931c95cc9016f75d49cead60adbcf0a3`.
Code has an MIT license. The released model repository also declares MIT;
its README explicitly retains separate terms for third-party resources. Record
checkpoint SHA256s and retain the accompanying licenses before use. No MICA
initializer or Ava256 training dataset is needed for this inference trial.

The official scripts default to the separately licensed `flame2023.pkl`.
Pass our actual **FLAME 2023 Open** pickle with `--flame_model`; do not rename a
restricted release to Open. Local array checks show that Open has the same
9,976-triangle topology as `flame_assets.npz`, 300 identity plus 100 expression
directions, 36 pose correctives and five-joint skinning weights. This establishes
structural compatibility only. Open's expression basis may differ from the
release used by the authors: evaluate neutral meshes and expression leakage,
and label the substitution in all results. The CUDA execution and checkpoint
behavior have **not** yet been tested with Open.

Expected externally supplied files:

```
weights/facebox/face_box.pth
weights/flame/flame_assets.npz
weights/realdenseface/vitb.pth
weights/realdenseface/vits.pth
/private/models/flame2023_Open.pkl
```

[Official code and requirements](https://github.com/LinzhouLi/RealDenseFace),
[released model card](https://huggingface.co/LinzhouLi/RealDenseFace),
[FLAME Open terms](https://flame.is.tue.mpg.de/modellicense.html#open-model-license).

## Trial procedure

1. Run the local photo baseline and prepare its exact train/hold-out photo bundle:

   ```bash
   PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.realdenseface_trial \
     --session .private-webcam-runs/c79e26de178a434aa3f20682fdb087ed \
     --baseline-report .private-webcam-runs/flame-fits/c79e26de-direct-photo-100-prior100/report.json \
     --out .private-webcam-runs/realdenseface-trial/c79e26de-photo-eval
   ```

   This copies only the 13 selected original photos plus a hash manifest. It does
   not copy credentials, unrelated captures, calibration drafts or model assets.
   It performs no network operation. Verify the hashes again after any transfer.

2. On the approved GPU host, activate the environment and run
   `bash scripts/realdenseface_trial_setup.sh /absolute/new/trial-directory`.
   This installs the pinned project revision and builds its CUDA solver. Upstream
   Python dependencies are not fully pinned; freeze the resolved environment in
   the output. This setup script is syntax checked locally, **not CUDA tested**.

3. Obtain and verify the checkpoint/assets; run one training image first:

   ```bash
   python fit_single_image.py --input /private/trial/train/front.png \
     --flame_model /private/models/flame2023_Open.pkl \
     --output_npz /private/results/front.npz \
     --output_image /private/results/front.jpg --no_compile
   ```

4. Run shared-identity fitting with the nine training photos only:

   ```bash
   python track_video_offline.py --input /private/trial/train --discontinuous \
     --flame_model /private/models/flame2023_Open.pkl \
     --output_npz /private/results/shared-identity.npz --no_compile
   ```

   Frame directories and `--discontinuous` are supported by the audited source.
   Keep the native, uncropped image framing. Record estimated focal/FOV; the
   stock search range is a potential source of bias for these captures. Record
   initialization, seed, wall time, GPU peak memory and solver stop conditions.

5. Freeze the training identity before evaluating the four hold-out photos.
   The stock offline CLI does not implement this evaluation protocol: add a
   fixed-identity pose/expression adapter before claiming hold-out results.
   Do **not** run a second shared identity fit on the hold-out directory and call
   that a hold-out evaluation. Compare neutral identity meshes separately from
   expression-deformed per-photo meshes.

## Decision criteria

Compare the direct-photo baseline, existing reconstruction-fit FLAME, and RDF
using matched photos and overlays. Inspect nasal bridge height, nose projection,
lower jaw and menton from frontal and oblique views. Existing FLAME point and
perimeter attachments can be recomputed by original triangle/barycentric indices;
retain their pending review status and do not copy physical scale.

Report detector reprojection on held-out photos (including a nose subset excluded
from baseline pose estimation), repeated-photo-subset variation in the requested
lengths, and model-vs-photo contour differences. Detector residuals and consistency
are diagnostics, not anatomical accuracy. Before selecting a method for people,
collect repeated captures plus independent measured distances/arcs, using one tape
route for scale and separate measurements for validation. One participant/session
cannot establish performance across faces, cameras or lighting.

First go/no-go: does Open execute correctly and does the neutral RDF nose improve
visually without hiding errors in expression/camera parameters? A failed install,
model incompatibility or exhausted three-hour window ends the first trial; retain
logs and propose the next step before spending more.
