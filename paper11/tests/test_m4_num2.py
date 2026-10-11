"""Corrected proposal oracles. Synthetic fixtures are not neural findings."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.special import gammaln
from scipy.stats import multivariate_normal, norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import guided_poisson_filter as guided
from oracle_m4_num2 import fixture, quadrature
import oracle_m4_num2 as oracle


class GuidedTests(unittest.TestCase):
    def test_gaussian_density_independent_scipy(self):
        precision = np.array([[2., .3], [.3, 1.2]])
        z = np.array([[1., 2.], [-.2, .4]])
        np.testing.assert_allclose(guided.log_gaussian(z, np.zeros(2), precision),
            multivariate_normal.logpdf(z, cov=np.linalg.inv(precision)), atol=1e-12)

    def test_analytic_gaussian_posterior_correction(self):
        prior_variance, noise, observed = 1., .4, 1.2
        posterior_variance = 1/(1/prior_variance+1/noise)
        posterior_mean = posterior_variance*observed/noise
        z = np.array([-2., -.1, .5, 2.])
        result = guided.correction(norm.logpdf(observed, z, np.sqrt(noise)), norm.logpdf(z),
            norm.logpdf(z, posterior_mean, np.sqrt(posterior_variance)), 0, 0)
        np.testing.assert_allclose(result, norm.logpdf(observed, scale=np.sqrt(1+noise)), atol=1e-12)

    def test_state_and_initial_correction(self):
        rng = np.random.default_rng(19)
        p, q = np.array([.8, .2]), np.array([.15, .85])
        states, lp, lq = guided.draw_states(np.tile(p,(100000,1)), rng, np.tile(q,(100000,1)))
        likelihood = np.array([.4, .1])
        weights = guided.correction(np.log(likelihood[states]), 0, 0, lp, lq)
        score, normalized, ess = guided.normalize(weights)
        self.assertLess(abs(np.exp(score)-p@likelihood), .005)
        self.assertAlmostEqual(normalized.sum(), 1.)
        self.assertTrue(1 <= ess <= len(states))

    def test_state_support_loss_rejected(self):
        with self.assertRaises(ValueError):
            guided.draw_states(np.array([[.5,.5]]), np.random.default_rng(1), np.array([[1.,0.]]))

    def test_log_score_ess_resampling(self):
        score, weights, ess = guided.normalize(np.log(np.array([1., 2., 3., 4.])))
        self.assertAlmostEqual(score, np.log(2.5))
        self.assertAlmostEqual(ess, 1/np.sum(weights**2))
        indices = guided.resample(np.array([0., 0., 1., 0.]), np.random.default_rng(2))
        np.testing.assert_array_equal(indices, [2,2,2,2])
        with self.assertRaises(ValueError):
            guided.normalize(np.full(4, -np.inf))

    def test_laplace_gradient_and_precision(self):
        model = fixture()
        y, offset = np.array([0.,1.,0.,2.]), np.full(4, -1.)
        mean, cov = np.array([.2,-.1]), np.array([[1.,.2],[.2,1.3]])
        mode, hessian, diagnostic = guided.laplace(y, offset, model['biases'][0], model['loadings'], mean, cov)
        rates = np.exp(offset+model['loadings']@mode)
        np.testing.assert_allclose(hessian, np.linalg.inv(cov)+model['loadings'].T@(rates[:,None]*model['loadings']))
        self.assertTrue(diagnostic['converged'])
        self.assertLess(diagnostic['gradient_max'], 1e-7)

    def test_causal_sequence_and_initial_weighting(self):
        model = fixture()
        y, offset = np.ones((3,4)), np.full((3,4),-1.)
        first, _ = guided.particle(model,y,offset,1024,11)
        y[-1] = 12
        second, _ = guided.particle(model,y,offset,1024,11)
        np.testing.assert_array_equal(first[:-1],second[:-1])

    def test_exact_zero_loading(self):
        model = fixture()
        model['loadings'][:] = 0
        y, offset = np.ones((3,4)), np.full((3,4),-1.)
        scores, diagnostic = guided.particle(model,y,offset,64,11)
        exact = np.sum(y*offset-np.exp(offset)-gammaln(y+1),axis=1)
        np.testing.assert_allclose(scores,exact,atol=1e-12)
        self.assertAlmostEqual(diagnostic['minimum_ess_fraction'], 1.)

    def test_defensive_mixture_density_not_single_component(self):
        z = np.array([[2.,-1.]])
        prior = guided.log_gaussian(z,np.zeros(2),np.eye(2))
        guide = guided.log_gaussian(z,np.array([1.,.5]),np.eye(2)*2)
        mixture = np.logaddexp(np.log(.9)+guide,np.log(.1)+prior)
        self.assertFalse(np.allclose(mixture,guide))
        self.assertLessEqual(float(np.exp(prior-mixture)[0]),10.+1e-12)

    def test_quadrature_initial_independent_of_dynamics(self):
        model = fixture(2)
        y, offset = np.ones((1,4)), np.full((1,4),-1.)
        first = quadrature(model,y,offset,16)
        model['dynamics'][:] = 9
        np.testing.assert_array_equal(first,quadrature(model,y,offset,16))

    def test_unit_failure_stops_before_fixtures(self):
        with patch.object(oracle,'quadrature') as quadrature_mock, patch.object(guided,'particle') as particle_mock:
            rows, errors = oracle.evaluate(False)
        self.assertEqual(rows,[])
        self.assertEqual(errors,['Proposal unit tests failed'])
        quadrature_mock.assert_not_called()
        particle_mock.assert_not_called()

    def test_first_oracle_failure_stops_remaining_seeds(self):
        with patch.object(oracle,'quadrature',return_value=np.zeros(3)) as quadrature_mock:
            with patch.object(guided,'particle',return_value=(np.full(3,.04),{})) as particle_mock:
                rows, errors = oracle.evaluate(True)
        self.assertEqual(len(rows),1)
        self.assertIn('K1/seed1103',errors[0])
        self.assertEqual(quadrature_mock.call_count,2)
        particle_mock.assert_called_once()

    def test_quadrature_failure_stops_sampling(self):
        with patch.object(oracle,'quadrature',side_effect=[np.zeros(3),np.full(3,.01)]):
            with patch.object(guided,'particle') as particle_mock:
                rows, errors = oracle.evaluate(True)
        self.assertEqual(rows,[])
        self.assertIn('Quadrature oracle unresolved',errors[0])
        particle_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
