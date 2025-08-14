import json
import os
import io
import time
import logging
from typing import Any, Dict, List, Optional

import boto3
import torch
import pandas as pd
import numpy as np

# Local imports from this package
from .dataset import TabularFitDataset
from .features import FEATURES
from .model import FitClassifier, MLPConfig

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_DATA_URL = "https://www.breathesafe.xyz/facial_measurements_fit_tests.json"


def _get_s3_bucket_and_prefix() -> (str, str):
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


def _s3_client():
    region = os.environ.get("S3_BUCKET_REGION", "us-east-2")
    return boto3.client("s3", region_name=region)


def _try_load_remote_json(url: str, timeout_s: float = 15.0) -> Optional[pd.DataFrame]:
    import requests
    try:
        resp = requests.get(url, timeout=timeout_s)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Normalize various shapes
        keys = [
            "data",
            "rows",
            "items",
            "records",
            "facial_measurements_fit_tests",
            "fit_tests_with_facial_measurements",
        ]
        records = None
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            for k in keys:
                if k in data and isinstance(data[k], list):
                    records = data[k]
                    break
        if records is None:
            return None
        df = pd.json_normalize(records)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def _expand_one_hots(df: pd.DataFrame) -> pd.DataFrame:
    # Expand mask_id/style/strap_type
    for cat_col, prefix in [("mask_id", "mask_id_"), ("style", "style_"), ("strap_type", "strap_type_")]:
        if cat_col in df.columns:
            dummies = pd.get_dummies(df[cat_col].astype(str), prefix=prefix.rstrip("_"))
            dummies.columns = [
                f"{prefix}{c.split('_',1)[1]}" if c.startswith(prefix.rstrip('_')+"_") else f"{prefix}{c}"
                for c in dummies.columns
            ]
            for c in dummies.columns:
                if c not in df.columns:
                    df[c] = dummies[c]
    return df


def _filter_z_scores(df: pd.DataFrame) -> pd.DataFrame:
    z_cols = [c for c in df.columns if c.endswith("_z_score")]
    if not z_cols:
        return df
    zdf = df[z_cols].apply(pd.to_numeric, errors="coerce")
    within = (zdf.abs() <= 2.25) | zdf.isna()
    mask = within.all(axis=1)
    before = len(df)
    out = df.loc[mask].copy()
    after = len(out)
    if after < before:
        logger.info(f"Filtered out {before - after} rows due to extreme z-scores (>|2.25|).")
    return out


def _prepare_dataset(df: pd.DataFrame, target_col: str = "target") -> (TabularFitDataset, List[str]):
    # Determine target
    if target_col not in df.columns:
        if "qlft_pass" in df.columns:
            col = df["qlft_pass"]
            if col.dtype == bool:
                df["target"] = col.astype(int)
            else:
                df["target"] = col.astype(str).str.lower().map({"true": 1, "false": 0}).fillna(0).astype(int)
            target_col = "target"
            logger.info("Using qlft_pass as target (binary).")
        else:
            raise ValueError(f"Target column '{target_col}' not found and 'qlft_pass' missing.")
    # Clean target
    df = df.loc[df[target_col].notna()].copy()
    try:
        df[target_col] = df[target_col].astype(int)
    except Exception:
        cats = {v: i for i, v in enumerate(sorted(df[target_col].unique()))}
        df[target_col] = df[target_col].map(cats).astype(int)

    # Expand and filter
    df = _expand_one_hots(df)
    df = _filter_z_scores(df)

    feature_names: List[str] = list(FEATURES)
    feature_names += [c for c in df.columns if c.startswith("mask_id_") or c.startswith("style_") or c.startswith("strap_type_")]

    dataset = TabularFitDataset(df, feature_names=feature_names, target_col=target_col)
    return dataset, feature_names


