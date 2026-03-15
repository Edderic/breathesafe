import os

import boto3
import pandas as pd
import torch

from mask_recommender import train as train_module
from mask_recommender.feature_builder import build_feature_frame
from mask_recommender.inference import lambda_function
from mask_recommender.qa import build_mask_candidates, build_inference_rows
from mask_recommender.scripts import local_recommender_server
from mask_recommender.training.lambda_function import _build_train_argv


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
    monkeypatch.setenv("AWS_PROFILE", "breathesafe")
    fit_tests_df = _fit_tests_df()
    masks_df = _masks_df()
    mask_candidates = build_mask_candidates(masks_df)
    outer_dim = train_module._set_num_masks_times_num_bins_plus_other_features(mask_candidates)

    cleaned = train_module.prepare_training_data(fit_tests_df)
    features, target = train_module.build_feature_matrix(cleaned)
    torch.manual_seed(0)
    model, _, _, _, _, _, _, _, _ = train_module.train_predictor(
        features,
        target,
        outer_dim=outer_dim,
        epochs=2,
        learning_rate=0.01,
    )

    feature_columns = list(features.columns)
    categorical_columns = ["strap_type", "style", "brand_model", "unique_internal_model_code"]
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

    def fake_boto3_client(*args, **kwargs):
        return object()

    monkeypatch.setattr(boto3, "client", fake_boto3_client)

    monkeypatch.setattr(
        lambda_function.MaskRecommenderInference,
        "load_model",
        fake_load_model,
    )

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


def test_training_lambda_builds_exclude_brand_model_flag():
    argv = _build_train_argv(
        {
            "epochs": 100,
            "exclude_mask_code": True,
            "exclude_brand_model": True,
        }
    )

    assert "--epochs" in argv
    assert "--exclude-mask-code" in argv
    assert "--exclude-brand-model" in argv


def test_fit_zscore_stats_skips_perimeter_geometry_columns():
    features = pd.DataFrame(
        {
            "perimeter_diff": [1.0, 2.0, 3.0],
            "abs_perimeter_diff": [1.0, 2.0, 3.0],
            "perimeter_diff_sq": [1.0, 4.0, 9.0],
            "earloop_abs_diff": [0.0, 2.0, 0.0],
            "face_size_gap_cm": [3.0, -3.0, 0.0],
            "mask_empirical_badness": [1.0, 0.5, 0.2],
            "mask_badness_x_abs_perimeter_diff": [1.0, 1.0, 0.6],
            "nose_ratio": [0.1, 0.2, 0.3],
        }
    )

    stats = train_module.fit_zscore_stats(features, [0, 1, 2])

    assert "perimeter_diff" not in stats
    assert "abs_perimeter_diff" not in stats
    assert "perimeter_diff_sq" not in stats
    assert "earloop_abs_diff" not in stats
    assert "face_size_gap_cm" not in stats
    assert "mask_empirical_badness" not in stats
    assert "mask_badness_x_abs_perimeter_diff" not in stats
    assert "nose_ratio" in stats


def test_compute_mask_empirical_priors_and_attach_to_masks():
    priors = train_module.compute_mask_empirical_priors(train_module.filter_fit_tests(_fit_tests_df()))

    assert priors[1]["mask_fit_test_count"] == 2.0
    assert priors[1]["mask_smoothed_pass_rate"] == 0.5
    assert priors[1]["mask_empirical_badness"] == 0.5

    masks = train_module.attach_mask_empirical_priors_to_masks(_masks_df(), priors)

    mask_a = masks[masks["id"] == 1].iloc[0]
    assert mask_a["mask_fit_test_count"] == 2.0
    assert mask_a["mask_smoothed_pass_rate"] == 0.5
    assert mask_a["mask_empirical_badness"] == 0.5


def test_local_infer_exposes_empirical_debug_payload():
    artifacts = {
        "model": torch.nn.Sequential(torch.nn.Linear(2, 1)),
        "feature_columns": ["nose_mm", "chin_mm"],
        "categorical_columns": [],
        "metadata": {"timestamp": "2026-03-10", "environment": "development"},
        "mask_data": {
            "1": {
                "id": 1,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Headstrap",
                "style": "Cup",
                "mask_fit_test_count": 12,
                "mask_pass_count": 0,
                "mask_smoothed_pass_rate": 0.07,
            }
        },
    }

    result = local_recommender_server._infer(
        {
            "facial_measurements": {
                "nose_mm": 40,
                "chin_mm": 50,
                "top_cheek_mm": 60,
                "mid_cheek_mm": 55,
                "strap_mm": 120,
            }
        },
        artifacts,
    )

    assert result["model"]["empirical_debug"]["0"]["mask_fit_test_count"] == 12.0
    assert result["model"]["empirical_debug"]["0"]["mask_pass_count"] == 0.0



def test_prep_data_in_torch_with_categories_uses_float32_and_stable_shapes():
    cleaned = train_module.prepare_training_data(_fit_tests_df())
    category_metadata = train_module._custom_lr_category_metadata(cleaned)

    data = train_module.prep_data_in_torch_with_categories(
        cleaned,
        mask_categories=category_metadata["mask_code_categories"],
        style_categories=category_metadata["style_categories"],
        strap_categories=category_metadata["strap_type_categories"],
    )

    assert data["fit_tests_by_masks"].dtype == torch.float32
    assert data["fit_tests_by_styles"].dtype == torch.float32
    assert data["fit_tests_by_strap_types"].dtype == torch.float32
    assert data["perimeter_diffs"].dtype == torch.float32
    assert data["fit_tests_by_masks"].shape[1] == len(category_metadata["mask_code_categories"])
    assert data["fit_tests_by_styles"].shape[1] == len(category_metadata["style_categories"])
    assert data["fit_tests_by_strap_types"].shape[1] == len(category_metadata["strap_type_categories"])


def test_local_infer_custom_scores_masks():
    cleaned = train_module.prepare_training_data(_fit_tests_df())
    category_metadata = train_module._custom_lr_category_metadata(cleaned)
    full_idx = torch.arange(cleaned.shape[0])
    train_result = train_module.train_custom_lr_with_split(
        cleaned,
        train_idx=full_idx,
        val_idx=full_idx,
        category_metadata=category_metadata,
        epochs=2,
        learning_rate=0.01,
    )

    artifacts = {
        "params": train_result["params"],
        "metadata": {
            "timestamp": "2026-03-12",
            "environment": "development",
            **category_metadata,
        },
        "mask_data": {
            "1": {
                "id": 1,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
                "mask_fit_test_count": 2,
                "mask_pass_count": 1,
                "mask_smoothed_pass_rate": 0.5,
            },
            "2": {
                "id": 2,
                "unique_internal_model_code": "MASK-B",
                "perimeter_mm": 320,
                "strap_type": "Headstrap",
                "style": "Bifold",
                "mask_fit_test_count": 2,
                "mask_pass_count": 1,
                "mask_smoothed_pass_rate": 0.5,
            },
        },
    }

    result = local_recommender_server._infer_custom(
        {
            "model_type": "custom_lr",
            "facial_measurements": {
                "nose_mm": 40,
                "chin_mm": 50,
                "top_cheek_mm": 60,
                "mid_cheek_mm": 55,
                "strap_mm": 120,
                "facial_hair_beard_length_mm": 0,
            },
        },
        artifacts,
    )

    assert set(result["mask_id"].values()) == {1, 2}
    assert all(0.0 <= proba <= 1.0 for proba in result["proba_fit"].values())
