# ruff: noqa: N803 N806
"""
PyTorch training script for predicting qualitative fit test (QLFT) outcomes.

The script pulls merged facial measurement + fit test data from
`/facial_measurements_fit_tests.json`, engineers features that capture the
assumptions provided by the user (mask-specific Gaussian priors, perimeter
compatibility, and facial hair penalties), and trains a binary classifier with
class-imbalance aware loss.
"""

from __future__ import annotations

import argparse
import logging
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import requests
import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, Dataset, Subset

LOGGER = logging.getLogger("mask_recommender.mvn.training")

FACIAL_FEATURES = ["nose_mm", "top_cheek_mm", "mid_cheek_mm", "chin_mm"]
CATEGORICAL_STRAP_FALLBACK = "Unknown strap"
CATEGORICAL_STYLE_FALLBACK = "Unknown style"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def safe_float(value: Optional[float]) -> Optional[float]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_fit_test_records(url: str, timeout: int = 30) -> List[dict]:
    LOGGER.info("Fetching data from %s", url)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    records = payload.get("fit_tests_with_facial_measurements", [])
    LOGGER.info("Retrieved %d records", len(records))
    if not records:
        raise RuntimeError("No records returned from endpoint.")
    return records


def compute_mask_feature_stats(records: Iterable[dict]) -> Dict[int, Dict[str, Tuple[float, float]]]:
    accumulators: Dict[int, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for row in records:
        mask_id = row.get("mask_id")
        if mask_id is None:
            continue
        for feature in FACIAL_FEATURES:
            value = safe_float(row.get(feature))
            if value is not None:
                accumulators[mask_id][feature].append(value)

    stats: Dict[int, Dict[str, Tuple[float, float]]] = {}
    for mask_id, feature_values in accumulators.items():
        stats[mask_id] = {}
        for feature, values in feature_values.items():
            if values:
                arr = np.asarray(values, dtype=np.float32)
                stats[mask_id][feature] = (float(arr.mean()), float(arr.std() + 1e-6))
    return stats


def build_index(mapping_values: Iterable[str]) -> Dict[str, int]:
    return {value: idx for idx, value in enumerate(sorted(set(mapping_values)))}


def engineer_features(
    records: List[dict],
) -> Tuple[List[dict], Dict[int, int], Dict[str, int], Dict[str, int], Dict[int, Dict[str, Tuple[float, float]]]]:
    mask_stats = compute_mask_feature_stats(records)
    cleaned_rows: List[dict] = []
    mask_ids: List[int] = []
    styles: List[str] = []
    straps: List[str] = []

    for row in records:
        mask_id = row.get("mask_id")
        if mask_id is None:
            continue

        features = {}
        missing_feature = False
        for feature in FACIAL_FEATURES:
            value = safe_float(row.get(feature))
            if value is None:
                missing_feature = True
                break
            features[feature] = value
        if missing_feature:
            continue

        perimeter = safe_float(row.get("perimeter_mm"))
        facial_hair = safe_float(row.get("facial_hair_beard_length_mm"))
        qlft_pass = row.get("qlft_pass")
        if perimeter is None or qlft_pass is None:
            continue

        style = (row.get("style") or CATEGORICAL_STYLE_FALLBACK).strip() or CATEGORICAL_STYLE_FALLBACK
        strap = (row.get("strap_type") or CATEGORICAL_STRAP_FALLBACK).strip() or CATEGORICAL_STRAP_FALLBACK

        sum_faces = sum(features.values())
        perimeter_gap = perimeter - sum_faces
        perimeter_ratio = perimeter / max(sum_faces, 1e-6)

        mask_feature_stats = mask_stats.get(mask_id, {})
        mask_zscores = []
        mask_zscores_sq = []
        for feature in FACIAL_FEATURES:
            mean_std = mask_feature_stats.get(feature)
            if mean_std:
                mean, std = mean_std
                z = (features[feature] - mean) / std
            else:
                z = 0.0
            mask_zscores.append(z)
            mask_zscores_sq.append(z * z)

        cleaned_rows.append(
            {
                "mask_id": int(mask_id),
                "style": style,
                "strap_type": strap,
                "facial_features": [features[f] for f in FACIAL_FEATURES],
                "mask_zscores": mask_zscores,
                "mask_zscores_sq": mask_zscores_sq,
                "perimeter_mm": perimeter,
                "perimeter_gap": perimeter_gap,
                "perimeter_ratio": perimeter_ratio,
                "facial_hair_beard_length_mm": 0.0 if facial_hair is None else facial_hair,
                "label": 1.0 if bool(qlft_pass) else 0.0,
            }
        )
        mask_ids.append(int(mask_id))
        styles.append(style)
        straps.append(strap)

    LOGGER.info("Filtered down to %d usable records with complete facial measurements", len(cleaned_rows))
    if not cleaned_rows:
        raise RuntimeError(
            "No usable records after filtering. Ensure aggregated ARKit measurements are populated in the API response."
        )

    mask_index = {mask_id: idx for idx, mask_id in enumerate(sorted(set(mask_ids)))}
    style_index = build_index(styles) or {CATEGORICAL_STYLE_FALLBACK: 0}
    strap_index = build_index(straps) or {CATEGORICAL_STRAP_FALLBACK: 0}
    return cleaned_rows, mask_index, style_index, strap_index, mask_stats


class FitTestDataset(Dataset):
    def __init__(
        self,
        rows: List[dict],
        mask_index: Dict[int, int],
        style_index: Dict[str, int],
        strap_index: Dict[str, int],
    ) -> None:
        self.mask_count = len(mask_index)
        numeric_features: List[List[float]] = []
        mask_one_hot: List[np.ndarray] = []
        style_ids: List[int] = []
        strap_ids: List[int] = []
        labels: List[float] = []

        for row in rows:
            facial_features = row["facial_features"]
            mask_zscores = row["mask_zscores"]
            mask_zscores_sq = row["mask_zscores_sq"]
            derived = [
                row["perimeter_mm"],
                row["perimeter_gap"],
                row["perimeter_ratio"],
                row["facial_hair_beard_length_mm"],
                math.log1p(row["facial_hair_beard_length_mm"]),
            ]
            numeric_features.append(facial_features + mask_zscores + mask_zscores_sq + derived)

            mask_vec = np.zeros(self.mask_count, dtype=np.float32)
            mask_vec[mask_index[row["mask_id"]]] = 1.0
            mask_one_hot.append(mask_vec)

            style_ids.append(style_index[row["style"]])
            strap_ids.append(strap_index[row["strap_type"]])
            labels.append(row["label"])

        numeric_matrix = np.asarray(numeric_features, dtype=np.float32)
        self.numeric_mean = numeric_matrix.mean(axis=0)
        self.numeric_std = numeric_matrix.std(axis=0) + 1e-6
        normalized_numeric = (numeric_matrix - self.numeric_mean) / self.numeric_std

        self.numeric = torch.tensor(normalized_numeric, dtype=torch.float32)
        self.masks = torch.tensor(np.asarray(mask_one_hot, dtype=np.float32), dtype=torch.float32)
        self.style_ids = torch.tensor(style_ids, dtype=torch.long)
        self.strap_ids = torch.tensor(strap_ids, dtype=torch.long)
        self.labels = torch.tensor(labels, dtype=torch.float32)
        self.feature_dim = self.numeric.shape[1]

    def __len__(self) -> int:
        return self.numeric.shape[0]

    def __getitem__(self, idx: int) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
        return (
            self.numeric[idx],
            self.masks[idx],
            self.style_ids[idx],
            self.strap_ids[idx],
            self.labels[idx],
        )


class MaskFitModel(nn.Module):
    def __init__(
        self,
        numeric_dim: int,
        mask_count: int,
        style_count: int,
        strap_count: int,
        hidden_dim: int = 256,
        dropout: float = 0.2,
        style_emb_dim: int = 4,
        strap_emb_dim: int = 4,
    ) -> None:
        super().__init__()
        self.style_embedding = nn.Embedding(style_count, style_emb_dim)
        self.strap_embedding = nn.Embedding(strap_count, strap_emb_dim)
        input_dim = numeric_dim + mask_count + style_emb_dim + strap_emb_dim
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, hidden_dim // 4),
            nn.ReLU(),
            nn.Linear(hidden_dim // 4, 1),
        )

    def forward(self, numeric: Tensor, mask_one_hot: Tensor, style_ids: Tensor, strap_ids: Tensor) -> Tensor:
        embeddings = torch.cat(
            [
                numeric,
                mask_one_hot,
                self.style_embedding(style_ids),
                self.strap_embedding(strap_ids),
            ],
            dim=1,
        )
        return self.network(embeddings).squeeze(1)


def split_dataset(dataset: FitTestDataset, seed: int) -> Tuple[Subset, Subset, Subset]:
    indices = list(range(len(dataset)))
    random.Random(seed).shuffle(indices)
    train_end = int(0.7 * len(indices))
    val_end = int(0.85 * len(indices))
    return (
        Subset(dataset, indices[:train_end]),
        Subset(dataset, indices[train_end:val_end]),
        Subset(dataset, indices[val_end:]),
    )


def compute_class_weight(labels: Tensor) -> float:
    positives = labels.sum().item()
    negatives = labels.shape[0] - positives
    if positives == 0:
        return 1.0
    return negatives / max(positives, 1.0)


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> Dict[str, float]:
    model.eval()
    criterion = nn.BCEWithLogitsLoss()
    total_loss = 0.0
    preds: List[int] = []
    targets: List[int] = []
    with torch.no_grad():
        for numeric, mask_vec, style_ids, strap_ids, labels in loader:
            numeric = numeric.to(device)
            mask_vec = mask_vec.to(device)
            style_ids = style_ids.to(device)
            strap_ids = strap_ids.to(device)
            labels = labels.to(device)
            logits = model(numeric, mask_vec, style_ids, strap_ids)
            loss = criterion(logits, labels)
            total_loss += loss.item() * labels.size(0)
            probabilities = torch.sigmoid(logits)
            preds.extend((probabilities >= 0.5).long().tolist())
            targets.extend(labels.long().tolist())

    accuracy = np.mean([p == t for p, t in zip(preds, targets)]) if preds else 0.0
    tp = sum(1 for p, t in zip(preds, targets) if p == t == 1)
    fp = sum(1 for p, t in zip(preds, targets) if p == 1 and t == 0)
    fn = sum(1 for p, t in zip(preds, targets) if p == 0 and t == 1)
    precision = tp / (tp + fp + 1e-9)
    recall = tp / (tp + fn + 1e-9)
    return {
        "loss": total_loss / max(len(loader.dataset), 1),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
    }


def train(
    dataset: FitTestDataset,
    args: argparse.Namespace,
) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_set, val_set, test_set = split_dataset(dataset, args.seed)

    def make_loader(split: Subset, shuffle: bool) -> DataLoader:
        return DataLoader(split, batch_size=args.batch_size, shuffle=shuffle, drop_last=False)

    train_loader = make_loader(train_set, shuffle=True)
    val_loader = make_loader(val_set, shuffle=False)
    test_loader = make_loader(test_set, shuffle=False)

    model = MaskFitModel(
        numeric_dim=dataset.feature_dim,
        mask_count=dataset.mask_count,
        style_count=int(dataset.style_ids.max().item() + 1),
        strap_count=int(dataset.strap_ids.max().item() + 1),
        hidden_dim=args.hidden_dim,
        dropout=args.dropout,
    ).to(device)

    pos_weight_value = compute_class_weight(dataset.labels)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pos_weight_value, device=device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

    best_val_loss = float("inf")
    best_state = None

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for numeric, mask_vec, style_ids, strap_ids, labels in train_loader:
            numeric = numeric.to(device)
            mask_vec = mask_vec.to(device)
            style_ids = style_ids.to(device)
            strap_ids = strap_ids.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            logits = model(numeric, mask_vec, style_ids, strap_ids)
            loss = criterion(logits, labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()
            total_loss += loss.item() * labels.size(0)

        train_loss = total_loss / max(len(train_loader.dataset), 1)
        val_metrics = evaluate(model, val_loader, device)
        LOGGER.info(
            "Epoch %d/%d — train_loss=%.4f val_loss=%.4f val_acc=%.3f val_prec=%.3f val_rec=%.3f",
            epoch,
            args.epochs,
            train_loss,
            val_metrics["loss"],
            val_metrics["accuracy"],
            val_metrics["precision"],
            val_metrics["recall"],
        )

        if val_metrics["loss"] < best_val_loss:
            best_val_loss = val_metrics["loss"]
            best_state = model.state_dict()

    if best_state is None:
        raise RuntimeError("Training failed to produce a valid model state.")

    model.load_state_dict(best_state)
    test_metrics = evaluate(model, test_loader, device)
    LOGGER.info(
        "Test metrics — loss=%.4f acc=%.3f prec=%.3f rec=%.3f",
        test_metrics["loss"],
        test_metrics["accuracy"],
        test_metrics["precision"],
        test_metrics["recall"],
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / "mask_fit_model.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "numeric_mean": dataset.numeric_mean,
            "numeric_std": dataset.numeric_std,
            "mask_count": dataset.mask_count,
            "style_vocab_size": int(dataset.style_ids.max().item() + 1),
            "strap_vocab_size": int(dataset.strap_ids.max().item() + 1),
            "config": vars(args),
        },
        artifact_path,
    )
    LOGGER.info("Saved best model to %s", artifact_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train MVN-based mask fit predictor.")
    parser.add_argument("--url", type=str, default="http://localhost:3000/facial_measurements_fit_tests.json")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output-dir", type=str, default="python/mask_recommender/mvn/artifacts")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parse_args()
    set_seed(args.seed)
    raw_records = fetch_fit_test_records(args.url)
    rows, mask_index, style_index, strap_index, _ = engineer_features(raw_records)
    dataset = FitTestDataset(rows, mask_index, style_index, strap_index)
    LOGGER.info(
        "Dataset: %d samples | %d masks | %d styles | %d strap types",
        len(dataset),
        dataset.mask_count,
        int(dataset.style_ids.max().item() + 1),
        int(dataset.strap_ids.max().item() + 1),
    )
    train(dataset, args)


if __name__ == "__main__":
    main()

