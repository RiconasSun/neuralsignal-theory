"""Registered saved-only A documentation; never fit, select, bootstrap or unlock.

CLI: python -B paper11_v2/scripts/r2_development_report.py register|verify|report
Parent registers before tests/report. Outputs live only in R2_development_report.
Documentation completeness is NOT scientific R2 PASS or regime validation.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime, timezone

import run_r2 as runner

OUT = runner.base.STUDY / "results/R2_development_report"
FILES = ("paper11_v2/scripts/r2_development_report.py",
         "paper11_v2/tests/test_r2_development_report.py")
ARTIFACTS = ("input_QC.json", "numerical_oracle.json", "tests.log",
             "baseline_selection.json", "model_selection_manifest.json",
             "selected_development_rows.json", "subject_statistics.json",
             "conditional_uncertainty.json")
PAIRS = [("discrete", "continuous"), ("discrete", "hybrid"),
         ("continuous", "hybrid"), ("discrete", "baseline"),
         ("continuous", "baseline"), ("hybrid", "baseline")]
FAILURE = "FAIL / DATA_INSUFFICIENT: external source support incomplete; spikes locked"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)


def config_key(config):
    return json.dumps(config, sort_keys=True, separators=(",", ":"))


def finite(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def close(left, right):
    if not finite(left) or not finite(right) or not math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-12):
        raise ValueError("Saved numerical identity mismatch")


def matched_means(left, right):
    if set(left) != set(right):
        raise ValueError("Patient identity mismatch")
    for subject in left:
        close(left[subject], right[subject])


def patient_means(rows, field="trial_scores"):
    """Descriptive equal-session/equal-patient arithmetic, no new inference."""
    grouped = {}
    for row in rows:
        value = row[field]
        score = sum(value) / len(value) if isinstance(value, list) else value
        grouped.setdefault(row["subject"], []).append(score)
    patients = {subject: sum(scores) / len(scores) for subject, scores in grouped.items()}
    return patients, sum(patients.values()) / len(patients)


def validate_records(rows, qc, configurations, sessions):
    """Exact Cartesian saved roster with matched feature/unit-bin/trial identity.

    Units are bound indirectly through feature SHA + independently checked QC.
    Stationary B0 has one exact seed=None; all other candidates have 11/23/37.
    Tests can pass small analytical rosters; production separately requires9/23/57.
    """
    qmap = {q["key"]: q for q in qc}
    if len(qmap) != len(qc) or set(qmap) != set(sessions):
        raise ValueError("QC/session roster mismatch")
    expected = {(session, config_key(c), seed) for session in sessions for c in configurations
                for seed in ([None] if c["family"] == "stationary" else runner.SEEDS)}
    indexed = {}
    for row in rows:
        key = (row["session"], config_key(row["config"]), row["seed"])
        if key not in expected or key in indexed:
            raise ValueError("Duplicate or unexpected mandatory fit")
        indexed[key] = row
        q = qmap[row["session"]]
        units, tids = q["unit_ids"], q["validation_ids"]
        if (row.get("converged") is not True or row.get("error") is not None
                or row.get("real_data") is not True):
            raise ValueError("Failed/nonexecuted mandatory seed")
        if (row["subject"] != q["subject"] or row["subject"] != row["session"].split("/")[0]
                or row["feature_sha256"] != q["feature_sha256"]
                or row["validation_trial_ids"] != tids
                or len(set(tids)) != len(tids) or len(set(units)) != len(units)
                or q["units"] != len(units) or not units or not tids
                or len(set(q["train_ids"])) != len(q["train_ids"])
                or set(q["train_ids"]) & set(tids)
                or q["train_trials"] != len(q["train_ids"])
                or q["validation_trials"] != len(tids)
                or row["training_unit_bins"] != len(q["train_ids"]) * 60 * len(units)
                or row["validation_unit_bins"] != len(tids) * 60 * len(units)):
            raise ValueError("Matched feature/unit-bin/trial identity mismatch")
        scores = row["trial_scores"]
        if len(scores) != len(tids) or not all(finite(v) for v in scores):
            raise ValueError("Invalid whole-trial scores")
        if not finite(row["loss"]) or not all(finite(v) for v in row["theta"]):
            raise ValueError("Invalid saved objective/parameters")
        close(sum(scores) / len(scores), row["validation_nats_per_unit_bin"])
        if (type(row["shared_parameters"]) is not int or row["shared_parameters"] < 0
                or row["extra_parameters"] != len(row["theta"])
                or row["total_parameters"] != row["extra_parameters"] + row["shared_parameters"]):
            raise ValueError("Nominal parameter identity mismatch")
    if set(indexed) != expected:
        raise ValueError("Missing mandatory candidate/seed")
    resolved = {}
    for c in configurations:
        resolved[config_key(c)] = []
        for session in sessions:
            seeds = [None] if c["family"] == "stationary" else runner.SEEDS
            candidates = [indexed[(session, config_key(c), seed)] for seed in seeds]
            # Verify the original training-objective seed rule, never dev-best.
            resolved[config_key(c)].append(min(enumerate(candidates), key=lambda p: (p[1]["loss"], p[0]))[1])
    return resolved


def snapshot_paths():
    paths = sorted((runner.OUT / "fits").rglob("*.json"))
    configs = runner.baseline_configs() + runner.family_configs()
    expected = len(runner.roster()) * sum(
        1 if c["family"] == "stationary" else len(runner.SEEDS) for c in configs)
    if len(paths) != expected:
        raise ValueError(f"Expected exactly{expected} primary fit files")
    return paths + [runner.OUT / name for name in ARTIFACTS]


def snapshot():
    return {runner.relative(p): digest(p) for p in snapshot_paths()}


def register():
    """Immutable prospective source/test registration and complete A snapshot."""
    runner.verify()
    if (OUT / "registration.json").exists():
        verify_snapshot()
        return
    hashes = snapshot()
    OUT.mkdir(parents=True, exist_ok=True)
    save_new(OUT / "registration.json", {
        "study": "P11-v2", "phase": "SAVED_ONLY_A_DOCUMENTATION",
        "registered_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {name: digest(runner.base.ROOT / name) for name in FILES},
        "r2_registration_sha256": digest(runner.OUT / "registration.json"),
        "snapshot_sha256": hashes, "scientific_outcome": FAILURE,
        "before_tests_and_report": True, "external_spikes_authorized": False})
    runner.verify()


def verify_snapshot():
    """Verify preceding immutable archives via frozen run_r2.verify, then snapshot."""
    runner.verify()
    reg = load(OUT / "registration.json")
    if (reg.get("phase") != "SAVED_ONLY_A_DOCUMENTATION"
            or reg.get("scientific_outcome") != FAILURE
            or reg.get("before_tests_and_report") is not True
            or reg.get("external_spikes_authorized") is not False):
        raise ValueError("Wrong documentation registration/policy")
    if reg["source_sha256"] != {name: digest(runner.base.ROOT / name) for name in FILES}:
        raise ValueError("Report source/test hashes changed")
    if digest(runner.OUT / "registration.json") != reg["r2_registration_sha256"]:
        raise ValueError("R2 registration changed")
    if snapshot() != reg["snapshot_sha256"]:
        raise ValueError("A snapshot changed")
    return reg


def checked_saved():
    reg = verify_snapshot()
    qc = load(runner.OUT / "input_QC.json")
    sessions = runner.roster()
    if len(qc) != 23 or len({q["subject"] for q in qc}) != 9:
        raise ValueError("Frozen9patient23session coverage required")
    for q in qc:
        feature = runner.data.COHORT / "features" / (q["key"].replace("/", "_") + ".json")
        if digest(feature) != q["feature_sha256"]:
            raise ValueError("Frozen feature changed")
        f = load(feature)  # R0 train/dev only; no original oldtest or external accessor.
        if (f["unit_ids"] != q["unit_ids"] or f["train_trial_ids"] != q["train_ids"]
                or f["validation_trial_ids"] != q["validation_ids"]):
            raise ValueError("QC/feature unit/trial identity mismatch")
    configs = runner.baseline_configs() + runner.family_configs()
    if len(configs) != 57:
        raise ValueError("Frozen57config grid mismatch")
    rows = [load(p) for p in sorted((runner.OUT / "fits").rglob("*.json"))]
    resolved = validate_records(rows, qc, configs, sessions)
    baseline = load(runner.OUT / "baseline_selection.json")
    manifest = load(runner.OUT / "model_selection_manifest.json")
    chosen = load(runner.OUT / "selected_development_rows.json")
    if set(chosen) != {"baseline", "discrete", "continuous", "hybrid"}:
        raise ValueError("Selected family roster mismatch")
    offset_config = baseline["combined_offset"]["selected_config"]
    if manifest["offset_config"] != offset_config or offset_config["family"] != "combined":
        raise ValueError("Shared offset selection mismatch")
    offsets = {r["session"]: r for r in resolved[config_key(offset_config)]}
    for row in rows:
        expected = offsets[row["session"]]["extra_parameters"] if row["config"]["family"] in ("discrete", "continuous", "hybrid") else 0
        if row["shared_parameters"] != expected:
            raise ValueError("Frozen shared offset nominal complexity mismatch")
    if manifest["external_spikes_accessed"] is not False or manifest["final_locked"] is not True:
        raise ValueError("Holdout/access policy mismatch")
    for family, selected in chosen.items():
        c = selected["selection"]["selected_config"]
        if c != manifest["families"][family]["selected_config"]:
            raise ValueError("Saved family selection mismatch")
        if family == "baseline" and c != baseline["strongest_baseline"]:
            raise ValueError("Strongest baseline mismatch")
        if selected["rows"] != resolved[config_key(c)]:
            raise ValueError("Selected saved rows/seed rule mismatch")
    selections = [(baseline["one_SE_baseline"], runner.baseline_configs()),
                  (baseline["combined_offset"], [c for c in configs if c["family"] == "combined"]),
                  (manifest["global_family_selection"], runner.family_configs())]
    selections += [(manifest["families"][f], [c for c in configs if c["family"] == f])
                   for f in ("discrete", "continuous", "hybrid")]
    for selection, grid in selections:
        frontier = selection["frontier"]
        if [r["config"] for r in frontier] != grid:
            raise ValueError("Saved selection frontier/configuration roster mismatch")
        if selection["selected_config"] != grid[selection["selected_index"]]:
            raise ValueError("Saved selected index/configuration mismatch")
        for item, c in zip(frontier, grid):
            close(item["mean"], patient_means(resolved[config_key(c)])[1])
            close(item["mean_complexity"], patient_means(resolved[config_key(c)], "total_parameters")[1])
    oracle = load(runner.OUT / "numerical_oracle.json")
    if (oracle["cases"] != 108 or not finite(oracle["gradient_error"])
            or not finite(oracle["score_error_nats_unit_bin"])):
        raise ValueError("Initial numerical oracle incomplete")
    tests = (runner.OUT / "tests.log").read_text(encoding="utf-8")
    if "Ran 34 tests" not in tests or not tests.rstrip().endswith("OK"):
        raise ValueError("Initial registered34test receipt not successful")
    statistics = load(runner.OUT / "subject_statistics.json")
    uncertainty = load(runner.OUT / "conditional_uncertainty.json")
    if [(c["left"], c["right"]) for c in statistics["comparisons"]] != PAIRS:
        raise ValueError("Six saved contrast roster mismatch")
    patients = {}
    for family, selected in chosen.items():
        patients[family], mean = patient_means(selected["rows"])
        matched_means(statistics["means"][family]["patient_means"], patients[family])
        close(mean, statistics["means"][family]["overall_mean"])
        intervals = uncertainty["sessions"][family]
        if len(intervals) != 23 or {r["session"] for r in intervals} != set(sessions):
            raise ValueError("Conditional session coverage mismatch")
        by_session = {r["session"]: r for r in selected["rows"]}
        for interval in intervals:
            row = by_session[interval["session"]]
            if interval["subject"] != row["subject"]:
                raise ValueError("Conditional patient identity mismatch")
            close(interval["mean"], row["validation_nats_per_unit_bin"])
            validate_interval(interval)
        if set(uncertainty["patients"][family]) != set(patients[family]):
            raise ValueError("Conditional patient coverage mismatch")
        for subject, interval in uncertainty["patients"][family].items():
            close(interval["mean"], patients[family][subject])
            validate_interval(interval)
    for contrast in statistics["comparisons"]:
        expected = {p: patients[contrast["left"]][p] - patients[contrast["right"]][p]
                    for p in patients["baseline"]}
        matched_means(expected, contrast["patient_differences"])
        if contrast["subject_count"] != 9:
            raise ValueError("Patient pairing mismatch")
        close(sum(expected.values()) / 9, contrast["mean"])
        validate_interval(contrast)
        if not 0 <= contrast["holm_p_value"] <= 1 or not 0 <= contrast["sign_flip"]["p_value"] <= 1:
            raise ValueError("Invalid saved six-contrast probabilities")
    return reg, configs, rows, resolved, chosen, statistics, uncertainty, patients


def validate_interval(row):
    if (row["replicates"] != 10000 or row["seed"] != 20261011
            or len(row["ci"]) != 2 or not all(finite(v) for v in row["ci"])
            or row["ci"][0] > row["ci"][1] or not finite(row["se"]) or row["se"] < 0):
        raise ValueError("Invalid saved CI identity")


def flatten(value, prefix=""):
    result = {}
    for key, item in value.items():
        name = prefix + key
        if isinstance(item, dict):
            result.update(flatten(item, name + "."))
        elif isinstance(item, list):
            result[name] = json.dumps(item, separators=(",", ":"))
        else:
            result[name] = item
    return result


def csv_new(path, rows):
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def report():
    reg, configs, rows, resolved, chosen, statistics, uncertainty, patients = checked_saved()
    destination = OUT / "report"
    destination.mkdir(exist_ok=False)
    frontier = []
    for c in configs:
        selected = resolved[config_key(c)]
        frontier.append({"family": c["family"], "ridge": c["ridge"], "size": c.get("size", ""),
                         "lags": c.get("lags", ""), "seed_rule": "training objective minimum; order11,23,37 tie-break" if c["family"] != "stationary" else "exact B0 seedNone",
                         "extra_parameters": patient_means(selected, "extra_parameters")[1],
                         "shared_offset_parameters": patient_means(selected, "shared_parameters")[1],
                         "total_nominal_parameters": patient_means(selected, "total_parameters")[1],
                         "patient_weighted_dev_mean": patient_means(selected)[1]})
    csv_new(destination / "all57configurations.csv", frontier)
    csv_new(destination / "six_subject_contrasts.csv", [flatten(c) for c in statistics["comparisons"]])
    csv_new(destination / "selected_patient_scores.csv", [dict(subject=p, **{f: patients[f][p] for f in patients}) for p in sorted(patients["baseline"])])
    csv_new(destination / "session_conditional_CIs.csv", [dict(family=f, **flatten(r)) for f, values in uncertainty["sessions"].items() for r in values])
    csv_new(destination / "patient_conditional_CIs.csv", [dict(family=f, subject=p, **flatten(r)) for f, values in uncertainty["patients"].items() for p, r in values.items()])
    csv_new(destination / "optimizer_diagnostics.csv", [{k: row.get(k) for k in ("session", "subject", "seed", "iterations", "gradient_norm", "design_rank", "message", "status")} | {"config": config_key(row["config"])} for row in rows])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    contrasts = [c for c in statistics["comparisons"] if c["right"] == "baseline"]
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, c in enumerate(contrasts):
        ax.plot(c["ci"], [i, i], color="black")
        ax.scatter([c["mean"]], [i], color="black")
    ax.set_yticks(range(3), [c["left"] for c in contrasts])
    ax.axvline(0, color="gray", linestyle="--", label="zero")
    ax.axvline(.01, color="red", linestyle=":", label="0.01 practical reference")
    ax.set_xlabel("Patient-primary gain vs strongest baseline (nats/unit-bin)")
    ax.set_title("Saved paired subject bootstrap CIs; postselection exploratory")
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination / "paired_gain_forest.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    for family in dict.fromkeys(r["family"] for r in frontier):
        subset = [r for r in frontier if r["family"] == family]
        ax.scatter([r["total_nominal_parameters"] for r in subset], [r["patient_weighted_dev_mean"] for r in subset], label=family)
    ax.set_xlabel("Patient-weighted total nominal parameters (including shared offset)")
    ax.set_ylabel("Patient-weighted dev nats/unit-bin")
    ax.set_title("All57 frozen configurations; no new selection")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(destination / "nominal_parameter_frontier.png", dpi=160)
    plt.close(fig)
    text = ("# Saved A Documentation\n\n" + FAILURE + "\n\n"
            f"A documentation gate PASS:{len(rows)}/{len(rows)} primary fits,57 configurations,9 patients/23 sessions. "
            "This is not R2 scientific PASS, null validation or physical regime validation. "
            "No incomplete B nulls are interpreted. No cohort pruning or unknown-support zero filling.\n\n"
            "Saved selection only; training-objective seed rule. Equal-session within patient, "
            "equal-patient population summaries. CIs/Holm-six copied without new inference; "
            "session/patient whole-trial intervals descriptive, not independent windows.\n\n"
            "design_rank is the recorded FIRST-unit design rank only, not a global rank. "
            "Optimizer success (including ftol termination or nit1) does not establish small "
            "gradient or global optimality; see full diagnostics.\n\n"
            "Reproduce saved-only: `python -B paper11_v2/scripts/r2_development_report.py verify` "
            "then `python -B paper11_v2/scripts/r2_development_report.py report` once after registration; "
            "existing report outputs are never overwritten.\n")
    (destination / "report.md").write_text(text, encoding="utf-8")
    verify_snapshot()
    save_new(destination / "manifest.json", {"documentation_gate": "PASS", "scientific_outcome": FAILURE,
             "registration_sha256": digest(OUT / "registration.json"),
             "source_sha256": reg["source_sha256"], "r2_registration_sha256": reg["r2_registration_sha256"],
             "snapshot_sha256": reg["snapshot_sha256"], "coverage": {"patients": 9, "sessions": 23, "fits": len(rows), "configurations": len(configs)},
             "external_spikes_authorized": False, "new_inference_executed": False,
             "outputs_sha256": {p.name: digest(p) for p in sorted(destination.iterdir())}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("register", "verify", "report"))
    command = parser.parse_args().command
    if command == "register":
        register()
    elif command == "verify":
        checked_saved()
        destination = OUT / "report"
        if destination.exists():
            manifest = load(destination / "manifest.json")
            actual = {p.name: digest(p) for p in destination.iterdir() if p.name != "manifest.json"}
            if actual != manifest["outputs_sha256"] or manifest["registration_sha256"] != digest(OUT / "registration.json"):
                raise ValueError("Saved report output identity mismatch")
    else:
        report()
    print("Saved-only " + command + " complete; scientific outcome remains " + FAILURE)


if __name__ == "__main__":
    main()
