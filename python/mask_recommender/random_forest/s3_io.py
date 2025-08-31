import io
import json
import os
import time
from typing import Any, Dict, Tuple

import boto3
import joblib


def _env() -> str:
    env = os.environ.get("ENVIRONMENT", "staging").strip().lower()
    return env if env in ("staging", "production", "development") else "staging"


def get_s3_bucket_and_prefix() -> Tuple[str, str]:
    env = _env()
    default_bucket = {
        "production": "breathesafe-production",
        "staging": "breathesafe-staging",
        "development": "breathesafe-development",
    }[env]
    bucket = os.environ.get("S3_BUCKET", default_bucket)
    prefix = f"mask-recommender-{env}/models"
    return bucket, prefix


def s3_client():
    region = os.environ.get("S3_BUCKET_REGION", "us-east-2")
    return boto3.client("s3", region_name=region)


def save_bytes_to_s3(data: bytes, key: str) -> str:
    if _env() == "development":
        base = "/tmp/mask-recommender-development/models"
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, key)
        with open(path, "wb") as f:
            f.write(data)
        return f"file://{path}"
    else:
        bucket, prefix = get_s3_bucket_and_prefix()
        s3 = s3_client()
        s3.put_object(Bucket=bucket, Key=f"{prefix}/{key}", Body=data)
        return f"s3://{bucket}/{prefix}/{key}"


def upload_checkpoint(state: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, str]:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # Model (joblib)
    buf = io.BytesIO()
    joblib.dump(state, buf)
    buf.seek(0)
    model_latest = save_bytes_to_s3(buf.getvalue(), "rf_classifier_latest.joblib")
    buf.seek(0)
    model_versioned = save_bytes_to_s3(buf.getvalue(), f"rf_classifier_{timestamp}.joblib")
    # Metrics
    metrics_bytes = json.dumps(metrics).encode("utf-8")
    metrics_latest = save_bytes_to_s3(metrics_bytes, "metrics_latest.json")
    metrics_versioned = save_bytes_to_s3(metrics_bytes, f"metrics_{timestamp}.json")
    return {
        "model_latest": model_latest,
        "model_versioned": model_versioned,
        "metrics_latest": metrics_latest,
        "metrics_versioned": metrics_versioned,
    }


def save_mask_data(mask_data: Dict[str, Any]) -> Dict[str, str]:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    payload = json.dumps(mask_data).encode("utf-8")
    if _env() == "development":
        base = "/tmp/mask-recommender-development/models"
        os.makedirs(base, exist_ok=True)
        latest_path = os.path.join(base, "mask_data_latest.json")
        versioned_path = os.path.join(base, f"mask_data_{timestamp}.json")
        with open(latest_path, "wb") as f:
            f.write(payload)
        with open(versioned_path, "wb") as f:
            f.write(payload)
        return {
            "mask_data_latest": f"file://{latest_path}",
            "mask_data_versioned": f"file://{versioned_path}",
        }
    else:
        bucket, prefix = get_s3_bucket_and_prefix()
        s3 = s3_client()
        latest_key = f"{prefix}/mask_data_latest.json"
        versioned_key = f"{prefix}/mask_data_{timestamp}.json"
        s3.put_object(Bucket=bucket, Key=latest_key, Body=payload)
        s3.put_object(Bucket=bucket, Key=versioned_key, Body=payload)
        return {
            "mask_data_latest": f"s3://{bucket}/{latest_key}",
            "mask_data_versioned": f"s3://{bucket}/{versioned_key}",
        }


def load_mask_data() -> Dict[str, Any]:
    if _env() == "development":
        base = "/tmp/mask-recommender-development/models"
        path = os.path.join(base, "mask_data_latest.json")
        with open(path, "rb") as f:
            return json.loads(f.read().decode("utf-8"))
    else:
        env = _env()
        bucket = os.environ.get(
            "S3_BUCKET",
            {
                "production": "breathesafe-production",
                "staging": "breathesafe-staging",
                "development": "breathesafe-development",
            }[env],
        )
        s3 = s3_client()
        # Try RF prefix first, then fall back to common prefix used by PyTorch
        keys_to_try = [
            f"mask-recommender-{env}/models/mask_data_latest.json",
            f"mask-recommender-{env}/models/mask_data_latest.json",
        ]
        last_err: Optional[Exception] = None
        for key in keys_to_try:
            try:
                buf = io.BytesIO()
                s3.download_fileobj(bucket, key, buf)
                buf.seek(0)
                return json.loads(buf.read().decode("utf-8"))
            except Exception as e:
                last_err = e
                continue
        if last_err is not None:
            raise last_err
        return {}


def load_latest_model() -> Dict[str, Any]:
    if _env() == "development":
        base = "/tmp/mask-recommender-development/models"
        path = os.path.join(base, "rf_classifier_latest.joblib")
        with open(path, "rb") as f:
            buf = io.BytesIO(f.read())
        buf.seek(0)
        state = joblib.load(buf)
        return state
    else:
        bucket, prefix = get_s3_bucket_and_prefix()
        s3 = s3_client()
        key = f"{prefix}/rf_classifier_latest.joblib"
        buf = io.BytesIO()
        s3.download_fileobj(bucket, key, buf)
        buf.seek(0)
        state = joblib.load(buf)
        return state
