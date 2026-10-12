import unittest
import closeout
import register as r


class CloseoutTests(unittest.TestCase):
    def test_unknown_eligibility_not_zero_or_insufficient(self):
        report, gate, summary = closeout.derive()
        self.assertEqual(gate['gate'], 'FAIL')
        self.assertEqual(gate['scientific_verdict'], 'INCONCLUSIVE')
        self.assertIsNone(gate['actual_eligible_development_mice'])
        self.assertIsNone(gate['actual_eligible_final_mice'])
        self.assertEqual(len(report), 26)
        self.assertEqual(gate['model_fits'], 0)
        self.assertEqual(gate['final_evaluations'], 0)
        self.assertFalse(gate['scientific_validation_pass'])
        self.assertTrue(summary['all_mice_metadata_trial_coverage_pass'])

    def test_frozen_complete_grid(self):
        p = r.load(r.HERE / 'protocol.json')['models']
        count = 1 + (len(p['baselines']) - 1) * len(p['ridge'])
        count += sum(len(p[x]) * len(p['ridge']) for x in ('HMM_states', 'recurrent_dimensions', 'hybrid_states'))
        self.assertEqual(count, 57)
        self.assertEqual(count, p['configuration_count'])
        self.assertEqual(p['seeds'], [11, 23, 37])

    def test_final_roles_and_masks_not_reallocated(self):
        trials = r.load(r.HERE / 'locks/trials.json')
        for t in trials:
            if t['group'] == 'final':
                self.assertIn(t['partition'], ('calibration', 'locked_evaluation'))
            else:
                self.assertIn(t['partition'], ('train', 'validation'))
            if t['metadata_admitted']:
                self.assertGreaterEqual(t['provider_stop'], t['analysis_stop'])
        self.assertEqual(sum(not t['metadata_admitted'] for t in trials), 39)

    def test_quarantine_preserved(self):
        units = r.load(r.HERE / 'locks/units.json')
        quarantined = [u for u in units if u['metadata_quarantined']]
        self.assertEqual(len(quarantined), 82)
        self.assertEqual({u['probe_id'] for u in quarantined}, {'846401834'})
        self.assertTrue(all(u['physiological_QC'] == 'NOT_ASSESSED' for u in units))
        self.assertTrue(all(u['finite_CCF_coordinates'] == 'True' for u in units))


if __name__ == '__main__':
    unittest.main()
