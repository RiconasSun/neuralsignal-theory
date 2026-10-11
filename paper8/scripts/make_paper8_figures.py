from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    ladder = read_json(RESULTS / "p8_e1_e6_hcp_physio_ladder_smoke.json")
    rungs = ladder.get("rung_results", {})
    labels = list(rungs.keys())
    contrasts = [rungs[k]["same_vs_different_transition"]["contrast"] for k in labels]
    accs = [rungs[k]["leave_one_run_out_classification"]["accuracy"] for k in labels]

    clean_labels = [k.replace("_", "\n") for k in labels]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axhline(0, color="#222222", linewidth=1)
    ax.plot(clean_labels, contrasts, marker="o", color="#2f6f8f")
    ax.set_title("P8 transition contrast across measured nuisance ladder")
    ax.set_ylabel("Same - different transition centroid similarity")
    ax.set_xlabel("Nuisance rung")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure1_p8_nuisance_ladder_transition_contrast.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axhline(0.5, color="#222222", linewidth=1, linestyle="--", label="chance")
    ax.bar(clean_labels, accs, color="#7c4d79")
    ax.set_title("P8 transition-label classification across nuisance ladder")
    ax.set_ylabel("Leave-one-run-out accuracy")
    ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure2_p8_nuisance_ladder_classification.png", dpi=180)
    plt.close(fig)

    print(f"Wrote figures to {FIGURES}")


if __name__ == "__main__":
    main()
