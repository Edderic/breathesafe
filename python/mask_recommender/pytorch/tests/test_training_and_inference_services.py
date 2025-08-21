import os
import sys
import types

import numpy as np
import pandas as pd
import torch

HERE = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

from python.mask_recommender.pytorch.training_service import train as train_impl
from python.mask_recommender.pytorch.inference_service import infer as infer_impl
from python.mask_recommender.pytorch.model import FitClassifier, MLPConfig


def test_training_service_train_smoke(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'staging')
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')

    # Provide a tiny dataframe via try_load_remote_json
    df = pd.DataFrame({
        'qlft_pass': [True, False, True, False],
        'face_width': [120, 130, 110, 100],
        'face_length': [110, 120, 105, 95],
        'nose_protrusion': [20, 25, 18, 15],
        'bitragion_subnasale_arc': [220, 230, 210, 200],
        'facial_hair_beard_length_mm': [0, 0, 0, 0],
        'mask_id': [18, 22, 18, 22],
        'style': ['Boat', 'Cup', 'Boat', 'Cup'],
        'strap_type': ['Headstrap', 'Earloops', 'Headstrap', 'Earloops'],
        'perimeter_mm': [400.0, 410.0, 400.0, 410.0],
    })

    import python.mask_recommender.pytorch.training_service as ts

    monkeypatch.setattr(ts, 'try_load_remote_json', lambda url: df)

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

    def fake_save_mask_data(md):
        saved['mask_data'] = md
        return {'mask_data_latest': 's3://fake/mask_data_latest.json', 'mask_data_versioned': 's3://fake/mask_data_YYYY.json'}

    # Patch both module-level references and the s3_io module used within training_service
    monkeypatch.setattr(ts, 'upload_checkpoint', fake_upload_checkpoint, raising=False)
    monkeypatch.setattr(ts, 'save_mask_data', fake_save_mask_data, raising=False)
    import python.mask_recommender.pytorch.s3_io as s3io
    monkeypatch.setattr(s3io, 'upload_checkpoint', fake_upload_checkpoint)
    monkeypatch.setattr(s3io, 'save_mask_data', fake_save_mask_data)

    result = train_impl(data_url='http://example', epochs=1)

    assert 'metrics' in result and 'artifacts' in result
    assert 'model_latest' in result['artifacts']
    assert 'mask_data' in result
    assert isinstance(result['mask_data'], dict)


def test_inference_service_infer_smoke(monkeypatch):
    # Build a minimal model state
    feature_names = [
        'face_width', 'face_length', 'nose_protrusion', 'bitragion_subnasale_arc', 'facial_hair_beard_length_mm',
        'perimeter_mm', 'adjustable_headstrap', 'adjustable_earloops',
        'mask_id_18', 'style_Boat', 'strap_type_Headstrap',
    ]
    config = {'input_dim': len(feature_names), 'hidden_dim': 8, 'depth': 0, 'dropout': 0.0, 'num_classes': 2}
    model = FitClassifier(MLPConfig(**config))
    state = {
        'model_state': model.state_dict(),
        'feature_names': feature_names,
        'config': config,
        'stats': None,
    }

    import python.mask_recommender.pytorch.s3_io as s3io

    monkeypatch.setattr(s3io, 'load_latest_model', lambda: state)
    monkeypatch.setattr(s3io, 'load_mask_data', lambda: {'18': {'mask_id': 18, 'style': 'Boat', 'strap_type': 'Headstrap', 'perimeter_mm': 400.0}})

    facial = {
        'face_width': 120,
        'face_length': 110,
        'nose_protrusion': 20,
        'bitragion_subnasale_arc': 220,
        'facial_hair_beard_length_mm': 0,
    }

    out = infer_impl(facial, mask_ids=[18])
    assert 'mask_id' in out and 'proba_fit' in out
    # Should include one entry for mask 18
    assert 18 in out['mask_id'].values()
