import numpy as np
import pandas as pd
import requests
import pymc as pm
import arviz as az
import os
from pymc.sampling.jax import sample_numpyro_nuts
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss

print(pm.__version__)
os.environ["PYMC_EXPERIMENTAL_JAX"] = "1"

# 1. Data loading function (unchanged)
def get_facial_measurements_with_fit_tests(endpoint):
    try:
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        data = response.json()
        if 'fit_tests_with_facial_measurements' in data:
            return data['fit_tests_with_facial_measurements']
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Unexpected response format: {type(data)}")
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise


def scale_data(df, features):
    # ... after loading df ...
    features_to_scale = [
        k for k, v in features.items() if v['scalable']
    ]

    scaler = StandardScaler()
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale])


def ensure_correct_types(df, features_to_type_mapping):
    # Ensure correct types
    for k, v in features_to_type_mapping.items():
        df[k] = df[k].astype(v['data_type'])


def get_train_test_split(df):
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
    n_train = int(0.8 * len(df))

    return df.iloc[:n_train], df.iloc[n_train:]


def get_and_set_mask_idx(X_train):
    mask_ids = X_train['mask_id'].unique()
    mask_id_to_idx = {mid: i for i, mid in enumerate(mask_ids)}
    X_train['mask_idx'] = X_train['mask_id'].map(mask_id_to_idx)
    return mask_id_to_idx, X_train['mask_idx'].values


def encode_categorical_variables(df, categorical_cols):
    """Encode categorical variables as integers for PyMC"""
    encodings = {}
    for col in categorical_cols:
        if col in df.columns:
            unique_values = df[col].unique()
            value_to_idx = {val: i for i, val in enumerate(unique_values)}
            df[f'{col}_encoded'] = df[col].map(value_to_idx)
            encodings[col] = value_to_idx
    return encodings


def train_model(facial_X, mask_idx, y_train, perimeter_mm, facial_hair_beard_length_mm, strap_type_encoded):
    # 5. Build PyMC model
    with pm.Model() as model:
        # Global multipliers for each facial measurement
        multipliers = pm.Normal(
            'multipliers', mu=0, sigma=5, shape=facial_X.shape[1]
        )

        # Mask-level random effects
        a_mask = pm.Normal('a_mask', mu=0, sigma=2, shape=len(mask_idx))
        c_mask = pm.Normal('c_mask', mu=0, sigma=5, shape=len(mask_idx))

        # Strap type effects
        n_strap_types = len(np.unique(strap_type_encoded))
        strap_type_effect = pm.Normal('strap_type_effect', mu=0, sigma=1, shape=n_strap_types)

        # Facial hair
        facial_hair_multiplier = pm.Uniform('facial_hair_multiplier', lower=-10, upper=0)

        # Compute facial_sum for each sample
        facial_sum = pm.math.dot(facial_X, multipliers)  # shape (n_samples,)
        distance = (facial_sum - perimeter_mm) ** 2

        # Get mask-specific a and c for each sample
        a = a_mask[mask_idx]
        c = c_mask[mask_idx]

        # Get strap type effect for each sample
        strap_effect = strap_type_effect[strap_type_encoded]

        logit_p = a * distance + c + strap_effect + facial_hair_multiplier * facial_hair_beard_length_mm
        p = pm.math.sigmoid(logit_p)

        # Likelihood
        obs = pm.Bernoulli('obs', p=p, observed=y_train)

        # 6. Sample from the posterior
        trace = sample_numpyro_nuts(1000, tune=1000, target_accept=0.95)

    return model, trace
    # 7. Posterior predictive checks and diagnostics
    print("\nModel summary:")
    print(az.summary(trace, var_names=['multipliers', 'a_mask', 'c_mask', 'strap_type_effect', 'facial_hair_multiplier']))


def save_trace(
    trace,
    trace_path='pymc_trace.nc'
):
    print(f"\nsaving trace to {trace_path}")
    az.to_netcdf(trace, trace_path)


def show_diagnostics(trace):
    # Diagnostics
    print("\nModel diagnostics:")
    print(az.plot_trace(trace, var_names=['multipliers', 'a_mask', 'c_mask', 'strap_type_effect', 'facial_hair_multiplier']))
    print(az.plot_energy(trace))


