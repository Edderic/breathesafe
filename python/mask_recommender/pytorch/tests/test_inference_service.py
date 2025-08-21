import os
import sys
import numpy as np
import torch

HERE = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

from python.mask_recommender.pytorch.inference_service import build_feature_row, standardize_numeric


def test_build_feature_row_sets_onehots_and_numeric():
    feature_names = [
        "face_width",
        "perimeter_mm",
        "mask_id_18",
        "style_Boat",
        "strap_type_Headstrap",
    ]
    facial = {"face_width": 120}
    mask_info = {"mask_id": 18, "style": "Boat", "strap_type": "Headstrap", "perimeter_mm": 400}
    df = build_feature_row(feature_names, facial, mask_info)
    assert df.loc[0, "face_width"] == 120
    assert df.loc[0, "perimeter_mm"] == 400
    assert df.loc[0, "mask_id_18"] == 1
    assert df.loc[0, "style_Boat"] == 1
    assert df.loc[0, "strap_type_Headstrap"] == 1


def test_standardize_numeric_uses_stats():
    X = np.array([[10.0, 0.0, 1.0], [12.0, 0.0, 0.0]], dtype=np.float32)
    feature_names = ["face_width", "mask_id_18", "adjustable_headstrap"]
    stats = {"mean": [11.0], "std": [2.0]}
    out = standardize_numeric(X.copy(), feature_names, stats)
    # first column standardized
    assert np.allclose(out[:, 0], np.array([-0.5, 0.5]))
    # binary untouched
    assert np.allclose(out[:, 1], X[:, 1])
    assert np.allclose(out[:, 2], X[:, 2])
