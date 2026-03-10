import argparse
import io
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[0]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import boto3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from botocore.exceptions import ClientError
from breathesafe_network import (build_session,
                                 fetch_facial_measurements_fit_tests,
                                 fetch_json)
from feature_builder import (ABS_PERIMETER_DIFF_STYLE_PREFIX,
                             FACE_SHAPE_FEATURE_COLUMNS,
                             FACE_STYLE_INTERACTION_PREFIX,
                             FACIAL_FEATURE_COLUMNS,
                             FACIAL_PERIMETER_COMPONENTS,
                             MASK_EMPIRICAL_FEATURE_COLUMNS,
                             MASK_SIZE_FEATURE_COLUMNS,
                             PERIMETER_PENALTY_FEATURE_COLUMNS,
                             PERIMETER_DIFF_SQ_STYLE_PREFIX,
                             PERIMETER_DIFF_STYLE_PREFIX,
                             STRAP_STYLE_INTERACTION_PREFIX,
                             add_face_shape_features,
                             add_face_style_interactions,
                             add_brand_model_column,
                             add_geometry_penalty_features,
                             add_mask_size_face_interactions,
                             add_mask_size_features,
                             add_strap_style_interactions,
                             add_strap_type_features,
                             add_style_perimeter_interactions,
                             build_feature_frame, derive_brand_model,
                             diff_bin_edges, diff_bin_index, diff_bin_labels,
                             scale_perimeter_diff_features)
from predict_arkit_from_traditional import predict_arkit_from_traditional
from prob_model import (normalize_qlft_pass, predict_prob_model,
                        train_prob_model)
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


def get_sorted_tested_masks(fit_tests_df):
    """
    Parameters:
        fit_tests_df: pd.DataFrame

    Returns: pd.DataFrame
        Masks dataframe that has been sorted by mask_id
    """

    fit_tested_mask_ids = fit_tests_df.drop_duplicates('mask_id')['mask_id']
    tested_masks = masks_df[masks_df['id'].isin(fit_tested_mask_ids)]

    return tested_masks.drop_duplicates('mask_id').sort_values(by='mask_id')


def compute_difference(mask_perimeters, user_face_perimeters, mask_ones, user_ones):
    mask_perimeters_over_users = user_ones @ mask_perimeters.float()
    user_perimeters_over_users = user_face_perimeter * mask_ones.T

    return mask_perimeters_over_users - user_perimeters_over_users


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

def calc_preds(
    beta_style_diff_bins,
    diff_bins,
    user_ones,
    users_by_masks_by_strap_types,
    users_by_masks_by_style, betas):

    diff_bins = produce_diff_bins(user_ones, sorted_tested_masks, sorted_styles, difference, start=-50, end=50)
    # TODO: add in strap effects
    # TODO: consider regular vs. extended length headstraps
    beta_tensor_diff_styles = produce_beta_tensor_diff_styles(
        beta_style_diff_bins,
        styles=sorted_styles,
        diff_bins=diff_bins,
        num_users=num_users,
        num_masks=num_masks
    )
    # dist bin, style, user, mask

    import pdb; pdb.set_trace()

    summation = produce_summation(diff_bins, betas, users_by_masks_by_strap_types, users_by_masks_by_style)

    # TODO: add in alpha
    return torch.logistic(summation)


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
        priors[int(mask_id)] = {
            'mask_fit_test_count': count,
            'mask_smoothed_pass_rate': smoothed_pass_rate,
            'mask_log_fit_test_count': float(np.log1p(count)),
            'mask_smoothed_pass_logit': float(np.log(clipped_rate / (1.0 - clipped_rate))),
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
    }

    mask_id_source = result.get('mask_id')
    if mask_id_source is None:
        mask_id_source = result.get('id')
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
            result.at[idx, column] = float(prior.get(column, defaults[column]))

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
    ] + PERIMETER_PENALTY_FEATURE_COLUMNS
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


def _probe_payloads():
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


