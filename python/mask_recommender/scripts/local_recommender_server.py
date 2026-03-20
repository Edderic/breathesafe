import json
import os
import sys
from pathlib import Path

import boto3
import pandas as pd
import torch
from botocore.exceptions import ClientError
from flask import Flask, jsonify, request

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from mask_recommender.feature_builder import (  # noqa: E402
    FACIAL_FEATURE_COLUMNS,
    MASK_EMPIRICAL_FEATURE_COLUMNS,
    derive_brand_model,
)
from mask_recommender.train import (  # noqa: E402
    calc_preds,
    prep_data_in_torch_with_categories,
    _custom_lr_mask_categories,
)

APP = Flask(__name__)
APP.logger.setLevel("INFO")
DEFAULT_MODEL_TYPE = "custom_lr"


def _normalize_model_type(model_type):
    normalized = str(model_type or DEFAULT_MODEL_TYPE).strip()
    if not normalized or normalized == DEFAULT_MODEL_TYPE:
        return DEFAULT_MODEL_TYPE
    APP.logger.info("Coercing unsupported model_type=%s to %s", normalized, DEFAULT_MODEL_TYPE)
    return DEFAULT_MODEL_TYPE


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


def _custom_model_root() -> Path:
    override = os.environ.get("MASK_RECOMMENDER_LOCAL_CUSTOM_MODEL_DIR")
    if override:
        return Path(override).expanduser()
    return _model_root()


def _download_latest_custom_from_s3() -> Path:
    s3 = boto3.client("s3", region_name=_s3_region())
    bucket = _s3_bucket()
    latest_key = "mask_recommender/models/custom_latest.json"
    payload = json.loads(
        s3.get_object(Bucket=bucket, Key=latest_key)["Body"].read().decode("utf-8")
    )
    timestamp = payload.get("timestamp") or "latest"
    output_dir = _model_root() / f"custom_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    for key_name in ("params_key", "metadata_key", "mask_data_key"):
        key = payload[key_name]
        filename = Path(key).name
        target = output_dir / filename
        s3.download_file(bucket, key, str(target))

    return output_dir


def _artifact_timestamp(directory: Path, metadata_filename: str) -> str:
    metadata_path = directory / metadata_filename
    if metadata_path.exists():
        try:
            with metadata_path.open("r", encoding="utf-8") as handle:
                metadata = json.load(handle)
            timestamp = metadata.get("timestamp")
            if timestamp is not None:
                return str(timestamp)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass
    return directory.name


def _find_latest_custom_model_dir(base_dir: Path) -> Path:
    if base_dir.is_file():
        return base_dir.parent

    if (base_dir / "custom_model_params.pt").exists():
        return base_dir

    if not base_dir.exists():
        raise FileNotFoundError(f"Custom model directory not found: {base_dir}")

    candidates = [
        entry for entry in base_dir.iterdir()
        if entry.is_dir() and (entry / "custom_model_params.pt").exists()
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No custom model artifacts found in {base_dir}. Expected custom_model_params.pt"
        )

    return max(
        candidates,
        key=lambda candidate: _artifact_timestamp(candidate, "custom_model_metadata.json"),
    )


def _load_custom_artifacts(model_dir: Path):
    params_path = model_dir / "custom_model_params.pt"
    metadata_path = model_dir / "custom_model_metadata.json"
    mask_data_path = model_dir / "custom_mask_data.json"

    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    with mask_data_path.open("r", encoding="utf-8") as handle:
        mask_data = json.load(handle)

    params = torch.load(params_path, map_location="cpu")
    return {
        "params": params,
        "metadata": metadata,
        "mask_data": mask_data,
    }


