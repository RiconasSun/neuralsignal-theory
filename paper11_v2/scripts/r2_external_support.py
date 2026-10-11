"""Prospective endpoint-only external observation-support auditor.

No import-time I/O, network, output writes or physiological decoding. Parent
registers this source/tests and source audit before calling audit(). The parent
supplies a bounded HDF opener, ONLY after registration and prerequisite checks.
Neither support inference nor metadata unit labels establishes spike adequacy.
"""

import hashlib
import json
import math
from pathlib import Path
import re

from run_r0 import RangeReader

VERSION = "0.220126.1852"
NAMESPACE = "R2_external_support"
SOURCE_URL = "https://www.nature.com/articles/s41597-020-0415-9"
CLOCK = "seconds_relative_experiment"
PHASE = "METADATA_ONLY_PREFLIGHT"
SPIKE_PREREQUISITE = "REQUIRED_BEFORE_SPIKES"
ORDERING_PROOF = "before_spikes != before_metadata"
ALLOWED = {"acquisition/events/data": (0, -1),
           "acquisition/events/timestamps": (0, -1)}
POLICY = {"http_status": 206, "verify_content_range": True,
          "max_read_bytes": 8 * 1024 * 1024,
          "max_fetched_bytes_per_asset": 12 * 1024 * 1024,
          "hdf_links": "hard_only", "decode": "scalar_endpoints_only",
          "adjacent_bytes": "buffered_undecoded_only",
          "full_file_fallback": False, "namespace": NAMESPACE}
FILES = ("paper11_v2/scripts/r2_external_support.py",
         "paper11_v2/tests/test_r2_external_support.py")


class RegistrationError(ValueError):
    """Prerequisites/identity are invalid; no asset access is permitted."""


class DecodeDenied(ValueError):
    """Requested dataset, index, link or scalar representation is forbidden."""


class MetadataRangeReader(RangeReader):
    """Fixed inherited R0 HTTP206/range limits; lazy, in-memory transport only.

    session is supplied by parent at later acquisition. No HTTP occurs during
    construction; only HDF metadata/allowed scalar reads subsequently seek.
    No full-file checksum claim is made from a partial range audit.
    """
    def __init__(self, session, asset_identity):
        self.asset_identity = dict(asset_identity)
        self.version = VERSION
        self.namespace = NAMESPACE
        asset = asset_identity["asset_id"]
        super().__init__("https://api.dandiarchive.org/api/assets/" + asset + "/download/",
                         asset_identity["size"], session)


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _inside(root, relative):
    path = (root / relative).resolve()
    if path == root or root not in path.parents:
        raise RegistrationError("Registered path escapes workspace")
    return path


def _check_hashes(root, hashes):
    if not isinstance(hashes, dict) or not hashes:
        raise RegistrationError("Missing immutable hash mapping")
    for relative, sha in hashes.items():
        path = _inside(root, relative)
        if not path.is_file() or _sha(path.read_bytes()) != sha:
            raise RegistrationError("Immutable identity mismatch: " + relative)


def _finite(value):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value))


def _session_identity(session):
    return {key: session[key] for key in
            ("asset_id", "path", "patient", "published_sha256", "size")}


def validate_split(lock, assets):
    """Validate exact registered 52-session identity and chronological floor60/40.

    Frozen metadata contains row IDs/onsets, not physiological timestamps.
    Return sessions; no new selection, pruning or adequacy inference is made.
    """
    if lock.get("dataset") != "DANDI:000004" or lock.get("version") != VERSION:
        raise RegistrationError("Wrong external dataset/version")
    sessions = lock.get("eligible_sessions", [])
    if len(sessions) != 52 or len(assets) != 52:
        raise RegistrationError("Exact 52 pinned assets required")
    actual = {s["asset_id"]: _session_identity(s) for s in sessions}
    if len(actual) != 52 or actual != assets:
        raise RegistrationError("Pinned asset roster/identity mismatch")
    for session in sessions:
        trials = session["valid_recognition_trials"]
        rows = [t["row"] for t in trials]
        onsets = [t["start"] for t in trials]
        if (not rows or len(set(rows)) != len(rows)
                or any(not _finite(t) for t in onsets)
                or any(b <= a for a, b in zip(onsets, onsets[1:]))):
            raise RegistrationError("Invalid frozen trial identity/clock")
        ntrain = math.floor(0.6 * len(rows))
        if (session["calibration_train_rows"] != rows[:ntrain]
                or session["locked_final_rows"] != rows[ntrain:]):
            raise RegistrationError("Frozen chronological split identity mismatch")
    return sessions


