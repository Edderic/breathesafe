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

STYLE_INTERACTION_PREFIX = "style_term_"
PERIMETER_DIFF_STYLE_PREFIX = "perimeter_diff_x_"
ABS_PERIMETER_DIFF_STYLE_PREFIX = "abs_perimeter_diff_x_"
PERIMETER_DIFF_SQ_STYLE_PREFIX = "perimeter_diff_sq_x_"
STRAP_STYLE_INTERACTION_PREFIX = "strap_style_x_"
FACE_STYLE_INTERACTION_PREFIX = "face_style_x_"
MM_PER_CM = 10.0
# Increase style-specific penalty from squared perimeter mismatch so large
# perimeter/style mismatches influence ranking more strongly.
ABS_PERIMETER_DIFF_STYLE_INTERACTION_MULTIPLIER = 6.0
PERIMETER_DIFF_SQ_STYLE_INTERACTION_MULTIPLIER = 25.0

STRAP_FEATURE_COLUMNS = [
    "strap_is_earloop_like",
    "strap_is_headstrap_like",
    "strap_is_adjustable",
    "strap_type_strength",
]

FACE_SHAPE_FEATURE_COLUMNS = [
    "facial_perimeter_cm",
    "strap_ratio",
    "nose_ratio",
    "chin_ratio",
    "top_cheek_ratio",
    "mid_cheek_ratio",
    "chin_to_nose_ratio",
    "top_to_mid_cheek_ratio",
    "strap_minus_perimeter_cm",
    "nose_sq_cm2",
    "chin_sq_cm2",
    "top_cheek_sq_cm2",
    "mid_cheek_sq_cm2",
    "strap_sq_cm2",
]

MASK_SIZE_FEATURE_COLUMNS = [
    "mask_face_size_rank",
    "mask_face_size_is_xs",
    "mask_face_size_is_s",
    "mask_face_size_is_regular",
    "mask_face_size_is_large",
    "mask_face_size_is_xxl",
    "mask_face_size_anchor_cm",
    "face_size_gap_cm",
    "abs_face_size_gap_cm",
    "face_size_gap_sq",
    "mask_strap_length_rank",
    "mask_strap_length_is_extended",
    "mask_size_face_perimeter_match",
    "mask_size_chin_match",
    "mask_size_top_cheek_match",
    "mask_strap_length_strap_match",
]

PERIMETER_PENALTY_FEATURE_COLUMNS = [
    "abs_perimeter_diff_gt_1cm",
    "abs_perimeter_diff_gt_2cm",
    "abs_perimeter_diff_gt_3cm",
    "abs_perimeter_diff_gt_4cm",
    "abs_perimeter_diff_gt_5cm",
    "bifold_abs_diff_gt_1cm",
    "bifold_abs_diff_gt_2cm",
    "cup_abs_diff_gt_2cm",
    "cup_abs_diff_gt_3cm",
    "boat_duckbill_positive_diff_gt_2cm",
    "boat_duckbill_negative_diff_ok_band",
    "earloop_abs_diff",
    "earloop_abs_diff_sq",
    "earloop_and_diff_gt_2cm",
    "earloop_and_diff_gt_3cm",
    "headstrap_abs_diff",
    "abs_face_size_gap_gt_2cm",
    "abs_face_size_gap_gt_4cm",
    "face_too_large_for_mask_gt_2cm",
    "face_too_small_for_mask_gt_2cm",
    "xs_large_face_penalty",
    "s_large_face_penalty",
    "petite_large_face_penalty",
    "kids_large_face_penalty",
    "small_mask_large_face_gt_30cm",
]

