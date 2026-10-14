"""Exact frozen candidate settings on small synthetic recurrent fixtures."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'frozen_sources'))
import unittest
import numpy as np
import study as r
from test_conditioning import fixture
from conditioning import hessian,scale_from_diagonal
from policies import run,Coordinates,physical_pg
from model_math import objective
from independent_ad import value_gradient

class RegisteredPolicySupport(unittest.TestCase):
    def verify(self,candidate):
        model,initial=fixture(1);H,_=hessian(initial,lambda t:objective(t,model,.001),1e-7);S=scale_from_diagonal(np.diag(H))
        config=next(z for z in r.load(r.HERE/'candidate_protocol.json')['candidates'] if z['id']==candidate)
        result=run(config,initial,S,lambda t:objective(t,model,.001));theta=result['theta'];f,g=objective(theta,model,.001);adf,adg,_=value_gradient(theta,model.y,model.x,model.offset,1,.001)
        self.assertTrue(np.isfinite(theta).all());self.assertTrue(np.all(np.abs(theta)<=8));self.assertAlmostEqual(f,adf,places=10);np.testing.assert_allclose(g,adg,atol=1e-8,rtol=0);self.assertLessEqual(result['call_count'],config['objective_gradient_call_cap']);self.assertEqual(result['coordinate_roundtrip_abs_max']<1e-12,True)
        if candidate=='B':self.assertEqual(result['warm_accepted'],300)
        # Correct solver behavior on deterministic toy is support, not real-data feasibility.
        self.assertLess(physical_pg(theta,g),.001)
    def test_exact_registered_A(self):self.verify('A')
    def test_exact_registered_B(self):self.verify('B')
    def test_exact_registered_C(self):self.verify('C')

if __name__=='__main__':unittest.main(verbosity=2)
