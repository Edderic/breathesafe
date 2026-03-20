import argparse
import io
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

REPO_ROOT = Path(__file__).resolve().parents[0]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import boto3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from botocore.exceptions import ClientError
from matplotlib.lines import Line2D
from breathesafe_network import (build_session, fetch_facial_measurements_fit_tests,
                                 fetch_json, login_with_credentials, logout)
from feature_builder import (ABS_PERIMETER_DIFF_STYLE_PREFIX,
                             FACE_SHAPE_FEATURE_COLUMNS,
                             FACE_STYLE_INTERACTION_PREFIX,
                             FACIAL_FEATURE_COLUMNS,
                             FACIAL_PERIMETER_COMPONENTS,
                             MASK_EMPIRICAL_FEATURE_COLUMNS,
                             MASK_SIZE_FEATURE_COLUMNS,
                             PERIMETER_DIFF_SQ_STYLE_PREFIX,
                             PERIMETER_DIFF_STYLE_PREFIX,
                             PERIMETER_PENALTY_FEATURE_COLUMNS,
                             STRAP_STYLE_INTERACTION_PREFIX,
                             add_brand_model_column, add_face_shape_features,
                             add_face_style_interactions,
                             add_geometry_penalty_features,
                             add_mask_size_face_interactions,
                             add_mask_size_features,
                             add_strap_style_interactions,
                             add_strap_type_features,
                             add_style_perimeter_interactions,
                             build_feature_frame, derive_brand_model,
                             diff_bin_edges, diff_bin_index, diff_bin_labels,
                             scale_perimeter_diff_features)
from predict_arkit_from_traditional import (TARGET_COLUMNS,
                                            predict_arkit_from_traditional)
from qa import build_mask_candidates, build_recommendation_preview
from sklearn.metrics import (auc, f1_score, precision_score, recall_score,
                             roc_auc_score, roc_curve)
from utils import display_percentage

"""
Notes

generally speaking, the bigger the difference between the facial and mask
perimeters, the lower the probability of fit, with some exceptions:

- bifold,

- duckbill and boat masks wrap under the chin so can have mask perimeters
that are significantly larger than the facial perimeters, yet have a great
fit.

- baggy blues should in theory have poor performance regardless of
difference

- strapless w/ adhesive style (e.g. Readimask) should have more of a
uniform distribution

- elastomerics: has more rigidity than filtering facepiece respirators
(FFRs). Long nose vs short nose could make a big difference in fit
(relative to FFR — FFR is more flexible.)

TODO: incorporate fit testing data that has no facial measurements associated with
them. Incorporate those here.

TODO: some iOS aggregated facial measurements are from actual face scans, while
others are just predicted. For those that are predicted, set requires_grad
= True, but for those that are from actual face scans, set requires_grad
to False,

Maybe instead of user vs. masks, really it should be more like
facial measurements vs. mask. The latter allows the same user being represented
more than once, as they age (and their facial measurements change)?

"""

STRAP_TYPES = [
    'Earloop',
    'Adjustable Earloop',
    'Headstrap',
    'Adjustable Headstrap',
    'Strapless'
]

FACIAL_MEASUREMENTS = [
    'nose_mm',
    'top_cheek_mm',
    'mid_cheek_mm',
    'chin_mm',
]

STYLE_TYPES = [
    'Cup',
    'Duckbill',
    'Bifold',
    'Bifold & Gasket',
    'Boat',
    'Adhesive',
    'Elastomeric'
]

DEFAULT_PROBE_PAYLOADS = [
    {
        'label': 'edderic_probe_20260310',
        'facial_measurements': {
            'nose_mm': 46.72047233581543,
            'chin_mm': 122.5139946937561,
            'top_cheek_mm': 98.81752729415894,
            'mid_cheek_mm': 95.16602277755737,
            'strap_mm': 130.28683853149414,
            'facial_hair_beard_length_mm': 0.0,
        }
    }
]
PROBE_WATCHLIST_FAMILIES = ['drager', 'laianzhi', 'trident', 'aura', 'zimi']


def initialize_betas(diff_keys, num_users, num_masks, style_types):
    """
    Creates torch tensor consisting of parameters taking into account
    interactions between mask style (e.g. cup, bifold, etc.) and facial vs. mask perimeter
    distance.

    Parameters:
        diff_keys: list[str]
            e.g. 'x < -50', '-50 <= x < -40', '-40 <= x < -30', ... 'x > 50'

        num_users: integer

        num_masks: integer

    Returns: torch.tensor
        Size: (num_users, num_masks, len(STYLE_TYPES), len(diff_keys)).
    """

    return torch.rand((num_users, num_masks, len(style_types)), len(diff_keys))


def produce_beta_tensor_diff_styles(beta_style_diff_bins, styles, diff_bins, num_users, num_masks):
    """
    Parameters:
        beta_style_diff_bins

    """
    i = 0
    to_concat = []
    users_by_masks_ones = torch.ones((num_users, num_masks))

    for i, _ in diff_bins.enumerate():
        for j in styles:
            to_concat.append(
                # TODO: verify that the multiplication is correct
                users_by_masks_ones * beta_style_diff_bins[i]
            )

            i += 1

    return torch.stack(to_concat)


def produce_diff_bins(user_ones, difference, start, end, interval=10):
    """
    Computes membership of user-mask pair difference being in a particular bin.

    Parameters:
        difference: torch.tensor
            Has the shape (num_users, num_masks), consisting of 1s and 0s, where
            1 indicates membership and 0 indicates not being part of the group

    Returns: torch.tensor
        Size: (num_bins, num_users, num_masks)
    """

    type_tensors = []

    type_tensors.append(
        (difference < start).float()
    )

    for i in range(start, end, interval):
        type_tensors.append(
            ((difference >= i) & (difference < (i + interval))).float()
        )

    type_tensors.append(
        (difference > end).float()
    )


    return torch.stack(type_tensors)


def get_users(fit_tests_df, with_perimeter, user_arkit_table):
    """
    Parameters:
        fit_tests_df: pd.DataFrame

        with_perimeter: pd.DataFrame
            masks dataframe that have perimeter values


    Returns: int
    """
    fit_tests_with_perimeter_mm = fit_tests_df[
        fit_tests_df['mask_id'].isin(with_perimeter['id'])
    ]

    user_ids = list(sorted(fit_tests_with_perimeter_mm['user_id'].unique()))
    return user_arkit_table[user_arkit_table['user_id'].isin(user_ids)]


def produce_filters_diff_styles(diff_bins, user_ones, mask_vs_styles):
    """
    Produces filters where each 2D matrix denotes membership for a particular diff_bin and style.

    Parameters:
        diff_bins: torch.tensor
            Size: (num_bins, num_users, num_masks)

        user_ones: torch.tensor
            Size: (num_users, 1)

    Returns: torch.tensor
        Size: (num_bins x num_styles, num_users, num_masks)
    """
    to_concat = []
    for j, d in enumerate(diff_bins.shape[0]):
        for i, _ in enumerate(mask_vs_styles.shape[1]):
            user_vs_styles = user_ones @ mask_vs_styles[:, i].T
            to_concat.append(d * user_vs_styles)

    return torch.stack(to_concat)


def produce_summation(betas, users_by_masks_by_strap_types, users_by_masks_by_style):
    """
    For each difference bin (e.g. diff < -50, -50 <= diff < -40, ...),
    multiply the mask_types_over_users filters, which is a tensor of size (num_users, num_masks, len(STYLE_TYPES)) with the corresponding betas,
    also of size (num_users, num_masks, len(STYLE_TYPES)). Then add them up
    to get a matrix of size (num_users, num_masks) which represents scores.


    Parameters:
        betas: torch.tensor
            size (num_users, num_masks, len(STYLE_TYPES), len(diff_bins))

        mask_types_over_users: torch.tensor
            size (num_users, num_masks, len(STYLE_TYPES), len(diff_bins))

    Returns: torch.tensor
        Size: (num_users, num_masks)
    """
    summation = None
    for i in range(len(STYLE_TYPES)):
        if summation is None:
            summation = betas[:,:,:,i] * users_by_masks_by_style[:,:,:,i]
        else:
            summation += betas[:,:,:,i] * users_by_masks_by_style[:,:,:,i]

    return summation.sum(axis=2)


def get_masks(session, masks_url):
    masks_payload = fetch_json(session, masks_url).get("masks", [])
    return pd.DataFrame(masks_payload)


def get_users_by_masks_by_types(user_ones, sorted_tested_masks, by):
    """
    This returns a (num_users, num_masks, num strap_types) torch tensor,
    representing whether or not the mask for a given user is of a particular strap_type.
    This will be used as a filter that will be multiplied with strap-related weights.

    Parameters:
        sorted_tested_masks: pd.DataFrame

        by: str
            e.g. 'strap_type', 'style'

    Returns: torch.tensor
        Size: (num strap_types, num_users, num_masks)
    """

    type_dummies = pd.get_dummies(sorted_tested_masks[by])
    len_types = type_dummies.shape[1]

    masks_vs_type_dummies = torch.from_numpy(type_dummies.to_numpy())

    type_tensors = []
    for i in range(len_types):
        expanded = user_ones @ masks_vs_type_dummies[:, i].float().unsqueeze(0)
        type_tensors.append(expanded.unsqueeze(-1))

    return torch.cat(type_tensors)


def _is_truthy(value):
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return str(value).strip().lower() in ['true', '1', 'yes', 'y']


def _normalize_pass(value):
    if isinstance(value, bool):
        return int(value)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    normalized = str(value).strip().lower()
    if normalized in ['true', '1', 'pass', 'passed', 'yes', 'y']:
        return 1
    if normalized in ['false', '0', 'fail', 'failed', 'no', 'n']:
        return 0
    return None


def filter_fit_tests(fit_tests_df):
    filtered = fit_tests_df.copy()
    filtered = filtered[filtered['perimeter_mm'].notna()]

    if 'mask_modded' in filtered.columns:
        mask_modded_flags = filtered['mask_modded'].apply(_is_truthy)
        filtered = filtered[~mask_modded_flags]
    else:
        logging.info("mask_modded column not found; skipping modded filtering.")

    filtered = filtered.dropna(subset=FACIAL_FEATURE_COLUMNS)

    filtered['qlft_pass_normalized'] = filtered['qlft_pass'].apply(_normalize_pass)
    filtered = filtered[filtered['qlft_pass_normalized'].notna()]
    return filtered


