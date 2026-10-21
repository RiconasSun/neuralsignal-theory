"""R4-specific synthetic/saved identity gates; never scientific fitting."""
import hashlib
import inspect
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from .core import *
from . import controller, source


class R4GateTests(unittest.TestCase):
    def test_policy_only_ftol_and_frozen_all_original_gates(self):
        expected=load(R/'paper16_m1/NUMERICAL_POLICY.json');expected['options']['ftol']=0.0
        self.assertEqual(NUMERIC,expected)
        for name in ['features.py','models.py','panels.py','controls.py']:
            self.assertEqual(sha(P/name),sha(R/'paper16_development_r3'/name))

    def test_complete_original_plan_minus_952_and_diagnostic_not_inserted(self):
        old=load(R/'paper16_development_r3/results/TASK_PLAN.json')['tasks']
        admitted=controller.admitted_lookup();new=load(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks']
        self.assertEqual(new,[t for t in old if t['id'] not in admitted])
        self.assertEqual((len(old),len(admitted),len(new)),(6471,952,5519))
        failed='733457989:S02:C:951800892:None:GLOBAL'
        task=next(t for t in new if t['id']==failed)
        self.assertTrue(controller.task_folder(task).is_relative_to(P/'work/fits'))
        self.assertNotIn(failed,admitted)

    def test_cached_lookup_is_identity_equivalent_not_state_relabeling(self):
        a=controller.admitted_lookup();b=controller.admitted_lookup()
        self.assertIs(a,b)
        self.assertTrue(all(r['historical_ftol']==1e-12 and r['generated_by']=='R3' for r in a.values()))
        task=load(R/'paper16_development_r3/results/TASK_PLAN.json')['tasks'][0]
        self.assertTrue(controller.task_folder(task).is_relative_to(R/'paper16_development_r3'))

    def test_prefit_tamper_and_all_roles_fail_closed_before_authority(self):
        for role in ['B','C','D','Final','A','E']:
            with self.subTest(role=role),patch.object(source,'native_role',side_effect=AssertionError('No source')):
                with self.assertRaises((AccessStop,FileNotFoundError)):controller.require_phase(role)
        approval=load(E/'REUSE_ADMISSION_APPROVAL.json')
        self.assertEqual(approval['decision'],'ACCEPTED_HISTORICAL_STATE_ADMISSION_ONLY')
        target=R/approval['files'][0]['path'];real=controller.sha
        def altered(path):return '0'*64 if Path(path)==target else real(path)
        with patch.object(controller,'sha',side_effect=altered):
            with self.assertRaises(AccessStop):controller.verify_prefit()

    def test_missing_M4_all_states_or_task_coverage_refused(self):
        with self.assertRaises(AccessStop):controller.validate_m4_freeze({}, {'tasks':[]})
        fake={'task_plan_sha256':sha(R/'paper16_development_r3/results/TASK_PLAN.json'),
              'task_origins':[], 'states':[], 'selected_seeds':[]}
        with self.assertRaises(AccessStop):controller.validate_m4_freeze(fake,{'tasks':[]})

    def test_E_only_after_review_same_deadline_and_single_exclusive_claim(self):
        text=inspect.getsource(controller.worker)
        self.assertLess(text.index('fitted=seal'),text.index("while not (E/'M4_APPROVAL.json')"))
        self.assertLess(text.index("review_binding('M4_APPROVAL.json'"),text.index("once(P/'results/E_BATCH_CLAIM.json'"))
        self.assertLess(text.index("once(P/'results/E_BATCH_CLAIM.json'"),text.index('evaluate_E('))
        self.assertEqual(text.count('make_stage('),0)
        self.assertIn('analysis_oracles.statistics(values)',inspect.getsource(controller.evaluate_E))

    def test_original_statistics_exact_signs_Holm5_CI_LOMO_on_synthetic(self):
        x=np.arange(24,dtype=float).reshape(4,6)*.0001-.0009
        stats=analysis_oracles.statistics(x)
        self.assertTrue(stats['exact']);self.assertEqual(stats['sign_patterns'],16)
        np.testing.assert_array_equal(stats['secondary_Holm5'],spec.holm(stats['p'][1:]))
        self.assertEqual(stats['LOMO'].shape,(4,6));self.assertEqual(stats['CI'].shape,(2,6))


if __name__=='__main__':unittest.main(verbosity=2)
