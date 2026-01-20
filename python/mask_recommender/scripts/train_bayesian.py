import argparse
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

import arviz as az
import boto3
import numpy as np
import pandas as pd
import pymc as pm
import pytensor
import torch
from data_prep import (BAYESIAN_FACE_COLUMNS, FACIAL_FEATURE_COLUMNS, get_masks,
                       filter_fit_tests_for_bayesian,
                       load_fit_tests_with_imputation)
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score


pytensor.config.cxx = ""
pytensor.config.mode = "FAST_COMPILE"


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


def _upload_json_to_s3(payload, key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    profile = os.environ.get('AWS_PROFILE')
    logging.info(
        "S3 upload using bucket=%s region=%s profile=%s",
        bucket,
        _s3_region(),
        profile or "default"
    )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload, indent=2).encode('utf-8'),
        ContentType='application/json'
    )
    return f"s3://{bucket}/{key}"


def parse_args():
    parser = argparse.ArgumentParser(description="Train a Bayesian mask fit model.")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BREATHESAFE_BASE_URL", "http://localhost:3000"),
        help="Base URL for the Breathesafe API.",
    )
    parser.add_argument("--cookie", help="Session cookie for authentication.")
    parser.add_argument("--email", help="Email for authentication (optional).")
    parser.add_argument("--password", help="Password for authentication (optional).")
    parser.add_argument("--draws", type=int, default=1000, help="Posterior draws.")
    parser.add_argument("--tune", type=int, default=1000, help="Tuning steps.")
    parser.add_argument(
        "--target-accept", type=float, default=0.9, help="Target acceptance rate."
    )
    parser.add_argument(
        "--val-split", type=float, default=0.2, help="Validation split fraction."
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to write metrics JSON output.",
    )
    parser.add_argument(
        "--nn-epochs",
        type=int,
        default=50,
        help="Epochs for the baseline neural network comparison.",
    )
    parser.add_argument(
        "--nn-learning-rate",
        type=float,
        default=0.01,
        help="Learning rate for the baseline neural network comparison.",
    )
    return parser.parse_args()


def build_perimeter_bins():
    edges = [-np.inf]
    edges.extend(np.arange(-120, 121, 15).tolist())
    edges.append(np.inf)
    labels = []
    for left, right in zip(edges[:-1], edges[1:]):
        labels.append(f"{left}_to_{right}")
    return edges, labels


def sigmoid(values):
    return 1 / (1 + np.exp(-values))


def build_bayesian_model(
    coords,
    mask_style_idx,
    train_mask_idx,
    train_bin,
    train_beard,
    train_ear,
    train_head,
    train_labels,
    args,
):
    with pm.Model(coords=coords) as model:
        mask_idx = pm.Data("mask_idx", train_mask_idx)
        bin_idx = pm.Data("bin_idx", train_bin)
        beard_len = pm.Data("beard_length", train_beard)
        earloop = pm.Data("is_earloop", train_ear)
        headstrap = pm.Data("is_headstrap", train_head)

        alpha_style_bin = pm.HalfNormal(
            "alpha_perimeter_bin_style",
            sigma=10,
            dims=("style", "bin")
        )
        beta_style_bin = pm.HalfNormal(
            "beta_perimeter_bin_style",
            sigma=10,
            dims=("style", "bin")
        )

        alpha_mask_bin = alpha_style_bin[mask_style_idx]
        beta_mask_bin = beta_style_bin[mask_style_idx]

        p_mask = pm.Beta(
            "p_mask",
            alpha=alpha_mask_bin,
            beta=beta_mask_bin,
            dims=("mask", "bin")
        )

        beta_facial_hair = pm.Normal("beta_facial_hair", mu=0, sigma=1)
        beta_earloop = pm.Normal("beta_earloop", mu=0, sigma=1)
        beta_headstrap = pm.Normal("beta_headstrap", mu=1, sigma=1)
        alpha = pm.Normal("alpha", mu=0, sigma=3)

        p_facial_hair_strap = pm.math.sigmoid(
            beta_facial_hair * beard_len
            + beta_earloop * earloop
            + beta_headstrap * headstrap
            + alpha
        )
        p = pm.Deterministic("p", p_mask[mask_idx, bin_idx] * p_facial_hair_strap)
        pm.Bernoulli("qlft_pass", p=p, observed=train_labels)

        trace = pm.sample(
            draws=args.draws,
            tune=args.tune,
            target_accept=args.target_accept,
            random_seed=args.seed,
            progressbar=True,
        )

    return model, trace


def predict_from_trace(trace, mask_idx, bin_idx, beard, earloop, headstrap):
    p_mask_mean = trace.posterior["p_mask"].mean(dim=("chain", "draw")).values
    beta_facial_hair_mean = float(trace.posterior["beta_facial_hair"].mean().values)
    beta_earloop_mean = float(trace.posterior["beta_earloop"].mean().values)
    beta_headstrap_mean = float(trace.posterior["beta_headstrap"].mean().values)
    alpha_mean = float(trace.posterior["alpha"].mean().values)

    linear = (
        beta_facial_hair_mean * beard
        + beta_earloop_mean * earloop
        + beta_headstrap_mean * headstrap
        + alpha_mean
    )
    p_facial = sigmoid(linear)
    return p_mask_mean[mask_idx, bin_idx] * p_facial


