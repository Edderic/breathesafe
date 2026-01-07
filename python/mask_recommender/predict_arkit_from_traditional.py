"""
Utility script that:

1. Downloads aggregated traditional + ARKit facial measurement data.
2. Trains a regression model to infer ARKit (nose_mm, strap_mm, etc.)
      from traditional measurements.
3. Fetches fit-test level facial measurement data and fills in missing
      ARKit aggregates with model predictions.

Usage example:

python python/mask_recommender/predict_arkit_from_traditional.py \
    --base-url http://localhost:3000 \
    --cookie "_session_id=YOUR_SESSION_COOKIE" \
    --output-file python/mask_recommender/predicted_fit_tests.csv
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List
import joblib

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from breathesafe_network import (
    build_session,
    login_with_credentials,
    logout,
    fetch_json,
)

FEATURE_COLUMNS = [
    "face_width",
    "face_length",
    "bitragion_subnasale_arc",
    "nose_protrusion",
    "nasal_root_breadth",
    "nose_bridge_height",
]

TARGET_COLUMNS = [
    "nose_mm",
    "strap_mm",
    "top_cheek_mm",
    "mid_cheek_mm",
    "chin_mm",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://localhost:3000",
        help="Base URL for the Breathesafe instance (default: %(default)s)",
    )
    parser.add_argument(
        "--cookie",
        default=None,
        help="Optional Cookie header value for authenticated requests "
        '(example: "_session_id=abc123"). If not provided, you must pass '
        "--email/--password for programmatic login.",
    )
    parser.add_argument(
        "--email",
        default=None,
        help="Service-account email for programmatic login.",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="Service-account password for programmatic login.",
    )
    parser.add_argument(
        "--logout",
        action="store_true",
        help="If set, call users/log_out at the end when login credentials were used.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path("python/mask_recommender/predicted_fit_tests.csv"),
        help="Where to store the CSV containing predictions for fit tests "
        "that lacked ARKit aggregates.",
    )
    parser.add_argument(
        "--users-output-file",
        type=Path,
        default=Path("python/mask_recommender/user_arkit_table.csv"),
        help="Where to store the CSV representing user-level ARKit aggregates "
        "(actual or predicted).",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("python/mask_recommender/arkit_prediction_model.pkl"),
        help="Optional path to persist the trained model as a pickle file.",
    )
    return parser.parse_args()


def prepare_dataframe(
    payload: List[Dict], feature_cols: List[str], target_cols: List[str]
) -> pd.DataFrame:
    df = pd.DataFrame(payload)

    for col in feature_cols + target_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    if "user_id" not in df.columns:
        raise RuntimeError("facial_measurements/summary payload must include user_id.")

    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    return df


def build_user_table(df: pd.DataFrame, pipeline: Pipeline):
    if "user_id" not in df.columns:
        raise RuntimeError(
            "facial_measurements/summary payload must include user_id for each row."
        )

    table_df = df.set_index("user_id")
    has_actual = table_df[TARGET_COLUMNS].notna().all(axis=1)
    has_full_features = table_df[FEATURE_COLUMNS].notna().all(axis=1)
    prediction_mask = (~has_actual) & has_full_features

    logging.info(
        "User summary: %d rows total | %d with actual ARKit aggregates | %d eligible for prediction.",
        len(table_df),
        has_actual.sum(),
        prediction_mask.sum(),
    )

    predicted_rows = pd.DataFrame(columns=TARGET_COLUMNS)
    if prediction_mask.any():
        features = table_df.loc[prediction_mask, FEATURE_COLUMNS]
        predictions = pipeline.predict(features)
        table_df.loc[prediction_mask, TARGET_COLUMNS] = predictions
        predicted_rows = table_df.loc[prediction_mask, TARGET_COLUMNS].copy()

    table_df["actual"] = has_actual
    return table_df.reset_index(), predicted_rows


def train_model(df: pd.DataFrame) -> Pipeline:
    feature_df = df[FEATURE_COLUMNS]
    target_df = df[TARGET_COLUMNS]

    target_complete = target_df.notna().all(axis=1)
    feature_complete = feature_df.notna().all(axis=1)
    valid_rows = target_complete & feature_complete
    if valid_rows.sum() == 0:
        raise RuntimeError(
            "No rows contain complete traditional + ARKit aggregates. Cannot train model."
        )

    X_train = feature_df.loc[valid_rows]
    y_train = target_df.loc[valid_rows]

    if len(X_train) < 20:
        logging.warning(
            "Only %d rows available for training. Predictions may be noisy.",
            len(X_train),
        )

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                MultiOutputRegressor(LinearRegression()),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_train)
    r2 = r2_score(y_train, predictions, multioutput="uniform_average")
    mae = mean_absolute_error(y_train, predictions, multioutput="uniform_average")
    logging.info("Training metrics -> R^2: %.4f  MAE: %.4f mm", r2, mae)

    return pipeline


def predict_missing_arkit(
    pipeline: Pipeline, df: pd.DataFrame
) -> pd.DataFrame:
    df = df.copy()
    aggregated = df[TARGET_COLUMNS]
    missing_mask = aggregated.isna().all(axis=1)
    feature_complete = df[FEATURE_COLUMNS].notna().all(axis=1)
    import pdb; pdb.set_trace()

    eligible_mask = missing_mask & feature_complete

    logging.info(
        "Found %d / %d fit tests lacking ARKit aggregates and eligible for prediction.",
        eligible_mask.sum(),
        len(df),
    )

    if eligible_mask.any():
        features = df.loc[eligible_mask, FEATURE_COLUMNS]
        predicted = pipeline.predict(features)
        df.loc[eligible_mask, TARGET_COLUMNS] = predicted

    return df


def predict_arkit_from_traditional(
    base_url,
    cookie=None,
    email=None,
    password=None,
    model_path=None,
    users_output_file=None,
    output_file=None
):
    base_url = base_url.rstrip("/")
    session = build_session(cookie)

    logged_in = False
    if cookie:
        logging.info("Using provided cookie for authentication.")
    elif email and password:
        login_with_credentials(session, base_url, email, password)
        logged_in = True
    else:
        raise SystemExit(
            "Authentication required. Provide either --cookie or --email/--password."
        )

    summary_url = f"{base_url}/facial_measurements/summary.json"
    fit_tests_url = f"{base_url}/facial_measurements_fit_tests.json"

    summary_payload = fetch_json(session, summary_url)["facial_measurements"]
    summary_df = prepare_dataframe(summary_payload, FEATURE_COLUMNS, TARGET_COLUMNS)

    model = train_model(summary_df)
    if model_path:
        model_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(model, model_path)
        logging.info("Saved trained model to %s", model_path)

    user_table_df, _ = build_user_table(summary_df, model)

    if users_output_file:
        users_output_file.parent.mkdir(parents=True, exist_ok=True)
        user_table_df[
            ["user_id"] + FEATURE_COLUMNS + TARGET_COLUMNS + ["actual"]
        ].to_csv(users_output_file, index=False)

        logging.info("Wrote user-level ARKit aggregates to %s", users_output_file)

    fit_tests_payload = fetch_json(session, fit_tests_url)[
        "fit_tests_with_facial_measurements"
    ]

    logout(session, base_url)

    fit_tests_df = prepare_dataframe(fit_tests_payload, FEATURE_COLUMNS, TARGET_COLUMNS)

    with_present_qlft_pass = fit_tests_df[fit_tests_df['qlft_pass'].notna()]

    fit_tests_enhanced_with_traditional_to_arkit_model = with_present_qlft_pass.merge(user_table_df, on='user_id', how='left', suffixes=('', '_imputation'))

    for col in TARGET_COLUMNS:
        imputed_col = f"{col}_imputation"
        if imputed_col not in fit_tests_enhanced_with_traditional_to_arkit_model.columns:
            continue

        if col in fit_tests_enhanced_with_traditional_to_arkit_model.columns:
            missing_mask = fit_tests_enhanced_with_traditional_to_arkit_model[col].isna()
            fit_tests_enhanced_with_traditional_to_arkit_model.loc[
                missing_mask, col
            ] = fit_tests_enhanced_with_traditional_to_arkit_model.loc[
                missing_mask, imputed_col
            ]
        else:
            fit_tests_enhanced_with_traditional_to_arkit_model[col] = fit_tests_enhanced_with_traditional_to_arkit_model[
                imputed_col
            ]

    fit_tests_enhanced_with_traditional_to_arkit_model = fit_tests_enhanced_with_traditional_to_arkit_model.drop(
        [f"{col}_imputation" for col in TARGET_COLUMNS],
        axis=1,
        errors="ignore",
    )

    output = fit_tests_enhanced_with_traditional_to_arkit_model

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)

        output.to_csv(
            output_file,
            index=False,
        )

    return output


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    args = parse_args()
    arkit_predictions = predict_arkit_from_traditional(
        base_url=args.base_url,
        cookie=args.cookie,
        email=args.email,
        password=args.password
    )

    logging.info("Wrote predictions to %s", args.output_file)


if __name__ == "__main__":
    main()
