"""Regression for negative replay without parameters or constructible models."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import r2_saved_audit as audit


class SavedAuditTests(unittest.TestCase):
    def test_constructor_failure_without_theta_never_reconstructed(self):
        row = {'converged':False,'error':'ValueError: fixture constructor','seed':11}
        with patch.object(audit.run,'make_pair',side_effect=AssertionError('must never construct')):
            result = audit.check_row(row,None)
        self.assertEqual(result['state'],'PRESERVED_FAILURE')
        self.assertFalse(result['refitted'])
        self.assertIs(result['record'],row)


if __name__=='__main__':
    unittest.main()
