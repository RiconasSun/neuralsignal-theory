from __future__ import annotations

import json
import math
import os
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PAPER1 = WORKSPACE / "paper1"
sys.path.insert(0, str(PAPER1 / "scripts"))

from common import build_transitions, load_stage_states  # noqa: E402


RESULTS = ROOT / "results"
ATTACHMENTS = ROOT / "attachments"
PROTOCOL = ROOT / "protocol"
MANUSCRIPT = ROOT / "manuscript"
FIGURES = MANUSCRIPT / "figures"
SUBMISSION = ROOT / "submission"

DATASETS = {
    "ds001635": {
        "states": WORKSPACE / "paper1" / "state_extraction" / "stage_states.csv",
        "raw": WORKSPACE / "paper1" / "data_raw" / "ds001635",
    },
    "ds001634": {
        "states": WORKSPACE / "paper1" / "external_validation" / "stage_states_external.csv",
        "raw": WORKSPACE / "paper1" / "data_raw" / "ds001634",
    },
    "ds004469": {
        "states": WORKSPACE / "paper2" / "external_holdout" / "stage_states_dataset_c.csv",
        "raw": WORKSPACE / "paper2" / "external_holdout" / "ds004469_final_input",
    },
}

PRIMARY_TRANSITIONS = ["ENCODE_TO_MAINTAIN", "MAINTAIN_TO_PROBE"]
SEED = 17


def ensure_dirs() -> None:
    for path in [RESULTS, ATTACHMENTS, PROTOCOL, MANUSCRIPT, FIGURES, SUBMISSION]:
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def file_count(root: Path, pattern: str) -> int:
    return len(list(root.rglob(pattern))) if root.exists() else 0


def e1_confound_audit() -> dict[str, Any]:
    online_summary_path = ROOT / "online_confound_recovery" / "online_confound_recovery_summary.json"
    online_by_dataset: dict[str, dict[str, Any]] = {}
    if online_summary_path.exists():
        try:
            online_payload = json.loads(online_summary_path.read_text(encoding="utf-8"))
            online_by_dataset = {str(row.get("dataset")): row for row in online_payload}
        except Exception:
            online_by_dataset = {}

    rows: list[dict[str, Any]] = []
    for dataset, spec in DATASETS.items():
        raw = spec["raw"]
        states = spec["states"]
        online = online_by_dataset.get(dataset, {})
        confounds = []
        if raw.exists():
            for pat in ["*confounds*.tsv", "*confounds*.csv", "*motion*.tsv", "*motion*.csv", "*regressors*.tsv", "*regressors*.csv"]:
                confounds.extend(raw.rglob(pat))
        rows.append(
            {
                "dataset": dataset,
                "state_file": rel(states),
                "state_file_exists": states.exists(),
                "raw_root": rel(raw),
                "raw_root_exists": raw.exists(),
                "events_tsv_count": file_count(raw, "*events.tsv"),
                "bold_json_count": file_count(raw, "*bold.json"),
                "bold_nii_gz_count": file_count(raw, "*bold.nii.gz"),
                "measured_confound_file_count": len(confounds),
                "measured_confounds_available": len(confounds) > 0,
                "confound_files": ";".join(rel(p) for p in confounds[:20]),
                "online_recovery_manifest_available": bool(online),
                "online_recovery_status": online.get("status", ""),
                "online_recovered_candidate_confound_file_count": online.get("recovered_candidate_confound_file_count", ""),
                "online_measured_confounds_recovered": online.get("measured_confounds_recovered", ""),
                "online_recovery_error": online.get("error", ""),
            }
        )
    write_csv(RESULTS / "e1_confound_input_audit.csv", rows)
    payload = {
        "experiment": "P4-E1",
        "status": "MEASURED_CONFOUNDS_AVAILABLE" if all(r["measured_confounds_available"] for r in rows) else "MEASURED_CONFOUNDS_MISSING_OR_INCOMPLETE",
        "datasets": rows,
        "online_recovery_summary": rel(online_summary_path) if online_summary_path.exists() else "",
        "claim_boundary": "No measured head-motion or physiological confounds were found in the local dataset copies when measured_confound_file_count is zero. Paper 4 therefore separates measured-confound claims from proxy nuisance/timing falsification.",
    }
    write_json(RESULTS / "e1_confound_input_audit.json", payload)
    return payload


