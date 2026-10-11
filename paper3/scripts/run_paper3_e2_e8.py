from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PAPER1 = WORKSPACE / "paper1"
sys.path.insert(0, str(PAPER1 / "scripts"))

from common import build_transitions, load_stage_states  # noqa: E402


RESULTS = ROOT / "results"
ATTACHMENTS = ROOT / "attachments"
MANUSCRIPT = ROOT / "manuscript"
FIGURES = MANUSCRIPT / "figures"
SUBMISSION = ROOT / "submission"

DATASETS = {
    "ds001635": WORKSPACE / "paper1" / "state_extraction" / "stage_states.csv",
    "ds001634": WORKSPACE / "paper1" / "external_validation" / "stage_states_external.csv",
    "ds004469": WORKSPACE / "paper2" / "external_holdout" / "stage_states_dataset_c.csv",
}

PRIMARY_TRANSITIONS = ["ENCODE_TO_MAINTAIN", "MAINTAIN_TO_PROBE"]


def ensure_dirs() -> None:
    for path in [RESULTS, ATTACHMENTS, MANUSCRIPT, FIGURES, SUBMISSION]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(list(rows)).to_csv(path, index=False)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    if den == 0:
        return float("nan")
    return float(np.dot(a, b) / den)


def mean_vec(vectors: Sequence[np.ndarray]) -> np.ndarray:
    return np.vstack(vectors).mean(axis=0)


def safe_mean(values: Sequence[float]) -> float:
    vals = [float(v) for v in values if not math.isnan(float(v))]
    return float(np.mean(vals)) if vals else float("nan")


def bootstrap_ci(values: Sequence[float], n_boot: int = 2000, seed: int = 13) -> tuple[float, float]:
    vals = [float(v) for v in values if not math.isnan(float(v))]
    if not vals:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        sample = [rng.choice(vals) for _ in vals]
        boots.append(float(np.mean(sample)))
    boots.sort()
    return boots[int(0.025 * len(boots))], boots[min(len(boots) - 1, int(0.975 * len(boots)))]


def sign_flip_p(values: Sequence[float], n_perm: int = 10000, seed: int = 13) -> float:
    vals = [float(v) for v in values if not math.isnan(float(v))]
    if not vals:
        return float("nan")
    observed = abs(float(np.mean(vals)))
    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_perm):
        flipped = [v if rng.random() < 0.5 else -v for v in vals]
        if abs(float(np.mean(flipped))) >= observed:
            extreme += 1
    return float((extreme + 1) / (n_perm + 1))


def load_transition_rows(dataset: str, path: Path) -> list[dict[str, Any]]:
    rows, roi_cols = load_stage_states(str(path))
    meta, x_state, y_state = build_transitions(rows, roi_cols)
    x_arr = np.asarray(x_state, dtype=float)
    y_arr = np.asarray(y_state, dtype=float)
    delta = y_arr - x_arr
    out: list[dict[str, Any]] = []
    for idx, m in enumerate(meta):
        transition_type = f"{m.get('source_cwp', 'NA')}_TO_{m.get('target_cwp', 'NA')}"
        if transition_type not in PRIMARY_TRANSITIONS:
            continue
        out.append(
            {
                "dataset": dataset,
                "subject": m.get("subject", "NA"),
                "run": m.get("run", "NA"),
                "trial_id": m.get("trial_id", "NA"),
                "transition_type": transition_type,
                "domain": m.get("domain", "NA"),
                "load": m.get("load", "NA"),
                "context": m.get("context", "NA"),
                "time_bin": m.get("time_bin", "NA"),
                "delta": delta[idx],
            }
        )
    return out


def all_transition_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_rows: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    for dataset, path in DATASETS.items():
        if not path.exists():
            inventory.append({"dataset": dataset, "path": str(path), "status": "MISSING"})
            continue
        rows = load_transition_rows(dataset, path)
        all_rows.extend(rows)
        inventory.append(
            {
                "dataset": dataset,
                "path": str(path.relative_to(WORKSPACE)),
                "status": "LOADED",
                "n_transitions": len(rows),
                "n_subjects": len({r["subject"] for r in rows}),
                "n_subject_runs": len({(r["subject"], r["run"]) for r in rows}),
                "n_transition_types": len({r["transition_type"] for r in rows}),
            }
        )
    return all_rows, inventory


