from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


@dataclass(frozen=True)
class RepoCandidate:
    dataset_id: str
    role: str
    owner: str
    repo: str
    branch: str
    expected_stage_terms: list[str]


REPOS = [
    RepoCandidate("ds004752", "primary_candidate", "OpenNeuroDatasets", "ds004752", "main", ["encoding", "maintenance", "recall"]),
    RepoCandidate("ds002550", "external_candidate", "nemarDatasets", "on002550", "main", ["selection", "maintenance", "workingmemory", "working_memory"]),
    RepoCandidate("ds004117", "external_candidate", "OpenNeuroDatasets", "ds004117", "main", ["presentation", "maintenance", "probe"]),
]


def fetch_json(url: str, timeout: int) -> tuple[dict | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "NSI-Paper6-EventAudit/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTPError:{exc.code}"
    except urllib.error.URLError as exc:
        return None, f"URLError:{exc.reason}"
    except TimeoutError:
        return None, "TimeoutError"
    except json.JSONDecodeError as exc:
        return None, f"JSONDecodeError:{exc}"


def fetch_text(url: str, timeout: int) -> tuple[str | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "NSI-Paper6-EventAudit/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTPError:{exc.code}"
    except urllib.error.URLError as exc:
        return None, f"URLError:{exc.reason}"
    except TimeoutError:
        return None, "TimeoutError"


def raw_url(repo: RepoCandidate, path: str) -> str:
    quoted = urllib.parse.quote(path)
    return f"https://raw.githubusercontent.com/{repo.owner}/{repo.repo}/{repo.branch}/{quoted}"


def parse_tsv_preview(text: str) -> dict:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return {"columns": [], "n_preview_rows": 0, "trial_type_values": [], "value_terms": []}
    reader = csv.DictReader(lines, delimiter="\t")
    rows = list(reader)
    columns = reader.fieldnames or []
    values = set()
    for row in rows:
        for key in ["trial_type", "event_type", "condition", "stage", "task", "stim_type", "response_type"]:
            if key in row and row[key]:
                values.add(row[key])
    column_values = {}
    for key in ["trial_type", "event_type", "task_role", "memory_cond", "condition", "stage", "value"]:
        if key in columns:
            column_values[key] = sorted({row.get(key, "") for row in rows if row.get(key, "")})[:80]
    joined = " ".join(" ".join(row.values()) for row in rows).lower()
    return {
        "columns": columns,
        "n_preview_rows": len(rows),
        "trial_type_values": sorted(values)[:40],
        "column_values": column_values,
        "value_terms": sorted({term for term in ["encoding", "maintenance", "recall", "probe", "presentation", "selection"] if term in joined}),
    }


def audit_repo(repo: RepoCandidate, timeout: int, preview_limit: int) -> dict:
    tree_url = f"https://api.github.com/repos/{repo.owner}/{repo.repo}/git/trees/{repo.branch}?recursive=1"
    tree_payload, tree_error = fetch_json(tree_url, timeout)
    if tree_error or not tree_payload:
        return {
            "dataset_id": repo.dataset_id,
            "role": repo.role,
            "repo": f"{repo.owner}/{repo.repo}",
            "tree_error": tree_error,
            "e2_status": "TREE_UNAVAILABLE",
        }
    paths = [item["path"] for item in tree_payload.get("tree", []) if item.get("type") == "blob"]
    event_paths = sorted([p for p in paths if p.endswith("_events.tsv")])
    channel_paths = sorted([p for p in paths if p.endswith("_channels.tsv")])
    recording_paths = sorted([p for p in paths if p.endswith((".edf", ".vhdr", ".set", ".fif", ".ds", ".meg4"))])
    sidecars = sorted([p for p in paths if p.endswith(("_events.json", "_eeg.json", "_ieeg.json", "_meg.json"))])

    previews = []
    for path in event_paths[:preview_limit]:
        text, error = fetch_text(raw_url(repo, path), timeout)
        preview = parse_tsv_preview(text) if text else {"columns": [], "n_preview_rows": 0, "trial_type_values": [], "value_terms": []}
        previews.append({"path": path, "fetch_error": error, **preview})

    all_columns = sorted({col for preview in previews for col in preview.get("columns", [])})
    all_values = " ".join(
        [
            " ".join(preview.get("trial_type_values", []))
            + " "
            + " ".join(preview.get("value_terms", []))
            + " "
            + " ".join(
                value
                for values in preview.get("column_values", {}).values()
                for value in values
            )
            for preview in previews
        ]
    ).lower()
    has_onset_or_sample = any(col in all_columns for col in ["onset", "duration", "sample", "start_sample", "end_sample", "start", "end"])
    stage_hits = {term: term.lower() in all_values for term in repo.expected_stage_terms}
    semantic_aliases = {
        "encoding": ["encoding", "to_remember", "show_letter", "stimulus"],
        "presentation": ["presentation", "show_letter", "stimulus"],
        "maintenance": ["maintenance", "work_memory", "show_dash", "wm"],
        "recall": ["recall", "probe"],
        "probe": ["probe", "probe_target"],
        "selection": ["selection", "cueleft", "cueright", "cue"],
        "workingmemory": ["workingmemory", "working memory", "work_memory"],
        "working_memory": ["working_memory", "working memory", "work_memory"],
    }
    semantic_stage_hits = {
        term: stage_hits[term] or any(alias in all_values for alias in semantic_aliases.get(term, []))
        for term in repo.expected_stage_terms
    }
    has_expected_terms = sum(semantic_stage_hits.values()) >= max(1, min(2, len(repo.expected_stage_terms)))
    has_events = len(event_paths) > 0
    has_recordings = len(recording_paths) > 0

    if has_events and has_recordings and has_onset_or_sample and has_expected_terms:
        status = "PASS_E2_INITIAL_TRANSITION_AUDIT"
    elif has_events and has_recordings and has_onset_or_sample:
        status = "PARTIAL_EVENTS_NEED_MANUAL_STAGE_MAPPING"
    elif has_events:
        status = "PARTIAL_EVENTS_NEED_TIMING_COLUMNS"
    else:
        status = "FAIL_NO_EVENTS"

    return {
        "dataset_id": repo.dataset_id,
        "role": repo.role,
        "repo": f"{repo.owner}/{repo.repo}",
        "tree_error": None,
        "n_files": len(paths),
        "n_event_files": len(event_paths),
        "n_channel_files": len(channel_paths),
        "n_recording_files": len(recording_paths),
        "n_sidecar_files": len(sidecars),
        "example_event_files": event_paths[:10],
        "example_recording_files": recording_paths[:10],
        "event_preview": previews,
        "all_preview_columns": all_columns,
        "has_onset_or_sample_timing": has_onset_or_sample,
        "expected_stage_hits_in_preview": stage_hits,
        "semantic_stage_hits_in_preview": semantic_stage_hits,
        "e2_status": status,
    }


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "dataset_id",
        "role",
        "repo",
        "e2_status",
        "n_files",
        "n_event_files",
        "n_channel_files",
        "n_recording_files",
        "has_onset_or_sample_timing",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper 6 E2 event semantics audit for candidate electrophysiology datasets.")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--preview-limit", type=int, default=5)
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for repo in REPOS:
        row = audit_repo(repo, args.timeout, args.preview_limit)
        rows.append(row)
        print(f"{repo.dataset_id}: {row['e2_status']}", flush=True)

    payload = {
        "experiment": "P6-E2-event-semantics-audit",
        "status": "PASS_INITIAL_E2" if any(r["e2_status"] == "PASS_E2_INITIAL_TRANSITION_AUDIT" for r in rows) else "NEEDS_MANUAL_STAGE_MAPPING",
        "rows": rows,
        "claim_audit": {
            "can_define_primary_transition_windows_without_download": any(
                r["e2_status"] == "PASS_E2_INITIAL_TRANSITION_AUDIT" for r in rows
            ),
            "can_claim_fast_dynamics_existence": False,
            "can_claim_nap_exists": False,
            "allowed_current_claim": "P6 has an event-semantics audit for public candidate datasets; no fast neural dynamics have been modeled.",
        },
    }
    (RESULTS / "e2_event_semantics_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows, RESULTS / "e2_event_semantics_audit.csv")
    return 0 if payload["status"] == "PASS_INITIAL_E2" else 2


if __name__ == "__main__":
    sys.exit(main())
