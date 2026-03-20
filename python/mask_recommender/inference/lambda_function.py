import json
import logging
import os
import time
from typing import Dict, List, Tuple

import boto3
import pandas as pd
import torch
try:
    from feature_builder import FACIAL_FEATURE_COLUMNS, MASK_EMPIRICAL_FEATURE_COLUMNS, derive_brand_model
    from train import calc_preds, prep_data_in_torch_with_categories, _custom_lr_mask_categories
except ModuleNotFoundError:
    from mask_recommender.feature_builder import (  # type: ignore
        FACIAL_FEATURE_COLUMNS,
        MASK_EMPIRICAL_FEATURE_COLUMNS,
        derive_brand_model,
    )
    from mask_recommender.train import (  # type: ignore
        calc_preds,
        prep_data_in_torch_with_categories,
        _custom_lr_mask_categories,
    )

logger = logging.getLogger()
logger.setLevel(logging.INFO)
DEFAULT_MODEL_TYPE = "custom_lr"


def _normalize_model_type(model_type):
    normalized = str(model_type or DEFAULT_MODEL_TYPE).strip()
    if not normalized or normalized == DEFAULT_MODEL_TYPE:
        return DEFAULT_MODEL_TYPE
    logger.info("Coercing unsupported model_type=%s to %s", normalized, DEFAULT_MODEL_TYPE)
    return DEFAULT_MODEL_TYPE

class MaskRecommenderInference:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=self._s3_region())
        self.bucket = self._bucket_name()
        self.custom_params = None
        self.custom_metadata = None
        self.custom_mask_data = None
        self.custom_last_loaded_at = None
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
        self.load_custom_model(force=True)

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

    def _infer_linear_specs(self, state_dict: Dict) -> List[Tuple[int, int, int]]:
        specs = []
        for key, value in state_dict.items():
            if not key.endswith('.weight'):
                continue
            layer_token = key.split('.')[0]
            if not layer_token.isdigit() or value.ndim != 2:
                continue
            layer_idx = int(layer_token)
            out_features, in_features = int(value.shape[0]), int(value.shape[1])
            specs.append((layer_idx, in_features, out_features))
        specs.sort(key=lambda item: item[0])
        if len(specs) < 2:
            raise RuntimeError("Unexpected model format; unable to infer linear layers.")
        return specs

    def _maybe_refresh_custom(self) -> None:
        if self.custom_last_loaded_at is None:
            self.load_custom_model(force=True)
            return
        if (time.time() - self.custom_last_loaded_at) > self.refresh_seconds:
            self.load_custom_model(force=True)

    def load_custom_model(self, force: bool = False) -> None:
        if not force and self.custom_params is not None:
            return

        latest_key = 'mask_recommender/models/custom_latest.json'
        latest_path = '/tmp/mask_recommender_custom_latest.json'
        self._download_file(latest_key, latest_path)
        with open(latest_path, 'r') as f:
            latest_payload = json.load(f)

        params_key = latest_payload['params_key']
        metadata_key = latest_payload['metadata_key']
        mask_data_key = latest_payload['mask_data_key']

        params_path = '/tmp/mask_recommender_custom_params.pt'
        metadata_path = '/tmp/mask_recommender_custom_metadata.json'
        mask_data_path = '/tmp/mask_recommender_custom_mask_data.json'

        self._download_file(params_key, params_path)
        self._download_file(metadata_key, metadata_path)
        self._download_file(mask_data_key, mask_data_path)

        with open(metadata_path, 'r') as f:
            self.custom_metadata = json.load(f)

        with open(mask_data_path, 'r') as f:
            self.custom_mask_data = json.load(f)

        self.custom_params = torch.load(params_path, map_location='cpu')
        self.custom_last_loaded_at = time.time()
        logger.info(
            "Loaded custom model %s from s3://%s/%s",
            latest_payload.get('timestamp'),
            self.bucket,
            params_key
        )

    def _build_inference_rows(self, mask_data: Dict, facial_features: Dict) -> pd.DataFrame:
        rows = []
        for mask_id, mask_info in mask_data.items():
            perimeter = mask_info.get('perimeter_mm')
            if perimeter is None or (isinstance(perimeter, float) and pd.isna(perimeter)):
                perimeter = 0
            row = {
                'mask_id': int(mask_id),
                'fit_family_id': mask_info.get('fit_family_id'),
                'perimeter_mm': perimeter,
                'strap_type': mask_info.get('strap_type') or '',
                'style': mask_info.get('style') or '',
                'brand_model': mask_info.get('brand_model') or derive_brand_model(
                    mask_info.get('unique_internal_model_code'),
                    mask_info.get('current_state')
                ),
                'unique_internal_model_code': mask_info.get('unique_internal_model_code') or '',
                'facial_hair_beard_length_mm': facial_features.get('facial_hair_beard_length_mm', 0) or 0,
            }
            for col in FACIAL_FEATURE_COLUMNS:
                row[col] = facial_features.get(col, 0) or 0
            for col in MASK_EMPIRICAL_FEATURE_COLUMNS:
                row[col] = mask_info.get(col, 0) or 0
            rows.append(row)
        return pd.DataFrame(rows)


    def recommend_masks_custom(self, facial_features: Dict) -> List[Dict]:
        self._maybe_refresh_custom()
        if not self.custom_params or not self.custom_metadata or not self.custom_mask_data:
            logger.error('Custom model or mask data not loaded; returning empty recommendations.')
            return []

        inference_rows = self._build_inference_rows(self.custom_mask_data, facial_features)
        custom_data = prep_data_in_torch_with_categories(
            inference_rows,
            mask_categories=_custom_lr_mask_categories(self.custom_metadata),
            style_categories=self.custom_metadata['style_categories'],
            strap_categories=self.custom_metadata['strap_type_categories'],
        )
        with torch.no_grad():
            probs = calc_preds(custom_data, self.custom_params).squeeze(1).cpu().tolist()

        recommendations = []
        for idx, (mask_id, mask_info) in enumerate(self.custom_mask_data.items()):
            recommendations.append({
                'mask_id': int(mask_id),
                'proba_fit': float(probs[idx]),
                'mask_info': mask_info,
            })
        recommendations.sort(key=lambda x: x['proba_fit'], reverse=True)
        return recommendations


def handler(event, context):
    try:
        payload = event or {}
        method = payload.get("method")
        facial_features = payload.get('facial_measurements', {})
        model_type = _normalize_model_type(payload.get('model_type'))
        recommender = MaskRecommenderInference()
        if method == "warmup":
            recommender.load_custom_model(force=True)
            warmed_model = recommender.custom_metadata
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'warmed',
                    'model_type': model_type,
                    'model': warmed_model,
                })
            }
        recommendations = recommender.recommend_masks_custom(facial_features)
        model_payload = recommender.custom_metadata
        mask_id_map = {str(idx): rec['mask_id'] for idx, rec in enumerate(recommendations)}
        proba_map = {str(idx): rec['proba_fit'] for idx, rec in enumerate(recommendations)}
        return {
            'statusCode': 200,
            'body': json.dumps({
                'mask_id': mask_id_map,
                'proba_fit': proba_map,
                'model': model_payload,
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
