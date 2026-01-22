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

    inference_rows = pd.DataFrame(
        [
            {
                "mask_id": 1,
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
                "unique_internal_model_code": "MASK-A",
                "facial_hair_beard_length_mm": 0,
                "nose_mm": facial_features["nose_mm"],
                "chin_mm": facial_features["chin_mm"],
                "top_cheek_mm": facial_features["top_cheek_mm"],
                "mid_cheek_mm": facial_features["mid_cheek_mm"],
                "strap_mm": facial_features["strap_mm"],
            },
            {
                "mask_id": 2,
                "perimeter_mm": 320,
                "strap_type": "Headstrap",
                "style": "Bifold",
                "unique_internal_model_code": "MASK-B",
                "facial_hair_beard_length_mm": 0,
                "nose_mm": facial_features["nose_mm"],
                "chin_mm": facial_features["chin_mm"],
                "top_cheek_mm": facial_features["top_cheek_mm"],
                "mid_cheek_mm": facial_features["mid_cheek_mm"],
                "strap_mm": facial_features["strap_mm"],
            },
        ]
    )

    categorical_columns = ["strap_type", "style", "unique_internal_model_code"]
    expected = pd.get_dummies(inference_rows, columns=categorical_columns, dummy_na=True)
    feature_columns = list(expected.columns)

    def fake_load_model(self, force=False):
        self.model = torch.nn.Sequential(torch.nn.Linear(len(feature_columns), 1))
        torch.nn.init.zeros_(self.model[0].weight)
        torch.nn.init.zeros_(self.model[0].bias)
        column_index = {name: idx for idx, name in enumerate(feature_columns)}
        for code, weight in (("unique_internal_model_code_MASK-A", 1.0),
                             ("unique_internal_model_code_MASK-B", -1.0)):
            idx = column_index.get(code)
            if idx is not None:
                self.model[0].weight.data[0, idx] = weight
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

    recommender = lambda_function.MaskRecommenderInference()
    recommendations = recommender.recommend_masks(facial_features)

    assert len(recommendations) == 2
    assert {rec["mask_id"] for rec in recommendations} == {1, 2}
    assert all(0.0 <= rec["proba_fit"] <= 1.0 for rec in recommendations)
    assert recommendations[0]["mask_id"] == 1


def test_handler_accepts_facial_measurements(monkeypatch):
    class DummyRecommender:
        def __init__(self):
            self.latest_payload = {"timestamp": "test"}

        def recommend_masks(self, facial_features):
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
