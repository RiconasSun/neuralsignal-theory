from __future__ import annotations

import csv
import gzip
import json
import argparse
from pathlib import Path
from statistics import mean, pstdev


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
STATE = ROOT / "state_extraction" / "ds005795_physio_extension"
DATA = ROOT / "data_ds005795_smoke"
SUBJECT = "sub-01"
TASK = "learning"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_physio(path: Path) -> list[tuple[float, float, float]]:
    rows = []
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                try:
                    rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
                except ValueError:
                    continue
    return rows


def read_events(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def summarize(values: list[float]) -> tuple[float, float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0, 0.0
    return mean(values), pstdev(values) if len(values) > 1 else 0.0, min(values), max(values)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build TR-aligned ds005795 physiology features.")
    parser.add_argument("--subjects", nargs="+", default=[SUBJECT], help="BIDS subject IDs, e.g. sub-01 sub-02")
    parser.add_argument("--task", default=TASK)
    return parser.parse_args()


def build_subject(subject: str, task: str) -> dict:
    RESULTS.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    func = DATA / subject / "func"
    physio_path = func / f"{subject}_task-{task}_physio.tsv.gz"
    events_path = func / f"{subject}_task-{task}_events.tsv"
    bold_json = read_json(func / f"{subject}_task-{task}_bold.json")
    physio_sidecar = read_json(DATA / "physio.json")
    tr = float(bold_json.get("RepetitionTime", 2.0))
    physio = read_physio(physio_path)
    events = read_events(events_path)
    duration = physio[-1][0] - physio[0][0] if physio else 0.0
    n_tr = int(duration // tr)
    rows = []
    for idx in range(n_tr):
        start = idx * tr
        end = start + tr
        chunk = [row for row in physio if start <= row[0] < end]
        cardiac = [row[1] for row in chunk]
        resp = [row[2] for row in chunk]
        c_mean, c_sd, c_min, c_max = summarize(cardiac)
        r_mean, r_sd, r_min, r_max = summarize(resp)
        event_types = [
            row.get("trial_type", "")
            for row in events
            if row.get("onset") not in {"", "n/a"} and start <= float(row["onset"]) < end
        ]
        rows.append({
            "subject": subject,
            "task": task,
            "tr_index": idx,
            "time_start": start,
            "time_end": end,
            "n_physio_samples": len(chunk),
            "cardiac_mean": c_mean,
            "cardiac_sd": c_sd,
            "cardiac_min": c_min,
            "cardiac_max": c_max,
            "respiratory_mean": r_mean,
            "respiratory_sd": r_sd,
            "respiratory_min": r_min,
            "respiratory_max": r_max,
            "n_events": len(event_types),
            "event_types": "|".join(sorted(set(event_types))),
        })
    out_csv = STATE / f"p8_ds005795_{subject.replace('-', '')}_{task}_physio_tr_features.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    return {
        "subject": subject,
        "task": task,
        "repetition_time": tr,
        "n_physio_samples": len(physio),
        "n_event_rows": len(events),
        "n_tr_feature_rows": len(rows),
        "output_csv": str(out_csv),
        "status": "ready" if rows else "failed_no_rows",
    }


def main() -> None:
    args = parse_args()
    subject_results = [build_subject(subject, args.task) for subject in args.subjects]
    physio_sidecar = read_json(DATA / "physio.json")
    payload = {
        "paper": "Paper 8",
        "experiment": "P8-final-extension-ds005795-physio-feature-smoke",
        "status": "PASS_DS005795_TR_PHYSIO_FEATURES_BUILT" if all(row["status"] == "ready" for row in subject_results) else "FAILED_NO_PHYSIO_FEATURE_ROWS",
        "subjects": args.subjects,
        "task": args.task,
        "physio_columns": physio_sidecar.get("Columns"),
        "subject_results": subject_results,
        "claim_boundary": "This builds TR-aligned measured cardiac/respiratory nuisance features for smoke subjects. It does not establish physiology-robust transition dynamics.",
    }
    (RESULTS / "p8_final_extension_ds005795_physio_feature_smoke.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not all(row["status"] == "ready" for row in subject_results):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
