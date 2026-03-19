#!/usr/bin/env python3
import argparse
import json
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Optional libraries for other analyses
try:
    from sklearn.inspection import permutation_importance
except Exception:  # pragma: no cover
    permutation_importance = None

try:
    from sklearn.feature_selection import mutual_info_classif
except Exception:  # pragma: no cover
    mutual_info_classif = None

USC_SIZING_QUESTION = "What do you think about the sizing of this mask relative to your face?"
USC_NEGATIVE_Q = "...how much air passed between your face and the mask?"
USC_POSITIVE_GLASSES_Q = "...how much did your glasses fog up?"
USC_POSITIVE_BUILDUP_Q = "...how much pressure build up was there?"
USC_POSITIVE_AIR_MOVEMENT_Q = "...how much air movement on your face along the seal of the mask did you feel?"

USC_KEYS = [
    ("user_seal_check.sizing", USC_SIZING_QUESTION),
    ("user_seal_check.negative", USC_NEGATIVE_Q),
    ("user_seal_check.positive", USC_POSITIVE_GLASSES_Q),
    ("user_seal_check.positive", USC_POSITIVE_BUILDUP_Q),
    ("user_seal_check.positive", USC_POSITIVE_AIR_MOVEMENT_Q),
]


@dataclass
class Config:
    endpoint: str = "http://localhost:3000/facial_measurements_fit_tests.json"
    seed: int = 13
    # analysis mode: all data, or restrict to "sizing in-between" rows
    restrict_to_in_between: bool = False


IN_BETWEEN_SIZING_VALUES = {
    "Just right",
    "Somewhat small",
    "Somewhat big",
}


def load_data(cfg: Config) -> pd.DataFrame:
    r = requests.get(cfg.endpoint, timeout=60)
    r.raise_for_status()
    payload = r.json()
    rows = payload.get("fit_tests_with_facial_measurements", [])

    df = pd.DataFrame(rows)
    return df


def flatten_usc_answers(df: pd.DataFrame) -> pd.DataFrame:
    # Extract USC answers into top-level string columns; missing => 'MISSING'
    def extract_answer(row: dict, section: str, question: str) -> str:
        try:
            section_obj = row.get(section, {}) or {}
            ans = section_obj.get(question)
            if ans is None or ans == "":
                return "MISSING"
            return str(ans)
        except Exception:
            return "MISSING"

    df = df.copy()
    # Ensure nested object exists
    if "user_seal_check" not in df.columns:
        # The service returns user_seal_check as a JSON column; ensure present
        df["user_seal_check"] = None

    for section, question in USC_KEYS:
        top_key = f"usc::{question}"
        sec = section.split(".")[-1]
        df[top_key] = df["user_seal_check"].apply(lambda x: extract_answer(x or {}, sec, question))

    # Label
    if "qlft_pass" in df.columns:
        # Keep boolean; drop NULLs
        df = df[~df["qlft_pass"].isna()].copy()
        df["fit_label"] = df["qlft_pass"].astype(bool)
    else:
        raise ValueError("qlft_pass not found in returned data")

    # Build unique key for user-mask for deduplication
    # Expect user_id and mask_id present; if not, try id or unique_internal_model_code
    if "user_id" not in df.columns:
        raise ValueError("user_id missing from dataset; cannot deduplicate by user")
    mask_key = "mask_id" if "mask_id" in df.columns else "unique_internal_model_code"
    if mask_key not in df.columns:
        raise ValueError("mask identifier missing (mask_id or unique_internal_model_code)")

    df["user_mask_key"] = df["user_id"].astype(str) + "::" + df[mask_key].astype(str)

    return df