def _save_bytes_to_s3(data: bytes, key: str) -> str:
    bkt, prefix = _get_s3_bucket_and_prefix()
    s3 = _s3_client()
    s3.put_object(Bucket=bkt, Key=f"{prefix}/{key}", Body=data)
    return f"s3://{bkt}/{prefix}/{key}"


def _upload_checkpoint(state: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, str]:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # Model
    buf = io.BytesIO()
    torch.save(state, buf)
    buf.seek(0)
    model_latest = _save_bytes_to_s3(buf.getvalue(), "fit_classifier_latest.pt")
    buf.seek(0)
    model_versioned = _save_bytes_to_s3(buf.getvalue(), f"fit_classifier_{timestamp}.pt")
    # Metrics
    metrics_bytes = json.dumps(metrics).encode("utf-8")
    metrics_latest = _save_bytes_to_s3(metrics_bytes, "metrics_latest.json")
    metrics_versioned = _save_bytes_to_s3(metrics_bytes, f"metrics_{timestamp}.json")
    return {
        "model_latest": model_latest,
        "model_versioned": model_versioned,
        "metrics_latest": metrics_latest,
        "metrics_versioned": metrics_versioned,
    }


def _train(data_url: Optional[str] = None, csv_path: Optional[str] = None, epochs: int = 50, batch_size: int = 64, lr: float = 1e-3, hidden: int = 128, depth: int = 2, dropout: float = 0.0, val_split: float = 0.2, target_col: str = "target") -> Dict[str, Any]:
    from torch.utils.data import DataLoader, random_split
    import torch.nn as nn

    # Load data
    df = None
    if data_url:
        df = _try_load_remote_json(data_url)
        if df is not None:
            logger.info(f"Loaded remote dataset from {data_url} with shape {df.shape}")
    if df is None and csv_path:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded local CSV from {csv_path} with shape {df.shape}")
    if df is None:
        raise ValueError("No data available for training.")

    dataset, feature_names = _prepare_dataset(df, target_col=target_col)

    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FitClassifier(MLPConfig(input_dim=len(feature_names), hidden_dim=hidden, depth=depth, dropout=dropout, num_classes=2)).to(device)

    def accuracy(probs: torch.Tensor, y: torch.Tensor) -> float:
        preds = (probs.view(-1) >= 0.5).long()
        return (preds == y).float().mean().item()

    def train_one_epoch(model, loader, loss_fn, optimizer, device):
        model.train()
        total_loss, total_acc, n = 0.0, 0.0, 0
        for X, y in loader:
            X = X.to(device)
            y = y.to(device)
            optimizer.zero_grad()
            probs = model(X).view(-1)
            loss = loss_fn(probs, y.float())
            loss.backward()
            optimizer.step()
            bsz = y.size(0)
            total_loss += loss.item() * bsz
            total_acc += accuracy(probs.detach(), y) * bsz
            n += bsz
        return total_loss / n, total_acc / n

    def evaluate(model, loader, loss_fn, device):
        model.eval()
        total_loss, total_acc, n = 0.0, 0.0, 0
        tp = tn = fp = fn = 0
        with torch.no_grad():
            for X, y in loader:
                X = X.to(device)
                y = y.to(device)
                probs = model(X).view(-1)
                loss = loss_fn(probs, y.float())
                bsz = y.size(0)
                total_loss += loss.item() * bsz
                total_acc += accuracy(probs, y) * bsz
                n += bsz
                preds = (probs >= 0.5).long()
                tp += int(((preds == 1) & (y == 1)).sum().item())
                tn += int(((preds == 0) & (y == 0)).sum().item())
                fp += int(((preds == 1) & (y == 0)).sum().item())
                fn += int(((preds == 0) & (y == 1)).sum().item())
        ppv = float(tp / (tp + fp)) if (tp + fp) > 0 else float('nan')
        npv = float(tn / (tn + fn)) if (tn + fn) > 0 else float('nan')
        return total_loss / n, total_acc / n, ppv, npv

    loss_fn = torch.nn.BCELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    best_val = float("inf")
    best_state = None
    best_metrics = {}
    for epoch in range(1, epochs + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        va_loss, va_acc, va_ppv, va_npv = evaluate(model, val_loader, loss_fn, device)
        logger.info(
            f"epoch={epoch} train_loss={tr_loss:.4f} train_acc={tr_acc:.3f} "
            f"val_loss={va_loss:.4f} val_acc={va_acc:.3f} val_ppv={va_ppv:.3f} val_npv={va_npv:.3f}"
        )
        if va_loss < best_val:
            best_val = va_loss
            best_state = {
                "model_state": model.state_dict(),
                "feature_names": feature_names,
                "config": {
                    "input_dim": len(feature_names),
                    "hidden_dim": hidden,
                    "depth": depth,
                    "dropout": dropout,
                    "num_classes": 2,
                },
                "stats": dataset.get_stats().__dict__ if dataset.get_stats() is not None else None,
            }
            best_metrics = {
                "epoch": epoch,
                "train_loss": tr_loss,
                "train_acc": tr_acc,
                "val_loss": va_loss,
                "val_acc": va_acc,
                "val_ppv": va_ppv,
                "val_npv": va_npv,
            }

    # Upload artifacts
    s3_paths = _upload_checkpoint(best_state, best_metrics)
    return {"metrics": best_metrics, "artifacts": s3_paths}


def _load_mask_data() -> Dict[str, Any]:
    # Reuse existing mask data from the training lambda
    env = os.environ.get("ENVIRONMENT", "staging").strip().lower()
    bucket = os.environ.get("S3_BUCKET", {
        "production": "breathesafe-production",
        "staging": "breathesafe-staging",
        "development": "breathesafe-development",
    }.get(env, "breathesafe-staging"))
    key = f"mask-recommender-training-{env}/models/mask_data_latest.json"
    s3 = _s3_client()
    buf = io.BytesIO()
    s3.download_fileobj(bucket, key, buf)
    buf.seek(0)
    return json.loads(buf.read().decode("utf-8"))


def _load_latest_model() -> Dict[str, Any]:
    bkt, prefix = _get_s3_bucket_and_prefix()
    s3 = _s3_client()
    key = f"{prefix}/fit_classifier_latest.pt"
    buf = io.BytesIO()
    s3.download_fileobj(bkt, key, buf)
    buf.seek(0)
    state = torch.load(buf, map_location="cpu")
    return state


def _build_feature_row(feature_names: List[str], facial: Dict[str, Any], mask_info: Dict[str, Any]) -> pd.DataFrame:
    # Construct a single-row with numeric and one-hot fields, then select feature_names
    row: Dict[str, Any] = {k: 0 for k in feature_names}
    # Numerics we might use
    base_numeric = {
        "face_width": float(facial.get("face_width", 0.0)),
        "face_length": float(facial.get("face_length", 0.0)),
        "nose_protrusion": float(facial.get("nose_protrusion", 0.0)),
        "bitragion_subnasale_arc": float(facial.get("bitragion_subnasale_arc", 0.0)),
        "facial_hair_beard_length_mm": float(facial.get("facial_hair_beard_length_mm", 0.0)),
        "lip_width": float(facial.get("lip_width", 0.0)),
        "perimeter_mm": float(mask_info.get("perimeter_mm", 0.0)),
        "adjustable_headstrap": float(mask_info.get("adjustable_headstrap", 0)),
        "adjustable_earloops": float(mask_info.get("adjustable_earloops", 0)),
    }
    for k, v in base_numeric.items():
        if k in row:
            row[k] = v
    # One-hots
    mask_id = str(mask_info.get("mask_id", mask_info.get("id", "")))
    style = str(mask_info.get("style", ""))
    strap_type = str(mask_info.get("strap_type", ""))
    one_hots = [
        f"mask_id_{mask_id}",
        f"style_{style}",
        f"strap_type_{strap_type}",
    ]
    for oh in one_hots:
        if oh in row:
            row[oh] = 1
    df = pd.DataFrame([row])
    return df


def _standardize_numeric(X: np.ndarray, feature_names: List[str], stats: Optional[Dict[str, Any]]) -> np.ndarray:
    if not stats:
        return X
    mean = np.array(stats.get("mean", []), dtype=np.float32)
    std = np.array(stats.get("std", []), dtype=np.float32)
    # Identify numeric columns as those not strictly 0/1 in the checkpoint's training split
    # Here, assume columns with names not starting with known one-hot prefixes are numeric
    is_binary = np.array([
        name.startswith("mask_id_") or name.startswith("style_") or name.startswith("strap_type_") or name in ("adjustable_headstrap", "adjustable_earloops")
        for name in feature_names
    ])
    idx = np.where(~is_binary)[0]
    if idx.size > 0 and mean.size == idx.size and std.size == idx.size:
        X[:, idx] = (X[:, idx] - mean) / np.where(std == 0, 1.0, std)
    return X


def _infer(facial_measurements: Dict[str, Any], mask_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    state = _load_latest_model()
    feature_names: List[str] = state["feature_names"]
    config = state["config"]
    stats = state.get("stats", None)

    model = FitClassifier(MLPConfig(**config))
    model.load_state_dict(state["model_state"])
    model.eval()

    mask_data = _load_mask_data()  # dict keyed by mask_id string
    # filter mask_ids if provided
    items = list(mask_data.items())
    if mask_ids:
        wanted = set(int(i) for i in mask_ids)
        items = [(mid, info) for mid, info in items if int(mid) in wanted]

    rows = []
    for mid, info in items:
        # Ensure mask_id present in info for feature building
        info = {**info, "mask_id": int(mid)}
        df_row = _build_feature_row(feature_names, facial_measurements, info)
        rows.append(df_row)
    if not rows:
        return {"mask_id": {}, "proba_fit": {}}

    df_all = pd.concat(rows, ignore_index=True)

    # Align order and fill missing
    for c in feature_names:
        if c not in df_all.columns:
            df_all[c] = 0
    X = df_all[feature_names].to_numpy(dtype=np.float32)
    X = _standardize_numeric(X, feature_names, stats)
    X = torch.from_numpy(X)

    with torch.no_grad():
        probs = model(X).view(-1).numpy()

    # Build legacy output shape
    sorted_idx = np.argsort(-probs)
    mask_ids_sorted = [int(df_all.iloc[i].get("mask_id", 0)) for i in sorted_idx]
    out = {
        "mask_id": {str(i): mid for i, mid in enumerate(mask_ids_sorted)},
        "proba_fit": {str(i): float(probs[idx]) for i, idx in enumerate(sorted_idx)},
    }
    return out


def handler(event, context):
    try:
        body = event.get("body") if isinstance(event, dict) else None
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception:
                body = {}
        if not isinstance(body, dict):
            body = event if isinstance(event, dict) else {}

        method = (body.get("method") or "infer").strip().lower()
        if method == "train":
            epochs = int(body.get("epochs", 50))
            data_url = body.get("data_url", DEFAULT_DATA_URL)
            target_col = body.get("target_col", "target")
            result = _train(data_url=data_url, csv_path=None, epochs=epochs, target_col=target_col)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Training completed successfully",
                    "artifacts": result["artifacts"],
                    "metrics": result["metrics"],
                })
            }
        elif method == "infer":
            facial = body.get("facial_measurements", {})
            mask_ids = body.get("mask_ids")
            out = _infer(facial, mask_ids)
            return {
                "statusCode": 200,
                "body": json.dumps(out)
            }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown method: {method}"})
            }
    except Exception as e:
        logger.exception("Lambda execution failed")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