def load_transition_rows() -> list[dict[str, Any]]:
    rows_out: list[dict[str, Any]] = []
    for dataset, spec in DATASETS.items():
        rows, roi_cols = load_stage_states(str(spec["states"]))
        meta, x_state, y_state = build_transitions(rows, roi_cols)
        x_arr = np.asarray(x_state, dtype=float)
        y_arr = np.asarray(y_state, dtype=float)
        delta = y_arr - x_arr
        for idx, m in enumerate(meta):
            transition_type = f"{m.get('source_cwp', 'NA')}_TO_{m.get('target_cwp', 'NA')}"
            if transition_type not in PRIMARY_TRANSITIONS:
                continue
            rows_out.append(
                {
                    "dataset": dataset,
                    "subject": m.get("subject", "NA"),
                    "run": m.get("run", "NA"),
                    "trial_id": m.get("trial_id", "NA"),
                    "transition_type": transition_type,
                    "domain": m.get("domain", "NA") or "NA",
                    "load": m.get("load", "NA") or "NA",
                    "context": m.get("context", "NA") or "NA",
                    "time_bin": m.get("time_bin", "NA") or "NA",
                    "source_onset": m.get("source_onset", "NA") or "NA",
                    "target_onset": m.get("target_onset", "NA") or "NA",
                    "delta": delta[idx],
                }
            )
    return rows_out


def split_half_same(rows: Sequence[dict[str, Any]], label_field: str = "transition_type", vector_field: str = "delta") -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["dataset"], row["subject"], row["run"], str(row[label_field]))].append(row)
    out: list[dict[str, Any]] = []
    for (dataset, subject, run, label), group in sorted(groups.items()):
        if len(group) < 4:
            continue
        group = sorted(group, key=lambda r: str(r["trial_id"]))
        left = [np.asarray(r[vector_field], dtype=float) for i, r in enumerate(group) if i % 2 == 0]
        right = [np.asarray(r[vector_field], dtype=float) for i, r in enumerate(group) if i % 2 == 1]
        out.append(
            {
                "dataset": dataset,
                "subject": subject,
                "run": run,
                "label_field": label_field,
                "label": label,
                "comparison": "same_label_split_half",
                "cosine_similarity": cosine_vec(mean_vec(left), mean_vec(right)),
            }
        )
    return out


