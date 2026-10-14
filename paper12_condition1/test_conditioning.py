import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'frozen_sources'))
import unittest
import numpy as np
from conditioning import hessian,spectrum,scale_from_diagonal,saturation
from policies import Coordinates,physical_pg,adam_step,run
from model_math import make,objective
from independent_ad import value_gradient

def fixture(dimension=2):
    rng=np.random.default_rng(20261014);y=rng.poisson(.3,size=(2,6,2));x=rng.normal(0,.1,size=(2,6,3));offset=np.full(y.shape,-.7);model=make('Continuous',y,x,offset,dimension);return model,model.initial(11)
def toy_policy(kind):
    p={'kind':kind,'objective_gradient_call_cap':500,'options':{'maxiter':200,'maxfun':450,'ftol':1e-14,'gtol':1e-9,'maxls':30,'maxcor':10}}
    if kind=='adam_lbfgsb':p.update(warm_steps=6,warm_schedule=[[2,.01],[4,.003],[6,.001]],beta1=.9,beta2=.999,epsilon=1e-8)
    if kind=='trust_constr':p['options']={'maxiter':200,'gtol':1e-9,'xtol':1e-12,'barrier_tol':1e-10,'sparse_jacobian':True,'factorization_method':'AugmentedSystem','initial_tr_radius':1.,'initial_constr_penalty':1.,'initial_barrier_parameter':.1,'initial_barrier_tolerance':.1,'verbose':0}
    return p

class NumericalSupport(unittest.TestCase):
    def test_exact_indefinite_quadratic_hessian(self):
        q=np.array([[3.,.5],[.5,-2.]])
        x=np.array([.2,-.3]);H,c=hessian(x,lambda t:(float(t@q@t/2),q@t),1e-7)
        np.testing.assert_allclose(H,q,atol=1e-8,rtol=0);self.assertEqual(spectrum(H)['negative_count'],1);self.assertEqual(c,0)
    def test_ill_conditioned_spectrum(self):
        result=spectrum(np.diag([1e-12,1,1e6]));self.assertEqual(result['near_zero_count'],1);self.assertAlmostEqual(result['resolved_abs_condition_estimate'],1e6)
    def test_scale_rule_deterministic_positive(self):
        np.testing.assert_allclose(scale_from_diagonal(np.array([0.,-4.,1e16])),[1000.,.5,1e-4]);self.assertTrue(np.isfinite(scale_from_diagonal(np.zeros(4))).all())
    def test_coordinate_domain_and_inverse(self):
        c=Coordinates([.001,1000]);theta=np.array([-8.,8.]);np.testing.assert_allclose(c.forward(c.inverse(theta)),theta,atol=1e-15);np.testing.assert_allclose(c.forward(c.bounds[:,0]),[-8,-8]);np.testing.assert_allclose(c.forward(c.bounds[:,1]),[8,8])
    def test_transformed_chain_rule_and_ridge(self):
        model,t=fixture();s=np.geomspace(.01,10,len(t));c=Coordinates(s);z=c.inverse(t);f,g=objective(t,model,.001);f2,g2=objective(c.forward(z),model,.001);adf,adg,_=value_gradient(c.forward(z),model.y,model.x,model.offset,2,.001)
        self.assertAlmostEqual(f,f2,places=12);np.testing.assert_allclose(c.gradient(g2),s*adg,atol=1e-10,rtol=0);self.assertAlmostEqual(f2,adf,places=12)
    def test_recurrent_hessian_symmetry_and_AD(self):
        model,t=fixture(1);H,_=hessian(t,lambda z:objective(z,model,.001),1e-6);self.assertLess(spectrum(H)['asymmetry_inf_relative'],1e-7);f,g=objective(t,model,.001);v,a,_=value_gradient(t,model.y,model.x,model.offset,1,.001);np.testing.assert_allclose(g,a,atol=1e-12);self.assertAlmostEqual(f,v,places=12)
    def test_tanh_saturation_stress(self):
        model,t=fixture();low=saturation(t,model.y,model.x,2);high=t.copy();high[:4]=8;high[4:]=8;stress=saturation(high,model.y,model.x,2);self.assertGreater(stress['fraction_abs_gt_0.99'],low['fraction_abs_gt_0.99']);self.assertTrue(stress['finite'])
    def test_original_physical_projection(self):
        self.assertEqual(physical_pg(np.array([-8.,8.]),np.array([2.,-3.])),0);self.assertEqual(physical_pg(np.array([-8.,8.]),np.array([-2.,3.])),3)
    def test_adam_closed_first_step(self):
        z,m,v=adam_step(np.array([1.,-1.]),np.array([2.,-3.]),np.zeros(2),np.zeros(2),1,.01)
        np.testing.assert_allclose(z,[.99,-.99],atol=1e-10);np.testing.assert_allclose(m,[.2,-.3])
    def test_A_transformed_bound_quadratic(self):self.quadratic('lbfgsb')
    def test_B_fixed_warm_then_bound_quadratic(self):self.quadratic('adam_lbfgsb')
    def test_C_trust_bound_quadratic(self):self.quadratic('trust_constr')
    def quadratic(self,kind):
        q=np.array([.1,10.]);target=np.array([1.,-2.]);fun=lambda t:(float(np.sum(q*(t-target)**2)/2),q*(t-target));result=run(toy_policy(kind),np.array([3.,3.]),np.array([2.,.2]),fun)
        self.assertLess(physical_pg(result['theta'],fun(result['theta'])[1]),1e-5);self.assertTrue(np.all(np.abs(result['theta'])<=8));self.assertLessEqual(result['call_count'],500)
        if kind=='adam_lbfgsb':self.assertEqual(result['warm_accepted'],6)
    def test_hard_budget_no_hidden_extra_call(self):
        p=toy_policy('lbfgsb');p['objective_gradient_call_cap']=1;result=run(p,np.array([2.]),np.array([1.]),lambda t:(float(t@t),2*t));self.assertEqual(result['call_count'],1);self.assertEqual(result['solver_status'],'BudgetExhausted')
    def test_nonfinite_failure_retained(self):
        result=run(toy_policy('lbfgsb'),np.array([1.]),np.array([1.]),lambda t:(float('inf'),np.array([1.])));self.assertEqual(result['solver_status'],'NumericalFailure');self.assertFalse(result['calls'][0]['finite'])
    def test_unacceptable_scale_rejected(self):
        with self.assertRaises(ValueError):Coordinates([0.])
    def test_raised_objective_attempt_and_history_retained(self):
        def raised(t):raise ValueError('synthetic raised objective')
        result=run(toy_policy('lbfgsb'),np.array([1.]),np.array([1.]),raised)
        self.assertEqual(result['call_count'],1);self.assertEqual(result['solver_status'],'NumericalFailure');self.assertEqual(result['calls'][0]['objective_exception_type'],'ValueError');np.testing.assert_array_equal(result['theta'],[1.])
    def test_unexpected_solver_exception_retained(self):
        from unittest.mock import patch
        with patch('policies.minimize',side_effect=ValueError('synthetic solver exception')):
            result=run(toy_policy('lbfgsb'),np.array([1.]),np.array([1.]),lambda t:(float(t@t),2*t))
        self.assertEqual(result['solver_status'],'OptimizerException:ValueError');self.assertEqual(result['call_count'],0);self.assertEqual(result['accepted_count'],0);self.assertEqual(result['solver_message'],'synthetic solver exception')

if __name__=='__main__':unittest.main(verbosity=2)
