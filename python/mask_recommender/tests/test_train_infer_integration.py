import os
import json
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
import pytest
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
                "fit_family_id": 101,
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
                "fit_family_id": 102,
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
                "fit_family_id": 102,
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
                "fit_family_id": 101,
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
                "fit_family_id": 101,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
            },
            {
                "id": 2,
                "fit_family_id": 102,
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
            "fit_family_id": int(row["fit_family_id"]),
            "unique_internal_model_code": row["unique_internal_model_code"],
            "perimeter_mm": row["perimeter_mm"],
            "strap_type": row["strap_type"],
            "style": row["style"],
        }
        for _, row in masks_df.iterrows()
    }

    category_metadata = train_module._custom_lr_category_metadata(cleaned)
    custom_result = train_module.train_custom_lr_with_split(
        cleaned,
        train_idx=torch.arange(cleaned.shape[0]),
        val_idx=torch.arange(cleaned.shape[0]),
        category_metadata=category_metadata,
        epochs=2,
        learning_rate=0.01,
        class_weighting=False,
    )

    def fake_load_custom_model(self, force=False):
        self.custom_params = custom_result["params"]
        self.custom_metadata = {"timestamp": "test-custom", **category_metadata}
        self.custom_mask_data = mask_data

    def fake_boto3_client(*args, **kwargs):
        return object()

    monkeypatch.setattr(boto3, "client", fake_boto3_client)

    monkeypatch.setattr(
        lambda_function.MaskRecommenderInference,
        "load_custom_model",
        fake_load_custom_model,
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
    recommendations = recommender.recommend_masks_custom(facial_features)

    assert len(recommendations) == 2
    assert {rec["mask_id"] for rec in recommendations} == {1, 2}


def test_training_lambda_builds_custom_lr_argv():
    argv = _build_train_argv(
        {
            "epochs": 100,
            "model_type": "prob",
            "retrain_with_full": True,
        }
    )

    assert "--epochs" in argv
    assert "--model-type" in argv
    assert "custom_lr" in argv
    assert "--retrain-with-full" in argv


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
        "params": {
            "mask_specific_parameters": torch.tensor([[0.0, 0.0, 0.5]], dtype=torch.float32),
            "style_specific_parameters": torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float32),
            "strap_specific_parameters": torch.tensor([[0.0]], dtype=torch.float32),
        },
        "metadata": {
            "timestamp": "2026-03-10",
            "environment": "development",
            "fit_family_categories": ["1"],
            "style_categories": ["Cup"],
            "strap_type_categories": ["Headstrap"],
        },
        "mask_data": {
            "1": {
                "id": 1,
                "fit_family_id": 1,
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

    result = local_recommender_server._infer_custom(
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
        mask_categories=category_metadata["fit_family_categories"],
        style_categories=category_metadata["style_categories"],
        strap_categories=category_metadata["strap_type_categories"],
    )

    assert data["fit_tests_by_masks"].dtype == torch.float32
    assert data["fit_tests_by_styles"].dtype == torch.float32
    assert data["fit_tests_by_strap_types"].dtype == torch.float32
    assert data["perimeter_diffs"].dtype == torch.float32
    assert data["fit_tests_by_masks"].shape[1] == len(category_metadata["fit_family_categories"])
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
                "fit_family_id": 101,
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
                "fit_family_id": 102,
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


def test_local_infer_custom_shares_scores_for_same_fit_family():
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
            "timestamp": "2026-03-19",
            "environment": "development",
            **category_metadata,
        },
        "mask_data": {
            "1": {
                "id": 1,
                "fit_family_id": 101,
                "unique_internal_model_code": "MASK-A",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
            },
            "3": {
                "id": 3,
                "fit_family_id": 101,
                "unique_internal_model_code": "MASK-A-BLACK",
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
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

    probabilities_by_mask = {
        mask_id: result["proba_fit"][index]
        for index, mask_id in result["mask_id"].items()
    }
    assert probabilities_by_mask[1] == probabilities_by_mask[3]


def test_group_train_val_indices_by_user_prevents_user_leakage():
    cleaned = train_module.prepare_training_data(_fit_tests_df())

    torch.manual_seed(0)
    train_idx, val_idx = train_module._group_train_val_indices_by_user(cleaned, train_fraction=0.5)

    train_users = set(cleaned.iloc[train_idx.tolist()]["user_id"].tolist())
    val_users = set(cleaned.iloc[val_idx.tolist()]["user_id"].tolist())

    assert train_users
    assert val_users
    assert train_users.isdisjoint(val_users)


def test_group_train_val_indices_by_user_is_seeded_and_repeatable():
    cleaned = train_module.prepare_training_data(_fit_tests_df())

    first_train_idx, first_val_idx = train_module._group_train_val_indices_by_user(
        cleaned,
        train_fraction=0.5,
        random_seed=42,
    )
    second_train_idx, second_val_idx = train_module._group_train_val_indices_by_user(
        cleaned,
        train_fraction=0.5,
        random_seed=42,
    )
    third_train_idx, third_val_idx = train_module._group_train_val_indices_by_user(
        cleaned,
        train_fraction=0.5,
        random_seed=7,
    )

    assert first_train_idx.tolist() == second_train_idx.tolist()
    assert first_val_idx.tolist() == second_val_idx.tolist()
    assert (
        first_train_idx.tolist() != third_train_idx.tolist()
        or first_val_idx.tolist() != third_val_idx.tolist()
    )


def test_dedupe_prediction_rows_collapses_clone_like_validation_duplicates():
    fit_tests_df = pd.DataFrame(
        [
            {
                "id": 1,
                "user_id": 100,
                "mask_id": 1,
                "fit_family_id": 101,
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
                "user_id": 100,
                "mask_id": 1,
                "fit_family_id": 101,
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
                "created_at": "2026-01-02T00:00:00Z",
            },
        ]
    )
    cleaned = train_module.prepare_training_data(fit_tests_df)

    deduped_frame, deduped_probs, deduped_labels = train_module._dedupe_prediction_rows(
        cleaned,
        probabilities=np.array([0.8, 0.8]),
        labels=np.array([1.0, 1.0]),
    )

    assert cleaned.shape[0] == 2
    assert deduped_frame.shape[0] == 1
    assert deduped_probs.tolist() == [0.8]
    assert deduped_labels.tolist() == [1.0]


def test_dedupe_prediction_rows_prefers_source_fit_test_lineage():
    fit_tests_df = pd.DataFrame(
        [
            {
                "id": 10,
                "source_fit_test_id": None,
                "user_id": 100,
                "mask_id": 1,
                "fit_family_id": 101,
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
                "id": 11,
                "source_fit_test_id": 10,
                "user_id": 100,
                "mask_id": 1,
                "fit_family_id": 101,
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
                "created_at": "2026-01-02T00:00:00Z",
            },
        ]
    )
    cleaned = train_module.prepare_training_data(fit_tests_df)

    deduped_frame, deduped_probs, deduped_labels = train_module._dedupe_prediction_rows(
        cleaned,
        probabilities=np.array([0.8, 0.8]),
        labels=np.array([1.0, 1.0]),
    )

    assert deduped_frame.shape[0] == 1
    assert deduped_probs.tolist() == [0.8]
    assert deduped_labels.tolist() == [1.0]


def test_group_k_fold_indices_by_user_prevents_overlap_across_folds():
    fit_tests_df = pd.DataFrame(
        [
            {**_fit_tests_df().iloc[0].to_dict(), "id": 1, "user_id": 100},
            {**_fit_tests_df().iloc[1].to_dict(), "id": 2, "user_id": 101},
            {**_fit_tests_df().iloc[2].to_dict(), "id": 3, "user_id": 102},
            {**_fit_tests_df().iloc[3].to_dict(), "id": 4, "user_id": 103},
        ]
    )
    cleaned = train_module.prepare_training_data(fit_tests_df)

    folds = train_module._group_k_fold_indices_by_user(cleaned, num_folds=3)

    assert len(folds) == 3
    for train_idx, val_idx in folds:
        train_users = set(cleaned.iloc[train_idx.tolist()]["user_id"].tolist())
        val_users = set(cleaned.iloc[val_idx.tolist()]["user_id"].tolist())
        assert train_users.isdisjoint(val_users)


def test_compute_binary_metrics_supports_equal_user_weighting():
    labels = np.array([1.0, 0.0, 0.0])
    probabilities = np.array([0.9, 0.8, 0.7])
    frame = pd.DataFrame({"user_id": [100, 100, 101]})

    unweighted = train_module._compute_binary_metrics(labels, probabilities, threshold=0.5)
    user_weighted = train_module._compute_binary_metrics(
        labels,
        probabilities,
        threshold=0.5,
        sample_weights=train_module._user_equal_weights(frame),
    )

    assert unweighted["precision"] != user_weighted["precision"]
    assert user_weighted["sample_count"] == 3


def test_compute_top_k_hit_rates_reports_per_user_hit_rate():
    frame = pd.DataFrame(
        {
            "user_id": [100, 100, 101, 101, 102],
        }
    )
    labels = np.array([0.0, 1.0, 0.0, 1.0, 0.0])
    probabilities = np.array([0.9, 0.8, 0.7, 0.95, 0.99])

    top_k = train_module._compute_top_k_hit_rates(
        frame,
        labels=labels,
        probabilities=probabilities,
        ks=(1, 2, 3),
    )

    assert top_k["eligible_users"] == 2
    assert top_k["top_k_hit_rate"]["1"] == 0.5
    assert top_k["top_k_hit_rate"]["2"] == 1.0
    assert top_k["top_k_hit_rate"]["3"] == 1.0


def test_compute_top_k_any_fit_probability_metrics_uses_top_three_predictions():
    frame = pd.DataFrame(
        {
            "user_id": [100, 100, 100, 101, 101, 101, 102, 102],
        }
    )
    labels = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    probabilities = np.array([0.9, 0.4, 0.2, 0.8, 0.3, 0.1, 0.7, 0.2])

    result = train_module._compute_top_k_any_fit_probability_metrics(
        frame,
        labels=labels,
        probabilities=probabilities,
        k=3,
    )

    expected_user_100 = 1.0 - ((1.0 - 0.9) * (1.0 - 0.4) * (1.0 - 0.2))
    expected_user_101 = 1.0 - ((1.0 - 0.8) * (1.0 - 0.3) * (1.0 - 0.1))

    assert result["eligible_users"] == 2
    assert result["excluded_users_with_fewer_than_k_rows"] == 1
    assert result["independence"]["sample_count"] == 2
    assert result["independence"]["positive_rate"] == 0.5
    assert result["independence"]["roc_auc"] == 1.0
    assert result["max_baseline"]["roc_auc"] == 1.0
    assert result["independence"]["mean_predicted_probability"] == pytest.approx(
        np.mean([expected_user_100, expected_user_101])
    )
    assert result["max_baseline"]["mean_predicted_probability"] == pytest.approx(
        np.mean([0.9, 0.8])
    )
    assert result["independence_calibration_bins"]
    assert result["max_baseline_calibration_bins"]


def test_build_cross_validation_top_k_hit_rate_plot_saves_png(tmp_path, monkeypatch):
    monkeypatch.setenv("MASK_RECOMMENDER_IMAGES_DIR", str(tmp_path))
    monkeypatch.setenv("RAILS_ENV", "development")

    artifact = train_module._build_cross_validation_top_k_hit_rate_plot(
        {
            "top_1_hit_rate_mean": 0.76,
            "top_3_hit_rate_mean": 0.92,
            "top_5_hit_rate_mean": 0.95,
        },
        timestamp="20260413210000",
    )

    assert artifact is not None
    artifact_path = Path(artifact)
    assert artifact_path.exists()
    assert artifact_path.suffix == ".png"


def test_save_local_custom_artifacts_persists_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("MASK_RECOMMENDER_LOCAL_MODEL_DIR", str(tmp_path))

    artifact_dir = train_module._save_local_custom_artifacts(
        timestamp="20260328030000",
        params={"weights": torch.tensor([1.0])},
        metadata={"timestamp": "20260328030000"},
        mask_data={"1": {"id": 1}},
        metrics={"threshold": 0.42, "val_f1": 0.73},
    )

    metrics_path = artifact_dir / "custom_metrics.json"
    assert metrics_path.exists()
    assert json.loads(metrics_path.read_text(encoding="utf-8"))["val_f1"] == 0.73
