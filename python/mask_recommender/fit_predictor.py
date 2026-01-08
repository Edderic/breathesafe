import logging
import os

import pandas as pd
import torch
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


if __name__ == '__main__':
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

    logging.info(f"masks with fit tests that are missing perimeter_mm: {tested_missing_perimeter_mm}")
    import pdb; pdb.set_trace()


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
