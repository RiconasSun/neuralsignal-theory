"""M1 only: pinned progressive acquisition, anatomy/alignment and train-only QC."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import run_m0 as m0

PAPER, ROOT = m0.PAPER, m0.ROOT
DATA = PAPER / "raw" / "M1"
MANIFEST = PAPER / "data_manifest" / "M1"
RESULTS = PAPER / "results" / "M1"
SPLIT = MANIFEST / "trial_splits.json"
SPLIT_LOCK = MANIFEST / "split_lock.json"
RECEIPTS = MANIFEST / "acquisition_receipts.json"
DATASETS = {"nm000363": ("nemarDatasets", m0.NM), "ds004752": ("OpenNeuroDatasets", m0.DS)}


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def prerequisite():
    m0.verify()
    gate = m0.load(m0.RESULTS / "gate_result.json")
    if gate["gate"] != "PASS" or gate["tests_exit_code"] != 0 or gate["freeze_sha256"] != digest(m0.LOCK):
        raise ValueError("M0 prerequisite failed")
    if gate["candidate_source_identity"] != m0.load(m0.LOCK)["sha256"]:
        raise ValueError("M0 evidence source identity mismatch")


def rows(path):
    # Companion TSV uses CRCRLF; universal newline handling preserves fields.
    with path.open(encoding="utf-8-sig", newline=None) as handle:
        return list(csv.DictReader(handle, delimiter="," if path.suffix == ".csv" else "\t"))


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Nonfinite numeric value")
    return result


def integer(value):
    result = number(value)
    if result != int(result):
        raise ValueError("Noninteger identity")
    return int(result)


def anatomy(label):
    lower = label.lower()
    hippocampus = bool(re.search(r"\b(?:hipp|[rc]hipp|hippocampus|hippocampal)\b", lower))
    other = [name for name, pattern in (("entorhinal", r"entorhinal|\bent\b"), ("amygdala", r"amyg|\bamy\b"), ("parahippocampal", r"parahipp|\bphg\b"), ("fusiform", r"fusiform|\bfug\b")) if re.search(pattern, lower)]
    region = "ambiguous" if hippocampus and other else "hippocampus" if hippocampus else other[0] if len(other) == 1 else "unknown"
    left, right = bool(re.search(r"\bleft\b", lower)), bool(re.search(r"\bright\b", lower))
    hemisphere = "left" if left and not right else "right" if right and not left else "unknown"
    return region, hemisphere


def fetch(url):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "NSI-P11-M1-pinned-audit"})
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read(32 * 1024 * 1024 + 1)
                if len(content) > 32 * 1024 * 1024:
                    raise ValueError("Per-file acquisition limit exceeded")
                return content, response.status
        except OSError:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def tree(dataset, acquire):
    owner, commit = DATASETS[dataset]
    path = MANIFEST / "repository_trees" / f"{dataset}.json"
    if not path.exists():
        if not acquire:
            raise ValueError(f"Missing pinned tree: {dataset}; run --acquire")
        content, _ = fetch(f"https://api.github.com/repos/{owner}/{dataset}/git/trees/{commit}?recursive=1")
        parsed = json.loads(content)
        if parsed.get("truncated") or not parsed.get("sha"):
            raise ValueError("Incomplete repository tree")
        write_json(path, {"dataset": dataset, "commit": commit, "retrieved_at_utc": now(), "response": parsed})
    result = m0.load(path)
    if result["commit"] != commit or result["response"]["truncated"]:
        raise ValueError("Repository tree pin mismatch")
    return {entry["path"]: entry for entry in result["response"]["tree"] if entry["type"] == "blob"}


def download(dataset, path, entries, acquire):
    if path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("Unsafe dataset path")
    entry = entries[path]
    if entry["mode"] != "100644":
        raise ValueError(f"Unresolved annex/pointer path: {path}")
    destination = DATA / dataset / path
    owner, commit = DATASETS[dataset]
    url = f"https://raw.githubusercontent.com/{owner}/{dataset}/{commit}/{path}"
    if destination.exists():
        content = destination.read_bytes()
        if blob_sha(content) != entry["sha"]:
            raise ValueError(f"Cached content corrupted: {dataset}/{path}")
        receipt = {"dataset": dataset, "version_commit": commit, "path": path, "url": url, "bytes": len(content), "sha256": digest(destination), "git_blob_sha": entry["sha"], "content_verified": True}
        return receipt
    if not acquire:
        raise ValueError(f"Missing raw file: {dataset}/{path}; run --acquire")
    content, status = fetch(url)
    if blob_sha(content) != entry["sha"]:
        raise ValueError(f"Downloaded content not equal to pinned Git blob: {path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return {"dataset": dataset, "version_commit": commit, "path": path, "url": url, "http_status": status, "retrieved_at_utc": now(), "bytes": len(content), "sha256": digest(destination), "git_blob_sha": entry["sha"], "content_verified": True}


def session_key(path):
    match = re.match(r"(sub-\d+)/(ses-\d+)/", path)
    return "/".join(match.groups()) if match else None


def aligned_trial(trial, event):
    expected = {"set_size": ("SetSize", integer), "probe_letter": ("ProbeLetter", str), "correct": ("Correct", integer), "artifact": ("Artifact", integer)}
    for left, (right, convert) in expected.items():
        if convert(trial[left]) != convert(event[right]):
            return False
    if {1: "IN", 2: "OUT"}.get(integer(trial["match"])) != event["Match"]:
        return False
    return math.isclose(number(trial["response_time"]), number(event["ResponseTime"]), abs_tol=1e-6)


def trial_audit(trials, trialevents, companion):
    ids = [integer(row["trial"]) for row in trials]
    if min(ids, default=0) < 1 or len(ids) != len(set(ids)):
        raise ValueError("Duplicate or invalid trial ID")
    phase = defaultdict(dict)
    phase_names = {"Fixation": (-6.0, 1.0), "Stimulus": (-5.0, 2.0), "Maintenance": (-3.0, 3.0), "Probe": (0.0, None)}
    for row in trialevents:
        tid = integer(row["trial"])
        if tid not in ids:
            raise ValueError("Event references absent trial")
        name = row["nix_event"].split("_")[0]
        if name in phase_names:
            if name in phase[tid]:
                raise ValueError("Duplicate trial phase")
            phase[tid][name] = row
    events = {}
    if companion is not None:
        for event in companion:
            tid = integer(event["nTrial"])
            if tid in events or tid not in ids:
                raise ValueError("Companion trial ID mismatch")
            if number(event["onset"]) < 0 or number(event["duration"]) < 6:
                raise ValueError("Companion observation coverage invalid")
            events[tid] = event
        if set(events) != set(ids):
            raise ValueError("Companion trial roster differs")
    valid, exclusions = [], []
    for row in trials:
        tid = integer(row["trial"])
        reasons = []
        if companion is not None and not aligned_trial(row, events[tid]):
            raise ValueError(f"Companion task/trial alignment failed: {tid}")
        try:
            if integer(row["artifact"]) != 0:
                reasons.append("artifact_flag")
            if integer(row["set_size"]) not in (4, 6, 8) or integer(row["match"]) not in (1, 2):
                reasons.append("invalid_task_metadata")
            if number(row["response_time"]) < 0:
                reasons.append("invalid_response_time")
            for name, (onset, duration) in phase_names.items():
                event = phase[tid][name]
                if not math.isclose(number(event["onset"]), onset, abs_tol=1e-6) or (duration is not None and not math.isclose(number(event["duration"]), duration, abs_tol=1e-6)):
                    reasons.append("invalid_trial_epoch")
        except (ValueError, KeyError):
            reasons.append("missing_or_nonfinite_trial_metadata")
        if reasons:
            exclusions.append({"trial": tid, "reasons": sorted(set(reasons))})
        else:
            valid.append(tid)
    return {"total_trials": len(trials), "valid_trials": sorted(valid), "excluded_trials": exclusions,
            "alignment": "PAIRED_VERIFIED" if companion is not None else "UNPAIRED", "paired_trials_checked": len(events)}


def freeze_splits(sessions, input_hashes):
    prospective = {"m0_freeze_sha256": digest(m0.LOCK), "algorithm": "M0 chronological whole-trial 60/20/20", "sessions": sessions}
    if SPLIT_LOCK.exists():
        lock = m0.load(SPLIT_LOCK)
        if digest(SPLIT) != lock["split_sha256"] or lock["metadata_sha256"] != input_hashes or m0.load(SPLIT) != prospective:
            raise ValueError("Frozen split/metadata differs; refusing to overwrite holdouts")
        return lock
    if SPLIT.exists():
        raise ValueError("Unsealed split already exists; investigate before overwriting")
    write_json(SPLIT, prospective)
    lock = {"frozen_at_utc": now(), "split_sha256": digest(SPLIT), "metadata_sha256": input_hashes,
            "protocol_sha256": digest(PAPER / "protocol" / "protocol.json"), "spike_counts_inspected_at_freeze": False}
    write_json(SPLIT_LOCK, lock)
    return lock


def train_spike_qc(path, train_ids, all_ids, hippocampal_units):
    counts, invalid, rows_seen = Counter(), set(), 0
    with path.open(encoding="utf-8-sig", newline=None) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != ["unit_id", "trial", "spike_time"]:
            raise ValueError("Unexpected spike TSV schema")
        for row in reader:
            tid = integer(row["trial"])
            if tid not in all_ids:
                raise ValueError("Spike refers to missing trial")
            # Heldout timestamp and unit columns are not decoded or used for QC.
            if tid not in train_ids:
                continue
            uid = integer(row["unit_id"])
            if uid not in hippocampal_units:
                continue
            rows_seen += 1
            try:
                spike = number(row["spike_time"])
                if spike < -6 or spike > 2:
                    invalid.add(uid)
                if -6 <= spike < 0:
                    counts[uid] += 1
            except ValueError:
                invalid.add(uid)
    return counts, invalid, rows_seen


def csv_output(name, records):
    path = RESULTS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]) if records else ["empty"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def session_eligible(valid_trials, eligible_units):
    protocol = m0.load(PAPER / "protocol" / "protocol.json")
    return (valid_trials >= protocol["eligibility"]["minimum_valid_trials_per_session"]
            and eligible_units >= protocol["eligibility"]["minimum_train_selected_hippocampal_units"])


def coverage_sufficient(eligible_subjects):
    return eligible_subjects >= m0.load(PAPER / "protocol" / "protocol.json")["eligibility"]["minimum_subjects_for_confirmatory_comparison"]


def pipeline(acquire):
    prerequisite()
    nm, ds = tree("nm000363", acquire), tree("ds004752", acquire)
    previous_receipts = m0.load(RECEIPTS).get("files", []) if RECEIPTS.exists() else []
    receipts = {(r["dataset"], r["path"]): r for r in previous_receipts}
    def get_many(items):
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda item: download(item[0], item[1], nm if item[0] == "nm000363" else ds, acquire), items))
        for receipt in results:
            key = receipt["dataset"], receipt["path"]
            if key in receipts and receipts[key]["sha256"] != receipt["sha256"]:
                raise ValueError("Previously acquired file changed")
            if key not in receipts:
                receipts[key] = receipt
        write_json(RECEIPTS, {"datasets": {d: {"owner": owner, "commit": commit} for d, (owner, commit) in DATASETS.items()}, "files": [receipts[k] for k in sorted(receipts)]})
    metadata_paths = [p for p in nm if p.endswith(("_trials.tsv", "_trialevents.tsv", "_units.tsv", "_sessions.tsv")) or p in ("task-verbalWM_units.json", "task-verbalWM_trials.json", "task-verbalWM_trialevents.json", "task-verbalWM_spikes.json", "LICENSE", "code/source_provenance.json")]
    pilot = [p for p in metadata_paths if p.startswith("sub-01/ses-01/")]
    get_many([("nm000363", p) for p in pilot])
    print("M1 pilot metadata acquired and pinned blob hashes verified", flush=True)
    companion_paths = [p for p in ds if re.match(r"sub-0[1-9]/ses-\d+/ieeg/", p) and p.endswith(("_events.tsv", "_electrodes.tsv"))]
    get_many([("nm000363", p) for p in metadata_paths] + [("ds004752", p) for p in companion_paths])
    audits, splits, all_units = {}, {}, {}
    raw_metadata = [DATA / r["dataset"] / r["path"] for r in receipts.values() if not r["path"].endswith("_spikes.tsv")]
    for trial_path in sorted(p for p in metadata_paths if p.endswith("_trials.tsv")):
        key = session_key(trial_path)
        stem = trial_path[:-len("trials.tsv")]
        trials = rows(DATA / "nm000363" / trial_path)
        events = rows(DATA / "nm000363" / (stem + "trialevents.tsv"))
        companion_files = [p for p in companion_paths if session_key(p) == key and p.endswith("_events.tsv")]
        if len(companion_files) > 1:
            raise ValueError("Multiple companion runs need explicit crosswalk")
        companion = rows(DATA / "ds004752" / companion_files[0]) if companion_files else None
        audits[key] = trial_audit(trials, events, companion)
        valid = audits[key]["valid_trials"]
        partitions = m0.chronological_split(valid) if len(valid) >= 40 else {"train": [], "validation": [], "test": []}
        splits[key] = {"subject": key.split("/")[0], "session": key.split("/")[1], "partitions": partitions,
                       "valid_trials": valid, "excluded_trials": audits[key]["excluded_trials"], "alignment": audits[key]["alignment"]}
        all_units[key] = rows(DATA / "nm000363" / (stem + "units.tsv")) if stem + "units.tsv" in nm else []
    hashes = {p.relative_to(PAPER).as_posix(): digest(p) for p in raw_metadata}
    hashes.update({p.relative_to(PAPER).as_posix(): digest(p) for p in (MANIFEST / "repository_trees").glob("*.json")})
    lock = freeze_splits(splits, hashes)
    print(f"M1 actual metadata trial splits frozen: {len(splits)} sessions; no spike timestamps parsed", flush=True)
    unit_report, session_report = [], []
    for key, unit_rows in sorted(all_units.items()):
        ids = [integer(u["unit_id"]) for u in unit_rows]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate session-local unit ID")
        hip = {integer(u["unit_id"]) for u in unit_rows if anatomy(u["anatomical_location"])[0] == "hippocampus"}
        split = splits[key]["partitions"]
        spikes = [p for p in nm if session_key(p) == key and p.endswith("_spikes.tsv")]
        if bool(unit_rows) != bool(spikes) or len(spikes) > 1:
            raise ValueError("Unit/spike file availability mismatch")
        counts, invalid, rows_seen = Counter(), set(), 0
        if spikes:
            get_many([("nm000363", spikes[0])])
            counts, invalid, rows_seen = train_spike_qc(DATA / "nm000363" / spikes[0], set(split["train"]), {integer(t["trial"]) for t in rows(DATA / "nm000363" / next(p for p in metadata_paths if session_key(p) == key and p.endswith("_trials.tsv")))}, hip)
        electrodes_paths = [p for p in companion_paths if session_key(p) == key and p.endswith("_electrodes.tsv")]
        electrodes = {r["name"]: r for r in rows(DATA / "ds004752" / electrodes_paths[0])} if electrodes_paths else {}
        eligible = 0
        for unit in unit_rows:
            uid = integer(unit["unit_id"])
            region, hemisphere = anatomy(unit["anatomical_location"])
            reasons = []
            if region != "hippocampus":
                reasons.append("nonhippocampal_or_ambiguous_anatomy")
            if hemisphere == "unknown":
                reasons.append("hemisphere_unresolved")
            try:
                xyz = [number(unit[f"macro_contact_mni_{axis}"]) for axis in ("x", "y", "z")]
            except ValueError:
                xyz = []
                reasons.append("invalid_coordinates")
            full_coverage = integer(unit["n_trials_with_spike_array"]) == audits[key]["total_trials"]
            if not full_coverage:
                reasons.append("observation_array_coverage_incomplete")
            electrode = electrodes.get(unit["macro_contact"])
            mapping = "UNPAIRED" if not electrodes else "CONTACT_MISSING" if electrode is None else "VERIFIED"
            if electrode is not None and (anatomy(electrode["AnatomicalLocation"]) != (region, hemisphere) or (xyz and any(not math.isclose(a, number(electrode[axis]), abs_tol=1e-6) for a, axis in zip(xyz, ("x", "y", "z"))))):
                mapping = "DISAGREEMENT"
                reasons.append("companion_anatomy_disagreement")
            if mapping == "CONTACT_MISSING":
                reasons.append("companion_contact_missing")
            if uid in invalid:
                reasons.append("invalid_training_timestamps")
            if region == "hippocampus" and counts[uid] < 20:
                reasons.append("training_epoch_spikes_below_20")
            ok = not reasons and len(split["train"]) > 0
            eligible += int(ok)
            unit_report.append({"subject": key.split("/")[0], "session": key.split("/")[1], "unit_id": uid,
                "macro_contact": unit["macro_contact"], "anatomical_label": unit["anatomical_location"], "region": region, "hemisphere": hemisphere,
                "unit_type": "SU_MU_NOT_DISTINGUISHED", "companion_electrode_mapping": mapping,
                "full_observation_array_coverage": full_coverage, "training_preprobe_spikes": counts[uid] if region == "hippocampus" else "NOT_ASSESSED",
                "eligible": ok, "exclusion_reasons": ";".join(reasons)})
        is_eligible = session_eligible(len(audits[key]["valid_trials"]), eligible)
        for record in unit_report:
            if record["subject"] + "/" + record["session"] == key:
                record["primary_analysis_eligible"] = record["eligible"] and is_eligible
        session_report.append({"subject": key.split("/")[0], "session": key.split("/")[1], "total_trials": audits[key]["total_trials"],
            "valid_trials": len(audits[key]["valid_trials"]), "train_trials": len(split["train"]), "validation_trials": len(split["validation"]), "test_trials": len(split["test"]),
            "sorted_units": len(unit_rows), "hippocampal_units": len(hip), "eligible_hippocampal_units": eligible,
            "alignment": audits[key]["alignment"], "training_hippocampal_rows_parsed": rows_seen, "eligible": is_eligible})
        print(f"M1 {key}: {eligible} eligible hippocampal units; {len(audits[key]['valid_trials'])} valid trials; {audits[key]['alignment']}", flush=True)
    # Reverify the metadata lock after signal acquisition/QC; never rewrite it.
    freeze_splits(splits, hashes)
    subjects = sorted({r["subject"] for r in session_report})
    subject_report = [{"subject": s, "sessions": sum(r["subject"] == s for r in session_report),
                       "eligible_sessions": sum(r["subject"] == s and r["eligible"] for r in session_report),
                       "eligible": any(r["subject"] == s and r["eligible"] for r in session_report)} for s in subjects]
    csv_output("unit_qc.csv", unit_report)
    csv_output("session_qc.csv", session_report)
    csv_output("subject_coverage.csv", subject_report)
    write_json(RESULTS / "trial_alignment_qc.json", audits)
    license_bytes = (DATA / "nm000363" / "LICENSE").read_bytes()
    (RESULTS / "DERIVED_DATA_LICENSE.txt").write_bytes(license_bytes)
    return {"subjects_audited": len(subjects), "eligible_subjects": sum(r["eligible"] for r in subject_report),
            "sessions_audited": len(session_report), "eligible_sessions": sum(r["eligible"] for r in session_report),
            "sorted_units_audited": len(unit_report), "unit_qc_passing_hippocampal_units": sum(r["eligible"] for r in unit_report),
            "primary_analysis_eligible_hippocampal_units": sum(r["primary_analysis_eligible"] for r in unit_report),
            "anatomical_regions": dict(Counter(r["region"] for r in unit_report)),
            "paired_sessions": sum(r["alignment"] == "PAIRED_VERIFIED" for r in session_report),
            "unpaired_sessions": [r["subject"] + "/" + r["session"] for r in session_report if r["alignment"] == "UNPAIRED"],
            "downloaded_files": len(receipts), "downloaded_bytes": sum(r["bytes"] for r in receipts.values()),
            "split_sha256": lock["split_sha256"], "holdout_timestamps_parsed": False,
            "unit_type_limitations": "SU/MU unlabelled upstream; sorted units only", "external_test": "NOT_EXECUTED_M6"}


def execute(acquire):
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = now()
    errors, qc = [], {}
    try:
        qc = pipeline(acquire)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(PAPER / "tests"), "-p", "test_m1.py", "-v"], cwd=ROOT, text=True, capture_output=True)
    (RESULTS / "tests.txt").write_text(run.stdout + run.stderr, encoding="utf-8", newline="\n")
    if run.returncode:
        errors.append("M1 automated tests failed")
    insufficient = not errors and not coverage_sufficient(qc["eligible_subjects"])
    gate = "FAIL" if errors else "DATA_INSUFFICIENT" if insufficient else "PASS"
    source = {p.relative_to(PAPER).as_posix(): digest(p) for p in [Path(__file__), PAPER / "tests" / "test_m1.py", PAPER / "scripts" / "reproduce-m1.ps1", PAPER / "REPRODUCE_M1.md"]}
    write_json(RESULTS / "qc_report.json", {"scope": "real acquisition/anatomy/alignment and training-only eligibility; no model findings", "summary": qc, "errors": errors})
    write_json(RESULTS / "claim_audit.json", {"milestone": "M1", "gate": gate, "scientific_verdict": "DATA_INSUFFICIENT" if insufficient else None,
        "regime_preference": "NOT_TESTED", "nap_validated": False, "cwp_validated": False, "external_convergence": "NOT_TESTED",
        "holdout_timestamps_parsed": False, "limitations": ["SU/MU unresolved upstream", "epilepsy clinical sample", "unit identity session-local", "upstream sorting was session-wide"],
        "eligible_subjects": qc.get("eligible_subjects"), "allowed_claim": "observed dataset eligibility/QC only; no dynamical regime conclusion"})
    result = {"milestone": "M1", "gate": gate, "started_at_utc": started, "finished_at_utc": now(), "candidate_commit": m0.git("rev-parse", "HEAD"),
        "preceding_gates": {"M0": "PASS"} if not errors or qc else {"M0": "see errors"}, "m0_freeze_sha256": digest(m0.LOCK),
        "source_sha256": source, "split_sha256": qc.get("split_sha256"), "tests_exit_code": run.returncode, "errors": errors,
        "next_milestone_executed": False, "evidence": ["paper11/results/M1/qc_report.json", "paper11/results/M1/tests.txt", "paper11/results/M1/unit_qc.csv", "paper11/results/M1/session_qc.csv", "paper11/results/M1/subject_coverage.csv", "paper11/results/M1/claim_audit.json"]}
    write_json(RESULTS / "gate_result.json", result)
    status = ["# P11 Milestone Status", "", "P11 - Hippocampal Dynamical Regime", "", "| Milestone | Status | Evidence |", "| --- | --- | --- |",
        "| M0 | PASS | [frozen gate](results/M0/gate_result.json), unchanged |", f"| M1 | {gate} | [gate](results/M1/gate_result.json), [QC](results/M1/qc_report.json), [tests](results/M1/tests.txt) |"]
    status += [f"| M{i} | NOT_STARTED | Requires preceding gate and separate execution |" for i in range(2, 8)]
    status += ["", f"Eligible subjects: {qc.get('eligible_subjects', 'unresolved')}; no model comparison performed.", "Scientific verdict: " + ("DATA_INSUFFICIENT" if insufficient else "NOT_EVALUATED"),
        "M0 protocol and frozen holdouts unchanged. Stop after M1.", "See [reproduction](REPRODUCE_M1.md)."]
    (PAPER / "MILESTONE_STATUS.md").write_text("\n".join(status) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"milestone": "M1", "gate": gate, "qc": qc, "errors": errors, "tests_exit_code": run.returncode}, indent=2), flush=True)
    return 0 if gate == "PASS" else 2 if insufficient else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire", action="store_true", help="Get only pinned M1 files progressively; cached bytes verified")
    args = parser.parse_args()
    raise SystemExit(execute(args.acquire))
