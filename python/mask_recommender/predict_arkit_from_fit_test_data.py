"""
Predict ARKit-style facial aggregates for users who lack them by leveraging
nearest-neighbor matches in fit-test results.

Workflow:
- Load `predicted_fit_tests.csv`, which may still contain NaNs for some users.
- Load a local export of fit tests (CSV or JSON) that includes pass/fail info.
- Represent each user as a vector over the masks THEY tested (1=pass, -1=fail, 0=unknown).
- For every user missing aggregates, find neighbors (users with actual aggregates)
  whose cosine similarity is >= 0 on the overlapping masks.
- Use a similarity-weighted average of those neighbors' aggregates to impute the
  missing `nose_mm`, `chin_mm`, `top_cheek_mm`, `mid_cheek_mm`, `strap_mm`.

Outputs:
- Updated fit-test level CSV with predicted aggregates filled in.
- User-level table (`user_predictions.csv`) summarizing which users were imputed,
  neighbor counts, and the `actual` flag (False for imputed rows).

To run:
    python ./python/mask_recommender/predict_arkit_from_fit_test_data.py \
        --predicted-fit-tests=python/mask_recommender/predicted_fit_tests.csv


"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from python.mask_recommender.breathesafe_network import (
  build_session,
  fetch_facial_measurements_fit_tests,
)

TARGET_COLUMNS = [
  "nose_mm",
  "chin_mm",
  "top_cheek_mm",
  "mid_cheek_mm",
  "strap_mm",
]

PASS_VALUE_TRUE = {True, 1, "1", "true", "TRUE", "t", "T", "pass", "PASS", "passed", "PASSED"}
PASS_VALUE_FALSE = {False, 0, "0", "false", "FALSE", "f", "F", "fail", "FAIL", "failed", "FAILED"}


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--predicted-fit-tests",
    type=Path,
    default=Path("python/mask_recommender/predicted_fit_tests.csv"),
    help="CSV produced by predict_arkit_from_traditional.py.",
  )
  parser.add_argument(
    "--fit-tests-base-url",
    type=str,
    default="http://localhost:3000",
    help="Base URL hosting the facial_measurements_fit_tests endpoint.",
  )
  parser.add_argument(
    "--output-fit-tests",
    type=Path,
    default=Path("python/mask_recommender/predicted_fit_tests_with_neighbors.csv"),
    help="Where to write the updated fit_test-level CSV.",
  )
  parser.add_argument(
    "--user-output",
    type=Path,
    default=Path("python/mask_recommender/fit_test_similarity_user_table.csv"),
    help="Where to write the user-level aggregates with `actual` flag.",
  )
  parser.add_argument(
    "--neighbors",
    type=int,
    default=5,
    help="Maximum number of neighbors to use for each imputation.",
  )
  parser.add_argument(
    "--min-similarity",
    type=float,
    default=0.0,
    help="Minimum cosine similarity required (inclusive).",
  )
  return parser.parse_args()


def normalize_pass_value(value) -> Optional[int]:
  if value in PASS_VALUE_TRUE:
    return 1
  if value in PASS_VALUE_FALSE:
    return -1
  return None


def derive_pass_column(df: pd.DataFrame) -> pd.Series:
  pass_columns = [col for col in df.columns if col.endswith("_pass")]
  if not pass_columns:
    raise ValueError(
      "Could not find any *_pass columns in fit-tests data. "
      "Please ensure the file came from facial_measurements_fit_tests."
    )

  values = []
  for _, row in df.iterrows():
    val = None
    for col in pass_columns:
      raw = row.get(col)
      normalized = normalize_pass_value(raw)
      if normalized is not None:
        val = normalized
        break
    values.append(val)
  return pd.Series(values, index=df.index, name="pass_flag")


def build_user_mask_matrix(df: pd.DataFrame) -> Dict[int, Dict[int, int]]:
  matrix: Dict[int, Dict[int, int]] = {}
  for _, row in df.iterrows():
    user_id = row.get("user_id")
    mask_id = row.get("mask_id")
    result = row.get("pass_flag")
    if pd.isna(user_id) or pd.isna(mask_id):
      continue
    matrix.setdefault(int(user_id), {})
    if result is None:
      continue
    matrix[int(user_id)][int(mask_id)] = int(result)
  return matrix


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
  if not vec_a.size or not vec_b.size:
    return 0.0
  denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
  if denom == 0:
    return 0.0
  return float(np.dot(vec_a, vec_b) / denom)


def user_vector(
  mask_ids: List[int], mask_results: Dict[int, int]
) -> np.ndarray:
  return np.array([mask_results.get(mask_id, 0) for mask_id in mask_ids], dtype=float)


def compute_user_measurements(predicted_df: pd.DataFrame) -> pd.DataFrame:
  grouped = predicted_df.groupby("user_id")[TARGET_COLUMNS].mean()
  return grouped


def users_with_complete_measurements(user_measurements: pd.DataFrame) -> pd.Index:
  return user_measurements.dropna(subset=TARGET_COLUMNS).index


def users_missing_measurements(user_measurements: pd.DataFrame) -> pd.Index:
  mask = user_measurements[TARGET_COLUMNS].isna().any(axis=1)
  return user_measurements[mask].index


def nearest_neighbor_predictions(
  target_user: int,
  mask_matrix: Dict[int, Dict[int, int]],
  available_users: Iterable[int],
  user_measurements: pd.DataFrame,
  neighbors: int,
  min_similarity: float,
) -> Optional[np.ndarray]:
  target_masks = mask_matrix.get(target_user, {})
  observed_masks = [mask for mask, result in target_masks.items() if result != 0]
  if not observed_masks:
    return None

  target_vec = user_vector(observed_masks, target_masks)
  similarities: List[Tuple[float, int]] = []

  for candidate in available_users:
    if candidate == target_user:
      continue
    candidate_masks = mask_matrix.get(candidate, {})
    candidate_vec = user_vector(observed_masks, candidate_masks)
    if not candidate_vec.any():
      continue
    sim = cosine_similarity(target_vec, candidate_vec)
    if sim >= min_similarity:
      similarities.append((sim, candidate))

  if not similarities:
    return None

  similarities.sort(reverse=True)
  top_neighbors = similarities[:neighbors]
  weights = np.array([sim for sim, _ in top_neighbors], dtype=float)
  if weights.sum() == 0:
    return None
  measurements = np.array(
    [user_measurements.loc[candidate, TARGET_COLUMNS].to_numpy() for _, candidate in top_neighbors],
    dtype=float,
  )
  weighted_average = np.average(measurements, axis=0, weights=weights)
  return weighted_average


def main() -> None:
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
  )
  args = parse_args()

  predicted_df = pd.read_csv(args.predicted_fit_tests)
  session = build_session(None)
  fit_tests_payload = fetch_facial_measurements_fit_tests(
    base_url=args.fit_tests_base_url,
    session=session,
  )
  fit_tests_df = pd.DataFrame(fit_tests_payload)
  fit_tests_df["pass_flag"] = derive_pass_column(fit_tests_df)

  user_measurements = compute_user_measurements(predicted_df)
  complete_users = set(users_with_complete_measurements(user_measurements))
  missing_users = set(users_missing_measurements(user_measurements))

  mask_matrix = build_user_mask_matrix(fit_tests_df)
  available_neighbors = [u for u in complete_users if u in mask_matrix]
  logging.info(
    "Users with complete measurements: %d | missing: %d",
    len(available_neighbors),
    len(missing_users),
  )

  user_predictions: Dict[int, np.ndarray] = {}
  for user_id in missing_users:
    if user_id not in mask_matrix:
      continue
    prediction = nearest_neighbor_predictions(
      target_user=user_id,
      mask_matrix=mask_matrix,
      available_users=available_neighbors,
      user_measurements=user_measurements,
      neighbors=args.neighbors,
      min_similarity=args.min_similarity,
    )
    if prediction is not None:
      user_predictions[user_id] = prediction

  if not user_predictions:
    logging.info("No users could be imputed via nearest neighbors.")
  else:
    logging.info("Predicted aggregates for %d users via fit-test similarity.", len(user_predictions))

  # Apply predictions back to predicted_df
  for user_id, values in user_predictions.items():
    for idx, column in enumerate(TARGET_COLUMNS):
      mask = (predicted_df["user_id"] == user_id) & predicted_df[column].isna()
      predicted_df.loc[mask, column] = values[idx]

  args.output_fit_tests.parent.mkdir(parents=True, exist_ok=True)
  predicted_df.to_csv(args.output_fit_tests, index=False)

  user_table = user_measurements.copy()
  user_table["actual"] = True
  for user_id, values in user_predictions.items():
    user_table.loc[user_id, TARGET_COLUMNS] = values
    user_table.loc[user_id, "actual"] = False

  args.user_output.parent.mkdir(parents=True, exist_ok=True)
  user_table.reset_index().to_csv(args.user_output, index=False)
  logging.info(
    "Wrote updated fit tests to %s and user table to %s",
    args.output_fit_tests,
    args.user_output,
  )


if __name__ == "__main__":
  main()
