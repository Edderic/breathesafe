from __future__ import annotations

import argparse
from typing import List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV with features and target")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.0)
    parser.add_argument("--val_split", type=float, default=0.2)
    parser.add_argument("--save", type=str, default="fit_classifier.pt")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)

    # Build full feature list including dynamic mask_id_* columns present in CSV
    feature_names: List[str] = list(FEATURES)
    feature_names += [c for c in df.columns if c.startswith("mask_id_")]

    dataset = TabularFitDataset(df, feature_names=feature_names, target_col="target")

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
