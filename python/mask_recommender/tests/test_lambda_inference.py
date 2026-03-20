import pandas as pd
import torch
from mask_recommender.inference import lambda_function


def test_lambda_recommendations_with_facial_inputs(monkeypatch):
    mask_data = {
        "1": {
            "id": 1,
            "perimeter_mm": 300,
            "strap_type": "Earloop",
            "style": "Cup",
            "unique_internal_model_code": "MASK-A",
        },
        "2": {
            "id": 2,
            "perimeter_mm": 320,
            "strap_type": "Headstrap",
            "style": "Bifold",
            "unique_internal_model_code": "MASK-B",
        },
    }
    facial_features = {
        "nose_mm": 40,
        "chin_mm": 50,
        "top_cheek_mm": 60,
        "mid_cheek_mm": 55,
        "strap_mm": 120,
        "facial_hair_beard_length_mm": 0,
    }

    def fake_load_custom_model(self, force=False):
        self.custom_mask_data = {
            "1": {**mask_data["1"], "fit_family_id": 1},
            "2": {**mask_data["2"], "fit_family_id": 2},
        }
        self.custom_metadata = {
            "timestamp": "test-custom",
            "fit_family_categories": ["1", "2"],
            "style_categories": ["Bifold", "Cup"],
            "strap_type_categories": ["Earloop", "Headstrap"],
        }
        self.custom_params = {
            "mask_specific_parameters": torch.tensor(
                [[0.0, 0.0, 1.0], [0.0, 0.0, -1.0]],
                dtype=torch.float32,
            ),
            "style_specific_parameters": torch.zeros((2, 3), dtype=torch.float32),
            "strap_specific_parameters": torch.zeros((2, 1), dtype=torch.float32),
        }

    monkeypatch.setattr(
        lambda_function.MaskRecommenderInference,
        "load_custom_model",
        fake_load_custom_model,
    )

    recommender = lambda_function.MaskRecommenderInference()
    recommendations = recommender.recommend_masks_custom(facial_features)

    assert len(recommendations) == 2
    assert {rec["mask_id"] for rec in recommendations} == {1, 2}
    assert all(0.0 <= rec["proba_fit"] <= 1.0 for rec in recommendations)
    assert recommendations[0]["mask_id"] == 1


def test_handler_accepts_facial_measurements(monkeypatch):
    class DummyRecommender:
        def __init__(self):
            self.latest_payload = {"timestamp": "test"}
            self.custom_metadata = {"timestamp": "custom-test"}

        def recommend_masks_custom(self, facial_features):
            assert "nose_mm" in facial_features
            return [
                {"mask_id": 10, "proba_fit": 0.9, "mask_info": {}},
                {"mask_id": 20, "proba_fit": 0.1, "mask_info": {}},
            ]

    monkeypatch.setattr(lambda_function, "MaskRecommenderInference", DummyRecommender)

    event = {
        "facial_measurements": {
            "nose_mm": 40,
            "chin_mm": 50,
            "top_cheek_mm": 60,
            "mid_cheek_mm": 55,
            "strap_mm": 120,
            "facial_hair_beard_length_mm": 0,
        }
    }
    response = lambda_function.handler(event, None)
    assert response["statusCode"] == 200
