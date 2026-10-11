"""P11 M0: metadata-only acquisition and fail-closed protocol freeze verification."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import platform
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parent
RESULTS = PAPER / "results" / "M0"
META = PAPER / "data_manifest" / "metadata"
LOCK = PAPER / "protocol" / "freeze.json"
NM = "b054fbef57f9c4fb93477ecc5c88c6114dbc5662"
DS = "234fd4c04dea66ab9b0fd5ddbf4ec51f56b6ad02"
DANDI_VERSION = "0.220126.1852"
SOURCES = {
    "nm_tag.json": "https://api.github.com/repos/nemarDatasets/nm000363/git/ref/tags/v1.0.0",
    "nm_annotated_tag.json": "https://api.github.com/repos/nemarDatasets/nm000363/git/tags/2ed15e39c2f9b8306fecab5571ebbf5f5c3129af",
    "nm_description.json": f"https://raw.githubusercontent.com/nemarDatasets/nm000363/{NM}/dataset_description.json",
    "nm_readme.md": f"https://raw.githubusercontent.com/nemarDatasets/nm000363/{NM}/README.md",
    "nm_participants.tsv": f"https://raw.githubusercontent.com/nemarDatasets/nm000363/{NM}/participants.tsv",
    "ds_tag.json": "https://api.github.com/repos/OpenNeuroDatasets/ds004752/git/ref/tags/1.0.1",
    "ds_description.json": f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds004752/{DS}/dataset_description.json",
    "ds_participants.tsv": f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds004752/{DS}/participants.tsv",
    "dandi_info.json": f"https://api.dandiarchive.org/api/dandisets/000004/versions/{DANDI_VERSION}/info/",
}
FROZEN_INPUTS = [
    "protocol/protocol.json", "scripts/run_m0.py", "tests/test_m0.py",
    "scripts/reproduce-m0.ps1", "REPRODUCE_M0.md",
    "data_manifest/source_receipts.json", "environment/environment.json",
] + [f"data_manifest/metadata/{name}" for name in SOURCES]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def environment() -> dict:
    return {
        "python_version": platform.python_version(), "implementation": platform.python_implementation(),
        "platform": platform.platform(), "executable": sys.executable,
        "m0_dependencies": "Python standard library only; future modeling dependencies not installed or certified by M0",
        "installed_distributions": sorted({(d.metadata["Name"], d.version) for d in importlib.metadata.distributions() if d.metadata["Name"]}),
    }


def acquire_metadata() -> None:
    if LOCK.exists():
        raise ValueError("Freeze exists: cannot refetch or overwrite frozen metadata")
    META.mkdir(parents=True, exist_ok=True)
    receipts = []
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={"User-Agent": "NSI-P11-M0-metadata-audit", "Accept": "application/json,text/plain,*/*"})
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read(2 * 1024 * 1024 + 1)
            if len(content) > 2 * 1024 * 1024:
                raise ValueError(f"Metadata size limit exceeded: {name}")
            status = response.status
        if name.endswith(".json"):
            json.loads(content)
        (META / name).write_bytes(content)
        receipts.append({"name": name, "url": url, "retrieved_at_utc": now(), "http_status": status, "bytes": len(content), "sha256": sha(META / name)})
    write_json(PAPER / "data_manifest" / "source_receipts.json", {"scope": "metadata only; no experimental data", "sources": receipts})


def chronological_split(trial_ids: list[int]) -> dict[str, list[int]]:
    if len(trial_ids) < 40:
        raise ValueError("DATA_INSUFFICIENT: fewer than 40 metadata-valid trials")
    if any(type(t) is not int or t < 1 for t in trial_ids) or len(set(trial_ids)) != len(trial_ids):
        raise ValueError("Invalid or duplicate trial identity")
    trials = sorted(trial_ids)
    ntrain, nval = len(trials) * 6 // 10, len(trials) * 2 // 10
    return {"train": trials[:ntrain], "validation": trials[ntrain:ntrain+nval], "test": trials[ntrain+nval:]}


def validate_protocol(p: dict) -> None:
    if p["execution"]["milestone"] != "M0" or not p["execution"]["stop_after_gate"]:
        raise ValueError("M0-only execution required")
    if p["data"]["primary_spikes"]["git_commit"] != NM or p["data"]["companion_ieeg"]["git_commit"] != DS:
        raise ValueError("Pinned primary source identity changed")
    if p["data"]["external"]["version"] != DANDI_VERSION or p["data"]["companion_ieeg"]["pooled_with_spikes"]:
        raise ValueError("External pin or modality separation violated")
    if p["features"]["primary_bin_ms"] != 100 or p["statistics"]["independent_unit"] != "subject":
        raise ValueError("Primary bin or independent unit changed")
    if p["splits"]["train_fraction"] != 0.6 or p["splits"]["validation_fraction"] != 0.2:
        raise ValueError("Split contract mismatch")
    if "y_<t" not in p["primary_metric"]["formula"] or "nats" not in p["primary_metric"]["units"]:
        raise ValueError("Causal predictive likelihood required")
    required = {"rate_preserving", "spike_jitter", "time_shift", "trial_position", "random_segmentation"}
    if {n["id"] for n in p["null_tests"]} != required:
        raise ValueError("Required null tests missing")
    if set(p["models"]) != {"discrete", "continuous", "hybrid", "shared"}:
        raise ValueError("Model family silently removed")
    if p["data"]["external"]["direct_replication_claim_allowed"]:
        raise ValueError("External direct-replication claim forbidden")


def validate_sources() -> dict:
    for name, expected in (("nm_tag.json", NM), ("ds_tag.json", DS)):
        record = load(META / name)
        if name == "nm_tag.json" and record["object"]["type"] == "tag":
            tag = load(META / "nm_annotated_tag.json")
            if tag["sha"] != record["object"]["sha"] or tag["tag"] != "v1.0.0":
                raise ValueError("Annotated tag identity mismatch")
            record = tag
        if record["object"]["type"] != "commit" or record["object"]["sha"] != expected:
            raise ValueError(f"Source tag mismatch: {name}")
    nm, ds = load(META / "nm_description.json"), load(META / "ds_description.json")
    if "nm000363" not in json.dumps(nm) or "ds004752.v1.0.1" not in json.dumps(ds):
        raise ValueError("Dataset description identifier mismatch")
    dandi = load(META / "dandi_info.json")
    if dandi.get("version") != DANDI_VERSION or "000004" not in json.dumps(dandi):
        raise ValueError("DANDI published version mismatch")
    receipts = load(PAPER / "data_manifest" / "source_receipts.json")["sources"]
    if {r["name"] for r in receipts} != set(SOURCES):
        raise ValueError("Incomplete source receipts")
    for receipt in receipts:
        if receipt["url"] != SOURCES[receipt["name"]] or receipt["http_status"] != 200 or receipt["sha256"] != sha(META / receipt["name"]):
            raise ValueError("Source receipt or checksum mismatch")
    def participants(name: str) -> list[str]:
        with (META / name).open(encoding="utf-8-sig", newline="") as handle:
            return [r["participant_id"] for r in csv.DictReader(handle, delimiter="\t")]
    nm_ids, ds_ids = participants("nm_participants.tsv"), participants("ds_participants.tsv")
    if not nm_ids or len(set(nm_ids)) != len(nm_ids) or not set(nm_ids).issubset(ds_ids):
        raise ValueError("Participant roster alignment failed")
    return {"nm_metadata_participants": nm_ids, "companion_metadata_participants": ds_ids,
            "anatomy_task_unit_trial_qc": "NOT_ASSESSED_M1_REQUIRED", "external_eligibility": "NOT_ASSESSED",
            "source_receipts": len(receipts), "experimental_data_acquired": False}


def verify_hashes(base: Path, hashes: dict[str, str]) -> None:
    for name, expected in hashes.items():
        if sha(base / name) != expected:
            raise ValueError(f"Frozen artifact mismatch: {name}")


def preserved_papers() -> None:
    paths = [f"paper{i}" for i in range(1, 11)]
    if git("diff", "HEAD", "--name-only", "--", *paths):
        raise ValueError("Papers 1-10 modified")
    if LOCK.exists():
        base = load(LOCK)["repository"]["base_commit"]
        if git("diff", base, "HEAD", "--name-only", "--", *paths):
            raise ValueError("Papers 1-10 changed since freeze")


def freeze() -> None:
    if LOCK.exists():
        raise ValueError("Freeze already exists; refusing overwrite")
    validate_protocol(load(PAPER / "protocol" / "protocol.json"))
    validate_sources()
    preserved_papers()
    write_json(PAPER / "environment" / "environment.json", environment())
    write_json(LOCK, {"frozen_at_utc": now(), "revision": 1, "holdout_accessed": False,
                      "repository": {"base_commit": git("rev-parse", "HEAD"), "base_tree": git("rev-parse", "HEAD^{tree}"), "branch": git("branch", "--show-current")},
                      "sha256": {name: sha(PAPER / name) for name in FROZEN_INPUTS}})


def verify() -> dict:
    lock = load(LOCK)
    if set(lock["sha256"]) != set(FROZEN_INPUTS) or lock["holdout_accessed"] is not False:
        raise ValueError("Invalid frozen input inventory or holdout flag")
    verify_hashes(PAPER, lock["sha256"])
    validate_protocol(load(PAPER / "protocol" / "protocol.json"))
    qc = validate_sources()
    preserved_papers()
    current = environment()
    frozen_env = load(PAPER / "environment" / "environment.json")
    if json.loads(json.dumps(current)) != frozen_env:
        raise ValueError("Environment differs from frozen environment; disclose before reproducing")
    qc.update({"freeze_sha256": sha(LOCK), "frozen_input_count": len(FROZEN_INPUTS), "papers_1_to_10_unchanged": True,
               "primary_bin_ms": 100, "actual_trial_split_manifest": "NOT_CREATED_M1_METADATA_REQUIRED"})
    return qc


def execute() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    start = now()
    errors = []
    qc = {}
    try:
        qc = verify()
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(PAPER / "tests"), "-v"], cwd=ROOT, capture_output=True, text=True)
    (RESULTS / "tests.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
    if run.returncode:
        errors.append("Automated tests failed; see tests.txt")
    passed = not errors
    write_json(RESULTS / "qc_report.json", {"scope": "M0 protocol/environment/provenance QC only", "checks": qc, "errors": errors})
    write_json(RESULTS / "claim_audit.json", {"engineering_gate": "PASS" if passed else "FAIL", "scientific_verdict": None,
        "eligible_subject_coverage": "NOT_ASSESSED", "model_comparison": "NOT_RUN", "holdout_accessed": False,
        "nap_validated": False, "cwp_validated": False, "allowed_claim": "M0 metadata and protocol freeze verified" if passed else "M0 incomplete",
        "previous_evidence_boundary": "P10 global result does not rule out local hippocampal discrete or hybrid models"})
    gate = {"milestone": "M0", "gate": "PASS" if passed else "FAIL", "started_at_utc": start, "finished_at_utc": now(),
            "candidate_commit": git("rev-parse", "HEAD"), "candidate_source_identity": load(LOCK)["sha256"] if LOCK.exists() else {},
            "freeze_sha256": sha(LOCK) if LOCK.exists() else None, "tests_exit_code": run.returncode,
            "errors": errors, "scope": "engineering/protocol gate, not scientific outcome", "preceding_gates": [], "next_milestone_executed": False,
            "evidence": ["paper11/results/M0/tests.txt", "paper11/results/M0/qc_report.json", "paper11/results/M0/claim_audit.json"]}
    write_json(RESULTS / "gate_result.json", gate)
    status = ["# P11 Milestone Status", "", "P11 - Hippocampal Dynamical Regime", "", "| Milestone | Status | Evidence |", "| --- | --- | --- |",
              f"| M0 | {'PASS' if passed else 'FAIL'} | [gate](results/M0/gate_result.json), [QC](results/M0/qc_report.json), [tests](results/M0/tests.txt) |"]
    status += [f"| M{i} | NOT_STARTED | Requires preceding gate; not executed |" for i in range(1, 8)]
    status += ["", "Scientific verdict: NOT_EVALUATED (not a final scientific verdict).", "Eligible hippocampal coverage: NOT_ASSESSED; M1 required.",
               "No spikes, features, models or heldout outcomes were analyzed in M0.", "Stop after M0. A separate authorized execution is required for M1.", "", "See [reproduction](REPRODUCE_M0.md)."]
    (PAPER / "MILESTONE_STATUS.md").write_text("\n".join(status) + "\n", encoding="utf-8")
    print(json.dumps(gate, indent=2))
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire-metadata", action="store_true")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error("Select --acquire-metadata, --freeze or --verify")
    if args.acquire_metadata:
        acquire_metadata()
    if args.freeze:
        freeze()
    return execute() if args.verify else 0


if __name__ == "__main__":
    raise SystemExit(main())
