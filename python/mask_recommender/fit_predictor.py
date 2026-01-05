import itertools

import numpy as np
import pandas as pd
import torch
from breathesafe_network import (build_session, fetch_json,
                                 login_with_credentials, logout)

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


TODO: some iOS aggregated facial measurements are from actual face scans, while
others are just predicted. For those that are predicted, set requires_grad
= True, but for those that are from actual face scans, set requires_grad
to False,


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

    return torch.rand((num_users, num_masks, len(style_types4)), len(diff_keys))


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

    base_url = 'http://localhost:3000'
    fit_tests_url = f"{base_url}/facial_measurements_fit_tests.json"
    masks_url = f"{base_url}/masks.json?per_page=1000"

    session = build_session(None)
    fit_tests_payload = fetch_json(session, fit_tests_url)[
        "fit_tests_with_facial_measurements"
    ]

    masks_df = get_masks(session, masks_url)

    user_arkit_table = pd.read_csv('./python/mask_recommender/user_arkit_table.csv')
    predicted_fit_tests = pd.read_csv('./python/mask_recommender/predicted_fit_tests.csv')

    fit_tests_df = pd.DataFrame(fit_tests_payload)
    sorted_tested_masks = get_sorted_tested_masks(fit_tests_df)

    with_perimeter = sorted_tested_masks[sorted_tested_masks['perimeter_mm'].notna()]

    # users of fit tests associated with masks that have perimeters
    user_arkit_for_masks_that_have_perimeters = get_users(fit_tests_df, with_perimeter, user_arkit_table)
    # users WITHOUT facial measurements WITHOUT fit tests: don't care
    # users with facial measurements WITHOUT fit tests: don't care
    #
    # users with facial measurements WITH fit tests: care
    # users MISSING facial measurements WITH fit tests: technically offers some
    # information, but we'd have to do some imputation of their facial features.
    #
    # Could use fit test results to find similar people who do have facial
    # measurement data
    #
    # - unique_internal_model_code
    # - perimeter_mm
    # - style
    # - strap type
    # - fit_test pass / fail
    #
    # Goal: predict facial measurement data from fit tests as a starting point.
    # 1. Find people who are fit test results that are similar to one who does
    # not have facial measurement data.
    #
    # Challenges: fit tests are sparse, e.g. Let's say we are interested in
    # predicting facial measurements for an individual O, who passed with masks A
    # and B.
    #
    # Let's say there are the following individuals:
    # An individual P with facial measurements passed in masks A and B
    # An individual Q with facial measurements who only passed with mask A, did not do a fit test with B
    # An individual R with facial measurements only passed with mask B, and did # not do a fit test with A
    # An individual S with facial measurements failed with both A and B
    # An individual T with facial measurements failed with A, did not do a fit test with B
    # An individual U with facial measurements failed with B, did not do a fit test with A
    #
    # Individual O should be closest to P, then Q and R, then T and U, then S,
    # in that order
    #
    # I suppose we can represent the other individuals as vectors, where the
    # dimensions are the masks that the individual-of-interest that we have
    # data for.
    #
    # P: [1, 1]
    # Q: [1, 0]
    # R: [0, 1]
    # S: [-1, -1]
    # T: [-1, 0]
    # U: [0. -1]
    #
    # Cosine(O, P): [1, 1] dot [1, 1] / ((\sum_i i^2) * (\sum_j j^2)) = 2 / 2 = # 1
    # Cosine(O, Q): [1, 1] dot [1, 0] / ((\sum_i i^2) * (\sum_j j^2)) = 1 / (sqrt(2) * 1) = 0.707
    # Cosine(O, R): [1, 1] dot [0, 1] / ((\sum_i i^2) * (\sum_j j^2)) = 1 / (1 * sqrt(2)) = 0.707
    # Cosine(O, S): [1, 1] dot [-1, -1] / ((\sum_i i^2) * (\sum_j j^2)) = -2 / (sqrt(2) * sqrt(2)) = -1
    # Cosine(O, T): [1, 1] dot [-1, 0] / ((\sum_i i^2) * (\sum_j j^2)) = -1 / (sqrt(2) * 1) = -0.707
    # Cosine(O, U): [1, 1] dot [0, -1] / ((\sum_i i^2) * (\sum_j j^2)) = -1 / (1 * sqrt(2)) = -0.707
    #
    #
    #
    #

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
