import json
import os
from pathlib import Path

import boto3


def _env_name():
    env = os.environ.get("RAILS_ENV", "").strip().lower()
    if env in ("production", "staging", "development"):
        return env
    return "development"


def _s3_bucket():
    mapping = {
        "production": "breathesafe",
        "staging": "breathesafe-staging",
        "development": "breathesafe-development",
    }
    return mapping[_env_name()]


def _s3_region():
    return os.environ.get("S3_BUCKET_REGION") or os.environ.get("AWS_REGION") or "us-east-1"


def _model_root():
    override = os.environ.get("MASK_RECOMMENDER_LOCAL_MODEL_DIR")
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parents[1] / "local_models"


def main():
    s3 = boto3.client("s3", region_name=_s3_region())
    bucket = _s3_bucket()
    latest_key = "mask_recommender/models/latest.json"
    payload = json.loads(s3.get_object(Bucket=bucket, Key=latest_key)["Body"].read().decode("utf-8"))

    timestamp = payload.get("timestamp") or "latest"
    output_dir = _model_root() / str(timestamp)
    output_dir.mkdir(parents=True, exist_ok=True)

    for key_name in ("model_key", "metadata_key", "mask_data_key"):
        key = payload[key_name]
        filename = Path(key).name
        target = output_dir / filename
        s3.download_file(bucket, key, str(target))
        print(f"Downloaded s3://{bucket}/{key} -> {target}")

    print(f"Local model directory: {output_dir}")


if __name__ == "__main__":
    main()
