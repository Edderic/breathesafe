import json
import os
import sys
from pathlib import Path

import boto3
import pandas as pd
import torch
from flask import Flask, jsonify, request

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from mask_recommender.feature_builder import (  # noqa: E402
    FACIAL_FEATURE_COLUMNS,
    build_feature_frame,
)

APP = Flask(__name__)


def _env_name() -> str:
    env = os.environ.get("RAILS_ENV", "").strip().lower()
    if env in ("production", "staging", "development"):
        return env
    return "development"


def _s3_bucket() -> str:
    mapping = {
        "production": "breathesafe",
        "staging": "breathesafe-staging",
        "development": "breathesafe-development",
    }
    return mapping[_env_name()]


def _s3_region() -> str:
    return os.environ.get("S3_BUCKET_REGION") or os.environ.get("AWS_REGION") or "us-east-1"


def _model_root() -> Path:
    override = os.environ.get("MASK_RECOMMENDER_LOCAL_MODEL_DIR")
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parents[1] / "local_models"


def _download_latest_from_s3() -> Path:
    s3 = boto3.client("s3", region_name=_s3_region())
    bucket = _s3_bucket()
    latest_key = "mask_recommender/models/latest.json"
    payload = json.loads(
        s3.get_object(Bucket=bucket, Key=latest_key)["Body"].read().decode("utf-8")
    )
    timestamp = payload.get("timestamp") or "latest"
    output_dir = _model_root() / str(timestamp)
    output_dir.mkdir(parents=True, exist_ok=True)

    for key_name in ("model_key", "metadata_key", "mask_data_key"):
        key = payload[key_name]
        filename = Path(key).name
        target = output_dir / filename
        s3.download_file(bucket, key, str(target))

    return output_dir


def _default_model_dir() -> Path:
    return _model_root()


def _find_latest_model_dir(base_dir: Path) -> Path:
    if base_dir.is_file():
        return base_dir.parent

    if (base_dir / "model_state_dict.pt").exists():
        return base_dir

    if not base_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {base_dir}")

    candidates = [
        entry for entry in base_dir.iterdir()
        if entry.is_dir() and (entry / "model_state_dict.pt").exists()
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No model artifacts found in {base_dir}. Expected model_state_dict.pt"
        )

    return sorted(candidates)[-1]


def _load_artifacts(model_dir: Path):
    model_path = model_dir / "model_state_dict.pt"
    metadata_path = model_dir / "model_metadata.json"
    mask_data_path = model_dir / "mask_data.json"

    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    with mask_data_path.open("r", encoding="utf-8") as handle:
        mask_data = json.load(handle)

    feature_columns = metadata["feature_columns"]
    categorical_columns = metadata["categorical_columns"]
    hidden_sizes = metadata.get("hidden_sizes", [32, 16])
    input_dim = len(feature_columns)
    model = torch.nn.Sequential(
        torch.nn.Linear(input_dim, hidden_sizes[0]),
        torch.nn.ReLU(),
        torch.nn.Linear(hidden_sizes[0], hidden_sizes[1]),
        torch.nn.ReLU(),
        torch.nn.Linear(hidden_sizes[1], 1),
    )
    state_dict = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    return {
        "model": model,
        "feature_columns": feature_columns,
        "categorical_columns": categorical_columns,
        "mask_data": mask_data,
        "metadata": metadata,
    }


def _extract_facial_measurements(payload):
    if not payload:
        return {}

    if "facial_measurements" in payload:
        return payload.get("facial_measurements") or {}

    nested = payload.get("mask_recommender") or {}
    return nested.get("facial_measurements") or {}


def _build_inference_rows(mask_data, facial_features):
    rows = []
    for mask_id, mask_info in mask_data.items():
        perimeter = mask_info.get("perimeter_mm")
        if perimeter is None or (isinstance(perimeter, float) and pd.isna(perimeter)):
            perimeter = 0
        row = {
            "mask_id": int(mask_id),
            "perimeter_mm": perimeter,
            "strap_type": mask_info.get("strap_type") or "",
            "style": mask_info.get("style") or "",
            "unique_internal_model_code": mask_info.get("unique_internal_model_code") or "",
            "facial_hair_beard_length_mm": facial_features.get("facial_hair_beard_length_mm", 0) or 0,
        }
        for col in FACIAL_FEATURE_COLUMNS:
            row[col] = facial_features.get(col, 0) or 0
        rows.append(row)
    return pd.DataFrame(rows)