def evaluate(
    model,
    trace,
    test_df,
    predictor_cols,
    facial_measurement_cols,
    mask_id_to_idx,
    testing_type,
    outcome_variable='qlft_pass',
):
    """
    Parameters:
        test_df: pd.DataFrame

        predictor_cols: list[str]

        facial_measurement_cols: list[str]

        mask_id_to_idx: dict
            Keys are mask_id
            idx is index

        outcome_variable: string. Defaults to 'qlft_pass'

    Returns: tuple(np.array, np.array)
        (y_pred, y_prob)
    """
    # 8. Evaluate on test set
    # Prepare test data
    X_test = test_df[predictor_cols].copy()
    y_test = test_df[outcome_variable].values
    X_test['mask_idx'] = X_test['mask_id'].map(mask_id_to_idx)
    mask_idx_test = X_test['mask_idx']

    # Find rows with NaN mask_idx (unseen mask_id in test set)
    nan_mask_rows = X_test[mask_idx_test.isna()]
    if not nan_mask_rows.empty:
        print("Warning: The following test rows have mask_id not seen in training and will be dropped:")
        print(nan_mask_rows[['mask_id']])
        # Drop these rows from test set
        X_test = X_test[mask_idx_test.notna()]
        y_test = y_test[mask_idx_test.notna()]
        mask_idx_test = X_test['mask_idx']

    # Now safe to convert to int
    mask_idx_test = mask_idx_test.astype(int).values

    perimeter_mm_test = X_test['perimeter_mm'].values
    facial_X_test = X_test[facial_measurement_cols].values

    # Posterior predictive for test set
    with model:
        # Use posterior means for multipliers, a_mask, c_mask
        posterior = trace.posterior
        mean_multipliers = posterior['multipliers'].mean(dim=('chain', 'draw')).values
        mean_a_mask = posterior['a_mask'].mean(dim=('chain', 'draw')).values
        mean_c_mask = posterior['c_mask'].mean(dim=('chain', 'draw')).values
        mean_strap_type_effect = posterior['strap_type_effect'].mean(dim=('chain', 'draw')).values
        facial_hair_multiplier = posterior['facial_hair_multiplier'].mean(dim=('chain', 'draw')).values
        facial_hair_beard_length_mm = X_test['facial_hair_beard_length_mm']
        strap_type_encoded_test = X_test['strap_type_encoded'].values

        facial_sum_test = np.dot(facial_X_test, mean_multipliers)
        distance_test = (facial_sum_test - perimeter_mm_test) ** 2
        a_test = mean_a_mask[mask_idx_test]
        c_test = mean_c_mask[mask_idx_test]
        strap_effect_test = mean_strap_type_effect[strap_type_encoded_test]
        logit_p_test = a_test * distance_test + c_test + strap_effect_test + facial_hair_beard_length_mm * facial_hair_multiplier
        logit_p_test = np.clip(logit_p_test, -20, 20)
        y_prob = 1 / (1 + np.exp(-logit_p_test))
        y_pred = (y_prob > 0.5).astype(int)
        accuracy = (y_pred == y_test).mean()
        # Compute PPV and NPV
        tp = np.sum((y_pred == 1) & (y_test == 1))
        fp = np.sum((y_pred == 1) & (y_test == 0))
        tn = np.sum((y_pred == 0) & (y_test == 0))
        fn = np.sum((y_pred == 0) & (y_test == 1))
        ppv = tp / (tp + fp) if (tp + fp) > 0 else float('nan')
        npv = tn / (tn + fn) if (tn + fn) > 0 else float('nan')
        print(f"\n{testing_type} set accuracy: {accuracy:.3f} ({y_pred.sum()} positive predictions out of {len(y_pred)})")
        print(f"{testing_type} set PPV (precision): {ppv:.3f}")
        print(f"{testing_type} set NPV: {npv:.3f}")

        # Calculate log loss
        test_log_loss = log_loss(y_test, y_prob)
        print(f"{testing_type} set log loss: {test_log_loss:.3f}")

        return y_pred, y_prob

def presum_log_loss(y_true, y_prob):
    return -(y_true * np.log(y_prob) + (1 - y_true) * np.log(1 - y_prob))


