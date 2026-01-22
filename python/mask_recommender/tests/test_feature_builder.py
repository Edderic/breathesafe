import pandas as pd

from mask_recommender.feature_builder import build_feature_frame


def test_build_feature_frame_matches_get_dummies():
    inference_rows = pd.DataFrame(
        [
            {
                "mask_id": 1,
                "perimeter_mm": 300,
                "strap_type": "Earloop",
                "style": "Cup",
                "unique_internal_model_code": "MASK-A",
                "facial_hair_beard_length_mm": 0,
                "nose_mm": 40,
                "chin_mm": 50,
                "top_cheek_mm": 60,
                "mid_cheek_mm": 55,
                "strap_mm": 120,
            },
            {
                "mask_id": 2,
                "perimeter_mm": 320,
                "strap_type": "Headstrap",
                "style": "Bifold",
                "unique_internal_model_code": "MASK-B",
                "facial_hair_beard_length_mm": 2,
                "nose_mm": 42,
                "chin_mm": 52,
                "top_cheek_mm": 62,
                "mid_cheek_mm": 58,
                "strap_mm": 125,
            },
        ]
    )
    categorical_columns = ["strap_type", "style", "unique_internal_model_code"]
    expected = pd.get_dummies(
        inference_rows,
        columns=categorical_columns,
        dummy_na=True
    )
    feature_columns = list(expected.columns)
    expected = expected.reindex(columns=feature_columns, fill_value=0)
    expected = expected.apply(pd.to_numeric, errors="coerce").fillna(0).astype(float)

    encoded = build_feature_frame(
        inference_rows,
        feature_columns=feature_columns,
        categorical_columns=categorical_columns,
    )

    pd.testing.assert_frame_equal(encoded, expected)
