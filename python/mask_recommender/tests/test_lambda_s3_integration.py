import json
import os
from pathlib import Path

import boto3
import pandas as pd
import pytest
import torch

from mask_recommender.inference import lambda_function
from mask_recommender.train import _detach_custom_lr_parameters


try:
    from moto import mock_s3 as moto_mock_s3
except ImportError:  # pragma: no cover
    moto_mock_s3 = None

try:
    from moto import mock_aws as moto_mock_aws
except ImportError:  # pragma: no cover
    moto_mock_aws = None


def _mock_s3():
    if moto_mock_s3 is not None:
        return moto_mock_s3()
    if moto_mock_aws is not None:
        return moto_mock_aws()
    return None


@pytest.mark.skipif(_mock_s3() is None, reason="moto is not installed")
def test_lambda_loads_model_from_s3_and_recommends():
    with _mock_s3():
        tmp_dir = Path("/tmp/mask_recommender_tests")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        credentials_path = tmp_dir / "aws_credentials"
        credentials_path.write_text(
            "[breathesafe]\n"
            "aws_access_key_id=testing\n"
            "aws_secret_access_key=testing\n"
        )
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(credentials_path)
        os.environ["AWS_PROFILE"] = "breathesafe"
        os.environ["RAILS_ENV"] = "development"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["S3_BUCKET_REGION"] = "us-east-1"

        bucket = "breathesafe-development"
        session = boto3.Session(profile_name="breathesafe", region_name="us-east-1")
        s3 = session.client("s3")
        s3.create_bucket(Bucket=bucket)

        mask_data = {
            "1": {
                "id": 1,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
            }
        }
        facial_features = {
            "nose_mm": 40,
            "chin_mm": 50,
            "top_cheek_mm": 60,
            "mid_cheek_mm": 55,
            "strap_mm": 120,
            "facial_hair_beard_length_mm": 0,
        }
        params = _detach_custom_lr_parameters(
            {
                "mask_specific_parameters": torch.tensor([[0.0, 0.0, 1.0]], dtype=torch.float32),
                "style_specific_parameters": torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float32),
                "strap_specific_parameters": torch.tensor([[0.0]], dtype=torch.float32),
            }
        )
        model_path = tmp_dir / "custom_model_params.pt"
        torch.save(params, model_path)

        metadata = {
            "timestamp": "20260101000000",
            "model_type": "custom_lr",
            "fit_family_categories": ["1"],
            "style_categories": ["Cup"],
            "strap_type_categories": ["Earloop"],
        }
        metadata_path = tmp_dir / "custom_model_metadata.json"
        metadata_path.write_text(json.dumps(metadata))

        mask_data["1"]["fit_family_id"] = 1
        mask_data_path = tmp_dir / "custom_mask_data.json"
        mask_data_path.write_text(json.dumps(mask_data))

        prefix = "mask_recommender/models/20260101000000"
        latest_payload = {
            "timestamp": "20260101000000",
            "params_key": f"{prefix}/custom_model_params.pt",
            "metadata_key": f"{prefix}/custom_model_metadata.json",
            "mask_data_key": f"{prefix}/custom_mask_data.json",
        }

        s3.upload_file(str(model_path), bucket, latest_payload["params_key"])
        s3.upload_file(str(metadata_path), bucket, latest_payload["metadata_key"])
        s3.upload_file(str(mask_data_path), bucket, latest_payload["mask_data_key"])
        s3.put_object(
            Bucket=bucket,
            Key="mask_recommender/models/custom_latest.json",
            Body=json.dumps(latest_payload).encode("utf-8"),
            ContentType="application/json",
        )

        recommender = lambda_function.MaskRecommenderInference()
        recommendations = recommender.recommend_masks_custom(facial_features)

        assert len(recommendations) == 1
        assert recommendations[0]["mask_id"] == 1
        assert 0.0 <= recommendations[0]["proba_fit"] <= 1.0
