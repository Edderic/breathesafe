import json
import re

import numpy as np
import pandas as pd

FACIAL_FEATURE_COLUMNS = [
    "nose_mm",
    "chin_mm",
    "top_cheek_mm",
    "mid_cheek_mm",
    "strap_mm",
]

FACIAL_PERIMETER_COMPONENTS = [
    "nose_mm",
    "chin_mm",
    "top_cheek_mm",
    "mid_cheek_mm",
]


def _extract_breakdown(current_state):
    if current_state is None or (isinstance(current_state, float) and pd.isna(current_state)):
        return []

    payload = current_state
    if isinstance(payload, str):
        raw = payload.strip()
        if not raw:
            return []
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    if not isinstance(payload, dict):
        return []

    # Common shape from Rails is:
    # {"current_state": {"breakdown": [{"3M":"brand"},{"Aura":"model"}, ...]}}
    nested = payload.get("current_state")
    if isinstance(nested, dict):
        breakdown = nested.get("breakdown")
    else:
        breakdown = payload.get("breakdown")

    return breakdown if isinstance(breakdown, list) else []


def _tokenize_mask_code(unique_internal_model_code):
    if unique_internal_model_code is None:
        return []
    text = str(unique_internal_model_code).strip()
    if not text:
        return []
    return [token for token in re.split(r"[\s\-—,\[\]\(\)/]+", text) if token]


def derive_brand_model(unique_internal_model_code, current_state=None):
    brand_tokens = []
    model_tokens = []

    breakdown = _extract_breakdown(current_state)
    for entry in breakdown:
        if not isinstance(entry, dict) or not entry:
            continue
        token, label = next(iter(entry.items()))
        label_normalized = str(label).strip().lower()
        token_normalized = str(token).strip()
        if not token_normalized:
            continue
        if label_normalized == "brand":
            brand_tokens.append(token_normalized)
        if label_normalized == "model":
            model_tokens.append(token_normalized)

    # Keep first-seen order while de-duplicating.
    brand_tokens = list(dict.fromkeys(brand_tokens))
    model_tokens = list(dict.fromkeys(model_tokens))

    brand = " ".join(brand_tokens).strip() if brand_tokens else None
    model = " ".join(model_tokens).strip() if model_tokens else None
    has_labeled_breakdown = bool(brand_tokens or model_tokens)

    fallback_tokens = _tokenize_mask_code(unique_internal_model_code)
    # Only infer brand/model from raw mask code when no labeled breakdown exists.
    # If breakdown explicitly contains only brand (or only model), preserve that.
    if not has_labeled_breakdown:
        if not brand and fallback_tokens:
            brand = fallback_tokens[0]
        if not model and len(fallback_tokens) > 1:
            model = fallback_tokens[1]

    parts = [part for part in [brand, model] if part]
    return " ".join(parts).strip()


def add_brand_model_column(frame):
    if frame is None or frame.empty:
        return frame

    current_state_series = frame.get("current_state")
    if current_state_series is None:
        current_state_series = pd.Series([None] * len(frame), index=frame.index)

    derived = [
        derive_brand_model(code, state)
        for code, state in zip(frame["unique_internal_model_code"], current_state_series)
    ]

    result = frame.copy()
    if "brand_model" in result.columns:
        existing = result["brand_model"].fillna("").astype(str).str.strip()
        result["brand_model"] = np.where(existing.ne(""), existing, derived)
    else:
        result["brand_model"] = derived

    return result


def diff_bin_edges():
    edges = [-float("inf")]
    edges.extend(list(range(-120, 121, 15)))
    edges.append(float("inf"))
    return edges


def diff_bin_labels():
    edges = diff_bin_edges()
    labels = []
    for left, right in zip(edges[:-1], edges[1:]):
        labels.append(f"diff_bin_{left}_to_{right}")
    return labels


def diff_bin_index(series):
    cleaned = pd.to_numeric(series, errors="coerce").fillna(0)
    return pd.cut(
        cleaned,
        bins=diff_bin_edges(),
        labels=False,
        right=False
    ).astype(int)


