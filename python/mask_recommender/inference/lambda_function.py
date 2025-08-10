import numpy as np
import arviz as az
import boto3
import json
import os
import logging
from typing import Dict, List
import traceback

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MaskRecommenderInference:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        # Map environment -> bucket
        env = os.environ.get('ENVIRONMENT', 'staging').strip().lower()
        if env not in ('staging', 'production', 'development'):
            env = 'staging'
        default_bucket = {
            'production': 'breathesafe-production',
            'staging': 'breathesafe-staging',
            'development': 'breathesafe-development',
        }[env]
        self.bucket = os.environ.get('S3_BUCKET', default_bucket)
        self.trace = None
        self.mask_data = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Load the latest PyMC trace and mask data from S3"""
        try:
            # Download latest trace written by training for this environment
            logger.info("Loading model from " +
                        f"s3://{self.bucket}/mask-recommender-training-{os.environ.get('ENVIRONMENT', 'staging').lower()}/models/pymc_trace_latest.nc")
            self.s3_client.download_file(
                self.bucket,
                f"mask-recommender-training-{os.environ.get('ENVIRONMENT', 'staging').lower()}/models/pymc_trace_latest.nc",
                '/tmp/pymc_trace.nc'
            )
            self.trace = az.from_netcdf('/tmp/pymc_trace.nc')

            # Load mask data
            logger.info(
                "Loading mask data from " +
                f"s3://{self.bucket}/mask-recommender-training-{os.environ.get('ENVIRONMENT', 'staging').lower()}/models/mask_data_latest.json"
            )
            self.s3_client.download_file(
                self.bucket,
                f"mask-recommender-training-{os.environ.get('ENVIRONMENT', 'staging').lower()}/models/mask_data_latest.json",
                '/tmp/mask_data.json'
            )
            with open('/tmp/mask_data.json', 'r') as f:
                self.mask_data = json.load(f)

            # Load scaler (if available)
            try:
                self.s3_client.download_file(
                    self.bucket,
                    f"mask-recommender-training-{os.environ.get('ENVIRONMENT', 'staging').lower()}/models/scaler_latest.json",
                    '/tmp/scaler.json'
                )
                with open('/tmp/scaler.json', 'r') as f:
                    scaler_data = json.load(f)
                self.scaler = scaler_data
            except:
                logger.warning("No scaler found, using raw features")
                self.scaler = None

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def scale_features(self, facial_features: Dict) -> np.ndarray:
        """Scale facial features using the same scaler from training"""
        features = np.array([
            facial_features['face_width'],
            facial_features['face_length'],
            facial_features['bitragion_subnasale_arc'],
            facial_features['nose_protrusion']
        ]).reshape(1, -1)

        if self.scaler:
            # Apply the same scaling as in training
            mean = np.array(self.scaler['mean'])
            scale = np.array(self.scaler['scale'])
            features = (features - mean) / scale

        return features.flatten()

    def predict_fit_probability(
        self, facial_features: Dict, mask_id: int
    ) -> float:
        """Predict fit probability for a specific mask"""
        try:
            # Extract posterior means
            posterior = self.trace.posterior
            global_multipliers = posterior['global_multipliers'].mean(
                dim=('chain', 'draw')).values
            style_adjustments = posterior['style_multiplier_adjustments'].mean(
                dim=('chain', 'draw')).values
            a_mask = posterior['a_mask'].mean(dim=('chain', 'draw')).values
            c_mask = posterior['c_mask'].mean(dim=('chain', 'draw')).values
            strap_type_effect = posterior['strap_type_effect'].mean(
                dim=('chain', 'draw')).values
            facial_hair_multiplier = posterior['facial_hair_multiplier'].mean(
                dim=('chain', 'draw')).values

            # Get mask info
            mask_info = self.mask_data[str(mask_id)]
            style_encoded = mask_info['style_encoded']
            strap_type_encoded = mask_info['strap_type_encoded']
            perimeter_mm = mask_info['perimeter_mm']

            # Scale facial features
            facial_X = self.scale_features(facial_features)

            # Compute prediction (same logic as training)
            style_adjustment = style_adjustments[style_encoded]
            final_multipliers = global_multipliers + style_adjustment

            facial_sum = np.sum(facial_X * final_multipliers)
            distance = (facial_sum - perimeter_mm) ** 2

            a = a_mask[mask_id]
            c = c_mask[mask_id]
            strap_effect = strap_type_effect[strap_type_encoded]
            facial_hair = facial_features.get('facial_hair_beard_length_mm', 0)

            logit_p = a * distance + c + strap_effect \
                + facial_hair * facial_hair_multiplier
            logit_p = np.clip(logit_p, -20, 20)
            prob = 1 / (1 + np.exp(-logit_p))

            return float(prob)

        except Exception as e:
            logger.error(f"Error predicting for mask {mask_id}: {e}")
            return 0.0

    def recommend_masks(self, facial_features: Dict) -> List[Dict]:
        """Return sorted list of masks with fit probabilities"""
        recommendations = []

        for mask_id, mask_info in self.mask_data.items():
            prob = self.predict_fit_probability(facial_features, int(mask_id))
            recommendations.append({
                'mask_id': int(mask_id),
                'proba_fit': prob,
                'mask_info': mask_info
            })

        # Sort by probability (highest first)
        recommendations.sort(key=lambda x: x['proba_fit'], reverse=True)
        return recommendations


def handler(event, context):
    """AWS Lambda handler"""
    try:
        facial_features = event.get('facial_measurements', {})

        # Initialize inference engine
        recommender = MaskRecommenderInference()

        # Get recommendations
        recommendations = recommender.recommend_masks(facial_features)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'mask_id': {
                    str(i): rec['mask_id']
                    for i, rec in enumerate(recommendations)
                },
                'proba_fit': {
                    str(i): rec['proba_fit']
                    for i, rec in enumerate(recommendations)
                }
            })
        }

    except Exception as e:
        logger.error(f"Error in handler: {e}")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
