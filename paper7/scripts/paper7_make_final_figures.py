from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


CONTRASTS = [
    ("delta_mse_true_vs_no_structure", "No structure"),
    ("delta_mse_true_vs_group_mean", "Group mean"),
    ("delta_mse_true_vs_swap", "Swapped"),
    ("delta_mse_true_vs_rewire", "Rewired"),
    ("delta_mse_true_vs_distance", "Distance"),
]


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    payload = json.loads((RESULTS / "p7_e7_final_structural_hypothesis_test.json").read_text(encoding="utf-8"))
    summary = payload["summary"]
    means = np.asarray([summary[key]["mean"] for key, _ in CONTRASTS], dtype=float)
    ci_low = np.asarray([summary[key]["ci95"][0] for key, _ in CONTRASTS], dtype=float)
    ci_high = np.asarray([summary[key]["ci95"][1] for key, _ in CONTRASTS], dtype=float)
    labels = [label for _, label in CONTRASTS]
    yerr = np.vstack([means - ci_low, ci_high - means])

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x = np.arange(len(labels))
    colors = ["#3b6ea8" if mean > 0 else "#8f3d38" for mean in means]
    ax.bar(x, means, color=colors, edgecolor="#222222", linewidth=0.8)
    ax.errorbar(x, means, yerr=yerr, fmt="none", ecolor="#111111", elinewidth=1.1, capsize=4)
    ax.axhline(0, color="#111111", linewidth=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Delta MSE: comparator - true $G_i$")
    ax.set_title("Paper 7 final structural hypothesis test")
    ax.text(
        0.99,
        0.03,
        "Positive values favor true subject structure; all final gates failed.",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    png = FIGURES / "paper7_final_structural_hypothesis_delta_mse.png"
    svg = FIGURES / "paper7_final_structural_hypothesis_delta_mse.svg"
    fig.savefig(png, dpi=200)
    fig.savefig(svg)
    plt.close(fig)

    result = {
        "paper": "Paper 7",
        "status": "PASS_FINAL_FIGURE_GENERATION",
        "source": str(RESULTS / "p7_e7_final_structural_hypothesis_test.json"),
        "figures": [str(png), str(svg)],
        "claim_boundary": "Figure generated from final result JSON. Positive delta MSE favors true subject structure; the plotted final contrasts do not support subject-specific structural grounding.",
    }
    (RESULTS / "p7_final_figures.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