def prepare_training_data(
    fit_tests_df,
    mask_empirical_priors=None,
    use_facial_perimeter=False,
    use_diff_perimeter_bins=False,
    use_diff_perimeter_mask_bins=False
):
    filtered = filter_fit_tests(fit_tests_df)
    filtered = add_brand_model_column(filtered)
    filtered = add_strap_type_features(filtered)
    filtered = add_face_shape_features(filtered)
    filtered = add_mask_size_features(filtered)
    filtered = add_mask_size_face_interactions(filtered)
    filtered = add_geometry_penalty_features(filtered)
    filtered = add_mask_empirical_prior_features(filtered, mask_empirical_priors or {})
    filtered = add_strap_style_interactions(filtered)

    feature_cols = []
    if use_diff_perimeter_bins or use_diff_perimeter_mask_bins:
        filtered['perimeter_diff'] = filtered['facial_perimeter_mm'] - filtered['perimeter_mm']
        filtered['perimeter_diff_bin_index'] = diff_bin_index(filtered['perimeter_diff'])
        filtered = scale_perimeter_diff_features(filtered)
        filtered = add_geometry_penalty_features(filtered)
        if use_diff_perimeter_bins:
            filtered['perimeter_diff_bin'] = pd.cut(
                filtered['perimeter_diff'],
                bins=diff_bin_edges(),
                labels=diff_bin_labels(),
                right=False
            )
            diff_dummies = pd.get_dummies(filtered['perimeter_diff_bin'])
            filtered = pd.concat([filtered, diff_dummies], axis=1)
            feature_cols += list(diff_dummies.columns)
        if use_diff_perimeter_mask_bins:
            mask_bins = pd.DataFrame(
                0,
                index=filtered.index,
                columns=filtered['unique_internal_model_code'].astype(str)
            )
            mask_bins = mask_bins.loc[:, ~mask_bins.columns.duplicated()]
            mask_codes = filtered['unique_internal_model_code'].astype(str)
            mask_bins.values[range(len(mask_bins)), mask_bins.columns.get_indexer(mask_codes)] = filtered[
                'perimeter_diff_bin_index'
            ].values
            mask_bins.columns = [f"mask_bin_{col}" for col in mask_bins.columns]
            filtered = pd.concat([filtered, mask_bins], axis=1)
            feature_cols += list(mask_bins.columns)
    else:
        filtered['perimeter_diff'] = filtered['facial_perimeter_mm'] - filtered['perimeter_mm']
        filtered['perimeter_diff_sq'] = filtered['perimeter_diff'] ** 2
        filtered = scale_perimeter_diff_features(filtered)
        filtered = add_geometry_penalty_features(filtered)
        filtered = add_style_perimeter_interactions(filtered)
        filtered = add_face_style_interactions(filtered)
        filtered = add_strap_style_interactions(filtered)
        interaction_cols = sorted(
            [
                column for column in filtered.columns
                if column.startswith(PERIMETER_DIFF_STYLE_PREFIX)
                or column.startswith(ABS_PERIMETER_DIFF_STYLE_PREFIX)
                or column.startswith(PERIMETER_DIFF_SQ_STYLE_PREFIX)
                or column.startswith(FACE_STYLE_INTERACTION_PREFIX)
                or column.startswith(STRAP_STYLE_INTERACTION_PREFIX)
            ]
        )

        feature_cols = [
            'perimeter_diff',
            'abs_perimeter_diff',
            'perimeter_diff_sq'
        ] + PERIMETER_PENALTY_FEATURE_COLUMNS + FACE_SHAPE_FEATURE_COLUMNS + MASK_SIZE_FEATURE_COLUMNS + MASK_EMPIRICAL_FEATURE_COLUMNS + interaction_cols
        if use_facial_perimeter:
            feature_cols.append('facial_perimeter_mm')
        else:
            feature_cols += FACIAL_FEATURE_COLUMNS
    feature_cols += [
        'mask_id',
        'fit_family_id',
        'user_id',
        'strap_is_earloop_like',
        'strap_is_headstrap_like',
        'strap_is_adjustable',
        'strap_type_strength',
        'facial_hair_beard_length_mm',
        'strap_type',
        'style',
        'brand_model',
        'unique_internal_model_code'
    ]
    filtered = filtered[feature_cols + ['qlft_pass_normalized']]
    return filtered


def build_feature_matrix(filtered_df, categorical_cols=None):
    if categorical_cols is None:
        categorical_cols = ['strap_type', 'style', 'brand_model', 'unique_internal_model_code']
    filtered_df = filtered_df.drop(columns=['mask_id', 'fit_family_id'], errors='ignore')
    features = pd.get_dummies(filtered_df, columns=categorical_cols, dummy_na=True)
    target = features.pop('qlft_pass_normalized')
    features = features.apply(pd.to_numeric, errors='coerce').fillna(0)
    features = features.astype(float)
    target = pd.to_numeric(target, errors='coerce').fillna(0).astype(float)
    return features, target


def compute_mask_empirical_priors(fit_tests_df):
    if fit_tests_df is None or fit_tests_df.empty:
        return {}

    grouped = (
        fit_tests_df.groupby('mask_id', dropna=True)['qlft_pass_normalized']
        .agg(['count', 'sum'])
        .reset_index()
    )

    priors = {}
    for _, row in grouped.iterrows():
        mask_id = row.get('mask_id')
        if pd.isna(mask_id):
            continue
        count = float(row.get('count', 0) or 0)
        passes = float(row.get('sum', 0) or 0)
        smoothed_pass_rate = (passes + 1.0) / (count + 2.0)
        clipped_rate = min(max(smoothed_pass_rate, 1e-6), 1 - 1e-6)
        empirical_badness = 1.0 - smoothed_pass_rate
        zero_passes = passes == 0.0
        priors[int(mask_id)] = {
            'mask_fit_test_count': count,
            'mask_pass_count': passes,
            'mask_smoothed_pass_rate': smoothed_pass_rate,
            'mask_log_fit_test_count': float(np.log1p(count)),
            'mask_smoothed_pass_logit': float(np.log(clipped_rate / (1.0 - clipped_rate))),
            'mask_empirical_badness': empirical_badness,
            'mask_zero_passes_min_5': float(zero_passes and count >= 5.0),
            'mask_zero_passes_min_10': float(zero_passes and count >= 10.0),
            'mask_fail_only_rate': float(zero_passes),
        }
    return priors


def add_mask_empirical_prior_features(frame, priors_by_mask_id):
    if frame is None or frame.empty:
        return frame

    result = frame.copy()
    defaults = {
        'mask_fit_test_count': 0.0,
        'mask_smoothed_pass_rate': 0.5,
        'mask_log_fit_test_count': 0.0,
        'mask_smoothed_pass_logit': 0.0,
        'mask_empirical_badness': 0.5,
        'mask_zero_passes_min_5': 0.0,
        'mask_zero_passes_min_10': 0.0,
        'mask_fail_only_rate': 0.0,
        'mask_badness_x_abs_perimeter_diff': 0.0,
        'mask_zero_passes_min_10_x_earloop': 0.0,
    }

    mask_id_source = result.get('mask_id')
    if mask_id_source is None:
        mask_id_source = result.get('id')
    if mask_id_source is None or not hasattr(mask_id_source, 'items'):
        mask_ids = pd.Series([np.nan] * len(result), index=result.index)
    else:
        mask_ids = pd.to_numeric(mask_id_source, errors='coerce')
    for column in MASK_EMPIRICAL_FEATURE_COLUMNS:
        result[column] = defaults[column]

    for idx, mask_id in mask_ids.items():
        if pd.isna(mask_id):
            continue
        prior = priors_by_mask_id.get(int(mask_id))
        if not prior:
            continue
        for column in MASK_EMPIRICAL_FEATURE_COLUMNS:
            if column in prior:
                result.at[idx, column] = float(prior.get(column, defaults[column]))

    if 'abs_perimeter_diff' in result.columns:
        result['mask_badness_x_abs_perimeter_diff'] = (
            pd.to_numeric(result['mask_empirical_badness'], errors='coerce').fillna(0)
            * pd.to_numeric(result['abs_perimeter_diff'], errors='coerce').fillna(0)
        )
    if 'strap_is_earloop_like' in result.columns:
        result['mask_zero_passes_min_10_x_earloop'] = (
            pd.to_numeric(result['mask_zero_passes_min_10'], errors='coerce').fillna(0)
            * pd.to_numeric(result['strap_is_earloop_like'], errors='coerce').fillna(0)
        )

    return result


def attach_mask_empirical_priors_to_masks(mask_frame, priors_by_mask_id):
    if mask_frame is None or mask_frame.empty:
        return mask_frame
    return add_mask_empirical_prior_features(mask_frame, priors_by_mask_id)


def _is_binary_series(series):
    unique_values = pd.unique(pd.to_numeric(series, errors='coerce').fillna(0))
    if unique_values.size == 0:
        return True
    rounded = {float(np.round(value, 10)) for value in unique_values}
    return rounded.issubset({0.0, 1.0})


PERIMETER_ZSCORE_EXCLUDED_COLUMNS = set(
    [
        'perimeter_diff',
        'abs_perimeter_diff',
        'perimeter_diff_sq',
        'mask_face_size_anchor_cm',
        'face_size_gap_cm',
        'abs_face_size_gap_cm',
        'face_size_gap_sq',
    ] + PERIMETER_PENALTY_FEATURE_COLUMNS + MASK_EMPIRICAL_FEATURE_COLUMNS
)

PERIMETER_ZSCORE_EXCLUDED_PREFIXES = (
    PERIMETER_DIFF_STYLE_PREFIX,
    ABS_PERIMETER_DIFF_STYLE_PREFIX,
    PERIMETER_DIFF_SQ_STYLE_PREFIX,
)


def _should_skip_zscore(column):
    if column in PERIMETER_ZSCORE_EXCLUDED_COLUMNS:
        return True
    return any(column.startswith(prefix) for prefix in PERIMETER_ZSCORE_EXCLUDED_PREFIXES)


def fit_zscore_stats(features, row_indices):
    if isinstance(row_indices, torch.Tensor):
        row_indices = row_indices.detach().cpu().numpy()

    if len(row_indices) == 0:
        return {}

    train_frame = features.iloc[row_indices]
    stats = {}
    for column in features.columns:
        column_values = pd.to_numeric(train_frame[column], errors='coerce').fillna(0)
        if _should_skip_zscore(column):
            continue
        if _is_binary_series(column_values):
            continue

        mean_value = float(column_values.mean())
        std_value = float(column_values.std(ddof=0))
        if not np.isfinite(mean_value):
            mean_value = 0.0
        if not np.isfinite(std_value) or std_value == 0.0:
            std_value = 1.0
        stats[column] = {
            'mean': mean_value,
            'std': std_value,
        }

    return stats