def deduplicate_by_user_mask(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    # Deterministically shuffle, then keep first per user_mask_key
    return (
        df.sample(frac=1, random_state=seed)
          .drop_duplicates("user_mask_key", keep="first")
          .reset_index(drop=True)
    )


def filter_in_between(df: pd.DataFrame) -> pd.DataFrame:
    sizing_col = f"usc::{USC_SIZING_QUESTION}"
    return df[df[sizing_col].isin(IN_BETWEEN_SIZING_VALUES)].copy()


def build_feature_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    # One-hot encode USC answers; include MISSING as a valid category
    y = df["fit_label"].astype(int).values
    usc_cols = [f"usc::{q}" for _, q in USC_KEYS]
    X_df = df[usc_cols].astype(str)

    # Handle scikit-learn >=1.4 where 'sparse' was removed in favor of 'sparse_output'
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        # Fallback for older versions
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
    X = ohe.fit_transform(X_df)
    feature_names = ohe.get_feature_names_out(usc_cols).tolist()
    return X, y, feature_names


def l1_logistic_cv(X: np.ndarray, y: np.ndarray, feature_names: List[str], seed: int) -> pd.DataFrame:
    # Strong L1 to induce sparsity
    # We will cross-validate C over a grid
    Cs = np.logspace(-3, 1, 9)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

    best_auc = -np.inf
    best = None
    for C in Cs:
        aucs = []
        coefs = []
        for tr, te in cv.split(X, y):
            clf = LogisticRegression(
                penalty="l1",
                solver="saga",
                C=C,
                max_iter=2000,
                random_state=seed,
            )
            clf.fit(X[tr], y[tr])
            proba = clf.predict_proba(X[te])[:, 1]
            aucs.append(roc_auc_score(y[te], proba))
            coefs.append(clf.coef_[0])
        mean_auc = float(np.mean(aucs))
        if mean_auc > best_auc:
            best_auc = mean_auc
            best = (C, np.mean(np.stack(coefs), axis=0))

    C_best, coef_mean = best
    coef_df = pd.DataFrame({
        "feature": feature_names,
        "coef": coef_mean,
        "abs_coef": np.abs(coef_mean),
    }).sort_values("abs_coef", ascending=False)
    coef_df["cv_auc"] = best_auc
    coef_df["C_best"] = C_best
    return coef_df


def permutation_importance_cv(X: np.ndarray, y: np.ndarray, feature_names: List[str], seed: int) -> Optional[pd.DataFrame]:
    if permutation_importance is None:
        return None
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    importances = []
    for tr, te in cv.split(X, y):
        clf = LogisticRegression(
            penalty="l2",
            solver="lbfgs",
            C=1.0,
            max_iter=2000,
            random_state=seed,
        )
        clf.fit(X[tr], y[tr])
        r = permutation_importance(clf, X[te], y[te], n_repeats=20, random_state=seed, scoring="roc_auc")
        importances.append(r.importances_mean)
    mean_imp = np.mean(np.stack(importances), axis=0)
    imp_df = pd.DataFrame({
        "feature": feature_names,
        "perm_importance": mean_imp,
        "abs_perm_importance": np.abs(mean_imp),
    }).sort_values("abs_perm_importance", ascending=False)
    return imp_df


def mutual_info_scores(X: np.ndarray, y: np.ndarray, feature_names: List[str], seed: int) -> Optional[pd.DataFrame]:
    if mutual_info_classif is None:
        return None
    mi = mutual_info_classif(X, y, random_state=seed, discrete_features=True)
    mi_df = pd.DataFrame({
        "feature": feature_names,
        "mutual_info": mi,
    }).sort_values("mutual_info", ascending=False)
    return mi_df


def print_group_summaries(coef_df: pd.DataFrame) -> pd.DataFrame:
    # Summarize by original question groups (not specific categories)
    def group_of(feature: str) -> str:
        # feature like 'usc::question=Answer'
        return feature.split("=")[0]

    grp = coef_df.groupby(coef_df["feature"].apply(group_of))["abs_coef"].sum().sort_values(ascending=False)
    print("\n[Group importance by L1 abs coef sum]\n", grp.to_string())
    return grp.reset_index().rename(columns={"feature": "group", "abs_coef": "l1_abs_coef_sum"})


def main():
    parser = argparse.ArgumentParser(description="Analyze conditional redundancy among user_seal_check questions.")
    parser.add_argument("--endpoint", default=os.getenv("FMWFT_ENDPOINT", "http://localhost:3000/facial_measurements_fit_tests.json"))
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--restrict-in-between", action="store_true", help="Restrict to rows where sizing is in-between (not too small/big)")
    parser.add_argument("--outdir", default="./python/mask_recommender/data/usc_analysis")
    args = parser.parse_args()

    cfg = Config(endpoint=args.endpoint, seed=args.seed, restrict_to_in_between=args.restrict_in_between)

    os.makedirs(args.outdir, exist_ok=True)

    # Load and prep
    df_raw = load_data(cfg)
    import pdb; pdb.set_trace()

    df = flatten_usc_answers(df_raw)

    # Deduplicate user-mask
    df = deduplicate_by_user_mask(df, seed=cfg.seed)

    # Restrict to in-between if requested
    if cfg.restrict_to_in_between:
        df = filter_in_between(df)

    # Build X, y
    X, y, feature_names = build_feature_matrix(df)

    # L1 logistic selection
    coef_df = l1_logistic_cv(X, y, feature_names, seed=cfg.seed)
    grp_df = print_group_summaries(coef_df)

    # Permutation importance (L2 baseline)
    perm_df = permutation_importance_cv(X, y, feature_names, seed=cfg.seed)

    # Mutual information
    mi_df = mutual_info_scores(X, y, feature_names, seed=cfg.seed)

    # Save outputs
    coef_path = os.path.join(args.outdir, "l1_logit_features.csv")
    grp_path = os.path.join(args.outdir, "l1_logit_groups.csv")
    pd.DataFrame(coef_df).to_csv(coef_path, index=False)
    pd.DataFrame(grp_df).to_csv(grp_path, index=False)

    if perm_df is not None:
        perm_path = os.path.join(args.outdir, "permutation_importance.csv")
        perm_df.to_csv(perm_path, index=False)

    if mi_df is not None:
        mi_path = os.path.join(args.outdir, "mutual_info.csv")
        mi_df.to_csv(mi_path, index=False)

    # Console summary
    print("\nSaved:")
    print("-", coef_path)
    print("-", grp_path)
    if perm_df is not None:
        print("-", perm_path)
    if mi_df is not None:
        print("-", mi_path)

    # Scenario of interest: sizing in-between only
    sizing_col = f"usc::{USC_SIZING_QUESTION}"
    in_between_mask = df[sizing_col].isin(IN_BETWEEN_SIZING_VALUES)
    if in_between_mask.any():
        X_inb = X[in_between_mask.values]
        y_inb = y[in_between_mask.values]
        feat_inb = feature_names
        print("\n[In-between sizing subset] n=", X_inb.shape[0])
        coef_inb = l1_logistic_cv(X_inb, y_inb, feat_inb, seed=cfg.seed)
        print_group_summaries(coef_inb)
        coef_inb.to_csv(os.path.join(args.outdir, "l1_logit_features_in_between.csv"), index=False)


if __name__ == "__main__":
    main()
