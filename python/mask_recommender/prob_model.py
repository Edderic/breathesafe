import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from feature_builder import FACIAL_PERIMETER_COMPONENTS

STRAP_TYPES = [
    "Earloop",
    "Adjustable Earloop",
    "Headstrap",
    "Adjustable Headstrap",
    "Strapless",
]

logger = logging.getLogger(__name__)


def normalize_qlft_pass(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.map(
        {
            "pass": 1.0,
            "passed": 1.0,
            "true": 1.0,
            "1": 1.0,
            "yes": 1.0,
            "fail": 0.0,
            "failed": 0.0,
            "false": 0.0,
            "0": 0.0,
            "no": 0.0,
        }
    ).fillna(0.0)


def build_prob_data(
    fit_tests: pd.DataFrame,
    mask_id_index: List[int],
    style_categories: List[str],
) -> Dict[str, torch.Tensor]:
    face_nose_mm = torch.from_numpy(fit_tests["nose_mm"].to_numpy()).unsqueeze(-1).float()
    face_chin_mm = torch.from_numpy(fit_tests["chin_mm"].to_numpy()).unsqueeze(-1).float()
    face_top_cheek_mm = torch.from_numpy(fit_tests["top_cheek_mm"].to_numpy()).unsqueeze(-1).float()
    face_mid_cheek_mm = torch.from_numpy(fit_tests["mid_cheek_mm"].to_numpy()).unsqueeze(-1).float()
    perimeter_mm = torch.from_numpy(fit_tests["perimeter_mm"].to_numpy()).unsqueeze(-1).float()
    face_perimeter_mm = face_nose_mm + face_chin_mm + face_top_cheek_mm + face_mid_cheek_mm

    is_headstraps = torch.from_numpy(
        fit_tests["strap_type"].astype(str).str.contains("eadstrap").to_numpy()
    ).unsqueeze(-1).float()
    is_adjustable = torch.from_numpy(
        fit_tests["strap_type"].astype(str).str.contains("djustable").to_numpy()
    ).unsqueeze(-1).float()

    facial_hair_beard_length_mm = torch.from_numpy(
        fit_tests["facial_hair_beard_length_mm"].to_numpy()
    ).unsqueeze(-1).float()

    mask_id_cat = pd.Categorical(fit_tests["mask_id"], categories=mask_id_index, ordered=False)
    mask_dummies = pd.get_dummies(mask_id_cat)
    mask_dummies = mask_dummies.reindex(columns=mask_id_index, fill_value=0)
    mask_dummies_over_fit_tests = torch.from_numpy(mask_dummies.to_numpy()).float()

    style_cat = pd.Categorical(fit_tests["style"], categories=style_categories, ordered=False)
    style_dummies = pd.get_dummies(style_cat)
    style_dummies = style_dummies.reindex(columns=style_categories, fill_value=0)
    style_dummies_over_fit_tests = torch.from_numpy(style_dummies.to_numpy()).float()

    return {
        "face_perimeter_mm": face_perimeter_mm,
        "style_len": style_dummies.shape[1],
        "style_dummies_over_fit_tests": style_dummies_over_fit_tests,
        "face_nose_mm": face_nose_mm,
        "face_top_cheek_mm": face_top_cheek_mm,
        "face_mid_cheek_mm": face_mid_cheek_mm,
        "face_chin_mm": face_chin_mm,
        "is_headstraps": is_headstraps,
        "is_adjustable": is_adjustable,
        "facial_hair_beard_length_mm": facial_hair_beard_length_mm,
        "mask_dummies_over_fit_tests": mask_dummies_over_fit_tests,
        "perimeter_mm": perimeter_mm,
    }


def init_params(mask_ids: List[int], data: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
    beta_mask_for_distance_a = torch.nn.Parameter(torch.zeros((len(mask_ids), 1)))
    beta_mask_for_distance_b = torch.nn.Parameter(torch.zeros((len(mask_ids), 1)))
    beta_mask_for_distance_c = torch.nn.Parameter(torch.zeros((len(mask_ids), 1)))

    beta_style_for_distance_a = torch.nn.Parameter(
        torch.rand((data['style_len'], 1)) - 0.5
    )
    beta_style_for_distance_b = torch.nn.Parameter(torch.rand((data['style_len'], 1)))
    beta_style_for_distance_c = torch.nn.Parameter(torch.rand((data['style_len'], 1)))

    alpha_misc_fit = torch.nn.Parameter(torch.rand(1))
    beta_is_headstraps = torch.nn.Parameter(torch.rand(1))
    beta_is_adjustable = torch.nn.Parameter(torch.rand(1))
    beta_beard_length = torch.nn.Parameter(torch.rand(1))

    return {
        "alpha_misc_fit": alpha_misc_fit,
        "beta_mask_for_distance_a": beta_mask_for_distance_a,
        "beta_mask_for_distance_b": beta_mask_for_distance_b,
        "beta_mask_for_distance_c": beta_mask_for_distance_c,
        "beta_style_for_distance_a": beta_style_for_distance_a,
        "beta_style_for_distance_b": beta_style_for_distance_b,
        "beta_style_for_distance_c": beta_style_for_distance_c,
        "beta_is_headstraps": beta_is_headstraps,
        "beta_is_adjustable": beta_is_adjustable,
        "beta_beard_length": beta_beard_length,
    }


def predict_proba(params: Dict[str, torch.Tensor], data: Dict[str, torch.Tensor]) -> torch.Tensor:
    face_vs_mask_perimeter_distance = torch.abs(
        data["face_perimeter_mm"] - data["perimeter_mm"]
    )

    beta_mask_for_dist_a = (
        data["mask_dummies_over_fit_tests"]
        @ params["beta_mask_for_distance_a"]
    )

    beta_style_for_dist_a = (
        data["style_dummies_over_fit_tests"]
        @ params["beta_style_for_distance_a"]
    )

    beta_mask_for_dist_b = (
        data["mask_dummies_over_fit_tests"]
        @ params["beta_mask_for_distance_b"]
    )

    beta_style_for_dist_b = (
        data["style_dummies_over_fit_tests"]
        @ params["beta_style_for_distance_b"]
    )

    beta_mask_for_dist_c = (
        data["mask_dummies_over_fit_tests"]
        @ params["beta_mask_for_distance_c"]
    )

    beta_style_for_dist_c = (
        data["style_dummies_over_fit_tests"]
        @ params["beta_style_for_distance_c"]
    )

    results = torch.sigmoid(
        (beta_style_for_dist_a + beta_mask_for_dist_a)
        * (
            face_vs_mask_perimeter_distance
            + beta_style_for_dist_b
            + beta_mask_for_dist_b
        )**2
        + params["beta_is_headstraps"] * data["is_headstraps"]
        + params["beta_is_adjustable"] * data["is_adjustable"]
        + params["beta_beard_length"] * data["facial_hair_beard_length_mm"]
        + params["alpha_misc_fit"]
        + beta_mask_for_dist_c
        + beta_style_for_dist_c
    )

    return results


def train_prob_model(
    train_df: pd.DataFrame,
    mask_id_index: List[int],
    style_categories: List[str],
    epochs: int,
    learning_rate: float,
) -> Tuple[Dict[str, torch.Tensor], List[float]]:
    data = build_prob_data(train_df, mask_id_index, style_categories)
    params = init_params(mask_id_index, data)
    trainable_params = [value for value in params.values() if value.requires_grad]
    optimizer = torch.optim.Adam(trainable_params, lr=learning_rate)
    loss_fn = torch.nn.BCELoss()

    labels = torch.from_numpy(normalize_qlft_pass(train_df["qlft_pass"]).to_numpy()).float().unsqueeze(-1)

    losses = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        probs = predict_proba(params, data)
        loss = loss_fn(probs, labels)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))
        if (epoch + 1) % 10 == 0 or epoch == 0:
            logger.info("prob-model epoch=%s loss=%.4f", epoch + 1, loss.item())

    return params, losses


def predict_prob_model(
    params: Dict[str, torch.Tensor],
    inference_df: pd.DataFrame,
    mask_id_index: List[int],
    style_categories: List[str],
) -> np.ndarray:
    data = build_prob_data(inference_df, mask_id_index, style_categories)
    with torch.no_grad():
        probs = predict_proba(params, data).squeeze().cpu().numpy()
    return probs
