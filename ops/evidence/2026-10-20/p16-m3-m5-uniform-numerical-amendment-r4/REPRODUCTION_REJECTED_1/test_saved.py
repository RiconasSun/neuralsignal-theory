"""Pure saved arithmetic regressions; no neural/model functions imported."""
import unittest
from . import reproduce_saved as saved


class SavedTests(unittest.TestCase):
    def test_unknown_or_partial_call_record_never_counted_as_complete(self):
        a={'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]}
        self.assertEqual(saved.prior.call_prefix([a],1),(1,0))
        with self.assertRaises(RuntimeError):saved.prior.call_prefix([{'event':'COMPLETED','call':1}],1)
        with self.assertRaises(RuntimeError):saved.prior.call_prefix([{**a,'call':2}],1)

    def test_full_coordinate_diagnostic_prefix_keeps_frozen_step(self):
        d=[{'kind':'ANALYTIC_RESERVED','checkpoint':'initial','index':1},
           {'kind':'AD_RESERVED','checkpoint':'initial','index':1}]
        self.assertEqual(saved.prior.diagnostic_prefix(d,1),{'FD_RESERVED':0,'AD_RESERVED':1,'ANALYTIC_RESERVED':1})
        with self.assertRaises(RuntimeError):saved.prior.diagnostic_prefix(d+[{'kind':'FD_RESERVED','checkpoint':'initial','index':1,'h':.003,'coordinate':0,'side':'plus'}],1)

    def test_bound_signs_do_not_zero_inward_gradient(self):
        import numpy as np
        np.testing.assert_array_equal(saved.prior.projected(np.array([-1.,1.,-1.,1.]),np.array([2.,-3.,-4.,5.]),-1,1),[0.,0.,-4.,5.])

    def test_missing_and_tampered_manifest_fail_closed(self):
        from unittest.mock import patch
        with self.assertRaises(RuntimeError):saved.identities({'files':[{'path':'paper16_development_r4/MISSING_REQUIRED_STATE','sha256':'0'*64}]})
        row={'path':'paper16_development_r4/UNIFORM_NUMERICAL_AMENDMENT.json','sha256':'0'*64}
        with self.assertRaises(RuntimeError):saved.identities({'files':[row]})


if __name__=='__main__':unittest.main(verbosity=2)
