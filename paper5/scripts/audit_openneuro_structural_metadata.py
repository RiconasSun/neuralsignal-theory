from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from openneuro import _download


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUT = ROOT / "online_structural_audit"

STRUCTURAL_TOKENS = [
    "/anat/",
    "/dwi/",
    "T1w",
    "T2w",
    "dwi",
    "bvec",
    "bval",
    "connectome",
    "tract",
    "fiber",
    "fibre",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def classify(filename: str) -> str:
    lower = filename.lower()
    if "/dwi/" in lower or lower.endswith(".bvec") or lower.endswith(".bval") or "_dwi." in lower:
        return "dwi"
    if "/anat/" in lower or "t1w" in lower or "t2w" in lower:
        return "anat"
    if "connectome" in lower or "tract" in lower or "fiber" in lower or "fibre" in lower:
        return "connectome_or_tract"
    return "other_structural_candidate"


def audit_dataset(dataset: str, tag: str | None = None) -> dict[str, Any]:
    try:
        metadata = _download._get_download_metadata(
            dataset_id=dataset,
            tag=tag,
            max_retries=2,
            metadata_timeout=90.0,
        )
        files = [f.filename for f in metadata.files]
        candidates = [name for name in files if any(token.lower() in name.lower() for token in STRUCTURAL_TOKENS)]
        by_type: dict[str, int] = {}
        for name in candidates:
            by_type[classify(name)] = by_type.get(classify(name), 0) + 1
        return {
            "dataset": dataset,
            "tag": tag or "",
            "status": "STRUCTURAL_CANDIDATES_FOUND" if candidates else "NO_STRUCTURAL_CANDIDATES_IN_OPENNEURO_METADATA",
            "snapshot_id": metadata.id,
            "n_total_files": len(files),
            "n_structural_candidate_files": len(candidates),
            "structural_candidate_counts_by_type": by_type,
            "structural_candidate_files": candidates[:500],
            "error": "",
        }
    except Exception as exc:
        return {
            "dataset": dataset,
            "tag": tag or "",
            "status": "OPENNEURO_METADATA_QUERY_FAILED",
            "snapshot_id": "",
            "n_total_files": 0,
            "n_structural_candidate_files": 0,
            "structural_candidate_counts_by_type": {},
            "structural_candidate_files": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit OpenNeuro metadata for structural/anat/dwi/connectome files.")
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    payload = [audit_dataset(dataset, args.tag or None) for dataset in args.dataset]
    (OUT / "openneuro_structural_metadata_audit.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    sys.exit(main())