# 2. Main training script
def main():
    endpoint = 'https://www.breathesafe.xyz/facial_measurements_fit_tests.json'
    data = get_facial_measurements_with_fit_tests(endpoint)
    df = pd.DataFrame(data)
    outcome_variable = 'qlft_pass'

    features_to_type_mapping = {
        'face_width': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': True,
        },
        'face_length': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': True,
        },
        'bitragion_subnasale_arc': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': True,
        },
        'nose_bridge_height': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': True,
        },
        'nasal_root_breadth': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': True,
        },
        'nose_protrusion': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': True,
        },
        'facial_hair_beard_length_mm': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': False,
        },
        'perimeter_mm': {
            'data_type': float,
            'scalable': True,
            'facial_measurement': False,
        },
        'mask_id': {
            'data_type': int,
            'scalable': False,
            'facial_measurement': False,
        },
        'qlft_pass': {
            'data_type': int,
            'scalable': False,
            'facial_measurement': False,
        },
        'strap_type': {
            'data_type': str,
            'scalable': False,
            'facial_measurement': False,
        },
        'style': {
            'data_type': str,
            'scalable': False,
            'facial_measurement': False,
        }
    }

    scale_data(df, features_to_type_mapping)
    predictor_cols = [
        k for k, v in features_to_type_mapping.items() if k != outcome_variable
    ]

    # Filter out rows with extreme z-scores for facial measurements
    facial_measurement_cols = [k for k, v in features_to_type_mapping.items() if v['facial_measurement']]
    z_score_cols = [f"{col}_z_score" for col in facial_measurement_cols]

    # Check if z-score columns exist in the data
    existing_z_score_cols = [col for col in z_score_cols if col in df.columns]
    if existing_z_score_cols:
        # Convert z-score columns to numeric, coercing errors to NaN
        for col in existing_z_score_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Create mask for rows to keep (z-scores within ±2.25, excluding NaN values)
        keep_mask = pd.Series([True] * len(df), index=df.index)
        for col in existing_z_score_cols:
            # Keep rows where z-score is NaN (missing) or within ±2.25
            keep_mask &= (df[col].isna() | (df[col].abs() <= 2.25))

        initial_count = len(df)
        df = df[keep_mask].reset_index(drop=True)
        filtered_count = initial_count - len(df)
        print(f"Filtered out {filtered_count} rows with extreme z-scores (|z| > 2.25) out of {initial_count} total rows")
    else:
        print("No z-score columns found in data, skipping z-score filtering")

    unique_internal_model_code_to_mask_id = pd.DataFrame(data).groupby(['unique_internal_model_code', 'mask_id', 'style', 'strap_type']).count().rename(columns={'id': 'count'})[['count']]
    unique_internal_model_code_to_mask_id

    # Only keep relevant columns
    features_to_keep = [k for k, v in features_to_type_mapping.items()]
    df = df[features_to_keep]

    # Drop rows with missing values
    df = df.dropna()

    # Encode categorical variables
    categorical_cols = ['strap_type', 'style']
    encodings = encode_categorical_variables(df, categorical_cols)

    # Add encoded columns to predictor columns
    for col in categorical_cols:
        if f'{col}_encoded' in df.columns:
            predictor_cols.append(f'{col}_encoded')

    ensure_correct_types(df, features_to_type_mapping)

    # 3. Train/test split (80/20, randomized)
    train_df, test_df = get_train_test_split(df)

    # 4. Prepare data for PyMC
    X_train = train_df[predictor_cols].copy()
    y_train = train_df[outcome_variable].values
    mask_id_to_idx, mask_idx = get_and_set_mask_idx(X_train)
    perimeter_mm = X_train['perimeter_mm'].values
    # Facial measurements matrix (n_samples, n_features)
    facial_measurement_cols = [
        k for k, v in features_to_type_mapping.items() if v['facial_measurement']
    ]

    facial_X = X_train[facial_measurement_cols].values
    facial_hair = X_train['facial_hair_beard_length_mm']

    # Encode strap types
    strap_type_encoded = X_train['strap_type_encoded'].values

    model, trace = train_model(facial_X, mask_idx, y_train, perimeter_mm, facial_hair, strap_type_encoded)

    # Posterior predictive on train set
    # with model:
    #     ppc = pm.sample_posterior_predictive(trace, var_names=['obs'])
    # az.plot_ppc(az.from_pymc3(posterior_predictive=ppc, model=model, observed_data={'obs': y_train}))
    # Save trace to disk
    save_trace(trace)
    show_diagnostics(trace)

    print("Doing evaluation on training set...")
    y_pred_train, y_prob_train = evaluate(
        model=model,
        trace=trace,
        test_df=train_df,
        predictor_cols=predictor_cols,
        facial_measurement_cols=facial_measurement_cols,
        mask_id_to_idx=mask_id_to_idx,
        outcome_variable=outcome_variable,
        testing_type="Training"
    )

    print("Doing evaluation on test set...")
    y_pred_test, y_prob_test = evaluate(
        model=model,
        trace=trace,
        test_df=test_df,
        predictor_cols=predictor_cols,
        facial_measurement_cols=facial_measurement_cols,
        mask_id_to_idx=mask_id_to_idx,
        outcome_variable=outcome_variable,
        testing_type="Test"
    )


    train_df_copy = train_df.copy()
    train_df_copy['y_pred'] = y_pred_train
    train_df_copy['y_prob'] = y_prob_train
    train_df_copy['presum_log_loss'] = presum_log_loss(train_df[outcome_variable].values, y_prob_train)
    train_df_copy

    train_df_copy_with_mask_names = unique_internal_model_code_to_mask_id\
        .reset_index()\
        .set_index('mask_id')\
        .merge( train_df_copy, left_index=True, right_on='mask_id')

    train_df_copy_with_mask_names

    import pdb; pdb.set_trace()
    # Which mask_ids are harder to make good predictions on?
    #
    train_df_copy_with_mask_names.columns
    train_df_copy_with_mask_names.groupby(['unique_internal_model_code', 'strap_type_encoded','style_encoded'])['presum_log_loss'].mean().sort_values()
    train_df_copy_with_mask_names.groupby('unique_internal_model_code')['presum_log_loss'].mean().sort_values()

    train_df_copy_with_mask_names[train_df_copy_with_mask_names['unique_internal_model_code'].str.contains('9601')]
    train_df_copy_with_mask_names[train_df_copy_with_mask_names['unique_internal_model_code'].str.contains('9601')].iloc[0]
    train_df_copy_with_mask_names[train_df_copy_with_mask_names['unique_internal_model_code'].str.contains('9601')].iloc[1]
    # )
    train_df_copy_with_mask_names[train_df_copy_with_mask_names['unique_internal_model_code'].str.contains('blox')]
    # What if we split the data into boat & duckbill vs. cup, bifold, bifold +
    # gasket?


if __name__ == '__main__':
    main()
