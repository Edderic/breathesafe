from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from .data_prep import prepare_dataset
from .features import FEATURES
from . import s3_io as s3io


def to_float_safe(value: Any, default: float = 0.0) -> float:
    if value is None:
        return float(default)
    try:
        return float(value)
    except Exception:
        return float(default)


def to_binary_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("1", "true", "t", "yes", "y"):
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
        # face_length intentionally omitted for RF
        "nose_protrusion": to_float_safe(facial.get("nose_protrusion")),
        "bitragion_subnasale_arc": to_float_safe(facial.get("bitragion_subnasale_arc")),
        "facial_hair_beard_length_mm": to_float_safe(facial.get("facial_hair_beard_length_mm")),
        # mask features
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
    style = "" if mask_info.get("style") is None else str(mask_info.get("style"))
    strap_type = "" if mask_info.get("strap_type") is None else str(mask_info.get("strap_type"))
    one_hots = [f"mask_id_{mask_id_val}", f"style_{style}", f"strap_type_{strap_type}"]
    for oh in one_hots:
        if oh in row:
            row[oh] = 1
    df = pd.DataFrame([row])
    df["mask_id"] = mask_id_int
    return df


def infer(facial_measurements: Dict[str, Any], mask_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    state = s3io.load_latest_model()
    feature_names: List[str] = state["feature_names"]
    stats = state.get("stats", None)  # may be unused for RF

    rf: RandomForestClassifier = state["model"]

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

    probs = rf.predict_proba(X)[:, 1]
    sorted_idx = np.argsort(-probs)
    mask_ids_sorted = [int(df_all.iloc[i]["mask_id"]) for i in sorted_idx]
    out = {
        "mask_id": {str(i): mid for i, mid in enumerate(mask_ids_sorted)},
        "proba_fit": {str(i): float(probs[idx]) for i, idx in enumerate(sorted_idx)},
    }
    out["threshold"] = float(state.get("threshold", 0.5))
    return out
