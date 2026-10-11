"""Prospective, metadata-only registration and fail-closed external audit."""
import argparse
import hashlib
import io
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "paper11_v2"
OUT = STUDY / "results" / "R0"
API = "https://api.dandiarchive.org/api"
VERSION = "0.220126.1852"
ALLOWED = {
    "units/id", "units/electrodes", "units/electrodes_index",
    "general/extracellular_ephys/electrodes/location",
    "intervals/trials/start_time", "intervals/trials/stop_time",
    "intervals/trials/stim_phase",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj, immutable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    if immutable and path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(f"Immutable artifact already exists: {path}")
        return
    path.write_bytes(data)


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def archive_inventory():
    paths = git("ls-files", "-z").split("\0")
    return {p: digest(ROOT / p) for p in paths if re.match(r"paper(?:[1-9]|10|11)/", p)}


def register():
    target = OUT / "registration.json"
    if target.exists():
        verify_registration()
        print("Existing prospective registration verified; no overwrite.")
        return
    protocol = json.loads((STUDY / "protocol/protocol.json").read_text())
    if protocol["archive"]["v1_failures_final"] is not True:
        raise RuntimeError("Archive must remain final")
    inputs = [STUDY / "protocol/protocol.json", Path(__file__),
              STUDY / "tests/test_r0.py", STUDY / "scripts/reproduce-r0.ps1",
              ROOT / "paper11/data_manifest/M1/trial_splits.json"]
    save(target, {
        "study": "P11-v2", "milestone": "R0", "registered_utc": datetime.now(timezone.utc).isoformat(),
        "base_commit": git("rev-parse", "HEAD"),
        "input_sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in inputs},
        "archive_sha256": archive_inventory(),
        "prior_public_metadata_access": "Dataset version/asset JSON and publication schema queried before registration; no NWB physiological values or prediction outcomes accessed.",
        "no_final_neural_access": True,
        "trial_rule": "Finite start/stop, stop>start; next chronological trial onset >=start+1s. Stimulus offset is not recording stop. Physiological recording coverage is a later train-only QC gate.",
        "range_policy": "HTTP206 only; <=8MiB individual read, <=12MiB fetched per asset; only allowlisted HDF dataset values decoded. Adjacent uninterpreted transport bytes may be buffered.",
        "missing_schema_policy": "Do not infer hippocampus or silently substitute metadata. Missing schema stops external gate.",
        "source_independence": "Published cohort/site disjoint from Zurich; cannot certify private reidentification; related companion sources excluded.",
        "candidate_gate": {"minimum_subjects": 8, "minimum_units": 5, "minimum_trials": 40},
    }, immutable=True)
    print(f"REGISTERED {target}; sha256={digest(target)}")


def verify_registration():
    obj = json.loads((OUT / "registration.json").read_text())
    for rel, sha in obj["input_sha256"].items():
        if digest(ROOT / rel) != sha:
            raise RuntimeError(f"Registered input changed: {rel}")
    if archive_inventory() != obj["archive_sha256"]:
        raise RuntimeError("Archived paper content changed")
    return obj


class RangeReader(io.RawIOBase):
    """Bounded public HTTP random access; never accept a whole-file fallback."""
    def __init__(self, url, size, session):
        self.url, self.size, self.session = url, size, session
        self.pos, self.fetched = 0, 0
        self.blocks = {}
        self.receipts = []

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        new = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        if new < 0:
            raise ValueError("Negative seek")
        self.pos = new
        return new

    def readinto(self, buf):
        data = self.read(len(buf))
        buf[:len(data)] = data
        return len(data)

    def read(self, n=-1):
        if n < 0 or n > 8 * 1024 * 1024:
            raise RuntimeError("Unbounded HDF read prohibited")
        end = min(self.pos + n, self.size)
        if end <= self.pos:
            return b""
        pieces = []
        while self.pos < end:
            base = (self.pos // 65536) * 65536
            stop = min(base + 65536, self.size) - 1
            if base not in self.blocks:
                if self.fetched + stop - base + 1 > 12 * 1024 * 1024:
                    raise RuntimeError("Metadata-only transport budget exceeded")
                response = self.session.get(self.url, headers={"Range": f"bytes={base}-{stop}", "Accept-Encoding": "identity"}, timeout=90, stream=True)
                try:
                    expected = f"bytes {base}-{stop}/{self.size}"
                    if response.status_code != 206 or response.headers.get("Content-Range") != expected:
                        raise RuntimeError(f"Range response rejected: {response.status_code}, {response.headers.get('Content-Range')}; expected {expected}")
                    data = response.raw.read(stop - base + 2)
                    if len(data) != stop - base + 1:
                        raise RuntimeError("Range size mismatch")
                finally:
                    response.close()
                self.blocks[base] = data
                self.fetched += len(data)
                self.receipts.append({"start": base, "stop": stop, "sha256": hashlib.sha256(data).hexdigest()})
            count = min(end - self.pos, stop + 1 - self.pos)
            pieces.append(self.blocks[base][self.pos - base:self.pos - base + count])
            self.pos += count
        return b"".join(pieces)


def decode(x):
    return x.decode("utf-8") if isinstance(x, bytes) else str(x)


def permitted_read(file, path, ledger):
    if path not in ALLOWED:
        raise RuntimeError(f"Forbidden metadata path: {path}")
    ledger.append(path)
    return file[path][...]


def hippocampal_locations(locations):
    result = []
    for x in locations:
        label = decode(x).strip()
        # Abbreviations require explicit published mapping; unknown is not hippocampus.
        result.append(bool(re.search(r"\bhippocamp(?:us|al)\b", label, re.I)))
    return result


def summarize_metadata(file, ledger):
    ids = permitted_read(file, "units/id", ledger)
    refs = permitted_read(file, "units/electrodes", ledger)
    locations = permitted_read(file, "general/extracellular_ephys/electrodes/location", ledger)
    hip = hippocampal_locations(locations)
    if "units/electrodes_index" in file:
        ends = permitted_read(file, "units/electrodes_index", ledger)
        if len(ends) != len(ids):
            raise RuntimeError("Unit-electrode ragged mapping mismatch")
        starts = [0] + list(ends[:-1])
        rows = [refs[int(a):int(b)] for a, b in zip(starts, ends)]
    else:
        if len(refs) != len(ids):
            raise RuntimeError("Unit-electrode mapping mismatch")
        rows = [[r] for r in refs]
    selected = []
    for uid, row in zip(ids, rows):
        if len(row) and all(0 <= int(r) < len(hip) and hip[int(r)] for r in row):
            selected.append({"unit_id": int(uid), "electrode_rows": [int(r) for r in row], "locations": [decode(locations[int(r)]) for r in row]})
    starts = permitted_read(file, "intervals/trials/start_time", ledger)
    stops = permitted_read(file, "intervals/trials/stop_time", ledger)
    phases = permitted_read(file, "intervals/trials/stim_phase", ledger)
    if not len(starts) == len(stops) == len(phases):
        raise RuntimeError("Trial metadata lengths differ")
    valid = []
    for i, (a, b, phase) in enumerate(zip(starts, stops, phases)):
        if decode(phase).strip().lower() != "recognition":
            continue
        if math.isfinite(float(a)) and math.isfinite(float(b)) and b > a and (i + 1 == len(starts) or starts[i + 1] >= a + 1):
            valid.append({"row": i, "start": float(a), "stimulus_stop": float(b)})
    ntrain = math.floor(.6 * len(valid))
    return {"hippocampal_units": selected, "electrode_location_labels": sorted(set(map(decode, locations))),
            "phase_labels": sorted(set(map(decode, phases))), "valid_recognition_trials": valid,
            "calibration_train_rows": [x["row"] for x in valid[:ntrain]],
            "locked_final_rows": [x["row"] for x in valid[ntrain:]],
            "metadata_candidate": len(selected) >= 5 and len(valid) >= 40}


def canonical_patient(path):
    subject = path.split("/")[0]
    if not re.fullmatch(r"sub-P\d+(?:HMH|CS|TWH)(?:_\d+)?", subject):
        raise RuntimeError(f"Unregistered patient alias pattern: {subject}")
    return re.sub(r"_\d+$", "", subject)


def exposure_audit():
    matches = []
    # Enumerate tracked evidence text only; never open raw physiological files.
    for rel in git("ls-files", "-z").split("\0"):
        p = ROOT / rel
        if p.suffix.lower() not in {".md", ".json", ".py", ".ps1", ".tsv", ".toml", ".txt", ".yaml", ".yml"} or not p.exists():
            continue
        if p.stat().st_size > 4 * 1024 * 1024 or re.search(r"(?:raw|cache|counts|spikes|features)[/\\]", rel):
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        if re.search(r"DANDI|000004|nm000363|ds004752", content, re.I):
            matches.append({"path": rel, "sha256": digest(p), "external_mentions": [line[:1000] for line in content.splitlines() if re.search(r"DANDI|000004", line, re.I)][:40]})
    splits = json.loads((ROOT / "paper11/data_manifest/M1/trial_splits.json").read_text())
    gates = []
    for p in sorted((ROOT / "paper11/results").glob("**/gate_result.json")):
        gates.append({"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(p), "evidence": json.loads(p.read_text())})
    obj = {"tracked_text_inventory": matches, "archived_gate_inventory": gates,
           "old_final_test_forbidden": {s: v["partitions"]["test"] for s, v in splits["sessions"].items()},
           "development_exposure": "Repeated v1 training/validation scoring, numerical design and selection; development is exploratory, never pristine.",
           "external_exposure": "Prior v1 metadata compatibility planning only per gate receipts; no physiological DANDI acquisition found. R0 new access is metadata only. Cannot certify private human prior knowledge beyond repository evidence.",
           "same_cohort": "nm000363/ds004752/GIN d76994 share Zurich primary patients; cannot be independent validation.",
           "sites_reference": "https://www.nature.com/articles/s41597-020-0415-9",
           "external_sites": ["Cedars-Sinai Medical Center", "Huntington Memorial Hospital", "Toronto Western Hospital"],
           "primary_site": "Schweizerisches Epilepsie-Zentrum, Zurich", "private_identity_certified": False}
    save(OUT / "exposure_audit.json", obj, immutable=True)
    return obj


def request_json(session, url):
    response = session.get(url, headers={"Accept": "application/json"}, timeout=90)
    response.raise_for_status()
    return response.json()


def acquire():
    verify_registration()
    import h5py
    import requests
    session = requests.Session()
    meta = OUT / "metadata"
    release = request_json(session, f"{API}/dandisets/000004/versions/{VERSION}/")
    if release.get("version") != VERSION:
        raise RuntimeError("Version mismatch")
    save(meta / "release.json", release, immutable=True)
    listing = request_json(session, f"{API}/dandisets/000004/versions/{VERSION}/assets/?page_size=100")
    if listing["next"] is not None or listing["count"] != len(listing["results"]):
        raise RuntimeError("Incomplete release asset roster")
    save(meta / "asset_roster.json", listing, immutable=True)
    for asset in sorted(listing["results"], key=lambda a: a["path"]):
        aid = asset["asset_id"]
        target = meta / "audits" / f"{aid}.json"
        if target.exists():
            print(f"READBACK {asset['path']}", flush=True)
            continue
        info = request_json(session, f"{API}/assets/{aid}/")
        save(meta / "assets" / f"{aid}.json", info, immutable=True)
        sha = info.get("digest", {}).get("dandi:sha2-256")
        if not sha or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise RuntimeError("Missing published SHA256")
        url = next(u for u in info["contentUrl"] if u.startswith("https://dandiarchive.s3.amazonaws.com/blobs/"))
        reader = RangeReader(url, asset["size"], session)
        ledger = []
        result = {"asset_id": aid, "path": asset["path"], "published_sha256": sha, "size": asset["size"], "patient": canonical_patient(asset["path"])}
        try:
            with h5py.File(reader, "r") as file:
                result.update(summarize_metadata(file, ledger))
            result["schema_status"] = "VERIFIED"
        except (KeyError, RuntimeError, ValueError, OSError) as exc:
            result.update({"schema_status": "FAIL", "reason": str(exc), "metadata_candidate": False})
        result.update({"decoded_paths": ledger, "range_receipts": reader.receipts, "transport_bytes": reader.fetched,
                       "neural_values_decoded": False, "whole_asset_checksum_verified": False})
        save(target, result, immutable=True)
        print(f"AUDIT {asset['path']} {result['schema_status']} units={len(result.get('hippocampal_units', []))} trials={len(result.get('valid_recognition_trials', []))}", flush=True)
        # Unexpected schema is not scientific exclusion; fail closed and preserve the exact blocker.
        if result["schema_status"] != "VERIFIED":
            break


def evaluate():
    reg = verify_registration()
    exposure_audit()
    rosterpath = OUT / "metadata/asset_roster.json"
    listing = json.loads(rosterpath.read_text()) if rosterpath.exists() else {"results": []}
    audits = [json.loads(p.read_text()) for p in sorted((OUT / "metadata/audits").glob("*.json"))]
    candidate = sorted(set(a["patient"] for a in audits if a.get("metadata_candidate")))
    missing = sorted(set(a["asset_id"] for a in listing["results"]) - set(a["asset_id"] for a in audits))
    failures = [a for a in audits if a["schema_status"] != "VERIFIED"]
    passed = bool(listing["results"]) and not missing and not failures and len(candidate) >= 8
    verdict = "PASS" if passed else "FAIL"
    report = {"study": "P11-v2", "milestone": "R0", "gate_verdict": verdict,
              "registered_at": reg["registered_utc"], "roster_assets": len(listing["results"]),
              "audited_assets": len(audits), "missing_asset_ids": missing, "schema_failures": failures,
              "metadata_candidate_subjects": candidate, "candidate_subject_count": len(candidate),
              "minimum_subjects": 8, "external_neural_access": False, "archived_v1_unchanged": True,
              "scientific_regime_verdict": "NOT_EVALUATED", "next_milestone_authorized": passed,
              "limitation": None if passed else "Independent hippocampal spiking candidate coverage has not been verified; no predictive competition or external unlock permitted.",
              "checksums": "Published whole-NWB SHA256 pinned, not verified without downloading signal data; metadata/range hashes verified separately."}
    save(OUT / "gate_result.json", report)
    save(OUT / "QC.json", report)
    if passed:
        save(OUT / "final_validation_lock.json", {"study": "P11-v2", "release": VERSION, "roster_sha256": digest(rosterpath), "eligible_sessions": [a for a in audits if a["metadata_candidate"]], "protocol_sha256": digest(STUDY / "protocol/protocol.json"), "external_neural_access": False}, immutable=True)
    print(json.dumps({k: v for k, v in report.items() if k != "schema_failures"}, indent=2))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["register", "acquire", "evaluate", "verify"])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.action == "register":
        register()
    elif args.action == "verify":
        verify_registration()
        print("Registered inputs and archived evidence unchanged.")
    elif args.action == "acquire":
        acquire()
    else:
        return evaluate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
