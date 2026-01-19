import argparse
import json
import logging
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pymc as pm
import torch
from breathesafe_network import build_session, fetch_facial_measurements_fit_tests
from predict_arkit_from_traditional import predict_arkit_from_traditional
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from train import build_feature_matrix, train_predictor_with_split

FACIAL_FEATURE_COLUMNS = [
    'nose_mm',
    'chin_mm',
    'top_cheek_mm',
    'mid_cheek_mm',
    'strap_mm',
]


def _normalize_pass(value):
    if isinstance(value, bool):
        return int(value)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    normalized = str(value).strip().lower()
    if normalized in ['true', '1', 'pass', 'passed', 'yes', 'y']:
        return 1
    if normalized in ['false', '0', 'fail', 'failed', 'no', 'n']:
        return 0
    return None


def _is_truthy(value):
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return str(value).strip().lower() in ['true', '1', 'yes', 'y']


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


def prepare_fit_tests(df):
    filtered = df.copy()
    filtered = filtered[filtered["perimeter_mm"].notna()]
    filtered = filtered[filtered["perimeter_mm"] > 0]

    if "mask_modded" in filtered.columns:
        filtered = filtered[~filtered["mask_modded"].apply(_is_truthy)]

    filtered = filtered.dropna(subset=FACIAL_FEATURE_COLUMNS)
    filtered = filtered[filtered["unique_internal_model_code"].notna()]
    filtered = filtered[filtered["style"].notna()]
    filtered = filtered[filtered["strap_type"].notna()]

    filtered["qlft_pass_normalized"] = filtered["qlft_pass"].apply(_normalize_pass)
    filtered = filtered[filtered["qlft_pass_normalized"].notna()]
    return filtered


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

    session = build_session(None)
    fit_tests_payload = fetch_facial_measurements_fit_tests(session=session)
    fit_tests = pd.DataFrame(fit_tests_payload)

    email = args.email or os.getenv('BREATHESAFE_SERVICE_EMAIL')
    password = args.password or os.getenv('BREATHESAFE_SERVICE_PASSWORD')
    if email and password:
        fit_tests = predict_arkit_from_traditional(
            base_url=args.base_url,
            cookie=args.cookie,
            email=email,
            password=password,
        )
    else:
        logging.info(
            "BREATHESAFE_SERVICE_EMAIL/PASSWORD not set; skipping ARKit imputation."
        )

    fit_tests = prepare_fit_tests(fit_tests)
    if fit_tests.empty:
        logging.warning("No fit tests available after filtering.")
        raise SystemExit(0)

    fit_tests["face_perimeter_mm"] = fit_tests[FACIAL_FEATURE_COLUMNS].sum(axis=1)
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

    p_mask_mean = trace.posterior["p_mask"].mean(dim=("chain", "draw")).values
    beta_facial_hair_mean = float(trace.posterior["beta_facial_hair"].mean().values)
    beta_earloop_mean = float(trace.posterior["beta_earloop"].mean().values)
    beta_headstrap_mean = float(trace.posterior["beta_headstrap"].mean().values)
    alpha_mean = float(trace.posterior["alpha"].mean().values)

    val_linear = (
        beta_facial_hair_mean * val_beard
        + beta_earloop_mean * val_ear
        + beta_headstrap_mean * val_head
        + alpha_mean
    )
    val_p_facial = sigmoid(val_linear)
    val_probs = p_mask_mean[val_mask_idx, val_bin] * val_p_facial

    bayesian_metrics = evaluate_predictions(val_probs, val_labels)

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
