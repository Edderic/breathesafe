import os
import sys
import json
import pytest

# Ensure we can import lambda_function
HERE = os.path.abspath(os.path.dirname(__file__))
INF_DIR = os.path.abspath(os.path.join(HERE, '..'))
if INF_DIR not in sys.path:
    sys.path.append(INF_DIR)


@pytest.mark.skipif(sys.platform != 'linux', reason='PyMC/JAX stack only supported in CI on Linux')
def test_toddler_has_low_proba_for_3m_9205(monkeypatch):
    """For toddler-like measurements, 3M 9205+ (mask_id=18) should have low proba_fit."""
    # Configure test environment so inference reads from local tmp instead of S3
    monkeypatch.setenv('ENVIRONMENT', 'test')
    # Simulate bucket region but not used when ENVIRONMENT=test in our code
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')

    # Import after env set
    from lambda_function import MaskRecommenderInference

    # Build recommender and load local artifacts if code supports ENV=test
    recommender = MaskRecommenderInference()

    toddler = {
        'bitragion_subnasale_arc': 180,
        'face_width': 88,
        'face_length': 77,
        'nose_protrusion': 12,
        'facial_hair_beard_length_mm': 0,
    }

    proba = recommender.predict_fit_probability(toddler, mask_id=18)
    assert proba < 0.1
