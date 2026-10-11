"""Parser fixtures are tests only, never substituted for experimental findings."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

PAPER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAPER / "scripts"))
import run_m1 as m


class M1Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = {"trial": "1", "set_size": "8", "probe_letter": "H", "match": "2", "correct": "0", "artifact": "0", "response_time": "1.5"}
        self.companion = {"nTrial": "1", "SetSize": "8", "ProbeLetter": "H", "Match": "OUT", "Correct": "0", "Artifact": "0", "ResponseTime": "1.5", "onset": "0.0005", "duration": "8"}
        self.phases = [{"trial": "1", "onset": onset, "duration": duration, "nix_event": name} for onset, duration, name in [('-6','1','Fixation_ss8'),('-5','2','Stimulus_ss8'),('-3','3','Maintenance'),('0','n/a','Probe_m2_H')]]
        self.temp_root = PAPER / "results" / "M1" / "test-temp"
        self.temp_root.mkdir(parents=True, exist_ok=True)

    def temporary(self):
        return tempfile.TemporaryDirectory(dir=self.temp_root)

    def test_explicit_hippocampus_and_hemisphere(self):
        self.assertEqual(m.anatomy("Hipp, Left Hippocampus rHipp, rostral hippocampus"), ("hippocampus", "left"))
        self.assertEqual(m.anatomy("Right hippocampus"), ("hippocampus", "right"))

    def test_other_mtl_never_promoted_to_hippocampus(self):
        for label in ("Left entorhinal cortex", "Right amygdala", "parahippocampal gyrus", "no_label_found", "MTL"):
            self.assertNotEqual(m.anatomy(label)[0], "hippocampus")

    def test_mixed_anatomy_is_ambiguous(self):
        self.assertEqual(m.anatomy("Left hippocampus and amygdala")[0], "ambiguous")
        self.assertEqual(m.anatomy("Left and right hippocampus")[1], "unknown")

    def test_trial_alignment_and_incorrect_trial_retained(self):
        audit = m.trial_audit([self.fixture], self.phases, [self.companion])
        self.assertEqual(audit["valid_trials"], [1])
        self.assertEqual(audit["alignment"], "PAIRED_VERIFIED")

    def test_each_companion_field_mismatch_rejected(self):
        for field, value in [("SetSize", "4"), ("ProbeLetter", "X"), ("Match", "IN"), ("Correct", "1"), ("Artifact", "1"), ("ResponseTime", "2.0")]:
            changed = dict(self.companion, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.trial_audit([self.fixture], self.phases, [changed])

    def test_missing_companion_is_labelled_unpaired(self):
        audit = m.trial_audit([self.fixture], self.phases, None)
        self.assertEqual(audit["alignment"], "UNPAIRED")
        self.assertEqual(audit["paired_trials_checked"], 0)

    def test_artifact_trial_excluded_before_split(self):
        audit = m.trial_audit([dict(self.fixture, artifact="1")], self.phases, None)
        self.assertFalse(audit["valid_trials"])
        self.assertIn("artifact_flag", audit["excluded_trials"][0]["reasons"])

    def test_trial_epoch_must_cover_frozen_preprobe_window(self):
        changed = copy.deepcopy(self.phases)
        changed[0]["onset"] = "-5.5"
        self.assertFalse(m.trial_audit([self.fixture], changed, None)["valid_trials"])

    def test_duplicate_trial_and_phase_fail(self):
        with self.assertRaises(ValueError):
            m.trial_audit([self.fixture, self.fixture], self.phases, None)
        with self.assertRaises(ValueError):
            m.trial_audit([self.fixture], self.phases + [self.phases[0]], None)

    def test_spike_qc_ignores_heldout_timestamp_and_unit_values(self):
        with self.temporary() as directory:
            path = Path(directory) / "fixture.tsv"
            path.write_text("unit_id\ttrial\tspike_time\n1\t1\t-5\nBAD_HELDOUT_UNIT\t2\tHELDOUT_NOT_PARSED\n", encoding="utf-8")
            counts, invalid, parsed = m.train_spike_qc(path, {1}, {1, 2}, {1})
            self.assertEqual(counts[1], 1)
            self.assertFalse(invalid)
            self.assertEqual(parsed, 1)

    def test_count_epoch_half_open_and_nonfinite_training_flag(self):
        with self.temporary() as directory:
            path = Path(directory) / "fixture.tsv"
            path.write_text("unit_id\ttrial\tspike_time\n1\t1\t-6\n1\t1\t0\n1\t1\tnan\n", encoding="utf-8")
            counts, invalid, _ = m.train_spike_qc(path, {1}, {1}, {1})
            self.assertEqual(counts[1], 1)
            self.assertEqual(invalid, {1})

    def test_session_identity_is_not_neuron_identity(self):
        self.assertNotEqual(m.session_key("sub-01/ses-01/ieeg/a.tsv"), m.session_key("sub-01/ses-02/ieeg/a.tsv"))

    def test_split_lock_never_overwrites_or_reassigns(self):
        with self.temporary() as directory:
            base = Path(directory)
            with patch.object(m, "SPLIT", base / "split.json"), patch.object(m, "SPLIT_LOCK", base / "lock.json"):
                sessions = {"fixture": {"train": [1], "test": [2]}}
                first = m.freeze_splits(sessions, {"fixture_metadata": "fixture-hash"})
                self.assertEqual(first, m.freeze_splits(sessions, {"fixture_metadata": "fixture-hash"}))
                before = m.SPLIT.read_bytes()
                with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                    m.freeze_splits({"fixture": {"train": [2], "test": [1]}}, {"fixture_metadata": "fixture-hash"})
                self.assertEqual(m.SPLIT.read_bytes(), before)

    def test_git_blob_checksum_is_content_bound(self):
        self.assertEqual(m.blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")
        self.assertNotEqual(m.blob_sha(b"changed\n"), m.blob_sha(b"hello\n"))

    def test_csv_qc_and_tsv_source_have_correct_delimiters(self):
        with self.temporary() as directory:
            base = Path(directory)
            for extension, delimiter in ((".csv", ","), (".tsv", "\t")):
                path = base / ("fixture" + extension)
                path.write_text(f"subject{delimiter}session\nfixture-subject{delimiter}fixture-session\n", encoding="utf-8")
                self.assertEqual(m.rows(path), [{"subject": "fixture-subject", "session": "fixture-session"}])

    def test_explicit_fusiform_is_not_unknown_or_hippocampus(self):
        self.assertEqual(m.anatomy("FuG, Right Fusiform Gyrus A20rv, rostroventral area 20"), ("fusiform", "right"))

    def test_real_preceding_gate_and_frozen_protocol(self):
        m.prerequisite()

    def test_real_splits_and_metadata_integrity(self):
        lock = m.m0.load(m.SPLIT_LOCK)
        self.assertEqual(m.digest(m.SPLIT), lock["split_sha256"])
        self.assertFalse(lock["spike_counts_inspected_at_freeze"])
        for path, expected in lock["metadata_sha256"].items():
            self.assertEqual(m.digest(PAPER / path), expected)
        for session in m.m0.load(m.SPLIT)["sessions"].values():
            partitions = session["partitions"]
            if partitions["train"]:
                self.assertEqual(partitions, m.m0.chronological_split(session["valid_trials"]))

    def test_real_acquisition_receipts_and_no_iEEG_signal(self):
        for receipt in m.m0.load(m.RECEIPTS)["files"]:
            path = m.DATA / receipt["dataset"] / receipt["path"]
            self.assertEqual(m.digest(path), receipt["sha256"])
            self.assertEqual(m.blob_sha(path.read_bytes()), receipt["git_blob_sha"])
            self.assertTrue(receipt["content_verified"])
            self.assertFalse(receipt["path"].endswith((".edf", ".nwb", ".h5")))

    def test_frozen_population_and_subject_thresholds(self):
        self.assertTrue(m.session_eligible(40, 5))
        self.assertFalse(m.session_eligible(39, 5))
        self.assertFalse(m.session_eligible(50, 4))
        self.assertTrue(m.coverage_sufficient(6))
        self.assertFalse(m.coverage_sufficient(5))

    def test_real_primary_units_require_eligible_population_session(self):
        sessions = {r["subject"] + "/" + r["session"]: r for r in m.rows(m.RESULTS / "session_qc.csv")}
        for unit in m.rows(m.RESULTS / "unit_qc.csv"):
            if unit["primary_analysis_eligible"] == "True":
                self.assertEqual(unit["region"], "hippocampus")
                self.assertEqual(unit["eligible"], "True")
                self.assertEqual(sessions[unit["subject"] + "/" + unit["session"]]["eligible"], "True")

    def test_raw_experimental_files_not_in_git(self):
        self.assertFalse(m.m0.git("ls-files", "--", "paper11/raw"))


if __name__ == "__main__":
    unittest.main()
