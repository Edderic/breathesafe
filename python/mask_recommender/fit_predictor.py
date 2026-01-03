import numpy as np
import pandas as pd
import torch
from breathesafe_network import (build_session, fetch_json,
                                 login_with_credentials, logout)

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


def initialize_betas(diff_keys, num_users, num_masks):
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

    return torch.rand((num_users, num_masks, len(STYLE_TYPES)), len(diff_keys))


def produce_diff_bins(difference):
    """
    Parameters:
        difference: torch.tensor
            Has the shape (num_users, num_masks), consisting of 1s and 0s, where
            1 indicates membership and 0 indicates not being part of the group

    Returns: dict
        e.g. {
            'x < -50': ...,
            '-50 <= x < -50': ...,
            ...
            '-40 <= x < 50': ...,
            'x > 50': ...,
        }

    """
    diff = {
        'x < -50': (difference < -50).float(),
        'x > 50': (difference > 50).float(),
    }

    for i in range(-50, 50, 10):
        diff[f'{i} <= x < {i + 10}'] = ((difference >= i) & (difference < (i + 10))).float()

    return diff


def produce_summation(betas, mask_types_over_users):
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
            summation = betas[:,:,:,i] * mask_types_over_users[:,:,:,i]
        else:
            summation += betas[:,:,:,i] * mask_types_over_users[:,:,:,i]

    return summation.sum(axis=2)

def calc_preds(mask_perimeters_over_users, user_perimeters_over_users):
    difference = mask_perimeters_over_users - user_perimeters_over_users
    diff_bins = produce_diff_bins(difference)
    betas = initialize_betas(diff_bins.keys(), num_users, num_masks)

    # TODO: actually implement this
    mask_types_over_users = torch.rand((num_users, num_masks, len(STYLE_TYPES), len(diff_bins.keys())))

    # TODO: add in strap effects
    # TODO: consider regular vs. extended length headstraps
    summation = produce_summation(diff_bins, betas, mask_types_over_users)

    # TODO: add in alpha
    return torch.logistic(summation)




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
    masks_payload = fetch_json(session, masks_url).get("masks", [])

    user_arkit_table = pd.read_csv('./python/mask_recommender/user_arkit_table.csv')
    predicted_fit_tests = pd.read_csv('./python/mask_recommender/predicted_fit_tests.csv')

    num_users = user_arkit_table.shape[0]
    num_masks = 100

    user_and_facial_measurements_for_face_perimeter_calculation = torch.from_numpy(user_arkit_table[FACIAL_FEATURE_COLUMNS].to_numpy())
    user_face_perimeter = user_and_facial_measurements_for_face_perimeter_calculation.sum(axis=1).unsqueeze(1)

    # TODO: use actual users and facial measurements
    # TODO: some iOS aggregated facial measurements are from actual face scans, while
    # others are just predicted. For those that are predicted, set requires_grad
    # = True, but for those that are from actual face scans, set requires_grad
    # to False,
    #

    # TODO: use actual mask perimeters
    # TODO: get actual mask_perimeter values. Should values are unobserved but
    # we ccould make educated guesses. With those educated guesses, we treat
    # those as random variables (with requires_grad set to True), and those that
    # have been measured as constantss (with requires_grad set to False.
    mask_perimeter = torch.rand((num_masks, 1))

    mask_ones = torch.ones((num_masks, 1))
    user_ones = torch.ones((num_users, 1))

    mask_perimeters_over_users = user_ones @ mask_perimeter.T
    user_perimeters_over_users = user_face_perimeter * mask_ones.T


    # TODO: one-hot encoded, so that we can multiply
    mask_strap_types = torch.rand((num_masks, len(STRAP_TYPES)))

    strap_tensors = []
    for strap_index in range(len(STRAP_TYPES)):
        expanded = user_ones @ mask_strap_types[:, strap_index].unsqueeze(0)
        strap_tensors.append(expanded.unsqueeze(-1))

    users_by_masks_by_strap_types = torch.cat(strap_tensors, dim=-1)



    fit_tests_df = pd.DataFrame(fit_tests_payload)
    masks_df = pd.DataFrame(masks_payload)

    fit_tests_df.drop_duplicates('mask_id')[['mask_id', 'style']]
    masks_df[['id', 'unique_internal_model_code', 'style', 'strap_type']]

    import pdb; pdb.set_trace()
    # generally speaking, the bigger the difference between the facial and mask
    # perimeters, the lower the probability of fit, with some exceptions:
    #
    # - bifold,
    #
    # - duckbill and boat masks wrap under the chin so can have mask perimeters
    # that are significantly larger than the facial perimeters, yet have a great
    # fit.
    #
    # - baggy blues should in theory have poor performance regardless of
    # difference
    #
    # - strapless w/ adhesive style (e.g. Readimask) should have more of a
    # uniform distribution
    #
    # - elastomerics: has more rigidity than filtering facepiece respirators
    # (FFRs). Long nose vs short nose could make a big difference in fit
    # (relative to FFR — FFR is more flexible.)
    results = calc_preds(mask_perimeters_over_users, user_perimeters_over_users)