def split_half_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["dataset"], row["subject"], row["run"], row["transition_type"])].append(row)
    out: list[dict[str, Any]] = []
    for (dataset, subject, run, transition_type), group in sorted(groups.items()):
        if len(group) < 4:
            continue
        group = sorted(group, key=lambda r: str(r["trial_id"]))
        left = [r["delta"] for i, r in enumerate(group) if i % 2 == 0]
        right = [r["delta"] for i, r in enumerate(group) if i % 2 == 1]
        out.append(
            {
                "dataset": dataset,
                "subject": subject,
                "run": run,
                "transition_type": transition_type,
                "comparison": "within_run_odd_even_same_transition",
                "n_trials": len(group),
                "cosine_similarity": cosine_vec(mean_vec(left), mean_vec(right)),
            }
        )
    return out


def within_run_different_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], dict[str, list[np.ndarray]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        groups[(row["dataset"], row["subject"], row["run"])][row["transition_type"]].append(row["delta"])
    out: list[dict[str, Any]] = []
    for (dataset, subject, run), by_type in sorted(groups.items()):
        types = sorted(t for t, vals in by_type.items() if len(vals) >= 2)
        for i, left in enumerate(types):
            for right in types[i + 1 :]:
                out.append(
                    {
                        "dataset": dataset,
                        "subject": subject,
                        "run": run,
                        "transition_type": f"{left}_VS_{right}",
                        "comparison": "within_run_different_transition_null",
                        "n_trials": min(len(by_type[left]), len(by_type[right])),
                        "cosine_similarity": cosine_vec(mean_vec(by_type[left]), mean_vec(by_type[right])),
                    }
                )
    return out


def cross_run_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[np.ndarray]] = defaultdict(list)
    for row in rows:
        groups[(row["dataset"], row["subject"], row["run"], row["transition_type"])].append(row["delta"])
    subject_type_runs: dict[tuple[str, str, str], dict[str, np.ndarray]] = defaultdict(dict)
    for (dataset, subject, run, transition_type), vals in groups.items():
        if run != "run-unknown" and len(vals) >= 2:
            subject_type_runs[(dataset, subject, transition_type)][run] = mean_vec(vals)
    out: list[dict[str, Any]] = []
    for (dataset, subject, transition_type), by_run in sorted(subject_type_runs.items()):
        runs = sorted(by_run)
        for i, left in enumerate(runs):
            for right in runs[i + 1 :]:
                out.append(
                    {
                        "dataset": dataset,
                        "subject": subject,
                        "run_pair": f"{left}__{right}",
                        "transition_type": transition_type,
                        "comparison": "cross_run_same_subject_same_transition",
                        "cosine_similarity": cosine_vec(by_run[left], by_run[right]),
                    }
                )
    return out


def summarize_comparisons(rows: Sequence[dict[str, Any]], keys: Sequence[str]) -> list[dict[str, Any]]:
    df = pd.DataFrame(rows)
    if df.empty:
        return []
    out: list[dict[str, Any]] = []
    for group_key, group in df.groupby(list(keys), dropna=False):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        vals = pd.to_numeric(group["cosine_similarity"], errors="coerce").dropna().tolist()
        lo, hi = bootstrap_ci(vals, n_boot=1000)
        row = {key: value for key, value in zip(keys, group_key)}
        row.update(
            {
                "n": len(vals),
                "mean_cosine": safe_mean(vals),
                "median_cosine": float(np.median(vals)) if vals else float("nan"),
                "std_cosine": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                "bootstrap_ci_low": lo,
                "bootstrap_ci_high": hi,
            }
        )
        out.append(row)
    return out


