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

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from python.mask_recommender.breathesafe_network import (
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

  return df


def build_user_table(df: pd.DataFrame, pipeline: Pipeline) -> pd.DataFrame:
  if "user_id" not in df.columns:
    raise RuntimeError(
      "facial_measurements/summary payload must include user_id for each row."
    )

  table_df = df.copy()
  has_actual = table_df[TARGET_COLUMNS].notna().all(axis=1)
  missing_mask = ~has_actual

  logging.info(
    "User summary: %d rows total | %d with actual ARKit aggregates | %d needing predictions.",
    len(table_df),
    has_actual.sum(),
    missing_mask.sum(),
  )

  if missing_mask.any():
    features = table_df.loc[missing_mask, FEATURE_COLUMNS]
    predictions = pipeline.predict(features)
    table_df.loc[missing_mask, TARGET_COLUMNS] = predictions

  table_df["actual"] = has_actual
  return table_df


def train_model(df: pd.DataFrame) -> Pipeline:
  feature_df = df[FEATURE_COLUMNS]
  target_df = df[TARGET_COLUMNS]

  valid_rows = target_df.dropna().index
  if len(valid_rows) == 0:
    raise RuntimeError(
      "No rows contain complete ARKit aggregates. Cannot train model."
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
      ("imputer", SimpleImputer(strategy="median")),
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

  logging.info(
    "Found %d / %d fit tests lacking ARKit aggregates.",
    missing_mask.sum(),
    len(df),
  )

  if missing_mask.any():
    features = df.loc[missing_mask, FEATURE_COLUMNS].apply(
      pd.to_numeric, errors="coerce"
    )
    predicted = pipeline.predict(features)
    df.loc[missing_mask, TARGET_COLUMNS] = predicted

  return df


def main() -> None:
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
  )
  args = parse_args()
  base_url = args.base_url.rstrip("/")
  session = build_session(args.cookie)

  logged_in = False
  if args.cookie:
    logging.info("Using provided cookie for authentication.")
  elif args.email and args.password:
    login_with_credentials(session, base_url, args.email, args.password)
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
  if args.model_path:
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    import joblib

    joblib.dump(model, args.model_path)
    logging.info("Saved trained model to %s", args.model_path)

  user_table_df = build_user_table(summary_df, model)
  args.users_output_file.parent.mkdir(parents=True, exist_ok=True)
  user_table_df[
    ["user_id"] + FEATURE_COLUMNS + TARGET_COLUMNS + ["actual"]
  ].to_csv(args.users_output_file, index=False)
  logging.info("Wrote user-level ARKit aggregates to %s", args.users_output_file)

  fit_tests_payload = fetch_json(session, fit_tests_url)[
    "fit_tests_with_facial_measurements"
  ]

  fit_tests_df = prepare_dataframe(fit_tests_payload, FEATURE_COLUMNS, TARGET_COLUMNS)
  fit_tests_df["fit_test_id"] = [
    row.get("id") for row in fit_tests_payload
  ]
  fit_tests_df["user_id"] = [
    row.get("user_id") for row in fit_tests_payload
  ]
  fit_tests_df["mask_id"] = [
    row.get("mask_id") for row in fit_tests_payload
  ]

  enriched_df = predict_missing_arkit(model, fit_tests_df)

  args.output_file.parent.mkdir(parents=True, exist_ok=True)
  enriched_df[["fit_test_id", "user_id", "mask_id"] + FEATURE_COLUMNS + TARGET_COLUMNS].to_csv(
    args.output_file,
    index=False,
  )
  logging.info("Wrote predictions to %s", args.output_file)

  if logged_in and args.logout:
    logout(session, base_url)


if __name__ == "__main__":
  main()
