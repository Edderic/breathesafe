import os
import sys
import pandas as pd

HERE = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

from python.mask_recommender.pytorch.data_prep import prepare_dataset


def test_prepare_dataset_builds_features_and_dataset():
    df = pd.DataFrame(
        {
            "qlft_pass": [True, False, True],
            "face_width": [120, 130, 110],
            "face_length": [110, 120, 105],
            "mask_id": [18, 22, 18],
            "style": ["Boat", "Cup", "Boat"],
            "strap_type": ["Headstrap", "Earloops", "Headstrap"],
        }
    )
    dataset, feature_names = prepare_dataset(df)
    assert len(dataset) == 3
    assert any(c.startswith("mask_id_") for c in feature_names)
    assert any(c.startswith("style_") for c in feature_names)
    assert any(c.startswith("strap_type_") for c in feature_names)
