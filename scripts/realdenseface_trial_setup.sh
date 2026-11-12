#!/usr/bin/env bash
# Run ONLY on an explicitly approved NVIDIA/CUDA host in an activated Python 3.11 environment.
# Does not launch EC2, upload captures, obtain FLAME, or start fitting.
set -euo pipefail
trial_root="${1:?Usage: bash scripts/realdenseface_trial_setup.sh /absolute/new/trial-directory}"
if [ -e "$trial_root" ]; then
  echo 'Choose a new trial directory.' >&2
  exit 1
fi
python - <<'PY'
import sys, torch
assert sys.version_info[:2] == (3, 11), 'Activate Python 3.11 first'
assert torch.cuda.is_available(), 'A CUDA-enabled PyTorch installation and NVIDIA driver are required'
print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0))
PY
nvcc --version
mkdir -p "$trial_root"
trial_root="$(cd "$trial_root" && pwd)"
git clone https://github.com/LinzhouLi/RealDenseFace.git "$trial_root/source"
git -C "$trial_root/source" checkout --detach 7d855a29931c95cc9016f75d49cead60adbcf0a3
export MAX_JOBS=4
export TORCH_CUDA_ARCH_LIST=8.9
python -m pip install -r "$trial_root/source/requirements.txt"
python -m pip install -e "$trial_root/source/cuda_extensions/flame_solver" --no-build-isolation
python -m pip freeze > "$trial_root/environment.txt"
nvidia-smi > "$trial_root/nvidia-smi.txt"
printf '%s\n' 'Source and solver built. Weights, FLAME Open compatibility and photo transfer still require their documented checks.'
