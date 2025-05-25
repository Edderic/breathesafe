import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from fit_testing import convert_n99_mode_scores_to_n95_mode, \
    estimate_n95_mode_ff_from_n99_mode_results, preprocess_fit_tests, convert_n99_mode_scores_to_n95_mode

def train():
    date = '2025-04-09'
    prefix = 'python/mask_recommender'
    masks_path = f'{prefix}/data/sql_imports/{date}-masks.csv'
    fit_test_path = f'{prefix}/data/sql_imports/{date}-fit_tests.csv'
    facial_measurements_path = f'{prefix}/data/sql_imports/{date}-latest_facial_measurements.csv'

    X, y = data_prep(masks_path, fit_test_path, facial_measurements_path)
    classifier = RandomForestClassifier()

    X.columns = X.columns.astype(str)

    classifier.fit(X, y)

    filename = 'fit_predictor.pkl'
    pickle.dump(classifier, open(f'{prefix}/models/{filename}', 'wb'))


def data_prep(masks_path, fit_tests_path, facial_measurements_path):
    masks = prepare_masks(masks_path)
    fit_tests = prepare_fit_tests(fit_tests_path)
    latest_facial_measurements = prepare_facial_measurements(facial_measurements_path)

    #latest_facial_measurements = \
    #    unique_facial_measurements\
    #        .sort_values(by='updated_at', ascending=False)\
    #        .drop_duplicates(
    #            subset=['user_id']
    #        ).copy()

    fit_tests_with_qlft_actual_and_estimates = \
        get_fit_tests_with_qlft_actual_and_estimates(fit_tests, masks)

    fit_tests_with_latest_facial_measurements = \
        fit_tests_with_qlft_actual_and_estimates.merge(
            latest_facial_measurements,
            on='user_id'
        )

    fit_test_counts_per_user = fit_tests\
        .groupby('user_id')\
        .count()\
        .rename(columns={'facial_hair_short': 'fit_test_count'})[['fit_test_count']]

    fit_tests_with_latest_facial_measurements_with_outlier_users_excluded = \
        remove_facial_measurement_outliers(
            latest_facial_measurements,
            fit_tests_with_latest_facial_measurements,
            fit_test_counts_per_user
        )

    mask_dummies = pd.get_dummies(
        fit_tests_with_latest_facial_measurements_with_outlier_users_excluded['mask_id'].astype(int)
    )
    with_mask_dummies = pd.concat(
        [
            fit_tests_with_latest_facial_measurements_with_outlier_users_excluded,
            mask_dummies
        ],
        axis=1
    )
    with_mask_dummies['qlft_pass'] = \
        with_mask_dummies['qlft_pass'].astype(int)

    mask_predictors = ['Adjustable Earloop', 'Adjustable Headstrap',
           'Earloop', 'Headstrap', 'Bifold', 'Bifold & Gasket', 'Boat',
           'Cotton + High Filtration Efficiency Material', 'Cup', 'Duckbill',
           'Elastomeric', 'perimeter_mm']

    # mask_predictors_df = \
        # with_mask_dummies[['unique_internal_model_code', 'mask_id'] + mask_predictors]\
            # .drop_duplicates(subset='mask_id')\
            # .dropna(subset=['perimeter_mm'])\
            # .sort_values(by='unique_internal_model_code')

    facial_measurement_predictors = [
        'face_width',
        'face_length',
        'bitragion_subnasale_arc',
        'nasal_root_breadth',
        'nose_protrusion',
        'nose_bridge_height',
    ]

    subset_facial_measurement_predictors = [
        'bitragion_subnasale_arc',
        'face_width',
        'nose_protrusion'
    ]

    data = with_mask_dummies.dropna(
        subset=['bitragion_subnasale_arc', 'perimeter_mm', 'nose_bridge_height']
    )

    X = data[
        subset_facial_measurement_predictors + \
            ['facial_hair_beard_length_mm'] + \
            list(mask_dummies.columns) + \
            list(mask_predictors)
    ]

    y = data['qlft_pass']

    return X, y

