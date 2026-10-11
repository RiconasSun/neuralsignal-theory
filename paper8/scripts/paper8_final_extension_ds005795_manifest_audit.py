from __future__ import annotations

import csv
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
AUDIT = ROOT / "dataset_audit"
EXT = ROOT / "extensions" / "measured_physio_final"
DATASET_ID = "on005795"
VERSION = "v1.0.0"
DATASET_PAGE = "https://www.nemar.org/dataset/on005795"
MANIFEST_URL = f"https://data.nemar.org/{DATASET_ID}/{VERSION}/manifest.json"
DESCRIPTION_URL = f"https://data.nemar.org/{DATASET_ID}/{VERSION}/dataset_description.json"
OPENNEURO_ID = "ds005795"
OPENNEURO_TAG = "1.0.0"
OPENNEURO_GRAPHQL = "https://openneuro.org/crn/graphql"


def fetch_json(url: str) -> tuple[dict | list | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            raw = resp.read()
        return json.loads(raw.decode("utf-8")), ""
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {str(exc)[:300]}"


def fetch_openneuro_files() -> tuple[list[dict], str]:
    query = """
    query SnapshotFiles($datasetId: ID!, $tag: String!) {
      snapshot(datasetId: $datasetId, tag: $tag) {
        files(recursive: true) {
          filename
          size
          directory
          annexed
        }
      }
    }
    """
    body = json.dumps({"query": query, "variables": {"datasetId": OPENNEURO_ID, "tag": OPENNEURO_TAG}}).encode("utf-8")
    req = urllib.request.Request(
        OPENNEURO_GRAPHQL,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "nsi-paper8-manifest-audit/0.1"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [], f"{type(exc).__name__}: {str(exc)[:300]}"
    if payload.get("errors"):
        return [], json.dumps(payload["errors"])[:500]
    files = payload.get("data", {}).get("snapshot", {}).get("files", [])
    if not isinstance(files, list):
        return [], "OpenNeuro response did not contain a file list"
    return files, ""


def flatten_manifest(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [row if isinstance(row, dict) else {"value": row} for row in payload]
    if not isinstance(payload, dict):
        return []
    for key in ["files", "entries", "objects", "manifest"]:
        value = payload.get(key)
        if isinstance(value, list):
            return [row if isinstance(row, dict) else {"value": row} for row in value]
    return []


def file_path(row: dict) -> str:
    for key in ["path", "filename", "name", "key", "url"]:
        value = row.get(key)
        if isinstance(value, str):
            return value
    return ""


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def classify(paths: list[str]) -> dict:
    lower = [p.lower() for p in paths]
    subjects = set()
    tasks = set()
    for p in lower:
        for part in p.split("/"):
            if re.fullmatch(r"sub-[a-z0-9]+", part):
                subjects.add(part)
        tasks.update(re.findall(r"_task-([a-z0-9]+)", p))
    return {
        "n_total_files": len(paths),
        "n_subjects_detected": len(subjects),
        "subjects_detected": sorted(subjects),
        "tasks_detected": sorted(tasks),
        "n_func_files": sum("/func/" in p for p in lower),
        "n_bold_files": sum(p.endswith("_bold.nii.gz") or "_bold." in p for p in lower),
        "n_physio_files": sum("physio" in p for p in lower),
        "n_respiration_candidates": sum(("resp" in p or "breath" in p or "respiration" in p) for p in lower),
        "n_cardiac_candidates": sum(("cardiac" in p or "pulse" in p or "ecg" in p) for p in lower),
        "n_eeg_files": sum("/eeg/" in p for p in lower),
        "n_anat_files": sum("/anat/" in p for p in lower),
        "n_events_files": sum(p.endswith("_events.tsv") for p in lower),
        "n_channels_files": sum(p.endswith("_channels.tsv") for p in lower),
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    EXT.mkdir(parents=True, exist_ok=True)

    manifest_payload, manifest_error = fetch_json(MANIFEST_URL)
    description_payload, description_error = fetch_json(DESCRIPTION_URL)
    manifest_rows = flatten_manifest(manifest_payload)
    openneuro_error = ""
    source_used = "nemar_manifest"
    if not manifest_rows:
        manifest_rows, openneuro_error = fetch_openneuro_files()
        source_used = "openneuro_graphql" if manifest_rows else "none"
    paths = [file_path(row) for row in manifest_rows]
    paths = [p for p in paths if p]
    counts = classify(paths)

    selected_rows = []
    for row in manifest_rows:
        path = file_path(row)
        low = path.lower()
        if any(token in low for token in ["/func/", "/eeg/", "/anat/", "physio", "resp", "pulse", "ecg", "_events.tsv", "_channels.tsv"]):
            selected_rows.append({
                "path": path,
                "size": row.get("size") or row.get("size_bytes") or row.get("bytes") or "",
                "annexed": row.get("annexed", ""),
                "url": row.get("url", ""),
                "directory": row.get("directory", ""),
            })

    description_name = ""
    if isinstance(description_payload, dict):
        description_name = str(description_payload.get("Name") or description_payload.get("name") or "")

    status = "PASS_DS005795_MANIFEST_AUDITED" if paths else "BLOCKED_DS005795_MANIFEST_UNAVAILABLE"
    payload = {
        "paper": "Paper 8",
        "experiment": "P8-final-extension-ds005795-manifest-audit",
        "status": status,
        "dataset_id": DATASET_ID,
        "version": VERSION,
        "dataset_page": DATASET_PAGE,
        "manifest_url": MANIFEST_URL,
        "dataset_description_url": DESCRIPTION_URL,
        "dataset_name_from_description": description_name,
        "manifest_error": manifest_error,
        "openneuro_graphql_url": OPENNEURO_GRAPHQL,
        "openneuro_graphql_error": openneuro_error,
        "source_used": source_used,
        "description_error": description_error,
        **counts,
        "selected_file_rows_written": len(selected_rows),
        "role": "convergent measured-physiology validation, not direct Encode/Maintain/Probe replication",
        "claim_boundary": "This step audits public ds005795/NEMAR file availability only. It does not run the nuisance ladder or establish physiology-robust transition dynamics.",
        "forbidden_claims": [
            "P8 v2 is rescued",
            "ds005795 directly replicates HCP working-memory transitions",
            "measured physiology confounds are resolved",
            "NAP is validated",
            "CWP is validated",
        ],
    }
    write_csv(AUDIT / "p8_final_extension_ds005795_selected_files.csv", selected_rows)
    (RESULTS / "p8_final_extension_ds005795_manifest_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not status.startswith("PASS"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