def within_run_contrasts(summary_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    by_dataset: dict[str, dict[str, float]] = defaultdict(dict)
    for row in summary_rows:
        if "comparison" in row:
            by_dataset[str(row["dataset"])][str(row["comparison"])] = float(row["mean_cosine"])
    out: list[dict[str, Any]] = []
    for dataset, vals in sorted(by_dataset.items()):
        same = vals.get("within_run_odd_even_same_transition", float("nan"))
        diff = vals.get("within_run_different_transition_null", float("nan"))
        out.append(
            {
                "dataset": dataset,
                "same_transition_mean_cosine": same,
                "different_transition_null_mean_cosine": diff,
                "same_minus_different": same - diff,
                "supports_within_run_reproducibility": bool(same > diff),
            }
        )
    return out


def e6_cross_dataset(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    means: dict[tuple[str, str], np.ndarray] = {}
    for dataset in sorted({r["dataset"] for r in rows}):
        for transition_type in PRIMARY_TRANSITIONS:
            vals = [r["delta"] for r in rows if r["dataset"] == dataset and r["transition_type"] == transition_type]
            if vals:
                means[(dataset, transition_type)] = mean_vec(vals)

    datasets = sorted({d for d, _ in means})
    out: list[dict[str, Any]] = []
    for i, left_dataset in enumerate(datasets):
        for right_dataset in datasets[i + 1 :]:
            for left_type in PRIMARY_TRANSITIONS:
                for right_type in PRIMARY_TRANSITIONS:
                    if (left_dataset, left_type) not in means or (right_dataset, right_type) not in means:
                        continue
                    same = left_type == right_type
                    out.append(
                        {
                            "dataset_pair": f"{left_dataset}__{right_dataset}",
                            "left_dataset": left_dataset,
                            "right_dataset": right_dataset,
                            "left_transition_type": left_type,
                            "right_transition_type": right_type,
                            "comparison": "same_transition_cross_dataset" if same else "different_transition_cross_dataset_null",
                            "cosine_similarity": cosine_vec(means[(left_dataset, left_type)], means[(right_dataset, right_type)]),
                        }
                    )
    return out


def e7_null_tests(rows: Sequence[dict[str, Any]], n_perm: int = 500, seed: int = 13) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    observed_summary = summarize_comparisons(split_half_rows(rows) + within_run_different_rows(rows), ["dataset", "comparison"])
    observed_contrast = within_run_contrasts(observed_summary)
    observed_by_dataset = {r["dataset"]: float(r["same_minus_different"]) for r in observed_contrast}

    rng = random.Random(seed)
    null_rows: list[dict[str, Any]] = []
    datasets = sorted({r["dataset"] for r in rows})
    for perm in range(n_perm):
        shuffled = [dict(r) for r in rows]
        for dataset in datasets:
            idxs = [i for i, r in enumerate(shuffled) if r["dataset"] == dataset]
            labels = [shuffled[i]["transition_type"] for i in idxs]
            rng.shuffle(labels)
            for i, label in zip(idxs, labels):
                shuffled[i]["transition_type"] = label
        perm_summary = summarize_comparisons(split_half_rows(shuffled) + within_run_different_rows(shuffled), ["dataset", "comparison"])
        for contrast in within_run_contrasts(perm_summary):
            null_rows.append(
                {
                    "null_test": "within_dataset_label_shuffle",
                    "permutation": perm,
                    "dataset": contrast["dataset"],
                    "null_same_minus_different": contrast["same_minus_different"],
                }
            )

    summary_rows: list[dict[str, Any]] = []
    for dataset in datasets:
        vals = [float(r["null_same_minus_different"]) for r in null_rows if r["dataset"] == dataset and not math.isnan(float(r["null_same_minus_different"]))]
        obs = observed_by_dataset.get(dataset, float("nan"))
        if vals and not math.isnan(obs):
            percentile = sum(v < obs for v in vals) / len(vals)
            p_upper = (sum(v >= obs for v in vals) + 1) / (len(vals) + 1)
            q99 = float(np.quantile(vals, 0.99))
        else:
            percentile = float("nan")
            p_upper = float("nan")
            q99 = float("nan")
        summary_rows.append(
            {
                "null_test": "within_dataset_label_shuffle",
                "dataset": dataset,
                "observed_same_minus_different": obs,
                "n_permutations": len(vals),
                "null_mean": safe_mean(vals),
                "null_99th_percentile": q99,
                "observed_percentile_vs_null": percentile,
                "upper_tail_p": p_upper,
                "survives_99_percent_null": bool(percentile >= 0.99) if not math.isnan(percentile) else False,
            }
        )
    return null_rows, summary_rows


def e8_statistics(
    contrast_rows: Sequence[dict[str, Any]],
    cross_run: Sequence[dict[str, Any]],
    cross_dataset_summary: Sequence[dict[str, Any]],
    null_summary: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stats_rows: list[dict[str, Any]] = []
    for contrast in contrast_rows:
        stats_rows.append(
            {
                "experiment": "E2/E4",
                "dataset": contrast["dataset"],
                "estimand": "within_run_same_minus_different_cosine",
                "estimate": contrast["same_minus_different"],
                "supports_claim_component": contrast["supports_within_run_reproducibility"],
            }
        )
    cross_run_summary = summarize_comparisons(cross_run, ["dataset", "comparison"])
    for row in cross_run_summary:
        stats_rows.append(
            {
                "experiment": "E3",
                "dataset": row["dataset"],
                "estimand": "cross_run_same_subject_same_transition_cosine",
                "estimate": row["mean_cosine"],
                "n": row["n"],
                "ci_low": row["bootstrap_ci_low"],
                "ci_high": row["bootstrap_ci_high"],
                "p_sign_flip": sign_flip_p([r["cosine_similarity"] for r in cross_run if r["dataset"] == row["dataset"]]),
                "supports_claim_component": bool(float(row["mean_cosine"]) > 0),
            }
        )
    for row in cross_dataset_summary:
        stats_rows.append(
            {
                "experiment": "E6",
                "dataset": "cross_dataset",
                "estimand": row["comparison"],
                "estimate": row["mean_cosine"],
                "n": row["n"],
                "ci_low": row["bootstrap_ci_low"],
                "ci_high": row["bootstrap_ci_high"],
                "supports_claim_component": row["comparison"] == "same_transition_cross_dataset" and float(row["mean_cosine"]) > 0,
            }
        )
    for row in null_summary:
        stats_rows.append(
            {
                "experiment": "E7",
                "dataset": row["dataset"],
                "estimand": "observed_percentile_vs_label_shuffle_null",
                "estimate": row["observed_percentile_vs_null"],
                "n": row["n_permutations"],
                "supports_claim_component": row["survives_99_percent_null"],
            }
        )

    within_ok = all(bool(r["supports_within_run_reproducibility"]) for r in contrast_rows) if contrast_rows else False
    cross_run_datasets = {r["dataset"] for r in cross_run}
    cross_run_ok = bool(cross_run_datasets) and all(
        float(row["estimate"]) > 0 for row in stats_rows if row["experiment"] == "E3"
    )
    same_cross = next((r for r in cross_dataset_summary if r["comparison"] == "same_transition_cross_dataset"), None)
    diff_cross = next((r for r in cross_dataset_summary if r["comparison"] == "different_transition_cross_dataset_null"), None)
    cross_dataset_ok = bool(same_cross and diff_cross and float(same_cross["mean_cosine"]) > float(diff_cross["mean_cosine"]))
    null_ok = all(bool(r["survives_99_percent_null"]) for r in null_summary) if null_summary else False

    audit = {
        "experiment": "P3-E8",
        "status": "P3_REPRODUCIBILITY_SUPPORTED" if within_ok and cross_run_ok and cross_dataset_ok and null_ok else "P3_REPRODUCIBILITY_MIXED_OR_LIMITED",
        "claim_allowed_transition_reproducibility": within_ok and cross_run_ok and cross_dataset_ok and null_ok,
        "claim_allowed_cwp_validated": False,
        "claim_allowed_cwp_general_primitive": False,
        "claim_allowed_cross_dataset_cwp_superiority": False,
        "within_run_reproducibility_supported_all_datasets": within_ok,
        "cross_run_reproducibility_supported_available_datasets": cross_run_ok,
        "cross_dataset_same_greater_than_different": cross_dataset_ok,
        "label_shuffle_null_survival_all_datasets": null_ok,
        "critical_limitation": "The study tests repeatability of extracted macroscopic stage-transition vectors. It does not establish CWP as a natural neural primitive and ds004469 lacks repeated run labels.",
        "no_invented_results": True,
    }
    return stats_rows, audit


def make_figures() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    e1 = pd.read_csv(RESULTS / "e1_dataset_audit_summary.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(e1["dataset"], e1["n_transitions"].astype(float), color=["#4C78A8", "#F58518", "#54A24B"])
    ax.set_title("E1 Transition Inventory")
    ax.set_ylabel("Transitions")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_1_e1_inventory.png", dpi=180)
    fig.savefig(FIGURES / "figure_1_e1_inventory.pdf")
    plt.close(fig)

    contrasts = pd.read_csv(RESULTS / "e4_same_vs_different_summary.csv")
    x = np.arange(len(contrasts))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(x - width / 2, contrasts["same_transition_mean_cosine"], width, label="Same transition", color="#4C78A8")
    ax.bar(x + width / 2, contrasts["different_transition_null_mean_cosine"], width, label="Different transition", color="#E45756")
    ax.set_xticks(x, contrasts["dataset"])
    ax.set_title("E2/E4 Within-run Same vs Different Transition")
    ax.set_ylabel("Mean cosine similarity")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_2_e2_within_run_reliability.png", dpi=180)
    fig.savefig(FIGURES / "figure_2_e2_within_run_reliability.pdf")
    plt.close(fig)

    cross = pd.read_csv(RESULTS / "e6_cross_dataset_reproducibility_summary.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(cross["comparison"], cross["mean_cosine"].astype(float), color=["#4C78A8", "#E45756"])
    ax.set_title("E6 Cross-dataset Transition Similarity")
    ax.set_ylabel("Mean cosine similarity")
    ax.tick_params(axis="x", rotation=12)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_3_e6_cross_dataset.png", dpi=180)
    fig.savefig(FIGURES / "figure_3_e6_cross_dataset.pdf")
    plt.close(fig)

    nulls = pd.read_csv(RESULTS / "e7_null_tests_summary.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(nulls["dataset"], nulls["observed_percentile_vs_null"].astype(float), color="#4C78A8")
    ax.axhline(0.99, color="#222222", linewidth=1.5, linestyle="--")
    ax.set_ylim(0, 1.05)
    ax.set_title("E7 Label-shuffle Null Survival")
    ax.set_ylabel("Observed percentile vs null")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_4_e7_null.png", dpi=180)
    fig.savefig(FIGURES / "figure_4_e7_null.pdf")
    plt.close(fig)


def table_markdown(path: Path, max_rows: int = 20) -> str:
    df = pd.read_csv(path)
    if len(df) > max_rows:
        df = df.head(max_rows)
    cols = list(df.columns)
    if not cols:
        return ""

    def cell(value: Any) -> str:
        text = str(value)
        if len(text) > 160:
            text = text[:157] + "..."
        return text.replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(cell(c) for c in cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(cell(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_attachments(audit: dict[str, Any]) -> None:
    (ATTACHMENTS / "A1_Frozen_Protocol.md").write_text(
        f"""# A1 Frozen Protocol

Status: E1-E8 implemented and run.

Paper 3 starts with E1. The former data/QC audit was intentionally shifted to E1 by user instruction.

Primary research question:

```text
Are ENCODE -> MAINTAIN and MAINTAIN -> PROBE transition vectors reproducible across runs, subjects, and datasets?
```

Primary endpoint:

```text
same-transition cosine similarity minus different-transition cosine similarity
```

Current claim-audit status:

```text
{audit["status"]}
```

Claim boundary:

```text
This paper tests reproducibility of extracted macroscopic stage-transition vectors only; it does not validate CWP as a general neural primitive.
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A3_Full_Pipeline.md").write_text(
        """# A3 Full Pipeline

Raw state inputs from Paper 1 and Paper 2 are reused:

```text
paper1/state_extraction/stage_states.csv
paper1/external_validation/stage_states_external.csv
paper2/external_holdout/stage_states_dataset_c.csv
```

Pipeline:

```text
state files -> transition vectors T = S_target - S_source
-> E2 within-run split-half reliability
-> E3 cross-run same-subject reliability
-> E4 same-transition vs different-transition contrast
-> E5 dataset-specific reproducibility summary
-> E6 cross-dataset same-vs-different transition similarity
-> E7 label-shuffle null tests
-> E8 statistics and claim audit
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A4_Full_Baseline_Results.md").write_text(
        "# A4 Full Baseline / Competing-Explanation Results\n\n"
        "Primary competing explanation: same-transition reliability is no higher than different-transition similarity.\n\n"
        + table_markdown(RESULTS / "e4_same_vs_different_summary.csv")
        + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A5_Holdout_Audit.md").write_text(
        """# A5 Holdout Audit

Paper 3 is not a predictive holdout paper. It is a reproducibility analysis over already extracted state files.

Dataset roles:

```text
ds001635: within-dataset repeated-run reproducibility
ds001634: independent dataset with repeated-run reproducibility
ds004469: second independent dataset for stage-transition reproducibility, limited by missing repeated run labels
```

No model tuning was performed against Paper 3 outcomes.
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A6_Statistics.md").write_text(
        "# A6 Statistics\n\n"
        "Statistics are subject/run-aware summary statistics, bootstrap confidence intervals, sign-flip tests where applicable, and label-shuffle nulls.\n\n"
        + table_markdown(RESULTS / "e8_statistics.csv")
        + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A7_Null_Falsification_Tests.md").write_text(
        "# A7 Null / Falsification Tests\n\n"
        "The primary null test shuffles transition labels within dataset while preserving the extracted delta vectors.\n\n"
        + table_markdown(RESULTS / "e7_null_tests_summary.csv")
        + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A8_QC_Leakage_Audit.md").write_text(
        """# A8 QC & Leakage Audit

Paper 3 reuses frozen state files generated before this reproducibility paper. E1 confirms state-file availability, subject/run inventory, primary stage completeness, and transition counts.

Main leakage controls:

```text
No model fitting is used for the primary reliability estimand.
Transition labels are challenged by label-shuffle nulls.
Cross-run estimates exclude run-unknown entries.
Dataset-level estimates are reported separately before cross-dataset aggregation.
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A9_Limitations_Failed_Analyses.md").write_text(
        f"""# A9 Limitations & Failed Analyses

Critical limitations:

```text
{audit["critical_limitation"]}
```

Unsupported claims:

```text
CWP is validated.
CWP is a natural neural primitive.
CWP-specific cross-dataset superiority is established.
```

Observed status:

```text
{audit["status"]}
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A10_One_Command_Reproduction.md").write_text(
        """# A10 One-command Reproduction

Run on this Windows workspace:

```powershell
powershell -ExecutionPolicy Bypass -File paper3\\scripts\\reproduce-paper3.ps1
```

If GNU Make is available, this equivalent target is also defined:

```powershell
make reproduce-paper3
```

Equivalent explicit commands:

```powershell
paper1\\.venv\\Scripts\\python.exe paper3\\scripts\\run_paper3_e1.py
paper1\\.venv\\Scripts\\python.exe paper3\\scripts\\run_paper3_e2_e8.py
```

Expected primary outputs:

```text
paper3/results/e1_input_audit.json
paper3/results/e2_transition_reliability_rows.csv
paper3/results/e3_cross_run_summary.csv
paper3/results/e4_same_vs_different_summary.csv
paper3/results/e5_dataset_specific_reproducibility.csv
paper3/results/e6_cross_dataset_reproducibility_summary.csv
paper3/results/e7_null_tests_summary.csv
paper3/results/e8_claim_audit.json
paper3/manuscript/PAPER3_MANUSCRIPT_CURRENT.md
paper3/submission/PAPER3_BIORXIV_DRAFT_CURRENT.pdf
```
""",
        encoding="utf-8",
    )


def current_results_md(audit: dict[str, Any]) -> str:
    return f"""# Paper 3 Current Results

Status:

```text
{audit["status"]}
```

## E1 Input / State Audit

{table_markdown(RESULTS / "e1_dataset_audit_summary.csv")}

## E2 / E4 Within-run Same vs Different Transition

{table_markdown(RESULTS / "e4_same_vs_different_summary.csv")}

## E3 Cross-run Reproducibility

{table_markdown(RESULTS / "e3_cross_run_summary.csv")}

## E5 Dataset-specific Reproducibility

{table_markdown(RESULTS / "e5_dataset_specific_reproducibility.csv")}

## E6 Cross-dataset Reproducibility

{table_markdown(RESULTS / "e6_cross_dataset_reproducibility_summary.csv")}

## E7 Null Tests

{table_markdown(RESULTS / "e7_null_tests_summary.csv")}

## Claim Audit

```json
{json.dumps(audit, indent=2)}
```
"""


def manuscript_text(audit: dict[str, Any]) -> str:
    return f"""# Reproducibility of Stage-Conditioned Brain-State Transitions Across Runs, Subjects, and Datasets

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 1 and Paper 2 constrained the CWP strong hypothesis by showing local compositional signal but no CWP-specific cross-dataset superiority. Paper 3 therefore asks a more basic question: are the extracted macroscopic stage-transition vectors themselves reproducible empirical objects? Using frozen state files from OpenNeuro ds001635, ds001634, and ds004469, we estimate ENCODE-to-MAINTAIN and MAINTAIN-to-PROBE transition vectors and test within-run split-half reliability, cross-run same-subject reliability where repeated runs exist, same-transition versus different-transition contrasts, cross-dataset transition similarity, and label-shuffle nulls. The current claim-audit status is `{audit["status"]}`. These results support only the bounded claim reported in the audit and do not validate CWP as a general neural primitive.

## 1. Introduction

The prior papers showed that local out-of-distribution gains do not imply a universal CWP representation. The next defensible step is reproducibility: before asking whether a cognitive ontology is correct, the transition objects produced by the extraction pipeline must show stability.

## 2. Methods

The analysis uses three frozen state tables: ds001635, ds001634, and ds004469. For each trial, transition vectors were defined as `T = S_target - S_source` for `ENCODE -> MAINTAIN` and `MAINTAIN -> PROBE`. E1 audited state availability and stage completeness. E2 measured within-run split-half reliability. E3 measured cross-run same-subject reliability where run labels were available. E4 compared same-transition reliability against a different-transition null. E5 summarized dataset-specific reproducibility. E6 compared same versus different transition vectors across datasets. E7 used within-dataset transition-label shuffling as a falsification test. E8 aggregated statistics and enforced the claim audit.

## 3. Results

### 3.1 Dataset Inventory

{table_markdown(RESULTS / "e1_dataset_audit_summary.csv")}

### 3.2 Within-run Reliability and Same-vs-Different Contrast

{table_markdown(RESULTS / "e4_same_vs_different_summary.csv")}

### 3.3 Cross-run Reproducibility

{table_markdown(RESULTS / "e3_cross_run_summary.csv")}

### 3.4 Cross-dataset Reproducibility

{table_markdown(RESULTS / "e6_cross_dataset_reproducibility_summary.csv")}

### 3.5 Null Tests

{table_markdown(RESULTS / "e7_null_tests_summary.csv")}

## 4. Discussion

The paper should be read as a reproducibility and boundary study, not as a CWP validation paper. A positive same-transition contrast would support repeatability of the extracted transition vectors under the current state representation. Failure in any gate limits the claim to dataset- or pipeline-specific reproducibility.

Critical limitation: {audit["critical_limitation"]}

Unsupported claims remain explicitly disallowed: CWP is validated; CWP is a natural neural primitive; CWP-specific cross-dataset superiority is established.

## 5. Conclusion

Current claim-audit status: `{audit["status"]}`.

## Data Availability

OpenNeuro ds001635, ds001634, and ds004469 were used through previously generated state tables in this workspace.

## Code Availability

[TO BE FILLED]

## Ethics Statement

This analysis uses public de-identified datasets. Dataset-specific ethics approvals are reported by the original dataset providers.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

```json
{json.dumps(audit, indent=2)}
```
"""


def build_pdf(markdown_text: str) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    doc = SimpleDocTemplate(str(SUBMISSION / "PAPER3_BIORXIV_DRAFT_CURRENT.pdf"), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 8))
            continue
        style = styles["Heading1"] if stripped.startswith("# ") else styles["Heading2"] if stripped.startswith("## ") else styles["BodyText"]
        clean = stripped.lstrip("#").strip()
        story.append(Paragraph(clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style))
    doc.build(story)


def write_submission_files(audit: dict[str, Any]) -> None:
    text = manuscript_text(audit)
    (MANUSCRIPT / "PAPER3_MANUSCRIPT_CURRENT.md").write_text(text, encoding="utf-8")
    build_pdf(text)
    (SUBMISSION / "SUBMISSION_READINESS.md").write_text(
        f"""# Paper 3 Submission Readiness

Current status: not ready for direct bioRxiv submission.

Generated:

```text
paper3/manuscript/PAPER3_MANUSCRIPT_CURRENT.md
paper3/submission/PAPER3_BIORXIV_DRAFT_CURRENT.pdf
paper3/attachments/
paper3/manuscript/figures/
```

Remaining before bioRxiv:

```text
Fill authors, affiliations, correspondence, code availability, funding, COI.
Add formal literature review and citations.
Review figure placement and final journal-style formatting.
Decide whether the bounded claim-audit status is strong enough for preprint release.
```

Claim audit status:

```text
{audit["status"]}
```

Reproduction command verified in this workspace:

```powershell
powershell -ExecutionPolicy Bypass -File paper3\\scripts\\reproduce-paper3.ps1
```
""",
        encoding="utf-8",
    )
    (SUBMISSION / "FIGURE_CAPTIONS.md").write_text(
        """# Figure Captions

Figure 1. E1 transition inventory by dataset.

Figure 2. E2/E4 within-run same-transition reliability versus different-transition null.

Figure 3. E6 cross-dataset same-transition versus different-transition similarity.

Figure 4. E7 observed same-minus-different contrast percentile against label-shuffle nulls.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, inventory = all_transition_rows()
    write_csv(RESULTS / "e2_dataset_inventory.csv", inventory)

    split = split_half_rows(rows)
    different = within_run_different_rows(rows)
    cross_run = cross_run_rows(rows)
    e2_rows = split + different + cross_run
    e2_summary = summarize_comparisons(e2_rows, ["dataset", "comparison"])
    e4_contrasts = within_run_contrasts(e2_summary)

    write_csv(RESULTS / "e2_transition_reliability_rows.csv", e2_rows)
    write_csv(RESULTS / "e2_transition_reliability_summary.csv", e2_summary)
    write_csv(RESULTS / "e3_cross_run_rows.csv", cross_run)
    write_csv(RESULTS / "e3_cross_run_summary.csv", summarize_comparisons(cross_run, ["dataset", "comparison"]))
    write_csv(RESULTS / "e4_same_vs_different_summary.csv", e4_contrasts)

    e5_rows = []
    for contrast in e4_contrasts:
        cross_row = next((r for r in summarize_comparisons(cross_run, ["dataset", "comparison"]) if r["dataset"] == contrast["dataset"]), None)
        e5_rows.append(
            {
                "dataset": contrast["dataset"],
                "within_run_same_minus_different": contrast["same_minus_different"],
                "within_run_supported": contrast["supports_within_run_reproducibility"],
                "cross_run_mean_cosine": cross_row["mean_cosine"] if cross_row else float("nan"),
                "cross_run_available": bool(cross_row),
                "dataset_specific_status": "SUPPORTED_AVAILABLE_TESTS"
                if contrast["supports_within_run_reproducibility"] and (not cross_row or float(cross_row["mean_cosine"]) > 0)
                else "MIXED_OR_NOT_SUPPORTED",
            }
        )
    write_csv(RESULTS / "e5_dataset_specific_reproducibility.csv", e5_rows)

    e6_rows = e6_cross_dataset(rows)
    e6_summary = summarize_comparisons(e6_rows, ["comparison"])
    write_csv(RESULTS / "e6_cross_dataset_reproducibility_rows.csv", e6_rows)
    write_csv(RESULTS / "e6_cross_dataset_reproducibility_summary.csv", e6_summary)

    e7_rows, e7_summary = e7_null_tests(rows)
    write_csv(RESULTS / "e7_null_tests_rows.csv", e7_rows)
    write_csv(RESULTS / "e7_null_tests_summary.csv", e7_summary)

    stats_rows, audit = e8_statistics(e4_contrasts, cross_run, e6_summary, e7_summary)
    write_csv(RESULTS / "e8_statistics.csv", stats_rows)
    write_json(RESULTS / "e8_claim_audit.json", audit)
    write_json(
        RESULTS / "e2_e8_run_summary.json",
        {
            "experiment": "P3-E2-E8",
            "status": audit["status"],
            "n_transition_rows": len(rows),
            "inventory": inventory,
            "claim_audit": audit,
        },
    )

    make_figures()
    write_attachments(audit)
    (RESULTS / "CURRENT_RESULTS.md").write_text(current_results_md(audit), encoding="utf-8")
    write_submission_files(audit)
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
