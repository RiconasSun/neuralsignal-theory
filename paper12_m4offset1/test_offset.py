import unittest
import numpy as np
from baseline_fit import objective,projected_gradient
from baseline_features import design,training_scaler,transform
from numerical import gradient_check
from offset_math import features


class OffsetOracles(unittest.TestCase):
    def fixture(self):
        y=np.random.default_rng(20261013).poisson(.4,(8,20,2))
        return y,features(y,np.arange(8),np.arange(8)*70)

    def test_all_offset_coordinates_all_seeds(self):
        y,x=self.fixture()
        for seed in (11,23,37):
            theta=np.random.default_rng(seed).normal(0,.05,58)
            self.assertTrue(gradient_check(theta,y,x,.1,range(58))['passed'])

    def test_same_features_and_no_count_covariate(self):
        y,x=self.fixture();c=np.arange(8);o=c*70
        raw=np.concatenate((design(y,c,o,'event'),design(y,c,o,'drift')[...,1:]),axis=-1)
        np.testing.assert_array_equal(x,transform(raw,training_scaler(raw)))
        np.testing.assert_array_equal(x,features(y+10,c,o))
        self.assertEqual(x.shape[-1],29)

    def test_per_unit_exposure_and_unpenalized_intercept(self):
        y,x=self.fixture();theta=np.full(58,.01)
        a=objective(theta,y,x,.1,'per_unit_exposure');b=objective(theta,np.concatenate((y,y)),np.concatenate((x,x)),.1,'per_unit_exposure')
        self.assertAlmostEqual(a[0],b[0],12);np.testing.assert_allclose(a[1],b[1],atol=1e-12)
        theta=np.zeros(58);theta[::29]=1
        self.assertEqual(objective(theta,y,x,0,'per_unit_exposure')[0],objective(theta,y,x,.1,'per_unit_exposure')[0])

    def test_bound_KKT_signs(self):
        self.assertEqual(projected_gradient(np.array([-8.,8.]),np.array([1.,-1.])),0)
        self.assertEqual(projected_gradient(np.array([-8.,8.]),np.array([-2.,3.])),3)

    def test_all_seed_mean_log_rate(self):
        y,x=self.fixture();weights=np.random.default_rng(11).normal(0,.05,(3,2,29))
        a=np.einsum('ntuf,uf->ntu',x,weights.mean(axis=0))
        b=np.mean([np.einsum('ntuf,uf->ntu',x,w) for w in weights],axis=0)
        np.testing.assert_allclose(a,b,atol=1e-12,rtol=0)
