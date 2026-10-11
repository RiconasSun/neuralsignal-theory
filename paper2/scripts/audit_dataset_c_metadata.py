from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "paper2" / "external_holdout" / "ds004469_metadata_only"
OUT_DIR = ROOT / "paper2" / "external_holdout"


def main() -> None:
    events_files = sorted(DATASET.glob("sub-*/func/*_task-sternberg_events.tsv"))
    bold_json_files = sorted(DATASET.glob("sub-*/func/*_bold.json"))
    sternberg_bold_json_files = sorted(DATASET.glob("sub-*/func/*_task-sternberg_bold.json"))
    participants_path = DATASET / "participants.tsv"
    description_path = DATASET / "dataset_description.json"

    participants = pd.read_csv(participants_path, sep="\t")
    description = json.loads(description_path.read_text(encoding="utf-8"))

    rows: list[dict[str, object]] = []
    type_counter: Counter[str] = Counter()
    duration_by_type: dict[str, Counter[float]] = {}
    subject_counter: Counter[str] = Counter()

    for path in events_files:
        df = pd.read_csv(path, sep="\t")
        subject = path.parts[-3]
        required_columns = {"onset", "duration", "trial_type"}
        missing = sorted(required_columns.difference(df.columns))
        if missing:
            raise RuntimeError(f"{path} missing required columns: {missing}")
        subject_counter[subject] += 1
        for trial_type, count in df["trial_type"].astype(str).value_counts().items():
            type_counter[trial_type] += int(count)
        for trial_type, group in df.groupby("trial_type"):
            counter = duration_by_type.setdefault(str(trial_type), Counter())
            for value in group["duration"].astype(float):
                counter[float(value)] += 1
        rows.append(
            {
                "subject": subject,
                "events_file": str(path.relative_to(ROOT)),
                "n_events": int(len(df)),
                "trial_types": "|".join(sorted(df["trial_type"].astype(str).unique())),
                "first_onset": float(df["onset"].min()),
                "last_onset": float(df["onset"].max()),
            }
        )

    stage_map = {
        "Coding": "ENCODE",
        "Retention": "MAINTAIN",
        "Test": "PROBE",
    }
    observed_types = set(type_counter)
    required_types = set(stage_map)

    audit = {
        "dataset_id": "ds004469",
        "version": "1.1.3",
        "dataset_doi": description.get("DatasetDOI"),
        "name": description.get("Name"),
        "license": description.get("License"),
        "metadata_only_download": True,
        "participants_tsv_rows": int(len(participants)),
        "participants_total_unique": int(participants["participant_id"].nunique()),
        "task_fmri_vw_included_subjects": int(
            pd.to_numeric(participants.get("task_fmri_vw"), errors="coerce").fillna(0).sum()
        )
        if "task_fmri_vw" in participants
        else None,
        "events_files": len(events_files),
        "bold_json_files": len(bold_json_files),
        "sternberg_bold_json_files": len(sternberg_bold_json_files),
        "event_columns_required": ["onset", "duration", "trial_type"],
        "observed_trial_types": dict(sorted(type_counter.items())),
        "duration_by_trial_type": {
            key: {str(duration): count for duration, count in sorted(counter.items())}
            for key, counter in sorted(duration_by_type.items())
        },
        "frozen_stage_mapping": stage_map,
        "dataset_c_lock_recommendation": observed_types == required_types,
        "lock_rationale": (
            "Events expose Coding, Retention, and Test phases that map directly to "
            "ENCODE, MAINTAIN, and PROBE. This dataset can test stage-level CWP transfer "
            "but cannot test TRANSFORM because no manipulation phase is encoded."
        ),
        "final_performance_inspected": False,
        "bold_nii_downloaded_for_final_evaluation": False,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "dataset_c_metadata_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with (OUT_DIR / "dataset_c_event_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "subject",
                "events_file",
                "n_events",
                "trial_types",
                "first_onset",
                "last_onset",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