def _ensure_custom_artifacts(force_reload=False):
    if force_reload:
        APP.config.pop("custom_artifacts", None)
    if "custom_artifacts" in APP.config:
        return APP.config["custom_artifacts"]

    try:
        local_dir = _find_latest_custom_model_dir(_custom_model_root())
        APP.logger.info("Loaded local custom artifacts from: %s", local_dir)
        APP.config["custom_artifacts"] = _load_custom_artifacts(local_dir)
        return APP.config["custom_artifacts"]
    except FileNotFoundError:
        pass

    try:
        custom_dir = _download_latest_custom_from_s3()
        APP.config["custom_artifacts"] = _load_custom_artifacts(custom_dir)
        return APP.config["custom_artifacts"]
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            raise FileNotFoundError(
                "No custom LR artifacts found locally, and s3://"
                f"{_s3_bucket()}/mask_recommender/models/custom_latest.json does not exist."
            ) from exc
        raise


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
            "fit_family_id": mask_info.get("fit_family_id"),
            "perimeter_mm": perimeter,
            "strap_type": mask_info.get("strap_type") or "",
            "style": mask_info.get("style") or "",
            "brand_model": mask_info.get("brand_model") or derive_brand_model(
                mask_info.get("unique_internal_model_code"),
                mask_info.get("current_state")
            ),
            "unique_internal_model_code": mask_info.get("unique_internal_model_code") or "",
            "facial_hair_beard_length_mm": facial_features.get("facial_hair_beard_length_mm", 0) or 0,
        }
        for col in FACIAL_FEATURE_COLUMNS:
            row[col] = facial_features.get(col, 0) or 0
        for col in MASK_EMPIRICAL_FEATURE_COLUMNS:
            row[col] = mask_info.get(col, 0) or 0
        rows.append(row)
    return pd.DataFrame(rows)


def _infer_custom(payload, artifacts):
    facial_features = _extract_facial_measurements(payload)
    inference_rows = _build_inference_rows(artifacts["mask_data"], facial_features)
    custom_data = prep_data_in_torch_with_categories(
        inference_rows,
        mask_categories=_custom_lr_mask_categories(artifacts["metadata"]),
        style_categories=artifacts["metadata"]["style_categories"],
        strap_categories=artifacts["metadata"]["strap_type_categories"],
    )

    with torch.no_grad():
        probs = calc_preds(custom_data, artifacts["params"]).squeeze(1).cpu().tolist()

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
    empirical_debug_map = {
        str(idx): {
            "mask_fit_test_count": float(rec["mask_info"].get("mask_fit_test_count", 0) or 0),
            "mask_pass_count": float(rec["mask_info"].get("mask_pass_count", 0) or 0),
            "mask_smoothed_pass_rate": float(rec["mask_info"].get("mask_smoothed_pass_rate", 0.5) or 0.5),
        }
        for idx, rec in enumerate(recommendations)
    }
    return {
        "mask_id": mask_id_map,
        "proba_fit": proba_map,
        "model": {
            **artifacts["metadata"],
            "empirical_debug": empirical_debug_map,
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

    train_argv = []
    if (payload or {}).get("epochs") is not None:
        train_argv.extend(["--epochs", str(payload["epochs"])])
    if (payload or {}).get("learning_rate") is not None:
        train_argv.extend(["--learning-rate", str(payload["learning_rate"])])
    train_argv.extend(["--model-type", _normalize_model_type((payload or {}).get("model_type"))])
    if (payload or {}).get("class_reweight"):
        train_argv.append("--class-reweight")
    if (payload or {}).get("retrain_with_full"):
        train_argv.append("--retrain-with-full")

    result = train_main(train_argv)

    custom_artifacts = _ensure_custom_artifacts(force_reload=True)
    reload_status = {
        "status": "reloaded",
        "model_type": "custom_lr",
        "timestamp": custom_artifacts["metadata"].get("timestamp"),
        "environment": custom_artifacts["metadata"].get("environment"),
    }
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
    if payload.get("method") == "warmup":
        _normalize_model_type(payload.get("model_type"))
        try:
            custom_artifacts = _ensure_custom_artifacts()
        except (ClientError, FileNotFoundError) as exc:
            return jsonify({
                "error": "Custom LR artifacts are not available locally or in S3.",
                "details": str(exc),
            }), 503
        return jsonify({
            "status": "warmed",
            "model_type": "custom_lr",
            "model": custom_artifacts["metadata"],
        })
    _normalize_model_type(payload.get("model_type"))
    try:
        custom_artifacts = _ensure_custom_artifacts()
    except (ClientError, FileNotFoundError) as exc:
        return jsonify({
            "error": "Custom LR artifacts are not available locally or in S3.",
            "details": str(exc),
        }), 503
    return jsonify(_infer_custom(payload, custom_artifacts))


@APP.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


def main():
    artifacts = _ensure_custom_artifacts()
    timestamp = artifacts["metadata"].get("timestamp")
    environment = artifacts["metadata"].get("environment")
    print("Loaded local custom model")
    print(f"Model timestamp: {timestamp} (env={environment})")

    host = os.environ.get("MASK_RECOMMENDER_LOCAL_HOST", "127.0.0.1")
    port = int(os.environ.get("MASK_RECOMMENDER_LOCAL_PORT", "5055"))
    APP.run(host=host, port=port)


if __name__ == "__main__":
    main()
