import importlib.util
import io
import unittest
from pathlib import Path

import h5py
import numpy as np

spec = importlib.util.spec_from_file_location("r0", Path(__file__).resolve().parents[1] / "scripts/run_r0.py")
r0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r0)


class Response:
    def __init__(self, status=206, header="bytes 0-9/10", data=b"0123456789"):
        self.status_code = status
        self.headers = {"Content-Range": header}
        self.raw = io.BytesIO(data)
        self.closed = False

    def close(self):
        self.closed = True


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, *args, **kwargs):
        self.calls.append(kwargs)
        return self.response


class R0Tests(unittest.TestCase):
    def test_range_seeking_cache(self):
        session = Session(Response())
        reader = r0.RangeReader("https://example.invalid", 10, session)
        self.assertEqual(reader.read(3), b"012")
        reader.seek(-2, 2)
        self.assertEqual(reader.read(3), b"89")
        self.assertEqual(reader.fetched, 10)
        self.assertEqual(len(session.calls), 1)
        self.assertEqual(session.calls[0]["headers"]["Range"], "bytes=0-9")

    def test_whole_file_fallback_refused_before_body(self):
        response = Response(status=200)
        with self.assertRaises(RuntimeError):
            r0.RangeReader("https://example.invalid", 10, Session(response)).read(1)
        self.assertEqual(response.raw.tell(), 0)
        self.assertTrue(response.closed)

    def test_wrong_range_refused(self):
        with self.assertRaises(RuntimeError):
            r0.RangeReader("url", 10, Session(Response(header="bytes 1-9/10"))).read(1)

    def test_unbounded_read_refused(self):
        with self.assertRaises(RuntimeError):
            r0.RangeReader("url", 10, Session(Response())).read()

    def test_neural_path_refused(self):
        for key in ["units/spike_times", "units/spike_times_index", "acquisition/data", "intervals/trials/confidence"]:
            with self.assertRaises(RuntimeError):
                r0.permitted_read({}, key, [])

    def test_anatomy_not_all_mtl(self):
        self.assertEqual(r0.hippocampal_locations([b"left hippocampus", "right hippocampal", "amygdala", "MTL", "LH", "entorhinal"]), [True, True, False, False, False, False])

    def test_aliases_not_independent(self):
        self.assertEqual(r0.canonical_patient("sub-P10HMH_2/session.nwb"), "sub-P10HMH")
        with self.assertRaises(RuntimeError):
            r0.canonical_patient("sub-unknown/session.nwb")

    def test_metadata_ragged_mapping_and_split(self):
        with h5py.File(io.BytesIO(), "w") as f:
            f["units/id"] = np.arange(6)
            f["units/electrodes"] = [0, 0, 0, 0, 0, 1]
            f["units/electrodes_index"] = np.arange(1, 7)
            f["general/extracellular_ephys/electrodes/location"] = np.array(["left hippocampus", "amygdala"], dtype=h5py.string_dtype())
            f["intervals/trials/start_time"] = np.arange(40) * 2.
            f["intervals/trials/stop_time"] = np.arange(40) * 2. + .2
            f["intervals/trials/stim_phase"] = np.array(["recognition"] * 40, dtype=h5py.string_dtype())
            ledger = []
            result = r0.summarize_metadata(f, ledger)
        self.assertTrue(result["metadata_candidate"])
        self.assertEqual(len(result["hippocampal_units"]), 5)
        self.assertEqual(len(result["calibration_train_rows"]), 24)
        self.assertEqual(len(result["locked_final_rows"]), 16)
        self.assertFalse(set(result["calibration_train_rows"]) & set(result["locked_final_rows"]))
        self.assertTrue(set(ledger) <= r0.ALLOWED)

    def test_registration_archive_is_final(self):
        import json
        protocol = json.loads((r0.STUDY / "protocol/protocol.json").read_text())
        self.assertTrue(protocol["archive"]["v1_failures_final"])
        self.assertEqual(protocol["eligibility"]["minimum_subjects_external"], 8)
        self.assertFalse(protocol["external"]["direct_replication"])
        self.assertEqual(protocol["metric"]["units"], "nats/unit-bin")


if __name__ == "__main__":
    unittest.main()
