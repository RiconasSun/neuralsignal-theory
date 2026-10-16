import unittest
import itertools
from fractions import Fraction
import numpy as np
from . import animal_stats as s


class MouseStatsTests(unittest.TestCase):
    def scores(self,n=8):
        mice=[str(i) for i in range(n)]
        return {mouse:{'B4':-1.,'D':-.9,'C':-.95,'Bstar':-.92,'S':-.91} for mouse in mice},mice

    def test_exact_positive_and_zero_sign_enumeration(self):
        t=s.exact_signflip(np.ones(8));self.assertEqual(t['assignments'],256)
        self.assertEqual(t['exceedances_including_ties'],2);self.assertEqual(t['p'],2/256)
        zero=s.exact_signflip(np.zeros(8));self.assertEqual(zero['p'],1.)
        self.assertEqual(s.exact_signflip(np.array([1.,-1.]*4))['p'],1.)

    def test_Holm_manual_values_and_separate_families(self):
        np.testing.assert_allclose(s.holm([.01,.04,.03]),[.03,.06,.06],atol=1e-15)
        scores,mice=self.scores();result,_=s.summarize(scores,mice)
        for index,name in enumerate(s.CONTRASTS):
            row=result['contrasts'][name]
            self.assertEqual(row['multiplicity_family'],'three_primaries' if index<3 else 'three_interpretation_guards')
            self.assertEqual(row['Holm_adjusted_p'],6/256)

    def test_frozen_joint_whole_mouse_bootstrap_and_quantile(self):
        x=np.arange(48,dtype=float).reshape(8,6)
        interval,indices,means=s.whole_mouse_bootstrap(x)
        expected=np.random.default_rng(130041).integers(0,8,(10000,8),dtype=np.int64)
        np.testing.assert_array_equal(indices,expected)
        np.testing.assert_allclose(means,x[expected].mean(axis=1),atol=0)
        np.testing.assert_array_equal(interval,np.quantile(means,[.025,.975],axis=0,method='linear'))

    def test_exact_contrasts_Lomo_and_equal_mouse_means(self):
        scores,mice=self.scores();scores['7']['D']=-.8
        x=s.contrast_matrix(scores,mice);expected=np.array([.1,.05,.05,.02,-.03,.01])
        np.testing.assert_allclose(x[0],expected,atol=1e-15)
        result,arrays=s.summarize(scores,mice);row=result['contrasts']['D_minus_B4']
        self.assertAlmostEqual(row['mean_nats_per_nominal_unit_bin'],.1125)
        np.testing.assert_allclose(row['leave_one_mouse_out_means'],[np.delete(x[:,0],i).mean() for i in range(8)])
        self.assertEqual(arrays['mouse_contrast_matrix'].shape,(8,6));self.assertTrue(result['equal_mouse_aggregation'])

    def test_no_final_claim_from_statistics_alone(self):
        scores,mice=self.scores();result,_=s.summarize(scores,mice)
        self.assertTrue(result['contrasts']['D_minus_B4']['positive_statistical_conditions_met'])
        self.assertFalse(result['final_claims_evaluated'])
        self.assertTrue(result['contrasts']['C_minus_Bstar']['mean_nats_per_nominal_unit_bin']<0)
        self.assertFalse(result['contrasts']['C_minus_Bstar']['positive_statistical_conditions_met'])

    def test_missing_duplicate_nonfinite_or_insufficient_mouse_denied(self):
        scores,mice=self.scores()
        with self.assertRaises(ValueError):s.contrast_matrix(scores,mice[:7])
        with self.assertRaises(ValueError):s.contrast_matrix(scores,mice[:-1]+['0'])
        scores['0']['D']=float('nan')
        with self.assertRaises(ValueError):s.summarize(scores,mice)
        with self.assertRaises(ValueError):s.exact_signflip(np.ones(7))

    def fraction_oracle(self,values):
        fractions=[Fraction.from_float(float(v)) for v in values];observed=abs(sum(fractions))
        return sum(abs(sum(sign*value for sign,value in zip(signs,fractions)))>=observed
                   for signs in itertools.product([-1,1],repeat=len(values)))

    def test_review_counterexamples_and_Holm_gate_boundary(self):
        first=[.1,.2,.3,-.1,-.2,-.3,.1,.2];second=[.04,.1,-.01,.1,.04,.01,.05,.03]
        for values,count in [(first,170),(second,6)]:
            result=s.exact_signflip(values)
            self.assertEqual(result['exceedances_including_ties'],count)
            self.assertEqual(count,self.fraction_oracle(values))
        p=s.exact_signflip(second)['p'];adjusted=s.holm([p,.5,1.])[0]
        self.assertEqual(adjusted,.0703125);self.assertGreater(adjusted,.05)

    def test_exact_ties_fraction_oracle_and_permutation_invariance(self):
        vectors=[[.1,.2,.3,-.1,-.2,-.3,.1,.2],
                 [1e15,.125,-1e15,.25,.125,-.25,0.,0.],
                 [0.,0.,.1,.1,-.1,-.1,.2,.2],
                 [2**-100,2**-99,-2**-100,0.,.125,-.125,0.,2**-99]]
        for values in vectors:
            expected=self.fraction_oracle(values);base=s.exact_signflip(values)
            self.assertEqual(base['exceedances_including_ties'],expected)
            for order in [list(reversed(range(8))),[3,7,1,6,2,0,5,4]]:
                got=s.exact_signflip([values[i] for i in order])
                self.assertEqual(got['exceedances_including_ties'],expected)


if __name__=='__main__':unittest.main(verbosity=2)
