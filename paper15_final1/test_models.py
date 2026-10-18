"""Actual production equations and gradients; entirely synthetic input fixtures."""
import itertools
import json
import unittest
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp
from scipy.stats import poisson
from .models import Model, pg
from .independent_ad import coordinate_check
from .source import P, dump


def fixture(family='B4',k=2):
    rng=np.random.Generator(np.random.PCG64(150301))
    u=2;n=2;l=6;p=1+2+4*u+(2 if family=='C' else 0)
    x=rng.normal(0,.3,(n,l,p));x[:,:,0]=1;y=rng.poisson(.4,(n,l,u))
    return Model(x,y,family,.1,k=k,warm=2,nuisance=2)


class ProductionModels(unittest.TestCase):
    def test_all_coordinate_gradients_at_three_points(self):
        rows=[]
        for family in ['B0','B1','B2','B3','B4','C','D','S']:
            m=fixture(family);start=m.initialize(11)
            middle=start+.03*np.sin(np.arange(m.size));b=np.asarray(m.bounds);middle=np.clip(middle,b[:,0],b[:,1])
            fit=minimize(m.objective,start,jac=True,method='L-BFGS-B',bounds=m.bounds,
                options=dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6))
            self.assertLessEqual(pg(fit.x,m.objective(fit.x)[1],m.bounds),.001)
            for name,theta in [('initial',start),('fixed_intermediate',middle),('synthetic_endpoint',fit.x)]:
                check=coordinate_check(m,theta,synthetic=True)
                rows.append(dict(family=family,point=name,parameters=theta.tolist(),check=check))
                self.assertTrue(check['PASS'],(family,name,check['AD_max_scaled'],[(x['step'],x['max_scaled']) for x in check['FD']]))
        dump(P/'work/PRODUCTION_GRADIENT_SYNTHETIC.json',rows)
    def test_poisson_exact_factorial_exposure_and_denominator(self):
        m=fixture('B4');theta=m.initialize();w=m.unpack(theta)[0];eta=m.x@w
        expected=poisson.logpmf(m.y,m.delta*np.exp(eta))[:,m.warm:].sum()
        self.assertAlmostEqual(m.objective(theta)[0],-expected/m.T,places=12)
        self.assertAlmostEqual(m.prebin_logmasses(theta)[:,m.warm:].sum(),expected,places=12)
        self.assertNotAlmostEqual(m.objective(theta)[0],-expected/(m.T*m.u))
    def test_nominal_parameter_counts(self):
        u=8;x=np.zeros((1,20,70));x[:,:,0]=1;y=np.zeros((1,20,u))
        expected=dict(B0=8,B1=304,B2=336,B3=528,B4=560,D=571,S=578)
        for family,n in expected.items():
            self.assertEqual(Model(x,y,family,k=3 if family=='S' else 2).size,n)
        self.assertEqual(Model(x,y,'D',k=3).size,584)
        self.assertEqual(Model(x,y,'S',k=4).size,587)
        self.assertEqual(Model(np.pad(x,((0,0),(0,0),(0,2))),y,'C').size,576)
    def test_nested_predictions_and_constant_coordinates(self):
        ms=[fixture(f) for f in ['B0','B1','B2','B3','B4']]
        for m in ms:
            theta=m.initialize();self.assertTrue(np.allclose(m.prebin_logmasses(theta),ms[0].prebin_logmasses(ms[0].initialize())))
        m=fixture();active=np.ones(m.p,bool);active[3]=False
        limited=Model(m.x,m.y,'B4',active=active,warm=2,nuisance=2)
        self.assertEqual(limited.size,m.size-m.u);self.assertTrue((limited.unpack(limited.initialize())[0][3]==0).all())
    def test_nonzero_nested_model_embeddings_and_dynamic_reductions(self):
        base=fixture('B1');theta=base.initialize();theta[2:]+=.12
        w=base.unpack(theta)[0];expected=base.prebin_logmasses(theta)
        for family in ['B2','B3','B4','D','S']:
            m=fixture(family);v=m.initialize();v[:m.nlin]=w[m.mask]
            if family in ('D','S'):v[m.nlin:]=0
            np.testing.assert_allclose(m.prebin_logmasses(v),expected,atol=1e-12)
        c=fixture('C');v=c.initialize();wc=np.zeros((c.p,c.u));wc[:base.p]=w;v[:c.nlin]=wc[c.mask]
        # C's additional fixture columns are appended, base fixture prefixes identical.
        same=Model(np.concatenate([base.x,np.ones((*base.x.shape[:2],2))],axis=-1),base.y,'C',warm=2,nuisance=2)
        vs=same.initialize();ws=np.zeros((same.p,same.u));ws[:base.p]=w;vs[:same.nlin]=ws[same.mask]
        np.testing.assert_allclose(same.prebin_logmasses(vs),expected,atol=1e-12)
    def test_hmm_conditional_exact_bruteforce(self):
        m=fixture('D');theta=m.initialize();theta[m.nlin:m.nlin+m.u]=[.4,-.3]
        w,off,logP,logpi=m.unpack(theta);eta=m.x@w
        e=(m.y[:,:,None,:]*(np.log(m.delta)+eta[:,:,None,:]+off)-m.delta*np.exp(eta[:,:,None,:]+off)-gammaln(m.y[:,:,None,:]+1)).sum(-1)
        expected=0.
        for seq in e:
            values=[]
            for length in [len(seq),m.warm]:
                terms=[]
                for path in itertools.product(range(m.k),repeat=length):
                    z=logpi[path[0]]+sum(seq[t,s] for t,s in enumerate(path))+sum(logP[path[t-1],path[t]] for t in range(1,length));terms.append(z)
                values.append(logsumexp(terms))
            expected+=values[0]-values[1]
        self.assertAlmostEqual(m.prebin_logmasses(theta)[:,m.warm:].sum(),expected,places=11)
    def test_IID_transition_equals_static_same_K(self):
        d=fixture('D');s=fixture('S');td=d.initialize();ts=s.initialize()
        td[d.nlin+(d.k-1)*d.u:]=0;ts[s.nlin+(s.k-1)*s.u:]=0
        np.testing.assert_allclose(d.prebin_logmasses(td),s.prebin_logmasses(ts),atol=1e-12)
        self.assertAlmostEqual(d.objective(td)[0],s.objective(ts)[0],places=12)
    def test_static_not_persistent_filter(self):
        d=fixture('D');s=fixture('S');td=d.initialize();ts=s.initialize()
        off=np.array([1.,-.8]);td[d.nlin:d.nlin+2]=off;ts[s.nlin:s.nlin+2]=off
        self.assertGreater(float(np.max(np.abs(d.prebin_logmasses(td)-s.prebin_logmasses(ts)))),1e-5)
    def test_future_neural_filter_perturbation_invariance(self):
        m=fixture('D');theta=m.initialize();original=m.prebin_logmasses(theta)
        y=m.y.copy();y[:,4:]+=20;other=Model(m.x,y,'D',warm=2,nuisance=2)
        np.testing.assert_allclose(original[:,:4],other.prebin_logmasses(theta)[:,:4],atol=0)
    def test_outward_bound_pg_signs(self):
        theta=np.array([-1.,1.,-1.,1.]);g=np.array([3.,-3.,-2.,2.]);bounds=[(-1,1)]*4
        self.assertEqual(pg(theta,g,bounds),2.)
        self.assertEqual(pg(theta[:2],g[:2],bounds[:2]),0.)
    def test_invalid_values_fail_closed(self):
        m=fixture();bad=m.y.copy();bad[0,0,0]=-1
        with self.assertRaises(AssertionError):Model(m.x,bad,'B4',warm=2,nuisance=2)
        x=m.x.copy();x[0,0,0]=np.nan
        with self.assertRaises(AssertionError):Model(x,m.y,'B4',warm=2,nuisance=2)
    def test_ridge_intercept_exemption_and_three_seeds(self):
        m=fixture('D');theta=m.initialize(11)
        self.assertTrue((m.penalty[:m.u]==0).all());self.assertTrue((m.penalty[m.u:]==1).all())
        np.testing.assert_array_equal(theta,m.initialize(11));self.assertFalse(np.array_equal(theta,m.initialize(23)))
    def test_larger_state_grids_and_boundary_extension_derivatives(self):
        for family,k in [('D',3),('S',3),('S',4)]:
            m=fixture(family,k);theta=m.initialize(37)
            theta[0]=-8.;theta[m.u]=1.;theta[m.nlin]=2.
            check=coordinate_check(m,theta,synthetic=True)
            self.assertTrue(check['PASS'],(family,k,check['AD_max_scaled'],[(x['step'],x['max_scaled']) for x in check['FD']]))
    def test_value_only_is_identical_mathematical_objective(self):
        for family in ['B0','B1','B2','B3','B4','C','D','S']:
            m=fixture(family);v=m.initialize();v+=.02*np.cos(np.arange(len(v)))
            self.assertAlmostEqual(m.value(v),m.objective(v)[0],places=12)


if __name__=='__main__':unittest.main(verbosity=2)
