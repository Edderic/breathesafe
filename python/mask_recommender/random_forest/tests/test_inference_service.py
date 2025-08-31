import json
import types

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from python.mask_recommender.random_forest.inference_service import infer
from python.mask_recommender.random_forest import s3_io


class DummyState(dict):
    pass


def test_infer_shapes(monkeypatch):
    # Build dummy state
    rf = RandomForestClassifier(n_estimators=2, random_state=0)

    # 2 masks, simple features
    feature_names = [
        "face_width", "face_length",
        "nose_protrusion", "bitragion_subnasale_arc",
        "facial_hair_beard_length_mm", "perimeter_mm",
        "adjustable_headstrap", "adjustable_earloops",
        "mask_id_1", "mask_id_2",
    ]

    # Train a trivial model
    X_train = np.array([
        [140, 120, 25, 230, 0,   500, 1, 0, 1, 0],
        [130, 110, 30, 240, 5,   520, 0, 1, 0, 1],
    ], dtype=np.float32)
    y_train = np.array([1, 0], dtype=np.int64)
    rf.fit(X_train, y_train)

    state = DummyState(model=rf, feature_names=feature_names, threshold=0.5, stats=None)

    def fake_load_latest_model():
        return state

    def fake_load_mask_data():
        return {
            "1": {"mask_id": 1, "perimeter_mm": 500, "style": "fold", "strap_type": "ear"},
            "2": {"mask_id": 2, "perimeter_mm": 520, "style": "cup", "strap_type": "head"},
        }

    monkeypatch.setattr(s3_io, "load_latest_model", fake_load_latest_model)
    monkeypatch.setattr(s3_io, "load_mask_data", fake_load_mask_data)

    out = infer({"face_width": 135, "face_length": 112}, mask_ids=None)
    assert set(out.keys()) == {"mask_id", "proba_fit", "threshold"}
    assert len(out["mask_id"]) == 2
    assert len(out["proba_fit"]) == 2
