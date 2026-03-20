#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

import boto3


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare production Lambda recommendations vs local recommender output."
    )
    parser.add_argument(
        "--function-name",
        default="mask-recommender-production",
        help="Production Lambda function name.",
    )
    parser.add_argument(
        "--local-url",
        default="http://127.0.0.1:5055/mask_recommender",
        help="Local recommender endpoint URL.",
    )
    parser.add_argument(
        "--payload-json",
        default=None,
        help='Facial measurements JSON string, e.g. \'{"nose_mm":44.2,...}\'',
    )
    parser.add_argument(
        "--payload-file",
        default=None,
        help="Path to JSON file containing facial measurements payload.",
    )
    parser.add_argument(
        "--recommender-payload",
        default=None,
        help="Base64/base64url recommenderPayload value from masks URL.",
    )
    parser.add_argument(
        "--masks-url",
        default=None,
        help="Full masks URL containing recommenderPayload query param.",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "us-east-1"),
        help="AWS region for Lambda invoke.",
    )
    parser.add_argument(
        "--profile",
        default=os.environ.get("AWS_PROFILE"),
        help="Optional AWS profile (e.g. breathesafe).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="How many top recommendations to print per side.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to write full comparison JSON report.",
    )
    return parser.parse_args()


def _decode_base64url(value: str) -> Dict[str, Any]:
    raw = value.strip()
    padding = "=" * ((4 - len(raw) % 4) % 4)
    decoded = base64.urlsafe_b64decode(raw + padding)
    return json.loads(decoded.decode("utf-8"))


def _extract_payload_from_url(url: str) -> Dict[str, Any]:
    compact_url = "".join((url or "").split())
    parsed = urllib.parse.urlparse(compact_url)
    params = urllib.parse.parse_qs(parsed.query)
    encoded = params.get("recommenderPayload", [None])[0]
    if encoded:
        return _decode_base64url(encoded)

    # Vue hash routes often keep query params in the fragment, e.g.:
    # https://host/#/masks?recommenderPayload=...
    fragment = parsed.fragment or ""
    fragment_query = ""
    if "?" in fragment:
        fragment_query = fragment.split("?", 1)[1]
    elif "=" in fragment:
        fragment_query = fragment
    if fragment_query:
        fragment_params = urllib.parse.parse_qs(fragment_query)
        encoded = fragment_params.get("recommenderPayload", [None])[0]
    if not encoded:
        raise ValueError("No recommenderPayload found in masks URL.")
    return _decode_base64url(encoded)


def _load_facial_measurements(args: argparse.Namespace) -> Dict[str, Any]:
    if args.payload_json:
        return json.loads(args.payload_json)
    if args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    if args.recommender_payload:
        return _decode_base64url(args.recommender_payload)
    if args.masks_url:
        return _extract_payload_from_url(args.masks_url)
    raise ValueError(
        "Provide one of --payload-json, --payload-file, --recommender-payload, or --masks-url."
    )


def _parse_lambda_body(response_obj: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(response_obj, dict) and "body" in response_obj:
        body = response_obj["body"]
        if isinstance(body, str):
            return json.loads(body)
        return body
    return response_obj


def _invoke_production(
    function_name: str, region: str, facial_measurements: Dict[str, Any], profile: str | None
) -> Dict[str, Any]:
    payload = {"method": "infer", "facial_measurements": facial_measurements}
    if profile:
        session = boto3.session.Session(profile_name=profile, region_name=region)
        client = session.client("lambda")
    else:
        client = boto3.client("lambda", region_name=region)
    response = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload).encode("utf-8"),
    )
    raw = response["Payload"].read().decode("utf-8")
    parsed = json.loads(raw) if raw else {}
    return _parse_lambda_body(parsed)


