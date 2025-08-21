import json
import os
import sys
import types

import pandas as pd
import pytest

HERE = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.append(REPO_ROOT)

from python.mask_recommender.pytorch import data_utils as du


class FakeResp:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_try_load_remote_json_various_shapes(monkeypatch):
    cases = [
        [
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
        ],
        {"data": [{"a": 1}, {"a": 2}]},
        {"rows": [{"x": 1}]},
        {"items": [{"x": 1}]},
        {"records": [{"x": 1}]},
        {"facial_measurements_fit_tests": [{"x": 1}]},
        {"fit_tests_with_facial_measurements": [{"x": 1}]},
    ]

    def fake_get(url, timeout):
        payload = cases.pop(0)
        return FakeResp(200, payload)

    monkeypatch.setattr(du, "requests", types.SimpleNamespace(get=fake_get))

    for _ in range(7):
        df = du.try_load_remote_json("http://example.com")
        assert isinstance(df, pd.DataFrame)
        assert not df.empty


def test_expand_one_hots_and_filter_z_scores():
    df = pd.DataFrame(
        {
            "mask_id": [18, 22],
            "style": ["Boat", "Cup"],
            "strap_type": ["Headstrap", "Earloops"],
            "face_width_z_score": [0.5, 3.1],
        }
    )
    out = du.expand_one_hots(df.copy())
    assert any(c.startswith("mask_id_") for c in out.columns)
    assert any(c.startswith("style_") for c in out.columns)
    assert any(c.startswith("strap_type_") for c in out.columns)

    filtered = du.filter_z_scores(out)
    assert len(filtered) == 1
