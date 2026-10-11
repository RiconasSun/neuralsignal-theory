from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data_ds005795_smoke"
SUBJECT = "sub-01"
TASK = "learning"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def count_tsv(path: Path) -> tuple[list[str], int, list[list[str]]]:
    rows_preview: list[list[str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, [])
        count = 0
        for row in reader:
            if len(rows_preview) < 5:
                rows_preview.append(row)
            count += 1
    return header, count, rows_preview


def inspect_physio(path: Path, sidecar: dict) -> dict:
    columns = sidecar.get("Columns") if isinstance(sidecar.get("Columns"), list) else []
    sampling_frequency = sidecar.get("SamplingFrequency")
    start_time = sidecar.get("StartTime")
    n_rows = 0
    first_rows = []
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            values = line.rstrip("\n").split("\t")
            if n_rows < 5:
                first_rows.append(values)
            n_rows += 1
    duration_seconds = None
    if isinstance(sampling_frequency, (int, float)) and sampling_frequency > 0:
        duration_seconds = n_rows / sampling_frequency
    return {
        "path": str(path),
        "exists": path.exists(),
        "n_rows": n_rows,
        "columns_from_sidecar": columns,
        "n_columns_from_sidecar": len(columns),
        "sampling_frequency": sampling_frequency,
        "start_time": start_time,
        "duration_seconds": duration_seconds,
        "first_rows": first_rows,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    func = DATA / SUBJECT / "func"
    eeg = DATA / SUBJECT / "eeg"
    physio = func / f"{SUBJECT}_task-{TASK}_physio.tsv.gz"
    events = func / f"{SUBJECT}_task-{TASK}_events.tsv"
    bold_json = func / f"{SUBJECT}_task-{TASK}_bold.json"
    eeg_channels = eeg / f"{SUBJECT}_task-{TASK}_channels.tsv"
    physio_sidecar = read_json(DATA / "physio.json")
    bold_sidecar = read_json(bold_json)

    event_header, event_rows, event_preview = count_tsv(events)
    channel_header, channel_rows, channel_preview = count_tsv(eeg_channels)
    payload = {
        "paper": "Paper 8",
        "experiment": "P8-final-extension-ds005795-physio-parse-smoke",
        "status": "PASS_DS005795_PHYSIO_TIMING_PARSE_SMOKE",
        "subject": SUBJECT,
        "task": TASK,
        "physio": inspect_physio(physio, physio_sidecar),
        "events": {
            "path": str(events),
            "header": event_header,
            "n_rows": event_rows,
            "preview": event_preview,
        },
        "eeg_channels": {
            "path": str(eeg_channels),
            "header": channel_header,
            "n_rows": channel_rows,
            "preview": channel_preview,
        },
        "bold_repetition_time": bold_sidecar.get("RepetitionTime"),
        "bold_task_name": bold_sidecar.get("TaskName"),
        "claim_boundary": "This only parses one ds005795 smoke subject's physiology/event metadata. It does not run nuisance regression or transition testing.",
    }
    if not payload["physio"]["columns_from_sidecar"]:
        payload["status"] = "PARTIAL_DS005795_PHYSIO_SIDE_CAR_COLUMNS_MISSING"
    (RESULTS / "p8_final_extension_ds005795_physio_parse_smoke.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["status"].startswith("PASS"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
