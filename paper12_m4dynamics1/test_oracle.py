import unittest
import numpy as np
from oracle import synthetic_cases,check_gradient,scalar_ll,scalar_objective
from model_math import objective,projected_gradient

class Oracles(unittest.TestCase):
    def test_all_coordinates_every_registered_synthetic_case(self):
        rows=[]
        for f,k,r,s,m,theta in synthetic_cases():
            check=check_gradient(theta,m,r,f,k,range(len(theta)))
            rows.append(dict(family=f,size=k,ridge=r,seed=s,**check));self.assertTrue(check['passed'],rows[-1])
        self.assertEqual(len(rows),108);self.gradient_rows=rows

    def test_exhaustive_state_forward(self):
        for f,k,r,s,m,t in synthetic_cases():
            if f=='Continuous':continue
            x=np.empty(m.y.shape[:2]+(0,))
            reference=scalar_ll(t,f,m.y,x,m.offset,k,True)
            self.assertLessEqual(abs(m.score(t)-reference),1e-10)

    def test_all_coefficient_penalty_and_exposure(self):
        for f,k,r,s,m,t in synthetic_cases():
            v,g=objective(t,m,r);v0,g0=objective(t,m,0.)
            self.assertAlmostEqual(v-v0,r*float(t@t)/2,places=12)
            np.testing.assert_allclose(g-g0,r*t,rtol=0,atol=1e-12)
            self.assertAlmostEqual(v0,-m.score(t)/(m.y.shape[0]*m.y.shape[1]),places=12)

    def test_projected_gradient_bounds(self):
        theta=np.array([-8.,-8.,8.,8.,0.]);g=np.array([5.,-3.,-7.,2.,1.])
        self.assertEqual(projected_gradient(theta,g),3.)
        self.assertEqual(projected_gradient(np.array([-8.,8.]),np.array([1.,-1.])),0.)

    def test_continuous_recurrence_and_causality(self):
        from model_math import make
        for f,k,r,s,m,t in synthetic_cases():
            if f!='Continuous':continue
            self.assertLessEqual(abs(m.score(t)-scalar_ll(t,f,m.y,m.x,m.offset,k)),1e-10)
            y=m.y.copy();y[:,3]+=7
            altered=make(f,y,m.x,m.offset,k)
            np.testing.assert_allclose(m.log_means(t)[:,:3],altered.log_means(t)[:,:3],rtol=0,atol=1e-12)

if __name__=='__main__':unittest.main(verbosity=2)