def get_zscores_for_facial_measurements(facial_measurements):
    continuous_vars = [
        'face_width', 'jaw_width',
        'face_depth', 'face_length', 'lower_face_length',
        'bitragion_menton_arc', 'bitragion_subnasale_arc',
        'nose_bridge_height', 'lip_width', 'head_circumference',
        'nasal_root_breadth', 'nose_protrusion'
    ]

    facial_continuous = facial_measurements[
        continuous_vars + ['manager_email', 'user_id', 'first_name', 'last_name']
    ]
    facial_measurements = facial_continuous.drop_duplicates(subset='user_id').copy()

    for c in continuous_vars:
        facial_measurements.loc[:, c] = np.where(facial_measurements[c] == 0, np.nan, facial_measurements[c])

    for c in continuous_vars:
        facial_measurements[f'zscore_{c}'] = \
            (facial_measurements[c] - facial_measurements[c].mean()) / facial_measurements[c].std()

    return facial_measurements.set_index(
        ['manager_email', 'user_id', 'first_name', 'last_name']
    )[facial_measurements.columns[facial_measurements.columns.str.contains('zscore')]]


def remove_facial_measurement_outliers(
    facial_measurements,
    fit_tests_with_latest_facial_measurements,
    fit_test_counts_per_user
):
    """
    Remove facial measurement outliers, assuming the data is being inputted
    incorrectly

    Parameters:
        facial_measurements

        fit_tests_with_latest_facial_measurements

        fit_test_counts_per_user

                    fit_test_count
            user_id
            99	     101
            101	     39
            104	     8

    Returns: pd.DataFrame
    """

    zscores = get_zscores_for_facial_measurements(facial_measurements)
    subset_zscores = zscores[
        [
            'zscore_face_width',
            'zscore_face_length',
            'zscore_bitragion_subnasale_arc',
            'zscore_nasal_root_breadth',
            'zscore_nose_protrusion',
            'zscore_nose_bridge_height',
            'zscore_lip_width',
        ]
    ]

    facial_measurement_outliers = subset_zscores[
        ((subset_zscores > 2) | (subset_zscores < -2)).sum(axis=1) > 0
    ]

    facial_measurement_outliers_with_fit_test_count = \
        facial_measurement_outliers.reset_index().set_index('user_id').merge(
            fit_test_counts_per_user,
            left_index=True,
            right_index=True
        ).sort_values(by='fit_test_count', ascending=False)

    user_ids_with_outlier_facial_measurements_to_exclude = list(
        set(
            list(
                facial_measurement_outliers_with_fit_test_count.index
            )
        ) - set([361, 101])
    )

    return fit_tests_with_latest_facial_measurements[
        ~fit_tests_with_latest_facial_measurements['user_id'].isin(
            user_ids_with_outlier_facial_measurements_to_exclude
        )
    ].copy()

def get_fit_tests_with_qlft_actual_and_estimates(fit_tests, masks):
    """
    Combines too_small_or_too_big, fit_tests_with_actual_qlft_data, and
    fit_tests_with_actual_n95_mode_results

    Parameters:
        fit_tests: pd.DataFrame
            quantitative_testing_mode: str
            quantitative_hmff: float

    Returns: pd.DataFrame
    """
    masks_with_max_n99_mode_ff = get_masks_with_max_n99_mode_ff(fit_tests, masks)
    fit_tests_joined_with_filtration_efficiency = fit_tests.merge(
        masks_with_max_n99_mode_ff,
        left_on='mask_id',
        right_index=True,
    )

    n99_mode_with_fit_tests_and_filtration_efficiency = \
        fill_n99_filtration_efficiency_potentially_using_others_data(
            fit_tests_joined_with_filtration_efficiency
        )

    set_qlft_pass(n99_mode_with_fit_tests_and_filtration_efficiency)
    n99_mode_converted_to_qlft = n99_mode_with_fit_tests_and_filtration_efficiency[
        ~n99_mode_with_fit_tests_and_filtration_efficiency['n95_mode_estimate'].isna()
    ]

    fit_tests_with_actual_n95_mode_results = \
        get_fit_tests_with_actual_n95_mode_results(fit_tests)

    too_small_or_too_big = set_too_small_or_too_big_as_instant_fail(fit_tests)
    fit_tests_with_actual_qlft_data = get_fit_tests_with_actual_qlft_data(fit_tests)

    fit_tests_with_qlft_actual_and_estimates = pd.concat(
        [
            too_small_or_too_big.merge(
                masks,
                left_on='mask_id',
                right_index=True
            ),
            fit_tests_with_actual_qlft_data.merge(
                masks,
                left_on='mask_id',
                right_index=True
            ),
            fit_tests_with_actual_n95_mode_results.merge(
                masks,
                left_on='mask_id',
                right_index=True
            ),
            n99_mode_converted_to_qlft
        ]
    )
    fit_tests_with_qlft_actual_and_estimates.loc[:, 'qlft_pass'] = \
        fit_tests_with_qlft_actual_and_estimates['qlft_pass'].astype(int)

    return fit_tests_with_qlft_actual_and_estimates

