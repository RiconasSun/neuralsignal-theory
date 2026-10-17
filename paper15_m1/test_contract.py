"""Independent synthetic tests. Does not load neural caches or fit a model."""
import csv,itertools,json,math,unittest
from pathlib import Path
import numpy as np
import autograd.numpy as anp
from autograd import grad
from autograd.scipy.special import gammaln as agammaln,logsumexp as alogsumexp
from scipy.stats import poisson
try:from . import synthetic as s
except ImportError:import synthetic as s
P=Path(__file__).resolve().parent
ERRORS=[]

class Contract(unittest.TestCase):
    def test_poisson_factorial_exposure(self):
        y=np.array([[0,2],[3,1]]);eta=np.log(np.array([[2.,4.],[6.,8.]]))
        np.testing.assert_allclose(s.poisson_log_mass(y,eta,.05),poisson.logpmf(y,.05*np.exp(eta)),atol=1e-14)
        self.assertAlmostEqual(s.poisson_log_mass(2,math.log(4),.05),2*math.log(.2)-.2-math.log(2))
        # Actual unit-bin normalization differs from training objective T normalization.
        ll=s.poisson_log_mass(y,eta,.05).sum();self.assertAlmostEqual(ll/y.size,ll/4)
    def test_counts_and_nesting(self):
        q=s.parameter_counts(8);self.assertEqual([q[k] for k in ['B0','B1','B2','B3','B4','D','C','S']],[8,304,336,528,560,571,568,578])
        self.assertEqual(s.parameter_counts(8,3,2)['D'],584);self.assertEqual(s.parameter_counts(8,3,2)['S'],587)
        for u in [5,8,12,20]:
            for k in [2,3]:self.assertGreaterEqual(s.parameter_counts(u,k)['S'],s.parameter_counts(u,k)['D'])
        rng=np.random.default_rng(11);x=rng.normal(size=(4,37));h=rng.normal(size=(4,8,4));a=rng.normal(size=(37,8));b=rng.normal(size=8)
        eta=b+x@a
        np.testing.assert_array_equal(eta,eta+np.einsum('tvl,uvl->tu',h,np.zeros((8,8,4))))
        np.testing.assert_array_equal(eta,eta+s.fixed_state(np.ones((4,8)))@np.zeros((2,8)))
        # The own/other index partition reconstructs every full-history contribution exactly.
        w=rng.normal(size=(8,8,4));full=np.einsum('tvl,uvl->tu',h,w)
        own=np.column_stack([h[:,u,:]@w[u,u,:] for u in range(8)]);off=w.copy()
        for u in range(8):off[u,u]=0
        np.testing.assert_allclose(full,own+np.einsum('tvl,uvl->tu',h,off),atol=1e-14)
    def test_analytic_AD_all_frozen_FD_scales(self):
        rng=np.random.default_rng(37);x=np.column_stack([np.ones(6),rng.normal(size=(6,3))]);y=rng.poisson(.3,size=(6,2));lam=.1
        def independent(theta):
            w=anp.reshape(theta,(4,2));eta=anp.dot(x,w);mu=.05*anp.exp(eta)
            ll=anp.sum(y*(anp.log(.05)+eta)-mu-agammaln(y+1))
            return -ll/6+lam/2*anp.sum(w[1:]**2)
        for label,t in [('initial',np.zeros(8)),('intermediate',rng.normal(0,.1,8)),('fixed_endpoint',np.linspace(-.3,.4,8))]:
            j,g=s.glm_objective_gradient(t,x,y,.05,lam);gref=grad(independent)(t)
            scale=np.maximum(1,np.maximum(abs(g),abs(gref)));aderr=float(np.max(abs(g-gref)/scale));self.assertLessEqual(aderr,1e-8)
            self.assertAlmostEqual(j,float(independent(t)),places=13)
            for step in [1e-4,1e-5,1e-6]:
                fd=np.array([(independent(t+np.eye(8)[i]*step)-independent(t-np.eye(8)[i]*step))/(2*step) for i in range(8)])
                err=float(np.max(abs(g-fd)/np.maximum(1,np.maximum(abs(g),abs(fd)))));self.assertLessEqual(err,1e-5)
                ERRORS.append(dict(point=label,step=step,AD_max_scaled=aderr,FD_max_scaled=err,max_absolute=float(np.max(abs(g-fd)))))
    def test_PG_outward_and_inward(self):
        t=np.array([-1.,-1.,1.,1.,0.]);g=np.array([2.,-3.,-4.,5.,6.])
        np.testing.assert_array_equal(s.projected_gradient(t,g,-1,1),[0,-3,0,5,6])
    def test_hmm_exact_conditional_forward(self):
        pi=np.array([.4,.6]);a=np.array([[.8,.2],[.1,.9]]);e=np.log(np.array([[.3,.8],[.7,.2],[.4,.5],[.9,.1]]))
        for warm in [0,1,2]:self.assertAlmostEqual(s.hmm_forward(e,pi,a,warm),s.hmm_enumeration(e,pi,a,warm),places=13)
        # State offsets zero makes all state emissions equal: recovers factorized B4.
        e0=np.repeat(e[:,:1],2,axis=1);self.assertAlmostEqual(s.hmm_forward(e0,pi,a,1),e[1:,0].sum(),places=13)
    def test_hmm_AD_independent_enumeration_gradient(self):
        pi=np.array([.4,.6]);a=np.array([[.8,.2],[.1,.9]]);e=np.array([[-.3,-.8],[-.7,-.2],[-.4,-.5]])
        paths=list(itertools.product(range(2),repeat=3))
        def enumeration(v):
            z=anp.reshape(v,(3,2));terms=[]
            for p in paths:terms.append(anp.log(pi[p[0]])+sum(z[t,p[t]] for t in range(3))+sum(anp.log(a[p[t-1],p[t]]) for t in range(1,3)))
            return alogsumexp(anp.stack(terms))-alogsumexp(anp.log(pi)+z[0])
        g=grad(enumeration)(e.ravel())
        # Differentiate the independent forward implementation by fixed central differences.
        for step in [1e-4,1e-5,1e-6]:
            fd=np.array([(s.hmm_forward((e.ravel()+np.eye(6)[i]*step).reshape(3,2),pi,a,1)-s.hmm_forward((e.ravel()-np.eye(6)[i]*step).reshape(3,2),pi,a,1))/(2*step) for i in range(6)])
            self.assertLessEqual(np.max(abs(g-fd)),1e-5)
    def test_static_vs_persistent(self):
        pi=np.array([.5,.5]);iid=np.tile(pi,(2,1));e=np.log(np.array([[.9,.1],[.9,.1],[.1,.9]]))
        self.assertAlmostEqual(s.hmm_forward(e,pi,iid,1),s.iid_mixture(e,pi,1),places=13)
        self.assertGreater(abs(s.hmm_forward(e,pi,np.array([[.95,.05],[.05,.95]]),1)-s.iid_mixture(e,pi,1)),.01)
    def test_future_neural_invariance_and_resets(self):
        y=np.arange(60).reshape(20,3);r=np.zeros(20,bool);r[[0,10]]=True
        h=s.causal_lags(y,4,r);c=s.fixed_state(y,2,.1,r);z=y.copy();z[7:]+=9999
        np.testing.assert_array_equal(s.causal_lags(z,4,r)[:8],h[:8]);np.testing.assert_array_equal(s.fixed_state(z,2,.1,r)[:8],c[:8])
        np.testing.assert_array_equal(h[10],0);np.testing.assert_array_equal(c[10],0)
    def test_gap_is_not_zero_observation(self):
        y=np.ones((6,2));v=np.ones(6,bool);v[2]=False;h=s.causal_lags(y,2,valid=v)
        self.assertTrue(np.isnan(h[2]).all());np.testing.assert_array_equal(h[3],0);np.testing.assert_array_equal(h[4,0],1)
        self.assertFalse(v.all()) # whole epoch must be excluded in the production contract
    def test_future_wheel_and_event_availability(self):
        times=np.array([0.,1.,2.,3.]);values=np.array([0.,4.,7.,10.]);self.assertEqual(s.past_lookup(times,values,2.),4)
        z=values.copy();z[2:]=9999;self.assertEqual(s.past_lookup(times,z,2.),4)
        with self.assertRaises(ValueError):s.past_lookup(times,values,0.)
    def test_partitions_and_cohort(self):
        d=s.partition_trials(100);self.assertEqual(d['A'],list(range(59)));self.assertEqual(d['B'],list(range(61,79)));self.assertEqual(d['E'],list(range(81,100)))
        f=s.partition_trials(100,True);self.assertEqual(f['C'][-1],58);self.assertEqual(f['D'][0],61)
        with (P/'COHORT.csv').open(encoding='utf8',newline='') as h:rows=list(csv.DictReader(h))
        self.assertEqual(len(set(x['subject'] for x in rows)),20);self.assertEqual(sum(x['allocation']=='FINAL_RESERVED' for x in rows),8)
        self.assertTrue(all(x['allocation']=='DEVELOPMENT' for x in rows if x['subject'] in ['CSH_ZAD_026','NYU-30']))
    def test_signflip_holm_unavailable(self):
        self.assertEqual(s.sign_flip_p(np.ones(8)),1/256);self.assertEqual(s.sign_flip_p(np.ones(8),True),2/256)
        self.assertEqual(s.sign_flip_p(np.zeros(8)),1);np.testing.assert_allclose(s.holm([.01,.04,.03,1,1]),[.05,.12,.12,1,1])
    def test_control_seed_and_count_preservation(self):
        seed=s.control_seed('N1','synthetic','B',0);self.assertEqual(seed,s.control_seed('N1','synthetic','B',0));self.assertNotEqual(seed,s.control_seed('N1','synthetic','B',1))
        y=np.arange(60).reshape(20,3);z=s.rotate_counts(y,np.random.Generator(np.random.PCG64(seed)))
        np.testing.assert_array_equal(y.sum(axis=0),z.sum(axis=0));self.assertFalse(np.array_equal(y,z))
    def test_projection_finite_boxes(self):
        r=s.dct_projection(8,2);np.testing.assert_allclose(r.T@r,np.eye(2),atol=1e-14)
        for u in [5,8,12,20]:
            eta=8+3*(37+4*u+2)+2;self.assertTrue(np.isfinite(s.poisson_log_mass(100,eta,.05)))
    def test_frozen_fit_budget(self):
        self.assertEqual(1+4*3+2*3*3+2*2*3+2*3*3,61)
        self.assertEqual(12*61+8*12+11*5*20,1928)
    def test_S07_chunk_and_role_stream_regression(self):
        a=s.thinning_seed('synthetic','unit-1','C');self.assertNotEqual(a,s.thinning_seed('synthetic','unit-1','D'))
        self.assertNotEqual(a,s.thinning_seed('synthetic','unit-2','C'))
        full=np.random.Generator(np.random.PCG64(a)).random(101)
        rng=np.random.Generator(np.random.PCG64(a));chunk=np.r_[rng.random(17),rng.random(84)]
        np.testing.assert_array_equal(full,chunk);np.testing.assert_array_equal(full<.4,chunk<.4)
    def test_N2_wheel_interval_and_tie_regression(self):
        times=np.array([0.,.4,.8,1.,1.2]);values=np.array([0.,2.,5.,999.,9999.])
        # epochStart1: values strictly before1 and.5 are5 and2, magnitude3; equality is lower.
        self.assertEqual(s.wheel_stratum(times,values,1.,3.),0);self.assertEqual(s.wheel_stratum(times,values,1.,2.9),1)
        values[3:]=-9999;self.assertEqual(s.wheel_stratum(times,values,1.,3.),0)

def run():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contract))
    receipt=dict(synthetic_only=True,real_neural_access=False,real_model_fits=0,production_worker_certified=False,
        tests=result.testsRun,failures=len(result.failures)+len(result.errors),gradient_errors=ERRORS)
    (P/'work').mkdir(exist_ok=True);(P/'work/SYNTHETIC_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8',newline='\n')
    if not result.wasSuccessful():raise SystemExit(1)
    return receipt
if __name__=='__main__':run()
