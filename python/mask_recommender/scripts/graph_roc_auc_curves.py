import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import auc, roc_curve


def parse_args():
    parser = argparse.ArgumentParser(description="Graph ROC-AUC curves for models.")
    parser.add_argument(
        "--output-key",
        default=None,
        help="Optional S3 key for the ROC plot image.",
    )
    return parser.parse_args()


def _env_name():
    env = os.environ.get('RAILS_ENV', '').strip().lower()
    if env in ('production', 'staging', 'development'):
        return env
    return 'development'


def _s3_bucket():
    mapping = {
        'production': 'breathesafe',
        'staging': 'breathesafe-staging',
        'development': 'breathesafe-development',
    }
    return mapping[_env_name()]


def _s3_region():
    return os.environ.get('S3_BUCKET_REGION') or os.environ.get('AWS_REGION') or 'us-east-1'


def _upload_file_to_s3(local_path, key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    profile = os.environ.get('AWS_PROFILE')
    logging.info(
        "S3 upload using bucket=%s region=%s profile=%s",
        bucket,
        _s3_region(),
        profile or "default"
    )
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"


def _load_latest_gut_check():
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    latest_key = "mask_recommender/models/bayesian_gut_check_latest.json"
    try:
        response = s3.get_object(Bucket=bucket, Key=latest_key)
        payload = json.loads(response["Body"].read().decode("utf-8"))
        return payload
    except s3.exceptions.NoSuchKey:
        return None


def _find_local_recommendations(prefix):
    candidates = list(Path("/tmp").glob(f"{prefix}_recommendations_*.json"))
    if not candidates:
        return None
    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    return str(latest)


def _load_recommendations(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_scores(payload):
    y_true = []
    y_score = []
    for user in payload.get("users", []):
        for row in user.get("recommendations", []):
            ground_truth = row.get("ground_truth")
            if ground_truth not in ("pass", "fail"):
                continue
            y_true.append(1 if ground_truth == "pass" else 0)
            y_score.append(float(row.get("probability_of_fit", 0)))
    return np.array(y_true), np.array(y_score)


def _plot_roc(ax, y_true, y_score, title):
    if y_true.size == 0:
        ax.set_title(f"{title} (no data)")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
        return None
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, color="tab:blue", linewidth=2)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f"{title} (AUC={roc_auc:.3f})")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    return roc_auc


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    payload = _load_latest_gut_check()
    bayesian_path = None
    nn_path = None
    if payload:
        bucket = _s3_bucket()
        s3 = boto3.client('s3', region_name=_s3_region())
        bayesian_key = payload.get("bayesian_recommendations_key")
        nn_key = payload.get("neural_net_recommendations_key")
        if bayesian_key:
            bayesian_path = f"/tmp/{os.path.basename(bayesian_key)}"
            s3.download_file(bucket, bayesian_key, bayesian_path)
        if nn_key:
            nn_path = f"/tmp/{os.path.basename(nn_key)}"
            s3.download_file(bucket, nn_key, nn_path)

    if not bayesian_path:
        bayesian_path = _find_local_recommendations("bayesian")
    if not nn_path:
        nn_path = _find_local_recommendations("neural_net")

    if not bayesian_path or not nn_path:
        raise RuntimeError("Missing recommendation files for Bayesian or neural net models.")

    bayesian_payload = _load_recommendations(bayesian_path)
    nn_payload = _load_recommendations(nn_path)

    bayesian_labels, bayesian_scores = _extract_scores(bayesian_payload)
    nn_labels, nn_scores = _extract_scores(nn_payload)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    _plot_roc(axes[0], bayesian_labels, bayesian_scores, "Bayesian model")
    _plot_roc(axes[1], nn_labels, nn_scores, "Neural net")
    plt.tight_layout()

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    local_path = f"/tmp/roc_auc_curves_{run_timestamp}.png"
    plt.savefig(local_path, dpi=150)
    plt.close(fig)

    output_key = args.output_key or f"mask_recommender/models/{run_timestamp}/roc_auc_curves.png"
    output_uri = _upload_file_to_s3(local_path, output_key)
    logging.info("Saved ROC curves to %s (local=%s)", output_uri, local_path)


if __name__ == "__main__":
    main()
