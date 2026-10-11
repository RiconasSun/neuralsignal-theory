"""Registration repair isolation; no network or experimental values."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import r2_external_support as original
import run_r2_external_support_code1 as code1


class RepairTests(unittest.TestCase):
    def test_proof_and_output_namespace_do_not_mutate_original(self):
        self.assertEqual(code1.source_audit()['execution_order_proof'],original.ORDERING_PROOF)
        self.assertEqual(original.NAMESPACE,'R2_external_support')
        self.assertEqual(original.POLICY['namespace'],'R2_external_support')
        self.assertEqual(code1.support.NAMESPACE,'R2_external_support_code1')
        self.assertEqual(code1.support.POLICY['namespace'],'R2_external_support_code1')
        self.assertEqual(code1.support.ALLOWED,original.ALLOWED)
        self.assertEqual(code1.support.CLOCK,original.CLOCK)


if __name__=='__main__':
    unittest.main()