def main(argv=None):
    parser = argparse.ArgumentParser(description='Train fit predictor model.')
    parser.add_argument('--epochs', type=int, default=600, help='Number of training epochs.')
    parser.add_argument('--learning-rate', type=float, default=0.00005, help='Learning rate for optimizer.')
    parser.add_argument('--model-type', default='nn', choices=['nn', 'prob'], help='Model type to train.')
    parser.add_argument('--loss-plot', default='python/mask_recommender/training_loss.png', help='Path to save training loss plot.')
    parser.add_argument('--loss-type', default='bce', choices=['bce', 'focal'], help='Loss function to use.')
    parser.add_argument('--focal-alpha', type=float, default=0.25, help='Alpha for focal loss.')
    parser.add_argument('--focal-gamma', type=float, default=2.0, help='Gamma for focal loss.')
    parser.add_argument('--use-facial-perimeter', action='store_true', help='Use summed facial perimeter instead of component features.')
    parser.add_argument('--use-diff-perimeter-bins', action='store_true', help='Use perimeter difference bins instead of raw perimeter features.')
    parser.add_argument('--use-diff-perimeter-mask-bins', action='store_true', help='Include per-mask perimeter difference bin features.')
    parser.add_argument('--exclude-mask-code', action='store_true', help='Exclude unique_internal_model_code from categorical features.')
    parser.add_argument('--exclude-brand-model', action='store_true', help='Exclude brand_model from categorical features.')
    parser.add_argument('--zscore', action='store_true', help='Apply z-score normalization to non-binary numeric features.')
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

    if args.use_facial_perimeter and args.use_diff_perimeter_bins:
        raise SystemExit("Cannot use --use-facial-perimeter and --use-diff-perimeter-bins together.")
    if args.use_facial_perimeter and args.use_diff_perimeter_mask_bins:
        raise SystemExit("Cannot use --use-facial-perimeter and --use-diff-perimeter-mask-bins together.")

    cleaned_fit_tests = prepare_training_data(
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements,
        mask_empirical_priors=mask_empirical_priors,
        use_facial_perimeter=args.use_facial_perimeter,
        use_diff_perimeter_bins=args.use_diff_perimeter_bins,
        use_diff_perimeter_mask_bins=args.use_diff_perimeter_mask_bins
    )
    logging.info(
        "Fit tests after filtering: %s / %s",
        cleaned_fit_tests.shape[0],
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements.shape[0]
    )

    if cleaned_fit_tests.empty:
        logging.warning("No fit tests available after filtering. Exiting.")
        raise SystemExit(0)

    if args.model_type == 'prob':
        if args.zscore:
            logging.info("--zscore is currently only applied to model_type=nn. Ignoring for prob model.")
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        mask_id_index = sorted(cleaned_fit_tests['mask_id'].dropna().unique())
        style_categories = sorted(cleaned_fit_tests['style'].dropna().unique())

        num_rows = cleaned_fit_tests.shape[0]
        permutation = torch.randperm(num_rows)
        split_index = int(num_rows * 0.8)
        train_idx = permutation[:split_index]
        val_idx = permutation[split_index:]

        train_df = cleaned_fit_tests.iloc[train_idx]
        val_df = cleaned_fit_tests.iloc[val_idx]

        params, prob_losses = train_prob_model(
            train_df,
            mask_id_index,
            style_categories,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
        )

        val_probs = predict_prob_model(params, val_df, mask_id_index, style_categories)
        val_labels = normalize_qlft_pass(val_df["qlft_pass"]).to_numpy()
        val_preds = (val_probs >= 0.5).astype(float)

        try:
            roc_auc = roc_auc_score(val_labels, val_probs)
        except ValueError:
            roc_auc = None

        val_precision = precision_score(val_labels, val_preds, zero_division=0)
        val_recall = recall_score(val_labels, val_preds, zero_division=0)
        val_f1 = f1_score(val_labels, val_preds, zero_division=0)
        saved_model_scope = 'split_train'
        if args.retrain_with_full:
            logging.info("Retraining probabilistic model on full dataset for artifact save.")
            params, _ = train_prob_model(
                cleaned_fit_tests,
                mask_id_index,
                style_categories,
                epochs=args.epochs,
                learning_rate=args.learning_rate,
            )
            saved_model_scope = 'full_dataset'

        prefix = f"mask_recommender/models/{timestamp}"

        params_path = f"/tmp/mask_recommender_prob_params_{timestamp}.pt"
        torch.save({key: value.detach().cpu() for key, value in params.items()}, params_path)
        params_key = f"{prefix}/prob_model_params.pt"
        params_uri = _upload_file_to_s3(params_path, params_key)

        mask_data = {}
        for _, row in masks_df.iterrows():
            mask_id = row.get('id')
            if pd.isna(mask_id):
                continue
            mask_data[str(int(mask_id))] = {
                'id': int(mask_id),
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

        mask_data_key = f"{prefix}/prob_mask_data.json"
        mask_data_uri = _upload_json_to_s3(mask_data, mask_data_key)

        metadata = {
            'timestamp': timestamp,
            'environment': _env_name(),
            'model_type': 'prob',
            'mask_id_index': mask_id_index,
            'style_categories': style_categories,
            'retrain_with_full': bool(args.retrain_with_full),
            'saved_model_training_scope': saved_model_scope,
            'validation_metrics_source': 'split_validation',
        }
        metadata_key = f"{prefix}/prob_model_metadata.json"
        metadata_uri = _upload_json_to_s3(metadata, metadata_key)

        metrics = {
            'timestamp': timestamp,
            'environment': _env_name(),
            'roc_auc': roc_auc,
            'val_f1': val_f1,
            'val_precision': val_precision,
            'val_recall': val_recall,
            'train_samples': int(train_df.shape[0]),
            'val_samples': int(val_df.shape[0]),
            'losses': prob_losses,
            'retrain_with_full': bool(args.retrain_with_full),
            'saved_model_training_scope': saved_model_scope,
            'validation_metrics_source': 'split_validation',
        }
        metrics_key = f"{prefix}/prob_metrics.json"
        metrics_uri = _upload_json_to_s3(metrics, metrics_key)

        latest_payload = {
            'timestamp': timestamp,
            'model_type': 'prob',
            'params_key': params_key,
            'params_uri': params_uri,
            'metadata_key': metadata_key,
            'metadata_uri': metadata_uri,
            'mask_data_key': mask_data_key,
            'mask_data_uri': mask_data_uri,
            'metrics_key': metrics_key,
            'metrics_uri': metrics_uri,
        }
        latest_key = "mask_recommender/models/prob_latest.json"
        latest_uri = _upload_json_to_s3(latest_payload, latest_key)

        logging.info("Uploaded prob model params to %s", params_uri)
        logging.info("Uploaded prob metadata to %s", metadata_uri)
        logging.info("Uploaded prob metrics to %s", metrics_uri)
        logging.info("Updated prob latest pointer at %s", latest_uri)

        return latest_payload

    categorical_columns = ['strap_type', 'style']
    if not args.exclude_brand_model:
        categorical_columns.append('brand_model')
    if not args.exclude_mask_code:
        categorical_columns.append('unique_internal_model_code')

    features, target = build_feature_matrix(cleaned_fit_tests, categorical_columns)

    num_rows = features.shape[0]
    permutation = torch.randperm(num_rows)
    split_index = int(num_rows * 0.8)
    train_idx = permutation[:split_index]
    val_idx = permutation[split_index:]

    split_zscore_stats = fit_zscore_stats(features, train_idx) if args.zscore else {}
    features_for_eval = apply_zscore(features, split_zscore_stats) if args.zscore else features

    model, train_losses, val_losses, x_train, y_train, x_val, y_val, train_idx, val_idx = train_predictor_with_split(
        features_for_eval,
        target,
        train_idx,
        val_idx,
        outer_dim=model_config.outer_dim,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        loss_type=args.loss_type,
        focal_alpha=args.focal_alpha,
        focal_gamma=args.focal_gamma,
        class_weighting=args.class_reweight,
    )

    zscore_stats_for_saved_model = split_zscore_stats
    features_for_saved_model = features_for_eval

    logging.info("Model training complete. Feature count: %s", features_for_eval.shape[1])
    feature_columns = list(features_for_eval.columns)
    images_dir = _images_output_dir()
    os.makedirs(images_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    model.eval()
    with torch.no_grad():
        train_probs = model(x_train).squeeze().cpu().numpy()
        train_labels = y_train.squeeze().cpu().numpy()
        val_probs = model(x_val).squeeze().cpu().numpy()
        val_labels = y_val.squeeze().cpu().numpy()

    if val_probs.size:
        logging.info(
            "Validation probabilities: min=%.4f mean=%.4f max=%.4f",
            float(np.min(val_probs)),
            float(np.mean(val_probs)),
            float(np.max(val_probs))
        )

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
        logging.info("Retraining NN model on full dataset for artifact save.")
        if args.zscore:
            zscore_stats_for_saved_model = fit_zscore_stats(features, np.arange(features.shape[0]))
            features_for_saved_model = apply_zscore(features, zscore_stats_for_saved_model)
        full_idx = torch.arange(features_for_saved_model.shape[0])
        model, _, _, _, _, _, _, _, _ = train_predictor_with_split(
            features_for_saved_model,
            target,
            full_idx,
            full_idx,
            outer_dim=model_config.outer_dim,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            loss_type=args.loss_type,
            focal_alpha=args.focal_alpha,
            focal_gamma=args.focal_gamma,
            class_weighting=args.class_reweight,
        )
        saved_model_scope = 'full_dataset'

    recommendations_path = os.path.join(
        images_dir,
        f"recommendations_{timestamp}.json"
    )

    def predict_nn(inference_rows):
       encoded = build_feature_frame(
           inference_rows,
           feature_columns=feature_columns,
           categorical_columns=categorical_columns,
           use_facial_perimeter=args.use_facial_perimeter,
           use_diff_perimeter_bins=args.use_diff_perimeter_bins,
           use_diff_perimeter_mask_bins=args.use_diff_perimeter_mask_bins
       )
       if args.zscore and zscore_stats_for_saved_model:
           encoded = apply_zscore(encoded, zscore_stats_for_saved_model)
       x_infer = torch.tensor(encoded.to_numpy(), dtype=torch.float32)
       model.eval()
       with torch.no_grad():
           return model(x_infer).squeeze().cpu().numpy()

    recommendation_preview = build_recommendation_preview(
        user_ids=[99, 101],
        fit_tests_df=fit_tests_with_imputed_arkit_via_traditional_facial_measurements,
        mask_candidates=mask_candidates,
        predict_fn=predict_nn,
        output_path=None if _should_upload_visual_artifacts_to_s3() else recommendations_path,
        threshold=best_threshold,
    )
    recommendations_artifact = recommendations_path
    if _should_upload_visual_artifacts_to_s3():
        recommendations_key = f"mask_recommender/models/{timestamp}/recommendations_{timestamp}.json"
        recommendations_uri = _best_effort_visual_upload(
            lambda: _upload_json_to_s3(recommendation_preview, recommendations_key),
            "recommendation preview",
            fallback_artifact=None,
        )
        recommendations_artifact = recommendations_uri
        if recommendations_uri:
            logging.info("Saved recommendation preview to %s", recommendations_uri)
    else:
        logging.info("Saved recommendation preview to %s", recommendations_path)
    probe_diagnostics = _build_probe_diagnostics(
        model=model,
        mask_candidates=mask_candidates,
        feature_columns=feature_columns,
        categorical_columns=categorical_columns,
        args=args,
        zscore_stats=zscore_stats_for_saved_model,
    )
    probe_diagnostics_path = os.path.join(images_dir, f"{timestamp}_probe_diagnostics.json")
    probe_diagnostics_artifact = probe_diagnostics_path
    if _should_upload_visual_artifacts_to_s3():
        probe_diagnostics_key = f"mask_recommender/models/{timestamp}/{timestamp}_probe_diagnostics.json"
        probe_diagnostics_uri = _best_effort_visual_upload(
            lambda: _upload_json_to_s3(probe_diagnostics, probe_diagnostics_key),
            "probe diagnostics",
            fallback_artifact=None,
        )
        probe_diagnostics_artifact = probe_diagnostics_uri
        if probe_diagnostics_uri:
            logging.info("Saved probe diagnostics to %s", probe_diagnostics_uri)
    else:
        with open(probe_diagnostics_path, 'w', encoding='utf-8') as handle:
            json.dump(probe_diagnostics, handle, indent=2)
        logging.info("Saved probe diagnostics to %s", probe_diagnostics_path)
    loss_plot_artifact = None
    if train_losses:
        loss_plot_path = os.path.join(images_dir, f"{timestamp}_training_loss.png")
        plt.figure(figsize=(8, 4))
        epochs = range(1, len(train_losses) + 1)
        plt.plot(epochs, train_losses, label='train loss')
        if val_losses:
            plt.plot(epochs, val_losses, label='val loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training Loss')
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend()
        plt.tight_layout()
        loss_plot_artifact = loss_plot_path
        if _should_upload_visual_artifacts_to_s3():
            loss_buf = io.BytesIO()
            plt.savefig(loss_buf, format='png')
            loss_buf.seek(0)
            loss_plot_key = f"mask_recommender/models/{timestamp}/{timestamp}_training_loss.png"
            loss_plot_uri = _best_effort_visual_upload(
                lambda: _upload_png_bytes_to_s3(loss_buf.getvalue(), loss_plot_key),
                "training loss plot",
                fallback_artifact=None,
            )
            loss_plot_artifact = loss_plot_uri
            if loss_plot_uri:
                logging.info("Saved training loss plot to %s", loss_plot_uri)
        else:
            plt.savefig(loss_plot_path)
            logging.info("Saved training loss plot to %s", loss_plot_path)
        plt.close()

    roc_plot_path = os.path.join(images_dir, f"{timestamp}_roc_auc.png")
    plt.figure(figsize=(8, 4))
    train_auc = None
    val_auc = None
    try:
        train_fpr, train_tpr, _ = roc_curve(train_labels, train_probs)
        train_auc = auc(train_fpr, train_tpr)
        plt.plot(train_fpr, train_tpr, label=f'train (AUC={train_auc:.3f})', linewidth=2)
    except ValueError:
        logging.warning("Skipping train ROC curve due to missing class labels.")
    try:
        val_fpr, val_tpr, _ = roc_curve(val_labels, val_probs)
        val_auc = auc(val_fpr, val_tpr)
        plt.plot(val_fpr, val_tpr, label=f'validation (AUC={val_auc:.3f})', linewidth=2)
    except ValueError:
        logging.warning("Skipping validation ROC curve due to missing class labels.")
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC-AUC Curves')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()
    plt.tight_layout()
    roc_plot_artifact = roc_plot_path
    if _should_upload_visual_artifacts_to_s3():
        roc_buf = io.BytesIO()
        plt.savefig(roc_buf, format='png')
        roc_buf.seek(0)
        roc_plot_key = f"mask_recommender/models/{timestamp}/{timestamp}_roc_auc.png"
        roc_plot_uri = _best_effort_visual_upload(
            lambda: _upload_png_bytes_to_s3(roc_buf.getvalue(), roc_plot_key),
            "ROC plot",
            fallback_artifact=None,
        )
        roc_plot_artifact = roc_plot_uri
        if roc_plot_uri:
            logging.info("Saved ROC-AUC plot to %s", roc_plot_uri)
    else:
        plt.savefig(roc_plot_path)
        logging.info("Saved ROC-AUC plot to %s", roc_plot_path)
    plt.close()

    val_results_path = os.path.join(images_dir, f"{timestamp}_validation_results.json")
    val_frame = features_for_eval.iloc[val_idx].copy()
    val_frame["probability_of_fit"] = val_probs
    val_frame["ground_truth"] = val_labels
    val_frame["prediction"] = (val_probs >= best_threshold).astype(int)
    val_frame["correct"] = val_frame["prediction"] == val_frame["ground_truth"]
    val_frame["confidence"] = np.maximum(val_probs, 1 - val_probs)
    val_frame = val_frame.sort_values(by="confidence", ascending=False)
    val_results = val_frame.to_dict(orient="records")
    val_results_artifact = val_results_path
    if _should_upload_visual_artifacts_to_s3():
        val_results_key = f"mask_recommender/models/{timestamp}/{timestamp}_validation_results.json"
        val_results_uri = _best_effort_visual_upload(
            lambda: _upload_json_to_s3(val_results, val_results_key),
            "validation results",
            fallback_artifact=None,
        )
        val_results_artifact = val_results_uri
        if val_results_uri:
            logging.info("Saved validation results to %s", val_results_uri)
    else:
        with open(val_results_path, "w", encoding="utf-8") as handle:
            json.dump(val_results, handle, indent=2)
        logging.info("Saved validation results to %s", val_results_path)

    logging.info(f"masks with fit tests that are missing perimeter_mm: {tested_missing_perimeter_mm}")

    logging.info(f"Total # fit tests missing parameter_mm: {total_fit_tests_missing_parameter_mm}")

    threshold = best_threshold
    val_preds = (val_probs >= threshold).astype(float)
    try:
        roc_auc = roc_auc_score(val_labels, val_probs)
    except ValueError:
        roc_auc = None

    val_precision = precision_score(val_labels, val_preds, zero_division=0)
    val_recall = recall_score(val_labels, val_preds, zero_division=0)

    prefix = f"mask_recommender/models/{timestamp}"

    model_path = f"/tmp/mask_recommender_model_{timestamp}.pt"
    torch.save(model.state_dict(), model_path)
    model_key = f"{prefix}/model_state_dict.pt"
    model_uri = _upload_file_to_s3(model_path, model_key)

    mask_data = {}
    for _, row in masks_df.iterrows():
        mask_id = row.get('id')
        if pd.isna(mask_id):
            continue
        mask_data[str(int(mask_id))] = {
            'id': int(mask_id),
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

    mask_data_key = f"{prefix}/mask_data.json"
    mask_data_uri = _upload_json_to_s3(mask_data, mask_data_key)

    actual_series = fit_tests_with_imputed_arkit_via_traditional_facial_measurements.get('actual')
    if actual_series is None:
        actual_series = pd.Series([None] * total_num_fit_tests)
    actual_series = actual_series.fillna(False).astype(bool)
    actual_count = int(actual_series.sum())
    predicted_count = int(total_num_fit_tests - actual_count)

    training_actual_count = 0
    training_predicted_count = 0
    if 'actual' in filtered_fit_tests.columns:
        training_actual_count = int(filtered_fit_tests['actual'].fillna(False).astype(bool).sum())
        training_predicted_count = int(filtered_fit_tests.shape[0] - training_actual_count)

    metrics = {
        'timestamp': timestamp,
        'environment': _env_name(),
        'threshold': threshold,
        'val_loss': val_losses[-1] if val_losses else None,
        'roc_auc': roc_auc,
        'val_f1': best_f1,
        'val_precision': val_precision,
        'val_recall': val_recall,
        'train_samples': int(features.shape[0]),
        'val_samples': int(y_val.shape[0]),
        'fit_tests_total': int(total_num_fit_tests),
        'fit_tests_total_actual_arkit': actual_count,
        'fit_tests_total_predicted_arkit': predicted_count,
        'fit_tests_training_total': int(filtered_fit_tests.shape[0]),
        'fit_tests_training_actual_arkit': training_actual_count,
        'fit_tests_training_predicted_arkit': training_predicted_count,
        'recommendations_artifact': recommendations_artifact,
        'training_loss_artifact': loss_plot_artifact,
        'roc_auc_artifact': roc_plot_artifact,
        'validation_results_artifact': val_results_artifact,
        'probe_diagnostics_artifact': probe_diagnostics_artifact,
        'retrain_with_full': bool(args.retrain_with_full),
        'saved_model_training_scope': saved_model_scope,
        'validation_metrics_source': 'split_validation',
        'exclude_mask_code': bool(args.exclude_mask_code),
        'exclude_brand_model': bool(args.exclude_brand_model),
        'zscore': bool(args.zscore),
        'zscore_features_count': len(zscore_stats_for_saved_model),
    }
    metrics_key = f"{prefix}/metrics.json"
    metrics_uri = _upload_json_to_s3(metrics, metrics_key)

    metadata = {
        'timestamp': timestamp,
        'environment': _env_name(),
        'feature_columns': feature_columns,
        'categorical_columns': categorical_columns,
        'hidden_sizes': _extract_hidden_sizes(model),
        'outer_dim': model_config.outer_dim,
        'threshold': threshold,
        'model_class': 'torch.nn.Sequential',
        'use_facial_perimeter': args.use_facial_perimeter,
        'use_diff_perimeter_bins': args.use_diff_perimeter_bins,
        'use_diff_perimeter_mask_bins': args.use_diff_perimeter_mask_bins,
        'exclude_mask_code': args.exclude_mask_code,
        'exclude_brand_model': args.exclude_brand_model,
        'retrain_with_full': bool(args.retrain_with_full),
        'saved_model_training_scope': saved_model_scope,
        'validation_metrics_source': 'split_validation',
        'zscore': bool(args.zscore),
        'zscore_stats': zscore_stats_for_saved_model,
    }
    metadata_key = f"{prefix}/model_metadata.json"
    metadata_uri = _upload_json_to_s3(metadata, metadata_key)

    latest_payload = {
        'timestamp': timestamp,
        'model_key': model_key,
        'model_uri': model_uri,
        'metrics_key': metrics_key,
        'metrics_uri': metrics_uri,
        'metadata_key': metadata_key,
        'metadata_uri': metadata_uri,
        'mask_data_key': mask_data_key,
        'mask_data_uri': mask_data_uri,
    }
    latest_key = "mask_recommender/models/latest.json"
    latest_uri = _upload_json_to_s3(latest_payload, latest_key)

    logging.info("Uploaded model to %s", model_uri)
    logging.info("Uploaded metadata to %s", metadata_uri)
    logging.info("Uploaded metrics to %s", metrics_uri)
    logging.info("Updated latest pointer at %s", latest_uri)

    return latest_payload


if __name__ == '__main__':
    main()
