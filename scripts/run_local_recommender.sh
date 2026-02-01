#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export AWS_PROFILE="${AWS_PROFILE:-breathesafe}"
export RAILS_ENV="${RAILS_ENV:-development}"
export BREATHESAFE_BASE_URL="${BREATHESAFE_BASE_URL:-http://localhost:3000}"

echo "==> Using AWS_PROFILE=${AWS_PROFILE}"
echo "==> Using RAILS_ENV=${RAILS_ENV}"

if [[ "${NO_DOWNLOAD:-0}" != "1" ]]; then
  echo "==> Downloading latest NN model artifacts from S3..."
  python "$ROOT_DIR/python/mask_recommender/scripts/download_latest_nn_model.py"
else
  echo "==> Skipping download (NO_DOWNLOAD=1)"
fi

echo "==> Starting local recommender server..."
echo "==> Set LOCAL_LAMBDA_URL=http://127.0.0.1:5055/mask_recommender to route Rails locally."
python "$ROOT_DIR/python/mask_recommender/scripts/local_recommender_server.py"
