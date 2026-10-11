"""Network-recovery namespaces never mutate the original registered auditor."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import r2_external_support as original
import run_r2_external_support_code1 as code1
import run_r2_external_support_code2 as code2


class RecoveryTests(unittest.TestCase):
    def test_exact_same_policy_except_output_namespace(self):
        self.assertEqual(code2.adapter.support.NAMESPACE,'R2_external_support_code2')
        self.assertEqual(code1.support.NAMESPACE,'R2_external_support_code1')
        self.assertEqual(original.NAMESPACE,'R2_external_support')
        self.assertEqual(code2.adapter.support.ALLOWED,original.ALLOWED)
        self.assertEqual({k:v for k,v in code2.adapter.support.POLICY.items() if k!='namespace'},
                         {k:v for k,v in original.POLICY.items() if k!='namespace'})
        self.assertEqual(code2.adapter.support.CLOCK,original.CLOCK)


if __name__=='__main__':
    unittest.main()
