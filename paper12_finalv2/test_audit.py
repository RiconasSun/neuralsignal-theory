"""Audit regressions do not certify the missing final-release controller."""
import unittest
from audit import LABEL, PRIMARY, build, outcome, release_allowed
from register_audit import HERE, load


class AuditTests(unittest.TestCase):
    def test_fail_closed_empty(self):
        self.assertFalse(release_allowed([]))

    def test_fail_closed_each_nonpass(self):
        for status in ('FAIL', 'HOLD', 'UNVERIFIED', 'NOT_IMPLEMENTED', 'SUPPORTED_WITHIN_REGISTERED_THREAT_MODEL'):
            self.assertFalse(release_allowed([{'status': 'PASS'}, {'status': status}]))

    def test_no_scientific_values_in_stopped_result(self):
        value = outcome([{'status': 'FAIL'}])
        self.assertEqual(list(value['contrasts']), list(PRIMARY))
        for contrast in value['contrasts'].values():
            self.assertEqual(contrast['classification'], LABEL)
            for key in ('effect', 'holm_p', 'CI95'):
                self.assertIsNone(contrast[key])
            self.assertEqual(contrast['null_verdict'], 'NOT_EXECUTED')

    def test_complete_atomic_contract(self):
        mission = load(HERE / 'mission.json')
        self.assertEqual(mission['baseline_requirement_count'], 60)
        self.assertEqual(len(mission['requirements']), 60)
        self.assertEqual(len({r['id'] for r in mission['requirements']}), 60)

    def test_exact_saved_audit_rebuild(self):
        self.assertEqual(build(), load(HERE / 'pre_release_audit.json'))

    def test_all_final_mice_and_stop(self):
        value = build()
        self.assertEqual(len(value['final_mouse_metadata']), 13)
        self.assertTrue(all(z['public_primary_cap32_possible'] for z in value['final_mouse_metadata']))
        self.assertFalse(value['release_allowed'])
        self.assertEqual(value['C_calibration_fits'], 0)
        self.assertEqual(value['D_assessments'], 0)
        self.assertEqual(value['protected_payloads_opened_by_audit'], 0)
        self.assertEqual(value['protected_keys_opened_by_audit'], 0)

    def test_scientific_failure_not_erased(self):
        value = build()
        self.assertFalse(value['historical_numerical_failures_reclassified'])
        self.assertEqual(value['stage_1'], 'CRITICAL_GATE_FAILED_STOP')
        self.assertEqual({g['id'] for g in value['gates'] if g['status'] == 'FAIL'}, {'G08', 'G09'})


if __name__ == '__main__':
    unittest.main()
