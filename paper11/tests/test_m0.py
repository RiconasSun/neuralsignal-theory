"""Contract fixtures only; no synthetic spikes or scientific evidence."""

import copy
import importlib.util
import unittest
import tempfile
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("p11_m0", PAPER / "scripts" / "run_m0.py")
m0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m0)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.protocol = m0.load(PAPER / "protocol" / "protocol.json")

    def test_complete_contract(self):
        m0.validate_protocol(self.protocol)

    def test_no_next_milestone(self):
        self.protocol["execution"]["milestone"] = "M1"
        with self.assertRaises(ValueError):
            m0.validate_protocol(self.protocol)

    def test_required_null_cannot_be_removed(self):
        for index in range(5):
            p = copy.deepcopy(self.protocol)
            p["null_tests"].pop(index)
            with self.assertRaises(ValueError):
                m0.validate_protocol(p)

    def test_models_cannot_be_removed(self):
        del self.protocol["models"]["hybrid"]
        with self.assertRaises(ValueError):
            m0.validate_protocol(self.protocol)

    def test_subject_independent_unit(self):
        self.protocol["statistics"]["independent_unit"] = "trial"
        with self.assertRaises(ValueError):
            m0.validate_protocol(self.protocol)

    def test_no_modality_pooling(self):
        self.protocol["data"]["companion_ieeg"]["pooled_with_spikes"] = True
        with self.assertRaises(ValueError):
            m0.validate_protocol(self.protocol)

    def test_no_draft_external(self):
        self.protocol["data"]["external"]["version"] = "draft"
        with self.assertRaises(ValueError):
            m0.validate_protocol(self.protocol)

    def test_no_direct_external_replication(self):
        self.protocol["data"]["external"]["direct_replication_claim_allowed"] = True
        with self.assertRaises(ValueError):
            m0.validate_protocol(self.protocol)

    def test_split_whole_trials_disjoint_and_chronological(self):
        split = m0.chronological_split(list(range(50, 0, -1)))
        self.assertEqual(split["train"], list(range(1, 31)))
        self.assertEqual(split["validation"], list(range(31, 41)))
        self.assertEqual(split["test"], list(range(41, 51)))
        self.assertFalse(set(split["train"]) & set(split["test"]))

    def test_split_rounding_and_no_trial_omission(self):
        split = m0.chronological_split(list(range(1, 48)))
        self.assertEqual([len(split[k]) for k in ("train", "validation", "test")], [28, 9, 10])
        self.assertEqual(sum(split.values(), []), list(range(1, 48)))

    def test_insufficient_trials_rejected(self):
        with self.assertRaisesRegex(ValueError, "DATA_INSUFFICIENT"):
            m0.chronological_split(list(range(1, 40)))

    def test_duplicate_and_noninteger_trial_rejected(self):
        for trials in ([1] * 40, list(range(1, 40)) + [True], list(range(1, 40)) + ["40"]):
            with self.assertRaises(ValueError):
                m0.chronological_split(trials)

    def test_all_metadata_sources_pinned_no_experimental_download(self):
        self.assertEqual(len(m0.SOURCES), 9)
        self.assertNotIn("latest", " ".join(m0.SOURCES.values()))
        self.assertNotIn("draft", " ".join(m0.SOURCES.values()))
        for name in m0.SOURCES:
            self.assertTrue(name.endswith((".json", ".md", ".tsv")))

    def test_freeze_refuses_overwrite(self):
        if not m0.LOCK.exists():
            self.skipTest("Initial freeze not created; rerun as part of M0 verification")
        with self.assertRaisesRegex(ValueError, "refusing overwrite"):
            m0.freeze()

    def test_frozen_artifact_and_environment_integrity(self):
        if not m0.LOCK.exists():
            self.skipTest("Initial freeze not created; rerun as part of M0 verification")
        qc = m0.verify()
        self.assertFalse(qc["experimental_data_acquired"])
        self.assertEqual(qc["source_receipts"], 9)

    def test_corrupt_or_missing_frozen_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path = base / "fixture.txt"
            path.write_text("contract fixture, not scientific data", encoding="utf-8")
            hashes = {"fixture.txt": m0.sha(path)}
            m0.verify_hashes(base, hashes)
            path.write_text("changed fixture", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Frozen artifact mismatch"):
                m0.verify_hashes(base, hashes)
            path.unlink()
            with self.assertRaises(OSError):
                m0.verify_hashes(base, hashes)


if __name__ == "__main__":
    unittest.main()
