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
    return pd.cut(
        series,
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
            mask_bins.values[range(len(mask_bins)), mask_bins.columns.get_indexer(mask_codes)] = inference_rows[
                "perimeter_diff_bin_index"
            ].values
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
    encoded = pd.get_dummies(transformed, columns=categorical_columns, dummy_na=True)
    for column in feature_columns:
        if column not in encoded.columns:
            encoded[column] = 0
    encoded = encoded[feature_columns]
    encoded = encoded.apply(pd.to_numeric, errors="coerce").fillna(0).astype(float)
    return encoded
