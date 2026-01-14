import argparse
import logging
import os
import re
import sys

import matplotlib.pyplot as plt
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
PYTHON_DIR = os.path.join(REPO_ROOT, "python", "mask_recommender")

if PYTHON_DIR not in sys.path:
    sys.path.append(PYTHON_DIR)

from predict_arkit_from_traditional import predict_arkit_from_traditional  # noqa: E402


FACIAL_COMPONENTS = [
    "nose_mm",
    "top_cheek_mm",
    "mid_cheek_mm",
    "chin_mm",
]


def normalize_bool(value):
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    normalized = str(value).strip().lower()
    if normalized in ["true", "1", "pass", "passed", "yes", "y"]:
        return True
    if normalized in ["false", "0", "fail", "failed", "no", "n"]:
        return False
    return None


def slugify(value):
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", value).strip("_")


def build_bins():
    edges = [-float("inf")]
    edges.extend(range(-50, 51, 10))
    edges.append(float("inf"))
    labels = [
        "i < -50",
        "-50 <= i < -40",
        "-40 <= i < -30",
        "-30 <= i < -20",
        "-20 <= i < -10",
        "-10 <= i < 0",
        "0 <= i < 10",
        "10 <= i < 20",
        "20 <= i < 30",
        "30 <= i < 40",
        "40 <= i < 50",
        "i >= 50",
    ]
    return edges, labels


def main():
    parser = argparse.ArgumentParser(description="EDA for qlft pass vs. perimeter difference.")
    parser.add_argument("--output-dir", required=True, help="Directory to save PNG plots.")
    parser.add_argument("--base-url", default="http://localhost:3000", help="Base URL for API.")
    parser.add_argument("--grid-cols", type=int, default=3, help="Number of subplot columns.")
    parser.add_argument("--output-file", default="qlft_pass_by_diff.png", help="Output PNG filename.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    os.makedirs(args.output_dir, exist_ok=True)

    email = os.getenv("BREATHESAFE_SERVICE_EMAIL")
    password = os.getenv("BREATHESAFE_SERVICE_PASSWORD")

    df = predict_arkit_from_traditional(
        base_url=args.base_url,
        email=email,
        password=password,
    )

    df = df[df["perimeter_mm"].notna()]
    if "mask_modded" in df.columns:
        df = df[~df["mask_modded"].apply(lambda v: normalize_bool(v) is True)]
    else:
        logging.warning("mask_modded column missing; skipping modded filtering.")

    df["facial_perimeter_mm"] = df[FACIAL_COMPONENTS].sum(axis=1, min_count=len(FACIAL_COMPONENTS))
    df = df[df["facial_perimeter_mm"].notna()]

    df["qlft_pass_normalized"] = df["qlft_pass"].apply(normalize_bool)
    df = df[df["qlft_pass_normalized"].notna()]

    df["perimeter_diff"] = df["facial_perimeter_mm"] - df["perimeter_mm"]

    edges, labels = build_bins()
    df["diff_bin"] = pd.cut(df["perimeter_diff"], bins=edges, labels=labels, right=False)

    grouped = df.groupby(["style", "strap_type", "diff_bin"]).agg(
        pass_rate=("qlft_pass_normalized", "mean"),
        sample_count=("qlft_pass_normalized", "size"),
    )
    grouped = grouped.reset_index()

    combos = list(grouped.groupby(["style", "strap_type"]))
    if not combos:
        logging.warning("No style/strap combos found after filtering.")
        return

    num_plots = len(combos)
    cols = max(1, args.grid_cols)
    rows = (num_plots + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4), squeeze=False, sharey=True)
    x_min = 0
    x_max = len(labels) - 1
    for index, ((style, strap_type), subset) in enumerate(combos):
        row = index // cols
        col = index % cols
        ax = axes[row][col]
        subset = subset.set_index("diff_bin").reindex(labels).reset_index()
        ax.plot(range(len(labels)), subset["pass_rate"], marker="o")
        ax.set_ylim(0, 1)
        ax.set_xlim(x_min, x_max)
        ax.set_title(f"{style} / {strap_type}")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")

        if row == rows - 1:
            ax.set_xlabel("Facial perimeter - mask perimeter (mm)")
        if col == 0:
            ax.set_ylabel("QLFT pass probability")

    for index in range(num_plots, rows * cols):
        row = index // cols
        col = index % cols
        fig.delaxes(axes[row][col])

    fig.tight_layout()
    output_path = os.path.join(args.output_dir, args.output_file)
    fig.savefig(output_path)
    plt.close(fig)
    logging.info("Saved %s", output_path)


if __name__ == "__main__":
    main()
