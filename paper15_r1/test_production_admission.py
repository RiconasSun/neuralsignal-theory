import unittest
from unittest.mock import patch
from .production_admission import required_hashes,verify

class ProductionAdmissionTests(unittest.TestCase):
    def test_required_complete_corrected_inputs(self):
        keys=required_hashes(['a','b'])
        for key in ['A_FIT_PLAN.json','results/FULL_A_SOURCE_REVALIDATION.json','native_table.py','production_admission.py',
            'metadata/a_task.json','results/b_A_QC.json','states/a_A_PREPROCESSING.json']:
            self.assertIn(key,keys)

    def test_self_declared_or_empty_gate_denied_before_fit(self):
        with patch('paper15_r1.production_admission.admitted',return_value=['a']):
            with self.assertRaises(AssertionError):verify(dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',PRODUCTION_NUMERICAL_PASS=True,hashes={}),{})
            with self.assertRaises(AssertionError):verify(dict(mission='old',PRODUCTION_NUMERICAL_PASS=True),{})

if __name__=='__main__':unittest.main()
