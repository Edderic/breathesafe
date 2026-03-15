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
    build_feature_frame,
    derive_brand_model,
)
from mask_recommender.prob_model import predict_prob_model  # noqa: E402
from mask_recommender.train import calc_preds, prep_data_in_torch_with_categories  # noqa: E402

APP = Flask(__name__)
APP.logger.setLevel("INFO")
DEFAULT_MODEL_TYPE = "custom_lr"


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


def _download_latest_prob_from_s3() -> Path:
    s3 = boto3.client("s3", region_name=_s3_region())
    bucket = _s3_bucket()
    latest_key = "mask_recommender/models/prob_latest.json"
    payload = json.loads(
        s3.get_object(Bucket=bucket, Key=latest_key)["Body"].read().decode("utf-8")
    )
    timestamp = payload.get("timestamp") or "latest"
    output_dir = _model_root() / f"prob_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    for key_name in ("params_key", "metadata_key", "mask_data_key"):
        key = payload[key_name]
        filename = Path(key).name
        target = output_dir / filename
        s3.download_file(bucket, key, str(target))

    return output_dir


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
    state_dict = torch.load(model_path, map_location="cpu")
    linear_specs = []
    for key, value in state_dict.items():
        if not key.endswith(".weight"):
            continue
        if value.ndim != 2:
            continue
        layer_idx = int(key.split(".")[0])
        out_features, in_features = int(value.shape[0]), int(value.shape[1])
        linear_specs.append((layer_idx, in_features, out_features))
    linear_specs = sorted(linear_specs, key=lambda x: x[0])
    if not linear_specs:
        raise RuntimeError(f"No linear layers found in model state dict: {model_path}")

    layers = []
    for idx, (_, in_features, out_features) in enumerate(linear_specs):
        layers.append(torch.nn.Linear(in_features, out_features))
        if idx < len(linear_specs) - 1:
            layers.append(torch.nn.ReLU())
    model = torch.nn.Sequential(*layers)

    model.load_state_dict(state_dict)
    model.eval()

    return {
        "model": model,
        "feature_columns": feature_columns,
        "categorical_columns": categorical_columns,
        "mask_data": mask_data,
        "metadata": metadata,
    }


def _load_prob_artifacts(model_dir: Path):
    params_path = model_dir / "prob_model_params.pt"
    metadata_path = model_dir / "prob_model_metadata.json"
    mask_data_path = model_dir / "prob_mask_data.json"

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
    if artifacts["metadata"].get("zscore") and artifacts["metadata"].get("zscore_stats"):
        for column, values in artifacts["metadata"]["zscore_stats"].items():
            if column not in encoded.columns:
                continue
            mean_value = float(values.get("mean", 0.0))
            std_value = float(values.get("std", 1.0))
            if std_value == 0:
                std_value = 1.0
            encoded[column] = (
                pd.to_numeric(encoded[column], errors="coerce").fillna(0) - mean_value
            ) / std_value

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
            "timestamp": artifacts["metadata"].get("timestamp"),
            "environment": artifacts["metadata"].get("environment"),
            "empirical_debug": empirical_debug_map,
        }
    }


def _infer_prob(payload, artifacts):
    facial_features = _extract_facial_measurements(payload)
    inference_rows = _build_inference_rows(artifacts["mask_data"], facial_features)
    probs = predict_prob_model(
        artifacts["params"],
        inference_rows,
        artifacts["metadata"]["mask_id_index"],
        artifacts["metadata"]["style_categories"],
    )

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
        "model": artifacts["metadata"],
    }


def _infer_custom(payload, artifacts):
    facial_features = _extract_facial_measurements(payload)
    inference_rows = _build_inference_rows(artifacts["mask_data"], facial_features)
    custom_data = prep_data_in_torch_with_categories(
        inference_rows,
        mask_categories=artifacts["metadata"]["mask_code_categories"],
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
    if (payload or {}).get("model_type"):
        train_argv.extend(["--model-type", str(payload["model_type"])])
    if (payload or {}).get("loss_type"):
        train_argv.extend(["--loss-type", str(payload["loss_type"])])
    if (payload or {}).get("class_reweight"):
        train_argv.append("--class-reweight")
    if (payload or {}).get("zscore"):
        train_argv.append("--zscore")
    if (payload or {}).get("use_facial_perimeter"):
        train_argv.append("--use-facial-perimeter")
    if (payload or {}).get("use_diff_perimeter_bins"):
        train_argv.append("--use-diff-perimeter-bins")
    if (payload or {}).get("use_diff_perimeter_mask_bins"):
        train_argv.append("--use-diff-perimeter-mask-bins")
    if (payload or {}).get("exclude_mask_code"):
        train_argv.append("--exclude-mask-code")
    if (payload or {}).get("exclude_brand_model"):
        train_argv.append("--exclude-brand-model")
    if (payload or {}).get("retrain_with_full"):
        train_argv.append("--retrain-with-full")

    result = train_main(train_argv)

    if (payload or {}).get("model_type") == "custom_lr":
        custom_artifacts = _ensure_custom_artifacts(force_reload=True)
        reload_status = {
            "status": "reloaded",
            "model_type": "custom_lr",
            "timestamp": custom_artifacts["metadata"].get("timestamp"),
            "environment": custom_artifacts["metadata"].get("environment"),
        }
    elif (payload or {}).get("model_type") == "prob":
        APP.config.pop("prob_artifacts", None)
        prob_dir = _download_latest_prob_from_s3()
        APP.config["prob_artifacts"] = _load_prob_artifacts(prob_dir)
        reload_status = {
            "status": "reloaded",
            "model_type": "prob",
            "timestamp": APP.config["prob_artifacts"]["metadata"].get("timestamp"),
            "environment": APP.config["prob_artifacts"]["metadata"].get("environment"),
        }
    else:
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
    if payload.get("method") == "warmup":
        model_type = payload.get("model_type") or DEFAULT_MODEL_TYPE
        if model_type == "prob":
            if "prob_artifacts" not in APP.config:
                prob_dir = _download_latest_prob_from_s3()
                APP.config["prob_artifacts"] = _load_prob_artifacts(prob_dir)
            return jsonify({
                "status": "warmed",
                "model_type": "prob",
                "model": APP.config["prob_artifacts"]["metadata"],
            })
        if model_type == "custom_lr":
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
        return jsonify({
            "status": "warmed",
            "model_type": "nn",
            "model": APP.config["artifacts"]["metadata"],
        })
    model_type = payload.get("model_type") or DEFAULT_MODEL_TYPE
    if model_type == "prob":
        if "prob_artifacts" not in APP.config:
            prob_dir = _download_latest_prob_from_s3()
            APP.config["prob_artifacts"] = _load_prob_artifacts(prob_dir)
        return jsonify(_infer_prob(payload, APP.config["prob_artifacts"]))
    if model_type == "custom_lr":
        try:
            custom_artifacts = _ensure_custom_artifacts()
        except (ClientError, FileNotFoundError) as exc:
            return jsonify({
                "error": "Custom LR artifacts are not available locally or in S3.",
                "details": str(exc),
            }), 503
        return jsonify(_infer_custom(payload, custom_artifacts))
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
