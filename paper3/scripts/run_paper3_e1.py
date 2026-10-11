from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PAPER1 = WORKSPACE / "paper1"
sys.path.insert(0, str(PAPER1 / "scripts"))

from common import build_transitions, load_stage_states  # noqa: E402


RESULTS = ROOT / "results"
ATTACHMENTS = ROOT / "attachments"

DATASETS = {
    "ds001635": WORKSPACE / "paper1" / "state_extraction" / "stage_states.csv",
    "ds001634": WORKSPACE / "paper1" / "external_validation" / "stage_states_external.csv",
    "ds004469": WORKSPACE / "paper2" / "external_holdout" / "stage_states_dataset_c.csv",
}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def audit_dataset(dataset: str, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    if not path.exists():
        return (
            {
                "dataset": dataset,
                "state_file": str(path),
                "status": "MISSING",
                "blocker": "state file not found",
            },
            [],
            [],
        )

    rows, roi_cols = load_stage_states(str(path))
    transitions, _, _ = build_transitions(rows, roi_cols)

    subjects = sorted({r.get("subject", "NA") for r in rows})
    subject_runs = sorted({(r.get("subject", "NA"), r.get("run", "NA")) for r in rows})
    stage_counts = Counter(r.get("cwp", "NA") for r in rows)
    transition_counts = Counter(f"{m.get('source_cwp', 'NA')}_TO_{m.get('target_cwp', 'NA')}" for m in transitions)
    run_counts = Counter(r.get("run", "NA") for r in rows)

    by_subject: dict[str, Counter[str]] = defaultdict(Counter)
    by_subject_run: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        subject = row.get("subject", "NA")
        run = row.get("run", "NA")
        cwp = row.get("cwp", "NA")
        by_subject[subject][cwp] += 1
        by_subject_run[(subject, run)][cwp] += 1

    subject_rows = []
    for subject, counts in sorted(by_subject.items()):
        subject_rows.append(
            {
                "dataset": dataset,
                "subject": subject,
                "n_states": sum(counts.values()),
                "encode_states": counts.get("ENCODE", 0),
                "maintain_states": counts.get("MAINTAIN", 0),
                "probe_states": counts.get("PROBE", 0),
            }
        )

    run_rows = []
    for (subject, run), counts in sorted(by_subject_run.items()):
        run_rows.append(
            {
                "dataset": dataset,
                "subject": subject,
                "run": run,
                "n_states": sum(counts.values()),
                "encode_states": counts.get("ENCODE", 0),
                "maintain_states": counts.get("MAINTAIN", 0),
                "probe_states": counts.get("PROBE", 0),
            }
        )

    missing_stage_subjects = [
        subject
        for subject, counts in by_subject.items()
        if not all(counts.get(stage, 0) > 0 for stage in ["ENCODE", "MAINTAIN", "PROBE"])
    ]
    has_repeated_runs = any(count > 1 for count in Counter(subject for subject, _ in subject_runs).values())

    summary = {
        "dataset": dataset,
        "state_file": str(path.relative_to(WORKSPACE)),
        "status": "AUDITED",
        "n_states": len(rows),
        "n_transitions": len(transitions),
        "n_subjects": len(subjects),
        "n_subject_runs": len(subject_runs),
        "n_roi_features": len(roi_cols),
        "stage_counts": dict(sorted(stage_counts.items())),
        "transition_counts": dict(sorted(transition_counts.items())),
        "run_counts": dict(sorted(run_counts.items())),
        "has_repeated_runs_for_cross_run_reliability": has_repeated_runs,
        "subjects_missing_any_primary_stage": len(missing_stage_subjects),
        "primary_stage_completeness": len(missing_stage_subjects) == 0,
    }
    return summary, subject_rows, run_rows


def update_attachments(payload: dict[str, Any]) -> None:
    ATTACHMENTS.mkdir(parents=True, exist_ok=True)
    (ATTACHMENTS / "A1_Frozen_Protocol.md").write_text(
        f"""# A1 Frozen Protocol

Status: E1 input/state audit implemented and run.

Paper 3 starts with E1, which is the input/state audit formerly described as E0.

Primary endpoint for E1:

```text
state-file readiness for reproducibility analysis
```

Primary inputs:

```text
paper1/state_extraction/stage_states.csv
paper1/external_validation/stage_states_external.csv
paper2/external_holdout/stage_states_dataset_c.csv
```

Current E1 status:

```text
{payload["status"]}
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A2_Dataset_Manifest.md").write_text(
        """# A2 Dataset Manifest

Status: generated from E1 input/state audit.

See:

```text
paper3/results/e1_dataset_audit_summary.csv
paper3/results/e1_subject_stage_counts.csv
paper3/results/e1_subject_run_stage_counts.csv
paper3/results/e1_input_audit.json
```
""",
        encoding="utf-8",
    )


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    subject_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []

    for dataset, path in DATASETS.items():
        summary, subjects, runs = audit_dataset(dataset, path)
        summaries.append(summary)
        subject_rows.extend(subjects)
        run_rows.extend(runs)

    blockers = [
        f"{row['dataset']}: {row.get('blocker', 'unknown blocker')}"
        for row in summaries
        if row.get("status") != "AUDITED"
    ]
    warnings = []
    for row in summaries:
        if row.get("status") != "AUDITED":
            continue
        if not row.get("primary_stage_completeness"):
            warnings.append(f"{row['dataset']}: one or more subjects missing ENCODE/MAINTAIN/PROBE")
        if not row.get("has_repeated_runs_for_cross_run_reliability"):
            warnings.append(f"{row['dataset']}: no repeated run labels available for cross-run reliability")

    status = "PASS_READY_FOR_E2_RELIABILITY" if not blockers else "BLOCKED_INPUTS_MISSING"
    payload = {
        "experiment": "P3-E1",
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "datasets": summaries,
        "summary_csv": "paper3/results/e1_dataset_audit_summary.csv",
        "subject_counts_csv": "paper3/results/e1_subject_stage_counts.csv",
        "subject_run_counts_csv": "paper3/results/e1_subject_run_stage_counts.csv",
        "next_experiment": "P3-E2 transition reproducibility",
        "claim_boundary": "E1 is an input/state audit only; it does not test reproducibility or validate CWP.",
    }

    write_csv(RESULTS / "e1_dataset_audit_summary.csv", summaries)
    write_csv(RESULTS / "e1_subject_stage_counts.csv", subject_rows)
    write_csv(RESULTS / "e1_subject_run_stage_counts.csv", run_rows)
    (RESULTS / "e1_input_audit.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    update_attachments(payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