def get_fit_tests_with_actual_n95_mode_results(fit_tests):
    """
    Parameters:
        fit_tests: pd.DataFrame
            quantitative_testing_mode: str
            quantitative_hmff: float

    Returns: pd.DataFrame
    """
    fit_tests_with_actual_n95_mode_results = fit_tests[
        fit_tests['quantitative_testing_mode'] == 'N95'
    ].copy()

    fit_tests_with_actual_n95_mode_results['qlft_pass'] = \
        fit_tests_with_actual_n95_mode_results['quantitative_hmff'] >= 100

    return fit_tests_with_actual_n95_mode_results

def get_fit_tests_with_actual_qlft_data(fit_tests):
    """
    Parameters:
        fit_tests: pd.DataFrame
        Has the following columns
            'qualitative_normal_breathing_1',
            'qualitative_deep_breathing',
            'qualitative_head_side_to_side'
            'qualitative_head_up_and_down',
            'qualitative_talking'
            'qualitative_bend_over',
            'qualitative_normal_breathing_2'

    Returns: pd.DataFrame
        Has 'qlft_pass'
    """
    fit_tests_with_actual_qlft_data = fit_tests[
        ~fit_tests['qualitative_normal_breathing_1'].isna()
    ].copy()

    qualitative_tests = [
        'qualitative_normal_breathing_1',
        'qualitative_deep_breathing', 'qualitative_head_side_to_side',
        'qualitative_head_up_and_down', 'qualitative_talking',
        'qualitative_bend_over', 'qualitative_normal_breathing_2'
    ]

    fit_tests_with_actual_qlft_data['qlft_pass'] = (
        fit_tests_with_actual_qlft_data[
            qualitative_tests
        ] == 'Pass'
    ).sum(axis=1) == 7

    return fit_tests_with_actual_qlft_data

def set_too_small_or_too_big_as_instant_fail(fit_tests):
    """
    Parameters:
        fit_tests: pd.DataFrame
    """
    too_small_or_too_big = fit_tests[
        fit_tests['too_small_or_big'].isin(['Too small', 'Too big'])
    ].copy()
    too_small_or_too_big.loc[:, 'qlft_pass'] = 0

    return too_small_or_too_big

def set_qlft_pass(n99_mode_with_fit_tests_and_filtration_efficiency):
    """
    Parameters:
        n99_mode_with_fit_tests_and_filtration_efficiency: pd.DataFrame
            Has columns:
                n95_mode_estimate

    Returns: None
    """
    n99_mode_with_fit_tests_and_filtration_efficiency.loc[

        (~n99_mode_with_fit_tests_and_filtration_efficiency['n95_mode_estimate'].isna()),
        'qlft_pass'
    ] = n99_mode_with_fit_tests_and_filtration_efficiency['n95_mode_estimate'] >= 100

def prepare_masks(masks_path):
    """
    Read masks data. Add dummy variablse for strap_type and style.

    Parameters:
        masks_path: str
            CSV path of masks data.
            Has "strap_type", "style" as some of the columns.

    Returns: pd.DateFrame
    """
    masks = pd.read_csv(masks_path).set_index('id')

    masks = pd.concat(
        [
            masks,
            pd.get_dummies(masks['strap_type'])
        ],
        axis=1
    )

    masks = pd.concat(
        [
            masks,
            pd.get_dummies(masks['style'])
        ],
        axis=1
    )

    return masks

def prepare_fit_tests(fit_tests_path):
    fit_tests = pd.read_csv(fit_tests_path)
    fit_tests = preprocess_fit_tests(fit_tests)
    fit_tests = fit_tests.drop_duplicates(subset=['id'])

    return fit_tests

