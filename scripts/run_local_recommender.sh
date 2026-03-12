#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export AWS_PROFILE="${AWS_PROFILE:-breathesafe}"
export RAILS_ENV="${RAILS_ENV:-development}"
export BREATHESAFE_BASE_URL="${BREATHESAFE_BASE_URL:-http://localhost:3000}"
export LOCAL_RECOMMENDER_WARM_MODELS="${LOCAL_RECOMMENDER_WARM_MODELS:-}"

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
if [[ -n "${LOCAL_RECOMMENDER_WARM_MODELS}" ]]; then
  echo "==> Will warm local recommender models after startup: ${LOCAL_RECOMMENDER_WARM_MODELS}"
fi

(
  python "$ROOT_DIR/python/mask_recommender/scripts/local_recommender_server.py"
) &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [[ -n "${LOCAL_RECOMMENDER_WARM_MODELS}" ]]; then
  sleep 2
  IFS=',' read -r -a MODELS <<< "${LOCAL_RECOMMENDER_WARM_MODELS}"
  for model in "${MODELS[@]}"; do
    model="$(echo "$model" | xargs)"
    [[ -z "$model" ]] && continue
    echo "==> Warming model_type=${model}"
    curl -sf \
      -H 'Content-Type: application/json' \
      -d "{\"method\":\"warmup\",\"model_type\":\"${model}\"}" \
      "http://127.0.0.1:5055/mask_recommender" >/dev/null || {
        echo "==> Warmup failed for model_type=${model}"
      }
  done
fi

wait "$SERVER_PID"
