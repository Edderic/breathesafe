import json
import logging
from typing import Any, Dict

from .training_service import train
from .inference_service import infer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_DATA_URL = "https://www.breathesafe.xyz/facial_measurements_fit_tests.json"


def handler(event: Dict[str, Any], context: Any):
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
            epochs = int(body.get("epochs", 0))  # ignored by RF; retained for API parity
            data_url = body.get("data_url", DEFAULT_DATA_URL)
            target_col = body.get("target_col", "target")
            result = train(data_url=data_url, csv_path=None, target_col=target_col)
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
            return {"statusCode": 200, "body": json.dumps(out)}
        else:
            return {"statusCode": 400, "body": json.dumps({"error": f"Unknown method: {method}"})}
    except Exception as e:
        logger.exception("Lambda execution failed (RF)")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
