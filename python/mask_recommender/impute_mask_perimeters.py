"""
Estimate missing mask perimeter_mm values by combining:
- size hints inside unique_internal_model_code
- style-level medians
- co-test relationships between masks with known perimeters
- simple fallbacks for styles with no references

Outputs a CSV with the chosen imputation per mask plus provenance.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from breathesafe_network import (
  build_session,
  fetch_json,
  fetch_facial_measurements_fit_tests,
  fetch_dashboard_stats,
  login_with_credentials,
  logout,
)

FEATURE_COLUMNS = [
  "nose_mm",
  "chin_mm",
  "top_cheek_mm",
  "mid_cheek_mm",
  "strap_mm",
]

SIZE_ORDER = [
  "xxxs",
  "xxs",
  "kids",
  "petite",
  "xs",
  "x-small",
  "small",
  "s",
  "medium",
  "m",
  "regular",
  "large",
  "l",
  "xl",
  "x-large",
  "xxl",
  "2xl",
  "xxxl",
  "3xl",
]

SIZE_CANONICAL = {
  "xxxs": "xxxs",
  "xxs": "xxs",
  "kids": "kids",
  "child": "kids",
  "children": "kids",
  "petite": "petite",
  "xs": "xs",
  "x-small": "xs",
  "small": "small",
  "s": "small",
  "medium": "medium",
  "m": "medium",
  "regular": "medium",
  "large": "large",
  "l": "large",
  "xl": "xl",
  "x-large": "xl",
  "xxl": "xxl",
  "2xl": "xxl",
  "xxxl": "xxxl",
  "3xl": "xxxl",
}

TOKEN_REGEX = re.compile("|".join(sorted(SIZE_CANONICAL.keys(), key=len, reverse=True)), re.IGNORECASE)

PASS_TRUE = {True, 1, "1", "true", "TRUE", "t", "T", "pass", "PASS", "passed", "PASSED"}
PASS_FALSE = {False, 0, "0", "false", "FALSE", "f", "F", "fail", "FAIL", "failed", "FAILED"}


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--base-url",
    default="http://localhost:3000",
    help="Base URL for the Breathesafe instance (default: %(default)s)",
  )
  parser.add_argument(
    "--predicted-fit-tests",
    type=Path,
    default=Path("python/mask_recommender/predicted_fit_tests.csv"),
    help="CSV produced by predict_arkit_from_traditional.py",
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
    "--cookie",
    default=None,
    help="Optional Cookie header value if you already have a session.",
  )
  parser.add_argument(
    "--output-file",
    type=Path,
    default=Path("python/mask_recommender/mask_perimeter_imputations.csv"),
    help="Where to write imputation results",
  )
  return parser.parse_args()


def fetch_masks(session, base_url: str) -> pd.DataFrame:
  url = f"{base_url.rstrip('/')}/masks.json?per_page=2000"
  data = fetch_json(session, url)
  masks = data.get("masks", [])
  if not masks:
    return pd.DataFrame()
  df = pd.DataFrame(masks)
  df["perimeter_mm"] = pd.to_numeric(df.get("perimeter_mm"), errors="coerce")
  return df


def normalize_name(text: str) -> str:
  return re.sub(r"\s+", " ", text.strip().lower())


def extract_base_and_size(name: str) -> tuple[str, str]:
  if not isinstance(name, str):
    return ("", "unknown")

  tokens: List[str] = []

  def replacement(match):
    tokens.append(match.group(0))
    return ""

  cleaned = TOKEN_REGEX.sub(replacement, name)
  size = "unknown"
  if tokens:
    canonical = SIZE_CANONICAL.get(tokens[0].lower())
    if canonical:
      size = canonical
  base = normalize_name(re.sub(r"[-_/]", " ", cleaned))
  base = base.strip()
  return (base or normalize_name(name), size)


def derive_pass_flag(value) -> Optional[int]:
  if value in PASS_TRUE:
    return 1
  if value in PASS_FALSE:
    return -1
  return None


def add_pass_flag(df: pd.DataFrame) -> pd.DataFrame:
  pass_columns = [col for col in df.columns if col.endswith("_pass")]
  if not pass_columns:
    raise RuntimeError("fit_tests response lacks *_pass columns")
  flags = []
  for _, row in df.iterrows():
    flag = None
    for col in pass_columns:
      flag = derive_pass_flag(row.get(col))
      if flag is not None:
        break
    flags.append(flag)
  df = df.copy()
  df["pass_flag"] = flags
  return df


def size_rank(size: str) -> int:
  if size in SIZE_ORDER:
    return SIZE_ORDER.index(size)
  return len(SIZE_ORDER)


def co_test_estimate(
  mask_id: int,
  passers: Dict[int, List[int]],
  user_known_mask_values: Dict[int, List[float]],
) -> Optional[float]:
  users = passers.get(mask_id)
  if not users:
    return None
  values: List[float] = []
  for user in users:
    vals = user_known_mask_values.get(user)
    if vals:
      values.extend(vals)
  if values:
    return float(np.mean(values))
  return None


def main() -> None:
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
  args = parse_args()
  session = build_session(args.cookie)
  logged_in = False
  if args.cookie:
    logging.info("Using provided cookie for authentication.")
  elif args.email and args.password:
    login_with_credentials(session, args.base_url, args.email, args.password)
    logged_in = True
  else:
    logging.warning("Proceeding without authentication; some endpoints may fail.")

  masks_df = fetch_masks(session, args.base_url)
  if masks_df.empty:
    raise RuntimeError("No masks returned from API.")

  fit_tests_payload = fetch_facial_measurements_fit_tests(
    base_url=args.base_url,
    session=session,
    include_without_facial_measurements=True,
  )
  fit_tests_df = add_pass_flag(pd.DataFrame(fit_tests_payload))

  predicted_df = pd.read_csv(args.predicted_fit_tests)
  predicted_df["face_perimeter"] = predicted_df[FEATURE_COLUMNS].sum(axis=1)
  user_face_perimeter = (
    predicted_df.groupby("user_id")["face_perimeter"].mean().to_dict()
  )

  masks_df[["base_name", "size_code"]] = masks_df["unique_internal_model_code"].apply(
    lambda name: pd.Series(extract_base_and_size(name))
  )

  known_mask_perimeters = masks_df.dropna(subset=["perimeter_mm"]).set_index("id")[
    "perimeter_mm"
  ].to_dict()

  style_medians = (
    masks_df.dropna(subset=["perimeter_mm"]).groupby("style")["perimeter_mm"].median()
  )
  global_median = masks_df["perimeter_mm"].median()

  base_groups: Dict[str, pd.DataFrame] = {}
  for base_name, group in masks_df.dropna(subset=["perimeter_mm"]).groupby("base_name"):
    base_groups[base_name] = group[["size_code", "perimeter_mm"]]

  passers_by_mask: Dict[int, List[int]] = {}
  mask_fit_test_counts: Dict[int, int] = {}
  user_known_mask_values: Dict[int, List[float]] = {}
  for _, row in fit_tests_df.iterrows():
    mask_id = row.get("mask_id")
    user_id = row.get("user_id")
    flag = row.get("pass_flag")
    if pd.isna(mask_id) or pd.isna(user_id) or flag != 1:
      continue
    mask_id = int(mask_id)
    user_id = int(user_id)
    mask_fit_test_counts[mask_id] = mask_fit_test_counts.get(mask_id, 0) + 1
    passers_by_mask.setdefault(mask_id, []).append(user_id)
    if mask_id in known_mask_perimeters:
      user_known_mask_values.setdefault(user_id, []).append(known_mask_perimeters[mask_id])

  records = []

  for _, mask in masks_df.iterrows():
    mask_id = int(mask["id"])
    existing = mask.get("perimeter_mm")
    if pd.notna(existing):
      records.append(
        {
          "mask_id": mask_id,
          "unique_internal_model_code": mask.get("unique_internal_model_code"),
          "style": mask.get("style"),
          "strap_type": mask.get("strap_type"),
          "base_name": mask.get("base_name", ""),
          "size_code": mask.get("size_code", "unknown"),
          "fit_tests": mask_fit_test_counts.get(mask_id, 0),
          "perimeter_mm": existing,
          "source": "existing",
          "details": "",
        }
      )
      continue

    base_name = mask.get("base_name", "")
    size_code = mask.get("size_code", "unknown")
    imputed_value = None
    source = None
    detail = ""

    base_group = base_groups.get(base_name)
    if base_group is not None and not base_group.empty:
      exact = base_group.loc[base_group["size_code"] == size_code, "perimeter_mm"]
      if not exact.empty:
        imputed_value = float(exact.iloc[0])
        source = "base_size_exact"
      else:
        base_group = base_group.assign(rank=base_group["size_code"].apply(size_rank))
        base_group = base_group.sort_values("rank")
        if size_code != "unknown":
          target_rank = size_rank(size_code)
          nearest = base_group.iloc[(base_group["rank"] - target_rank).abs().argsort()]
          if not nearest.empty:
            imputed_value = float(nearest.iloc[0]["perimeter_mm"])
            source = "base_size_nearest"
            detail = f"nearest_size={nearest.iloc[0]['size_code']}"

    if imputed_value is None:
      co_est = co_test_estimate(
        mask_id,
        passers_by_mask,
        user_known_mask_values,
      )
      if co_est is not None:
        imputed_value = co_est
        source = "co_test"

    if imputed_value is None:
      style = mask.get("style")
      if style in style_medians.index:
        imputed_value = float(style_medians.loc[style])
        source = "style_median"
      elif pd.notna(global_median):
        imputed_value = float(global_median)
        source = "global_median"

    if imputed_value is not None and pd.isna(imputed_value):
      imputed_value = None

    if imputed_value is None:
      source = "insufficient_data"
      detail = ""

    records.append(
      {
        "mask_id": mask_id,
        "unique_internal_model_code": mask.get("unique_internal_model_code"),
        "style": mask.get("style"),
        "strap_type": mask.get("strap_type"),
        "base_name": base_name,
        "size_code": size_code,
        "fit_tests": mask_fit_test_counts.get(mask_id, 0),
        "perimeter_mm": imputed_value,
        "source": source,
        "details": detail,
      }
    )

  recorded_ids = {record["mask_id"] for record in records}

  # Add masks that still have no perimeter data and weren't imputed
  missing_masks = masks_df[
    masks_df["perimeter_mm"].isna() & ~masks_df["id"].isin(recorded_ids)
  ]
  for _, mask in missing_masks.iterrows():
    mask_id = int(mask["id"])
    records.append(
      {
        "mask_id": mask_id,
        "unique_internal_model_code": mask.get("unique_internal_model_code"),
        "style": mask.get("style"),
        "strap_type": mask.get("strap_type"),
        "base_name": mask.get("base_name", ""),
        "size_code": mask.get("size_code", "unknown"),
        "fit_tests": mask_fit_test_counts.get(mask_id, 0),
        "perimeter_mm": None,
        "source": "insufficient_data",
        "details": "",
      }
    )

  output_df = pd.DataFrame(records)
  total_fit_tests = output_df["fit_tests"].sum()
  logging.info(
    "mask_perimeter_imputations: %d rows | fit_tests_sum=%d",
    len(output_df),
    total_fit_tests,
  )
  try:
    dashboard_stats = fetch_dashboard_stats(args.base_url, session=session)
    unique_fit_tests = dashboard_stats["fit_tests"]["total_unique"]
    logging.info("dashboard total_unique_fit_tests=%s", unique_fit_tests)
  except Exception as exc:
    logging.warning("Failed to fetch dashboard stats: %s", exc)
  args.output_file.parent.mkdir(parents=True, exist_ok=True)
  output_df.to_csv(args.output_file, index=False)
  logging.info("Wrote imputation table to %s", args.output_file)

  if logged_in:
    logout(session, args.base_url)


if __name__ == "__main__":
  main()
