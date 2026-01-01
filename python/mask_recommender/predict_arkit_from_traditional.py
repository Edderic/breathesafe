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
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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
    "--model-path",
    type=Path,
    default=Path("python/mask_recommender/arkit_prediction_model.pkl"),
    help="Optional path to persist the trained model as a pickle file.",
  )
  return parser.parse_args()


def build_session(cookie: str | None) -> requests.Session:
  session = requests.Session()
  if cookie:
    session.headers.update({"Cookie": cookie})
  session.headers.update({"Accept": "application/json"})
  return session


def login_with_credentials(
  session: requests.Session, base_url: str, email: str, password: str
) -> None:
  login_url = f"{base_url}/users/log_in.json"
  logging.info("Logging in via %s", login_url)
  response = session.post(
    login_url,
    json={"user": {"email": email, "password": password}},
    timeout=30,
  )
  if response.status_code != 200:
    raise RuntimeError(f"Login failed ({response.status_code}): {response.text}")
  logging.info("Login successful; session cookie established.")


def logout(session: requests.Session, base_url: str) -> None:
  logout_url = f"{base_url}/users/log_out.json"
  logging.info("Logging out via %s", logout_url)
  response = session.delete(logout_url, timeout=30)
  if response.status_code != 200:
    logging.warning(
      "Logout returned status %s: %s", response.status_code, response.text
    )
  else:
    logging.info("Logout successful.")


def fetch_json(session: requests.Session, url: str) -> Dict:
  logging.info("Fetching %s", url)
  response = session.get(url, timeout=60)
  response.raise_for_status()
  return response.json()


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
      ("scaler", StandardScaler(with_mean=False)),
      (
        "model",
        MultiOutputRegressor(
          RandomForestRegressor(
            n_estimators=400,
            random_state=42,
            n_jobs=-1,
            min_samples_leaf=5,
          )
        ),
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
