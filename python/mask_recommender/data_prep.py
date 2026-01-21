import logging
import os

import pandas as pd
from breathesafe_network import build_session, fetch_facial_measurements_fit_tests, fetch_json
from predict_arkit_from_traditional import predict_arkit_from_traditional

FACIAL_FEATURE_COLUMNS = [
    'nose_mm',
    'chin_mm',
    'top_cheek_mm',
    'mid_cheek_mm',
    'strap_mm',
]

BAYESIAN_FACE_COLUMNS = [
    'nose_mm',
    'chin_mm',
    'top_cheek_mm',
    'mid_cheek_mm',
]


def _normalize_pass(value):
    if isinstance(value, bool):
        return int(value)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    normalized = str(value).strip().lower()
    if normalized in ['true', '1', 'pass', 'passed', 'yes', 'y']:
        return 1
    if normalized in ['false', '0', 'fail', 'failed', 'no', 'n']:
        return 0
    return None


def normalize_pass(value):
    return _normalize_pass(value)


def _is_truthy(value):
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return str(value).strip().lower() in ['true', '1', 'yes', 'y']


def is_truthy(value):
    return _is_truthy(value)


def load_fit_tests_with_imputation(base_url, session=None, email=None, password=None, cookie=None):
    session = session or build_session(None)
    fit_tests_payload = fetch_facial_measurements_fit_tests(
        base_url=base_url,
        session=session
    )
    fit_tests = pd.DataFrame(fit_tests_payload)

    email = email or os.getenv('BREATHESAFE_SERVICE_EMAIL')
    password = password or os.getenv('BREATHESAFE_SERVICE_PASSWORD')
    if email and password:
        return predict_arkit_from_traditional(
            base_url=base_url,
            cookie=cookie,
            email=email,
            password=password,
        )

    logging.info("BREATHESAFE_SERVICE_EMAIL/PASSWORD not set; skipping ARKit imputation.")
    return fit_tests


def filter_fit_tests_for_bayesian(df):
    filtered = df.copy()
    filtered = filtered[filtered["perimeter_mm"].notna()]
    filtered = filtered[filtered["perimeter_mm"] > 0]

    if "mask_modded" in filtered.columns:
        filtered = filtered[~filtered["mask_modded"].apply(_is_truthy)]

    filtered = filtered.dropna(subset=BAYESIAN_FACE_COLUMNS)
    filtered = filtered[filtered["unique_internal_model_code"].notna()]
    filtered = filtered[filtered["style"].notna()]
    filtered = filtered[filtered["strap_type"].notna()]

    filtered["qlft_pass_normalized"] = filtered["qlft_pass"].apply(_normalize_pass)
    filtered = filtered[filtered["qlft_pass_normalized"].notna()]
    return filtered


def get_masks(session, masks_url):
    session = session or build_session(None)
    masks_payload = fetch_json(session, masks_url).get("masks", [])
    return pd.DataFrame(masks_payload)
