from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


@dataclass(frozen=True)
class Candidate:
    dataset_id: str
    name: str
    modality: str
    role: str
    source_url: str
    dataset_description_url: str | None
    participants_url: str | None
    readme_url: str | None
    expected_transition_semantics: list[str]
    expected_strength: str


CANDIDATES = [
    Candidate(
        dataset_id="ds004752",
        name="Intracranial EEG, scalp EEG and beamforming sources during verbal working memory",
        modality="iEEG + scalp EEG + beamforming derivatives",
        role="primary_candidate",
        source_url="https://openneuro.org/datasets/ds004752",
        dataset_description_url="https://raw.githubusercontent.com/OpenNeuroDatasets/ds004752/main/dataset_description.json",
        participants_url="https://raw.githubusercontent.com/OpenNeuroDatasets/ds004752/main/participants.tsv",
        readme_url="https://raw.githubusercontent.com/OpenNeuroDatasets/ds004752/main/README",
        expected_transition_semantics=["encoding", "maintenance", "recall"],
        expected_strength="best current P6 fit because encoding, maintenance and recall are temporally separated and iEEG is present",
    ),
    Candidate(
        dataset_id="ds002550",
        name="Differential brain mechanisms of selection and maintenance of information during working memory",
        modality="MEG",
        role="external_candidate",
        source_url="https://openneuro.org/datasets/ds002550",
        dataset_description_url="https://raw.githubusercontent.com/nemarDatasets/on002550/main/dataset_description.json",
        participants_url="https://raw.githubusercontent.com/nemarDatasets/on002550/main/participants.tsv",
        readme_url="https://raw.githubusercontent.com/nemarDatasets/on002550/main/README.md",
        expected_transition_semantics=["selection", "maintenance", "working memory"],
        expected_strength="strong external MEG candidate if events expose selection/maintenance timing",
    ),
    Candidate(
        dataset_id="ds004117",
        name="Modified Sternberg Working Memory Experiment",
        modality="EEG",
        role="external_candidate",
        source_url="https://openneuro.org/datasets/ds004117",
        dataset_description_url="https://raw.githubusercontent.com/OpenNeuroDatasets/ds004117/main/dataset_description.json",
        participants_url="https://raw.githubusercontent.com/OpenNeuroDatasets/ds004117/main/participants.tsv",
        readme_url="https://raw.githubusercontent.com/OpenNeuroDatasets/ds004117/main/README",
        expected_transition_semantics=["letter sequence presentation", "maintenance", "probe"],
        expected_strength="EEG Sternberg candidate for lower-resolution replication if event semantics are usable",
    ),
]


