from __future__ import annotations

import argparse
import os
from typing import Dict, List

from common import bootstrap_ci, fdr_bh, mean, read_table, root_path, sign_flip_p, subject_metric_differences, write_json, write_table


def load_if_exists(path: str) -> List[Dict[str, str]]:
    return read_table(path) if os.path.isfile(path) else []


def summarize_model_file(path: str, experiment: str) -> List[Dict[str, object]]:
    rows = load_if_exists(path)
    out = []
    by_model: Dict[str, List[float]] = {}
    for row in rows:
        model = row.get("model", "NA")
        by_model.setdefault(model, [])
        try:
            by_model[model].append(float(row["mse"]))
        except Exception:
            pass
    for model, values in by_model.items():
        out.append({"experiment": experiment, "model": model, "metric": "mse", "mean": mean(values), "n": len(values)})
    return out


def finite_float(value: object) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    return parsed if parsed == parsed else None


def gate_from_effect(
    rows: List[Dict[str, object]],
    experiment: str,
    baseline: str,
    comparison: str,
    require_ci_above_zero: bool,
) -> str:
    matches = [
        row
        for row in rows
        if row.get("experiment") == experiment
        and row.get("baseline_model") == baseline
        and row.get("comparison_model") == comparison
    ]
    if not matches:
        return "NOT_EVALUATED"
    mean_improvement = finite_float(matches[0].get("mean_improvement"))
    ci_low = finite_float(matches[0].get("bootstrap_ci_low"))
    if mean_improvement is None:
        return "NOT_EVALUATED"
    if require_ci_above_zero:
        if ci_low is not None and ci_low > 0:
            return "PASSED"
        if ci_low is not None and ci_low <= 0 and mean_improvement <= 0:
            return "FAILED"
        return "INCONCLUSIVE"
    return "PASSED" if mean_improvement > 0 else "FAILED"


def main() -> None:
    parser = argparse.ArgumentParser(description="E8: aggregate metrics, subject-level effects, bootstrap CI, sign-flip p, FDR, and claim audit.")
    parser.add_argument("--results-dir", default=root_path("results"))
    parser.add_argument("--external-dir", default=root_path("external_validation"))
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--permutations", type=int, default=10000)
    args = parser.parse_args()

    metric_files = {
        "E3": os.path.join(args.results_dir, "e3_m0_m4_metrics.csv"),
        "E4": os.path.join(args.results_dir, "e4_unseen_combination_metrics.csv"),
        "E5": os.path.join(args.results_dir, "e5_unseen_domain_metrics.csv"),
        "E7": os.path.join(args.external_dir, "e7_external_dataset_metrics.csv"),
    }
    primary_rows = []
    for exp, path in metric_files.items():
        primary_rows.extend(summarize_model_file(path, exp))
    write_table(os.path.join(args.results_dir, "primary_metrics.csv"), primary_rows)

    effects = []
    for exp, path in metric_files.items():
        rows = load_if_exists(path)
        if not rows:
            continue
        subject_field = "heldout_subject" if exp == "E3" else "heldout_cell" if exp == "E4" else "heldout_domain" if exp == "E5" else "external_subject"
        if exp == "E7":
            rows = [row for row in rows if row.get("external_subject") != "ALL_EXTERNAL"]
        for baseline, comparison in [("M2_strong_task", "M4_task_plus_cwp"), ("M2_strong_task", "M3_cwp")]:
            diffs = subject_metric_differences(rows, baseline, comparison, metric="mse", subject_field=subject_field)
            for row in diffs:
                row["experiment"] = exp
                improvements = [float(d["improvement_for_error_metric"]) for d in diffs]
                row["mean_improvement"] = mean(improvements)
                row["bootstrap_ci_low"], row["bootstrap_ci_high"] = bootstrap_ci(improvements, args.bootstrap)
                row["sign_flip_p"] = sign_flip_p(improvements, args.permutations)
            effects.extend(diffs)

    p_values = [float(r["sign_flip_p"]) for r in effects if str(r.get("sign_flip_p", "")) not in {"", "nan"}]
    q_values = fdr_bh(p_values)
    qi = 0
    for row in effects:
        if str(row.get("sign_flip_p", "")) not in {"", "nan"}:
            row["fdr_q"] = q_values[qi]
            qi += 1
    write_table(os.path.join(args.results_dir, "subject_level_effects.csv"), effects)

    e6_summary_path = os.path.join(args.results_dir, "e6_null_falsification_summary.json")
    e6_exists = os.path.isfile(e6_summary_path)
    gate_a = gate_from_effect(effects, "E3", "M2_strong_task", "M4_task_plus_cwp", require_ci_above_zero=True)
    gate_b_e4 = gate_from_effect(effects, "E4", "M2_strong_task", "M3_cwp", require_ci_above_zero=False)
    gate_b_e5 = gate_from_effect(effects, "E5", "M2_strong_task", "M3_cwp", require_ci_above_zero=False)
    if gate_b_e4 == "PASSED" and gate_b_e5 == "PASSED":
        gate_b = "PASSED"
    elif "FAILED" in {gate_b_e4, gate_b_e5}:
        gate_b = "FAILED"
    elif gate_b_e4 == "NOT_EVALUATED" or gate_b_e5 == "NOT_EVALUATED":
        gate_b = "NOT_EVALUATED"
    else:
        gate_b = "INCONCLUSIVE"
    gate_c = gate_from_effect(effects, "E7", "M2_strong_task", "M3_cwp", require_ci_above_zero=False)
    blockers = []
    if not load_if_exists(metric_files["E3"]):
        blockers.append("E3 metrics missing")
    if not load_if_exists(metric_files["E4"]) or not load_if_exists(metric_files["E5"]):
        blockers.append("OOD metrics missing")
    if not e6_exists:
        blockers.append("E6 null summary missing")
    if not load_if_exists(metric_files["E7"]):
        blockers.append("E7 external validation metrics missing")

    claim_audit = {
        "experiment": "E8",
        "status": "completed_audit_not_claim_validated",
        "gate_a_incremental": gate_a,
        "gate_b_ood": gate_b,
        "gate_b_components": {"E4_unseen_combination": gate_b_e4, "E5_unseen_domain": gate_b_e5},
        "gate_c_external": gate_c,
        "claim_allowed_cwp_foundation_holds": gate_a == "PASSED" and gate_b == "PASSED" and gate_c == "PASSED" and e6_exists,
        "claim_allowed_cwp_clearly_outperforms_task_labels": gate_a == "PASSED" and gate_b == "PASSED" and gate_c == "PASSED" and e6_exists,
        "remaining_blockers": blockers,
        "no_invented_results": True,
        "outputs": {
            "primary_metrics": os.path.join(args.results_dir, "primary_metrics.csv"),
            "subject_level_effects": os.path.join(args.results_dir, "subject_level_effects.csv"),
        },
    }
    write_json(os.path.join(args.results_dir, "claim_audit.json"), claim_audit)
    print("E8 wrote primary_metrics.csv, subject_level_effects.csv, and claim_audit.json")


if __name__ == "__main__":
    main()
