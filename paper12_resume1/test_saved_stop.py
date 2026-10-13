import unittest
import study as r


class SavedStopTests(unittest.TestCase):
    def test_m2_complete_real_cohort(self):
        gate=r.load(r.HERE/'results/M2/gate_result.json')
        self.assertEqual(gate['gate'],'PASS')
        self.assertEqual(gate['completed_QC'],{'development':13,'final':13})
        self.assertEqual(gate['eligible_mice'],{'development':13,'final':13})
        self.assertEqual(gate['completion_issuer_verified_count'],26)
        audit=r.load(r.HERE/'results/M2/source_checkpoint_integrity.json')
        self.assertEqual(audit['verified_completed_new_sessions'],18)
        self.assertEqual(len(audit['rows']),18)

    def test_m3_failure_not_reclassified(self):
        gate=r.load(r.HERE/'results/M3/progressive1/gate_result.json')
        self.assertEqual(gate['gate'],'FAIL');self.assertEqual(gate['scientific_verdict'],'INCONCLUSIVE')
        self.assertEqual(gate['completed_fit_count'],126);self.assertEqual(gate['mouse_count'],1)
        self.assertFalse(gate['full_cohort_execution'])
        for roi in ('CA1','DG'):
            for kind in ('history','population','event','drift','combined'):self.assertEqual(gate['eligible_ridges'][roi][kind],[])

    def test_native_role_and_final_lock(self):
        proof=r.load(r.HERE/'results/M3/progressive1/role_proof.json')
        self.assertTrue(proof['pass']);self.assertEqual(proof['capability_count'],0)
        receipt=r.load(r.HERE/'results/M3/progressive_launch_receipt_code4.json')
        self.assertEqual(receipt['exit_code'],2);self.assertEqual(receipt['M3_gate'],'FAIL')
        self.assertFalse(receipt['final_holdout_evaluated']);self.assertFalse(receipt['final_values_exposed_to_analysis'])
        self.assertFalse((r.HERE/'M4_implementation_registration.json').exists())
        self.assertFalse((r.HERE/'results/M4/numerical_gate.json').exists())