def _invoke_local(local_url: str, facial_measurements: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps(
        {"method": "infer", "facial_measurements": facial_measurements}
    ).encode("utf-8")
    req = urllib.request.Request(
        local_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as res:
        raw = res.read().decode("utf-8")
    parsed = json.loads(raw) if raw else {}
    return _parse_lambda_body(parsed)


def _to_ranked_rows(body: Dict[str, Any]) -> List[Dict[str, Any]]:
    mask_map = body.get("mask_id")
    proba_map = body.get("proba_fit")
    if not isinstance(mask_map, dict) or not isinstance(proba_map, dict):
        raise ValueError(f"Unexpected response shape: {body}")

    rows: List[Dict[str, Any]] = []
    for key, mask_id in mask_map.items():
        proba = proba_map.get(key)
        if proba is None:
            continue
        rows.append({"mask_id": int(mask_id), "proba_fit": float(proba)})

    rows.sort(key=lambda row: row["proba_fit"], reverse=True)
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    return rows


def _compare_rows(
    prod_rows: List[Dict[str, Any]], local_rows: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    prod_by_mask = {row["mask_id"]: row for row in prod_rows}
    local_by_mask = {row["mask_id"]: row for row in local_rows}
    all_mask_ids = sorted(set(prod_by_mask) | set(local_by_mask))
    diffs: List[Dict[str, Any]] = []
    for mask_id in all_mask_ids:
        p = prod_by_mask.get(mask_id)
        l = local_by_mask.get(mask_id)
        prod_prob = p["proba_fit"] if p else None
        local_prob = l["proba_fit"] if l else None
        prob_diff = None
        if prod_prob is not None and local_prob is not None:
            prob_diff = abs(prod_prob - local_prob)
        diffs.append(
            {
                "mask_id": mask_id,
                "prod_rank": p["rank"] if p else None,
                "prod_prob": prod_prob,
                "local_rank": l["rank"] if l else None,
                "local_prob": local_prob,
                "abs_prob_diff": prob_diff,
            }
        )
    diffs.sort(key=lambda row: (row["abs_prob_diff"] is None, -(row["abs_prob_diff"] or -1)))
    return diffs


def _print_top(title: str, rows: List[Dict[str, Any]], n: int) -> None:
    print(f"\n{title} (top {min(n, len(rows))})")
    print("-" * 60)
    for row in rows[:n]:
        print(f"rank={row['rank']:>3}  mask_id={row['mask_id']:>4}  proba={row['proba_fit']:.6f}")


def _print_diff(rows: List[Dict[str, Any]], n: int) -> None:
    print(f"\nLargest absolute probability deltas (top {min(n, len(rows))})")
    print("-" * 80)
    for row in rows[:n]:
        print(
            "mask_id={mask_id:>4}  prod(rank={pr}, p={pp})  local(rank={lr}, p={lp})  |delta|={d}".format(
                mask_id=row["mask_id"],
                pr=row["prod_rank"],
                pp=f"{row['prod_prob']:.6f}" if row["prod_prob"] is not None else "None",
                lr=row["local_rank"],
                lp=f"{row['local_prob']:.6f}" if row["local_prob"] is not None else "None",
                d=f"{row['abs_prob_diff']:.6f}" if row["abs_prob_diff"] is not None else "None",
            )
        )


def main() -> None:
    args = parse_args()
    facial_measurements = _load_facial_measurements(args)

    prod_body = _invoke_production(
        args.function_name, args.region, facial_measurements, args.profile
    )
    local_body = _invoke_local(args.local_url, facial_measurements)

    prod_rows = _to_ranked_rows(prod_body)
    local_rows = _to_ranked_rows(local_body)
    diffs = _compare_rows(prod_rows, local_rows)

    _print_top("Production", prod_rows, args.top_n)
    _print_top("Local", local_rows, args.top_n)
    _print_diff(diffs, args.top_n)

    if args.output_json:
        report = {
            "input_facial_measurements": facial_measurements,
            "production": prod_rows,
            "local": local_rows,
            "diffs": diffs,
        }
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        print(f"\nSaved report to {args.output_json}")


if __name__ == "__main__":
    main()