def evaluate_predictions(val_probs, val_labels):
    threshold_grid = np.arange(0.05, 0.96, 0.01)
    best_threshold = 0.5
    best_f1 = 0.0
    for candidate in threshold_grid:
        preds = (val_probs >= candidate).astype(int)
        candidate_f1 = f1_score(val_labels, preds, zero_division=0)
        if candidate_f1 > best_f1:
            best_f1 = candidate_f1
            best_threshold = float(candidate)

    val_preds = (val_probs >= best_threshold).astype(int)
    precision = precision_score(val_labels, val_preds, zero_division=0)
    recall = recall_score(val_labels, val_preds, zero_division=0)
    try:
        roc_auc = roc_auc_score(val_labels, val_probs)
    except ValueError:
        roc_auc = None

    return {
        "auc": roc_auc,
        "f1": best_f1,
        "precision": precision,
        "recall": recall,
        "threshold": best_threshold,
    }


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    fit_tests = load_fit_tests_with_imputation(
        base_url=args.base_url,
        email=args.email,
        password=args.password,
        cookie=args.cookie,
    )
    fit_tests = filter_fit_tests_for_bayesian(fit_tests)
    if fit_tests.empty:
        logging.warning("No fit tests available after filtering.")
        raise SystemExit(0)

    fit_tests["face_perimeter_mm"] = fit_tests[BAYESIAN_FACE_COLUMNS].sum(axis=1)
    fit_tests["facial_hair_beard_length_mm"] = (
        fit_tests["facial_hair_beard_length_mm"].fillna(0).astype(float)
    )
    fit_tests["perimeter_diff"] = fit_tests["face_perimeter_mm"] - fit_tests["perimeter_mm"]
    bin_edges, bin_labels = build_perimeter_bins()
    fit_tests["perimeter_bin"] = pd.cut(
        fit_tests["perimeter_diff"],
        bins=bin_edges,
        labels=False,
        right=False,
    )
    fit_tests = fit_tests[fit_tests["perimeter_bin"].notna()].copy()
    fit_tests["perimeter_bin"] = fit_tests["perimeter_bin"].astype(int)

    fit_tests["strap_type_normalized"] = (
        fit_tests["strap_type"].astype(str).str.strip().str.lower()
    )
    fit_tests["is_earloop"] = fit_tests["strap_type_normalized"].str.contains("earloop")
    fit_tests["is_headstrap"] = fit_tests["strap_type_normalized"].str.contains("headstrap")

    fit_tests["style_normalized"] = fit_tests["style"].astype(str).str.strip().str.lower()
    fit_tests["mask_code"] = fit_tests["unique_internal_model_code"].astype(str).str.strip()

    style_index = pd.Index(sorted(fit_tests["style_normalized"].unique()))
    mask_index = pd.Index(sorted(fit_tests["mask_code"].unique()))
    style_map = {style: idx for idx, style in enumerate(style_index)}
    mask_map = {mask: idx for idx, mask in enumerate(mask_index)}
    fit_tests["style_index"] = fit_tests["style_normalized"].map(style_map)
    fit_tests["mask_index"] = fit_tests["mask_code"].map(mask_map)

    mask_table = fit_tests[["mask_code", "style_normalized"]].drop_duplicates()
    mask_table = mask_table.set_index("mask_code").reindex(mask_index)
    mask_style_idx = mask_table["style_normalized"].map(style_map).to_numpy(dtype=int)

    rng = np.random.default_rng(args.seed)
    indices = np.arange(fit_tests.shape[0])
    rng.shuffle(indices)
    split_index = int(fit_tests.shape[0] * (1 - args.val_split))
    train_idx = indices[:split_index]
    val_idx = indices[split_index:]

    def split_array(values):
        return values[train_idx], values[val_idx]

    perimeter_bin = fit_tests["perimeter_bin"].to_numpy(dtype=int)
    beard = fit_tests["facial_hair_beard_length_mm"].to_numpy(dtype=float)
    is_earloop = fit_tests["is_earloop"].to_numpy(dtype=int)
    is_headstrap = fit_tests["is_headstrap"].to_numpy(dtype=int)
    labels = fit_tests["qlft_pass_normalized"].to_numpy(dtype=int)

    train_bin, val_bin = split_array(perimeter_bin)
    train_beard, val_beard = split_array(beard)
    train_ear, val_ear = split_array(is_earloop)
    train_head, val_head = split_array(is_headstrap)
    train_mask_idx, val_mask_idx = split_array(fit_tests["mask_index"].to_numpy(dtype=int))
    train_labels, val_labels = split_array(labels)

    coords = {
        "style": list(style_index),
        "mask": list(mask_index),
        "bin": list(bin_labels),
    }

    _, trace = build_bayesian_model(
        coords,
        mask_style_idx,
        train_mask_idx,
        train_bin,
        train_beard,
        train_ear,
        train_head,
        train_labels,
        args,
    )

    trace_path = f"/tmp/mask_recommender_bayesian_trace_{run_timestamp}.nc"
    az.to_netcdf(trace, trace_path)
    trace_key = f"mask_recommender/models/{run_timestamp}/bayesian_trace.nc"
    trace_uri = _upload_file_to_s3(trace_path, trace_key)
    logging.info("Uploaded trace to %s", trace_uri)

    base_url = args.base_url.rstrip("/")
    masks_url = f"{base_url}/masks.json?per_page=1000"
    masks_df = get_masks(session=None, masks_url=masks_url)
    mask_data = {}
    for _, row in masks_df.iterrows():
        mask_id = row.get('id')
        if pd.isna(mask_id):
            continue
        mask_data[str(int(mask_id))] = {
            'id': int(mask_id),
            'unique_internal_model_code': row.get('unique_internal_model_code', ''),
            'perimeter_mm': row.get('perimeter_mm', None),
            'strap_type': row.get('strap_type', ''),
            'style': row.get('style', ''),
        }

    mask_data_key = f"mask_recommender/models/{run_timestamp}/mask_data.json"
    mask_data_uri = _upload_json_to_s3(mask_data, mask_data_key)

    metadata = {
        'timestamp': run_timestamp,
        'environment': _env_name(),
        'mask_index': list(mask_index),
        'bin_edges': bin_edges,
    }
    metadata_key = f"mask_recommender/models/{run_timestamp}/bayesian_metadata.json"
    metadata_uri = _upload_json_to_s3(metadata, metadata_key)
    latest_payload = {
        "timestamp": run_timestamp,
        "trace_key": trace_key,
        "trace_uri": trace_uri,
        "mask_data_key": mask_data_key,
        "mask_data_uri": mask_data_uri,
        "metadata_key": metadata_key,
        "metadata_uri": metadata_uri,
    }
    latest_key = "mask_recommender/models/bayesian_latest.json"
    latest_uri = _upload_json_to_s3(latest_payload, latest_key)
    logging.info("Updated Bayesian latest pointer at %s", latest_uri)

    val_probs = predict_from_trace(
        trace,
        val_mask_idx,
        val_bin,
        val_beard,
        val_ear,
        val_head,
    )

    bayesian_metrics = evaluate_predictions(val_probs, val_labels)

    from train import build_feature_matrix, train_predictor_with_split

    baseline_df = fit_tests[
        [
            "perimeter_mm",
            "facial_hair_beard_length_mm",
            "strap_type",
            "style",
            "unique_internal_model_code",
            "qlft_pass_normalized",
        ]
        + FACIAL_FEATURE_COLUMNS
    ].copy()
    baseline_features, baseline_target = build_feature_matrix(baseline_df)
    baseline_model, _, _, baseline_x_val, baseline_y_val = train_predictor_with_split(
        baseline_features,
        baseline_target,
        train_idx,
        val_idx,
        epochs=args.nn_epochs,
        learning_rate=args.nn_learning_rate,
    )
    baseline_model.eval()
    with torch.no_grad():
        baseline_val_probs = (
            baseline_model(baseline_x_val).squeeze().cpu().numpy()
        )
        baseline_val_labels = baseline_y_val.squeeze().cpu().numpy()
    baseline_metrics = evaluate_predictions(baseline_val_probs, baseline_val_labels)

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "samples_total": int(fit_tests.shape[0]),
        "samples_train": int(train_idx.shape[0]),
        "samples_val": int(val_idx.shape[0]),
        "trace_uri": trace_uri,
        "val_auc": bayesian_metrics["auc"],
        "val_f1": bayesian_metrics["f1"],
        "val_precision": bayesian_metrics["precision"],
        "val_recall": bayesian_metrics["recall"],
        "val_threshold": bayesian_metrics["threshold"],
        "comparison": {
            "bayesian": bayesian_metrics,
            "neural_net": baseline_metrics,
        },
    }

    logging.info(
        "Bayesian metrics -> AUC=%s F1=%.3f precision=%.3f recall=%.3f threshold=%.2f",
        f"{bayesian_metrics['auc']:.3f}" if bayesian_metrics["auc"] is not None else "n/a",
        bayesian_metrics["f1"],
        bayesian_metrics["precision"],
        bayesian_metrics["recall"],
        bayesian_metrics["threshold"],
    )
    logging.info(
        "Neural net metrics -> AUC=%s F1=%.3f precision=%.3f recall=%.3f threshold=%.2f",
        f"{baseline_metrics['auc']:.3f}" if baseline_metrics["auc"] is not None else "n/a",
        baseline_metrics["f1"],
        baseline_metrics["precision"],
        baseline_metrics["recall"],
        baseline_metrics["threshold"],
    )

    output_path = args.output_json
    if not output_path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        output_path = f"python/mask_recommender/bayesian_metrics_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    logging.info("Saved metrics to %s", output_path)


if __name__ == "__main__":
    main()