def _infer(payload, artifacts):
    facial_features = _extract_facial_measurements(payload)
    inference_rows = _build_inference_rows(artifacts["mask_data"], facial_features)

    numeric_columns = FACIAL_FEATURE_COLUMNS + ["perimeter_mm"]
    numeric_frame = pd.DataFrame(
        {
            col: pd.to_numeric(inference_rows.get(col), errors="coerce")
            for col in numeric_columns
        }
    )
    numeric_frame = numeric_frame.replace([float("inf"), float("-inf")], float("nan")).fillna(0)
    inference_rows[numeric_columns] = numeric_frame

    encoded = build_feature_frame(
        inference_rows,
        feature_columns=artifacts["feature_columns"],
        categorical_columns=artifacts["categorical_columns"],
        use_facial_perimeter=artifacts["metadata"].get("use_facial_perimeter", False),
        use_diff_perimeter_bins=artifacts["metadata"].get("use_diff_perimeter_bins", False),
        use_diff_perimeter_mask_bins=artifacts["metadata"].get("use_diff_perimeter_mask_bins", False),
    )

    inputs = torch.tensor(encoded.to_numpy(), dtype=torch.float32)
    with torch.no_grad():
        logits = artifacts["model"](inputs).squeeze(1)
        probs = torch.sigmoid(logits).cpu().tolist()

    recommendations = []
    for idx, (mask_id, mask_info) in enumerate(artifacts["mask_data"].items()):
        recommendations.append({
            "mask_id": int(mask_id),
            "proba_fit": float(probs[idx]),
            "mask_info": mask_info,
        })

    recommendations.sort(key=lambda item: item["proba_fit"], reverse=True)
    mask_id_map = {str(idx): rec["mask_id"] for idx, rec in enumerate(recommendations)}
    proba_map = {str(idx): rec["proba_fit"] for idx, rec in enumerate(recommendations)}
    return {
        "mask_id": mask_id_map,
        "proba_fit": proba_map,
        "model": {
            "timestamp": artifacts["metadata"].get("timestamp"),
            "environment": artifacts["metadata"].get("environment"),
        }
    }


def _train(payload):
    env = (payload or {}).get("environment") or os.environ.get("ENVIRONMENT") or "development"
    base_url = (payload or {}).get("base_url") or os.environ.get("BREATHESAFE_BASE_URL")
    if env:
        os.environ["ENVIRONMENT"] = str(env)
        os.environ["RAILS_ENV"] = str(env)
    if base_url:
        os.environ["BREATHESAFE_BASE_URL"] = str(base_url)
    os.environ.setdefault("MPLBACKEND", "Agg")

    from mask_recommender.train import main as train_main  # noqa: E402

    result = train_main()

    reload_status = reload_model().get_json()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Training completed successfully",
            "result": result,
            "reload": reload_status,
        }),
    }


@APP.route("/mask_recommender", methods=["POST"])
@APP.route("/mask_recommender.json", methods=["POST"])
def recommend_masks():
    payload = request.get_json(silent=True) or {}
    if payload.get("method") == "train":
        return jsonify(_train(payload))
    return jsonify(_infer(payload, APP.config["artifacts"]))


@APP.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@APP.route("/reload", methods=["POST"])
def reload_model():
    try:
        s3_dir = _download_latest_from_s3()
        resolved_dir = _find_latest_model_dir(s3_dir)
        artifacts = _load_artifacts(resolved_dir)
        APP.config["artifacts"] = artifacts

        timestamp = artifacts["metadata"].get("timestamp")
        environment = artifacts["metadata"].get("environment")
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500
    return jsonify({
        "status": "reloaded",
        "model_dir": str(resolved_dir),
        "timestamp": timestamp,
        "environment": environment,
    })


def main():
    model_dir_env = os.environ.get("MASK_RECOMMENDER_LOCAL_MODEL_DIR")
    if model_dir_env:
        model_dir = Path(model_dir_env).expanduser()
    else:
        model_dir = _default_model_dir()

    resolved_dir = _find_latest_model_dir(model_dir)
    artifacts = _load_artifacts(resolved_dir)
    APP.config["artifacts"] = artifacts

    timestamp = artifacts["metadata"].get("timestamp")
    environment = artifacts["metadata"].get("environment")
    print(f"Loaded local model from: {resolved_dir}")
    print(f"Model timestamp: {timestamp} (env={environment})")

    host = os.environ.get("MASK_RECOMMENDER_LOCAL_HOST", "127.0.0.1")
    port = int(os.environ.get("MASK_RECOMMENDER_LOCAL_PORT", "5055"))
    APP.run(host=host, port=port)


if __name__ == "__main__":
    main()
