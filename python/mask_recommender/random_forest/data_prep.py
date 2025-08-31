from typing import List, Tuple

import pandas as pd

from .features import FEATURES
from .data_utils import expand_one_hots, filter_z_scores


def prepare_dataset(df: pd.DataFrame, target_col: str = "target") -> Tuple[pd.DataFrame, List[str]]:
    if target_col not in df.columns:
        if "qlft_pass" in df.columns:
            col = df["qlft_pass"]
            if col.dtype == bool:
                df["target"] = col.astype(int)
            else:
                df["target"] = (
                    col.astype(str).str.lower().map({"true": 1, "false": 0}).fillna(0).astype(int)
                )
            target_col = "target"
        else:
            raise ValueError(f"Target column '{target_col}' not found and 'qlft_pass' missing.")

    df = df.loc[df[target_col].notna()].copy()
    try:
        df[target_col] = df[target_col].astype(int)
    except Exception:
        cats = {v: i for i, v in enumerate(sorted(df[target_col].unique()))}
        df[target_col] = df[target_col].map(cats).astype(int)

    df = expand_one_hots(df)
    df = filter_z_scores(df)

    # Drop rows with missing required facial features for RF
    required_facial = [
        "face_width",
        "nose_protrusion",
        "bitragion_subnasale_arc",
        "facial_hair_beard_length_mm",
    ]
    if any(c not in df.columns for c in required_facial):
        # If columns are missing entirely, create them so dropna below removes rows
        for c in required_facial:
            if c not in df.columns:
                df[c] = None
    df = df.dropna(subset=required_facial).copy()

    feature_names: List[str] = list(FEATURES)
    feature_names += [
        c
        for c in df.columns
        if c.startswith("mask_id_") or c.startswith("style_") or c.startswith("strap_type_")
    ]

    # Ensure all features exist
    for c in feature_names:
        if c not in df.columns:
            df[c] = 0

    return df, feature_names
