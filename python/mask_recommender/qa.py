import json
from datetime import datetime, timezone

import pandas as pd
from data_prep import FACIAL_FEATURE_COLUMNS, normalize_pass


def build_mask_candidates(masks_df):
    mask_candidates = masks_df.copy()
    mask_candidates = mask_candidates[
        mask_candidates['perimeter_mm'].notna() &
        (mask_candidates['perimeter_mm'] > 0) &
        mask_candidates['strap_type'].notna() &
        mask_candidates['style'].notna() &
        mask_candidates['unique_internal_model_code'].notna()
    ]
    mask_candidates = mask_candidates[
        mask_candidates['strap_type'].astype(str).str.strip().ne('') &
        mask_candidates['style'].astype(str).str.strip().ne('') &
        mask_candidates['unique_internal_model_code'].astype(str).str.strip().ne('')
    ]
    return mask_candidates


def get_latest_user_features(user_id, fit_tests_df):
    user_rows = fit_tests_df[fit_tests_df['user_id'] == user_id]
    if user_rows.empty:
        return None
    user_rows = user_rows.dropna(subset=FACIAL_FEATURE_COLUMNS)
    if user_rows.empty:
        return None
    user_rows = user_rows.copy()
    if 'created_at' in user_rows.columns:
        user_rows['created_at_parsed'] = pd.to_datetime(user_rows['created_at'], errors='coerce')
        user_rows = user_rows.sort_values(by='created_at_parsed', ascending=False)
    return user_rows.iloc[0]


def build_ground_truth_map(user_id, fit_tests_df):
    user_rows = fit_tests_df[fit_tests_df['user_id'] == user_id].copy()
    if user_rows.empty:
        return {}
    if 'created_at' in user_rows.columns:
        user_rows['created_at_parsed'] = pd.to_datetime(user_rows['created_at'], errors='coerce')
        user_rows = user_rows.sort_values(by='created_at_parsed', ascending=False)
    ground_truth = {}
    for _, row in user_rows.iterrows():
        mask_id = row.get('mask_id')
        if pd.isna(mask_id) or mask_id in ground_truth:
            continue
        normalized = normalize_pass(row.get('qlft_pass'))
        if normalized is None:
            ground_truth[int(mask_id)] = None
        else:
            ground_truth[int(mask_id)] = 'pass' if normalized == 1 else 'fail'
    return ground_truth


def build_inference_rows(user_row, mask_candidates):
    base_features = {
        'perimeter_mm': mask_candidates['perimeter_mm'].to_numpy(),
        'facial_hair_beard_length_mm': user_row.get('facial_hair_beard_length_mm') or 0,
        'strap_type': mask_candidates['strap_type'].to_numpy(),
        'style': mask_candidates['style'].to_numpy(),
        'unique_internal_model_code': mask_candidates['unique_internal_model_code'].to_numpy(),
    }
    for column in FACIAL_FEATURE_COLUMNS:
        base_features[column] = user_row.get(column)
    return pd.DataFrame(base_features)


def build_recommendation_preview(
    user_ids,
    fit_tests_df,
    mask_candidates,
    predict_fn,
    output_path=None,
    threshold=0.5,
):
    recommendation_output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'users': []
    }

    for user_id in user_ids:
        user_row = get_latest_user_features(user_id, fit_tests_df)
        if user_row is None:
            continue

        inference_rows = build_inference_rows(user_row, mask_candidates)
        probs = predict_fn(inference_rows)

        ground_truth = build_ground_truth_map(user_id, fit_tests_df)
        recommendations = []
        for idx, mask_row in mask_candidates.reset_index(drop=True).iterrows():
            mask_id = int(mask_row['id'])
            recommendations.append({
                'user_id': int(user_id),
                'mask_id': mask_id,
                'unique_internal_model_code': mask_row.get('unique_internal_model_code', ''),
                'probability_of_fit': float(probs[idx]),
                'ground_truth': ground_truth.get(mask_id)
            })
        recommendations.sort(key=lambda row: row['probability_of_fit'], reverse=True)

        eval_rows = [row for row in recommendations if row['ground_truth'] in ('pass', 'fail')]
        precision = None
        recall = None
        if eval_rows:
            preds = [1 if row['probability_of_fit'] >= threshold else 0 for row in eval_rows]
            labels = [1 if row['ground_truth'] == 'pass' else 0 for row in eval_rows]
            true_pos = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 1)
            false_pos = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 0)
            false_neg = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 1)
            precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0.0
            recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0.0

        recommendation_output['users'].append({
            'user_id': int(user_id),
            'feature_source_fit_test_id': int(user_row.get('id')),
            'metrics': {
                'threshold': threshold,
                'precision': precision,
                'recall': recall,
                'ground_truth_count': len(eval_rows)
            },
            'recommendations': recommendations
        })

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(recommendation_output, handle, indent=2)

    return recommendation_output
