import pytest
import os
import sys
import math
import random

import numpy as np
import torch

HERE = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

from python.mask_recommender.pytorch.training_service import train as train_impl
from python.mask_recommender.pytorch.inference_service import infer as infer_impl
import python.mask_recommender.pytorch.s3_io as s3io


def _mock_s3(monkeypatch):
    saved = {}

    def fake_upload_checkpoint(state, metrics):
        saved['state'] = state
        saved['metrics'] = metrics
        return {
            'model_latest': 's3://fake/fit_classifier_latest.pt',
            'model_versioned': 's3://fake/fit_classifier_YYYY.pt',
            'metrics_latest': 's3://fake/metrics_latest.json',
            'metrics_versioned': 's3://fake/metrics_YYYY.json',
        }

    def fake_load_latest_model():
        return saved['state']

    # Minimal mask catalog with required fields for 9205+
    mask_data = {
        '18': {'mask_id': 18, 'style': 'Boat', 'strap_type': 'Headstrap', 'perimeter_mm': 400.0},
    }

    def fake_load_mask_data():
        return mask_data

    def fake_save_mask_data(md):
        saved['mask_data'] = md
        return {'mask_data_latest': 's3://fake/mask_data_latest.json', 'mask_data_versioned': 's3://fake/mask_data_YYYY.json'}

    monkeypatch.setattr(s3io, 'upload_checkpoint', fake_upload_checkpoint)
    monkeypatch.setattr(s3io, 'load_latest_model', fake_load_latest_model)
    monkeypatch.setattr(s3io, 'load_mask_data', fake_load_mask_data)
    monkeypatch.setattr(s3io, 'save_mask_data', fake_save_mask_data)

    return saved


def _set_seeds():
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)


def test_integration_toddler_low_proba_9205_real_data(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'staging')
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')
    _set_seeds()
    saved = _mock_s3(monkeypatch)

    # Train on real data
    from python.mask_recommender.pytorch import lambda_function as lf
    result = train_impl(data_url=lf.DEFAULT_DATA_URL, epochs=25)
    assert 'metrics' in result and 'artifacts' in result

    toddler = {
        'bitragion_subnasale_arc': 180,
        'face_width': 88,
        'face_length': 77,
        'nose_protrusion': 12,
        'facial_hair_beard_length_mm': 0,
    }
    out = infer_impl(toddler, mask_ids=[18, 222])
    proba_by_index = {int(k): v for k, v in out['proba_fit'].items()}
    mask_by_index = {int(k): v for k, v in out['mask_id'].items()}
    idx_18 = next(i for i, mid in mask_by_index.items() if mid == 18)
    assert proba_by_index[idx_18] < 0.2


@pytest.mark.f
def test_integration_adult_high_proba_9205_real_data(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'staging')
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')
    _set_seeds()
    saved = _mock_s3(monkeypatch)

    # Try a stronger model on real data
    from python.mask_recommender.pytorch import lambda_function as lf
    result = train_impl(data_url=lf.DEFAULT_DATA_URL, epochs=40, hidden=256, depth=4, dropout=0.1, lr=1e-3, val_split=0.1)

    assert 'metrics' in result and 'artifacts' in result

    adult = {
        'bitragion_subnasale_arc': 230,
        'face_width': 137,
        'face_length': 112,
        'nose_protrusion': 27,
        'facial_hair_beard_length_mm': 0,
    }
    out = infer_impl(adult, mask_ids=[18])
    proba_by_index = {int(k): v for k, v in out['proba_fit'].items()}
    mask_by_index = {int(k): v for k, v in out['mask_id'].items()}
    idx_18 = next(i for i, mid in mask_by_index.items() if mid == 18)
    assert proba_by_index[idx_18] > 0.5
