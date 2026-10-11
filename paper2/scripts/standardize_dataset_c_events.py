from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
DATASET = ROOT / "external_holdout" / "ds004469_final_input"
OUT_DIR = ROOT / "external_holdout" / "ds004469_standardized_events"

STAGE_MAP = {
    "Coding": "ENCODE",
    "Retention": "MAINTAIN",
    "Test": "PROBE",
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    event_paths = sorted(DATASET.glob("sub-*/func/*_task-sternberg_events.tsv"))
    if not event_paths:
        raise SystemExit(f"no Dataset C events found under {DATASET}")

    inventory: list[dict[str, object]] = []
    total_rows = 0
    skipped_rows = 0
    for src in event_paths:
        subject = src.parts[-3]
        dest_dir = OUT_DIR / subject / "func"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        df = pd.read_csv(src, sep="\t")
        if not {"onset", "duration", "trial_type"}.issubset(df.columns):
            missing = sorted({"onset", "duration", "trial_type"}.difference(df.columns))
            raise SystemExit(f"{src} missing required columns: {missing}")
        out_rows = []
        trial_id = 0
        for row in df.to_dict(orient="records"):
            trial_type = str(row["trial_type"])
            cwp = STAGE_MAP.get(trial_type)
            if not cwp:
                skipped_rows += 1
                continue
            if cwp == "ENCODE":
                trial_id += 1
            row["processing_stage"] = cwp
            row["domain"] = "NUMBER"
            row["load_type"] = "UNKNOWN"
            row["context"] = "STERNBERG_DIGIT"
            row["trial_id"] = str(trial_id)
            out_rows.append(row)
        total_rows += len(out_rows)
        pd.DataFrame(out_rows).to_csv(dest, sep="\t", index=False)
        inventory.append(
            {
                "subject": subject,
                "source_events": str(src.relative_to(WORKSPACE)),
                "standardized_events": str(dest.relative_to(WORKSPACE)),
                "rows_written": len(out_rows),
                "trial_count": trial_id,
            }
        )

    with (ROOT / "external_holdout" / "dataset_c_standardized_event_inventory.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "subject",
                "source_events",
                "standardized_events",
                "rows_written",
                "trial_count",
            ],
        )
        writer.writeheader()
        writer.writerows(inventory)

    summary = {
        "dataset_id": "ds004469",
        "version": "1.1.3",
        "source_events_files": len(event_paths),
        "standardized_events_files": len(inventory),
        "rows_written": total_rows,
        "skipped_rows": skipped_rows,
        "stage_map": STAGE_MAP,
        "domain_policy": "All task-sternberg trials are assigned NUMBER because the audited task uses digit lists and Paper 1/2 use NUMBER as the numeric-domain label.",
        "load_policy": "Load is marked UNKNOWN because local events do not encode per-trial memory set size.",
        "context_policy": "All rows use STERNBERG_DIGIT context.",
        "final_performance_inspected": False,
    }
    (ROOT / "external_holdout" / "dataset_c_standardized_event_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
