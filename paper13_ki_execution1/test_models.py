"""Independent synthetic mathematical tests; no real neural data or scores."""
import itertools
import unittest
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln,logsumexp
from . import models as m
from . import independent_ad as ad
from .features import nuisance
from unittest.mock import patch

class ModelTests(unittest.TestCase):
    def fixture(self,U=2,E=3,T=9):
        rng=np.random.default_rng(130071);y=rng.poisson(.7,(E,T,U));q=rng.normal(0,.2,(E,T,11))
        return y,q
    def test_baseline_parameter_counts(self):
        y,q=self.fixture(8);expected={'B0':8,'B1':96,'B2':32,'B3':176,'B4':288}
        for name,n in expected.items():
            x,src=m.raw_features(y,q,name);self.assertEqual(x.shape[-1]*8,n);self.assertEqual(src.shape,x.shape[-2:])
    def test_zero_variance_and_training_scaling(self):
        y,q=self.fixture();x,_=m.raw_features(y,q,'B4');s=m.fit_scale(x);z=m.scale(x,s)
        np.testing.assert_allclose(z[:,:,:,0],1);np.testing.assert_allclose(z.mean(axis=(0,1))[:,1:],0,atol=1e-15)
        zeros,_=m.raw_features(y*0,q*0,'B4');self.assertTrue(np.isfinite(m.scale(zeros,m.fit_scale(zeros))).all())
    def test_history_reset_and_no_current_or_future(self):
        y=np.zeros((2,9,2));y[0,0,0]=3;h=m.histories(y)
        self.assertEqual(h[0,1,0,0],3);self.assertEqual(h[0,0].sum(),0);self.assertEqual(h[1].sum(),0)
        yp=y.copy();yp[:,5:]=100
        np.testing.assert_array_equal(m.histories(yp)[:,:6],h[:,:6])
    def test_exact_hmm_against_enumerated_state_paths(self):
        y,_=self.fixture(E=1,T=7);offset=np.full(y.shape,-.7);d=np.array([[-.2,.1],[.3,-.1]]);p=.9
        def evidence(T):
            scores=[]
            for states in itertools.product([0,1],repeat=T):
                ll=-np.log(2)
                for t,s in enumerate(states):
                    if t:ll+=np.log(p if states[t-1]==s else 1-p)
                    eta=offset[0,t]+d[s];ll+=np.sum(y[0,t]*eta-np.exp(eta)-gammaln(y[0,t]+1))
                scores.append(ll)
            return logsumexp(scores)
        expected=evidence(7)-evidence(5)
        actual=m.hmm_eval(d.ravel(),y,offset,p,0,gradient=False,return_scores=True)[:,5:].sum()
        self.assertAlmostEqual(actual,expected,places=12)
    def test_static_mixture_is_iid_not_temporal(self):
        y,_=self.fixture();o=np.zeros(y.shape)-.7;d=np.array([[-.5,.3],[.4,-.2]])
        scores=m.hmm_eval(d.ravel(),y,o,.5,0,gradient=False,return_scores=True)
        eta=o[:,:,None,:]+d[None,None,:,:];em=(y[:,:,None,:]*eta-np.exp(eta)-gammaln(y[:,:,None,:]+1)).sum(-1)
        np.testing.assert_allclose(scores,logsumexp(em,axis=-1)-np.log(2),atol=1e-14)
    def test_hmm_persistence_and_future_perturbation(self):
        y,_=self.fixture();o=np.zeros(y.shape)-.7;d=np.array([[-.5,.3],[.4,-.2]])
        a=m.hmm_eval(d.ravel(),y,o,.98,0,gradient=False,return_scores=True)
        yp=y.copy();yp[:,-1]=20
        b=m.hmm_eval(d.ravel(),yp,o,.98,0,gradient=False,return_scores=True)
        np.testing.assert_allclose(a[:,:-1],b[:,:-1]);self.assertGreater(np.max(np.abs(a-b)),0)
    def test_hmm_joint_unit_denominator(self):
        y,_=self.fixture();o=np.zeros_like(y,dtype=float);theta=np.zeros(4)
        loss=m.hmm_eval(theta,y,o,.9,0,gradient=False)
        self.assertAlmostEqual(loss,-m.poisson_scores(y[:,5:],o[:,5:]).mean())
    def test_hmm_analytical_matches_independent_AD_and_FD(self):
        y,_=self.fixture();o=np.zeros_like(y,dtype=float)-.6;w=np.array([.2,-.3,-.1,.4])
        for p in [.5,.9,.98]:
            v,g=m.hmm_eval(w,y,o,p,.1);av,ag=ad.hmm(w,y,o,p,.1)
            self.assertAlmostEqual(v,av,places=12);self.assertLess(m.gradient_errors(g,ag)['max_relative'],1e-10)
            fd=m.finite_difference(lambda z:m.hmm_eval(z,y,o,p,.1,gradient=False),w)
            self.assertLess(m.gradient_errors(g,fd)['max_relative'],1e-5)
    def test_glm_all_baselines_independent_AD_and_FD(self):
        y,q=self.fixture()
        for name in ['B0','B1','B2','B3','B4']:
            x,_=m.raw_features(y,q,name);x=m.scale(x,m.fit_scale(x));w=m.glm_initial(x,y,11)
            v,g=m.glm_eval(w,x,y,.1);av,ag=ad.glm(w,x,y,.1)
            self.assertAlmostEqual(v,av,places=12);self.assertLess(m.gradient_errors(g,ag)['max_relative'],1e-10)
            fd=m.finite_difference(lambda z:m.glm_eval(z,x,y,.1,gradient=False),w)
            self.assertLess(m.gradient_errors(g,fd)['max_relative'],1e-5)
    def test_continuous_lag_QR_and_no_future(self):
        y,_=self.fixture();q=m.projection(11,2);np.testing.assert_allclose(q.T@q,np.eye(2),atol=1e-15)
        h=m.leaky(y,[.1,.3],q,np.zeros(2),np.ones(2));self.assertEqual(h[:,0].sum(),0)
        np.testing.assert_allclose(h[:,1],(1-np.exp(-.1/np.array([.1,.3])))*(y[:,0]@q))
        yp=y.copy();yp[:,-1]=500
        np.testing.assert_allclose(h,m.leaky(yp,[.1,.3],q,np.zeros(2),np.ones(2)))
    def test_continuous_16coef_and_independent_AD(self):
        y,_=self.fixture(U=8);x,s=m.continuous_features(y,[.3,1],11);w=np.linspace(-.1,.1,16);o=np.zeros_like(y,dtype=float)-.6
        v,g=m.glm_eval(w,x,y,.1,offset=o,penalize_intercept=True)
        av,ag=ad.glm(w,x,y,.1,offset=o,penalize_intercept=True)
        self.assertAlmostEqual(v,av,places=12);self.assertLess(m.gradient_errors(g,ag)['max_relative'],1e-10)
    def test_original_bound_projected_gradient_polarity(self):
        self.assertEqual(m.pg([-8,8,0],[3,-4,.0004]),.0004)
        self.assertEqual(m.pg([-8,8],[-3,4]),4)
    def test_bound_aware_fixed_FD(self):
        w=np.array([-8.,8.,2]);fd=m.finite_difference(lambda x:np.sum(x*x),w)
        np.testing.assert_allclose(fd,2*w,atol=1e-9)
    def test_regularization_normalization_and_no_intercept_penalty(self):
        y,q=self.fixture();x,_=m.raw_features(y,q,'B1');w=np.ones(x.shape[-2]*x.shape[-1])*.1
        v,g=m.glm_eval(w,x,y,1);v0,g0=m.glm_eval(w,x,y,0)
        b=w.reshape(2,-1);self.assertAlmostEqual(v-v0,np.sum(b[:,1:]**2)/4)
        np.testing.assert_allclose((g-g0).reshape(2,-1)[:,0],0,atol=1e-15)
    def test_synthetic_optimizer_fits_and_endpoint_AD(self):
        y,q=self.fixture(E=12,T=30);x,_=m.raw_features(y,q,'B4');x=m.scale(x,m.fit_scale(x));w=m.glm_initial(x,y,11)
        result=minimize(lambda z:m.glm_eval(z,x,y,.1),w,jac=True,method='L-BFGS-B',bounds=[(-8,8)]*len(w),options={'maxiter':2000,'maxfun':100000,'maxls':40,'maxcor':10,'ftol':1e-12,'gtol':1e-5})
        self.assertLessEqual(m.pg(result.x,result.jac),.001)
        av,ag=ad.glm(result.x,x,y,.1);self.assertLess(m.gradient_errors(result.jac,ag)['max_relative'],1e-5)
    def test_event_covariates_cannot_read_same_bin_future(self):
        events={'tone':np.array([1.,2.,3.05]),'noise':np.array([]),'airpuff':np.array([]),'opto':np.array([])}
        with patch('paper13_ki_execution1.features.event_series',return_value=events):
            q=nuisance({},[{'start':3.,'stop':6.,'ordinal':1}])
        self.assertEqual(q.shape,(1,30,11));self.assertEqual(q[0,0,7],2)
        self.assertAlmostEqual(q[0,0,6],np.log1p(1));self.assertAlmostEqual(q[0,1,6],np.log1p(.05))

if __name__=='__main__':unittest.main(verbosity=2)
