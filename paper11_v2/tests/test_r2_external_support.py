"""Prospective metadata-only fixtures; do not run before parent registration.

Synthetic HDF endpoints and temporary registration trees only; no network,
experimental timestamps/counts, outcome arrays or model fitting.
"""

import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import h5py
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import r2_external_support as support

TEST_FIXTURE = Path(__file__).resolve().parents[1] / ".venv/test_fixture/R2_external_support"


def synthetic_lock():
    sessions = []
    for i in range(52):
        sessions.append({"asset_id": "fixture-" + str(i), "path": "fixture/" + str(i),
                         "patient": "fixture-patient-" + str(i // 2),
                         "published_sha256": "a" * 64, "size": 100,
                         "valid_recognition_trials": [{"row": j, "start": 1. + 2 * j}
                                                      for j in range(5)],
                         "calibration_train_rows": [0, 1, 2], "locked_final_rows": [3, 4]})
    return {"dataset": "DANDI:000004", "version": support.VERSION,
            "eligible_sessions": sessions}


def assets(lock):
    return {s["asset_id"]: {k: s[k] for k in
                           ("asset_id", "path", "patient", "published_sha256", "size")}
            for s in lock["eligible_sessions"]}


def hdf(labels=(55, 77, 88, 66), times=(0., 2., 5., 10.), unit="seconds", label_dtype=None):
    file = h5py.File(io.BytesIO(), "w")
    if label_dtype is None:
        file["acquisition/events/data"] = np.asarray(labels)
    else:
        file.create_dataset("acquisition/events/data", data=labels, dtype=label_dtype)
    file["acquisition/events/timestamps"] = np.asarray(times)
    file["acquisition/events/timestamps"].attrs["unit"] = unit
    return file


class EnvelopeTests(unittest.TestCase):
    def test_analytic_envelope_and_half_open_boundary(self):
        trials = [{"row": 0, "start": 0.}, {"row": 1, "start": 9.}]
        result = support.envelope_support(55, 66, 0., 10., trials, support.CLOCK)
        self.assertEqual(result["status"], "DOCUMENTED_CONTINUOUS_SUPPORT")
        self.assertEqual(result["epochs"][1], {"row": 1, "start": 9., "stop": 10.})
        self.assertFalse(result["direct_dropout_certification"])
        self.assertFalse(result["final_unit_eligibility_established"])

    def test_nonfinite_reversed_unknown_boundaries_and_outside_epoch(self):
        for start, stop in ((np.nan, 10.), (0., np.inf), (10., 0.), (0., None)):
            result = support.envelope_support(55, 66, start, stop,
                                               [{"row": 1, "start": 1.}], support.CLOCK)
            self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
        for onset in (-0.01, 9.01, float("nan")):
            result = support.envelope_support(55, 66, 0., 10.,
                                               [{"row": 1, "start": onset}], support.CLOCK)
            self.assertEqual(result["status"], "UNKNOWN_SUPPORT")

    def test_unknown_label_clock_and_empty_trials(self):
        for first, last, clock in ((54, 66, support.CLOCK), (55, 67, support.CLOCK),
                                    (55, 66, "milliseconds"), (55, 66, "absolute_time")):
            self.assertEqual(support.envelope_support(first, last, 0., 10.,
                             [{"row": 1, "start": 1.}], clock)["status"], "UNKNOWN_SUPPORT")
        self.assertEqual(support.envelope_support(55, 66, 0., 10., [],
                                                  support.CLOCK)["status"], "UNKNOWN_SUPPORT")


class EndpointTests(unittest.TestCase):
    def test_only_four_scalar_reads_no_full_ttl_or_spikes(self):
        session = synthetic_lock()["eligible_sessions"][0]
        with hdf() as file:
            result = support.audit_asset(file, session, support.CLOCK)
        self.assertEqual(result["status"], "DOCUMENTED_CONTINUOUS_SUPPORT")
        self.assertEqual([(r["path"], r["index"]) for r in result["decoded_endpoints"]],
                         [("acquisition/events/data", 0), ("acquisition/events/data", -1),
                          ("acquisition/events/timestamps", 0),
                          ("acquisition/events/timestamps", -1)])
        self.assertTrue(all(r["decode_completed"] for r in result["decoded_endpoints"]))
        self.assertEqual([r["value"] for r in result["decoded_endpoints"]], [55, 66, 0., 10.])
        self.assertFalse(result["whole_asset_checksum_verified"])

    def test_fixed_bytes_and_vlen_strings_normalize_only_endpoint_ttl(self):
        cases = [(b" 55.0\t", b"66", "S8"),
                 (b"55", b" 66.0\n", h5py.string_dtype("ascii")),
                 ("\t55 ", "66.0", h5py.string_dtype("utf-8"))]
        for first, last, dtype in cases:
            with self.subTest(dtype=str(dtype)), hdf(
                    labels=(first, "unused-middle", "unused-middle", last),
                    label_dtype=dtype) as file:
                result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
            self.assertEqual(result["status"], "DOCUMENTED_CONTINUOUS_SUPPORT")
            ledger = result["decoded_endpoints"]
            self.assertEqual(len(ledger), 4)
            self.assertEqual([r["normalized_value"] for r in ledger[:2]], [55, 66])
            expected = [first.decode("ascii") if isinstance(first, bytes) else first,
                        last.decode("ascii") if isinstance(last, bytes) else last, 0., 10.]
            self.assertEqual([r["value"] for r in ledger], expected)
            self.assertEqual([r["index"] for r in ledger], [0, -1, 0, -1])
            self.assertTrue(all(not isinstance(r["value"], (list, np.ndarray)) for r in ledger))

    def test_python_bytes_and_str_scalar_normalization(self):
        for value in (b"55", "55.0", "\r\n55\t", 55, 55.0):
            self.assertEqual(support._ttl(value), 55)
        for value in (b"66", "66.0", " 66 ", 66, 66.0):
            self.assertEqual(support._ttl(value), 66)

    def test_unknown_string_ttl_keeps_scalar_receipt_and_denies_time_decode(self):
        for label in ("55.00", "+55", "055", "5.5e1", "55 response", "unknown", "\u00a055"):
            with self.subTest(label=label), hdf(
                    labels=(label, "unused", "unused", "66"),
                    label_dtype=h5py.string_dtype("utf-8")) as file:
                result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
            self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
            ledger = result["decoded_endpoints"]
            self.assertEqual(len(ledger), 1)
            self.assertTrue(ledger[0]["decode_completed"])
            self.assertIn("value", ledger[0])
            json.dumps(result, allow_nan=False)

    def test_nonstring_vlen_and_text_timestamps_are_denied(self):
        with hdf() as file:
            del file["acquisition/events/data"]
            file.create_dataset("acquisition/events/data", shape=(2,),
                                dtype=h5py.vlen_dtype(np.dtype("int32")))
            result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
        self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
        self.assertEqual(result["decoded_endpoints"], [])
        with hdf() as file:
            del file["acquisition/events/timestamps"]
            file.create_dataset("acquisition/events/timestamps", data=["0", "2", "5", "10"],
                                dtype=h5py.string_dtype("ascii"))
            file["acquisition/events/timestamps"].attrs["unit"] = "seconds"
            result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
        self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
        self.assertEqual(len(result["decoded_endpoints"]), 2)

    def test_unknown_labels_prevent_timestamp_decode(self):
        with hdf(labels=(55, 77, 88, 99)) as file:
            result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
        self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
        self.assertEqual(len(result["decoded_endpoints"]), 2)
        self.assertTrue(all(r["path"].endswith("data") for r in result["decoded_endpoints"]))

    def test_forbidden_path_and_index_guard_precedes_hdf_access(self):
        paths = ("units/spike_times", "units/spike_times_index", "units/waveforms",
                 "units/rates", "acquisition/raw/data", "intervals/trials/confidence")
        for path in paths:
            with self.assertRaises(support.DecodeDenied):
                support.read_endpoint(None, path, 0, [])
        for index in (1, -2, slice(None), True, [0, -1]):
            with self.assertRaises(support.DecodeDenied):
                support.read_endpoint(None, "acquisition/events/data", index, [])

    def test_unknown_timestamp_units_and_lengths_fail_without_time_decode(self):
        for kwargs in ({"unit": "ms"}, {"times": (0., 10.)}):
            with hdf(**kwargs) as file:
                result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
            self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
            self.assertEqual(len(result["decoded_endpoints"]), 2)

    def test_soft_links_denied_and_missing_end_is_unknown(self):
        with hdf() as file:
            del file["acquisition/events/timestamps"]
            file["acquisition/events/timestamps"] = h5py.SoftLink("/unregistered")
            result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
        self.assertEqual(result["status"], "UNKNOWN_SUPPORT")
        self.assertEqual(len(result["decoded_endpoints"]), 2)
        with hdf(labels=(55,)) as file:
            result = support.audit_asset(file, synthetic_lock()["eligible_sessions"][0], support.CLOCK)
        self.assertEqual(result["status"], "UNKNOWN_SUPPORT")

    def test_full_file_http_fallback_denied_before_body(self):
        class Response:
            status_code = 200
            headers = {}
            raw = io.BytesIO(b"forbidden full file")
            def close(self):
                pass
        class Session:
            def get(self, *args, **kwargs):
                return response
        response = Response()
        identity = assets(synthetic_lock())["fixture-0"]
        reader = support.MetadataRangeReader(Session(), identity)
        with self.assertRaises(RuntimeError):
            reader.read(1)
        self.assertEqual(response.raw.tell(), 0)
        with self.assertRaises(RuntimeError):
            reader.read()


class RegistrationTests(unittest.TestCase):
    def test_exact_roster_version_identity_and_floor_split(self):
        lock = synthetic_lock()
        self.assertEqual(len(support.validate_split(lock, assets(lock))), 52)
        for mutation in ("version", "roster", "split", "clock", "digest"):
            changed = copy.deepcopy(lock)
            registered = assets(lock)
            if mutation == "version":
                changed["version"] = "other"
            elif mutation == "roster":
                changed["eligible_sessions"].pop()
            elif mutation == "split":
                changed["eligible_sessions"][0]["calibration_train_rows"] = [0, 1, 3]
            elif mutation == "clock":
                changed["eligible_sessions"][0]["valid_recognition_trials"][0]["start"] = float("inf")
            else:
                registered["fixture-0"]["published_sha256"] = "b" * 64
            with self.subTest(mutation=mutation), self.assertRaises(support.RegistrationError):
                support.validate_split(changed, registered)

    def test_audit_never_opens_asset_when_registration_fails(self):
        with patch.object(support, "verify_registration", side_effect=support.RegistrationError("fixture denial")), \
                patch("builtins.open") as opener:
            with self.assertRaises(support.RegistrationError):
                support.audit("fixture", "fixture", opener)
        opener.assert_not_called()

    def fixture_registration(self, root):
        def write(relative, value):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")
            return hashlib.sha256(path.read_bytes()).hexdigest()
        tracked = {"fixture-prior.json": write("fixture-prior.json", {"immutable": True})}
        sources = {name: write(name, {"synthetic_source": name}) for name in support.FILES}
        lock = synthetic_lock()
        split_sha = write("paper11_v2/results/R0_schema1/final_validation_lock.json", lock)
        r2_sha = write("paper11_v2/results/R2/registration.json", {
            "source_sha256": tracked, "preceding_sha256": tracked, "archive_sha256": tracked,
            "external_split_sha256": split_sha})
        for milestone in ("R0_amendment1_code1", "R1_code1"):
            write("paper11_v2/results/" + milestone + "/gate_result.json", {"gate_verdict": "PASS"})
        gate_sha = write("paper11_v2/results/R2/gate_result.json", {
            "R2_A": "PASS", "R2_B": "NOT_EXECUTED", "R2_C": "NOT_EXECUTED"})
        source = {"url": support.SOURCE_URL, "line_refs": [101, 103, 136, 156],
                  "prose": "Synthetic source-support registration fixture, not article evidence.",
                  "support_kind": "DOCUMENTED_CONTINUOUS_SUPPORT", "direct_dropout_certification": False,
                  "execution_order_proof": support.ORDERING_PROOF}
        reg = {"study": "P11-v2", "namespace": support.NAMESPACE, "version": support.VERSION,
               "registered_utc": "fixture", "source_sha256": sources,
               "phase": support.PHASE, "ab_prerequisite": support.SPIKE_PREREQUISITE,
               "r2_registration_sha256": r2_sha, "r2_gate_sha256": gate_sha, "split_sha256": split_sha,
               "allowed_decodes": {k: list(v) for k, v in support.ALLOWED.items()},
               "range_policy": support.POLICY.copy(), "timestamp_clock": support.CLOCK,
               "source_audit": source, "source_audit_sha256": hashlib.sha256(json.dumps(
                   source, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
               "assets": assets(lock)}
        relative = "paper11_v2/results/R2_external_support/registration.json"
        write(relative, reg)
        return root / relative, reg

    def test_source_gate_policy_and_split_registration_denials(self):
        TEST_FIXTURE.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEST_FIXTURE) as temp:
            root = Path(temp)
            path, reg = self.fixture_registration(root)
            verified, sessions = support.verify_registration(root, path)
            self.assertEqual(len(sessions), 52)
            for field, value in (("split_sha256", "wrong"), ("timestamp_clock", "unknown"),
                                 ("source_audit_sha256", "wrong"), ("allowed_decodes", {}),
                                 ("range_policy", {}), ("r2_registration_sha256", "wrong"),
                                 ("phase", "SPIKES"), ("ab_prerequisite", "PASS"),
                                 ("r2_gate_sha256", "wrong")):
                changed = dict(reg, **{field: value})
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(field=field), self.assertRaises(support.RegistrationError):
                    support.verify_registration(root, path)
            path.write_text(json.dumps(reg), encoding="utf-8")
            gate = root / "paper11_v2/results/R2/gate_result.json"
            failed = {"R2_A": "FAIL", "R2_B": "NOT_EXECUTED", "R2_C": "NOT_EXECUTED"}
            gate.write_text(json.dumps(failed))
            changed = dict(reg, r2_gate_sha256=hashlib.sha256(gate.read_bytes()).hexdigest())
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(support.RegistrationError):
                support.verify_registration(root, path)
            gate.unlink()
            changed = dict(reg, r2_gate_sha256=None)
            path.write_text(json.dumps(changed), encoding="utf-8")
            self.assertEqual(len(support.verify_registration(root, path)[1]), 52)
            del changed["r2_gate_sha256"]
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(support.RegistrationError):
                support.verify_registration(root, path)
            path.write_text(json.dumps(reg), encoding="utf-8")
            with self.assertRaises(support.RegistrationError):
                support.verify_registration(root, path)
            path.write_text(json.dumps(dict(reg, r2_gate_sha256=None)), encoding="utf-8")
            (root / support.FILES[0]).write_text("changed")
            with self.assertRaises(support.RegistrationError):
                support.verify_registration(root, path)


if __name__ == "__main__":
    unittest.main()
