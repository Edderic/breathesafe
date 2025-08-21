import json
import os
import io
import time
import logging
from typing import Any, Dict, List, Optional

# Limit thread counts early to reduce chance of BLAS/OpenMP segfaults
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import boto3
import pandas as pd
import numpy as np
import torch

# Public services
from .training_service import train
from .inference_service import infer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_DATA_URL = "https://www.breathesafe.xyz/facial_measurements_fit_tests.json"


def handler(event, context):
    try:
        body = event.get("body") if isinstance(event, dict) else None
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception:
                body = {}
        if not isinstance(body, dict):
            body = event if isinstance(event, dict) else {}

        method = (body.get("method") or "infer").strip().lower()
        if method == "train":
            epochs = int(body.get("epochs", 50))
            data_url = body.get("data_url", DEFAULT_DATA_URL)
            target_col = body.get("target_col", "target")
            result = train(data_url=data_url, csv_path=None, epochs=epochs, target_col=target_col)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Training completed successfully",
                    "artifacts": result["artifacts"],
                    "metrics": result["metrics"],
                })
            }
        elif method == "infer":
            facial = body.get("facial_measurements", {})
            mask_ids = body.get("mask_ids")
            out = infer(facial, mask_ids)
            return {
                "statusCode": 200,
                "body": json.dumps(out)
            }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown method: {method}"})
            }
    except Exception as e:
        logger.exception("Lambda execution failed")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
