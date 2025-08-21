import io
import os
import sys

import boto3
import pytest

HERE = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

import python.mask_recommender.pytorch.s3_io as s3io


def test_get_s3_bucket_and_prefix_envs(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    bucket, prefix = s3io.get_s3_bucket_and_prefix()
    assert bucket == 'breathesafe-production'
    assert prefix.endswith('/models') and 'production' in prefix

    monkeypatch.setenv('ENVIRONMENT', 'development')
    bucket, prefix = s3io.get_s3_bucket_and_prefix()
    assert bucket == 'breathesafe-development'
    assert 'development' in prefix

    monkeypatch.setenv('ENVIRONMENT', 'staging')
    bucket, prefix = s3io.get_s3_bucket_and_prefix()
    assert bucket == 'breathesafe-staging'
    assert 'staging' in prefix


def test_save_and_load_helpers_monkeypatched(monkeypatch):
    # monkeypatch the boto3 client and in-memory object store
    store = {}

    class FakeS3:
        def put_object(self, Bucket, Key, Body):
            store[(Bucket, Key)] = Body

        def download_fileobj(self, Bucket, Key, Fileobj):
            if (Bucket, Key) not in store:
                raise RuntimeError('no such key')
            data = store[(Bucket, Key)]
            if isinstance(data, (bytes, bytearray)):
                Fileobj.write(data)
            else:
                # assume file-like
                Fileobj.write(data.getvalue())

    monkeypatch.setenv('ENVIRONMENT', 'staging')
    monkeypatch.setenv('S3_BUCKET_REGION', 'us-east-2')
    monkeypatch.setattr(s3io, 's3_client', lambda: FakeS3())

    # Test save_bytes_to_s3
    out_uri = s3io.save_bytes_to_s3(b'abc', 'foo.bin')
    assert out_uri.startswith('s3://') and out_uri.endswith('/foo.bin')

    # Test upload_checkpoint produces expected keys
    artifacts = s3io.upload_checkpoint({'x': 1}, {'m': 2})
    assert 'model_latest' in artifacts and 'metrics_latest' in artifacts

    # Test mask data helpers
    paths = s3io.save_mask_data({'18': {'mask_id': 18}})
    assert 'mask_data_latest' in paths

    # And load helpers read back the content
    # Put model file into the store to test load_latest_model
    bucket, prefix = s3io.get_s3_bucket_and_prefix()
    key = f"{prefix}/fit_classifier_latest.pt"
    fake_content = io.BytesIO()
    import torch
    torch.save({'feature_names': [], 'config': {'input_dim': 0, 'num_classes': 2}}, fake_content)
    fake_content.seek(0)
    store[(bucket, key)] = fake_content

    state = s3io.load_latest_model()
    assert 'feature_names' in state and 'config' in state

    # Put mask json
    env = os.environ.get('ENVIRONMENT', 'staging').strip().lower()
    mask_key = f"mask-recommender-{env}/models/mask_data_latest.json"
    store[(bucket, mask_key)] = b'{"18": {"mask_id": 18}}'
    md = s3io.load_mask_data()
    assert md['18']['mask_id'] == 18
