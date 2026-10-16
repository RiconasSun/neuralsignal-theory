import unittest
import copy
from fractions import Fraction
import numpy as np
from .audit_reduction import compare_score,gamma,check_copies,check_alias


class SavedReductionTests(unittest.TestCase):
    def test_fixed_synthetic_nonpositive_unit_and_grouped_reductions(self):
        rng=np.random.default_rng(130990)
        for scale in [1e-6,1.,1e6]:
            unit=-rng.uniform(.001,10.,(60,30,8))*scale
            original=float(unit[:,5:].sum()/12000)
            proof=compare_score(unit.sum(axis=2),original,'B4')
            self.assertFalse(proof['lossless_per_unit_reconstruction'])
            self.assertIn('not established',proof['premise'])

    def test_exact_dyadic_oracle_and_final_divisions(self):
        unit=-np.geomspace(2.**-30,2.**20,60*30*8).reshape(60,30,8)
        sequence=unit.sum(axis=2);original=float(unit[:,5:].sum()/12000)
        proof=compare_score(sequence,original,'C')
        truth=sum((Fraction.from_float(float(v)) for v in unit[:,5:].ravel()),Fraction(0))/12000
        bin_truth=sum((Fraction.from_float(float(v)) for v in sequence[:,5:].ravel()),Fraction(0))/12000
        bound=Fraction(proof['bound_exact_numerator'],proof['bound_exact_denominator'])
        self.assertLessEqual(abs(Fraction.from_float(original)-truth),abs(truth)*gamma(12001))
        self.assertLessEqual(abs(truth-bin_truth),abs(truth)*gamma(8))
        self.assertLessEqual(abs(Fraction.from_float(original)-Fraction.from_float(float(sequence[:,5:].sum()/12000))),bound)

    def test_material_drift_and_invalid_archives_fail_closed(self):
        sequence=np.full((60,30),-8.)
        proof=compare_score(sequence,-1.,'B0');bound=proof['bound_display']
        with self.assertRaises(RuntimeError):compare_score(sequence,-1.+100*bound,'B0')
        for bad in [np.full((60,30),np.nan),np.full((60,30),.1),np.full((59,30),-8.),sequence.astype(np.float32),sequence.astype(np.int64)]:
            with self.assertRaises(RuntimeError):compare_score(bad,-1.,'B0')

    def test_same_order_D_S_receive_no_rounding_allowance(self):
        sequence=np.full((60,30),-8.)
        for model in ['D','S']:
            self.assertEqual(compare_score(sequence,-1.,model)['mode'],'SAME_ORDER_EXACT')
            with self.assertRaises(RuntimeError):compare_score(sequence,np.nextafter(-1.,0.),model)

    def test_exact_rational_boundary_rejects_first_float_outside(self):
        sequence=np.full((60,30),-8.)
        proof=compare_score(sequence,-1.,'B0')
        limit=Fraction(-1)+Fraction(proof['bound_exact_numerator'],proof['bound_exact_denominator'])
        lower=float(limit)
        if Fraction.from_float(lower)>limit:lower=np.nextafter(lower,-np.inf)
        upper=np.nextafter(lower,np.inf)
        self.assertLessEqual(Fraction.from_float(float(lower)),limit)
        self.assertGreater(Fraction.from_float(float(upper)),limit)
        compare_score(sequence,float(lower),'B0')
        with self.assertRaises(RuntimeError):compare_score(sequence,float(upper),'B0')

    def test_exact_original_score_copies_and_journal_reject_tampering(self):
        final={'scores':{'B2':-1.,'Bstar':-1.}}
        primary={'result':copy.deepcopy(final),'state_identity':{'hash':'original'}}
        completed=[{'scores':copy.deepcopy(final['scores'])}]
        check_copies(primary,final,primary['state_identity'],completed)
        for which in ['primary','journal']:
            p=copy.deepcopy(primary);c=copy.deepcopy(completed)
            (p['result']['scores'] if which=='primary' else c[0]['scores'])['B2']=float(np.nextafter(-1.,0.))
            with self.assertRaises(RuntimeError):check_copies(p,final,primary['state_identity'],c)

    def test_Bstar_B2_score_or_array_one_ulp_change_rejected(self):
        a={'B2':np.full((60,30),-8.),'Bstar':np.full((60,30),-8.)};s={'B2':-1.,'Bstar':-1.}
        check_alias(a,s)
        bad=copy.deepcopy(a);bad['Bstar'][0,0]=np.nextafter(-8.,0.)
        with self.assertRaises(RuntimeError):check_alias(bad,s)
        badscores=dict(s);badscores['Bstar']=float(np.nextafter(-1.,0.))
        with self.assertRaises(RuntimeError):check_alias(a,badscores)

    def test_joint_negative_bins_cannot_certify_unseen_term_signs(self):
        unit=np.full((60,30,8),-1.);unit[:,:,0]=1024.;unit[:,:,1]=-1024.
        sequence=unit.sum(axis=2)
        self.assertTrue((unit>0).any());self.assertTrue((sequence<0).all())
        proof=compare_score(sequence,float(unit[:,5:].sum()/12000),'B0')
        self.assertIn('not established',proof['premise'])
        self.assertFalse(proof['lossless_per_unit_reconstruction'])


if __name__=='__main__':unittest.main()
