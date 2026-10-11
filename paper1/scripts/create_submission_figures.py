from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


RESULTS = ROOT / "results"
FIGURES = ROOT / "manuscript" / "figures"


MODEL_COLORS = {
    "M0_state": "#6b7280",
    "M1_flat_task": "#9ca3af",
    "M2_strong_task": "#ef4444",
    "M3_cwp": "#2563eb",
    "M4_task_plus_cwp": "#10b981",
}


def setup() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURES / f"{name}.png", bbox_inches="tight")
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def figure_1_framework() -> None:
    fig, ax = plt.subplots(figsize=(8, 3.7))
    ax.axis("off")
    boxes = [
        ("S_t", 0.08, 0.58),
        ("Task label\n(flat condition ID)", 0.08, 0.18),
        ("CWP + context\n(compositional)", 0.36, 0.18),
        ("Model\nsame capacity", 0.36, 0.58),
        ("Predicted\nS_t+1", 0.66, 0.58),
        ("Held-out\nOOD tests", 0.66, 0.18),
    ]
    for text, x, y in boxes:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.35", fc="#f8fafc", ec="#334155", lw=1.2),
            transform=ax.transAxes,
        )
    arrows = [
        ((0.16, 0.58), (0.28, 0.58)),
        ((0.44, 0.58), (0.58, 0.58)),
        ((0.16, 0.18), (0.28, 0.18)),
        ((0.44, 0.18), (0.58, 0.18)),
        ((0.36, 0.28), (0.36, 0.48)),
        ((0.66, 0.48), (0.66, 0.30)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color="#334155", lw=1.4))
    ax.text(
        0.5,
        0.92,
        "Paper 1 tests whether reusable CWP-style labels improve OOD brain-state prediction",
        ha="center",
        va="center",
        weight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.04,
        "Claim boundary: local compositional advantage is not evidence for a universal cognitive primitive.",
        ha="center",
        va="center",
        color="#475569",
        transform=ax.transAxes,
    )
    save(fig, "figure_1_framework")


def figure_2_stage_sanity() -> None:
    metrics = pd.read_csv(RESULTS / "e2_cwp_existence_metrics.csv")
    summary = json.loads((RESULTS / "e2_cwp_existence_summary.json").read_text())
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(metrics))
    ax.bar(x, metrics["macro_f1"], color="#94a3b8", label="macro F1 by held-out subject")
    ax.axhline(summary["overall_macro_f1"], color="#2563eb", lw=2, label=f"overall macro F1 = {summary['overall_macro_f1']:.3f}")
    ax.set_title("Figure 2. Stage sanity check is weak under the current raw grid pipeline")
    ax.set_xlabel("Held-out subject fold")
    ax.set_ylabel("Macro F1")
    ax.set_ylim(0, max(0.45, float(metrics["macro_f1"].max()) + 0.05))
    ax.set_xticks([])
    ax.legend(loc="upper right")
    save(fig, "figure_2_stage_sanity")


def bar_from_primary(experiment: str, title: str, name: str) -> None:
    primary = pd.read_csv(RESULTS / "primary_metrics.csv")
    df = primary[primary["experiment"] == experiment].copy()
    order = ["M0_state", "M1_flat_task", "M2_strong_task", "M3_cwp", "M4_task_plus_cwp"]
    df["model"] = pd.Categorical(df["model"], categories=order, ordered=True)
    df = df.sort_values("model")
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = [MODEL_COLORS[m] for m in df["model"]]
    ax.bar(df["model"].astype(str), df["mean"], color=colors)
    ax.set_title(title)
    ax.set_ylabel("Held-out MSE (lower is better)")
    ax.tick_params(axis="x", rotation=25)
    save(fig, name)


def figure_4_cells() -> None:
    df = pd.read_csv(RESULTS / "e4_unseen_combination_metrics.csv")
    keep = df[df["model"].isin(["M2_strong_task", "M3_cwp", "M4_task_plus_cwp"])].copy()
    pivot = keep.pivot_table(index="heldout_cell", columns="model", values="mse", aggfunc="mean")
    pivot = pivot.sort_index()
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = range(len(pivot))
    width = 0.25
    for offset, model in [(-width, "M2_strong_task"), (0, "M3_cwp"), (width, "M4_task_plus_cwp")]:
        ax.bar([i + offset for i in x], pivot[model], width=width, label=model, color=MODEL_COLORS[model])
    ax.set_title("Figure 4. Leave-one-combination-out favors CWP-style composition")
    ax.set_ylabel("Held-out MSE (lower is better)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([c.replace("__", "\n") for c in pivot.index], rotation=0)
    ax.legend()
    save(fig, "figure_4_unseen_combination")


def figure_5_domains() -> None:
    df = pd.read_csv(RESULTS / "e5_unseen_domain_metrics.csv")
    keep = df[df["model"].isin(["M2_strong_task", "M3_cwp", "M4_task_plus_cwp"])].copy()
    pivot = keep.pivot_table(index="heldout_domain", columns="model", values="mse", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    x = range(len(pivot))
    width = 0.25
    for offset, model in [(-width, "M2_strong_task"), (0, "M3_cwp"), (width, "M4_task_plus_cwp")]:
        ax.bar([i + offset for i in x], pivot[model], width=width, label=model, color=MODEL_COLORS[model])
    ax.set_title("Figure 5. Unseen-domain test favors CWP-style composition within ds001635")
    ax.set_ylabel("Held-out MSE (lower is better)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(pivot.index)
    ax.legend()
    save(fig, "figure_5_unseen_domain")


def figure_6_nulls() -> None:
    df = pd.read_csv(RESULTS / "e6_null_falsification_metrics.csv")
    true_mse = float(df[df["null_test"] == "true_cwp"]["mse"].iloc[0])
    pseudo = df[(df["null_test"] != "true_cwp") & (df["status"] == "completed")]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(pseudo["mse"], bins=20, color="#cbd5e1", edgecolor="#64748b", label="matched pseudo/null ontologies")
    ax.axvline(true_mse, color="#2563eb", lw=2.5, label=f"true CWP MSE = {true_mse:.3f}")
    ax.set_title("Figure 6. True CWP survives available pseudo-ontology null tests")
    ax.set_xlabel("MSE")
    ax.set_ylabel("Null count")
    ax.legend()
    save(fig, "figure_6_null_falsification")


def figure_7_external() -> None:
    bar_from_primary(
        "E7",
        "Figure 7. External validation fails for CWP-only transfer on ds001634",
        "figure_7_external_failure",
    )


def main() -> None:
    setup()
    figure_1_framework()
    figure_2_stage_sanity()
    bar_from_primary("E3", "Figure 3. Incremental Task+CWP gain over strong task is inconclusive", "figure_3_m0_m4")
    figure_4_cells()
    figure_5_domains()
    figure_6_nulls()
    figure_7_external()
    print(f"wrote figures to {FIGURES}")


if __name__ == "__main__":
    main()