def apply_zscore(features, zscore_stats):
    if not zscore_stats:
        return features

    scaled = features.copy()
    for column, values in zscore_stats.items():
        if column not in scaled.columns:
            continue
        mean_value = float(values.get('mean', 0.0))
        std_value = float(values.get('std', 1.0))
        if not np.isfinite(std_value) or std_value == 0.0:
            std_value = 1.0
        scaled[column] = (pd.to_numeric(scaled[column], errors='coerce').fillna(0) - mean_value) / std_value
    return scaled


@dataclass(frozen=True)
class TrainModelConfig:
    outer_dim: int


def _set_num_masks_times_num_bins_plus_other_features(mask_candidates):
    num_masks = int(mask_candidates.shape[0])
    num_bins = len(diff_bin_edges())
    num_styles = int(mask_candidates['style'].dropna().nunique())
    num_strap_types = int(mask_candidates['strap_type'].dropna().nunique())
    num_brand_models = int(mask_candidates['brand_model'].dropna().nunique())
    other_features = 1 + num_strap_types
    # For each bin, there's a quadratic term for the number of styles: ax2 +
    # bx...
    return (
        (num_masks + num_brand_models + num_styles + num_strap_types) * num_bins
        * 2 + other_features
    )


def _initialize_model(feature_count, outer_dim):
    outer_dim = int(outer_dim)
    if outer_dim <= 0:
        raise RuntimeError(
            "outer_dim must be a positive integer."
        )
    model = torch.nn.Sequential(
        torch.nn.Linear(feature_count, outer_dim),
        torch.nn.ReLU(),
        torch.nn.Linear(outer_dim, 1),
        torch.nn.Sigmoid()
    )
    return model


def _extract_hidden_sizes(model):
    hidden_sizes = []
    for layer in model:
        if isinstance(layer, torch.nn.Linear):
            hidden_sizes.append(int(layer.out_features))
    if not hidden_sizes:
        return []
    return hidden_sizes[:-1]


def _focal_loss(probs, targets, alpha=0.25, gamma=2.0, eps=1e-6):
    probs = torch.clamp(probs, eps, 1 - eps)
    p_t = torch.where(targets == 1, probs, 1 - probs)
    alpha_t = torch.where(targets == 1, alpha, 1 - alpha)
    loss = -alpha_t * (1 - p_t) ** gamma * torch.log(p_t)
    return loss


def _train_with_split(
    x_train,
    y_train,
    x_val,
    y_val,
    outer_dim,
    epochs=50,
    learning_rate=0.01,
    loss_type="bce",
    focal_alpha=0.25,
    focal_gamma=2.0,
    train_weights=None,
    val_weights=None,
    class_weighting=False,
):
    train_positive_rate = float(y_train.mean().item()) if y_train.numel() else 0.0
    val_positive_rate = float(y_val.mean().item()) if y_val.numel() else 0.0
    model = _initialize_model(x_train.shape[1], outer_dim=outer_dim)

    loss_fn = torch.nn.BCELoss(reduction='none')
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    train_losses = []
    val_losses = []
    pos_count = float(y_train.sum().item())
    neg_count = float((1 - y_train).sum().item())
    pos_weight = (neg_count / pos_count) if pos_count > 0 else 1.0
    pos_weight_tensor = torch.tensor(pos_weight, dtype=torch.float32)
    logging.info(
        "Training balance: train_pos_rate=%.3f val_pos_rate=%.3f pos_weight=%.3f loss=%s",
        train_positive_rate,
        val_positive_rate,
        pos_weight,
        loss_type
    )
    if class_weighting:
        logging.info("Class weighting enabled.")

    if train_weights is None:
        train_weights = torch.ones_like(y_train)
    if val_weights is None:
        val_weights = torch.ones_like(y_val)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        probs = model(x_train)
        if loss_type == "focal":
            loss = _focal_loss(
                probs,
                y_train,
                alpha=focal_alpha,
                gamma=focal_gamma
            )
            loss = (loss * train_weights).mean()
        else:
            if class_weighting:
                class_weights = torch.where(y_train == 1, pos_weight_tensor, torch.tensor(1.0))
            else:
                class_weights = torch.ones_like(y_train)
            loss = (loss_fn(probs, y_train) * class_weights * train_weights).mean()
        loss.backward()
        optimizer.step()
        train_losses.append(loss.item())

        if (epoch + 1) % 10 == 0 or epoch == 0:
            model.eval()
            with torch.no_grad():
                val_probs = model(x_val)
                if loss_type == "focal":
                    val_loss = _focal_loss(
                        val_probs,
                        y_val,
                        alpha=focal_alpha,
                        gamma=focal_gamma
                    )
                    val_loss = (val_loss * val_weights).mean().item()
                else:
                    if class_weighting:
                        class_weights = torch.where(y_val == 1, pos_weight_tensor, torch.tensor(1.0))
                    else:
                        class_weights = torch.ones_like(y_val)
                    val_loss = (loss_fn(val_probs, y_val) * class_weights * val_weights).mean().item()
                preds = (val_probs >= 0.5).float()
                accuracy = (preds == y_val).float().mean().item()
                true_pos = ((preds == 1) & (y_val == 1)).float().sum().item()
                false_pos = ((preds == 1) & (y_val == 0)).float().sum().item()
                false_neg = ((preds == 0) & (y_val == 1)).float().sum().item()
                precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0.0
                recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0.0
            logging.info(
                f"epoch={epoch + 1} train_loss={loss.item():.4f} val_loss={val_loss:.4f} "
                f"val_acc={accuracy:.3f} val_precision={precision:.3f} val_recall={recall:.3f}"
            )
        model.eval()
        with torch.no_grad():
            val_probs = model(x_val)
            if loss_type == "focal":
                val_loss = _focal_loss(
                    val_probs,
                    y_val,
                    alpha=focal_alpha,
                    gamma=focal_gamma
                )
                val_loss = (val_loss * val_weights).mean().item()
            else:
                class_weights = torch.where(y_val == 1, pos_weight_tensor, torch.tensor(1.0))
                val_loss = (loss_fn(val_probs, y_val) * class_weights * val_weights).mean().item()
        val_losses.append(val_loss)

    return model, train_losses, val_losses


def train_predictor_with_split(
    features,
    target,
    train_idx,
    val_idx,
    outer_dim,
    epochs=50,
    learning_rate=0.01,
    loss_type="bce",
    focal_alpha=0.25,
    focal_gamma=2.0,
    sample_weights=None,
    class_weighting=False,
):
    x = torch.tensor(features.to_numpy(), dtype=torch.float32)
    y = torch.tensor(target.to_numpy(), dtype=torch.float32).unsqueeze(1)

    x_train, y_train = x[train_idx], y[train_idx]
    x_val, y_val = x[val_idx], y[val_idx]
    train_weights = None
    val_weights = None
    if sample_weights is not None:
        train_weights = sample_weights[train_idx].unsqueeze(1)
        val_weights = sample_weights[val_idx].unsqueeze(1)

    model, train_losses, val_losses = _train_with_split(
        x_train,
        y_train,
        x_val,
        y_val,
        outer_dim=outer_dim,
        epochs=epochs,
        learning_rate=learning_rate,
        loss_type=loss_type,
        focal_alpha=focal_alpha,
        focal_gamma=focal_gamma,
        train_weights=train_weights,
        val_weights=val_weights,
        class_weighting=class_weighting,
    )

    return model, train_losses, val_losses, x_train, y_train, x_val, y_val, train_idx, val_idx


def train_predictor(
    features,
    target,
    outer_dim,
    epochs=50,
    learning_rate=0.01,
    loss_type="bce",
    focal_alpha=0.25,
    focal_gamma=2.0,
    class_weighting=False,
):
    num_rows = features.shape[0]
    permutation = torch.randperm(num_rows)
    split_index = int(num_rows * 0.8)
    train_idx = permutation[:split_index]
    val_idx = permutation[split_index:]

    return train_predictor_with_split(
        features,
        target,
        train_idx,
        val_idx,
        outer_dim=outer_dim,
        epochs=epochs,
        learning_rate=learning_rate,
        loss_type=loss_type,
        focal_alpha=focal_alpha,
        focal_gamma=focal_gamma,
        class_weighting=class_weighting,
    )


def _env_name():
    env = os.environ.get('RAILS_ENV', '').strip().lower()
    if env in ('production', 'staging', 'development'):
        return env
    return 'development'


def _s3_bucket():
    mapping = {
        'production': 'breathesafe',
        'staging': 'breathesafe-staging',
        'development': 'breathesafe-development',
    }
    return mapping[_env_name()]


def _s3_region():
    return os.environ.get('S3_BUCKET_REGION') or os.environ.get('AWS_REGION') or 'us-east-1'


def _is_lambda_runtime():
    return bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))


def _images_output_dir():
    override = os.environ.get('MASK_RECOMMENDER_IMAGES_DIR')
    if override:
        if _is_lambda_runtime():
            normalized = override.strip()
            if normalized.startswith("python/") or normalized.startswith("./python/"):
                return "/tmp/mask_recommender/images"
        return override
    if _is_lambda_runtime():
        return "/tmp/mask_recommender/images"
    return "python/mask_recommender/images"


def _local_model_root():
    override = os.environ.get('MASK_RECOMMENDER_LOCAL_MODEL_DIR')
    if override:
        return override
    if _is_lambda_runtime():
        return "/tmp/mask_recommender/local_models"
    return "python/mask_recommender/local_models"


def _save_local_custom_artifacts(timestamp, params, metadata, mask_data):
    local_dir = Path(_local_model_root()) / str(timestamp)
    local_dir.mkdir(parents=True, exist_ok=True)

    params_path = local_dir / "custom_model_params.pt"
    metadata_path = local_dir / "custom_model_metadata.json"
    mask_data_path = local_dir / "custom_mask_data.json"

    torch.save(params, params_path)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    mask_data_path.write_text(json.dumps(mask_data, indent=2), encoding='utf-8')

    logging.info("Saved local custom artifacts to %s", local_dir)
    return local_dir


def _should_upload_visual_artifacts_to_s3():
    return _env_name() in ("staging", "production")


def _upload_visual_artifact(local_path, timestamp):
    key = f"mask_recommender/models/{timestamp}/{os.path.basename(local_path)}"
    return _upload_file_to_s3(local_path, key)


