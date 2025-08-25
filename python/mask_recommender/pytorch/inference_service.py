from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import torch

from .model import FitClassifier, MLPConfig
from . import s3_io as s3io


def to_float_safe(value: Any, default: float = 0.0) -> float:
    """Convert to float, treating None and invalid values as default."""
    if value is None:
        return float(default)
    try:
        return float(value)
    except Exception:
        return float(default)


def to_binary_float(value: Any) -> float:
    """Convert various truthy/falsey values to 0.0/1.0 floats safely."""
    if value is None:
        return 0.0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("1", "true", "t", "yes", "y"):  # truthy
            return 1.0
        if v in ("0", "false", "f", "no", "n", ""):
            return 0.0
    try:
        return 1.0 if int(value) != 0 else 0.0
    except Exception:
        return 1.0 if bool(value) else 0.0


def build_feature_row(feature_names: List[str], facial: Dict[str, Any], mask_info: Dict[str, Any]) -> pd.DataFrame:
    row: Dict[str, Any] = {k: 0 for k in feature_names}
    base_numeric = {
        "face_width": to_float_safe(facial.get("face_width")),
        "face_length": to_float_safe(facial.get("face_length")),
        "nose_protrusion": to_float_safe(facial.get("nose_protrusion")),
        "bitragion_subnasale_arc": to_float_safe(facial.get("bitragion_subnasale_arc")),
        "facial_hair_beard_length_mm": to_float_safe(facial.get("facial_hair_beard_length_mm")),
        # "lip_width": to_float_safe(facial.get("lip_width")),
        "perimeter_mm": to_float_safe(mask_info.get("perimeter_mm")),
        "adjustable_headstrap": to_binary_float(mask_info.get("adjustable_headstrap")),
        "adjustable_earloops": to_binary_float(mask_info.get("adjustable_earloops")),
    }
    for k, v in base_numeric.items():
        if k in row:
            row[k] = v
    mask_id_val = mask_info.get("mask_id", mask_info.get("id", ""))
    try:
        mask_id_int = int(mask_id_val)
    except Exception:
        mask_id_int = 0
    mask_id = str(mask_id_val)
    style_val = mask_info.get("style")
    strap_val = mask_info.get("strap_type")
    style = "" if style_val is None else str(style_val)
    strap_type = "" if strap_val is None else str(strap_val)
    one_hots = [f"mask_id_{mask_id}", f"style_{style}", f"strap_type_{strap_type}"]
    for oh in one_hots:
        if oh in row:
            row[oh] = 1
    df = pd.DataFrame([row])
    df["mask_id"] = mask_id_int
    return df


def standardize_numeric(X: np.ndarray, feature_names: List[str], stats: Optional[Dict[str, Any]]) -> np.ndarray:
    if not stats:
        return X
    mean = np.array(stats.get("mean", []), dtype=np.float32)
    std = np.array(stats.get("std", []), dtype=np.float32)
    is_binary = np.array(
        [
            name.startswith("mask_id_")
            or name.startswith("style_")
            or name.startswith("strap_type_")
            or name in ("adjustable_headstrap", "adjustable_earloops")
            for name in feature_names
        ]
    )
    idx = np.where(~is_binary)[0]
    if idx.size > 0 and mean.size == idx.size and std.size == idx.size:
        X[:, idx] = (X[:, idx] - mean) / np.where(std == 0, 1.0, std)
    return X


def infer(facial_measurements: Dict[str, Any], mask_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    try:
        state = s3io.load_latest_model()
    except Exception as e:
        # Fallback for torch.load weights_only default in PyTorch 2.6+ when loading pickled objects
        import torch.serialization as _ts
        try:
            with _ts.safe_globals([__import__('numpy').core.multiarray._reconstruct]):
                state = s3io.load_latest_model()
        except Exception:
            raise
    feature_names: List[str] = state["feature_names"]
    config = state["config"]
    stats = state.get("stats", None)

    model = FitClassifier(MLPConfig(**config))
    model.load_state_dict(state["model_state"])
    model.eval()

    mask_data = s3io.load_mask_data()
    items = list(mask_data.items())
    if mask_ids:
        wanted = set(int(i) for i in mask_ids)
        items = [(mid, info) for mid, info in items if int(mid) in wanted]

    rows = []
    for mid, info in items:
        info = {**info, "mask_id": int(mid)}
        df_row = build_feature_row(feature_names, facial_measurements, info)
        rows.append(df_row)
    if not rows:
        return {"mask_id": {}, "proba_fit": {}}

    df_all = pd.concat(rows, ignore_index=True)
    for c in feature_names:
        if c not in df_all.columns:
            df_all[c] = 0
    X = df_all[feature_names].to_numpy(dtype=np.float32)
    X = standardize_numeric(X, feature_names, stats)
    X = torch.from_numpy(X)

    with torch.no_grad():
        outputs = model(X).view(-1)
        # Apply Platt scaling if available
        platt = state.get("platt")
        if platt and ("A" in platt and "B" in platt):
            A = float(platt["A"])
            B = float(platt["B"])
            outputs = A * outputs + B
        # If model outputs logits (add_sigmoid=False), convert to probabilities
        if not config.get("add_sigmoid", True):
            probs = torch.sigmoid(outputs)
        else:
            probs = outputs
        probs = probs.numpy()

    sorted_idx = np.argsort(-probs)
    mask_ids_sorted = [int(df_all.iloc[i]["mask_id"]) for i in sorted_idx]
    out = {
        "mask_id": {str(i): mid for i, mid in enumerate(mask_ids_sorted)},
        "proba_fit": {str(i): float(probs[idx]) for i, idx in enumerate(sorted_idx)},
    }
    # Include threshold used during training for downstream decisions
    thr = float(state.get("threshold", 0.5))
    out["threshold"] = thr
    return out
