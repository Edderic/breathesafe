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


def wilson_interval(successes, total, z):
    if total == 0:
        return None, None
    p_hat = successes / total
    z2 = z ** 2
    denom = 1 + z2 / total
    center = (p_hat + z2 / (2 * total)) / denom
    margin = (z / denom) * ((p_hat * (1 - p_hat) / total) + (z2 / (4 * total ** 2))) ** 0.5
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return lower, upper


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
    grouped["pass_count"] = (
        (grouped["pass_rate"] * grouped["sample_count"])
        .fillna(0)
        .round()
        .astype(int)
    )
    grouped[["ci99_lower", "ci99_upper"]] = grouped.apply(
        lambda row: pd.Series(
            wilson_interval(row["pass_count"], row["sample_count"], z=2.576)
        ),
        axis=1,
    )
    grouped[["ci50_lower", "ci50_upper"]] = grouped.apply(
        lambda row: pd.Series(
            wilson_interval(row["pass_count"], row["sample_count"], z=0.674)
        ),
        axis=1,
    )

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
        x_positions = range(len(labels))
        ax.plot(x_positions, subset["pass_rate"], marker="o")
        ax.fill_between(
            x_positions,
            subset["ci99_lower"],
            subset["ci99_upper"],
            alpha=0.15,
            label="99% CI"
        )
        ax.fill_between(
            x_positions,
            subset["ci50_lower"],
            subset["ci50_upper"],
            alpha=0.3,
            label="50% CI"
        )
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
        if row == 0 and col == 0:
            ax.legend(loc="upper right", fontsize="small")

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
