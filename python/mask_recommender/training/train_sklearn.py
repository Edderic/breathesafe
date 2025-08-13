from __future__ import annotations

import os
import sys
import json
import joblib
import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# Ensure the package root (the "python" directory) is on sys.path
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PKG_ROOT not in sys.path:
    sys.path.append(PKG_ROOT)

from mask_recommender.sklearn_pipeline import build_sklearn_pipeline


def is_test_env() -> bool:
    return os.environ.get('ENVIRONMENT', '').strip().lower() == 'test'


def fetch_dataset(url: str) -> pd.DataFrame:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and 'fit_tests_with_facial_measurements' in data:
        data = data['fit_tests_with_facial_measurements']
    return pd.DataFrame(data)


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        'qlft_pass',
        'mask_id',
        'style',
        'strap_type',
        'perimeter_mm',
        'face_width', 'face_length', 'bitragion_subnasale_arc', 'nose_protrusion',
    ]
    present = [c for c in cols if c in df.columns]
    out = df[present].dropna(subset=[c for c in present if c != 'strap_type'])
    # Ensure optional categoricals exist
    if 'strap_type' not in out.columns:
        out['strap_type'] = ''
    if 'style' not in out.columns:
        out['style'] = ''
    out['strap_type'] = out['strap_type'].astype(str).fillna('')
    out['style'] = out['style'].astype(str).fillna('')
    return out


def build_mask_metadata(df: pd.DataFrame) -> dict:
    """Aggregate style (mode), strap_type (mode) and perimeter (mean) per mask_id for inference."""
    meta = {}
    if 'mask_id' not in df.columns:
        return meta
    grouped = df.groupby('mask_id')
    for mask_id, g in grouped:
        style = ''
        if 'style' in g.columns and not g['style'].isna().all():
            style = g['style'].mode().iloc[0]
        strap_type = ''
        if 'strap_type' in g.columns and not g['strap_type'].isna().all():
            strap_type = g['strap_type'].mode().iloc[0]
        perimeter = 0.0
        if 'perimeter_mm' in g.columns:
            perimeter = float(g['perimeter_mm'].astype(float).mean())
        meta[str(int(mask_id))] = {
            'style': style,
            'strap_type': strap_type,
            'perimeter_mm': perimeter,
        }
    return meta


def train_and_save(df: pd.DataFrame) -> dict:
    df = select_columns(df)
    # Ensure proper dtypes
    df['qlft_pass'] = df['qlft_pass'].astype(int)
    df['mask_id'] = df['mask_id'].astype(int)
    df['perimeter_mm'] = df['perimeter_mm'].astype(float)

    X = df.drop(columns=['qlft_pass'])
    y = df['qlft_pass']

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    mask_ids = sorted(df['mask_id'].unique().tolist()) if 'mask_id' in df.columns else []
    pipe = build_sklearn_pipeline(mask_ids)
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, proba)

    # Save model
    model_path = '/tmp/mask_fit_model.joblib'
    joblib.dump(pipe, model_path)

    # Save mask metadata for inference (style, strap_type, perimeter)
    mask_meta = build_mask_metadata(df)
    mask_meta_path = '/tmp/mask_data.json'
    with open(mask_meta_path, 'w') as f:
        json.dump(mask_meta, f)

    return {
        'model_path': model_path,
        'mask_meta_path': mask_meta_path,
        'auc': float(auc),
        'num_train': int(len(X_train)),
        'num_val': int(len(X_val)),
    }


def main():
    url = 'https://www.breathesafe.xyz/facial_measurements_fit_tests.json'
    df = fetch_dataset(url)
    info = train_and_save(df)
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
