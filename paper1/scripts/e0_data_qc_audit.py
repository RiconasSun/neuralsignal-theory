from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict
from typing import Dict, List

from common import expand_glob, infer_cwp, infer_domain, infer_load, parse_subject_run, read_table, root_path, write_json, write_table


def manifest_row(kind: str, pattern: str, paths: List[str]) -> Dict[str, object]:
    return {
        "kind": kind,
        "pattern": pattern,
        "n_files": len(paths),
        "status": "FOUND" if paths else "MISSING",
        "example_path": os.path.abspath(paths[0]) if paths else "",
    }


def event_inventory(event_paths: List[str]) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    trial_counts = []
    subject_runs: Dict[str, set[str]] = defaultdict(set)
    required_fields = {"onset", "duration", "trial_type", "load_type", "processing_stage"}
    for path in event_paths:
        rows = read_table(path)
        subject, run = parse_subject_run(path, rows[0] if rows else None)
        subject_runs[subject].add(run)
        fields = set(rows[0].keys()) if rows else set()
        missing = sorted(required_fields - fields)
        cwp_counts = Counter(infer_cwp(r) for r in rows)
        domain_counts = Counter(infer_domain(r) for r in rows)
        load_counts = Counter(infer_load(r) for r in rows)
        trial_counts.append(
            {
                "subject": subject,
                "run": run,
                "events_path": os.path.abspath(path),
                "n_event_rows": len(rows),
                "missing_required_fields": ";".join(missing),
                "cwp_counts": dict(cwp_counts),
                "domain_counts": dict(domain_counts),
                "load_counts": dict(load_counts),
                "status": "PASS" if rows and not missing else "FAIL",
            }
        )
    qc_subjects = []
    for subject in sorted(subject_runs):
        runs = sorted(subject_runs[subject])
        qc_subjects.append(
            {
                "subject": subject,
                "n_runs_with_events": len(runs),
                "runs": ";".join(runs),
                "three_runs_present": str(len(runs) == 3),
                "status": "PASS" if len(runs) == 3 else "WARN",
            }
        )
    return trial_counts, qc_subjects


def main() -> None:
    parser = argparse.ArgumentParser(description="E0: audit local Paper 1 dataset inputs and write manifest/QC files.")
    parser.add_argument("--events-glob", default=root_path("data_manifest", "**", "*events.tsv"))
    parser.add_argument("--timeseries-glob", default=root_path("state_extraction", "input_timeseries", "**", "*.csv"))
    parser.add_argument("--bold-glob", default=root_path("preprocessing", "**", "*bold*.nii*"))
    parser.add_argument("--confounds-glob", default=root_path("preprocessing", "**", "*confounds*.tsv"))
    parser.add_argument("--external-states", default=root_path("external_validation", "stage_states_external.csv"))
    args = parser.parse_args()

    event_paths = expand_glob(args.events_glob)
    timeseries_paths = expand_glob(args.timeseries_glob)
    bold_paths = expand_glob(args.bold_glob)
    confounds_paths = expand_glob(args.confounds_glob)
    external_paths = [args.external_states] if os.path.isfile(args.external_states) else []

    manifest = [
        manifest_row("events", args.events_glob, event_paths),
        manifest_row("roi_timeseries", args.timeseries_glob, timeseries_paths),
        manifest_row("bold", args.bold_glob, bold_paths),
        manifest_row("confounds", args.confounds_glob, confounds_paths),
        manifest_row("external_stage_states", args.external_states, external_paths),
    ]
    write_table(root_path("data_manifest", "dataset_manifest.csv"), manifest)

    trial_counts, qc_subjects = event_inventory(event_paths)
    if not trial_counts:
        trial_counts = [
            {
                "subject": "",
                "run": "",
                "events_path": "",
                "n_event_rows": 0,
                "missing_required_fields": "events.tsv not found",
                "cwp_counts": "{}",
                "domain_counts": "{}",
                "load_counts": "{}",
                "status": "FAIL",
            }
        ]
    if not qc_subjects:
        qc_subjects = [
            {
                "subject": "",
                "n_runs_with_events": 0,
                "runs": "",
                "three_runs_present": "False",
                "status": "FAIL",
            }
        ]
    write_table(root_path("data_manifest", "trial_counts.csv"), trial_counts)
    write_table(root_path("data_manifest", "qc_subjects.csv"), qc_subjects)

    blockers = []
    if not event_paths:
        blockers.append("events.tsv missing")
    if not timeseries_paths and not bold_paths:
        blockers.append("ROI time-series or BOLD inputs missing")
    if not external_paths:
        blockers.append("external stage states missing for E7")
    write_json(
        root_path("data_manifest", "e0_summary.json"),
        {
            "experiment": "E0",
            "status": "PASS" if not blockers else "NEED_DATA",
            "n_events": len(event_paths),
            "n_roi_timeseries": len(timeseries_paths),
            "n_bold": len(bold_paths),
            "n_confounds": len(confounds_paths),
            "external_stage_states_present": bool(external_paths),
            "blockers": blockers,
        },
    )
    print(f"E0 status: {'PASS' if not blockers else 'NEED_DATA'}")


if __name__ == "__main__":
    main()
