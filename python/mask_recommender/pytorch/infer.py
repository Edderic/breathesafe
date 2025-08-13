from __future__ import annotations

import argparse
import json
from typing import List, Optional, Any

import numpy as np
import pandas as pd
import torch
import requests


def _try_load_remote_json(url: str, timeout_s: float = 15.0) -> Optional[pd.DataFrame]:
    try:
        resp = requests.get(url, timeout=timeout_s)
        if resp.status_code != 200:
            return None
        data = resp.json()

        def to_records(obj: Any) -> Optional[List[dict]]:
            if isinstance(obj, list):
                return obj
            if isinstance(obj, dict):
                for key in [
                    "data",
                    "rows",
                    "items",
                    "records",
                    "facial_measurements_fit_tests",
                    "fit_tests_with_facial_measurements",
                ]:
                    if key in obj and isinstance(obj[key], list):
                        return obj[key]
            return None

        records = to_records(data)
        if records is None:
            return None
        df = pd.json_normalize(records)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--csv", type=str, default=None, help="CSV with features only (no target)")
    parser.add_argument("--data_url", type=str, default="https://www.breathesafe.xyz/facial_measurements_fit_tests.json", help="Remote JSON with features; used when available")
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    ckpt = torch.load(args.model, map_location="cpu")

    feature_names: List[str] = ckpt["feature_names"]
    stats = ckpt.get("stats", None)
    if stats is not None:
        mean = np.array(stats["mean"], dtype=np.float32)
        std = np.array(stats["std"], dtype=np.float32)

    # Prefer remote features if available, otherwise fall back to CSV
    df: Optional[pd.DataFrame] = None
    if args.data_url:
        df = _try_load_remote_json(args.data_url)
        if df is not None:
            print(f"Loaded remote dataset from {args.data_url} with shape {df.shape}")
    if df is None:
        if args.csv is None:
            raise SystemExit("No remote data available and --csv was not provided.")
        df = pd.read_csv(args.csv)
        print(f"Loaded local CSV from {args.csv} with shape {df.shape}")
    # Expand one-hots for raw categorical columns if present
    for cat_col, prefix in [("mask_id", "mask_id_"), ("style", "style_"), ("strap_type", "strap_type_")]:
        if cat_col in df.columns:
            dummies = pd.get_dummies(df[cat_col].astype(str), prefix=prefix.rstrip("_"))
            dummies.columns = [f"{prefix}{c.split('_',1)[1]}" if c.startswith(prefix.rstrip('_')+"_") else f"{prefix}{c}" for c in dummies.columns]
            for c in dummies.columns:
                if c not in df.columns:
                    df[c] = dummies[c]

    for c in feature_names:
        if c not in df.columns:
            df[c] = 0
    X = df[feature_names].to_numpy(dtype=np.float32)

    # numeric standardization: assume any non {0,1} is numeric; this is heuristic
    if stats is not None:
        # choose columns that are not strictly binary in the CSV
        is_binary = np.all(np.isin(X, [0.0, 1.0]), axis=0)
        numeric_idx = np.where(~is_binary)[0]
        if numeric_idx.size > 0:
            X[:, numeric_idx] = (X[:, numeric_idx] - mean) / std

    X = torch.from_numpy(X)

    from .model import FitClassifier, MLPConfig

    config = ckpt["config"]
    model = FitClassifier(MLPConfig(**config))
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    with torch.no_grad():
        probs = model(X).view(-1).numpy()
        preds = (probs >= 0.5).astype(int)

    out = {
        "pred": preds.tolist(),
        "probs": probs.tolist(),
        "feature_names": feature_names,
    }
    with open(args.out, "w") as f:
        json.dump(out, f)


if __name__ == "__main__":
    main()
