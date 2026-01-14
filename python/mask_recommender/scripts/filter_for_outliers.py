import argparse
import logging
import os
import sys

import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
PYTHON_DIR = os.path.join(REPO_ROOT, "python", "mask_recommender")

if PYTHON_DIR not in sys.path:
    sys.path.append(PYTHON_DIR)

from predict_arkit_from_traditional import predict_arkit_from_traditional  # noqa: E402


FACIAL_COMPONENTS = [
    "nose_mm",
    "top_cheek_mm",
    "mid_cheek_mm",
    "chin_mm",
]


def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    normalized = str(value).strip().lower()
    if normalized in ["true", "1", "pass", "passed", "yes", "y"]:
        return True
    if normalized in ["false", "0", "fail", "failed", "no", "n"]:
        return False
    return None


def main():
    parser = argparse.ArgumentParser(description="Filter fit tests by perimeter diff outliers.")
    parser.add_argument("--abs-diff", type=float, required=True, help="Absolute diff threshold in mm.")
    parser.add_argument(
        "--output",
        default="python/mask_recommender/data/outlier_abs_diff.csv",
        help="Output CSV path.",
    )
    parser.add_argument("--base-url", default="http://localhost:3000", help="Base URL for API.")
    parser.add_argument(
        "--actual-only",
        action="store_true",
        help="Filter to rows where actual == true.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    email = os.getenv("BREATHESAFE_SERVICE_EMAIL")
    password = os.getenv("BREATHESAFE_SERVICE_PASSWORD")

    df = predict_arkit_from_traditional(
        base_url=args.base_url,
        email=email,
        password=password,
    )

    df = df[df["perimeter_mm"].notna()]
    if "mask_modded" in df.columns:
        df = df[~df["mask_modded"].apply(lambda v: normalize_bool(v) is True)]
    else:
        logging.warning("mask_modded column missing; skipping modded filtering.")

    df = df.dropna(subset=FACIAL_COMPONENTS)
    if args.actual_only and "actual" in df.columns:
        df = df[df["actual"] == True]
    elif args.actual_only:
        logging.warning("actual column missing; skipping actual-only filter.")

    df["facial_perimeter_mm"] = df[FACIAL_COMPONENTS].sum(axis=1, min_count=len(FACIAL_COMPONENTS))
    df = df[df["facial_perimeter_mm"].notna()]
    df["abs_diff"] = (df["facial_perimeter_mm"] - df["perimeter_mm"]).abs()

    outliers = df[df["abs_diff"] > args.abs_diff]

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    outliers.to_csv(args.output, index=False)
    logging.info("Saved %s rows to %s", outliers.shape[0], args.output)


if __name__ == "__main__":
    main()