def verify_registration(root, registration_path):
    """Check hashes/gates/source policy before any opener or endpoint read.

    New registration fields: study, namespace, registered_utc, source_sha256,
    phase, ab_prerequisite, r2_registration_sha256, r2_gate_sha256,
    split_sha256, assets, version, allowed_decodes,
    range_policy, timestamp_clock, source_audit and source_audit_sha256.
    source_audit includes prose, URL and line_refs [101,103,136,156]; its hash is
    SHA256 of UTF-8 json.dumps(...,sort_keys=True,separators=(',',':')). Parent
    must preserve its actual source reading and inferred-support limitations.
    A/B PASS is required before spikes, not before this metadata-only phase.
    Bind the gate hash when present; explicit null is required when absent.
    """
    root = Path(root).resolve()
    path = Path(registration_path).resolve()
    required_dir = root / "paper11_v2/results" / NAMESPACE
    if path.parent != required_dir or path.name != "registration.json":
        raise RegistrationError("Registration must use the new support namespace")
    reg = _json(path)
    if (reg.get("study") != "P11-v2" or reg.get("namespace") != NAMESPACE
            or reg.get("version") != VERSION or not reg.get("registered_utc")):
        raise RegistrationError("Missing prospective study/version identity")
    if reg.get("phase") != PHASE or reg.get("ab_prerequisite") != SPIKE_PREREQUISITE:
        raise RegistrationError("Metadata-only phase and before-spikes prerequisite required")
    sources = reg.get("source_sha256", {})
    if not set(FILES) <= sources.keys():
        raise RegistrationError("Both support source and test hashes required")
    _check_hashes(root, sources)
    r2path = root / "paper11_v2/results/R2/registration.json"
    if _sha(r2path.read_bytes()) != reg.get("r2_registration_sha256"):
        raise RegistrationError("R2 registration identity mismatch")
    r2 = _json(r2path)
    for field in ("source_sha256", "preceding_sha256", "archive_sha256"):
        _check_hashes(root, r2.get(field))
    for milestone in ("R0_amendment1_code1", "R1_code1"):
        gate = _json(root / "paper11_v2/results" / milestone / "gate_result.json")
        if gate.get("gate_verdict") != "PASS":
            raise RegistrationError("Preceding mandatory gate not PASS")
    gatepath = root / "paper11_v2/results/R2/gate_result.json"
    if "r2_gate_sha256" not in reg:
        raise RegistrationError("Explicit gate identity or null required")
    if gatepath.exists():
        if _sha(gatepath.read_bytes()) != reg["r2_gate_sha256"]:
            raise RegistrationError("R2 development/statistics gate identity mismatch")
        gate = _json(gatepath)
        stages = [gate.get(key) for key in ("R2_A", "R2_B", "R2_C")]
        if any(stage not in ("PASS", "RUNNING", "NOT_EXECUTED") for stage in stages):
            raise RegistrationError("R2 critical failure or unknown gate state")
        if (gate.get("tests_exit_code", 0) != 0 or gate.get("failed_candidate")
                or (gate.get("failures") and stages[:2] != ["PASS", "PASS"])):
            raise RegistrationError("R2 critical execution/verification failure")
    elif reg["r2_gate_sha256"] is not None:
        raise RegistrationError("Absent R2 gate requires registered null identity")
    # Overall FAIL can mean pending R2-C, not a failed scientific A/B gate.
    split = root / "paper11_v2/results/R0_schema1/final_validation_lock.json"
    split_sha = _sha(split.read_bytes())
    if split_sha != reg.get("split_sha256") or split_sha != r2.get("external_split_sha256"):
        raise RegistrationError("Frozen split identity mismatch")
    allowed = {key: list(value) for key, value in ALLOWED.items()}
    if reg.get("allowed_decodes") != allowed or reg.get("range_policy") != POLICY:
        raise RegistrationError("Strict decode/range policy mismatch")
    if reg.get("timestamp_clock") != CLOCK:
        raise RegistrationError("Unknown registered experiment clock")
    source = reg.get("source_audit", {})
    if (source.get("url") != SOURCE_URL or source.get("line_refs") != [101, 103, 136, 156]
            or not isinstance(source.get("prose"), str) or not source["prose"].strip()
            or source.get("direct_dropout_certification") is not False
            or source.get("execution_order_proof") != ORDERING_PROOF
            or source.get("support_kind") != "DOCUMENTED_CONTINUOUS_SUPPORT"):
        raise RegistrationError("Missing source-audited continuous-support inference")
    serialized = json.dumps(source, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if _sha(serialized) != reg.get("source_audit_sha256"):
        raise RegistrationError("Source audit prose/citation hash mismatch")
    sessions = validate_split(_json(split), reg.get("assets", {}))
    return reg, sessions


def _endpoint_dataset(file, path):
    if path not in ALLOWED:
        raise DecodeDenied("Forbidden dataset")
    import h5py
    group = file
    for part in path.split("/"):
        if not isinstance(group.get(part, getlink=True), h5py.HardLink):
            raise DecodeDenied("Missing/soft/external HDF link")
        group = group[part]
    if not isinstance(group, h5py.Dataset) or len(group.shape) != 1 or group.shape[0] < 2:
        raise DecodeDenied("Endpoint dataset must be a nonempty rank-one event sequence")
    numeric = group.dtype.kind in "iuf"
    string = h5py.check_string_dtype(group.dtype) is not None
    if not numeric and (path.endswith("timestamps") or not string):
        raise DecodeDenied("Unknown endpoint scalar representation")
    if path.endswith("timestamps"):
        unit = group.attrs.get("unit")
        if isinstance(unit, bytes):
            unit = unit.decode("ascii")
        if (unit not in ("s", "seconds") or group.attrs.get("conversion", 1) != 1
                or group.attrs.get("offset", 0) != 0):
            raise DecodeDenied("Unknown timestamp seconds/scale/offset")
    return group


def _ttl(value):
    """Accept only known scalar TTL55/66, with strict ASCII textual formatting."""
    if isinstance(value, bytes):
        value = value.decode("ascii")
    if isinstance(value, str):
        match = re.fullmatch(r"[ \t\r\n\f\v]*(55|66)(?:\.0)?[ \t\r\n\f\v]*", value)
        if match is not None:
            return int(match.group(1))
    elif _finite(value) and value in (55, 66):
        return int(value)
    raise DecodeDenied("Unknown scalar TTL label; expected exact55/66")


def read_endpoint(file, path, index, ledger):
    """Only data/timestamp scalar first/last values; reject before dereference.

    HDF metadata (shape/dtype/attributes/hard links) may be inspected. No unit
    ragged timestamp/index, acquisition signals, full TTL or outcome arrays.
    """
    if path not in ALLOWED or type(index) is not int or index not in ALLOWED[path]:
        raise DecodeDenied("Forbidden dataset or nonendpoint index")
    group = _endpoint_dataset(file, path)
    entry = {"path": path, "index": index, "decode_attempted": True,
             "decode_completed": False}
    ledger.append(entry)
    value = group[index]
    if not isinstance(value, (bytes, str)):
        value = value.item()
    entry["decode_completed"] = True
    if isinstance(value, bytes):
        try:
            entry["value"] = value.decode("ascii")
        except UnicodeDecodeError:
            entry["value"] = {"encoding": "hex", "bytes": value.hex()}
    elif isinstance(value, float) and not math.isfinite(value):
        entry["value"] = {"representation": "nonfinite_numeric", "text": repr(value)}
    else:
        entry["value"] = value
    if path.endswith("data"):
        normalized = _ttl(value)
        entry["normalized_value"] = normalized
        return normalized
    return value


def envelope_support(first_label, last_label, first_time, last_time, trials, clock):
    """Pure analytical [onset,onset+1) containment; never infer spike coverage."""
    def unknown(reason):
        return {"status": "UNKNOWN_SUPPORT", "reason": reason,
                "direct_dropout_certification": False,
                "final_unit_eligibility_established": False}
    if first_label != 55 or last_label != 66:
        return unknown("Unknown experiment start/end TTL labels; expected55/66")
    if clock != CLOCK:
        return unknown("Unknown experiment-relative seconds clock")
    if not _finite(first_time) or not _finite(last_time) or last_time <= first_time:
        return unknown("Nonfinite/unknown experiment boundaries")
    epochs = []
    for trial in trials:
        start = trial.get("start")
        if not _finite(start) or not math.isfinite(start + 1):
            return unknown("Unknown frozen trial onset")
        end = start + 1
        if start < first_time or end > last_time:
            return unknown("Frozen epoch is not enclosed by verified experiment boundaries")
        epochs.append({"row": trial["row"], "start": start, "stop": end})
    if not epochs:
        return unknown("No frozen trial epochs")
    return {"status": "DOCUMENTED_CONTINUOUS_SUPPORT",
            "experiment_start": first_time, "experiment_end": last_time,
            "clock": clock, "epochs": epochs,
            "basis": "Published continuous acquisition/stable units plus55/66 envelope",
            "direct_dropout_certification": False,
            "final_unit_eligibility_established": False,
            "limitation": "Source-support inference, not independently measured per-unit dropout."}


def audit_asset(file, session, clock):
    """Endpoint audit of one verified pinned asset; unknown support is retained."""
    ledger = []
    identity = _session_identity(session)
    try:
        first = read_endpoint(file, "acquisition/events/data", 0, ledger)
        last = read_endpoint(file, "acquisition/events/data", -1, ledger)
        if first != 55 or last != 66:
            result = envelope_support(first, last, None, None,
                                      session["valid_recognition_trials"], clock)
        elif clock != CLOCK:
            result = envelope_support(first, last, None, None,
                                      session["valid_recognition_trials"], clock)
        else:
            data_shape = _endpoint_dataset(file, "acquisition/events/data").shape
            time_shape = _endpoint_dataset(file, "acquisition/events/timestamps").shape
            if data_shape != time_shape:
                raise DecodeDenied("Event/time metadata lengths differ")
            start = read_endpoint(file, "acquisition/events/timestamps", 0, ledger)
            stop = read_endpoint(file, "acquisition/events/timestamps", -1, ledger)
            result = envelope_support(first, last, start, stop,
                                      session["valid_recognition_trials"], clock)
    except (DecodeDenied, KeyError, ValueError, TypeError, OverflowError, OSError, RuntimeError) as exc:
        result = {"status": "UNKNOWN_SUPPORT", "reason": str(exc),
                  "direct_dropout_certification": False,
                  "final_unit_eligibility_established": False}
    return {**identity, **result, "decoded_endpoints": ledger,
            "whole_asset_checksum_verified": False,
            "calibration_train_rows": session["calibration_train_rows"],
            "locked_final_rows": session["locked_final_rows"]}


def audit(root, registration_path, open_asset):
    """Verify first; audit exact roster, return reports without cache/output writes.

    open_asset(asset_identity, policy) is a parent-provided context manager
    yielding MetadataRangeReader, using a session created only at later approved
    acquisition. This function itself opens HDF through that bounded transport,
    retains range receipts and prevents full-file fallback. All future outputs
    belong to R2_external_support; transport cache is only in memory. This API
    never unlocks calibration or final spikes.
    audit_asset/read_endpoint/envelope_support are fixture-level primitives;
    real acquisition must enter through this verified audit() boundary.
    """
    reg, sessions = verify_registration(root, registration_path)
    import h5py
    reports = []
    for session in sessions:
        identity = _session_identity(session)
        with open_asset(identity, dict(POLICY)) as reader:
            if (type(reader) is not MetadataRangeReader or reader.asset_identity != identity
                    or reader.version != VERSION or reader.namespace != NAMESPACE):
                raise RegistrationError("Unregistered or identity-mismatched transport")
            with h5py.File(reader, "r") as file:
                report = audit_asset(file, session, reg["timestamp_clock"])
            report["range_receipts"] = list(reader.receipts)
            report["transport_bytes"] = reader.fetched
            reports.append(report)
    return {"namespace": NAMESPACE, "version": VERSION,
            "phase": PHASE, "ab_prerequisite": SPIKE_PREREQUISITE,
            "external_spikes_authorized": False,
            "source_audit_sha256": reg["source_audit_sha256"],
            "split_sha256": reg["split_sha256"], "sessions": reports,
            "support_complete": all(r["status"] == "DOCUMENTED_CONTINUOUS_SUPPORT"
                                    for r in reports),
            "direct_dropout_certification": False,
            "final_unit_eligibility_established": False,
            "scientific_R2_C_executed": False}
