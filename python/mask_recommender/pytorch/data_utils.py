from typing import Any, Dict, List, Optional

import pandas as pd
import requests


def try_load_remote_json(url: str, timeout_s: float = 15.0) -> Optional[pd.DataFrame]:
    try:
        resp = requests.get(url, timeout=timeout_s)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Normalize various shapes
        keys = [
            "data",
            "rows",
            "items",
            "records",
            "facial_measurements_fit_tests",
            "fit_tests_with_facial_measurements",
        ]
        records: Optional[List[Dict[str, Any]]] = None
        if isinstance(data, list):
            records = data  # type: ignore[assignment]
        elif isinstance(data, dict):
            for k in keys:
                if k in data and isinstance(data[k], list):
                    records = data[k]  # type: ignore[assignment]
                    break
        if records is None:
            return None
        df = pd.json_normalize(records)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def expand_one_hots(df: pd.DataFrame) -> pd.DataFrame:
    # Expand mask_id/style/strap_type
    for cat_col, prefix in [("mask_id", "mask_id_"), ("style", "style_"), ("strap_type", "strap_type_")]:
        if cat_col in df.columns:
            dummies = pd.get_dummies(df[cat_col].astype(str), prefix=prefix.rstrip("_"))
            dummies.columns = [
                f"{prefix}{c.split('_',1)[1]}" if c.startswith(prefix.rstrip('_')+"_") else f"{prefix}{c}"
                for c in dummies.columns
            ]
            for c in dummies.columns:
                if c not in df.columns:
                    df[c] = dummies[c]
    return df


def filter_z_scores(df: pd.DataFrame) -> pd.DataFrame:
    z_cols = [c for c in df.columns if c.endswith("_z_score")]
    if not z_cols:
        return df
    zdf = df[z_cols].apply(pd.to_numeric, errors="coerce")
    within = (zdf.abs() <= 2.25) | zdf.isna()
    mask = within.all(axis=1)
    out = df.loc[mask].copy()
    return out
