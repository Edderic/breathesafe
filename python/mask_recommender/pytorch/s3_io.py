import io
import json
import os
import time
from typing import Any, Dict, Tuple

import boto3
import torch


def get_s3_bucket_and_prefix() -> Tuple[str, str]:
    env = os.environ.get("ENVIRONMENT", "staging").strip().lower()
    if env not in ("staging", "production", "development"):
        env = "staging"
    default_bucket = {
        "production": "breathesafe-production",
        "staging": "breathesafe-staging",
        "development": "breathesafe-development",
    }[env]
    bucket = os.environ.get("S3_BUCKET", default_bucket)
    prefix = f"mask-recommender-pytorch-{env}/models"
    return bucket, prefix


def s3_client():
    region = os.environ.get("S3_BUCKET_REGION", "us-east-2")
    return boto3.client("s3", region_name=region)


def save_bytes_to_s3(data: bytes, key: str) -> str:
    bucket, prefix = get_s3_bucket_and_prefix()
    s3 = s3_client()
    s3.put_object(Bucket=bucket, Key=f"{prefix}/{key}", Body=data)
    return f"s3://{bucket}/{prefix}/{key}"


def upload_checkpoint(state: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, str]:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # Model
    buf = io.BytesIO()
    torch.save(state, buf)
    buf.seek(0)
    model_latest = save_bytes_to_s3(buf.getvalue(), "fit_classifier_latest.pt")
    buf.seek(0)
    model_versioned = save_bytes_to_s3(buf.getvalue(), f"fit_classifier_{timestamp}.pt")
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
    """
    Save mask_data into the PyTorch models prefix so inference sees fresh data.
    Writes mask_data_latest.json and a timestamped copy.
    """
    bucket, prefix = get_s3_bucket_and_prefix()
    s3 = s3_client()
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    payload = json.dumps(mask_data).encode("utf-8")
    latest_key = f"{prefix}/mask_data_latest.json"
    versioned_key = f"{prefix}/mask_data_{timestamp}.json"
    s3.put_object(Bucket=bucket, Key=latest_key, Body=payload)
    s3.put_object(Bucket=bucket, Key=versioned_key, Body=payload)
    return {
        "mask_data_latest": f"s3://{bucket}/{latest_key}",
        "mask_data_versioned": f"s3://{bucket}/{versioned_key}",
    }


def load_mask_data() -> Dict[str, Any]:
    # Reuse existing mask data from the training lambda
    env = os.environ.get("ENVIRONMENT", "staging").strip().lower()
    bucket = os.environ.get(
        "S3_BUCKET",
        {
            "production": "breathesafe-production",
            "staging": "breathesafe-staging",
            "development": "breathesafe-development",
        }.get(env, "breathesafe-staging"),
    )
    key = f"mask-recommender-{env}/models/mask_data_latest.json"
    s3 = s3_client()
    buf = io.BytesIO()
    s3.download_fileobj(bucket, key, buf)
    buf.seek(0)
    return json.loads(buf.read().decode("utf-8"))


def load_latest_model() -> Dict[str, Any]:
    bucket, prefix = get_s3_bucket_and_prefix()
    s3 = s3_client()
    key = f"{prefix}/fit_classifier_latest.pt"
    buf = io.BytesIO()
    s3.download_fileobj(bucket, key, buf)
    buf.seek(0)
    state = torch.load(buf, map_location="cpu")
    return state
