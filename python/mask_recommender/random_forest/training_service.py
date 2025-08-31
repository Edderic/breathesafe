import io
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import StratifiedShuffleSplit
import joblib

from .data_prep import prepare_dataset
from .data_utils import try_load_remote_json
from . import s3_io

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_DATA_URL = "https://www.breathesafe.xyz/facial_measurements_fit_tests.json"


def train(
    data_url: Optional[str] = None,
    csv_path: Optional[str] = None,
    n_estimators: int = 75,
    max_depth: Optional[int] = None,
    min_samples_leaf: int = 3,
    target_col: str = "target",
) -> Dict[str, Any]:
    df = None
    if data_url:
        df = try_load_remote_json(data_url)
        if df is not None:
            logger.info(f"Loaded remote dataset from {data_url} with shape {df.shape}")
    if df is None and csv_path:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded local CSV from {csv_path} with shape {df.shape}")
    if df is None:
        raise ValueError("No data available for training.")

    df_prep, feature_names = prepare_dataset(df, target_col=target_col)

    # Train/val split (stratified when possible)
    X = df_prep[feature_names].to_numpy(dtype=np.float32)
    y = df_prep[target_col].to_numpy(dtype=np.int64)
    n_samples = len(y)
    if n_samples <= 1 or np.unique(y).size < 2:
        # Not enough data/classes to stratify; use all as train
        train_idx = np.arange(n_samples)
        val_idx = np.array([], dtype=int)
    else:
        test_size = 0.1 if n_samples > 10 else 0.2
        sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        train_idx, val_idx = next(sss.split(X, y))

    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]

    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced_subsample",
    )
    rf.fit(X_train, y_train)

    # Evaluate on training subset
    if X_train.size > 0:
        probs_tr = rf.predict_proba(X_train)[:, 1]
        preds_tr = (probs_tr >= 0.5).astype(int)
        tr_precision, tr_recall, tr_f1, _ = precision_recall_fscore_support(
            y_train, preds_tr, average="binary", zero_division=0
        )
    else:
        tr_precision = tr_recall = tr_f1 = float("nan")

    # Evaluate on validation subset
    if X_val.size > 0:
        probs_val = rf.predict_proba(X_val)[:, 1]
        preds_val = (probs_val >= 0.5).astype(int)
        va_precision, va_recall, va_f1, _ = precision_recall_fscore_support(
            y_val, preds_val, average="binary", zero_division=0
        )
    else:
        va_precision = va_recall = va_f1 = float("nan")

    threshold = 0.5

    # Retrain on the full dataset to ship a stronger model for inference
    rf_full = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced_subsample",
    )
    rf_full.fit(X, y)

    state = {
        "model": rf_full,
        "feature_names": feature_names,
        "threshold": float(threshold),
        # stats key kept for interface parity with pytorch version
        "stats": None,
    }

    # Serialize model & metrics
    try:
        buf = io.BytesIO()
        joblib.dump(state, buf)
        buf.seek(0)
    except Exception:
        pass

    s3_paths = s3_io.upload_checkpoint(
        state,
        {  # type: ignore[arg-type]
            "train_precision": float(tr_precision) if not np.isnan(tr_precision) else float("nan"),
            "train_recall": float(tr_recall) if not np.isnan(tr_recall) else float("nan"),
            "train_f1": float(tr_f1) if not np.isnan(tr_f1) else float("nan"),
            "val_precision": float(va_precision) if not np.isnan(va_precision) else float("nan"),
            "val_recall": float(va_recall) if not np.isnan(va_recall) else float("nan"),
            "val_f1": float(va_f1) if not np.isnan(va_f1) else float("nan"),
            "threshold": float(threshold),
            "n_train": int(y_train.size),
            "n_val": int(y_val.size),
            "n_total": int(y.size),
        },
    )

    # Build mask catalog similar to pytorch training_service
    try:
        wanted_cols = [
            "mask_id",
            "style",
            "strap_type",
            "perimeter_mm",
            "unique_internal_model_code",
        ]
        present = [c for c in wanted_cols if c in df.columns]
        mask_df = df[present].copy()
        if "mask_id" not in mask_df.columns:
            raise ValueError("mask_id column missing in training data; cannot build mask catalog")
        mask_df = mask_df.dropna(subset=["mask_id"]).copy()
        mask_df["mask_id"] = mask_df["mask_id"].astype(int)
        if "perimeter_mm" in mask_df.columns:
            mask_df["perimeter_mm"] = pd.to_numeric(mask_df["perimeter_mm"], errors="coerce")
        mask_df = mask_df.drop_duplicates(subset=["mask_id"], keep="last")

        mask_data: Dict[str, Any] = {}
        for _, row in mask_df.iterrows():
            mid = int(row["mask_id"]) if pd.notna(row.get("mask_id")) else None
            if mid is None:
                continue
            entry: Dict[str, Any] = {"mask_id": mid}
            if "style" in mask_df.columns:
                entry["style"] = None if pd.isna(row.get("style")) else str(row.get("style"))
            if "strap_type" in mask_df.columns:
                entry["strap_type"] = None if pd.isna(row.get("strap_type")) else str(row.get("strap_type"))
            if "perimeter_mm" in mask_df.columns:
                val = row.get("perimeter_mm")
                entry["perimeter_mm"] = None if pd.isna(val) else float(val)
            if "unique_internal_model_code" in mask_df.columns:
                entry["unique_internal_model_code"] = None if pd.isna(row.get("unique_internal_model_code")) else str(row.get("unique_internal_model_code"))
            mask_data[str(mid)] = entry

        s3_mask_paths = s3_io.save_mask_data(mask_data)
        s3_paths.update(s3_mask_paths)
    except Exception as e:
        logger.warning(f"Could not build/save mask data from training dataframe: {e}")

    return {
        "metrics": {
            "train_precision": tr_precision,
            "train_recall": tr_recall,
            "train_f1": tr_f1,
            "val_precision": va_precision,
            "val_recall": va_recall,
            "val_f1": va_f1,
            "threshold": threshold,
            "n_train": int(y_train.size),
            "n_val": int(y_val.size),
            "n_total": int(y.size),
        },
        "artifacts": s3_paths,
    }