def _upload_file_to_s3(local_path, key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    profile = os.environ.get('AWS_PROFILE')
    logging.info(
        "S3 upload using bucket=%s region=%s profile=%s",
        bucket,
        _s3_region(),
        profile or "default"
    )
    s3.upload_file(local_path, bucket, key)
    return f"s3://{bucket}/{key}"


def _upload_json_to_s3(payload, key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    profile = os.environ.get('AWS_PROFILE')
    logging.info(
        "S3 upload using bucket=%s region=%s profile=%s",
        bucket,
        _s3_region(),
        profile or "default"
    )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload, indent=2).encode('utf-8'),
        ContentType='application/json'
    )
    return f"s3://{bucket}/{key}"


def _upload_png_bytes_to_s3(png_bytes, key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    profile = os.environ.get('AWS_PROFILE')
    logging.info(
        "S3 upload using bucket=%s region=%s profile=%s",
        bucket,
        _s3_region(),
        profile or "default"
    )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=png_bytes,
        ContentType='image/png'
    )
    return f"s3://{bucket}/{key}"


def _best_effort_visual_upload(upload_fn, artifact_name, fallback_artifact=None):
    """
    Visual/debug artifacts should not fail the entire training run.
    Model + metadata + metrics uploads remain strict.
    """
    try:
        return upload_fn()
    except (ClientError, OSError, RuntimeError, ValueError) as exc:
        logging.warning("Skipping %s upload due to error: %s", artifact_name, exc)
        return fallback_artifact


def _download_json_from_s3(key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    response = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response['Body'].read().decode('utf-8'))


def _download_state_dict_from_s3(key):
    bucket = _s3_bucket()
    s3 = boto3.client('s3', region_name=_s3_region())
    response = s3.get_object(Bucket=bucket, Key=key)
    return torch.load(io.BytesIO(response['Body'].read()), map_location='cpu')


def _load_previous_latest_nn_artifacts():
    latest_key = "mask_recommender/models/latest.json"
    latest_payload = _download_json_from_s3(latest_key)
    metadata = _download_json_from_s3(latest_payload['metadata_key'])
    state_dict = _download_state_dict_from_s3(latest_payload['model_key'])
    return {
        'latest': latest_payload,
        'metadata': metadata,
        'state_dict': state_dict,
    }


def _probe_payloads(base_url=None):
    probe_user_ids_raw = os.environ.get('MASK_RECOMMENDER_PROBE_USER_IDS')
    if probe_user_ids_raw:
        email = os.getenv('BREATHESAFE_SERVICE_EMAIL')
        password = os.getenv('BREATHESAFE_SERVICE_PASSWORD')
        if not email or not password:
            raise ValueError(
                "MASK_RECOMMENDER_PROBE_USER_IDS requires BREATHESAFE_SERVICE_EMAIL and "
                "BREATHESAFE_SERVICE_PASSWORD."
            )
        probe_user_ids = [
            int(value.strip())
            for value in probe_user_ids_raw.split(',')
            if value.strip()
        ]
        resolved_base_url = (base_url or os.environ.get('BREATHESAFE_BASE_URL') or 'http://localhost:3000').rstrip('/')
        session = build_session(None)
        login_with_credentials(session, resolved_base_url, email, password)
        try:
            probes = []
            for user_id in probe_user_ids:
                payload = fetch_json(
                    session,
                    f"{resolved_base_url}/mask_recommender/recommender_user_measurements.json"
                    f"?recommender_user_id={user_id}"
                )
                facial_measurements = payload.get('facial_measurements') or {}
                if not facial_measurements:
                    continue
                probes.append({
                    'label': f"user_{user_id}",
                    'facial_measurements': {
                        column: float(facial_measurements.get(column, 0) or 0)
                        for column in TARGET_COLUMNS
                    } | {
                        'facial_hair_beard_length_mm': float(
                            facial_measurements.get('facial_hair_beard_length_mm', 0) or 0
                        )
                    },
                    'user_id': user_id,
                })
        finally:
            logout(session, resolved_base_url)
        if probes:
            return probes

    raw = os.environ.get('MASK_RECOMMENDER_PROBES_JSON')
    if not raw:
        return DEFAULT_PROBE_PAYLOADS

    payload = json.loads(raw)
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        raise ValueError("MASK_RECOMMENDER_PROBES_JSON must decode to a list or object.")
    return payload


