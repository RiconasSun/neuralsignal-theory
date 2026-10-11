import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import preflight_r0 as gate


class PreflightTests(unittest.TestCase):
    def test_forbidden_test_does_not_supply_coverage(self):
        rows, upper = gate.usable_coverage({'s1/a': {'partitions': {'train': list(range(24)), 'validation': list(range(24,32)), 'test': list(range(32,50))}}})
        self.assertEqual(upper, [])
        self.assertEqual(rows[0]['usable_trials'], 32)

    def test_sessions_not_independent_subjects(self):
        parts = {'partitions': {'train': list(range(30)), 'validation': list(range(30,40)), 'test': list(range(40,50))}}
        rows, upper = gate.usable_coverage({'s1/a': parts, 's1/b': parts})
        self.assertEqual(len(rows), 2)
        self.assertEqual(upper, ['s1'])

    def test_leakage_overlap_rejected(self):
        with self.assertRaises(RuntimeError):
            gate.usable_coverage({'s/a': {'partitions': {'train': [1], 'validation': [2], 'test': [1]}}})

    def test_registered_threshold_unchanged(self):
        p = json.loads((gate.base.STUDY / 'protocol/protocol.json').read_text())
        self.assertEqual(p['eligibility']['minimum_valid_trials_session'], 40)
        self.assertEqual(p['eligibility']['minimum_subjects_development'], 8)
        self.assertTrue(p['archive']['v1_failures_final'])

    def test_metadata_inventory_consistency(self):
        roster = json.loads((gate.base.OUT / 'metadata/asset_roster.json').read_text())
        audits = [json.loads(p.read_text()) for p in (gate.schema.OUT / 'audits').glob('*.json')]
        self.assertEqual({a['asset_id'] for a in audits}, {a['asset_id'] for a in roster['results']})
        for a in audits:
            self.assertEqual(a['schema_status'], 'VERIFIED')
            self.assertFalse(a['neural_values_decoded'])
            self.assertLessEqual(set(a['decoded_paths']), gate.base.ALLOWED)
            self.assertFalse(set(a['calibration_train_rows']) & set(a['locked_final_rows']))
            self.assertEqual(len(a['calibration_train_rows']), int(.6 * len(a['valid_recognition_trials'])))
            self.assertEqual(a['metadata_candidate'], len(a['hippocampal_units']) >= 5 and len(a['valid_recognition_trials']) >= 40)

    def test_saved_artifacts_not_corrupted(self):
        lock = gate.OUT / 'artifact_lock.json'
        if lock.exists():
            for rel, sha in json.loads(lock.read_text())['sha256'].items():
                self.assertEqual(gate.base.digest(gate.base.ROOT / rel), sha, rel)


if __name__ == '__main__':
    unittest.main()
