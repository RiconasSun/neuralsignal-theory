from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "e3_e6_ds004117_full_cohort_batched_results.json"
E7_RESULTS = ROOT / "results" / "e7_ds004752_external_convergent_results.json"
FIGURES = ROOT / "figures"


def load_results() -> dict:
    with RESULTS.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_current(fig: plt.Figure, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=200)
    plt.close(fig)


def style_axes(ax: plt.Axes, title: str, ylabel: str | None = None) -> None:
    ax.set_title(title, fontsize=11, pad=10)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def figure1_pipeline(result: dict) -> None:
    steps = [
        "Events",
        "Windows",
        "EEG",
        "Bandpower",
        "E4",
        "E5",
        "E6",
        "Claim audit",
    ]
    fig, ax = plt.subplots(figsize=(10, 2.6))
    ax.set_xlim(0, len(steps) - 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for idx, step in enumerate(steps):
        ax.scatter(idx, 0.5, s=900, color="#2f6f73", zorder=3)
        ax.text(idx, 0.5, step, ha="center", va="center", color="white", fontsize=8)
        if idx < len(steps) - 1:
            ax.annotate(
                "",
                xy=(idx + 0.68, 0.5),
                xytext=(idx + 0.32, 0.5),
                arrowprops={"arrowstyle": "->", "color": "#444", "lw": 1.2},
            )
    ax.text(
        0,
        0.15,
        f"ds004117: {result['n_subjects']} subjects, {result['n_event_files']} runs/event files, "
        f"{result['n_windows']} transition windows",
        fontsize=9,
    )
    save_current(fig, "figure1_pipeline.png")


def figure2_window_inventory(result: dict) -> None:
    labels = ["Transition", "Random", "Time-shift", "Phase-rand"]
    values = [
        result["n_windows"],
        result["n_random_windows"],
        result["n_time_shift_windows"],
        result["n_phase_randomized_windows"],
    ]
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.bar(labels, values, color=["#2f6f73", "#9aa0a6", "#8f6a36", "#7b6aa8"])
    style_axes(ax, "Window inventory", "Windows")
    for idx, value in enumerate(values):
        ax.text(idx, value, str(value), ha="center", va="bottom", fontsize=9)
    save_current(fig, "figure2_window_inventory.png")


def figure3_reproducibility(result: dict) -> None:
    e4 = result["e4_existence"]
    labels = ["Same transition", "Random window"]
    values = [
        e4["same_transition_odd_even_centroid_similarity"],
        e4["random_window_odd_even_centroid_similarity"],
    ]
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.bar(labels, values, color=["#2f6f73", "#9aa0a6"])
    ax.axhline(0, color="#333", linewidth=1)
    style_axes(ax, "E4 same-transition reproducibility", "Odd/even centroid similarity")
    for idx, value in enumerate(values):
        y = value + 0.03 if value >= 0 else value - 0.08
        ax.text(idx, y, f"{value:.3f}", ha="center", va="bottom" if value >= 0 else "top", fontsize=9)
    save_current(fig, "figure3_e4_reproducibility.png")


def figure4_specificity_and_nulls(result: dict) -> None:
    e5 = result["e5_specificity"]
    e6 = result["e6_nulls"]
    null = e6["label_shuffle_accuracy_null"]
    labels = ["Real", "Label shuffle", "Random window", "Time-shift"]
    values = [
        e5["accuracy"],
        null["null_mean_accuracy"],
        e6["random_window_specificity_accuracy"]["accuracy"],
        e6["time_shift_specificity_accuracy"]["accuracy"],
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4))
    ax.bar(labels, values, color=["#2f6f73", "#9aa0a6", "#9aa0a6", "#8f6a36"])
    ax.axhline(0.5, color="#333", linewidth=1, linestyle="--")
    style_axes(ax, "E5/E6 transition specificity", "Accuracy")
    ax.set_ylim(0.35, 0.75)
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.01, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    save_current(fig, "figure4_e5_e6_specificity_nulls.png")


def figure5_subject_accuracy(result: dict) -> None:
    subjects = result["e5_subject_level"]["subjects"]
    labels = [entry["subject"].replace("sub-", "") for entry in subjects]
    values = [entry["accuracy"] for entry in subjects]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(labels, values, color="#2f6f73")
    ax.axhline(0.5, color="#333", linewidth=1, linestyle="--")
    style_axes(ax, "Subject-level transition specificity", "Accuracy")
    ax.set_xlabel("Subject")
    ax.set_ylim(0.35, 0.92)
    save_current(fig, "figure5_subject_accuracy.png")


def figure6_claim_boundary(result: dict) -> None:
    claims = result["claim_audit"]
    labels = [
        "Fast dynamics\nexistence",
        "Transition\nspecificity",
        "Cross-dataset\nreplication",
        "NAP\nexists",
    ]
    values = [
        int(claims["can_claim_fast_dynamics_existence"]),
        int(claims["can_claim_transition_specificity"]),
        int(claims["can_claim_cross_dataset_replication"]),
        int(claims["can_claim_nap_exists"]),
    ]
    colors = ["#2f6f73" if value else "#b24c4c" for value in values]
    fig, ax = plt.subplots(figsize=(7.2, 4))
    ax.bar(labels, values, color=colors)
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, 1], ["Forbidden", "Allowed"])
    style_axes(ax, "Claim audit", None)
    save_current(fig, "figure6_claim_audit.png")


def figure7_external_convergent() -> None:
    if not E7_RESULTS.exists():
        return
    result = json.loads(E7_RESULTS.read_text(encoding="utf-8"))
    null = result["e7_label_shuffle_null"]
    labels = ["Observed", "Label shuffle"]
    values = [result["e7_stage_specificity"]["accuracy"], null["null_mean_accuracy"]]
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.bar(labels, values, color=["#2f6f73", "#9aa0a6"])
    ax.axhline(0.5, color="#333", linewidth=1, linestyle="--")
    ax.set_ylim(0.4, 0.72)
    style_axes(ax, "E7 ds004752 external convergent test", "Encoding vs maintenance accuracy")
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.01, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    save_current(fig, "figure7_e7_external_convergent.png")


def main() -> None:
    result = load_results()
    figure1_pipeline(result)
    figure2_window_inventory(result)
    figure3_reproducibility(result)
    figure4_specificity_and_nulls(result)
    figure5_subject_accuracy(result)
    figure6_claim_boundary(result)
    figure7_external_convergent()
    print(f"Wrote figures to {FIGURES}")


if __name__ == "__main__":
    main()