def _build_model_from_state_dict(state_dict):
    linear_specs = []
    for key, value in state_dict.items():
        if not key.endswith('.weight'):
            continue
        layer_token = key.split('.')[0]
        if not layer_token.isdigit() or value.ndim != 2:
            continue
        linear_specs.append((int(layer_token), int(value.shape[1]), int(value.shape[0])))
    linear_specs.sort(key=lambda item: item[0])
    if len(linear_specs) < 2:
        raise RuntimeError("Unexpected model format; unable to infer linear layers.")

    layers = []
    for idx, (_, in_features, out_features) in enumerate(linear_specs):
        layers.append(torch.nn.Linear(in_features, out_features))
        if idx < len(linear_specs) - 1:
            layers.append(torch.nn.ReLU())

    model = torch.nn.Sequential(*layers)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def _predict_probe_probabilities(
    model,
    facial_measurements,
    mask_candidates,
    feature_columns,
    categorical_columns,
    mask_empirical_priors=None,
    use_facial_perimeter=False,
    use_diff_perimeter_bins=False,
    use_diff_perimeter_mask_bins=False,
    zscore_stats=None,
):
    probe_frame = pd.DataFrame(
        {
            'mask_id': mask_candidates['mask_id'].to_numpy(),
            'perimeter_mm': mask_candidates['perimeter_mm'].to_numpy(),
            'facial_hair_beard_length_mm': facial_measurements.get('facial_hair_beard_length_mm', 0) or 0,
            'strap_type': mask_candidates['strap_type'].to_numpy(),
            'style': mask_candidates['style'].to_numpy(),
            'brand_model': mask_candidates['brand_model'].to_numpy(),
            'unique_internal_model_code': mask_candidates['unique_internal_model_code'].to_numpy(),
        }
    )
    for column in FACIAL_FEATURE_COLUMNS:
        probe_frame[column] = facial_measurements.get(column, 0) or 0
    probe_frame = add_mask_empirical_prior_features(probe_frame, mask_empirical_priors or {})

    encoded = build_feature_frame(
        probe_frame,
        feature_columns=feature_columns,
        categorical_columns=categorical_columns,
        use_facial_perimeter=use_facial_perimeter,
        use_diff_perimeter_bins=use_diff_perimeter_bins,
        use_diff_perimeter_mask_bins=use_diff_perimeter_mask_bins
    )
    if zscore_stats:
        encoded = apply_zscore(encoded, zscore_stats)

    x_probe = torch.tensor(encoded.to_numpy(), dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        probs = model(x_probe).squeeze().cpu().numpy()

    rows = []
    for idx, mask_row in mask_candidates.reset_index(drop=True).iterrows():
        rows.append({
            'mask_id': int(mask_row['id']),
            'unique_internal_model_code': mask_row.get('unique_internal_model_code', ''),
            'brand_model': mask_row.get('brand_model', ''),
            'style': mask_row.get('style', ''),
            'strap_type': mask_row.get('strap_type', ''),
            'probability_of_fit': float(probs[idx]),
        })
    rows.sort(key=lambda row: row['probability_of_fit'], reverse=True)
    return rows


def _build_probe_diagnostics(
    model,
    mask_candidates,
    feature_columns,
    categorical_columns,
    args,
    zscore_stats,
    mask_empirical_priors,
):
    probes = _probe_payloads()
    previous_artifacts = None
    previous_error = None
    try:
        previous_artifacts = _load_previous_latest_nn_artifacts()
    except (ClientError, OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        previous_error = str(exc)

    previous_model = None
    previous_metadata = None
    if previous_artifacts is not None:
        previous_model = _build_model_from_state_dict(previous_artifacts['state_dict'])
        previous_metadata = previous_artifacts['metadata']

    diagnostics = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'previous_model_timestamp': previous_artifacts['latest'].get('timestamp') if previous_artifacts else None,
        'previous_model_error': previous_error,
        'probes': [],
    }

    for probe in probes:
        label = probe.get('label') or f"probe_{len(diagnostics['probes']) + 1}"
        facial_measurements = probe.get('facial_measurements') or {}
        current_rows = _predict_probe_probabilities(
            model,
            facial_measurements,
            mask_candidates,
            feature_columns,
            categorical_columns,
            mask_empirical_priors=mask_empirical_priors,
            use_facial_perimeter=args.use_facial_perimeter,
            use_diff_perimeter_bins=args.use_diff_perimeter_bins,
            use_diff_perimeter_mask_bins=args.use_diff_perimeter_mask_bins,
            zscore_stats=zscore_stats,
        )
        probe_payload = {
            'label': label,
            'facial_measurements': facial_measurements,
            'current_top_recommendations': current_rows[:25],
        }

        if previous_model is not None and previous_metadata is not None:
            previous_rows = _predict_probe_probabilities(
                previous_model,
                facial_measurements,
                mask_candidates,
                previous_metadata['feature_columns'],
                previous_metadata['categorical_columns'],
                mask_empirical_priors=mask_empirical_priors,
                use_facial_perimeter=previous_metadata.get('use_facial_perimeter', False),
                use_diff_perimeter_bins=previous_metadata.get('use_diff_perimeter_bins', False),
                use_diff_perimeter_mask_bins=previous_metadata.get('use_diff_perimeter_mask_bins', False),
                zscore_stats=previous_metadata.get('zscore_stats', {}) if previous_metadata.get('zscore') else {},
            )
            previous_by_id = {row['mask_id']: row for row in previous_rows}
            current_by_id = {row['mask_id']: row for row in current_rows}
            deltas = []
            for mask_id, current_row in current_by_id.items():
                previous_row = previous_by_id.get(mask_id)
                previous_prob = previous_row['probability_of_fit'] if previous_row else None
                delta = None if previous_prob is None else current_row['probability_of_fit'] - previous_prob
                deltas.append({
                    'mask_id': mask_id,
                    'unique_internal_model_code': current_row['unique_internal_model_code'],
                    'brand_model': current_row['brand_model'],
                    'style': current_row['style'],
                    'strap_type': current_row['strap_type'],
                    'current_probability_of_fit': current_row['probability_of_fit'],
                    'previous_probability_of_fit': previous_prob,
                    'delta_probability_of_fit': delta,
                })

            delta_rows = [row for row in deltas if row['delta_probability_of_fit'] is not None]
            delta_rows.sort(key=lambda row: row['delta_probability_of_fit'])
            probe_payload['largest_probability_drops'] = delta_rows[:25]
            probe_payload['largest_probability_gains'] = list(reversed(delta_rows[-25:]))
            watchlist = []
            for family in PROBE_WATCHLIST_FAMILIES:
                matching = [
                    row for row in deltas
                    if family in str(row['unique_internal_model_code']).lower()
                    or family in str(row['brand_model']).lower()
                ]
                if not matching:
                    continue
                matching_with_delta = [row for row in matching if row['delta_probability_of_fit'] is not None]
                watchlist.append({
                    'family': family,
                    'count': len(matching),
                    'max_current_probability_of_fit': max(row['current_probability_of_fit'] for row in matching),
                    'max_previous_probability_of_fit': (
                        max(row['previous_probability_of_fit'] for row in matching_with_delta)
                        if matching_with_delta else None
                    ),
                    'largest_gain': (
                        max(row['delta_probability_of_fit'] for row in matching_with_delta)
                        if matching_with_delta else None
                    ),
                    'largest_drop': (
                        min(row['delta_probability_of_fit'] for row in matching_with_delta)
                        if matching_with_delta else None
                    ),
                    'top_current_masks': sorted(
                        matching,
                        key=lambda row: row['current_probability_of_fit'],
                        reverse=True
                    )[:5],
                })
            probe_payload['watchlist_families'] = watchlist

        diagnostics['probes'].append(probe_payload)

    return diagnostics


def calc_preds(data, params):
    resolved_params = _resolve_custom_lr_parameter_views(params)
    fit_tests_by_mask_specific_parameters = data['fit_tests_by_masks'] @ resolved_params['mask_specific_parameters']
    fit_tests_by_style_specific_parameters = data['fit_tests_by_styles'] @ resolved_params['style_specific_parameters']
    fit_tests_by_mask_and_style_specific_parameters = fit_tests_by_mask_specific_parameters + fit_tests_by_style_specific_parameters

    fit_tests_by_facial_feature_fit = fit_tests_by_mask_and_style_specific_parameters * data['perimeter_diffs']
    fit_tests_by_strap_specific_parameters = data['fit_tests_by_strap_types'] @ resolved_params['strap_specific_parameters']

    logits = fit_tests_by_strap_specific_parameters + fit_tests_by_facial_feature_fit.sum(axis=1).reshape(-1, 1)

    return torch.sigmoid(logits)


def _fit_family_key_series(frame):
    working = frame.copy()
    if 'fit_family_id' in working.columns:
        fit_family_ids = pd.to_numeric(working['fit_family_id'], errors='coerce')
    else:
        fit_family_ids = pd.Series(np.nan, index=working.index, dtype=np.float32)

    if 'mask_id' in working.columns:
        mask_ids = pd.to_numeric(working['mask_id'], errors='coerce')
    else:
        mask_ids = pd.Series(np.nan, index=working.index, dtype=np.float32)

    fallback_ids = fit_family_ids.fillna(mask_ids)
    fallback_ids = fallback_ids.apply(
        lambda value: str(int(value)) if pd.notna(value) else None
    )
    if 'unique_internal_model_code' in working.columns:
        fallback_codes = working['unique_internal_model_code'].fillna('').astype(str)
    else:
        fallback_codes = pd.Series('', index=working.index, dtype=str)
    fallback_codes = fallback_codes.where(fallback_codes != '', 'unknown-fit-family')
    return fallback_ids.fillna(fallback_codes)


def _custom_lr_mask_categories(category_metadata):
    categories = category_metadata.get('fit_family_categories')
    if categories:
        return categories
    return category_metadata.get('mask_code_categories', [])


def prep_data_in_torch(cleaned_fit_tests):
    mask_categories = sorted(_fit_family_key_series(cleaned_fit_tests).dropna().unique())
    style_categories = sorted(cleaned_fit_tests['style'].dropna().unique())
    strap_categories = sorted(cleaned_fit_tests['strap_type'].dropna().unique())
    return prep_data_in_torch_with_categories(
        cleaned_fit_tests,
        mask_categories=mask_categories,
        style_categories=style_categories,
        strap_categories=strap_categories,
    )


def prep_data_in_torch_with_categories(
    frame,
    mask_categories,
    style_categories,
    strap_categories,
):
    frame = frame.copy()
    frame['fit_family_key'] = _fit_family_key_series(frame)
    if 'perimeter_diff' not in frame.columns:
        facial_perimeter_cm = frame[FACIAL_MEASUREMENTS].sum(axis=1).astype(np.float32) / 10.0
        mask_perimeter_cm = pd.to_numeric(frame.get('perimeter_mm', 0), errors='coerce').fillna(0).astype(np.float32) / 10.0
        frame['perimeter_diff'] = facial_perimeter_cm - mask_perimeter_cm
    if 'perimeter_diff_sq' not in frame.columns:
        frame['perimeter_diff_sq'] = pd.to_numeric(frame['perimeter_diff'], errors='coerce').fillna(0).astype(np.float32) ** 2

    fit_tests_by_strap_types = torch.from_numpy(
        pd.get_dummies(
            pd.Categorical(frame['strap_type'], categories=strap_categories)
        ).astype(np.float32).to_numpy()
    )

    facial_perimeter_cm_t = torch.from_numpy(
        frame[FACIAL_MEASUREMENTS].sum(axis=1).to_numpy(dtype=np.float32)
    ).reshape(-1, 1) / 10.0
    perimeter_diff_cm_t = torch.from_numpy(
        frame['perimeter_diff'].to_numpy(dtype=np.float32)
    ).reshape(-1, 1)
    perimeter_diff_cm_sq_t = torch.from_numpy(
        frame['perimeter_diff_sq'].to_numpy(dtype=np.float32)
    ).reshape(-1, 1)
    ones = torch.ones((perimeter_diff_cm_t.shape[0], 1), dtype=torch.float32)
    perimeter_diffs = torch.concat([perimeter_diff_cm_sq_t, perimeter_diff_cm_t, ones], axis=1)

    fit_tests_by_masks = torch.from_numpy(
        pd.get_dummies(
            pd.Categorical(frame['fit_family_key'], categories=mask_categories)
        ).astype(np.float32).to_numpy()
    )
    fit_tests_by_styles = torch.from_numpy(
        pd.get_dummies(
            pd.Categorical(frame['style'], categories=style_categories)
        ).astype(np.float32).to_numpy()
    )

    data = {
        'fit_tests_by_masks': fit_tests_by_masks,
        'fit_tests_by_styles': fit_tests_by_styles,
        'fit_tests_by_strap_types': fit_tests_by_strap_types,
        'perimeter_diffs': perimeter_diffs,
        'facial_perimeter_cm': facial_perimeter_cm_t,
    }

    return data


def _custom_lr_category_metadata(cleaned_fit_tests):
    return {
        'fit_family_categories': sorted(_fit_family_key_series(cleaned_fit_tests).dropna().unique().tolist()),
        'style_categories': sorted(cleaned_fit_tests['style'].dropna().unique().tolist()),
        'strap_type_categories': sorted(cleaned_fit_tests['strap_type'].dropna().unique().tolist()),
    }


def _subset_custom_lr_data(data, row_indices):
    if isinstance(row_indices, torch.Tensor):
        row_indices = row_indices.detach().cpu().long()
    else:
        row_indices = torch.tensor(row_indices, dtype=torch.long)
    return {
        key: value[row_indices]
        for key, value in data.items()
    }


def _initialize_custom_lr_parameters(category_metadata):
    mask_count = len(_custom_lr_mask_categories(category_metadata))
    style_count = len(category_metadata['style_categories'])
    strap_count = len(category_metadata['strap_type_categories'])

    return {
        'alpha_mask_raw': torch.full((mask_count, 1), -5.0, dtype=torch.float32, requires_grad=True),
        'beta_gamma_mask': torch.rand((mask_count, 2), dtype=torch.float32, requires_grad=True),
        'alpha_style_raw': torch.zeros((style_count, 1), dtype=torch.float32, requires_grad=True),
        'beta_gamma_style': torch.rand((style_count, 2), dtype=torch.float32, requires_grad=True),
        'strap_specific_parameters': (torch.rand((strap_count, 1), dtype=torch.float32) - 0.5).requires_grad_(),
    }


def _detach_custom_lr_parameters(parameters):
    return {
        key: value.detach().cpu()
        for key, value in parameters.items()
    }


def _resolve_custom_lr_parameter_views(params):
    if 'mask_specific_parameters' in params and 'style_specific_parameters' in params:
        return params

    mask_specific_parameters = torch.concat(
        [
            -torch.exp(params['alpha_mask_raw']),
            params['beta_gamma_mask']
        ],
        axis=1
    )
    style_specific_parameters = torch.concat(
        [
            -torch.exp(params['alpha_style_raw']),
            params['beta_gamma_style']
        ],
        axis=1
    )
    return {
        'mask_specific_parameters': mask_specific_parameters,
        'style_specific_parameters': style_specific_parameters,
        'strap_specific_parameters': params['strap_specific_parameters'],
    }


def _predict_custom_lr_probabilities(frame, parameters, category_metadata):
    data = prep_data_in_torch_with_categories(
        frame,
        mask_categories=_custom_lr_mask_categories(category_metadata),
        style_categories=category_metadata['style_categories'],
        strap_categories=category_metadata['strap_type_categories'],
    )
    with torch.no_grad():
        return calc_preds(data, parameters).squeeze(1).cpu().numpy()


def _custom_lr_params_with_zeroed_mask(parameters, mask_identity, category_metadata):
    cloned = {
        key: value.detach().clone()
        for key, value in _resolve_custom_lr_parameter_views(parameters).items()
    }
    try:
        mask_idx = _custom_lr_mask_categories(category_metadata).index(mask_identity)
    except ValueError:
        return cloned
    cloned['mask_specific_parameters'][mask_idx] = torch.zeros_like(cloned['mask_specific_parameters'][mask_idx])
    return cloned


def _mask_perimeter_mm_from_training_row(row):
    raw_perimeter_mm = pd.to_numeric(row.get('perimeter_mm'), errors='coerce')
    if pd.notna(raw_perimeter_mm):
        return float(raw_perimeter_mm)

    facial_perimeter_mm = sum(float(row.get(column, 0) or 0) for column in FACIAL_MEASUREMENTS)
    perimeter_diff_cm = pd.to_numeric(row.get('perimeter_diff'), errors='coerce')
    if pd.notna(perimeter_diff_cm):
        return float(facial_perimeter_mm - (float(perimeter_diff_cm) * 10.0))

    return float(facial_perimeter_mm)


def _build_custom_lr_perimeter_diff_diagnostics(
    cleaned_fit_tests,
    parameters,
    category_metadata,
    timestamp,
    mask_data=None,
    base_url=None,
):
    if cleaned_fit_tests.empty:
        return []

    images_dir = _images_output_dir()
    os.makedirs(images_dir, exist_ok=True)

    observed_min = float(pd.to_numeric(cleaned_fit_tests['perimeter_diff'], errors='coerce').min())
    observed_max = float(pd.to_numeric(cleaned_fit_tests['perimeter_diff'], errors='coerce').max())
    if not np.isfinite(observed_min) or not np.isfinite(observed_max):
        return []
    if observed_min == observed_max:
        observed_min -= 1.0
        observed_max += 1.0
    sort_columns = ['unique_internal_model_code']
    if 'created_at' in cleaned_fit_tests.columns:
        sort_columns.append('created_at')
    grouped = (
        cleaned_fit_tests
        .sort_values(sort_columns)
        .groupby('unique_internal_model_code', sort=True)
    )
    mask_codes = list(grouped.groups.keys())
    if not mask_codes:
        return []

    artifact_paths = []
    probe_point_rows = []
    per_page = 16
    num_pages = int(np.ceil(len(mask_codes) / per_page))
    probes = _probe_payloads(base_url=base_url)
    probe_colors = ['#111111', '#7a3cff', '#118ab2', '#ef476f', '#2a9d8f', '#bc6c25']

    for page_idx in range(num_pages):
        page_codes = mask_codes[page_idx * per_page:(page_idx + 1) * per_page]
        fig, axes = plt.subplots(4, 4, figsize=(20, 16), sharex=False, sharey=True)
        axes = axes.flatten()

        for ax_idx, mask_code in enumerate(page_codes):
            ax = axes[ax_idx]
            rows = grouped.get_group(mask_code).copy()
            representative = rows.iloc[-1]
            live_mask = None
            representative_mask_id = pd.to_numeric(representative.get('mask_id'), errors='coerce')
            if mask_data and pd.notna(representative_mask_id):
                live_mask = mask_data.get(str(int(representative_mask_id)))

            style = (live_mask or {}).get('style') or representative['style']
            strap_type = (live_mask or {}).get('strap_type') or representative['strap_type']
            fit_family_key = _fit_family_key_series(pd.DataFrame([representative])).iloc[0]
            live_perimeter_mm = pd.to_numeric((live_mask or {}).get('perimeter_mm'), errors='coerce')
            if pd.notna(live_perimeter_mm):
                mask_perimeter_mm = float(live_perimeter_mm)
            else:
                mask_perimeter_mm = _mask_perimeter_mm_from_training_row(representative)
            probe_positions = []
            for probe in probes:
                facial_measurements = probe.get('facial_measurements') or {}
                facial_perimeter_mm = sum(float(facial_measurements.get(column, 0) or 0) for column in FACIAL_MEASUREMENTS)
                probe_positions.append((facial_perimeter_mm - mask_perimeter_mm) / 10.0)

            row_diffs = pd.to_numeric(rows['perimeter_diff'], errors='coerce')
            row_min = float(row_diffs.min()) if row_diffs.notna().any() else observed_min
            row_max = float(row_diffs.max()) if row_diffs.notna().any() else observed_max
            subplot_min = min([observed_min, row_min] + probe_positions)
            subplot_max = max([observed_max, row_max] + probe_positions)
            if subplot_min == subplot_max:
                subplot_min -= 1.0
                subplot_max += 1.0
            subplot_padding = max(0.5, (subplot_max - subplot_min) * 0.05)
            subplot_min -= subplot_padding
            subplot_max += subplot_padding
            diff_values = np.linspace(subplot_min, subplot_max, 200, dtype=np.float32)

            curve_frame = pd.DataFrame({
                'unique_internal_model_code': [mask_code] * len(diff_values),
                'fit_family_id': [(live_mask or {}).get('fit_family_id', representative.get('fit_family_id'))] * len(diff_values),
                'style': [style] * len(diff_values),
                'strap_type': [strap_type] * len(diff_values),
                'perimeter_diff': diff_values,
                'perimeter_diff_sq': diff_values ** 2,
                'perimeter_mm': np.zeros(len(diff_values), dtype=np.float32),
                'facial_hair_beard_length_mm': np.zeros(len(diff_values), dtype=np.float32),
            })
            for column in FACIAL_MEASUREMENTS:
                curve_frame[column] = np.zeros(len(diff_values), dtype=np.float32)

            specific_probs = _predict_custom_lr_probabilities(
                curve_frame,
                parameters=parameters,
                category_metadata=category_metadata,
            )
            generic_probs = _predict_custom_lr_probabilities(
                curve_frame,
                parameters=_custom_lr_params_with_zeroed_mask(parameters, fit_family_key, category_metadata),
                category_metadata=category_metadata,
            )

            ax.plot(diff_values, specific_probs, label='mask-specific', color='#1f77b4', linewidth=2)
            ax.plot(diff_values, generic_probs, label='style-only', color='#ff7f0e', linewidth=2, linestyle='--')

            row_labels = pd.to_numeric(rows['qlft_pass_normalized'], errors='coerce')
            pass_mask = row_labels == 1
            fail_mask = row_labels == 0
            if pass_mask.any():
                ax.scatter(
                    row_diffs[pass_mask],
                    row_labels[pass_mask],
                    color='green',
                    alpha=0.5,
                    s=26,
                    label='pass',
                )
            if fail_mask.any():
                ax.scatter(
                    row_diffs[fail_mask],
                    row_labels[fail_mask],
                    color='red',
                    alpha=0.5,
                    s=26,
                    label='fail',
                )

            strap_type_value = representative['strap_type']
            style_value = representative['style']
            for probe_idx, probe in enumerate(probes):
                facial_measurements = probe.get('facial_measurements') or {}
                probe_label = probe.get('label') or f"probe_{probe_idx + 1}"
                facial_perimeter_mm = sum(float(facial_measurements.get(column, 0) or 0) for column in FACIAL_MEASUREMENTS)
                probe_diff_cm = (facial_perimeter_mm - mask_perimeter_mm) / 10.0
                probe_color = probe_colors[probe_idx % len(probe_colors)]
                ax.axvspan(
                    probe_diff_cm - 0.08,
                    probe_diff_cm + 0.08,
                    color=probe_color,
                    alpha=0.14,
                    zorder=1,
                )
                ax.axvline(
                    probe_diff_cm,
                    color=probe_color,
                    linestyle='-',
                    linewidth=2.4,
                    alpha=0.95,
                    zorder=2,
                )
                probe_frame = pd.DataFrame({
                    'unique_internal_model_code': [mask_code],
                    'fit_family_id': [(live_mask or {}).get('fit_family_id', representative.get('fit_family_id'))],
                    'style': [style_value],
                    'strap_type': [strap_type_value],
                    'perimeter_mm': [mask_perimeter_mm],
                    'facial_hair_beard_length_mm': [facial_measurements.get('facial_hair_beard_length_mm', 0) or 0],
                })
                for column in FACIAL_MEASUREMENTS:
                    probe_frame[column] = [facial_measurements.get(column, 0) or 0]
                probe_probability = float(
                    _predict_custom_lr_probabilities(
                        probe_frame,
                        parameters=parameters,
                        category_metadata=category_metadata,
                    )[0]
                )
                ax.scatter(
                    [probe_diff_cm],
                    [probe_probability],
                    color=probe_color,
                    edgecolors='black',
                    linewidths=1.2,
                    s=90,
                    marker='X',
                    zorder=10,
                )
                annotation_y = min(0.97, max(0.03, probe_probability + 0.06))
                annotation_va = 'bottom' if annotation_y >= probe_probability else 'top'
                ax.annotate(
                    f"{probe_label}: {probe_probability:.0%}",
                    xy=(probe_diff_cm, probe_probability),
                    xytext=(probe_diff_cm + 0.15, annotation_y),
                    textcoords='data',
                    fontsize=7,
                    color=probe_color,
                    fontweight='bold',
                    ha='left',
                    va=annotation_va,
                    bbox={
                        'boxstyle': 'round,pad=0.2',
                        'fc': 'white',
                        'ec': probe_color,
                        'alpha': 0.9,
                    },
                    arrowprops={
                        'arrowstyle': '-',
                        'color': probe_color,
                        'lw': 1.0,
                        'alpha': 0.9,
                    },
                    zorder=11,
                )
                probe_point_rows.append({
                    'page': page_idx + 1,
                    'mask_code': mask_code,
                    'probe_label': probe_label,
                    'probe_perimeter_diff_cm': probe_diff_cm,
                    'probe_probability_of_fit': probe_probability,
                })

                xticks = list(ax.get_xticks())
                xticks.append(probe_diff_cm)
                finite_xticks = []
                for x in xticks:
                    try:
                        x_value = float(x)
                    except (TypeError, ValueError):
                        continue
                    if np.isfinite(x_value):
                        finite_xticks.append(round(x_value, 2))
                if finite_xticks:
                    ax.set_xticks(sorted(set(finite_xticks)))
                ax.text(
                    0.02,
                    0.98 - (probe_idx * 0.09),
                    f"{probe_label}: x={probe_diff_cm:.2f}, p={probe_probability:.0%}",
                    transform=ax.transAxes,
                    ha='left',
                    va='top',
                    fontsize=7,
                    color=probe_color,
                    bbox={
                        'boxstyle': 'round,pad=0.2',
                        'fc': 'white',
                        'ec': probe_color,
                        'alpha': 0.9,
                    },
                    zorder=12,
                )

            ax.set_title(mask_code, fontsize=9)
            ax.set_xlim(subplot_min, subplot_max)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, linestyle='--', alpha=0.25)

        for unused_ax in axes[len(page_codes):]:
            unused_ax.axis('off')

        legend_handles = [
            Line2D([0], [0], color='#1f77b4', linewidth=2, label='mask-specific'),
            Line2D([0], [0], color='#ff7f0e', linewidth=2, linestyle='--', label='style-only'),
            Line2D([0], [0], marker='o', color='green', linestyle='None', alpha=0.5, markersize=6, label='pass'),
            Line2D([0], [0], marker='o', color='red', linestyle='None', alpha=0.5, markersize=6, label='fail'),
        ]
        for probe_idx, probe in enumerate(probes):
            probe_label = probe.get('label') or f"probe_{probe_idx + 1}"
            probe_color = probe_colors[probe_idx % len(probe_colors)]
            legend_handles.append(
                Line2D(
                    [0], [0],
                    color=probe_color,
                    linestyle='-',
                    linewidth=2.4,
                    marker='o',
                    markersize=5,
                    label=f'{probe_label} actual'
                )
            )
        if legend_handles:
            fig.legend(
                handles=legend_handles,
                loc='upper center',
                bbox_to_anchor=(0.5, 0.965),
                ncol=min(4, len(legend_handles)),
                frameon=False,
            )
        fig.supxlabel('perimeter_diff')
        fig.supylabel('probability / actual qlft pass')
        fig.suptitle(
            f'Custom LR perimeter_diff diagnostics (page {page_idx + 1}/{num_pages})',
            y=0.992
        )
        fig.tight_layout(rect=[0, 0, 1, 0.88])

        output_path = os.path.join(
            images_dir,
            f"{timestamp}_custom_perimeter_diff_diagnostics_page_{page_idx + 1}.png"
        )
        if _should_upload_visual_artifacts_to_s3():
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            output_key = (
                f"mask_recommender/models/{timestamp}/"
                f"{timestamp}_custom_perimeter_diff_diagnostics_page_{page_idx + 1}.png"
            )
            uploaded_uri = _best_effort_visual_upload(
                lambda: _upload_png_bytes_to_s3(buf.getvalue(), output_key),
                f"custom perimeter diff diagnostics page {page_idx + 1}",
                fallback_artifact=None,
            )
            if uploaded_uri:
                artifact_paths.append(uploaded_uri)
        else:
            fig.savefig(output_path)
            logging.info("Saved custom perimeter diff diagnostics to %s", output_path)
            artifact_paths.append(output_path)
        plt.close(fig)

    probe_points_path = os.path.join(images_dir, f"{timestamp}_custom_perimeter_diff_probe_points.json")
    if _should_upload_visual_artifacts_to_s3():
        probe_points_key = f"mask_recommender/models/{timestamp}/{timestamp}_custom_perimeter_diff_probe_points.json"
        _best_effort_visual_upload(
            lambda: _upload_json_to_s3(probe_point_rows, probe_points_key),
            "custom perimeter diff probe points",
            fallback_artifact=None,
        )
    else:
        with open(probe_points_path, 'w', encoding='utf-8') as handle:
            json.dump(probe_point_rows, handle, indent=2)
        logging.info("Saved custom perimeter diff probe points to %s", probe_points_path)

    return artifact_paths