def prepare_facial_measurements(facial_measurements_path):
    facial_measurements = pd.read_csv(facial_measurements_path)
    facial_continuous_vars = [
        'face_width', 'jaw_width',
        'face_depth', 'face_length', 'lower_face_length',
        'bitragion_menton_arc', 'bitragion_subnasale_arc',
        'nose_bridge_height', 'lip_width', 'head_circumference',
        'nasal_root_breadth', 'nose_protrusion'
    ]

    facial_continuous = facial_measurements[
        facial_continuous_vars + ['manager_email', 'user_id', 'first_name', 'last_name']
    ]
    unique_facial_measurements = facial_continuous.drop_duplicates(subset='user_id').copy()

    return unique_facial_measurements.drop_duplicates(subset='user_id').copy()

def get_n99_filtration_efficiency_estimates(fit_tests):
    return fit_tests[
        (fit_tests['quantitative_testing_mode'] == 'N99') & \
        (
            (
                (fit_tests['quantitative_procedure'] == 'Full OSHA') & \
                (fit_tests['quantitative_ex_8_name'] == 'Normal breathing (SEALED)') & \
                (~fit_tests['quantitative_ex_8_fit_factor'].isna())
            ) | (
                (fit_tests['quantitative_procedure'] == 'OSHA Fast Filtering Face Piece Respirators') & \
                (fit_tests['quantitative_ex_4_name'] == 'Normal breathing (SEALED)') & \
                (~fit_tests['quantitative_ex_4_fit_factor'].isna())
            )
        )
    ].copy()

def get_max_n99_mode_ff(n99_results_with_filtration_efficiency_estimates):
    return n99_results_with_filtration_efficiency_estimates[
        n99_results_with_filtration_efficiency_estimates.columns[
            n99_results_with_filtration_efficiency_estimates.columns.str.contains('quantitative_ex_') & \
            n99_results_with_filtration_efficiency_estimates.columns.str.contains('_fit_factor')
        ]
    ].max(axis=1) + 1

def get_masks_with_max_n99_mode_ff(fit_tests, masks):
    n99_results_with_filtration_efficiency_estimates = get_n99_filtration_efficiency_estimates(fit_tests)
    n99_results_with_filtration_efficiency_estimates['max_n99_mode_ff'] = \
        get_max_n99_mode_ff(n99_results_with_filtration_efficiency_estimates)

    max_n99_mode_ff = pd.DataFrame(
        n99_results_with_filtration_efficiency_estimates.groupby('mask_id')['max_n99_mode_ff'].mean()
    )

    max_n99_mode_ff['filtration_efficiency_estimate_at_normal_breathing'] = 1 - 1 / max_n99_mode_ff['max_n99_mode_ff']

    max_n99_mode_ff = pd.DataFrame(n99_results_with_filtration_efficiency_estimates.groupby('mask_id')['max_n99_mode_ff'].mean())

    return masks.merge(max_n99_mode_ff, left_index=True, right_index=True)

def fill_n99_filtration_efficiency_potentially_using_others_data(fit_tests_joined_with_filtration_efficiency):
    """
    Creates 'n95_mode_estimate' column on N99-mode fit testing data and returns the dataframe.

    Parameters:
        fit_tests_joined_with_filtration_efficiency: pd.DataFrame
            Has the following columns
                quantitative_testing_mode
                max_n99_mode_ff
                quantitative_ex_1_name
                quantitative_ex_1_fit_factor
                ...

    Returns: pd.DataFrame
    """
    n99_mode_with_fit_tests_and_filtration_efficiency = fit_tests_joined_with_filtration_efficiency[
        (fit_tests_joined_with_filtration_efficiency['quantitative_testing_mode'] == 'N99')
    ]

    # Take the largest value across the row and add 1.
    n99_mode_with_fit_tests_and_filtration_efficiency['max_n99_ff'] = \
        n99_mode_with_fit_tests_and_filtration_efficiency[
            [
                'max_n99_mode_ff'
            ] + list(n99_mode_with_fit_tests_and_filtration_efficiency.columns[
                n99_mode_with_fit_tests_and_filtration_efficiency.columns.str.contains('quantitative_ex_') & \
                n99_mode_with_fit_tests_and_filtration_efficiency.columns.str.contains('_fit_factor')
            ])
        ].max(axis=1) + 1

    n99_mode_with_fit_tests_and_filtration_efficiency['n95_mode_estimate'] = \
        n99_mode_with_fit_tests_and_filtration_efficiency.apply(
            convert_n99_mode_scores_to_n95_mode,
            axis=1
        )

    return n99_mode_with_fit_tests_and_filtration_efficiency

if __name__ == '__main__':
    train()
