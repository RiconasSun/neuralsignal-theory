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
    data = json.loads((RESULTS / "p8_final_extension_ds005795_streaming_nuisance_ladder.json").read_text(encoding="utf-8"))
    aggregate = data["aggregate_results"]
    order = [
        "N0_state_only",
        "N1_state_plus_cardiac_resp",
        "N2_state_plus_metadata",
        "N3_state_plus_physio_metadata",
    ]
    labels = [
        "State\nonly",
        "State +\nphysio",
        "State +\nmetadata",
        "State +\nphysio +\nmetadata",
    ]
    mses = [aggregate[key]["mean_mse"] for key in order]
    r2s = [aggregate[key]["mean_r2"] for key in order]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    colors = ["#5f6973", "#31706f", "#8d6a2f", "#2f5e9f"]

    axes[0].bar(range(len(order)), mses, color=colors)
    axes[0].set_xticks(range(len(order)), labels)
    axes[0].set_ylabel("Mean MSE")
    axes[0].set_title("Prediction error")

    axes[1].bar(range(len(order)), r2s, color=colors)
    axes[1].set_xticks(range(len(order)), labels)
    axes[1].set_ylabel("Mean R2")
    axes[1].set_title("Held-out fit")
    axes[1].set_ylim(0, max(r2s) * 1.2)

    fig.suptitle("P8 ds005795 convergent measured-physiology extension")
    fig.text(
        0.5,
        0.01,
        "Global BOLD endpoint; all complete task-learning subjects in audited manifest (n=5). Not direct HCP WM transition replication.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    png = FIGURES / "figure5_p8_ds005795_streaming_nuisance_ladder.png"
    svg = FIGURES / "figure5_p8_ds005795_streaming_nuisance_ladder.svg"
    fig.savefig(png, dpi=180)
    fig.savefig(svg)
    plt.close(fig)

    payload = {
        "status": "PASS_P8_DS005795_STREAMING_FIGURE",
        "figure_png": str(png),
        "figure_svg": str(svg),
        "source": str(RESULTS / "p8_final_extension_ds005795_streaming_nuisance_ladder.json"),
    }
    (RESULTS / "p8_ds005795_streaming_figure.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