def train_custom_lr_with_split(
    cleaned_fit_tests,
    train_idx,
    val_idx,
    category_metadata,
    epochs=50,
    learning_rate=0.01,
    class_weighting=False,
):
    data = prep_data_in_torch_with_categories(
        cleaned_fit_tests,
        mask_categories=_custom_lr_mask_categories(category_metadata),
        style_categories=category_metadata['style_categories'],
        strap_categories=category_metadata['strap_type_categories'],
    )
    target = torch.tensor(
        pd.to_numeric(cleaned_fit_tests['qlft_pass_normalized'], errors='coerce').fillna(0).to_numpy(dtype=np.float32)
    ).reshape(-1, 1)

    train_data = _subset_custom_lr_data(data, train_idx)
    val_data = _subset_custom_lr_data(data, val_idx)
    y_train = target[train_idx]
    y_val = target[val_idx]

    params = _initialize_custom_lr_parameters(category_metadata)
    optimizer = torch.optim.Adam(list(params.values()), lr=learning_rate)
    loss_fn = torch.nn.BCELoss(reduction='none')
    train_losses = []
    val_losses = []

    pos_count = float(y_train.sum().item())
    neg_count = float((1 - y_train).sum().item())
    pos_weight = (neg_count / pos_count) if pos_count > 0 else 1.0
    pos_weight_tensor = torch.tensor(pos_weight, dtype=torch.float32)

    logging.info(
        "Custom LR balance: train_pos_rate=%.3f val_pos_rate=%.3f pos_weight=%.3f",
        float(y_train.mean().item()) if y_train.numel() else 0.0,
        float(y_val.mean().item()) if y_val.numel() else 0.0,
        pos_weight,
    )
    if class_weighting:
        logging.info("Class weighting enabled.")

    for epoch in range(epochs):
        optimizer.zero_grad()
        train_probs = calc_preds(train_data, params)
        if class_weighting:
            class_weights = torch.where(y_train == 1, pos_weight_tensor, torch.tensor(1.0, dtype=torch.float32))
        else:
            class_weights = torch.ones_like(y_train)
        loss = (loss_fn(train_probs, y_train) * class_weights).mean()
        loss.backward()
        optimizer.step()
        train_losses.append(float(loss.item()))

        with torch.no_grad():
            val_probs = calc_preds(val_data, params)
            if class_weighting:
                val_class_weights = torch.where(y_val == 1, pos_weight_tensor, torch.tensor(1.0, dtype=torch.float32))
            else:
                val_class_weights = torch.ones_like(y_val)
            val_loss = (loss_fn(val_probs, y_val) * val_class_weights).mean().item()
            val_losses.append(float(val_loss))
            if (epoch + 1) % 10 == 0 or epoch == 0:
                preds = (val_probs >= 0.5).float()
                accuracy = (preds == y_val).float().mean().item()
                true_pos = ((preds == 1) & (y_val == 1)).float().sum().item()
                false_pos = ((preds == 1) & (y_val == 0)).float().sum().item()
                false_neg = ((preds == 0) & (y_val == 1)).float().sum().item()
                precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0.0
                recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0.0
                logging.info(
                    "custom_lr epoch=%s train_loss=%.4f val_loss=%.4f val_acc=%.3f val_precision=%.3f val_recall=%.3f",
                    epoch + 1,
                    float(loss.item()),
                    float(val_loss),
                    accuracy,
                    precision,
                    recall,
                )

    with torch.no_grad():
        final_train_probs = calc_preds(train_data, params).squeeze(1).cpu().numpy()
        final_val_probs = calc_preds(val_data, params).squeeze(1).cpu().numpy()

    return {
        'params': _detach_custom_lr_parameters(params),
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_probs': final_train_probs,
        'val_probs': final_val_probs,
        'y_train': y_train.squeeze(1).cpu().numpy(),
        'y_val': y_val.squeeze(1).cpu().numpy(),
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description='Train fit predictor model.')
    parser.add_argument('--epochs', type=int, default=600, help='Number of training epochs.')
    parser.add_argument('--learning-rate', type=float, default=0.00005, help='Learning rate for optimizer.')
    parser.add_argument('--model-type', default='custom_lr', choices=['custom_lr'], help='Model type to train.')
    parser.add_argument('--loss-plot', default='python/mask_recommender/training_loss.png', help='Path to save training loss plot.')
    parser.add_argument('--class-reweight', action='store_true', help='Reweight loss by class balance.')
    parser.add_argument(
        '--retrain-with-full',
        action='store_true',
        dest='retrain_with_full',
        help='After split metrics, retrain from scratch on the full dataset before saving artifacts.',
    )
    parser.add_argument(
        '--no-retrain-with-full',
        action='store_false',
        dest='retrain_with_full',
        help='Disable full-dataset retraining before artifact save.',
    )
    parser.set_defaults(retrain_with_full=True)
    args = parser.parse_args(argv)
    # [ ] Get a table of users and facial features
    # [ ] Get a table of masks and perimeters

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    base_url = os.environ.get('BREATHESAFE_BASE_URL', 'http://localhost:3000')
    masks_url = f"{base_url}/masks.json?per_page=1000"

    session = build_session(None)
    fit_tests_payload = fetch_facial_measurements_fit_tests(
        base_url=base_url,
        session=session,
    )
    fit_tests_df = pd.DataFrame(fit_tests_payload)

    masks_df = get_masks(session, masks_url)
    mask_candidates = build_mask_candidates(masks_df)
    model_config = TrainModelConfig(
        outer_dim=_set_num_masks_times_num_bins_plus_other_features(mask_candidates)
    )
    logging.info(
        "num_masks_times_num_bins_plus_other_features=%s",
        model_config.outer_dim
    )
    email = os.getenv('BREATHESAFE_SERVICE_EMAIL')
    password = os.getenv('BREATHESAFE_SERVICE_PASSWORD')

    fit_tests_with_imputed_arkit_via_traditional_facial_measurements = predict_arkit_from_traditional(
        base_url=base_url,
        email=email,
        password=password
    )

    missing_facial_measurement_id = fit_tests_with_imputed_arkit_via_traditional_facial_measurements['facial_measurement_id'].isna().sum()
    total_num_fit_tests = fit_tests_with_imputed_arkit_via_traditional_facial_measurements.shape[0]

    logging.info(f"Fit tests with qlft_pass not nil missing facial_measurement_id: {missing_facial_measurement_id} / {total_num_fit_tests}: {display_percentage(missing_facial_measurement_id, total_num_fit_tests)}")

    total_fit_tests_missing_style = fit_tests_with_imputed_arkit_via_traditional_facial_measurements['style'].isna().sum()
    logging.info(f"Total # fit tests missing style: {total_fit_tests_missing_style}")

    total_fit_tests_missing_parameter_mm = fit_tests_with_imputed_arkit_via_traditional_facial_measurements['perimeter_mm'].isna().sum()
    fit_tests_missing_parameters = fit_tests_with_imputed_arkit_via_traditional_facial_measurements[
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements['perimeter_mm'].isna()
    ]

    tested_missing_perimeter_mm = fit_tests_missing_parameters.groupby(
        ['mask_id', 'unique_internal_model_code']
    ).count()[['id']].sort_values(by='id', ascending=False)

    filtered_fit_tests = filter_fit_tests(
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements
    )
    mask_empirical_priors = compute_mask_empirical_priors(filtered_fit_tests)
    mask_candidates = attach_mask_empirical_priors_to_masks(mask_candidates, mask_empirical_priors)

    cleaned_fit_tests = prepare_training_data(
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements,
        mask_empirical_priors=mask_empirical_priors,
        use_facial_perimeter=False,
        use_diff_perimeter_bins=False,
        use_diff_perimeter_mask_bins=False
    )

    logging.info(
        "Fit tests after filtering: %s / %s",
        cleaned_fit_tests.shape[0],
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements.shape[0]
    )

    if cleaned_fit_tests.empty:
        logging.warning("No fit tests available after filtering. Exiting.")
        raise SystemExit(0)

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    category_metadata = _custom_lr_category_metadata(cleaned_fit_tests)
    num_rows = cleaned_fit_tests.shape[0]
    permutation = torch.randperm(num_rows)
    split_index = int(num_rows * 0.8)
    train_idx = permutation[:split_index]
    val_idx = permutation[split_index:]

    custom_result = train_custom_lr_with_split(
        cleaned_fit_tests,
        train_idx=train_idx,
        val_idx=val_idx,
        category_metadata=category_metadata,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        class_weighting=args.class_reweight,
    )

    params = custom_result['params']
    train_losses = custom_result['train_losses']
    val_losses = custom_result['val_losses']
    train_probs = custom_result['train_probs']
    val_probs = custom_result['val_probs']
    train_labels = custom_result['y_train']
    val_labels = custom_result['y_val']

    best_threshold = 0.5
    best_f1 = 0.0
    if val_probs.size:
        threshold_grid = np.arange(0.05, 0.96, 0.01)
        for candidate in threshold_grid:
            candidate_preds = (val_probs >= candidate).astype(float)
            candidate_f1 = f1_score(val_labels, candidate_preds, zero_division=0)
            if candidate_f1 > best_f1:
                best_f1 = candidate_f1
                best_threshold = float(candidate)
    logging.info("Selected threshold=%.2f with val_f1=%.3f", best_threshold, best_f1)

    saved_model_scope = 'split_train'
    if args.retrain_with_full:
        logging.info("Retraining custom_lr model on full dataset for artifact save.")
        full_idx = torch.arange(cleaned_fit_tests.shape[0])
        full_result = train_custom_lr_with_split(
            cleaned_fit_tests,
            train_idx=full_idx,
            val_idx=full_idx,
            category_metadata=category_metadata,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            class_weighting=args.class_reweight,
        )
        params = full_result['params']
        saved_model_scope = 'full_dataset'

    prefix = f"mask_recommender/models/{timestamp}"
    params_path = f"/tmp/mask_recommender_custom_params_{timestamp}.pt"
    torch.save(params, params_path)
    params_key = f"{prefix}/custom_model_params.pt"
    params_uri = _upload_file_to_s3(params_path, params_key)

    mask_data = {}
    for _, row in masks_df.iterrows():
        mask_id = row.get('id')
        if pd.isna(mask_id):
            continue
        fit_family_id = pd.to_numeric(row.get('fit_family_id'), errors='coerce')
        mask_data[str(int(mask_id))] = {
            'id': int(mask_id),
            'fit_family_id': int(fit_family_id) if pd.notna(fit_family_id) else None,
            'unique_internal_model_code': row.get('unique_internal_model_code', ''),
            'brand_model': derive_brand_model(
                row.get('unique_internal_model_code', ''),
                row.get('current_state')
            ),
            'perimeter_mm': row.get('perimeter_mm', None),
            'strap_type': row.get('strap_type', ''),
            'style': row.get('style', ''),
            **mask_empirical_priors.get(int(mask_id), {}),
        }

    mask_data_key = f"{prefix}/custom_mask_data.json"
    mask_data_uri = _upload_json_to_s3(mask_data, mask_data_key)

    def predict_custom(inference_rows):
        return _predict_custom_lr_probabilities(
            inference_rows,
            parameters=params,
            category_metadata=category_metadata,
        )

    images_dir = _images_output_dir()
    os.makedirs(images_dir, exist_ok=True)
    recommendations_path = os.path.join(images_dir, f"custom_recommendations_{timestamp}.json")
    recommendation_preview = build_recommendation_preview(
        user_ids=[99, 101],
        fit_tests_df=fit_tests_with_imputed_arkit_via_traditional_facial_measurements,
        mask_candidates=mask_candidates,
        predict_fn=predict_custom,
        output_path=None if _should_upload_visual_artifacts_to_s3() else recommendations_path,
        threshold=best_threshold,
    )
    recommendations_artifact = recommendations_path
    if _should_upload_visual_artifacts_to_s3():
        recommendations_key = f"mask_recommender/models/{timestamp}/custom_recommendations_{timestamp}.json"
        recommendations_uri = _best_effort_visual_upload(
            lambda: _upload_json_to_s3(recommendation_preview, recommendations_key),
            "custom recommendation preview",
            fallback_artifact=None,
        )
        recommendations_artifact = recommendations_uri
    else:
        logging.info("Saved recommendation preview to %s", recommendations_path)

    loss_plot_artifact = None
    if train_losses:
        loss_plot_path = os.path.join(images_dir, f"{timestamp}_custom_training_loss.png")
        plt.figure(figsize=(8, 4))
        epochs_range = range(1, len(train_losses) + 1)
        plt.plot(epochs_range, train_losses, label='train loss')
        if val_losses:
            plt.plot(epochs_range, val_losses, label='val loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Custom LR Training Loss')
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend()
        plt.tight_layout()
        loss_plot_artifact = loss_plot_path
        if _should_upload_visual_artifacts_to_s3():
            loss_buf = io.BytesIO()
            plt.savefig(loss_buf, format='png')
            loss_buf.seek(0)
            loss_plot_key = f"mask_recommender/models/{timestamp}/{timestamp}_custom_training_loss.png"
            loss_plot_uri = _best_effort_visual_upload(
                lambda: _upload_png_bytes_to_s3(loss_buf.getvalue(), loss_plot_key),
                "custom training loss plot",
                fallback_artifact=None,
            )
            loss_plot_artifact = loss_plot_uri
        else:
            plt.savefig(loss_plot_path)
            logging.info("Saved training loss plot to %s", loss_plot_path)
        plt.close()

    perimeter_diff_diagnostics_artifacts = _build_custom_lr_perimeter_diff_diagnostics(
        cleaned_fit_tests=cleaned_fit_tests,
        parameters=params,
        category_metadata=category_metadata,
        timestamp=timestamp,
        mask_data=mask_data,
        base_url=base_url,
    )

    roc_plot_path = os.path.join(images_dir, f"{timestamp}_custom_roc_auc.png")
    plt.figure(figsize=(8, 4))
    try:
        train_fpr, train_tpr, _ = roc_curve(train_labels, train_probs)
        train_auc = auc(train_fpr, train_tpr)
        plt.plot(train_fpr, train_tpr, label=f'train (AUC={train_auc:.3f})', linewidth=2)
    except ValueError:
        train_auc = None
        logging.warning("Skipping custom train ROC curve due to missing class labels.")
    try:
        val_fpr, val_tpr, _ = roc_curve(val_labels, val_probs)
        val_auc = auc(val_fpr, val_tpr)
        plt.plot(val_fpr, val_tpr, label=f'validation (AUC={val_auc:.3f})', linewidth=2)
    except ValueError:
        val_auc = None
        logging.warning("Skipping custom validation ROC curve due to missing class labels.")
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Custom LR ROC-AUC Curves')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()
    plt.tight_layout()
    roc_plot_artifact = roc_plot_path
    if _should_upload_visual_artifacts_to_s3():
        roc_buf = io.BytesIO()
        plt.savefig(roc_buf, format='png')
        roc_buf.seek(0)
        roc_plot_key = f"mask_recommender/models/{timestamp}/{timestamp}_custom_roc_auc.png"
        roc_plot_uri = _best_effort_visual_upload(
            lambda: _upload_png_bytes_to_s3(roc_buf.getvalue(), roc_plot_key),
            "custom ROC plot",
            fallback_artifact=None,
        )
        roc_plot_artifact = roc_plot_uri
    else:
        plt.savefig(roc_plot_path)
        logging.info("Saved ROC-AUC plot to %s", roc_plot_path)
    plt.close()

    try:
        roc_auc = roc_auc_score(val_labels, val_probs)
    except ValueError:
        roc_auc = None
    val_preds = (val_probs >= best_threshold).astype(float)
    val_precision = precision_score(val_labels, val_preds, zero_division=0)
    val_recall = recall_score(val_labels, val_preds, zero_division=0)

    metrics = {
        'timestamp': timestamp,
        'environment': _env_name(),
        'model_type': 'custom_lr',
        'threshold': best_threshold,
        'roc_auc': roc_auc,
        'val_f1': best_f1,
        'val_precision': val_precision,
        'val_recall': val_recall,
        'train_samples': int(len(train_labels)),
        'val_samples': int(len(val_labels)),
        'losses': train_losses,
        'val_losses': val_losses,
        'recommendations_artifact': recommendations_artifact,
        'training_loss_artifact': loss_plot_artifact,
        'roc_auc_artifact': roc_plot_artifact,
        'perimeter_diff_diagnostics_artifacts': perimeter_diff_diagnostics_artifacts,
        'retrain_with_full': bool(args.retrain_with_full),
        'saved_model_training_scope': saved_model_scope,
        'validation_metrics_source': 'split_validation',
    }
    metrics_key = f"{prefix}/custom_metrics.json"
    metrics_uri = _upload_json_to_s3(metrics, metrics_key)

    metadata = {
        'timestamp': timestamp,
        'environment': _env_name(),
        'model_type': 'custom_lr',
        'threshold': best_threshold,
        'retrain_with_full': bool(args.retrain_with_full),
        'saved_model_training_scope': saved_model_scope,
        'validation_metrics_source': 'split_validation',
        **category_metadata,
    }
    metadata_key = f"{prefix}/custom_model_metadata.json"
    metadata_uri = _upload_json_to_s3(metadata, metadata_key)
    local_artifact_dir = _save_local_custom_artifacts(
        timestamp=timestamp,
        params=params,
        metadata=metadata,
        mask_data=mask_data,
    )

    latest_payload = {
        'timestamp': timestamp,
        'model_type': 'custom_lr',
        'params_key': params_key,
        'params_uri': params_uri,
        'metadata_key': metadata_key,
        'metadata_uri': metadata_uri,
        'mask_data_key': mask_data_key,
        'mask_data_uri': mask_data_uri,
        'metrics_key': metrics_key,
        'metrics_uri': metrics_uri,
        'local_artifact_dir': str(local_artifact_dir),
    }
    latest_key = "mask_recommender/models/custom_latest.json"
    latest_uri = _upload_json_to_s3(latest_payload, latest_key)
    logging.info("Uploaded custom model params to %s", params_uri)
    logging.info("Uploaded custom metadata to %s", metadata_uri)
    logging.info("Uploaded custom metrics to %s", metrics_uri)
    logging.info("Updated custom latest pointer at %s", latest_uri)
    return latest_payload

