from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    data = json.loads((RESULTS / "p8_v2_signal_separation_audit.json").read_text(encoding="utf-8"))
    rows = list(data["results"].values())
    labels = [r["rung"].replace("_", "\n") for r in rows]

    plt.figure(figsize=(8, 4.5))
    x = range(len(rows))
    plt.bar(x, [r["true_same_minus_different_contrast"] for r in rows], color="#8f3f71", label="True")
    plt.errorbar(
        x,
        [r["label_shuffle_contrast_mean"] for r in rows],
        yerr=[
            [r["label_shuffle_contrast_mean"] - r["label_shuffle_contrast_ci95"][0] for r in rows],
            [r["label_shuffle_contrast_ci95"][1] - r["label_shuffle_contrast_mean"] for r in rows],
        ],
        fmt="o",
        color="#222222",
        capsize=4,
        label="Label-shuffle null 95% CI",
    )
    plt.axhline(0, color="#333333", linewidth=1)
    plt.xticks(list(x), labels)
    plt.ylabel("Same - different transition similarity")
    plt.title("P8-v2 primary endpoint remains unsupported")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "figure3_p8_v2_transition_nulls.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.bar(x, [r["true_logo_classification_accuracy"] for r in rows], color="#2f6f9f", label="ROI transition features")
    plt.scatter(x, [r["metadata_only_logo_accuracy"] for r in rows], color="#d08c2f", label="metadata-only")
    plt.errorbar(
        x,
        [r["classification_label_shuffle_mean"] for r in rows],
        yerr=[
            [r["classification_label_shuffle_mean"] - r["classification_label_shuffle_ci95"][0] for r in rows],
            [r["classification_label_shuffle_ci95"][1] - r["classification_label_shuffle_mean"] for r in rows],
        ],
        fmt="o",
        color="#222222",
        capsize=4,
        label="Label-shuffle null 95% CI",
    )
    plt.axhline(0.5, color="#333333", linewidth=1, linestyle="--")
    plt.xticks(list(x), labels)
    plt.ylabel("Leave-one-run-out accuracy")
    plt.title("P8-v2 secondary condition-classification signal")
    plt.ylim(0, 1)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "figure4_p8_v2_classification_nulls.png", dpi=180)
    plt.close()

    print(f"Wrote P8-v2 figures to {FIGURES}")


if __name__ == "__main__":
    main()
