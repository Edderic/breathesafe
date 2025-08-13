from __future__ import annotations

import argparse
import json
from typing import List

import numpy as np
import pandas as pd
import torch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--csv", type=str, required=True, help="CSV with features only (no target)")
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    ckpt = torch.load(args.model, map_location="cpu")

    feature_names: List[str] = ckpt["feature_names"]
    stats = ckpt.get("stats", None)
    if stats is not None:
        mean = np.array(stats["mean"], dtype=np.float32)
        std = np.array(stats["std"], dtype=np.float32)

    df = pd.read_csv(args.csv)
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
        logits = model(X)
        probs = torch.softmax(logits, dim=1).numpy()
        preds = probs.argmax(axis=1)

    out = {
        "pred": preds.tolist(),
        "probs": probs.tolist(),
        "feature_names": feature_names,
    }
    with open(args.out, "w") as f:
        json.dump(out, f)


if __name__ == "__main__":
    main()
