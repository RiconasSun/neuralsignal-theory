from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATASET = "ds004117"
OWNER = "OpenNeuroDatasets"
REPO = "ds004117"
BRANCH = "main"


def fetch_json(url: str, timeout: int) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "NSI-Paper6-TransitionWindows/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "NSI-Paper6-TransitionWindows/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def raw_url(path: str) -> str:
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{urllib.parse.quote(path)}"


def parse_events(text: str) -> list[dict]:
    rows = []
    for row in csv.DictReader(text.splitlines(), delimiter="\t"):
        parsed = dict(row)
        for key in ["onset", "duration"]:
            try:
                parsed[key] = float(row[key])
            except (KeyError, TypeError, ValueError):
                parsed[key] = None
        try:
            parsed["sample"] = int(float(row["sample"]))
        except (KeyError, TypeError, ValueError):
            parsed["sample"] = None
        rows.append(parsed)
    return rows


def ids_from_path(path: str) -> dict:
    subject = re.search(r"(sub-[^/]+)", path)
    session = re.search(r"(ses-[^/]+)", path)
    run = re.search(r"_run-([^_]+)_events.tsv$", path)
    return {
        "subject": subject.group(1) if subject else "",
        "session": session.group(1) if session else "",
        "run": run.group(1) if run else "",
    }


def build_windows_for_event_file(path: str, rows: list[dict], window_seconds: float) -> list[dict]:
    ids = ids_from_path(path)
    by_trial: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        trial = str(row.get("trial") or "")
        if trial:
            by_trial[trial].append(row)

    windows = []
    for trial, trial_rows in by_trial.items():
        trial_rows = sorted(trial_rows, key=lambda r: (r["onset"] is None, r["onset"] or 0.0))
        remember = [r for r in trial_rows if r.get("task_role") == "to_remember" and r["onset"] is not None]
        maintenance = [r for r in trial_rows if r.get("task_role") == "work_memory" and r["onset"] is not None]
        probe = [r for r in trial_rows if str(r.get("task_role", "")).startswith("probe") and r["onset"] is not None]
        if remember and maintenance:
            boundary = maintenance[0]["onset"]
            windows.append(
                {
                    **ids,
                    "event_file": path,
                    "trial": trial,
                    "transition": "encoding_to_maintenance",
                    "boundary_onset_s": boundary,
                    "pre_start_s": boundary - window_seconds,
                    "pre_end_s": boundary,
                    "post_start_s": boundary,
                    "post_end_s": boundary + window_seconds,
                    "memory_cond": maintenance[0].get("memory_cond") or remember[-1].get("memory_cond") or "",
                    "n_to_remember_events": len(remember),
                    "n_trial_events": len(trial_rows),
                    "window_status": "PASS",
                }
            )
        if maintenance and probe:
            boundary = probe[0]["onset"]
            windows.append(
                {
                    **ids,
                    "event_file": path,
                    "trial": trial,
                    "transition": "maintenance_to_probe",
                    "boundary_onset_s": boundary,
                    "pre_start_s": boundary - window_seconds,
                    "pre_end_s": boundary,
                    "post_start_s": boundary,
                    "post_end_s": boundary + window_seconds,
                    "memory_cond": probe[0].get("memory_cond") or maintenance[0].get("memory_cond") or "",
                    "n_to_remember_events": len(remember),
                    "n_trial_events": len(trial_rows),
                    "window_status": "PASS",
                }
            )
    return windows


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "subject",
        "session",
        "run",
        "trial",
        "transition",
        "boundary_onset_s",
        "pre_start_s",
        "pre_end_s",
        "post_start_s",
        "post_end_s",
        "memory_cond",
        "n_to_remember_events",
        "n_trial_events",
        "window_status",
        "event_file",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> int:
    parser = argparse.ArgumentParser(description="Build frozen ds004117 transition-window manifest from public events.tsv files.")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--limit-event-files", type=int, default=None)
    parser.add_argument("--window-seconds", type=float, default=1.0)
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    tree = fetch_json(f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1", args.timeout)
    event_paths = sorted(
        item["path"]
        for item in tree.get("tree", [])
        if item.get("type") == "blob" and item.get("path", "").endswith("_events.tsv") and "task-WorkingMemory" in item.get("path", "")
    )
    if args.limit_event_files:
        event_paths = event_paths[: args.limit_event_files]

    windows = []
    file_errors = []
    for path in event_paths:
        try:
            rows = parse_events(fetch_text(raw_url(path), args.timeout))
            windows.extend(build_windows_for_event_file(path, rows, args.window_seconds))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, csv.Error, ValueError) as exc:
            file_errors.append({"path": path, "error": type(exc).__name__, "message": str(exc)[:250]})
        print(f"processed {path}", flush=True)

    by_transition = defaultdict(int)
    by_subject = defaultdict(int)
    for row in windows:
        by_transition[row["transition"]] += 1
        by_subject[row["subject"]] += 1

    payload = {
        "experiment": "P6-E2-ds004117-transition-window-manifest",
        "status": "PASS_TRANSITION_WINDOWS_READY" if windows and not file_errors else "PARTIAL_OR_FAIL",
        "dataset": DATASET,
        "event_files_processed": len(event_paths),
        "file_errors": file_errors,
        "window_seconds_each_side": args.window_seconds,
        "n_windows": len(windows),
        "n_subjects_with_windows": len(by_subject),
        "windows_by_transition": dict(sorted(by_transition.items())),
        "windows_by_subject": dict(sorted(by_subject.items())),
        "claim_audit": {
            "can_run_e3_signal_extraction_after_data_download": bool(windows),
            "can_claim_fast_dynamics_existence": False,
            "can_claim_nap_exists": False,
            "allowed_current_claim": "ds004117 transition windows are defined from public event metadata; signal-level fast dynamics have not been analyzed.",
        },
    }
    write_csv(windows, RESULTS / "e2_ds004117_transition_windows.csv")
    (RESULTS / "e2_ds004117_transition_windows.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["status"] == "PASS_TRANSITION_WINDOWS_READY" else 2


if __name__ == "__main__":
    sys.exit(main())
