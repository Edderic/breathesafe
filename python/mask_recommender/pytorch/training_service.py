import io
import json
import logging
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import torch

from .data_prep import prepare_dataset
from .data_utils import try_load_remote_json
from .model import FitClassifier, MLPConfig
from . import s3_io
from .torch_utils import init_torch

logger = logging.getLogger()
logger.setLevel(logging.INFO)


DEFAULT_DATA_URL = "https://www.breathesafe.xyz/facial_measurements_fit_tests.json"


def train(
    data_url: Optional[str] = None,
    csv_path: Optional[str] = None,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    hidden: int = 256,
    depth: int = 3,
    dropout: float = 0.1,
    val_split: float = 0.1,
    target_col: str = "target",
) -> Dict[str, Any]:
    from torch.utils.data import DataLoader, random_split

    torch = init_torch()
    import torch.nn as nn

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

    dataset, feature_names = prepare_dataset(df, target_col=target_col)

    n_total = len(dataset)
    if n_total <= 1:
        val_size = 0
        train_size = n_total
    else:
        proposed = int(n_total * val_split)
        val_size = max(1, min(n_total - 1, proposed))
        train_size = n_total - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))

    DataLoader  # to satisfy type checker import
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Use logits + BCEWithLogits for more stable optimization; add sigmoid only at inference
    model = FitClassifier(MLPConfig(input_dim=len(feature_names), hidden_dim=hidden, depth=depth, dropout=dropout, num_classes=2, add_sigmoid=False)).to(device)

    def accuracy(logits: torch.Tensor, y: torch.Tensor) -> float:
        probs = torch.sigmoid(logits).view(-1)
        preds = (probs >= 0.5).long()
        return (preds == y).float().mean().item()

    def train_one_epoch(model, loader, loss_fn, optimizer, device):
        model.train()
        total_loss, total_acc, n = 0.0, 0.0, 0
        for X, y in loader:
            X = X.to(device)
            y = y.to(device)
            optimizer.zero_grad()
            logits = model(X).view(-1)
            loss = loss_fn(logits, y.float())
            loss.backward()
            optimizer.step()
            bsz = y.size(0)
            total_loss += loss.item() * bsz
            total_acc += accuracy(logits.detach(), y) * bsz
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
                logits = model(X).view(-1)
                loss = loss_fn(logits, y.float())
                bsz = y.size(0)
                total_loss += loss.item() * bsz
                total_acc += accuracy(logits, y) * bsz
                n += bsz
                preds = (torch.sigmoid(logits) >= 0.5).long()
                tp += int(((preds == 1) & (y == 1)).sum().item())
                tn += int(((preds == 0) & (y == 0)).sum().item())
                fp += int(((preds == 1) & (y == 0)).sum().item())
                fn += int(((preds == 0) & (y == 1)).sum().item())
        ppv = float(tp / (tp + fp)) if (tp + fp) > 0 else float('nan')
        npv = float(tn / (tn + fn)) if (tn + fn) > 0 else float('nan')
        return total_loss / n, total_acc / n, ppv, npv

    # Class imbalance handling: upweight positive class if present
    try:
        labels_np = dataset.y.numpy() if dataset.y is not None else None
        if labels_np is not None:
            num_pos = int((labels_np == 1).sum())
            num_neg = int((labels_np == 0).sum())
            if num_pos > 0 and num_neg > 0:
                # moderate upweighting of positives
                pos_weight = torch.tensor([(num_neg / max(1, num_pos)) ** 0.5], dtype=torch.float32, device=device)
                loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
            else:
                loss_fn = torch.nn.BCEWithLogitsLoss()
        else:
            loss_fn = torch.nn.BCEWithLogitsLoss()
    except Exception:
        loss_fn = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    best_val = float("inf")
    best_state: Optional[Dict[str, Any]] = None
    best_metrics: Dict[str, Any] = {}
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
                    "add_sigmoid": True,
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

    s3_paths = s3_io.upload_checkpoint(best_state, best_metrics)  # type: ignore[arg-type]

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
            mid = int(row["mask_id"]) if pd.notna(row["mask_id"]) else None
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
        mask_data = {}

    return {"metrics": best_metrics, "artifacts": s3_paths, "mask_data": mask_data}
