import unittest
import numpy as np
from baseline_features import design,training_scaler,transform
from baseline_fit import objective,projected_gradient
from numerical import gradient_check,scalar_unit,ORIGINAL,REPAIRED


class NumericalOracles(unittest.TestCase):
    def fixture(self,kind='combined'):
        y=np.random.default_rng(9001).poisson(.4,(8,20,2))
        raw=design(y,np.arange(8),np.arange(8)*70,kind)
        return y,transform(raw,training_scaler(raw))

    def test_all_feature_gradient_oracles(self):
        for kind in ('history','population','event','drift','combined'):
            y,x=self.fixture(kind);theta=np.random.default_rng(11).normal(0,.05,y.shape[-1]*x.shape[-1])
            for ridge in (.001,.01,.1,1.):
                self.assertTrue(gradient_check(theta,y,x,ridge,range(theta.size))['passed'])

    def test_scalar_objective(self):
        y,x=self.fixture();theta=np.linspace(-.1,.1,2*x.shape[-1]);m=theta.reshape(2,-1)
        expected=sum(scalar_unit(m[u],y[...,u],x[...,u,:],.1) for u in range(2))
        self.assertAlmostEqual(objective(theta,y,x,.1,'per_unit_exposure')[0],expected,places=12)

    def test_exposure_replication(self):
        y,x=self.fixture();theta=np.full(2*x.shape[-1],.01)
        a=objective(theta,y,x,.1,'per_unit_exposure');b=objective(theta,np.concatenate([y,y]),np.concatenate([x,x]),.1,'per_unit_exposure')
        self.assertAlmostEqual(a[0],b[0],places=12);np.testing.assert_allclose(a[1],b[1],atol=1e-12)

    def test_intercept_unpenalized(self):
        y,x=self.fixture();theta=np.zeros(2*x.shape[-1]);theta[::x.shape[-1]]=1
        a=objective(theta,y,x,0,'per_unit_exposure');b=objective(theta,y,x,1,'per_unit_exposure')
        self.assertEqual(a[0],b[0]);np.testing.assert_array_equal(a[1],b[1])

    def test_scaling(self):
        y,x=self.fixture();self.assertTrue(np.all(x[...,0]==1))
        np.testing.assert_allclose(x[...,1:].mean(axis=(0,1)),0,atol=1e-12)
        future=y.copy();future[:,10:]+=100
        for kind in ('history','population','combined'):
            a=design(y,np.arange(8),np.arange(8)*70,kind);b=design(future,np.arange(8),np.arange(8)*70,kind)
            np.testing.assert_array_equal(a[:,:11],b[:,:11])

    def test_active_bounds(self):
        self.assertEqual(projected_gradient(np.array([-8.,8.]),np.array([1.,-1.])),0)
        self.assertEqual(projected_gradient(np.array([-8.,8.]),np.array([-2.,3.])),3)
        self.assertEqual(projected_gradient(np.array([-7.99,7.99]),np.array([1.,-1.])),1)

    def test_budget(self):
        self.assertEqual(ORIGINAL,dict(ftol=1e-5,gtol=1e-5,maxiter=500,maxfun=20000))
        self.assertEqual(REPAIRED,dict(ftol=1e-10,gtol=1e-5,maxiter=2000,maxfun=80000))


if __name__=='__main__':unittest.main()
