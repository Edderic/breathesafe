from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .dataset import TabularFitDataset
from .features import FEATURES
from .data_utils import expand_one_hots, filter_z_scores


def prepare_dataset(df: pd.DataFrame, target_col: str = "target") -> Tuple[TabularFitDataset, List[str]]:
    # Determine target
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
    # Clean target
    df = df.loc[df[target_col].notna()].copy()
    try:
        df[target_col] = df[target_col].astype(int)
    except Exception:
        cats = {v: i for i, v in enumerate(sorted(df[target_col].unique()))}
        df[target_col] = df[target_col].map(cats).astype(int)

    # Expand and filter
    df = expand_one_hots(df)
    df = filter_z_scores(df)

    feature_names: List[str] = list(FEATURES)
    feature_names += [
        c
        for c in df.columns
        if c.startswith("mask_id_") or c.startswith("style_") or c.startswith("strap_type_")
    ]

    dataset = TabularFitDataset(df, feature_names=feature_names, target_col=target_col)
    return dataset, feature_names
