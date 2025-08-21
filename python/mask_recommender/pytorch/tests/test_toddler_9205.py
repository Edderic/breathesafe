import json
import os
import sys

import pytest
import torch

# Ensure we can import lambda_function
HERE = os.path.abspath(os.path.dirname(__file__))
PKG_DIR = os.path.abspath(os.path.join(HERE, '..'))
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


def test_toddler_has_low_proba_for_3m_9205_end_to_end(monkeypatch):
    """End-to-end: train then infer; toddler-like measurements should have low proba for 3M 9205+ (mask_id=18)."""
    # Use default data_url; keep env pointing to staging-like defaults but monkeypatch S3 IO
    monkeypatch.setenv('ENVIRONMENT', 'staging')
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')

    import random

    import numpy as np

    # Fix random seeds for stability
    from python.mask_recommender.pytorch import lambda_function as lf
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    # Stub S3 uploads/downloads: capture model state and mask data in memory
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

    # Minimal mask catalog with required fields
    mask_data = {
        '18': {'mask_id': 18, 'style': 'Boat', 'strap_type': 'Headstrap', 'perimeter_mm': 400.0},
    }

    def fake_load_mask_data():
        return mask_data

    def fake_save_mask_data(md):
        saved['mask_data'] = md
        return {'mask_data_latest': 's3://fake/mask_data_latest.json', 'mask_data_versioned': 's3://fake/mask_data_YYYY.json'}

    # Patch both legacy wrappers and the new modules
    import python.mask_recommender.pytorch.s3_io as s3io
    monkeypatch.setattr(s3io, 'upload_checkpoint', fake_upload_checkpoint)
    monkeypatch.setattr(s3io, 'load_latest_model', fake_load_latest_model)
    monkeypatch.setattr(s3io, 'load_mask_data', fake_load_mask_data)
    monkeypatch.setattr(s3io, 'save_mask_data', fake_save_mask_data)

    # Train on pinned local dataset for determinism
    from python.mask_recommender.pytorch.training_service import train
    import os as _os
    pinned_csv = _os.path.join(HERE, 'fixtures', 'pinned_dataset.csv')
    train_result = train(csv_path=pinned_csv, data_url=None, epochs=60)
    assert 'metrics' in train_result and 'artifacts' in train_result

    # Infer on toddler-like features
    toddler = {
        'bitragion_subnasale_arc': 180,
        'face_width': 88,
        'face_length': 77,
        'nose_protrusion': 12,
        'facial_hair_beard_length_mm': 0,
    }
    # Use public infer
    from python.mask_recommender.pytorch.inference_service import infer
    out = infer(toddler, mask_ids=[18, 222])
    # Extract proba for 3M 9205+ (18)
    proba_by_index = {int(k): v for k, v in out['proba_fit'].items()}
    mask_by_index = {int(k): v for k, v in out['mask_id'].items()}
    # Find the index where mask_id==18
    idx_18 = next(i for i, mid in mask_by_index.items() if mid == 18)
    assert proba_by_index[idx_18] < 0.1


def test_adult_has_higher_proba_for_3m_9205_end_to_end(monkeypatch):
    """End-to-end: train then infer; adult-like measurements should have higher proba for 3M 9205+ (mask_id=18)."""
    # Use default data_url; keep env pointing to staging-like defaults but monkeypatch S3 IO
    monkeypatch.setenv('ENVIRONMENT', 'staging')
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')

    import random

    import numpy as np
    # Fix random seeds for stability

    from python.mask_recommender.pytorch import lambda_function as lf
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    # Stub S3 uploads/downloads: capture model state and mask data in memory
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

    # Minimal mask catalog with required fields
    mask_data = {
        '18': {'mask_id': 18, 'style': 'Boat', 'strap_type': 'Headstrap', 'perimeter_mm': 400.0},
    }

    def fake_load_mask_data():
        return mask_data

    def fake_save_mask_data(md):
        saved['mask_data'] = md
        return {'mask_data_latest': 's3://fake/mask_data_latest.json', 'mask_data_versioned': 's3://fake/mask_data_YYYY.json'}

    import python.mask_recommender.pytorch.s3_io as s3io
    monkeypatch.setattr(s3io, 'upload_checkpoint', fake_upload_checkpoint)
    monkeypatch.setattr(s3io, 'load_latest_model', fake_load_latest_model)
    monkeypatch.setattr(s3io, 'load_mask_data', fake_load_mask_data)
    monkeypatch.setattr(s3io, 'save_mask_data', fake_save_mask_data)

    # Train on pinned local dataset for determinism
    from python.mask_recommender.pytorch.training_service import train
    import os as _os
    pinned_csv = _os.path.join(HERE, 'fixtures', 'pinned_dataset.csv')
    train_result = train(csv_path=pinned_csv, data_url=None, epochs=60)
    assert 'metrics' in train_result and 'artifacts' in train_result

    # Infer on adult-like features
    adult = {
        'bitragion_subnasale_arc': 230,
        'face_width': 137,
        'face_length': 112,
        'nose_protrusion': 27,
        'facial_hair_beard_length_mm': 0,
    }
    from python.mask_recommender.pytorch.inference_service import infer
    out = infer(adult, mask_ids=[18])

    # Extract proba for 3M 9205+ (18)
    proba_by_index = {int(k): v for k, v in out['proba_fit'].items()}
    mask_by_index = {int(k): v for k, v in out['mask_id'].items()}
    # Find the index where mask_id==18
    idx_18 = next(i for i, mid in mask_by_index.items() if mid == 18)
    assert proba_by_index[idx_18] > 0.5
