import torch

from mask_recommender import train as train_module


def test_initialize_model_uses_configured_outer_dimension():
    original_outer_dim = train_module.num_masks_times_num_bins_plus_other_features
    train_module.num_masks_times_num_bins_plus_other_features = 17
    try:
        model = train_module._initialize_model(feature_count=9)
    finally:
        train_module.num_masks_times_num_bins_plus_other_features = original_outer_dim

    assert isinstance(model[0], torch.nn.Linear)
    assert isinstance(model[2], torch.nn.Linear)
    assert model[0].in_features == 9
    assert model[0].out_features == 17
    assert model[2].in_features == 17
    assert model[2].out_features == 1
