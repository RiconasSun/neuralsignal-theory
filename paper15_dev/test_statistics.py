"""Registered mouse-level inference with explicit exploratory interpretation."""
import unittest
import numpy as np
from paper15_m1.synthetic import sign_flip_p,holm as frozen_holm
from .statistics import sign_flip,holm,summarize,analyze,PRIMARY,SECONDARY


class StatisticsTests(unittest.TestCase):
    def test_exhaustive_signs_match_frozen_oracle(self):
        values=np.array([.1,.2,-.1,.4])
        self.assertEqual(sign_flip(values),sign_flip_p(values))
        self.assertEqual(sign_flip(values,True),sign_flip_p(values,True))
        self.assertEqual(sign_flip(np.ones(8)),1/256)
        self.assertEqual(sign_flip(np.ones(8),True),2/256)
    def test_Holm_fixed_family_including_unavailable(self):
        p=np.array([.001,.02,1.,.05,.5]);np.testing.assert_array_equal(holm(p),frozen_holm(p))
        self.assertEqual(len(holm(p)),5);self.assertEqual(holm(p)[2],1.)
    def test_whole_mouse_equal_weight_not_pooled_unit_bins(self):
        rows=[dict(subject='a',lab='L1',models={'B4':dict(LL=2,unit_bins=10),'B1':dict(LL=0,unit_bins=10)}),
            dict(subject='b',lab='L2',models={'B4':dict(LL=1,unit_bins=100),'B1':dict(LL=0,unit_bins=100)})]
        r=analyze(rows,['a','b']);self.assertAlmostEqual(r[PRIMARY]['equal_mouse_mean'],.105)
        self.assertFalse(r[PRIMARY]['validated']);self.assertFalse(r[PRIMARY]['heldout_animal_confirmation'])
        self.assertTrue(all(r[k]['Holm5_adjusted_p']==1. for k in SECONDARY))
    def test_fixed_bootstrap_reproducibility_and_lab_diagnostics(self):
        d=np.arange(8)/1000;labs=['A','A','B','B','C','D','E','F']
        first=summarize(d,labs,PRIMARY);second=summarize(d,labs,PRIMARY)
        self.assertEqual(first,second);self.assertEqual(first['bootstrap_replicates'],10000)
        self.assertEqual(len(first['leave_one_mouse_out_means']),8);self.assertEqual(len(first['leave_one_lab_out_means']),6)
        self.assertIn('asymmetry',first['inferential_assumption'])
    def test_denominator_mismatch_is_rejected(self):
        row=dict(subject='a',lab='L',models={'B4':dict(LL=1,unit_bins=10),'B1':dict(LL=0,unit_bins=20)})
        with self.assertRaises(AssertionError):analyze([row],['a'])
    def test_primary_missing_duplicate_or_unexpected_mouse_is_rejected(self):
        a=dict(subject='a',lab='L',models={'B4':dict(LL=1,unit_bins=10),'B1':dict(LL=0,unit_bins=10)})
        b=dict(subject='b',lab='M',models={'B4':dict(LL=1,unit_bins=10)})
        with self.assertRaises(AssertionError):analyze([a,b],['a','b'])
        with self.assertRaises(AssertionError):analyze([a,a],['a','b'])
        with self.assertRaises(AssertionError):analyze([a],['a','b'])
    def test_secondary_missing_one_mouse_stays_unavailable_not_partial(self):
        a=dict(subject='a',lab='L',models={'B4':dict(LL=1,unit_bins=10),'B1':dict(LL=0,unit_bins=10),'D':dict(LL=2,unit_bins=10)})
        b=dict(subject='b',lab='M',models={'B4':dict(LL=1,unit_bins=10),'B1':dict(LL=0,unit_bins=10)})
        result=analyze([a,b],['a','b'])
        self.assertEqual(result['D-B4']['status'],'UNAVAILABLE_FIXED_COHORT');self.assertEqual(result['D-B4']['paired_sign_flip_p'],1.)
        self.assertEqual(result['D-B4']['missing_subjects'],['b'])


if __name__=='__main__':unittest.main(verbosity=2)
