from __future__ import annotations

import csv
import gzip
import json
import argparse
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
AUDIT = ROOT / "dataset_audit"
DATA = ROOT / "data_ds005795_smoke"
SELECTED = AUDIT / "p8_final_extension_ds005795_selected_files.csv"
DATASET = "ds005795"
TAG = "1.0.0"
SUBJECT = "sub-01"
TASK = "learning"


def candidate_urls(path: str) -> list[str]:
    encoded = urllib.parse.quote(path, safe="/")
    return [
        f"https://openneuro.org/crn/datasets/{DATASET}/snapshots/{TAG}/files/{encoded}",
        f"https://s3.amazonaws.com/openneuro.org/{DATASET}/{path}",
        f"https://s3.amazonaws.com/openneuro.org/{DATASET}/{TAG}/{path}",
    ]


def download(path: str, target: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    if target.exists() and target.stat().st_size > 0:
        return {"path": path, "target": str(target), "status": "exists", "size_bytes": target.stat().st_size, "url_used": ""}
    for url in candidate_urls(path):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "nsi-paper8-ds005795-smoke/0.1"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                target.write_bytes(resp.read())
            return {"path": path, "target": str(target), "status": "downloaded", "size_bytes": target.stat().st_size, "url_used": url}
        except (urllib.error.URLError, TimeoutError) as exc:
            errors.append({"url": url, "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
    return {"path": path, "target": str(target), "status": "failed", "size_bytes": 0, "errors": errors}


def inspect_tsv_gz(path: Path) -> dict:
    if not path.exists() or path.suffix != ".gz":
        return {}
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
        header = f.readline().strip().split("\t")
        rows = sum(1 for _ in f)
    return {"columns": header, "n_rows": rows}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download a small ds005795 fMRI/physio/eeg smoke subset.")
    parser.add_argument("--subjects", nargs="+", default=[SUBJECT], help="BIDS subject IDs, e.g. sub-01 sub-02 sub-03")
    parser.add_argument("--task", default=TASK)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    if not SELECTED.exists():
        raise SystemExit(f"Missing manifest audit CSV: {SELECTED}")
    rows = list(csv.DictReader(SELECTED.open("r", encoding="utf-8", newline="")))
    available = {row["path"]: row for row in rows}
    downloads = []
    per_subject = []
    for subject in args.subjects:
        wanted_names = [
            "physio.json",
            f"{subject}/func/{subject}_task-{args.task}_events.tsv",
            f"{subject}/func/{subject}_task-{args.task}_physio.tsv.gz",
            f"{subject}/func/{subject}_task-{args.task}_bold.json",
            f"{subject}/func/{subject}_task-{args.task}_bold.nii.gz",
            f"{subject}/eeg/{subject}_task-{args.task}_channels.tsv",
            f"{subject}/eeg/{subject}_task-{args.task}_events.tsv",
            f"{subject}/eeg/{subject}_task-{args.task}_eeg.json",
        ]
        subject_downloads = []
        for path in wanted_names:
            if path not in available:
                subject_downloads.append({"path": path, "status": "missing_from_manifest"})
                continue
            subject_downloads.append(download(path, DATA / path))
        downloads.extend(subject_downloads)
        physio_target = DATA / f"{subject}/func/{subject}_task-{args.task}_physio.tsv.gz"
        events_target = DATA / f"{subject}/func/{subject}_task-{args.task}_events.tsv"
        per_subject.append({
            "subject": subject,
            "physio_preview": inspect_tsv_gz(physio_target),
            "events_exists": events_target.exists(),
            "events_size_bytes": events_target.stat().st_size if events_target.exists() else 0,
            "status": "ready" if all(row.get("status") in {"downloaded", "exists"} for row in subject_downloads) else "partial",
        })
    payload = {
        "paper": "Paper 8",
        "experiment": "P8-final-extension-ds005795-smoke-download",
        "status": "PASS_DS005795_SMALL_PHYSIO_SMOKE_DOWNLOADED" if all(row.get("status") in {"downloaded", "exists"} for row in downloads) else "PARTIAL_DS005795_SMALL_PHYSIO_SMOKE_DOWNLOAD",
        "subjects": args.subjects,
        "task": args.task,
        "downloads": downloads,
        "per_subject": per_subject,
        "claim_boundary": "This downloads only a small ds005795 physiology/event smoke subset. It does not run the nuisance ladder or establish physiology-robust transition dynamics.",
    }
    (RESULTS / "p8_final_extension_ds005795_smoke_download.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["status"].startswith("PASS"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
