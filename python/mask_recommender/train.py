import numpy as np
import pandas as pd
import requests
import pymc as pm
import arviz as az
import os
from pymc.sampling.jax import sample_numpyro_nuts
from sklearn.preprocessing import StandardScaler

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

# 2. Main training script
def main():
    endpoint = 'https://www.breathesafe.xyz/facial_measurements_fit_tests.json'
    data = get_facial_measurements_with_fit_tests(endpoint)
    df = pd.DataFrame(data)

    # ... after loading df ...
    scaler = StandardScaler()
    facial_features = [
        'face_width', 'face_length', 'nose_protrusion',
        'bitragion_subnasale_arc', 'nose_bridge_height', 'nasal_root_breadth', 'perimeter_mm'
    ]
    df[facial_features] = scaler.fit_transform(df[facial_features])

    # Only keep relevant columns
    features = [
        'face_width',
        'face_length',
        'nose_protrusion',
        'bitragion_subnasale_arc',
        'nose_bridge_height',
        'nasal_root_breadth',
        'perimeter_mm',
        'mask_id',
        'qlft_pass'
    ]
    df = df[features]

    # Drop rows with missing values
    df = df.dropna()

    # Ensure correct types
    df['mask_id'] = df['mask_id'].astype(int)
    df['qlft_pass'] = df['qlft_pass'].astype(int)
    for col in features:
        if col != 'mask_id' and col != 'qlft_pass':
            df[col] = df[col].astype(float)

    # 3. Train/test split (80/20, randomized)
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
    n_train = int(0.8 * len(df))
    train_df = df.iloc[:n_train]
    test_df = df.iloc[n_train:]

    # 4. Prepare data for PyMC
    X_train = train_df[[
        'face_width',
        'face_length',
        'nose_protrusion',
        'bitragion_subnasale_arc',
        'nose_bridge_height',
        'nasal_root_breadth',
        'perimeter_mm',
        'mask_id'
    ]].copy()
    y_train = train_df['qlft_pass'].values
    mask_ids = X_train['mask_id'].unique()
    mask_id_to_idx = {mid: i for i, mid in enumerate(mask_ids)}
    X_train['mask_idx'] = X_train['mask_id'].map(mask_id_to_idx)
    mask_idx = X_train['mask_idx'].values
    perimeter_mm = X_train['perimeter_mm'].values
    # Facial measurements matrix (n_samples, n_features)
    facial_X = X_train[[
        'face_width',
        'face_length',
        'nose_protrusion',
        'bitragion_subnasale_arc',
        'nose_bridge_height',
        'nasal_root_breadth'
    ]].values

    # 5. Build PyMC model
    with pm.Model() as model:
        # Global multipliers for each facial measurement
        multipliers = pm.Normal('multipliers', mu=0, sigma=5, shape=facial_X.shape[1])

        # Mask-level random effects
        a_mask = pm.Normal('a_mask', mu=0, sigma=2, shape=len(mask_ids))
        c_mask = pm.Normal('c_mask', mu=0, sigma=5, shape=len(mask_ids))

        # Compute facial_sum for each sample
        facial_sum = pm.math.dot(facial_X, multipliers)  # shape (n_samples,)
        distance = (facial_sum - perimeter_mm) ** 2

        # Get mask-specific a and c for each sample
        a = a_mask[mask_idx]
        c = c_mask[mask_idx]

        logit_p = a * distance + c
        p = pm.math.sigmoid(logit_p)

        # Likelihood
        obs = pm.Bernoulli('obs', p=p, observed=y_train)

        # 6. Sample from the posterior
        trace = sample_numpyro_nuts(1000, tune=1000, target_accept=0.95)

    # 7. Posterior predictive checks and diagnostics
    print("\nModel summary:")
    print(az.summary(trace, var_names=['multipliers', 'a_mask', 'c_mask']))

    # Posterior predictive on train set
    # with model:
    #     ppc = pm.sample_posterior_predictive(trace, var_names=['obs'])
    # az.plot_ppc(az.from_pymc3(posterior_predictive=ppc, model=model, observed_data={'obs': y_train}))

    # Save trace to disk
    trace_path = 'pymc_trace.nc'
    print(f"\nSaving trace to {trace_path}")
    az.to_netcdf(trace, trace_path)

    # Diagnostics
    print("\nModel diagnostics:")
    print(az.plot_trace(trace, var_names=['multipliers', 'a_mask', 'c_mask']))
    print(az.plot_energy(trace))

    # 8. Evaluate on test set
    # Prepare test data
    X_test = test_df[[
        'face_width',
        'face_length',
        'nose_protrusion',
        'bitragion_subnasale_arc',
        'nose_bridge_height',
        'nasal_root_breadth',
        'perimeter_mm',
        'mask_id'
    ]].copy()
    y_test = test_df['qlft_pass'].values
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
    facial_X_test = X_test[[
        'face_width',
        'face_length',
        'nose_protrusion',
        'bitragion_subnasale_arc',
        'nose_bridge_height',
        'nasal_root_breadth'
    ]].values

    # Posterior predictive for test set
    with model:
        # Use posterior means for multipliers, a_mask, c_mask
        posterior = trace.posterior
        mean_multipliers = posterior['multipliers'].mean(dim=('chain', 'draw')).values
        mean_a_mask = posterior['a_mask'].mean(dim=('chain', 'draw')).values
        mean_c_mask = posterior['c_mask'].mean(dim=('chain', 'draw')).values
        facial_sum_test = np.dot(facial_X_test, mean_multipliers)
        distance_test = (facial_sum_test - perimeter_mm_test) ** 2
        a_test = mean_a_mask[mask_idx_test]
        c_test = mean_c_mask[mask_idx_test]
        logit_p_test = a_test * distance_test + c_test
        logit_p_test = np.clip(logit_p_test, -20, 20)
        p_test = 1 / (1 + np.exp(-logit_p_test))
        y_pred = (p_test > 0.5).astype(int)
        accuracy = (y_pred == y_test).mean()
        # Compute PPV and NPV
        tp = np.sum((y_pred == 1) & (y_test == 1))
        fp = np.sum((y_pred == 1) & (y_test == 0))
        tn = np.sum((y_pred == 0) & (y_test == 0))
        fn = np.sum((y_pred == 0) & (y_test == 1))
        ppv = tp / (tp + fp) if (tp + fp) > 0 else float('nan')
        npv = tn / (tn + fn) if (tn + fn) > 0 else float('nan')
        print(f"\nTest set accuracy: {accuracy:.3f} ({y_pred.sum()} positive predictions out of {len(y_pred)})")
        print(f"Test set PPV (precision): {ppv:.3f}")
        print(f"Test set NPV: {npv:.3f}")

if __name__ == '__main__':
    main()