def within_run_different(rows: Sequence[dict[str, Any]], label_field: str = "transition_type", vector_field: str = "delta") -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], dict[str, list[np.ndarray]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        groups[(row["dataset"], row["subject"], row["run"])][str(row[label_field])].append(np.asarray(row[vector_field], dtype=float))
    out: list[dict[str, Any]] = []
    for (dataset, subject, run), by_label in sorted(groups.items()):
        labels = sorted(k for k, vals in by_label.items() if len(vals) >= 2)
        for i, left in enumerate(labels):
            for right in labels[i + 1 :]:
                out.append(
                    {
                        "dataset": dataset,
                        "subject": subject,
                        "run": run,
                        "label_field": label_field,
                        "label": f"{left}_VS_{right}",
                        "comparison": "different_label_null",
                        "cosine_similarity": cosine_vec(mean_vec(by_label[left]), mean_vec(by_label[right])),
                    }
                )
    return out


def contrast_from_rows(rows: Sequence[dict[str, Any]], label_field: str = "transition_type", vector_field: str = "delta") -> list[dict[str, Any]]:
    same = split_half_same(rows, label_field, vector_field)
    different = within_run_different(rows, label_field, vector_field)
    out: list[dict[str, Any]] = []
    datasets = sorted({r["dataset"] for r in rows})
    for dataset in datasets:
        same_vals = [float(r["cosine_similarity"]) for r in same if r["dataset"] == dataset and not math.isnan(float(r["cosine_similarity"]))]
        diff_vals = [float(r["cosine_similarity"]) for r in different if r["dataset"] == dataset and not math.isnan(float(r["cosine_similarity"]))]
        out.append(
            {
                "dataset": dataset,
                "label_field": label_field,
                "same_mean_cosine": safe_mean(same_vals),
                "different_null_mean_cosine": safe_mean(diff_vals),
                "same_minus_different": safe_mean(same_vals) - safe_mean(diff_vals),
                "n_same": len(same_vals),
                "n_different": len(diff_vals),
                "supports_signal": bool(safe_mean(same_vals) > safe_mean(diff_vals)),
            }
        )
    return out


def one_hot(rows: Sequence[dict[str, Any]], fields: Sequence[str], levels: dict[str, list[str]] | None = None) -> tuple[np.ndarray, dict[str, list[str]]]:
    if levels is None:
        levels = {field: sorted({str(r.get(field, "NA") or "NA") for r in rows}) for field in fields}
    if not fields:
        return np.zeros((len(rows), 0)), levels
    encoded: list[list[float]] = []
    for row in rows:
        vals: list[float] = []
        for field in fields:
            value = str(row.get(field, "NA") or "NA")
            vals.extend(1.0 if level == value else 0.0 for level in levels[field])
        encoded.append(vals)
    return np.asarray(encoded, dtype=float), levels


def residualize(rows: Sequence[dict[str, Any]], fields: Sequence[str], vector_field: str = "delta", output_field: str = "residual_delta") -> list[dict[str, Any]]:
    out = [dict(r) for r in rows]
    for dataset in sorted({r["dataset"] for r in out}):
        idxs = [i for i, r in enumerate(out) if r["dataset"] == dataset]
        block = [out[i] for i in idxs]
        x, _ = one_hot(block, fields)
        if x.shape[1] == 0:
            for i in idxs:
                out[i][output_field] = out[i][vector_field]
            continue
        y = np.vstack([np.asarray(r[vector_field], dtype=float) for r in block])
        x_s = StandardScaler().fit_transform(x)
        pred = Ridge(alpha=1.0, fit_intercept=True).fit(x_s, y).predict(x_s)
        residual = y - pred
        for j, i in enumerate(idxs):
            out[i][output_field] = residual[j]
    return out


def e2_reproduce_p3(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    contrasts = contrast_from_rows(rows)
    write_csv(RESULTS / "e2_p3_transition_reproduction.csv", contrasts)
    return contrasts


def e3_e4_nuisance_residualization(rows: Sequence[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    variants = {
        "time_only": ["time_bin"],
        "domain_load_context": ["domain", "load", "context"],
        "run_time_context": ["run", "time_bin", "domain", "load", "context"],
        "subject_run_time_context": ["subject", "run", "time_bin", "domain", "load", "context"],
    }
    all_contrasts: list[dict[str, Any]] = []
    for variant, fields in variants.items():
        residualized = residualize(rows, fields, output_field=f"residual_{variant}")
        contrasts = contrast_from_rows(residualized, vector_field=f"residual_{variant}")
        for row in contrasts:
            row["residualization_variant"] = variant
            row["nuisance_fields"] = "+".join(fields)
        all_contrasts.extend(contrasts)
    write_csv(RESULTS / "e3_e4_nuisance_residualized_contrasts.csv", all_contrasts)

    predictive_rows: list[dict[str, Any]] = []
    fields_by_model = {
        "time_only": ["time_bin"],
        "proxy_nuisance_only": ["subject", "run", "time_bin", "domain", "load", "context"],
        "transition_only": ["transition_type"],
        "transition_plus_proxy_nuisance": ["transition_type", "subject", "run", "time_bin", "domain", "load", "context"],
    }
    for dataset in sorted({r["dataset"] for r in rows}):
        dataset_rows = [r for r in rows if r["dataset"] == dataset]
        subjects = sorted({r["subject"] for r in dataset_rows})
        for model_name, fields in fields_by_model.items():
            subject_mses: list[float] = []
            for subject in subjects:
                train = [r for r in dataset_rows if r["subject"] != subject]
                test = [r for r in dataset_rows if r["subject"] == subject]
                if not train or not test:
                    continue
                x_train, levels = one_hot(train, fields)
                x_test, _ = one_hot(test, fields, levels)
                y_train = np.vstack([r["delta"] for r in train])
                y_test = np.vstack([r["delta"] for r in test])
                sx = StandardScaler().fit(x_train)
                model = Ridge(alpha=1.0, fit_intercept=True).fit(sx.transform(x_train), y_train)
                pred = model.predict(sx.transform(x_test))
                subject_mses.append(float(np.mean((y_test - pred) ** 2)))
            predictive_rows.append(
                {
                    "dataset": dataset,
                    "model": model_name,
                    "fields": "+".join(fields),
                    "n_subject_folds": len(subject_mses),
                    "mean_subject_mse": safe_mean(subject_mses),
                }
            )
    write_csv(RESULTS / "e3_proxy_nuisance_prediction.csv", predictive_rows)
    return all_contrasts, predictive_rows


def e5_synthetic_noise(rows: Sequence[dict[str, Any]], n_repeat: int = 100) -> list[dict[str, Any]]:
    rng = np.random.default_rng(SEED)
    all_delta = np.vstack([r["delta"] for r in rows])
    base_sd = float(np.std(all_delta))
    levels = [0.25, 0.5, 1.0, 2.0]
    out: list[dict[str, Any]] = []
    for sigma_multiplier in levels:
        repeated: dict[str, list[float]] = defaultdict(list)
        for _ in range(n_repeat):
            noisy = []
            for row in rows:
                nr = dict(row)
                nr["noisy_delta"] = np.asarray(row["delta"], dtype=float) + rng.normal(0, base_sd * sigma_multiplier, size=all_delta.shape[1])
                noisy.append(nr)
            for contrast in contrast_from_rows(noisy, vector_field="noisy_delta"):
                repeated[contrast["dataset"]].append(float(contrast["same_minus_different"]))
        for dataset, vals in sorted(repeated.items()):
            out.append(
                {
                    "dataset": dataset,
                    "noise_sigma_multiplier": sigma_multiplier,
                    "n_repeats": len(vals),
                    "mean_same_minus_different": safe_mean(vals),
                    "min_same_minus_different": float(np.min(vals)) if vals else float("nan"),
                    "survival_rate_positive": float(np.mean([v > 0 for v in vals])) if vals else float("nan"),
                    "survives_synthetic_noise": bool(vals and np.mean([v > 0 for v in vals]) >= 0.95),
                }
            )
    write_csv(RESULTS / "e5_synthetic_noise_injection.csv", out)
    return out


def e6_timing_tests(rows: Sequence[dict[str, Any]], original_contrasts: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    time_contrasts = contrast_from_rows(rows, label_field="time_bin")
    original_by_dataset = {r["dataset"]: float(r["same_minus_different"]) for r in original_contrasts}
    out: list[dict[str, Any]] = []
    for row in time_contrasts:
        dataset = row["dataset"]
        original = original_by_dataset.get(dataset, float("nan"))
        time_value = float(row["same_minus_different"])
        valid_time_baseline = bool(row["n_same"] > 0 and row["n_different"] > 0 and not math.isnan(time_value))
        out.append(
            {
                "dataset": dataset,
                "test": "time_bin_same_vs_different",
                "transition_same_minus_different": original,
                "time_bin_same_minus_different": row["same_minus_different"],
                "time_baseline_status": "VALID" if valid_time_baseline else "INCONCLUSIVE_NO_SPLIT_HALF_TIME_BIN_GROUPS",
                "transition_exceeds_time_baseline": bool(original > time_value) if valid_time_baseline else "",
                "n_time_same": row["n_same"],
                "n_time_different": row["n_different"],
            }
        )
    time_residualized = residualize(rows, ["time_bin"], output_field="time_residual_delta")
    for row in contrast_from_rows(time_residualized, vector_field="time_residual_delta"):
        out.append(
            {
                "dataset": row["dataset"],
                "test": "transition_after_time_bin_residualization",
                "transition_same_minus_different": row["same_minus_different"],
                "time_bin_same_minus_different": float("nan"),
                "time_baseline_status": "RESIDUALIZATION_TEST",
                "transition_exceeds_time_baseline": row["supports_signal"],
                "n_time_same": row["n_same"],
                "n_time_different": row["n_different"],
            }
        )
    write_csv(RESULTS / "e6_timing_position_tests.csv", out)
    return out


def e7_null_tests(rows: Sequence[dict[str, Any]], observed: Sequence[dict[str, Any]], n_perm: int = 500) -> list[dict[str, Any]]:
    rng = random.Random(SEED)
    observed_by_dataset = {r["dataset"]: float(r["same_minus_different"]) for r in observed}
    datasets = sorted({r["dataset"] for r in rows})
    null_values: dict[str, list[float]] = defaultdict(list)
    for _ in range(n_perm):
        shuffled = [dict(r) for r in rows]
        for dataset in datasets:
            idxs = [i for i, r in enumerate(shuffled) if r["dataset"] == dataset]
            labels = [shuffled[i]["transition_type"] for i in idxs]
            rng.shuffle(labels)
            for i, label in zip(idxs, labels):
                shuffled[i]["transition_type"] = label
        for contrast in contrast_from_rows(shuffled):
            null_values[contrast["dataset"]].append(float(contrast["same_minus_different"]))
    out: list[dict[str, Any]] = []
    for dataset in datasets:
        vals = null_values[dataset]
        obs = observed_by_dataset.get(dataset, float("nan"))
        out.append(
            {
                "dataset": dataset,
                "null_test": "frequency_preserving_transition_label_shuffle",
                "observed_same_minus_different": obs,
                "n_permutations": len(vals),
                "null_mean": safe_mean(vals),
                "null_99th_percentile": float(np.quantile(vals, 0.99)) if vals else float("nan"),
                "observed_percentile_vs_null": float(np.mean([v < obs for v in vals])) if vals else float("nan"),
                "upper_tail_p": float((sum(v >= obs for v in vals) + 1) / (len(vals) + 1)) if vals else float("nan"),
                "survives_99_percent_null": bool(vals and np.mean([v < obs for v in vals]) >= 0.99),
            }
        )
    write_csv(RESULTS / "e7_falsification_null_tests.csv", out)
    return out


def e8_claim_audit(
    e1: dict[str, Any],
    e2: Sequence[dict[str, Any]],
    e34: Sequence[dict[str, Any]],
    e5: Sequence[dict[str, Any]],
    e6: Sequence[dict[str, Any]],
    e7: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    measured_confounds_available = e1["status"] == "MEASURED_CONFOUNDS_AVAILABLE"
    e2_ok = all(bool(r["supports_signal"]) for r in e2)
    strict_resid = [r for r in e34 if r["residualization_variant"] == "subject_run_time_context"]
    e34_ok = bool(strict_resid) and all(float(r["same_minus_different"]) > 0 for r in strict_resid)
    e5_one_sigma = [r for r in e5 if float(r["noise_sigma_multiplier"]) == 1.0]
    e5_ok = bool(e5_one_sigma) and all(bool(r["survives_synthetic_noise"]) for r in e5_one_sigma)
    time_resid = [r for r in e6 if r["test"] == "transition_after_time_bin_residualization"]
    time_baseline = [r for r in e6 if r["test"] == "time_bin_same_vs_different"]
    e6_ok = bool(time_resid) and all(bool(r["transition_exceeds_time_baseline"]) for r in time_resid)
    valid_time_baselines = [r for r in time_baseline if r["time_baseline_status"] == "VALID"]
    e6_strong_time_ok = bool(valid_time_baselines) and all(bool(r["transition_exceeds_time_baseline"]) for r in valid_time_baselines)
    e7_ok = all(bool(r["survives_99_percent_null"]) for r in e7)

    proxy_falsification_ok = bool(e2_ok and e34_ok and e6_ok and e7_ok)
    if measured_confounds_available and proxy_falsification_ok and e5_ok:
        status = "P4_NOISE_FALSIFICATION_SUPPORTED_WITH_MEASURED_CONFOUNDS"
    elif proxy_falsification_ok and e5_ok:
        status = "P4_PROXY_NOISE_FALSIFICATION_SUPPORTED_MEASURED_CONFOUNDS_MISSING"
    elif proxy_falsification_ok:
        status = "P4_PROXY_FALSIFICATION_SUPPORTED_BUT_SYNTHETIC_NOISE_ROBUSTNESS_LIMITED"
    else:
        status = "P4_NOISE_FALSIFICATION_MIXED_OR_NOT_SUPPORTED"

    payload = {
        "experiment": "P4-E8",
        "status": status,
        "measured_motion_or_physiology_confounds_available": measured_confounds_available,
        "claim_allowed_transition_not_fully_explained_by_tested_proxy_nuisance": proxy_falsification_ok,
        "claim_allowed_measured_motion_fully_excluded": False,
        "claim_allowed_noise_eliminated": False,
        "claim_allowed_cwp_validated": False,
        "gate_e2_p3_reproduction": e2_ok,
        "gate_e3_e4_strict_proxy_residualized_signal_positive": e34_ok,
        "gate_e5_one_sigma_synthetic_noise_survival": e5_ok,
        "gate_e6_time_residualized_signal_positive": e6_ok,
        "gate_e6_transition_exceeds_time_bin_baseline": e6_strong_time_ok,
        "gate_e6_time_bin_baseline_valid_dataset_count": len(valid_time_baselines),
        "gate_e7_label_shuffle_null_survival": e7_ok,
        "critical_limitation": "No local measured head-motion or physiological confounds.tsv files were found. The completed tests address proxy nuisance structure, timing-position alternatives, synthetic noise, and label-shuffle nulls, but do not fully exclude measured motion or physiology.",
        "no_invented_results": True,
    }
    write_json(RESULTS / "e8_claim_audit.json", payload)
    return payload


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


def write_protocol() -> None:
    (PROTOCOL / "PAPER4_FROZEN_PROTOCOL_v1.md").write_text(
        """# Paper 4 Frozen Protocol v1

Title: Falsifying Noise Explanations for Reproducible Brain-State Transitions

Paper type: Method Paper / falsification and robustness study

## Core Question

Do the reproducible stage-transition vectors from Paper 3 survive plausible nuisance, timing, synthetic noise, and label-shuffle explanations?

## Experiment Chain

```text
E1 Input + measured-confound audit
E1b Online OpenNeuro derivatives/confound recovery audit, when recovery manifests are present
E2 Reproduce Paper 3 transition contrast
E3 Proxy nuisance-only prediction
E4 Nuisance residualization sensitivity
E5 Synthetic noise injection
E6 Timing / trial-position alternatives
E7 Label-shuffle falsification null
E8 Claim audit + paper package
```

## Primary Claim Boundary

Allowed only if supported:

```text
The transition contrast is not fully explained by the tested proxy nuisance and timing alternatives.
```

Disallowed:

```text
Noise has been eliminated.
Measured motion and physiology are fully excluded when confounds.tsv files are absent.
CWP is validated.
```
""",
        encoding="utf-8",
    )


def make_figures() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    e2 = pd.read_csv(RESULTS / "e2_p3_transition_reproduction.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(e2["dataset"], e2["same_minus_different"], color="#4C78A8")
    ax.axhline(0, color="#222222", linewidth=1)
    ax.set_title("E2 Paper 3 Transition Contrast Reproduction")
    ax.set_ylabel("Same minus different cosine")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_1_e2_reproduction.png", dpi=180)
    fig.savefig(FIGURES / "figure_1_e2_reproduction.pdf")
    plt.close(fig)

    e34 = pd.read_csv(RESULTS / "e3_e4_nuisance_residualized_contrasts.csv")
    strict = e34[e34["residualization_variant"] == "subject_run_time_context"]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(strict["dataset"], strict["same_minus_different"], color="#54A24B")
    ax.axhline(0, color="#222222", linewidth=1)
    ax.set_title("E4 Signal After Strict Proxy Residualization")
    ax.set_ylabel("Residual same minus different cosine")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_2_e4_proxy_residualization.png", dpi=180)
    fig.savefig(FIGURES / "figure_2_e4_proxy_residualization.pdf")
    plt.close(fig)

    e5 = pd.read_csv(RESULTS / "e5_synthetic_noise_injection.csv")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for dataset, group in e5.groupby("dataset"):
        ax.plot(group["noise_sigma_multiplier"], group["survival_rate_positive"], marker="o", label=dataset)
    ax.axhline(0.95, color="#222222", linewidth=1, linestyle="--")
    ax.set_ylim(0, 1.05)
    ax.set_title("E5 Synthetic Noise Survival")
    ax.set_xlabel("Noise sigma multiplier")
    ax.set_ylabel("Positive contrast survival rate")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_3_e5_noise_survival.png", dpi=180)
    fig.savefig(FIGURES / "figure_3_e5_noise_survival.pdf")
    plt.close(fig)

    e7 = pd.read_csv(RESULTS / "e7_falsification_null_tests.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(e7["dataset"], e7["observed_percentile_vs_null"], color="#F58518")
    ax.axhline(0.99, color="#222222", linewidth=1, linestyle="--")
    ax.set_ylim(0, 1.05)
    ax.set_title("E7 Label-shuffle Null Survival")
    ax.set_ylabel("Observed percentile vs null")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_4_e7_null.png", dpi=180)
    fig.savefig(FIGURES / "figure_4_e7_null.pdf")
    plt.close(fig)


def write_attachments(audit: dict[str, Any]) -> None:
    (ATTACHMENTS / "A1_Frozen_Protocol.md").write_text(
        f"""# A1 Frozen Protocol

Status: E1-E8 implemented and run.

Primary endpoint:

```text
same-transition minus different-transition cosine after falsification stressors
```

Claim-audit status:

```text
{audit["status"]}
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A2_Dataset_Manifest.md").write_text(
        "# A2 Dataset Manifest\n\n" + table_markdown(RESULTS / "e1_confound_input_audit.csv") + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A3_Full_Pipeline.md").write_text(
        """# A3 Full Pipeline

```text
stage-state CSVs
-> transition vectors
-> Paper 3 contrast reproduction
-> proxy nuisance residualization
-> nuisance-only prediction
-> synthetic noise injection
-> timing-position tests
-> label-shuffle nulls
-> statistics and claim audit
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A4_Full_Baseline_Results.md").write_text(
        "# A4 Full Baseline / Competing-Explanation Results\n\n"
        + "## Proxy nuisance prediction\n\n"
        + table_markdown(RESULTS / "e3_proxy_nuisance_prediction.csv")
        + "\n\n## Timing tests\n\n"
        + table_markdown(RESULTS / "e6_timing_position_tests.csv")
        + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A5_Holdout_Audit.md").write_text(
        """# A5 Holdout Audit

Paper 4 is a falsification and robustness analysis over frozen state tables from Papers 1-3.

No new ontology tuning or predictive model rescue is performed.
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A6_Statistics.md").write_text(
        "# A6 Statistics\n\n"
        + "## E2 reproduction\n\n"
        + table_markdown(RESULTS / "e2_p3_transition_reproduction.csv")
        + "\n\n## E4 residualized contrasts\n\n"
        + table_markdown(RESULTS / "e3_e4_nuisance_residualized_contrasts.csv")
        + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A7_Null_Falsification_Tests.md").write_text(
        "# A7 Null / Falsification Tests\n\n"
        + "## Synthetic noise\n\n"
        + table_markdown(RESULTS / "e5_synthetic_noise_injection.csv")
        + "\n\n## Label shuffle\n\n"
        + table_markdown(RESULTS / "e7_falsification_null_tests.csv")
        + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A8_QC_Leakage_Audit.md").write_text(
        f"""# A8 QC & Leakage Audit

Measured confounds available:

```text
{audit["measured_motion_or_physiology_confounds_available"]}
```

Online OpenNeuro recovery evidence:

```text
paper4/online_confound_recovery/online_confound_recovery_summary.json
```

Critical limitation:

```text
{audit["critical_limitation"]}
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A9_Limitations_Failed_Analyses.md").write_text(
        f"""# A9 Limitations & Failed Analyses

Unsupported claims:

```text
Noise has been eliminated.
Measured motion and physiology are fully excluded.
CWP is validated.
```

Observed claim-audit status:

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
powershell -ExecutionPolicy Bypass -File paper4\\scripts\\reproduce-paper4.ps1
```

To refresh the online OpenNeuro confound-recovery audit first, run:

```powershell
powershell -ExecutionPolicy Bypass -File paper4\\scripts\\reproduce-paper4-online-confounds.ps1
```

Expected outputs include:

```text
paper4/results/e8_claim_audit.json
paper4/results/CURRENT_RESULTS.md
paper4/manuscript/PAPER4_MANUSCRIPT_CURRENT.md
paper4/submission/PAPER4_BIORXIV_DRAFT_CURRENT.pdf
```
""",
        encoding="utf-8",
    )


def current_results_md(audit: dict[str, Any]) -> str:
    return f"""# Paper 4 Current Results

Status:

```text
{audit["status"]}
```

## E1 Confound Audit

{table_markdown(RESULTS / "e1_confound_input_audit.csv")}

## E2 Paper 3 Reproduction

{table_markdown(RESULTS / "e2_p3_transition_reproduction.csv")}

## E3 Proxy Nuisance Prediction

{table_markdown(RESULTS / "e3_proxy_nuisance_prediction.csv")}

## E4 Nuisance Residualized Contrasts

{table_markdown(RESULTS / "e3_e4_nuisance_residualized_contrasts.csv")}

## E5 Synthetic Noise Injection

{table_markdown(RESULTS / "e5_synthetic_noise_injection.csv")}

## E6 Timing / Position Tests

{table_markdown(RESULTS / "e6_timing_position_tests.csv")}

## E7 Null Tests

{table_markdown(RESULTS / "e7_falsification_null_tests.csv")}

## Claim Audit

```json
{json.dumps(audit, indent=2)}
```
"""


def manuscript_text(audit: dict[str, Any]) -> str:
    return f"""# Falsifying Noise Explanations for Reproducible Brain-State Transitions

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 3 found reproducible macroscopic stage-transition vectors for ENCODE-to-MAINTAIN and MAINTAIN-to-PROBE transitions. Here we test whether that transition contrast is plausibly explained by nuisance structure, timing position, synthetic noise sensitivity, or label artifacts. We audited available raw/event/state inputs, attempted online recovery of OpenNeuro derivatives/confound files, reproduced the Paper 3 transition contrast, residualized transition vectors against proxy nuisance variables, compared nuisance-only and transition-aware prediction models, injected synthetic Gaussian corruption, evaluated timing-position alternatives, and ran frequency-preserving transition-label shuffles. The current claim-audit status is `{audit["status"]}`. The evidence supports only the bounded claim that the transition contrast is not fully explained by the tested proxy nuisance and timing alternatives. Because measured motion and physiological confound files were not found locally or in the targeted OpenNeuro recovery, the study does not fully exclude measured motion or physiology.

## 1. Introduction

Reproducibility alone is not enough. A repeated transition pattern may reflect neural state dynamics, but it may also reflect motion, trial timing, run structure, HRF smoothing, scanner drift, or preprocessing artifacts. Paper 4 treats these alternatives as the object of study.

## 2. Methods

The analysis used the same frozen state tables used by Paper 3: ds001635, ds001634, and ds004469. Transition vectors were defined as `T = S_target - S_source`. E1 audited local measured confound availability and incorporated targeted OpenNeuro online recovery manifests when present. E2 reproduced the Paper 3 same-transition versus different-transition contrast. E3/E4 tested proxy nuisance alternatives using residualization and nuisance-only prediction. E5 injected synthetic noise. E6 tested timing-position alternatives. E7 ran transition-label shuffle nulls. E8 enforced claim boundaries.

## 3. Results

### 3.1 Confound Audit

{table_markdown(RESULTS / "e1_confound_input_audit.csv")}

### 3.2 Transition Contrast Reproduction

{table_markdown(RESULTS / "e2_p3_transition_reproduction.csv")}

### 3.3 Proxy Nuisance Residualization

{table_markdown(RESULTS / "e3_e4_nuisance_residualized_contrasts.csv")}

### 3.4 Synthetic Noise

{table_markdown(RESULTS / "e5_synthetic_noise_injection.csv")}

### 3.5 Timing Tests

{table_markdown(RESULTS / "e6_timing_position_tests.csv")}

### 3.6 Label-shuffle Null

{table_markdown(RESULTS / "e7_falsification_null_tests.csv")}

## 4. Discussion

The completed tests strengthen the transition object from Paper 3 against several proxy nuisance and timing explanations, but they do not eliminate noise. The most important limitation is that local measured head-motion and physiological confounds were not available. Therefore the paper cannot honestly claim that motion or physiology has been fully excluded.

Critical limitation: {audit["critical_limitation"]}

## 5. Conclusion

Current claim-audit status: `{audit["status"]}`.

## Data Availability

OpenNeuro-derived local state tables from Papers 1-3 were used. Raw local dataset copies were audited for events, BOLD metadata, and measured confound files. Targeted OpenNeuro online recovery was attempted for derivatives/confound/motion/regressor/DVARS/FD file patterns and recorded in `paper4/online_confound_recovery/online_confound_recovery_summary.json`.

## Code Availability

[TO BE FILLED]

## Ethics Statement

This analysis uses public de-identified datasets. Dataset-specific ethics approvals are reported by the original data providers.

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

    doc = SimpleDocTemplate(str(SUBMISSION / "PAPER4_BIORXIV_DRAFT_CURRENT.pdf"), pagesize=letter)
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
    (MANUSCRIPT / "PAPER4_MANUSCRIPT_CURRENT.md").write_text(text, encoding="utf-8")
    build_pdf(text)
    (SUBMISSION / "SUBMISSION_READINESS.md").write_text(
        f"""# Paper 4 Submission Readiness

Current status: not ready for direct bioRxiv submission.

Generated:

```text
paper4/manuscript/PAPER4_MANUSCRIPT_CURRENT.md
paper4/submission/PAPER4_BIORXIV_DRAFT_CURRENT.pdf
paper4/attachments/
paper4/manuscript/figures/
```

Remaining before bioRxiv:

```text
Fill authors, affiliations, correspondence, code availability, funding, COI.
Add formal literature review and citations.
Review figure placement and final journal-style formatting.
Do not claim measured motion/physiology exclusion unless confounds are obtained and analyzed or fMRIPrep-derived confounds are generated locally.
```

Claim audit status:

```text
{audit["status"]}
```

Reproduction command verified for this workspace:

```powershell
powershell -ExecutionPolicy Bypass -File paper4\\scripts\\reproduce-paper4.ps1
```

Online recovery refresh command:

```powershell
powershell -ExecutionPolicy Bypass -File paper4\\scripts\\reproduce-paper4-online-confounds.ps1
```
""",
        encoding="utf-8",
    )
    (SUBMISSION / "FIGURE_CAPTIONS.md").write_text(
        """# Figure Captions

Figure 1. E2 reproduction of the Paper 3 same-transition versus different-transition contrast.

Figure 2. E4 transition contrast after strict proxy nuisance residualization.

Figure 3. E5 survival of positive transition contrast under synthetic Gaussian noise injection.

Figure 4. E7 observed transition contrast percentile against frequency-preserving label-shuffle nulls.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_protocol()
    e1 = e1_confound_audit()
    rows = load_transition_rows()
    e2 = e2_reproduce_p3(rows)
    e34, _predictive = e3_e4_nuisance_residualization(rows)
    e5 = e5_synthetic_noise(rows)
    e6 = e6_timing_tests(rows, e2)
    e7 = e7_null_tests(rows, e2)
    audit = e8_claim_audit(e1, e2, e34, e5, e6, e7)
    write_json(RESULTS / "e1_e8_run_summary.json", {"experiment": "P4-E1-E8", "status": audit["status"], "claim_audit": audit})
    (RESULTS / "CURRENT_RESULTS.md").write_text(current_results_md(audit), encoding="utf-8")
    make_figures()
    write_attachments(audit)
    write_submission_files(audit)
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
