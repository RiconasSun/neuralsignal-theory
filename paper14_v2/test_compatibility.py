"""Regression for the frozen row-preserving compatibility gate."""
import unittest
from .compatibility import numeric,categories,bridge_pass

class CompatibilityTests(unittest.TestCase):
    def test_finite_identity(self):
        s,b=numeric([1.,2.,None],[1.,2.,None]);self.assertTrue(s['match']);self.assertFalse(b.any())
    def test_fixed_tolerance(self):
        self.assertTrue(numeric([0.],[.9e-6])[0]['match'])
        self.assertFalse(numeric([0.],[1.1e-6])[0]['match'])
    def test_missingness_not_ignored_by_nanmax(self):
        s,b=numeric([None,2.],[1.,2.]);self.assertFalse(s['match']);self.assertEqual(s['missingness_mismatches'],1)
    def test_no_row_truncation(self):
        with self.assertRaises(ValueError):numeric([1.],[1.,2.])
    def test_no_row_reordering(self):self.assertFalse(numeric([2.,1.],[1.,2.])[0]['match'])
    def test_context_exact_no_time_tolerance(self):self.assertFalse(numeric([.2],[.2000001],0)[0]['match'])
    def test_categorical_discrepancy_fails(self):self.assertFalse(categories(['none'],['clockwise'])['match'])
    def test_any_required_mismatch_fails_bridge(self):self.assertFalse(bridge_pass({'stim':{'match':True},'movement':{'match':False}},True))
    def test_identity_required(self):self.assertFalse(bridge_pass({'stim':{'match':True}},False))
    def test_empty_bridge_never_passes(self):self.assertFalse(bridge_pass({},True))

if __name__=='__main__':unittest.main()
