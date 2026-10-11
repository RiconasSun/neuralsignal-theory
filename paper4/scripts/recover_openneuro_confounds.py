from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import openneuro


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
OUT_ROOT = ROOT / "online_confound_recovery"

INCLUDE_PATTERNS = [
    "**/*confound*",
    "**/*Confound*",
    "**/*motion*",
    "**/*Motion*",
    "**/*regressor*",
    "**/*Regressor*",
    "**/*dvars*",
    "**/*DVARS*",
    "**/*framewise*",
    "**/*Framewise*",
    "**/*fd*",
    "**/*FD*",
]

DERIVATIVES_PATTERNS = ["derivatives/**"]

CONFOUND_PATTERNS = [
    "*confound*",
    "*Confound*",
    "*motion*",
    "*Motion*",
    "*regressor*",
    "*Regressor*",
    "*dvars*",
    "*DVARS*",
    "*framewise*",
    "*Framewise*",
    "*fd*",
    "*FD*",
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def discover_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    if root.exists():
        for pattern in CONFOUND_PATTERNS:
            files.update(p for p in root.rglob(pattern) if p.is_file())
    return sorted(files)


def attempt_download(dataset: str, tag: str | None, target: Path, include_patterns: list[str]) -> dict[str, str]:
    try:
        openneuro.download(
            dataset=dataset,
            tag=tag,
            target_dir=target,
            include=include_patterns,
            verify_hash=False,
            verify_size=False,
            max_retries=2,
            max_concurrent_downloads=2,
            metadata_timeout=90.0,
        )
        return {"status": "DOWNLOAD_ATTEMPT_COMPLETED", "error": ""}
    except Exception as exc:
        return {"status": "DOWNLOAD_ATTEMPT_FAILED", "error": f"{type(exc).__name__}: {exc}"}


def recover(dataset: str, tag: str | None = None) -> dict[str, Any]:
    target = OUT_ROOT / dataset
    target.mkdir(parents=True, exist_ok=True)
    derivatives_attempt = attempt_download(dataset, tag, target, DERIVATIVES_PATTERNS)
    confounds_attempt = attempt_download(dataset, tag, target, INCLUDE_PATTERNS)

    files = discover_files(target)
    payload = {
        "dataset": dataset,
        "tag": tag or "",
        "target_dir": rel(target),
        "status": "MEASURED_CONFOUNDS_RECOVERED" if files else "NO_MEASURED_CONFOUNDS_FOUND_ON_OPENNEURO",
        "derivatives_attempt": derivatives_attempt,
        "confounds_filename_attempt": confounds_attempt,
        "error": "; ".join(x["error"] for x in [derivatives_attempt, confounds_attempt] if x["error"]),
        "include_patterns": INCLUDE_PATTERNS,
        "derivatives_patterns": DERIVATIVES_PATTERNS,
        "recovered_candidate_confound_file_count": len(files),
        "recovered_candidate_confound_files": [rel(p) for p in files[:200]],
        "measured_confounds_recovered": len(files) > 0,
    }
    (target / "recovery_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover OpenNeuro derivatives/confounds for Paper 4.")
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    payloads = [recover(dataset, args.tag or None) for dataset in args.dataset]
    summary_path = OUT_ROOT / "online_confound_recovery_summary.json"
    summary_path.write_text(json.dumps(payloads, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payloads, indent=2))


if __name__ == "__main__":
    main()