MASK_EMPIRICAL_FEATURE_COLUMNS = [
    "mask_fit_test_count",
    "mask_smoothed_pass_rate",
    "mask_log_fit_test_count",
    "mask_smoothed_pass_logit",
    "mask_empirical_badness",
    "mask_zero_passes_min_5",
    "mask_zero_passes_min_10",
    "mask_fail_only_rate",
    "mask_badness_x_abs_perimeter_diff",
    "mask_zero_passes_min_10_x_earloop",
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


def _size_tokens_from_breakdown(current_state):
    tokens = []
    for entry in _extract_breakdown(current_state):
        if not isinstance(entry, dict) or not entry:
            continue
        token, label = next(iter(entry.items()))
        label_normalized = str(label).strip().lower()
        if label_normalized not in {"size", "strap_length", "strap_size"}:
            continue
        normalized = str(token).strip()
        if normalized:
            tokens.append(normalized.lower())
    return tokens


def _normalized_mask_code_text(unique_internal_model_code, current_state=None):
    parts = []
    if unique_internal_model_code:
        parts.append(str(unique_internal_model_code).lower())
    parts.extend(_size_tokens_from_breakdown(current_state))
    return " ".join(parts)


def parse_mask_sizing(unique_internal_model_code, current_state=None):
    text = _normalized_mask_code_text(unique_internal_model_code, current_state=current_state)

    face_size_rank = 0.0
    face_size_bucket = "regular"
    strap_length_rank = 0.0
    strap_length_bucket = "regular"

    if "xxxl" in text or "triple extra large" in text:
        face_size_rank = 4.0
        face_size_bucket = "xxl"
    elif "xxl" in text or "double extra large" in text or "extra large" in text:
        face_size_rank = 3.0
        face_size_bucket = "xxl"
    elif re.search(r"(^|[^a-z])xs([^a-z]|$)", text) or "x-small" in text or "extra small" in text:
        face_size_rank = -2.0
        face_size_bucket = "xs"
    elif re.search(r"(^|[^a-z])s([^a-z]|$)", text) or "small" in text or "petite" in text:
        face_size_rank = -1.0
        face_size_bucket = "s"
    elif "regular/large" in text or "regular large" in text:
        face_size_rank = 1.0
        face_size_bucket = "large"
    elif "large" in text or "medium / large" in text or "medium/large" in text:
        face_size_rank = 1.0
        face_size_bucket = "large"
    elif "regular" in text or "medium" in text:
        face_size_rank = 0.0
        face_size_bucket = "regular"

    if "extended length" in text or "extended straps" in text or "extended strap" in text:
        strap_length_rank = 1.0
        strap_length_bucket = "extended"

    return {
        "mask_face_size_rank": face_size_rank,
        "mask_face_size_bucket": face_size_bucket,
        "mask_strap_length_rank": strap_length_rank,
        "mask_strap_length_bucket": strap_length_bucket,
    }


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


def add_mask_size_features(frame):
    if frame is None or frame.empty:
        return frame
    if "unique_internal_model_code" not in frame.columns:
        return frame

    result = frame.copy()
    current_state_series = result.get("current_state")
    if current_state_series is None:
        current_state_series = pd.Series([None] * len(result), index=result.index)

    sizing = [
        parse_mask_sizing(code, state)
        for code, state in zip(result["unique_internal_model_code"], current_state_series)
    ]
    sizing_frame = pd.DataFrame(sizing, index=result.index)
    result["mask_face_size_rank"] = sizing_frame["mask_face_size_rank"].astype(float)
    result["mask_strap_length_rank"] = sizing_frame["mask_strap_length_rank"].astype(float)
    result["mask_face_size_is_xs"] = (sizing_frame["mask_face_size_bucket"] == "xs").astype(float)
    result["mask_face_size_is_s"] = (sizing_frame["mask_face_size_bucket"] == "s").astype(float)
    result["mask_face_size_is_regular"] = (sizing_frame["mask_face_size_bucket"] == "regular").astype(float)
    result["mask_face_size_is_large"] = (sizing_frame["mask_face_size_bucket"] == "large").astype(float)
    result["mask_face_size_is_xxl"] = (sizing_frame["mask_face_size_bucket"] == "xxl").astype(float)
    result["mask_strap_length_is_extended"] = (
        sizing_frame["mask_strap_length_bucket"] == "extended"
    ).astype(float)
    return result


def add_style_perimeter_interactions(frame):
    if frame is None or frame.empty:
        return frame
    if "style" not in frame.columns:
        return frame
    if "perimeter_diff" not in frame.columns or "perimeter_diff_sq" not in frame.columns:
        return frame

    result = frame.copy()
    if "abs_perimeter_diff" not in result.columns:
        result["abs_perimeter_diff"] = result["perimeter_diff"].abs()
    style_series = result["style"].fillna("unknown").astype(str).str.strip()
    style_series = style_series.replace("", "unknown")
    style_dummies = pd.get_dummies(style_series, prefix=STYLE_INTERACTION_PREFIX.rstrip("_"))

    for column in style_dummies.columns:
        result[f"{PERIMETER_DIFF_STYLE_PREFIX}{column}"] = result["perimeter_diff"] * style_dummies[column]
        result[f"{ABS_PERIMETER_DIFF_STYLE_PREFIX}{column}"] = (
            result["abs_perimeter_diff"]
            * style_dummies[column]
            * ABS_PERIMETER_DIFF_STYLE_INTERACTION_MULTIPLIER
        )
        result[f"{PERIMETER_DIFF_SQ_STYLE_PREFIX}{column}"] = (
            result["perimeter_diff_sq"]
            * style_dummies[column]
            * PERIMETER_DIFF_SQ_STYLE_INTERACTION_MULTIPLIER
        )

    return result


def scale_perimeter_diff_features(frame):
    """Convert perimeter difference features from mm-space to cm-space."""
    if frame is None or frame.empty:
        return frame
    if "perimeter_diff" not in frame.columns:
        return frame

    result = frame.copy()
    result["perimeter_diff"] = result["perimeter_diff"] / MM_PER_CM
    result["abs_perimeter_diff"] = result["perimeter_diff"].abs()
    if "perimeter_diff_sq" in result.columns:
        result["perimeter_diff_sq"] = result["perimeter_diff_sq"] / (MM_PER_CM ** 2)
    result["abs_perimeter_diff_gt_1cm"] = (result["abs_perimeter_diff"] >= 1.0).astype(float)
    result["abs_perimeter_diff_gt_2cm"] = (result["abs_perimeter_diff"] >= 2.0).astype(float)
    result["abs_perimeter_diff_gt_3cm"] = (result["abs_perimeter_diff"] >= 3.0).astype(float)
    result["abs_perimeter_diff_gt_4cm"] = (result["abs_perimeter_diff"] >= 4.0).astype(float)
    result["abs_perimeter_diff_gt_5cm"] = (result["abs_perimeter_diff"] >= 5.0).astype(float)
    return result


def add_geometry_penalty_features(frame):
    if frame is None or frame.empty:
        return frame

    required_columns = [
        "style",
        "perimeter_diff",
        "abs_perimeter_diff",
        "perimeter_diff_sq",
        "strap_is_earloop_like",
        "strap_is_headstrap_like",
        "facial_perimeter_cm",
        "face_size_gap_cm",
        "abs_face_size_gap_cm",
        "mask_face_size_is_xs",
        "mask_face_size_is_s",
    ]
    if any(column not in frame.columns for column in required_columns):
        return frame

    result = frame.copy()
    style_series = result["style"].fillna("").astype(str).str.strip().str.lower()
    is_bifold = style_series.isin(["bifold", "bifold & gasket"])
    is_cup = style_series.eq("cup")
    is_boat_or_duckbill = style_series.isin(["boat", "duckbill"])

    result["bifold_abs_diff_gt_1cm"] = (
        is_bifold & (result["abs_perimeter_diff"] >= 1.0)
    ).astype(float)
    result["bifold_abs_diff_gt_2cm"] = (
        is_bifold & (result["abs_perimeter_diff"] >= 2.0)
    ).astype(float)
    result["cup_abs_diff_gt_2cm"] = (
        is_cup & (result["abs_perimeter_diff"] >= 2.0)
    ).astype(float)
    result["cup_abs_diff_gt_3cm"] = (
        is_cup & (result["abs_perimeter_diff"] >= 3.0)
    ).astype(float)
    result["boat_duckbill_positive_diff_gt_2cm"] = (
        is_boat_or_duckbill & (result["perimeter_diff"] >= 2.0)
    ).astype(float)
    result["boat_duckbill_negative_diff_ok_band"] = (
        is_boat_or_duckbill
        & (result["perimeter_diff"] <= -1.0)
        & (result["perimeter_diff"] >= -6.0)
    ).astype(float)

    result["earloop_abs_diff"] = result["strap_is_earloop_like"] * result["abs_perimeter_diff"]
    result["earloop_abs_diff_sq"] = result["strap_is_earloop_like"] * result["perimeter_diff_sq"]
    result["earloop_and_diff_gt_2cm"] = (
        result["strap_is_earloop_like"].astype(bool) & (result["abs_perimeter_diff"] >= 2.0)
    ).astype(float)
    result["earloop_and_diff_gt_3cm"] = (
        result["strap_is_earloop_like"].astype(bool) & (result["abs_perimeter_diff"] >= 3.0)
    ).astype(float)
    result["headstrap_abs_diff"] = result["strap_is_headstrap_like"] * result["abs_perimeter_diff"]
    result["abs_face_size_gap_gt_2cm"] = (result["abs_face_size_gap_cm"] >= 2.0).astype(float)
    result["abs_face_size_gap_gt_4cm"] = (result["abs_face_size_gap_cm"] >= 4.0).astype(float)
    result["face_too_large_for_mask_gt_2cm"] = (result["face_size_gap_cm"] >= 2.0).astype(float)
    result["face_too_small_for_mask_gt_2cm"] = (result["face_size_gap_cm"] <= -2.0).astype(float)

    code_series = result.get("unique_internal_model_code")
    if code_series is None:
        code_series = pd.Series([""] * len(result), index=result.index)
    code_text = code_series.fillna("").astype(str).str.lower()
    facial_perimeter_excess = (result["facial_perimeter_cm"] - 24.0).clip(lower=0.0)
    petite_flag = code_text.str.contains("petite", regex=False)
    kids_flag = code_text.str.contains(r"\bkids?\b|\bchild(?:ren)?\b|\byouth\b", regex=True)

    result["xs_large_face_penalty"] = result["mask_face_size_is_xs"] * facial_perimeter_excess
    result["s_large_face_penalty"] = result["mask_face_size_is_s"] * facial_perimeter_excess
    result["petite_large_face_penalty"] = petite_flag.astype(float) * facial_perimeter_excess
    result["kids_large_face_penalty"] = kids_flag.astype(float) * facial_perimeter_excess
    result["small_mask_large_face_gt_30cm"] = (
        (result["facial_perimeter_cm"] >= 30.0)
        & (
            result["mask_face_size_is_xs"].astype(bool)
            | result["mask_face_size_is_s"].astype(bool)
            | petite_flag
            | kids_flag
        )
    ).astype(float)

    return result


def add_strap_type_features(frame):
    if frame is None or frame.empty:
        return frame

    result = frame.copy()
    strap_series = result.get("strap_type")
    if strap_series is None:
        strap_series = pd.Series([""] * len(result), index=result.index)
    strap_series = strap_series.fillna("").astype(str).str.strip().str.lower()

    is_earloop = strap_series.isin(["earloop", "adjustable earloop"])
    is_headstrap = strap_series.isin(["headstrap", "adjustable headstrap"])
    is_adjustable = strap_series.str.contains("adjustable", regex=False)

    strength_map = {
        "earloop": -2.0,
        "adjustable earloop": -1.4,
        "headstrap": 0.8,
        "adjustable headstrap": 1.0,
        "strapless": -0.2,
    }
    strap_strength = strap_series.map(strength_map).fillna(0.0)

    result["strap_is_earloop_like"] = is_earloop.astype(float)
    result["strap_is_headstrap_like"] = is_headstrap.astype(float)
    result["strap_is_adjustable"] = is_adjustable.astype(float)
    result["strap_type_strength"] = strap_strength.astype(float)
    return result


def add_strap_style_interactions(frame):
    if frame is None or frame.empty:
        return frame
    if "style" not in frame.columns:
        return frame

    required_strap_features = [
        "strap_is_earloop_like",
        "strap_is_headstrap_like",
        "strap_is_adjustable",
        "strap_type_strength",
    ]
    if any(column not in frame.columns for column in required_strap_features):
        return frame

    result = frame.copy()
    style_series = result["style"].fillna("unknown").astype(str).str.strip()
    style_series = style_series.replace("", "unknown")
    style_dummies = pd.get_dummies(style_series, prefix=STYLE_INTERACTION_PREFIX.rstrip("_"))

    for style_column in style_dummies.columns:
        style_mask = style_dummies[style_column]
        for strap_column in required_strap_features:
            interaction_column = (
                f"{STRAP_STYLE_INTERACTION_PREFIX}{strap_column}_x_{style_column}"
            )
            result[interaction_column] = result[strap_column] * style_mask

    return result


def add_face_shape_features(frame):
    if frame is None or frame.empty:
        return frame

    required_columns = FACIAL_FEATURE_COLUMNS + ["perimeter_mm"]
    if any(column not in frame.columns for column in required_columns):
        return frame

    result = frame.copy()
    numeric_columns = required_columns
    result[numeric_columns] = (
        result[numeric_columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

    facial_perimeter_mm = result[FACIAL_PERIMETER_COMPONENTS].sum(axis=1)
    facial_perimeter_mm_safe = facial_perimeter_mm.replace(0, np.nan)

    result["facial_perimeter_mm"] = facial_perimeter_mm
    result["facial_perimeter_cm"] = facial_perimeter_mm / MM_PER_CM
    result["strap_ratio"] = (result["strap_mm"] / facial_perimeter_mm_safe).fillna(0)
    result["nose_ratio"] = (result["nose_mm"] / facial_perimeter_mm_safe).fillna(0)
    result["chin_ratio"] = (result["chin_mm"] / facial_perimeter_mm_safe).fillna(0)
    result["top_cheek_ratio"] = (result["top_cheek_mm"] / facial_perimeter_mm_safe).fillna(0)
    result["mid_cheek_ratio"] = (result["mid_cheek_mm"] / facial_perimeter_mm_safe).fillna(0)

    nose_safe = result["nose_mm"].replace(0, np.nan)
    mid_cheek_safe = result["mid_cheek_mm"].replace(0, np.nan)
    result["chin_to_nose_ratio"] = (result["chin_mm"] / nose_safe).fillna(0)
    result["top_to_mid_cheek_ratio"] = (result["top_cheek_mm"] / mid_cheek_safe).fillna(0)
    result["strap_minus_perimeter_cm"] = (result["strap_mm"] - facial_perimeter_mm) / MM_PER_CM

    result["nose_sq_cm2"] = (result["nose_mm"] / MM_PER_CM) ** 2
    result["chin_sq_cm2"] = (result["chin_mm"] / MM_PER_CM) ** 2
    result["top_cheek_sq_cm2"] = (result["top_cheek_mm"] / MM_PER_CM) ** 2
    result["mid_cheek_sq_cm2"] = (result["mid_cheek_mm"] / MM_PER_CM) ** 2
    result["strap_sq_cm2"] = (result["strap_mm"] / MM_PER_CM) ** 2
    return result


def add_mask_size_face_interactions(frame):
    if frame is None or frame.empty:
        return frame
    required_columns = [
        "mask_face_size_rank",
        "mask_strap_length_rank",
        "facial_perimeter_cm",
        "chin_mm",
        "top_cheek_mm",
        "strap_mm",
        "strap_ratio",
    ]
    if any(column not in frame.columns for column in required_columns):
        return frame

    result = frame.copy()
    result["mask_face_size_anchor_cm"] = (
        result["mask_face_size_is_xs"] * 22.0
        + result["mask_face_size_is_s"] * 25.0
        + result["mask_face_size_is_regular"] * 29.0
        + result["mask_face_size_is_large"] * 33.0
        + result["mask_face_size_is_xxl"] * 36.0
    )
    result["face_size_gap_cm"] = result["facial_perimeter_cm"] - result["mask_face_size_anchor_cm"]
    result["abs_face_size_gap_cm"] = result["face_size_gap_cm"].abs()
    result["face_size_gap_sq"] = result["face_size_gap_cm"] ** 2
    result["mask_size_face_perimeter_match"] = (
        result["mask_face_size_rank"] * result["facial_perimeter_cm"]
    )
    result["mask_size_chin_match"] = (
        result["mask_face_size_rank"] * (result["chin_mm"] / MM_PER_CM)
    )
    result["mask_size_top_cheek_match"] = (
        result["mask_face_size_rank"] * (result["top_cheek_mm"] / MM_PER_CM)
    )
    result["mask_strap_length_strap_match"] = (
        result["mask_strap_length_rank"] * result["strap_ratio"]
    )
    return result


def add_face_style_interactions(frame):
    if frame is None or frame.empty:
        return frame
    if "style" not in frame.columns:
        return frame
    if any(column not in frame.columns for column in FACE_SHAPE_FEATURE_COLUMNS):
        return frame

    result = frame.copy()
    style_series = result["style"].fillna("unknown").astype(str).str.strip()
    style_series = style_series.replace("", "unknown")
    style_dummies = pd.get_dummies(style_series, prefix=STYLE_INTERACTION_PREFIX.rstrip("_"))

    for style_column in style_dummies.columns:
        style_mask = style_dummies[style_column]
        for face_column in FACE_SHAPE_FEATURE_COLUMNS:
            interaction_column = (
                f"{FACE_STYLE_INTERACTION_PREFIX}{face_column}_x_{style_column}"
            )
            result[interaction_column] = result[face_column] * style_mask

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
    inference_rows = add_strap_type_features(inference_rows)
    inference_rows = add_face_shape_features(inference_rows)
    inference_rows = add_mask_size_features(inference_rows)
    inference_rows = add_mask_size_face_interactions(inference_rows)

    if use_diff_perimeter_bins or use_diff_perimeter_mask_bins:
        inference_rows = inference_rows.copy()
        numeric_columns = FACIAL_PERIMETER_COMPONENTS + ["perimeter_mm"]
        inference_rows[numeric_columns] = (
            inference_rows[numeric_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )
        inference_rows["perimeter_diff"] = inference_rows["facial_perimeter_mm"] - inference_rows["perimeter_mm"]
        inference_rows["perimeter_diff_bin_index"] = diff_bin_index(inference_rows["perimeter_diff"])
        inference_rows = scale_perimeter_diff_features(inference_rows)
        inference_rows = add_geometry_penalty_features(inference_rows)
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
        inference_rows = add_face_style_interactions(inference_rows)
        inference_rows = add_strap_style_interactions(inference_rows)
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
        numeric_columns = FACIAL_PERIMETER_COMPONENTS + ["perimeter_mm"]
        inference_rows[numeric_columns] = (
            inference_rows[numeric_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )
        inference_rows["perimeter_diff"] = inference_rows["facial_perimeter_mm"] - inference_rows["perimeter_mm"]
        inference_rows["perimeter_diff_sq"] = inference_rows["perimeter_diff"] ** 2
        inference_rows = scale_perimeter_diff_features(inference_rows)
        inference_rows = add_geometry_penalty_features(inference_rows)
        inference_rows = add_style_perimeter_interactions(inference_rows)
        inference_rows = add_face_style_interactions(inference_rows)
        inference_rows = add_strap_style_interactions(inference_rows)
        inference_rows = inference_rows.drop(columns=FACIAL_FEATURE_COLUMNS, errors="ignore")
        return inference_rows

    inference_rows = inference_rows.copy()
    numeric_columns = FACIAL_PERIMETER_COMPONENTS + ["perimeter_mm"]
    inference_rows[numeric_columns] = (
        inference_rows[numeric_columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
    )
    inference_rows["perimeter_diff"] = inference_rows["facial_perimeter_mm"] - inference_rows["perimeter_mm"]
    inference_rows["perimeter_diff_sq"] = inference_rows["perimeter_diff"] ** 2
    inference_rows = scale_perimeter_diff_features(inference_rows)
    inference_rows = add_geometry_penalty_features(inference_rows)
    inference_rows = add_style_perimeter_interactions(inference_rows)
    inference_rows = add_face_style_interactions(inference_rows)
    inference_rows = add_strap_style_interactions(inference_rows)

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