def fetch_text(url: str | None, timeout: int) -> tuple[str | None, str | None]:
    if not url:
        return None, "no_url"
    request = urllib.request.Request(url, headers={"User-Agent": "NSI-Paper6-DatasetAudit/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
        return body, None
    except urllib.error.HTTPError as exc:
        return None, f"HTTPError:{exc.code}"
    except urllib.error.URLError as exc:
        return None, f"URLError:{exc.reason}"
    except TimeoutError:
        return None, "TimeoutError"


def parse_subject_count(participants_tsv: str | None) -> int | None:
    if not participants_tsv:
        return None
    rows = [line for line in participants_tsv.splitlines() if line.strip()]
    if len(rows) <= 1:
        return 0
    return len(rows) - 1


def parse_dataset_description(text: str | None) -> dict:
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return {
        "Name": payload.get("Name") or payload.get("name"),
        "BIDSVersion": payload.get("BIDSVersion"),
        "DatasetDOI": payload.get("DatasetDOI"),
        "License": payload.get("License"),
        "Authors": payload.get("Authors") or payload.get("Authors".lower()),
    }


def keyword_hits(text: str | None, keywords: list[str]) -> dict[str, bool]:
    if not text:
        return {keyword: False for keyword in keywords}
    lowered = text.lower()
    return {keyword: bool(re.search(r"\b" + re.escape(keyword.lower()) + r"\b", lowered)) for keyword in keywords}


def score_candidate(candidate: Candidate, description: dict, participants_n: int | None, readme: str | None, errors: dict[str, str | None]) -> dict:
    text = " ".join(
        [
            str(description.get("Name") or ""),
            candidate.name,
            candidate.modality,
            readme or "",
        ]
    )
    modality_hits = keyword_hits(text, ["ieeg", "eeg", "meg", "intracranial", "scalp", "beamforming"])
    transition_hits = keyword_hits(text, candidate.expected_transition_semantics)
    has_fast_modality = any(modality_hits[k] for k in ["ieeg", "eeg", "meg", "intracranial"])
    has_transition_semantics = sum(transition_hits.values()) >= max(1, min(2, len(candidate.expected_transition_semantics)))
    has_subject_inventory = participants_n is not None and participants_n > 0
    metadata_accessible = errors.get("dataset_description") is None or errors.get("readme") is None

    if metadata_accessible and has_fast_modality and has_transition_semantics and has_subject_inventory:
        status = "PASS_INITIAL_E1"
    elif metadata_accessible and has_fast_modality and has_subject_inventory:
        status = "PARTIAL_NEEDS_EVENT_FILE_AUDIT"
    else:
        status = "NOT_READY"

    return {
        "dataset_id": candidate.dataset_id,
        "name": candidate.name,
        "role": candidate.role,
        "modality": candidate.modality,
        "source_url": candidate.source_url,
        "dataset_name_from_metadata": description.get("Name"),
        "bids_version": description.get("BIDSVersion"),
        "dataset_doi": description.get("DatasetDOI"),
        "license": description.get("License"),
        "n_participants_from_tsv": participants_n,
        "expected_transition_semantics": candidate.expected_transition_semantics,
        "transition_keyword_hits": transition_hits,
        "modality_keyword_hits": modality_hits,
        "metadata_errors": errors,
        "initial_e1_status": status,
        "p6_use": candidate.expected_strength,
    }


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "dataset_id",
        "role",
        "modality",
        "initial_e1_status",
        "n_participants_from_tsv",
        "dataset_name_from_metadata",
        "bids_version",
        "dataset_doi",
        "license",
        "source_url",
        "p6_use",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper 6 E1 public electrophysiology dataset audit.")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for candidate in CANDIDATES:
        desc_text, desc_error = fetch_text(candidate.dataset_description_url, args.timeout)
        participants_text, participants_error = fetch_text(candidate.participants_url, args.timeout)
        readme_text, readme_error = fetch_text(candidate.readme_url, args.timeout)
        row = score_candidate(
            candidate,
            parse_dataset_description(desc_text),
            parse_subject_count(participants_text),
            readme_text,
            {
                "dataset_description": desc_error,
                "participants": participants_error,
                "readme": readme_error,
            },
        )
        rows.append(row)
        print(f"{candidate.dataset_id}: {row['initial_e1_status']}", flush=True)

    payload = {
        "experiment": "P6-E1-dataset-audit",
        "status": "PASS_INITIAL_E1" if any(r["initial_e1_status"] == "PASS_INITIAL_E1" for r in rows) else "NO_PRIMARY_DATASET_READY",
        "paper_type": "Explanation Paper",
        "central_question": "Do reproducible macroscopic brain-state transitions contain reproducible subsecond neural dynamics?",
        "primary_candidate": "ds004752",
        "rows": rows,
        "claim_audit": {
            "can_claim_nap_exists": False,
            "can_claim_fast_dynamics_existence": False,
            "can_claim_transition_specificity": False,
            "can_claim_cross_dataset_replication": False,
            "allowed_current_claim": "P6 has a frozen protocol and an initial public dataset audit; neural dynamics tests have not yet been run.",
            "forbidden_claims": [
                "NAP is validated.",
                "CWP maps to NAP.",
                "Macro transitions are mechanistically explained.",
                "Fast neural dynamics are universal primitives.",
            ],
        },
    }
    (RESULTS / "e1_dataset_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows, RESULTS / "e1_dataset_audit.csv")
    return 0 if payload["status"] == "PASS_INITIAL_E1" else 2


if __name__ == "__main__":
    sys.exit(main())
