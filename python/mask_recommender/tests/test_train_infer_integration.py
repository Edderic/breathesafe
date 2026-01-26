import pandas as pd
import torch

from mask_recommender import train as train_module
from mask_recommender.feature_builder import build_feature_frame
from mask_recommender.inference import lambda_function
from mask_recommender.qa import build_mask_candidates, build_inference_rows


def _fit_tests_df():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "user_id": 100,
                "mask_id": 1,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
                "nose_mm": 40,
                "chin_mm": 50,
                "top_cheek_mm": 60,
                "mid_cheek_mm": 55,
                "strap_mm": 120,
                "facial_hair_beard_length_mm": 0,
                "qlft_pass": "pass",
                "created_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": 2,
                "user_id": 101,
                "mask_id": 2,
                "unique_internal_model_code": "MASK-B",
                "perimeter_mm": 320,
                "strap_type": "Headstrap",
                "style": "Bifold",
                "nose_mm": 42,
                "chin_mm": 52,
                "top_cheek_mm": 62,
                "mid_cheek_mm": 58,
                "strap_mm": 125,
                "facial_hair_beard_length_mm": 2,
                "qlft_pass": "fail",
                "created_at": "2026-01-02T00:00:00Z",
            },
            {
                "id": 3,
                "user_id": 100,
                "mask_id": 2,
                "unique_internal_model_code": "MASK-B",
                "perimeter_mm": 320,
                "strap_type": "Headstrap",
                "style": "Bifold",
                "nose_mm": 40,
                "chin_mm": 50,
                "top_cheek_mm": 60,
                "mid_cheek_mm": 55,
                "strap_mm": 120,
                "facial_hair_beard_length_mm": 0,
                "qlft_pass": "pass",
                "created_at": "2026-01-03T00:00:00Z",
            },
            {
                "id": 4,
                "user_id": 101,
                "mask_id": 1,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
                "nose_mm": 42,
                "chin_mm": 52,
                "top_cheek_mm": 62,
                "mid_cheek_mm": 58,
                "strap_mm": 125,
                "facial_hair_beard_length_mm": 2,
                "qlft_pass": "fail",
                "created_at": "2026-01-04T00:00:00Z",
            },
        ]
    )


def _masks_df():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
            },
            {
                "id": 2,
                "unique_internal_model_code": "MASK-B",
                "perimeter_mm": 320,
                "strap_type": "Headstrap",
                "style": "Bifold",
            },
        ]
    )


def test_training_and_inference_alignment(monkeypatch, tmp_path):
    fit_tests_df = _fit_tests_df()
    masks_df = _masks_df()
    mask_candidates = build_mask_candidates(masks_df)
    train_module.num_masks_times_num_bins_plus_other_features = (
        train_module._set_num_masks_times_num_bins_plus_other_features(mask_candidates)
    )

    cleaned = train_module.prepare_training_data(fit_tests_df)
    features, target = train_module.build_feature_matrix(cleaned)
    torch.manual_seed(0)
    model, _, _, _, _, _, _, _, _ = train_module.train_predictor(
        features,
        target,
        epochs=2,
        learning_rate=0.01,
    )

    feature_columns = list(features.columns)
    categorical_columns = ["strap_type", "style", "unique_internal_model_code"]
    user_row = fit_tests_df.iloc[0]
    inference_rows = build_inference_rows(user_row, mask_candidates)
    encoded = build_feature_frame(
        inference_rows,
        feature_columns=feature_columns,
        categorical_columns=categorical_columns,
    )
    assert list(encoded.columns) == feature_columns

    mask_data = {
        str(row["id"]): {
            "id": int(row["id"]),
            "unique_internal_model_code": row["unique_internal_model_code"],
            "perimeter_mm": row["perimeter_mm"],
            "strap_type": row["strap_type"],
            "style": row["style"],
        }
        for _, row in masks_df.iterrows()
    }

    def fake_load_model(self, force=False):
        self.model = model
        self.mask_data = mask_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.model_input_dim = len(feature_columns)
        self.use_facial_perimeter = False
        self.use_diff_perimeter_bins = False
        self.use_diff_perimeter_mask_bins = False

    monkeypatch.setattr(
        lambda_function.MaskRecommenderInference,
        "load_model",
        fake_load_model,
    )

    config_path = tmp_path / "aws_config"
    config_path.write_text("[profile breathesafe]\nregion = us-east-1\n")
    credentials_path = tmp_path / "aws_credentials"
    credentials_path.write_text(
        "[breathesafe]\naws_access_key_id = test\naws_secret_access_key = test\n"
    )
    monkeypatch.setenv("AWS_PROFILE", "breathesafe")
    monkeypatch.setenv("AWS_CONFIG_FILE", str(config_path))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(credentials_path))

    recommender = lambda_function.MaskRecommenderInference()
    facial_features = {
        "nose_mm": 40,
        "chin_mm": 50,
        "top_cheek_mm": 60,
        "mid_cheek_mm": 55,
        "strap_mm": 120,
        "facial_hair_beard_length_mm": 0,
    }
    recommendations = recommender.recommend_masks(facial_features)

    assert len(recommendations) == 2
    assert {rec["mask_id"] for rec in recommendations} == {1, 2}
