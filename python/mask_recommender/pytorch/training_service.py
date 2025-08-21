import io
import json
import logging
import time
import math
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np
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
    epochs: int = 80,
    batch_size: int = 64,
    lr: float = 1e-3,
    hidden: int = 384,
    depth: int = 5,
    dropout: float = 0.0,
    val_split: float = 0.1,
    target_col: str = "target",
) -> Dict[str, Any]:
    from torch.utils.data import DataLoader, Subset

    torch = init_torch()

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
        train_indices = list(range(n_total))
        val_indices = []
    else:
        proposed = int(n_total * val_split)
        val_size = max(1, min(n_total - 1, proposed))
        # Build stratified indices based on labels
        y_all = dataset.y.numpy() if dataset.y is not None else None
        if y_all is None:
            # fallback: non-stratified deterministic split
            rng = np.random.default_rng(seed=42)
            all_idx = np.arange(n_total)
            rng.shuffle(all_idx)
            val_indices = all_idx[:val_size].tolist()
            train_indices = all_idx[val_size:].tolist()
        else:
            pos_idx = np.where(y_all == 1)[0]
            neg_idx = np.where(y_all == 0)[0]
            rng = np.random.default_rng(seed=42)
            rng.shuffle(pos_idx)
            rng.shuffle(neg_idx)
            num_pos = pos_idx.size
            num_neg = neg_idx.size
            # desired per-class counts
            desired_pos = int(round(num_pos * (val_size / max(1, n_total))))
            desired_neg = val_size - desired_pos
            # clip to available
            desired_pos = max(0, min(num_pos, desired_pos))
            desired_neg = max(0, min(num_neg, desired_neg))
            # adjust if short due to clipping
            short = val_size - (desired_pos + desired_neg)
            if short > 0:
                # add remaining from the larger class if possible
                remaining_pos = num_pos - desired_pos
                take_pos = min(short, remaining_pos)
                desired_pos += take_pos
                short -= take_pos
                if short > 0:
                    remaining_neg = num_neg - desired_neg
                    take_neg = min(short, remaining_neg)
                    desired_neg += take_neg
                    short -= take_neg
            val_indices = np.concatenate([pos_idx[:desired_pos], neg_idx[:desired_neg]]).tolist()
            # build train as the rest
            mask = np.ones(n_total, dtype=bool)
            mask[np.array(val_indices, dtype=int)] = False
            train_indices = np.nonzero(mask)[0].tolist()
    train_ds, val_ds = Subset(dataset, train_indices), Subset(dataset, val_indices)

    DataLoader  # to satisfy type checker import
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Use logits + BCEWithLogits for more stable optimization; add sigmoid only at inference
    model = FitClassifier(
        MLPConfig(
            input_dim=len(feature_names),
            hidden_dim=hidden,
            depth=depth,
            dropout=dropout,
            num_classes=2,
            add_sigmoid=False,
        )
    ).to(device)

    # Initialize final layer bias to the logit of the positive prior
    try:
        y_all = dataset.y.numpy() if dataset.y is not None else None
        if y_all is not None and y_all.size > 0:
            pos_rate = float((y_all == 1).sum() / y_all.size)
            pos_rate = min(max(pos_rate, 1e-4), 1 - 1e-4)
            prior_logit = math.log(pos_rate / (1.0 - pos_rate))
            # locate last Linear layer
            last_linear_idx = None
            for i in range(len(model.net) - 1, -1, -1):
                if isinstance(model.net[i], torch.nn.Linear):
                    last_linear_idx = i
                    break
            if last_linear_idx is not None:
                with torch.no_grad():
                    model.net[last_linear_idx].bias.fill_(prior_logit)
    except Exception:
        pass

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
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else float('nan')
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else float('nan')
        if math.isnan(precision) or math.isnan(recall) or (precision + recall) == 0:
            f1 = float('nan')
        else:
            f1 = 2.0 * precision * recall / (precision + recall)
        npv = float(tn / (tn + fn)) if (tn + fn) > 0 else float('nan')
        return total_loss / n, total_acc / n, precision, npv, recall, f1

    def collect_val_outputs(model, loader, device):
        model.eval()
        all_probs = []
        all_targets = []
        with torch.no_grad():
            for X, y in loader:
                X = X.to(device)
                y = y.to(device)
                logits = model(X).view(-1)
                probs = torch.sigmoid(logits)
                all_probs.append(probs.cpu())
                all_targets.append(y.cpu())
        if all_probs:
            probs = torch.cat(all_probs).numpy()
            targets = torch.cat(all_targets).numpy()
        else:
            probs = torch.zeros(0)
            targets = torch.zeros(0)
        return probs, targets

    def collect_val_logits_targets(model, loader, device):
        model.eval()
        all_logits = []
        all_targets = []
        with torch.no_grad():
            for X, y in loader:
                X = X.to(device)
                y = y.to(device)
                logits = model(X).view(-1)
                all_logits.append(logits.cpu())
                all_targets.append(y.cpu())
        if all_logits:
            logits = torch.cat(all_logits)
            targets = torch.cat(all_targets)
        else:
            logits = torch.zeros(0)
            targets = torch.zeros(0, dtype=torch.long)
        return logits, targets

    def metrics_at_threshold(probs, targets, thr: float):
        if probs.size == 0:
            return float('nan'), float('nan'), float('nan')
        preds = (probs >= thr).astype(int)
        tp = int(((preds == 1) & (targets == 1)).sum())
        fp = int(((preds == 1) & (targets == 0)).sum())
        fn = int(((preds == 0) & (targets == 1)).sum())
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else float('nan')
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else float('nan')
        if math.isnan(precision) or math.isnan(recall) or (precision + recall) == 0:
            f1 = float('nan')
        else:
            f1 = 2.0 * precision * recall / (precision + recall)
        return precision, recall, f1

    # Class imbalance handling: upweight positive class if present
    try:
        labels_np = dataset.y.numpy() if dataset.y is not None else None
        if labels_np is not None:
            num_pos = int((labels_np == 1).sum())
            num_neg = int((labels_np == 0).sum())
            if num_pos > 0 and num_neg > 0:
                # upweight positives proportional to imbalance
                pos_weight = torch.tensor([num_neg / max(1, num_pos)], dtype=torch.float32, device=device)
                loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
            else:
                loss_fn = torch.nn.BCEWithLogitsLoss()
        else:
            loss_fn = torch.nn.BCEWithLogitsLoss()
    except Exception:
        loss_fn = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    best_f1 = -float("inf")
    best_state: Optional[Dict[str, Any]] = None
    best_metrics: Dict[str, Any] = {}
    for epoch in range(1, epochs + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        va_loss, va_acc, va_ppv, va_npv, va_recall, va_f1 = evaluate(model, val_loader, loss_fn, device)
        # Also compute metrics at a tuned threshold to improve PPV (precision)
        val_probs, val_targets = collect_val_outputs(model, val_loader, device)
        # Extended threshold tuning: search dense grid and target high precision
        candidates = np.linspace(0.5, 0.95, num=10).tolist()  # 0.50,0.55,...,0.95
        precision_target = 0.70
        tuned_ppv, tuned_recall, tuned_f1, tuned_thr = va_ppv, va_recall, va_f1, 0.5
        best_overall = (tuned_ppv, tuned_f1, -tuned_thr)
        # First pass: collect those meeting precision target
        feasible = []
        for thr in candidates:
            p, r, f = metrics_at_threshold(val_probs, val_targets, thr)
            if not math.isnan(p) and p >= precision_target:
                feasible.append((thr, p, r, f))
            # Track overall best by precision then F1 as fallback
            score = (p if not math.isnan(p) else -1.0, f if not math.isnan(f) else -1.0, -thr)
            if score > best_overall:
                best_overall = score
                tuned_thr, tuned_ppv, tuned_recall, tuned_f1 = thr, p, r, f
        if feasible:
            # Choose the feasible threshold with highest recall, then highest F1, then lowest thr
            feasible.sort(key=lambda x: (x[2], x[3], -x[0]), reverse=True)
            tuned_thr, tuned_ppv, tuned_recall, tuned_f1 = feasible[0]
        logger.info(
            f"epoch={epoch} train_loss={tr_loss:.4f} train_acc={tr_acc:.3f} "
            f"val_loss={va_loss:.4f} val_acc={va_acc:.3f} val_ppv={va_ppv:.3f} val_npv={va_npv:.3f} val_recall={va_recall:.3f} val_f1={va_f1:.3f} "
            f"tuned_thr={tuned_thr:.2f} tuned_ppv={tuned_ppv:.3f} tuned_recall={tuned_recall:.3f} tuned_f1={tuned_f1:.3f}"
        )
        # Select best checkpoint by validation F1 at threshold 0.5
        if not math.isnan(va_f1) and va_f1 > best_f1:
            best_f1 = va_f1
            best_state = {
                "model_state": model.state_dict(),
                "feature_names": feature_names,
                "config": {
                    "input_dim": len(feature_names),
                    "hidden_dim": hidden,
                    "depth": depth,
                    "dropout": dropout,
                    "num_classes": 2,
                    "add_sigmoid": False,
                },
                "stats": dataset.get_stats().__dict__ if dataset.get_stats() is not None else None,
                # Save tuned threshold favoring precision if available
                "threshold": float(tuned_thr),
            }
            best_metrics = {
                "epoch": epoch,
                "train_loss": tr_loss,
                "train_acc": tr_acc,
                "val_loss": va_loss,
                "val_acc": va_acc,
                "val_ppv": va_ppv,
                "val_npv": va_npv,
                "val_recall": va_recall,
                "val_f1": va_f1,
                "tuned_thr": float(tuned_thr),
                "tuned_ppv": float(tuned_ppv) if not math.isnan(tuned_ppv) else float('nan'),
                "tuned_recall": float(tuned_recall) if not math.isnan(tuned_recall) else float('nan'),
                "tuned_f1": float(tuned_f1) if not math.isnan(tuned_f1) else float('nan'),
                "threshold": float(tuned_thr),
            }

    # Ensure we always have a state to save, even if F1 is NaN throughout
    if best_state is None:
        best_state = {
            "model_state": model.state_dict(),
            "feature_names": feature_names,
            "config": {
                "input_dim": len(feature_names),
                "hidden_dim": hidden,
                "depth": depth,
                "dropout": dropout,
                "num_classes": 2,
                "add_sigmoid": False,
            },
            "stats": dataset.get_stats().__dict__ if dataset.get_stats() is not None else None,
            "threshold": 0.5,
        }
        best_metrics = {
            "epoch": epochs,
            "train_loss": tr_loss,
            "train_acc": tr_acc,
            "val_loss": va_loss,
            "val_acc": va_acc,
            "val_ppv": va_ppv,
            "val_npv": va_npv,
            "val_recall": va_recall,
            "val_f1": va_f1,
            "threshold": 0.5,
        }

    # Optional: Platt scaling on validation set to calibrate probabilities
    try:
        # Load best weights into model for calibration
        model.load_state_dict(best_state["model_state"])  # type: ignore[index]
        logits_val, targets_val = collect_val_logits_targets(model, val_loader, device)
        # Fit only if we have both classes present
        if logits_val.numel() > 0 and targets_val.numel() > 0 and targets_val.unique().numel() > 1:
            A = torch.tensor(1.0, requires_grad=True)
            B = torch.tensor(0.0, requires_grad=True)
            optimizer_platt = torch.optim.LBFGS([A, B], lr=0.5, max_iter=50)
            bce = torch.nn.BCEWithLogitsLoss()

            def closure():
                optimizer_platt.zero_grad()
                preds = A * logits_val + B
                loss = bce(preds, targets_val.float())
                loss.backward()
                return loss

            optimizer_platt.step(closure)
            best_state["platt"] = {"A": float(A.detach().cpu().item()), "B": float(B.detach().cpu().item())}
            best_metrics["platt_A"] = best_state["platt"]["A"]
            best_metrics["platt_B"] = best_state["platt"]["B"]
    except Exception:
        pass

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
