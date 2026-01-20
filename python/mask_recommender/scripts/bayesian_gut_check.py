import argparse
import json
import logging
import os
from datetime import datetime, timezone

import arviz as az
import boto3
import numpy as np
import pandas as pd

from bayesian import build_perimeter_bins, predict_from_trace
from data_prep import (BAYESIAN_FACE_COLUMNS, FACIAL_FEATURE_COLUMNS,
                       filter_fit_tests_for_bayesian, get_masks,
                       load_fit_tests_with_imputation)
from qa import build_mask_candidates, build_recommendation_preview


def parse_args():
    parser = argparse.ArgumentParser(description="Preview Bayesian recommendations.")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BREATHESAFE_BASE_URL", "http://localhost:3000"),
        help="Base URL for the Breathesafe API.",
    )
    parser.add_argument("--cookie", help="Session cookie for authentication.")
    parser.add_argument("--email", help="Email for authentication (optional).")
    parser.add_argument("--password", help="Password for authentication (optional).")
    parser.add_argument(
        "--output-key",
        default=None,
        help="Optional S3 key for the output JSON.",
    )
    return parser.parse_args()


def _env_name():
    env = os.environ.get('RAILS_ENV', '').strip().lower()
    if env in ('production', 'staging', 'development'):
        return env
    return 'development'


def _s3_bucket():
    mapping = {
        'production': 'breathesafe',
        'staging': 'breathesafe-staging',
        'development': 'breathesafe-development',
    }
    return mapping[_env_name()]


def _s3_region():
    return os.environ.get('S3_BUCKET_REGION') or os.environ.get('AWS_REGION') or 'us-east-1'


def _upload_file_to_s3(local_path, key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    profile = os.environ.get('AWS_PROFILE')
    logging.info(
        "S3 upload using bucket=%s region=%s profile=%s",
        bucket,
        _s3_region(),
        profile or "default"
    )
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"


def _download_latest_trace():
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    response = s3.list_objects_v2(Bucket=bucket, Prefix="mask_recommender/models/")
    candidates = [
        obj for obj in response.get("Contents", [])
        if obj["Key"].endswith("bayesian_trace.nc")
    ]
    if not candidates:
        raise RuntimeError("No bayesian_trace.nc found in S3.")
    latest = max(candidates, key=lambda obj: obj["LastModified"])
    local_path = f"/tmp/{os.path.basename(latest['Key'])}"
    s3.download_file(bucket, latest["Key"], local_path)
    return latest["Key"], local_path


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    trace_key, trace_path = _download_latest_trace()
    trace = az.from_netcdf(trace_path)

    fit_tests = load_fit_tests_with_imputation(
        base_url=args.base_url,
        email=args.email,
        password=args.password,
        cookie=args.cookie,
    )
    filtered_fit_tests = filter_fit_tests_for_bayesian(fit_tests)
    if filtered_fit_tests.empty:
        logging.warning("No fit tests available after filtering.")
        raise SystemExit(0)

    filtered_fit_tests["style_normalized"] = (
        filtered_fit_tests["style"].astype(str).str.strip().str.lower()
    )
    filtered_fit_tests["mask_code"] = (
        filtered_fit_tests["unique_internal_model_code"].astype(str).str.strip()
    )
    mask_index = sorted(filtered_fit_tests["mask_code"].unique())
    mask_map = {mask: idx for idx, mask in enumerate(mask_index)}

    base_url = args.base_url.rstrip("/")
    masks_url = f"{base_url}/masks.json?per_page=1000"
    masks_df = get_masks(session=None, masks_url=masks_url)
    mask_candidates = build_mask_candidates(masks_df)
    mask_candidates = mask_candidates[
        mask_candidates["unique_internal_model_code"].astype(str).isin(mask_map.keys())
    ].copy()

    bin_edges, _ = build_perimeter_bins()

    def predict_bayesian(inference_rows):
        face_perimeter = inference_rows[BAYESIAN_FACE_COLUMNS].sum(axis=1)
        perimeter_diff = face_perimeter - inference_rows["perimeter_mm"]
        bin_idx = pd.cut(
            perimeter_diff,
            bins=bin_edges,
            labels=False,
            right=False,
        ).astype(int)

        strap_normalized = inference_rows["strap_type"].astype(str).str.strip().str.lower()
        earloop = strap_normalized.str.contains("earloop").astype(int).to_numpy()
        headstrap = strap_normalized.str.contains("headstrap").astype(int).to_numpy()

        mask_idx = inference_rows["unique_internal_model_code"].astype(str).map(mask_map).to_numpy()
        beard = inference_rows["facial_hair_beard_length_mm"].fillna(0).to_numpy()

        return predict_from_trace(
            trace,
            mask_idx,
            bin_idx,
            beard,
            earloop,
            headstrap,
        )

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    local_output = f"/tmp/bayesian_recommendations_{run_timestamp}.json"
    preview = build_recommendation_preview(
        user_ids=[99, 101],
        fit_tests_df=fit_tests,
        mask_candidates=mask_candidates,
        predict_fn=predict_bayesian,
        output_path=local_output,
    )

    output_key = args.output_key
    if not output_key:
        output_key = f"mask_recommender/models/{run_timestamp}/bayesian_recommendations.json"

    output_uri = _upload_file_to_s3(local_output, output_key)
    logging.info("Saved Bayesian recommendations to %s (trace=%s)", output_uri, trace_key)


if __name__ == "__main__":
    main()
