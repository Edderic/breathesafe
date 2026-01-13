import logging
import os
import argparse

import pandas as pd
import torch
import matplotlib.pyplot as plt
from breathesafe_network import (build_session,
                                 fetch_facial_measurements_fit_tests,
                                 fetch_json)
from predict_arkit_from_traditional import predict_arkit_from_traditional

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

STYLE_TYPES = [
    'Cup',
    'Duckbill',
    'Bifold',
    'Bifold & Gasket',
    'Boat',
    'Adhesive',
    'Elastomeric'
]

FACIAL_FEATURE_COLUMNS = [
    'nose_mm',
    'chin_mm',
    'top_cheek_mm',
    'mid_cheek_mm',
]


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


def prepare_training_data(fit_tests_df):
    filtered = fit_tests_df.copy()
    filtered = filtered[filtered['perimeter_mm'].notna()]

    if 'mask_modded' in filtered.columns:
        mask_modded_flags = filtered['mask_modded'].apply(_is_truthy)
        filtered = filtered[~mask_modded_flags]
    else:
        logging.info("mask_modded column not found; skipping modded filtering.")

    filtered['facial_perimeter_mm'] = filtered[FACIAL_FEATURE_COLUMNS].sum(axis=1, min_count=1)
    filtered = filtered[filtered['facial_perimeter_mm'].notna()]

    filtered['qlft_pass_normalized'] = filtered['qlft_pass'].apply(_normalize_pass)
    filtered = filtered[filtered['qlft_pass_normalized'].notna()]

    feature_cols = [
        'perimeter_mm',
        'facial_perimeter_mm',
        'strap_type',
        'style',
        'unique_internal_model_code'
    ]
    filtered = filtered[feature_cols + ['qlft_pass_normalized']]
    return filtered


def build_feature_matrix(filtered_df):
    categorical_cols = ['strap_type', 'style', 'unique_internal_model_code']
    features = pd.get_dummies(filtered_df, columns=categorical_cols, dummy_na=True)
    target = features.pop('qlft_pass_normalized')
    features = features.apply(pd.to_numeric, errors='coerce').fillna(0)
    features = features.astype(float)
    target = pd.to_numeric(target, errors='coerce').fillna(0).astype(float)
    return features, target


def train_predictor(features, target, epochs=50, learning_rate=0.01):
    x = torch.tensor(features.to_numpy(), dtype=torch.float32)
    y = torch.tensor(target.to_numpy(), dtype=torch.float32).unsqueeze(1)

    num_rows = x.shape[0]
    permutation = torch.randperm(num_rows)
    split_index = int(num_rows * 0.8)
    train_idx = permutation[:split_index]
    val_idx = permutation[split_index:]

    x_train, y_train = x[train_idx], y[train_idx]
    x_val, y_val = x[val_idx], y[val_idx]

    model = torch.nn.Sequential(
        torch.nn.Linear(x.shape[1], 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 16),
        torch.nn.ReLU(),
        torch.nn.Linear(16, 1)
    )

    loss_fn = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        logits = model(x_train)
        loss = loss_fn(logits, y_train)
        loss.backward()
        optimizer.step()
        train_losses.append(loss.item())

        if (epoch + 1) % 10 == 0 or epoch == 0:
            model.eval()
            with torch.no_grad():
                val_logits = model(x_val)
                val_loss = loss_fn(val_logits, y_val).item()
                preds = (torch.sigmoid(val_logits) >= 0.5).float()
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
            val_logits = model(x_val)
            val_loss = loss_fn(val_logits, y_val).item()
        val_losses.append(val_loss)

    return model, train_losses, val_losses


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train fit predictor model.')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs.')
    parser.add_argument('--learning-rate', type=float, default=0.01, help='Learning rate for optimizer.')
    parser.add_argument('--loss-plot', default='python/mask_recommender/fit_predictor_training_loss.png', help='Path to save training loss plot.')
    args = parser.parse_args()
    # [ ] Get a table of users and facial features
    # [ ] Get a table of masks and perimeters

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    base_url = 'http://localhost:3000'
    masks_url = f"{base_url}/masks.json?per_page=1000"

    session = build_session(None)
    fit_tests_payload = fetch_facial_measurements_fit_tests(session=session)
    fit_tests_df = pd.DataFrame(fit_tests_payload)

    masks_df = get_masks(session, masks_url)
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

    cleaned_fit_tests = prepare_training_data(
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements
    )
    logging.info(
        "Fit tests after filtering: %s / %s",
        cleaned_fit_tests.shape[0],
        fit_tests_with_imputed_arkit_via_traditional_facial_measurements.shape[0]
    )

    if cleaned_fit_tests.empty:
        logging.warning("No fit tests available after filtering. Exiting.")
        raise SystemExit(0)

    features, target = build_feature_matrix(cleaned_fit_tests)
    model, train_losses, val_losses = train_predictor(features, target, epochs=args.epochs, learning_rate=args.learning_rate)

    logging.info("Model training complete. Feature count: %s", features.shape[1])
    if train_losses:
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
        plt.savefig(args.loss_plot)
        plt.close()
        logging.info("Saved training loss plot to %s", args.loss_plot)

    logging.info(f"masks with fit tests that are missing perimeter_mm: {tested_missing_perimeter_mm}")

    logging.info(f"Total # fit tests missing parameter_mm: {total_fit_tests_missing_parameter_mm}")

    user_arkit_table = pd.read_csv('./python/mask_recommender/user_arkit_table.csv')
    predicted_fit_tests = pd.read_csv('./python/mask_recommender/predicted_fit_tests.csv')

    sorted_tested_masks = get_sorted_tested_masks(fit_tests_df)

    with_perimeter = sorted_tested_masks[sorted_tested_masks['perimeter_mm'].notna()]

    # users of fit tests associated with masks that have perimeters
    user_arkit_for_masks_that_have_perimeters = get_users(fit_tests_df, with_perimeter, user_arkit_table)
    #

    user_arkit_for_masks_that_have_perimeters
    import pdb; pdb.set_trace()

    user_and_facial_measurements_for_face_perimeter_calculation = torch.from_numpy(
        user_arkit_for_masks_that_have_perimeters[FACIAL_FEATURE_COLUMNS].to_numpy()
    )

    user_ones = torch.ones((user_arkit_for_masks_that_have_perimeters.shape[0], 1))

    user_face_perimeter = user_and_facial_measurements_for_face_perimeter_calculation.sum(axis=1).unsqueeze(1)
    # filter
    users_by_masks_by_strap_types = get_users_by_masks_by_types(user_ones, sorted_tested_masks, by='strap_type')

    mask_perimeters = torch.from_numpy(with_perimeter['perimeter_mm'].to_numpy()).unsqueeze(0)
    num_masks = with_perimeter.shape[0]

    mask_ones = torch.ones((num_masks, 1))

    difference = compute_difference(mask_perimeters, user_face_perimeter, mask_ones, user_ones)
    import pdb; pdb.set_trace()

    diff_bins = produce_diff_bins(user_ones, difference, start=-60, end=60, interval=10)
    diff_bins.shape

    sorted_styles = sorted(list(with_perimeter['style'].unique()))
    beta_style_diff_bins = torch.rand((diff_bins.shape[0] * len(sorted_styles), 1), requires_grad=True)

    results = calc_preds(
        beta_style_diff_bins,
        diff_bins,
        user_ones,
        users_by_masks_by_strap_types,
        betas)
