import json
import logging
import os
import time
from typing import Dict, List

import boto3
import pandas as pd
import torch
try:
    from feature_builder import FACIAL_FEATURE_COLUMNS, build_feature_frame
except ModuleNotFoundError:
    from mask_recommender.feature_builder import (  # type: ignore
        FACIAL_FEATURE_COLUMNS,
        build_feature_frame,
    )

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class MaskRecommenderInference:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=self._s3_region())
        self.bucket = self._bucket_name()
        self.model = None
        self.mask_data = None
        self.feature_columns = None
        self.categorical_columns = None
        self.threshold = 0.5
        self.model_input_dim = None
        self.use_facial_perimeter = False
        self.use_diff_perimeter_bins = False
        self.use_diff_perimeter_mask_bins = False
        self.last_loaded_at = None
        self.latest_payload = None
        self.refresh_seconds = int(os.environ.get('MODEL_REFRESH_SECONDS', '300'))
        logger.info(
            "Lambda init: function=%s version=%s image_tag=%s",
            os.environ.get("AWS_LAMBDA_FUNCTION_NAME"),
            os.environ.get("AWS_LAMBDA_FUNCTION_VERSION"),
            os.environ.get("IMAGE_TAG"),
        )
        logger.info(
            "Lambda init: image_digest=%s",
            os.environ.get("IMAGE_DIGEST"),
        )
        self.load_model(force=True)

    def _env_name(self) -> str:
        env = os.environ.get('RAILS_ENV') or os.environ.get('ENVIRONMENT')
        env = (env or 'development').strip().lower()
        if env in ('production', 'staging', 'development'):
            return env
        return 'development'

    def _bucket_name(self) -> str:
        mapping = {
            'production': 'breathesafe',
            'staging': 'breathesafe-staging',
            'development': 'breathesafe-development',
        }
        return mapping[self._env_name()]

    def _s3_region(self) -> str:
        return os.environ.get('S3_BUCKET_REGION') or os.environ.get('AWS_REGION') or 'us-east-1'

    def _download_file(self, key: str, local_path: str) -> None:
        self.s3_client.download_file(self.bucket, key, local_path)

    def _infer_hidden_sizes(self, state_dict: Dict) -> List[int]:
        weight_keys = [
            key for key in state_dict.keys()
            if key.endswith('.weight') and key.split('.')[0].isdigit()
        ]
        weight_keys.sort(key=lambda key: int(key.split('.')[0]))
        if len(weight_keys) < 3:
            raise RuntimeError("Unexpected model format; unable to infer hidden sizes.")
        sizes = [int(state_dict[key].shape[0]) for key in weight_keys[:-1]]
        return sizes

    def _maybe_refresh(self) -> None:
        if self.last_loaded_at is None:
            self.load_model(force=True)
            return
        if (time.time() - self.last_loaded_at) > self.refresh_seconds:
            self.load_model(force=True)

    def load_model(self, force: bool = False) -> None:
        if not force and self.model is not None:
            return

        latest_key = 'mask_recommender/models/latest.json'
        latest_path = '/tmp/mask_recommender_latest.json'
        self._download_file(latest_key, latest_path)
        with open(latest_path, 'r') as f:
            latest_payload = json.load(f)

        model_key = latest_payload['model_key']
        metadata_key = latest_payload['metadata_key']
        mask_data_key = latest_payload['mask_data_key']

        model_path = '/tmp/mask_recommender_model.pt'
        metadata_path = '/tmp/mask_recommender_metadata.json'
        mask_data_path = '/tmp/mask_recommender_mask_data.json'

        self._download_file(model_key, model_path)
        self._download_file(metadata_key, metadata_path)
        self._download_file(mask_data_key, mask_data_path)

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        with open(mask_data_path, 'r') as f:
            self.mask_data = json.load(f)

        self.feature_columns = metadata['feature_columns']
        self.categorical_columns = metadata['categorical_columns']
        self.threshold = metadata.get('threshold', 0.5)
        self.use_facial_perimeter = metadata.get('use_facial_perimeter', False)
        self.use_diff_perimeter_bins = metadata.get('use_diff_perimeter_bins', False)
        self.use_diff_perimeter_mask_bins = metadata.get('use_diff_perimeter_mask_bins', False)

        state_dict = torch.load(model_path, map_location='cpu')
        hidden_sizes = self._infer_hidden_sizes(state_dict)
        input_dim = len(self.feature_columns)
        expected_input_dim = int(state_dict["0.weight"].shape[1])
        if expected_input_dim != input_dim:
            logger.warning(
                "Feature column count (%s) does not match model input dim (%s).",
                input_dim,
                expected_input_dim,
            )
            input_dim = expected_input_dim
        self.model_input_dim = input_dim
        model = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_sizes[0]),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_sizes[0], hidden_sizes[1]),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_sizes[1], 1)
        )
        model.load_state_dict(state_dict)
        model.eval()

        self.model = model
        self.last_loaded_at = time.time()
        self.latest_payload = latest_payload

        logger.info(
            "Loaded model %s from s3://%s/%s",
            latest_payload.get('timestamp'),
            self.bucket,
            model_key
        )

    def _build_inference_rows(self, facial_features: Dict) -> pd.DataFrame:
        rows = []
        for mask_id, mask_info in self.mask_data.items():
            perimeter = mask_info.get('perimeter_mm')
            if perimeter is None or (isinstance(perimeter, float) and pd.isna(perimeter)):
                perimeter = 0
            row = {
                'mask_id': int(mask_id),
                'perimeter_mm': perimeter,
                'strap_type': mask_info.get('strap_type') or '',
                'style': mask_info.get('style') or '',
                'unique_internal_model_code': mask_info.get('unique_internal_model_code') or '',
                'facial_hair_beard_length_mm': facial_features.get('facial_hair_beard_length_mm', 0) or 0,
            }
            for col in FACIAL_FEATURE_COLUMNS:
                row[col] = facial_features.get(col, 0) or 0
            rows.append(row)
        return pd.DataFrame(rows)

    def recommend_masks(self, facial_features: Dict) -> List[Dict]:
        self._maybe_refresh()

        if not self.model or not self.mask_data:
            logger.error('Model or mask data not loaded; returning empty recommendations.')
            return []

        inference_rows = self._build_inference_rows(facial_features)
        numeric_columns = FACIAL_FEATURE_COLUMNS + ["perimeter_mm"]
        numeric_frame = pd.DataFrame(
            {
                col: pd.to_numeric(inference_rows.get(col), errors="coerce")
                for col in numeric_columns
            }
        )
        non_finite_mask = ~numeric_frame.replace(
            [float("inf"), float("-inf")],
            float("nan")
        ).notna()
        if non_finite_mask.any().any():
            bad_cols = non_finite_mask.any().loc[lambda s: s].index.tolist()
            logger.warning("Non-finite values detected in columns: %s", ", ".join(bad_cols))

        encoded = build_feature_frame(
            inference_rows,
            feature_columns=self.feature_columns,
            categorical_columns=self.categorical_columns,
            use_facial_perimeter=self.use_facial_perimeter,
            use_diff_perimeter_bins=self.use_diff_perimeter_bins,
            use_diff_perimeter_mask_bins=self.use_diff_perimeter_mask_bins
        )
        inputs = torch.tensor(encoded.to_numpy(), dtype=torch.float32)
        with torch.no_grad():
            logits = self.model(inputs).squeeze(1)
            probs = torch.sigmoid(logits).cpu().tolist()

        recommendations = []
        for idx, (mask_id, mask_info) in enumerate(self.mask_data.items()):
            recommendations.append({
                'mask_id': int(mask_id),
                'proba_fit': float(probs[idx]),
                'mask_info': mask_info,
            })

        recommendations.sort(key=lambda x: x['proba_fit'], reverse=True)
        return recommendations


def handler(event, context):
    try:
        facial_features = event.get('facial_measurements', {})
        recommender = MaskRecommenderInference()
        recommendations = recommender.recommend_masks(facial_features)
        mask_id_map = {str(idx): rec['mask_id'] for idx, rec in enumerate(recommendations)}
        proba_map = {str(idx): rec['proba_fit'] for idx, rec in enumerate(recommendations)}
        return {
            'statusCode': 200,
            'body': json.dumps({
                'mask_id': mask_id_map,
                'proba_fit': proba_map,
                'model': recommender.latest_payload,
            })
        }
    except Exception as exc:
        logger.exception('Error in lambda handler: %s', exc)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(exc)
            })
        }