def apply_perimeter_features(
    inference_rows,
    use_facial_perimeter=False,
    use_diff_perimeter_bins=False,
    use_diff_perimeter_mask_bins=False
):
    if use_diff_perimeter_bins or use_diff_perimeter_mask_bins:
        inference_rows = inference_rows.copy()
        numeric_columns = FACIAL_PERIMETER_COMPONENTS + ["perimeter_mm"]
        inference_rows[numeric_columns] = (
            inference_rows[numeric_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )
        inference_rows["facial_perimeter_mm"] = inference_rows[FACIAL_PERIMETER_COMPONENTS].sum(axis=1)
        inference_rows["perimeter_diff"] = inference_rows["facial_perimeter_mm"] - inference_rows["perimeter_mm"]
        inference_rows["perimeter_diff_bin_index"] = diff_bin_index(inference_rows["perimeter_diff"])
        if use_diff_perimeter_bins:
            inference_rows["perimeter_diff_bin"] = pd.cut(
                inference_rows["perimeter_diff"],
                bins=diff_bin_edges(),
                labels=diff_bin_labels(),
                right=False
            )
            diff_dummies = pd.get_dummies(inference_rows["perimeter_diff_bin"])
            inference_rows = pd.concat([inference_rows, diff_dummies], axis=1)
        if use_diff_perimeter_mask_bins:
            mask_bins = pd.DataFrame(
                0,
                index=inference_rows.index,
                columns=inference_rows["unique_internal_model_code"].astype(str)
            )
            mask_bins = mask_bins.loc[:, ~mask_bins.columns.duplicated()]
            mask_codes = inference_rows["unique_internal_model_code"].astype(str)
            mask_indexer = mask_bins.columns.get_indexer(mask_codes)
            valid_mask = mask_indexer >= 0
            mask_bins_array = mask_bins.to_numpy(copy=True)
            row_positions = np.arange(len(mask_bins))[valid_mask]
            mask_bins_array[
                row_positions,
                mask_indexer[valid_mask]
            ] = inference_rows.loc[valid_mask, "perimeter_diff_bin_index"].values
            mask_bins = pd.DataFrame(mask_bins_array, index=mask_bins.index, columns=mask_bins.columns)
            mask_bins.columns = [f"mask_bin_{col}" for col in mask_bins.columns]
            inference_rows = pd.concat([inference_rows, mask_bins], axis=1)
        inference_rows = inference_rows.drop(
            columns=FACIAL_FEATURE_COLUMNS + [
                "perimeter_mm",
                "facial_perimeter_mm",
                "perimeter_diff",
                "perimeter_diff_bin",
                "perimeter_diff_bin_index"
            ],
            errors="ignore"
        )
        return inference_rows

    if use_facial_perimeter:
        inference_rows = inference_rows.copy()
        inference_rows["facial_perimeter_mm"] = inference_rows[FACIAL_PERIMETER_COMPONENTS].sum(axis=1)
        inference_rows = inference_rows.drop(columns=FACIAL_FEATURE_COLUMNS, errors="ignore")

    return inference_rows


def build_feature_frame(
    inference_rows,
    feature_columns,
    categorical_columns,
    use_facial_perimeter=False,
    use_diff_perimeter_bins=False,
    use_diff_perimeter_mask_bins=False,
):
    transformed = apply_perimeter_features(
        inference_rows,
        use_facial_perimeter=use_facial_perimeter,
        use_diff_perimeter_bins=use_diff_perimeter_bins,
        use_diff_perimeter_mask_bins=use_diff_perimeter_mask_bins
    )
    transformed = add_brand_model_column(transformed)


    for column in categorical_columns:
        if column not in transformed.columns:
            transformed[column] = ""
    encoded = pd.get_dummies(transformed, columns=categorical_columns, dummy_na=True)
    for column in feature_columns:
        if column not in encoded.columns:
            encoded[column] = 0
    encoded = encoded[feature_columns]
    encoded = encoded.apply(pd.to_numeric, errors="coerce").fillna(0).astype(float)
    return encoded
