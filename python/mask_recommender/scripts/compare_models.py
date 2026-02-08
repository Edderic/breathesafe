import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import auc, f1_score, roc_curve

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from breathesafe_network import build_session, fetch_facial_measurements_fit_tests  # noqa: E402
from predict_arkit_from_traditional import predict_arkit_from_traditional  # noqa: E402
from prob_model import normalize_qlft_pass, predict_prob_model, train_prob_model  # noqa: E402
from feature_builder import build_feature_frame  # noqa: E402
from qa import build_recommendation_preview  # noqa: E402
from train import (build_feature_matrix, build_mask_candidates, get_masks,  # noqa: E402
                   prepare_training_data, train_predictor_with_split,
                   _set_num_masks_times_num_bins_plus_other_features)


def parse_args():
    parser = argparse.ArgumentParser(description="Compare NN vs probabilistic model.")
    parser.add_argument('--epochs', type=int, default=200, help='Number of training epochs.')
    parser.add_argument('--learning-rate', type=float, default=0.0001, help='Learning rate.')
    parser.add_argument('--val-split', type=float, default=0.2, help='Validation split fraction.')
    parser.add_argument(
        '--preview-user-ids',
        type=int,
        nargs='+',
        default=[99, 101, 105],
        help='User IDs to include in recommendation preview.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    matplotlib.use("Agg")

    base_url = os.environ.get('BREATHESAFE_BASE_URL', 'http://localhost:3000')
    session = build_session(None)
    fit_tests_payload = fetch_facial_measurements_fit_tests(
        base_url=base_url,
        session=session,
    )
    fit_tests_df = pd.DataFrame(fit_tests_payload)

    masks_url = f"{base_url}/masks.json?per_page=1000"
    masks_df = get_masks(session, masks_url)
    mask_candidates = build_mask_candidates(masks_df)
    outer_dim = _set_num_masks_times_num_bins_plus_other_features(mask_candidates)

    email = os.getenv('BREATHESAFE_SERVICE_EMAIL')
    password = os.getenv('BREATHESAFE_SERVICE_PASSWORD')
    fit_tests_with_imputed = predict_arkit_from_traditional(
        base_url=base_url,
        email=email,
        password=password
    )

    filtered_fit_tests = fit_tests_with_imputed.copy()
    filtered_fit_tests = filtered_fit_tests[filtered_fit_tests['perimeter_mm'].notna()]
    filtered_fit_tests = filtered_fit_tests.dropna(subset=['nose_mm', 'chin_mm', 'mid_cheek_mm', 'top_cheek_mm'])
    filtered_fit_tests = filtered_fit_tests[filtered_fit_tests['qlft_pass'].notna()]
    filtered_fit_tests = filtered_fit_tests[filtered_fit_tests['style'].notna()]
    filtered_fit_tests = filtered_fit_tests[filtered_fit_tests['strap_type'].notna()]
    cleaned_fit_tests = prepare_training_data(filtered_fit_tests)
    if cleaned_fit_tests.empty:
        raise SystemExit("No fit tests available after filtering.")

    features, target = build_feature_matrix(
        cleaned_fit_tests,
        ['strap_type', 'style', 'brand_model', 'unique_internal_model_code']
    )

    num_rows = features.shape[0]
    permutation = torch.randperm(num_rows)
    split_index = int(num_rows * (1 - args.val_split))
    train_idx = permutation[:split_index]
    val_idx = permutation[split_index:]

    nn_model, _, _, x_train, y_train, x_val, y_val, _, _ = train_predictor_with_split(
        features,
        target,
        train_idx,
        val_idx,
        outer_dim=outer_dim,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )

    nn_model.eval()
    with torch.no_grad():
        nn_val_probs = nn_model(x_val).squeeze().cpu().numpy()
    nn_val_labels = y_val.squeeze().cpu().numpy()
    nn_val_preds = (nn_val_probs >= 0.5).astype(float)

    mask_id_index = sorted(filtered_fit_tests['mask_id'].dropna().unique())
    style_categories = sorted(filtered_fit_tests['style'].dropna().unique())
    prob_train_df = filtered_fit_tests.iloc[train_idx]
    prob_val_df = filtered_fit_tests.iloc[val_idx]
    prob_params, _ = train_prob_model(
        prob_train_df,
        mask_id_index,
        style_categories,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )

    prob_val_probs = predict_prob_model(prob_params, prob_val_df, mask_id_index, style_categories)
    prob_val_labels = normalize_qlft_pass(prob_val_df["qlft_pass"]).to_numpy()
    prob_val_preds = (prob_val_probs >= 0.5).astype(float)

    nn_f1 = f1_score(nn_val_labels, nn_val_preds, zero_division=0)
    prob_f1 = f1_score(prob_val_labels, prob_val_preds, zero_division=0)

    nn_fpr, nn_tpr, _ = roc_curve(nn_val_labels, nn_val_probs)
    prob_fpr, prob_tpr, _ = roc_curve(prob_val_labels, prob_val_probs)
    nn_auc = auc(nn_fpr, nn_tpr)
    prob_auc = auc(prob_fpr, prob_tpr)

    logging.info("NN: AUC=%.3f F1=%.3f", nn_auc, nn_f1)
    logging.info("Prob: AUC=%.3f F1=%.3f", prob_auc, prob_f1)

    images_dir = "python/mask_recommender/images"
    os.makedirs(images_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    roc_plot_path = os.path.join(images_dir, f"{timestamp}_compare_roc_auc.png")

    plt.figure(figsize=(8, 4))
    plt.plot(nn_fpr, nn_tpr, label=f'NN (AUC={nn_auc:.3f})', linewidth=2)
    plt.plot(prob_fpr, prob_tpr, label=f'Prob (AUC={prob_auc:.3f})', linewidth=2)
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC-AUC Comparison')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(roc_plot_path)
    plt.close()

    logging.info("Saved ROC-AUC comparison plot to %s", roc_plot_path)

    feature_columns = list(features.columns)
    categorical_columns = ['strap_type', 'style', 'brand_model', 'unique_internal_model_code']

    def predict_nn(inference_rows):
        encoded = build_feature_frame(
            inference_rows,
            feature_columns=feature_columns,
            categorical_columns=categorical_columns,
        )
        x_infer = torch.tensor(encoded.to_numpy(), dtype=torch.float32)
        nn_model.eval()
        with torch.no_grad():
            return nn_model(x_infer).squeeze().cpu().numpy()

    def predict_prob(inference_rows):
        prob_rows = inference_rows.copy()
        prob_rows['mask_id'] = mask_candidates.reset_index(drop=True)['id'].to_numpy()
        return predict_prob_model(prob_params, prob_rows, mask_id_index, style_categories)

    nn_preview_path = os.path.join(images_dir, f"{timestamp}_compare_nn_recommendations.json")
    prob_preview_path = os.path.join(images_dir, f"{timestamp}_compare_prob_recommendations.json")

    build_recommendation_preview(
        user_ids=args.preview_user_ids,
        fit_tests_df=fit_tests_with_imputed,
        mask_candidates=mask_candidates,
        predict_fn=predict_nn,
        output_path=nn_preview_path,
        threshold=0.5,
    )
    build_recommendation_preview(
        user_ids=args.preview_user_ids,
        fit_tests_df=fit_tests_with_imputed,
        mask_candidates=mask_candidates,
        predict_fn=predict_prob,
        output_path=prob_preview_path,
        threshold=0.5,
    )
    logging.info("Saved NN preview to %s", nn_preview_path)
    logging.info("Saved probabilistic preview to %s", prob_preview_path)


if __name__ == "__main__":
    main()
