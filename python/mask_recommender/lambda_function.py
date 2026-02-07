import json
import logging

from inference.lambda_function import handler as infer_handler
from training.lambda_function import handler as train_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _normalize_event(event):
    if event is None:
        return {}
    if isinstance(event, str):
        try:
            return json.loads(event)
        except json.JSONDecodeError:
            return {}
    if isinstance(event, dict) and "body" in event:
        body = event.get("body")
        if isinstance(body, str):
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return event
        if isinstance(body, dict):
            return body
    return event if isinstance(event, dict) else {}

def handler(event, context):
    payload = _normalize_event(event)
    method = payload.get("method") or (event or {}).get("method", "infer")
    logger.info("Combined lambda dispatch: method=%s", method)
    if method == "train":
        return train_handler(payload, context)
    if method == "warmup":
        return infer_handler({"method": "warmup", "model_type": payload.get("model_type")}, context)
    return infer_handler(payload, context)
