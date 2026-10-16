"""Registered family integration, shared offsets, scaling and selection oracles."""
import uuid
import unittest
from unittest.mock import patch
import numpy as np
from scipy.special import gammaln
from . import families as f
from .fit_engine import derivatives


class FamilyTests(unittest.TestCase):
    def data(self):
        rng=np.random.default_rng(97)
        y=rng.poisson(.2,(6,30,8));q=rng.normal(size=(6,30,11))
        raw,_=f.m.raw_features(y,q,'B4');scaler=f.m.fit_scale(raw)
        theta=np.zeros((8,36));theta[:,0]=np.log(.2);theta[:,1]=.01
        state={k:v.tolist() for k,v in scaler.items()}
        return y,q,theta.ravel(),state

    def test_exact_27_D_and_27_C_schedules_16_parameters(self):
        self.assertEqual(len(f.D_schedule()),27);self.assertEqual(len(set(f.D_schedule())),27)
        self.assertEqual(len(f.C_schedule()),27);self.assertEqual(len(set(f.C_schedule())),27)
        self.assertEqual({seed for _,_,seed in f.C_schedule()},{11,23,37})
        self.assertEqual(10*(27+27)+390,930)

    def test_zero_D_C_shifts_equal_same_B4_normalization(self):
        y,q,theta,state=self.data();offset=f.baseline_offset(y,q,theta,state)
        baseline=float(f.m.poisson_scores(y[:,5:],offset[:,5:]).sum()/y[:,5:].size)
        for p in f.PS:self.assertAlmostEqual(f.family_score('D',np.zeros(16),y,offset,p=p),baseline,13)
        x,_=f.continuous_design(y,(.1,.3),11)
        self.assertEqual(x.shape,(6,30,8,2))
        self.assertAlmostEqual(f.family_score('C',np.zeros(16),y,offset,x=x),baseline,13)

    def test_C_B_transform_reuses_exact_A_projection_and_scales(self):
        y,_,_,_=self.data();x,state=f.continuous_design(y,(.3,1.),23)
        yb=y+3;before=f.b.canonical(state)
        with patch.object(f.m,'projection',side_effect=AssertionError('B projection refit')):
            xb,unchanged=f.continuous_design(yb,(.3,1.),23,state)
        self.assertEqual(before,f.b.canonical(unchanged));self.assertEqual(before,f.b.canonical(state))
        self.assertGreater(abs(float(xb.mean())),.01)
        np.testing.assert_allclose(np.asarray(state['Q']).T@np.asarray(state['Q']),np.eye(2),atol=1e-15)
        future=yb.copy();future[:,-1]+=100
        xf,_=f.continuous_design(future,(.3,1.),23,state)
        np.testing.assert_array_equal(xb,xf)

    def test_static_S_is_joint_not_product_marginal_mixture(self):
        y,_,_,_=self.data();offset=np.full_like(y,-1.5,dtype=float)
        delta=np.stack([np.full(8,-.4),np.full(8,.4)])
        eta=offset[:,:,None,:]+delta[None,None,:,:]
        emission=y[:,:,None,:]*eta-np.exp(eta)-gammaln(y[:,:,None,:]+1)
        joint=np.logaddexp(emission.sum(axis=3)[:,:,0],emission.sum(axis=3)[:,:,1])-np.log(2.)
        expected=float(joint[:,5:].sum()/y[:,5:].size)
        actual=f.family_score('D',delta.ravel(),y,offset,p=.5)
        marginal=(np.logaddexp(emission[:,:,0,:],emission[:,:,1,:])-np.log(2.))[:,5:].mean()
        self.assertAlmostEqual(actual,expected,13);self.assertGreater(abs(actual-marginal),1e-5)

    def test_global_one_SE_ties_use_registered_memory_seed_priorities(self):
        D=[{'p':p,'ridge':ridge} for p in f.PS for ridge in f.RIDGES]
        C=[{'tau':list(tau),'ridge':ridge,'seed':seed} for tau,ridge,seed in f.C_schedule()]
        self.assertEqual(f.choose_configuration(np.zeros((8,9)),D,'D')['selected_configuration'],{'p':.5,'ridge':10.})
        self.assertEqual(f.choose_configuration(np.zeros((8,27)),C,'C')['selected_configuration'],{'tau':[.1,.3],'ridge':10.,'seed':11})
        result=f.choose_configuration(np.tile(np.arange(8)[:,None]*100,(1,27)),C,'C')
        self.assertEqual(result['selected_configuration']['seed'],11)
        self.assertEqual(len(result['all_configurations']),27)

    def test_fresh_M4_approval_required_before_prior_stage_or_values(self):
        root=f.P/'work'/('M4_denial_'+uuid.uuid4().hex);root.mkdir(parents=True)
        with patch.object(f,'P',root),patch.object(f,'prior_gates',side_effect=AssertionError('stage before approval')):
            with self.assertRaises(PermissionError):f.run()

    def test_missing_fullM3_selection_blocks_real_family_fits(self):
        with patch.object(f.dev,'approved',return_value='B-code'),patch.object(f.dev,'numerical_gate',return_value=({}, {}, {})),patch.object(f.b,'read',return_value={'M3':'PENDING'}):
            with self.assertRaises(f.ScientificStop):f.prior_gates()

    def test_independent_16_parameter_D_C_AD_and_fixedFD(self):
        y,q,theta,state=self.data();offset=f.baseline_offset(y,q,theta,state)
        w=np.random.default_rng(11).normal(0,.05,16)
        D=derivatives('HMM',w,{'y':y},.1,p=.9,offset=offset)
        x,_=f.continuous_design(y,(.1,.3),11)
        C=derivatives('C',np.zeros(16),{'y':y,'x':x},.1,offset=offset)
        for certificate in [D,C]:
            self.assertTrue(certificate['pass']);self.assertEqual(len(certificate['theta']),16)
            self.assertLess(certificate['AD_error']['max_relative'],1e-10)
            self.assertLess(certificate['fixed_FD_error']['max_relative'],1e-5)


if __name__=='__main__':unittest.main(verbosity=2)
