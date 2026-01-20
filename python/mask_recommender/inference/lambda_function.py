import json
import logging
import os
import time
from typing import Dict, List

import boto3
import arviz as az
import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FACIAL_FEATURE_COLUMNS = [
    'nose_mm',
    'chin_mm',
    'top_cheek_mm',
    'mid_cheek_mm',
]


def _sigmoid(values):
    return 1 / (1 + np.exp(-values))


def _compute_face_perimeter(facial_features: Dict) -> float:
    return sum(float(facial_features.get(col, 0) or 0) for col in FACIAL_FEATURE_COLUMNS)


class MaskRecommenderInference:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=self._s3_region())
        self.bucket = self._bucket_name()
        self.trace = None
        self.mask_data = None
        self.mask_index = None
        self.bin_edges = None
        self.last_loaded_at = None
        self.latest_payload = None
        self.refresh_seconds = int(os.environ.get('MODEL_REFRESH_SECONDS', '300'))
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

    def _maybe_refresh(self) -> None:
        if self.last_loaded_at is None:
            self.load_model(force=True)
            return
        if (time.time() - self.last_loaded_at) > self.refresh_seconds:
            self.load_model(force=True)

    def load_model(self, force: bool = False) -> None:
        if not force and self.trace is not None:
            return

        latest_key = 'mask_recommender/models/bayesian_latest.json'
        latest_path = '/tmp/mask_recommender_bayesian_latest.json'
        self._download_file(latest_key, latest_path)
        with open(latest_path, 'r') as f:
            latest_payload = json.load(f)

        trace_key = latest_payload['trace_key']
        metadata_key = latest_payload['metadata_key']
        mask_data_key = latest_payload['mask_data_key']

        trace_path = '/tmp/mask_recommender_bayesian_trace.nc'
        metadata_path = '/tmp/mask_recommender_bayesian_metadata.json'
        mask_data_path = '/tmp/mask_recommender_bayesian_mask_data.json'

        self._download_file(trace_key, trace_path)
        self._download_file(metadata_key, metadata_path)
        self._download_file(mask_data_key, mask_data_path)

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        with open(mask_data_path, 'r') as f:
            self.mask_data = json.load(f)

        self.mask_index = metadata['mask_index']
        self.bin_edges = metadata['bin_edges']
        self.trace = az.from_netcdf(trace_path)
        self.last_loaded_at = time.time()
        self.latest_payload = latest_payload

        logger.info(
            "Loaded model %s from s3://%s/%s",
            latest_payload.get('timestamp'),
            self.bucket,
            trace_key
        )

    def recommend_masks(self, facial_features: Dict) -> List[Dict]:
        self._maybe_refresh()

        if not self.trace or not self.mask_data:
            logger.error('Model or mask data not loaded; returning empty recommendations.')
            return []

        mask_map = {code: idx for idx, code in enumerate(self.mask_index)}
        face_perimeter = _compute_face_perimeter(facial_features)
        beard = float(facial_features.get('facial_hair_beard_length_mm', 0) or 0)
        bin_edges = np.array(self.bin_edges, dtype=float)

        p_mask_mean = self.trace.posterior["p_mask"].mean(dim=("chain", "draw")).values
        beta_facial_hair = float(self.trace.posterior["beta_facial_hair"].mean().values)
        beta_earloop = float(self.trace.posterior["beta_earloop"].mean().values)
        beta_headstrap = float(self.trace.posterior["beta_headstrap"].mean().values)
        alpha = float(self.trace.posterior["alpha"].mean().values)

        recommendations = []
        for mask_id, mask_info in self.mask_data.items():
            mask_code = mask_info.get('unique_internal_model_code') or ''
            mask_idx = mask_map.get(str(mask_code))
            if mask_idx is None:
                continue

            perimeter = mask_info.get('perimeter_mm')
            if perimeter is None:
                continue
            try:
                perimeter = float(perimeter)
            except (TypeError, ValueError):
                continue

            diff = face_perimeter - perimeter
            bin_idx = int(np.digitize(diff, bin_edges[1:-1], right=False))
            strap_type = (mask_info.get('strap_type') or '').lower()
            earloop = 1 if 'earloop' in strap_type else 0
            headstrap = 1 if 'headstrap' in strap_type else 0

            p_facial = _sigmoid(
                beta_facial_hair * beard
                + beta_earloop * earloop
                + beta_headstrap * headstrap
                + alpha
            )
            prob = float(p_mask_mean[mask_idx, bin_idx] * p_facial)
            recommendations.append({
                'mask_id': int(mask_id),
                'proba_fit': prob,
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
