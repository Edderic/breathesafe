import torch
import pytest

from mask_recommender import train as train_module


def test_initialize_model_uses_configured_outer_dimension():
    model = train_module._initialize_model(feature_count=9, outer_dim=17)

    assert isinstance(model[0], torch.nn.Linear)
    assert isinstance(model[2], torch.nn.Linear)
    assert model[0].in_features == 9
    assert model[0].out_features == 17
    assert model[2].in_features == 17
    assert model[2].out_features == 1


def test_initialize_model_rejects_non_positive_outer_dim():
    with pytest.raises(RuntimeError, match="outer_dim must be a positive integer"):
        train_module._initialize_model(feature_count=9, outer_dim=0)
