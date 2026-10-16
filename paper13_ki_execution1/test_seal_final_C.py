import unittest
from unittest.mock import patch
from . import seal_final_C as s


class SealTests(unittest.TestCase):
    def test_unapproved_source_or_incomplete_gate_denies_before_model_neural_open(self):
        with patch.object(s.final_C,'approved',side_effect=PermissionError('notreviewed')),patch.object(s.b,'read',side_effect=AssertionError('state before approval')):
            with self.assertRaises(PermissionError):s.run()
        for gate in [{'FINAL_C_NUMERICS':'FAIL'}, {'FINAL_C_NUMERICS':'PASS','source_freeze':'source','required':198,'completed':197,'fits':[]}]:
            with patch.object(s.final_C,'approved',return_value='source'),patch.object(s.b,'read',return_value=gate),patch.object(s.final_C,'load_C',side_effect=AssertionError('counts before valid saved gate')):
                with self.assertRaises(s.ScientificStop):s.run()
