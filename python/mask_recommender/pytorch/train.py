from __future__ import annotations

import argparse
from typing import List, Tuple, Optional, Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import requests

from .dataset import TabularFitDataset
from .features import FEATURES
from .model import FitClassifier, MLPConfig


def accuracy(logits: torch.Tensor, y: torch.Tensor) -> float:
    preds = logits.argmax(dim=1)
    return (preds == y).float().mean().item()


def train_one_epoch(model, loader, loss_fn, optimizer, device) -> Tuple[float, float]:
    model.train()
    total_loss, total_acc, n = 0.0, 0.0, 0
    for X, y in loader:
        X = X.to(device)
        y = y.to(device)
        optimizer.zero_grad()
        logits = model(X)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

        bsz = y.size(0)
        total_loss += loss.item() * bsz
        total_acc += accuracy(logits.detach(), y) * bsz
        n += bsz
    return total_loss / n, total_acc / n


def evaluate(model, loader, loss_fn, device) -> Tuple[float, float]:
    model.eval()
    total_loss, total_acc, n = 0.0, 0.0, 0
    with torch.no_grad():
        for X, y in loader:
            X = X.to(device)
            y = y.to(device)
            logits = model(X)
            loss = loss_fn(logits, y)
            bsz = y.size(0)
            total_loss += loss.item() * bsz
            total_acc += accuracy(logits, y) * bsz
            n += bsz
    return total_loss / n, total_acc / n


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
        import pdb; pdb.set_trace()
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
    parser.add_argument("--csv", type=str, default=None, help="Path to CSV with features and target (fallback if remote not available)")
    parser.add_argument("--data_url", type=str, default="https://www.breathesafe.xyz/facial_measurements_fit_tests.json", help="Remote JSON with features/target; used when available")
    parser.add_argument("--target_col", type=str, default="target", help="Target column name in the dataset")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--val_split", type=float, default=0.2)
    parser.add_argument("--save", type=str, default="fit_classifier.pt")
    args = parser.parse_args()

    # Prefer remote data if available, otherwise fall back to CSV
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

    # Build full feature list including dynamic one-hots for mask_id/style/strap_type present in data
    feature_names: List[str] = list(FEATURES)
    # If raw categorical columns exist (non one-hot), expand them
    for cat_col, prefix in [("mask_id", "mask_id_"), ("style", "style_"), ("strap_type", "strap_type_")]:
        if cat_col in df.columns:
            dummies = pd.get_dummies(df[cat_col].astype(str), prefix=prefix.rstrip("_"))
            # Ensure column names follow prefix_value convention
            dummies.columns = [f"{prefix}{c.split('_',1)[1]}" if c.startswith(prefix.rstrip('_')+"_") else f"{prefix}{c}" for c in dummies.columns]
            for c in dummies.columns:
                if c not in df.columns:
                    df[c] = dummies[c]
    # Collect any one-hot columns that now exist
    feature_names += [c for c in df.columns if c.startswith("mask_id_") or c.startswith("style_") or c.startswith("strap_type_")]


    dataset = TabularFitDataset(df, feature_names=feature_names, target_col=args.target_col)

    val_size = int(len(dataset) * args.val_split)
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FitClassifier(MLPConfig(input_dim=len(feature_names), hidden_dim=args.hidden, depth=args.depth, dropout=args.dropout)).to(device)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    best_val = float("inf")
    for epoch in range(1, args.epochs + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        va_loss, va_acc = evaluate(model, val_loader, loss_fn, device)
        print(f"epoch={epoch} train_loss={tr_loss:.4f} train_acc={tr_acc:.3f} val_loss={va_loss:.4f} val_acc={va_acc:.3f}")
        if va_loss < best_val:
            best_val = va_loss
            torch.save({
                "model_state": model.state_dict(),
                "feature_names": feature_names,
                "config": {
                    "input_dim": len(feature_names),
                    "hidden_dim": args.hidden,
                    "depth": args.depth,
                    "dropout": args.dropout,
                    "num_classes": 3,
                },
                "stats": dataset.get_stats().__dict__ if dataset.get_stats() is not None else None,
            }, args.save)
            print(f"saved to {args.save}")


if __name__ == "__main__":
    main()
