"""Mathematical fixtures only; never substitute for experimental findings."""
import itertools
import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.special import logsumexp, gammaln
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import poisson_regimes as p
import run_m4 as runner
import json
import tempfile
from unittest.mock import patch
from scipy.integrate import quad


class RegimeTests(unittest.TestCase):
    def test_nonzero_loading_quadrature_oracle(self):
        model = {'states': 1, 'dimension': 1, 'initial': np.ones(1), 'transition': np.ones((1, 1)),
                 'dynamics': np.zeros((1, 1, 1)), 'biases': np.zeros((1, 2)), 'loadings': np.array([[0.2], [0.4]])}
        y = np.array([[1, 2]])
        offset = np.array([[-1.0, -0.7]])
        def integrand(x):
            eta = offset[0] + model['loadings'][:, 0] * x
            log_joint = np.sum(y[0] * eta - np.exp(eta) - gammaln(y[0] + 1))
            return np.exp(log_joint - x*x/2) / np.sqrt(2*np.pi)
        exact, error = quad(integrand, -12, 12, epsabs=1e-12)
        self.assertLess(error, 1e-9)
        estimated = p.particle_predictive(model, y, offset, 1000000, 11)[0]
        self.assertLess(abs(estimated - np.log(exact)), 0.004)

    def test_required_nonconvergence_blocks(self):
        fixture = {'family': 'discrete', 'states': 2, 'dimension': 0, 'biases': np.zeros((2, 1)),
                   'converged': False, 'iterations': 500, 'training_objectives': [0.0]}
        arrays = (np.ones((1, 3, 1)), np.ones((1, 3, 1)), [np.zeros((1, 3, 1))]*2,
                  {'parameters': 1}, {}, [2])
        with tempfile.TemporaryDirectory(dir=runner.RESULTS) as folder:
            with patch.object(runner, 'RESULTS', Path(folder)), patch.object(runner, 'observations', return_value=arrays), patch.object(p, 'fit_hmm', return_value=fixture):
                with self.assertRaises(runner.ScientificGateFailure):
                    runner.fit_session('fixture/session')

    def test_mean_accuracy_cannot_certify_single_run(self):
        estimates = np.array([[0.002], [-0.002/3], [-0.002/3], [-0.002/3]])
        self.assertAlmostEqual(float(estimates.mean()), 0)
        self.assertGreater(runner.single_run_discrepancy(estimates, np.zeros(1), 0), 0.001)
    def test_numpy_scalar_serialization(self):
        result = runner.serial({'converged': np.bool_(True), 'iterations': np.int64(2), 'weights': np.array([0.5])})
        self.assertEqual(json.loads(json.dumps(result))['converged'], True)
    def test_forward_matches_enumeration(self):
        likes = np.log([[0.2, 0.7], [0.6, 0.3], [0.4, 0.8]])
        initial = np.array([0.3, 0.7])
        transition = np.array([[0.8, 0.2], [0.1, 0.9]])
        expected = []
        for path in itertools.product(range(2), repeat=3):
            value = np.log(initial[path[0]]) + sum(likes[t, state] for t, state in enumerate(path))
            value += sum(np.log(transition[path[t-1], path[t]]) for t in range(1, 3))
            expected.append(value)
        gamma, xi, result = p.forward_backward(likes, initial, transition)
        self.assertAlmostEqual(result, logsumexp(expected))
        np.testing.assert_allclose(gamma.sum(axis=1), 1)
        np.testing.assert_allclose(xi.sum(axis=(1, 2)), 1)

    def test_joint_not_separate_marginals(self):
        y = np.array([[2, 0]])
        biases = np.array([[1.0, -1.0], [-1.0, 1.0]])
        model = {'initial': np.array([0.5, 0.5]), 'transition': np.eye(2), 'biases': biases}
        joint = p.exact_predictive(model, y, np.zeros_like(y))[0]
        unit_likes = y[0] * biases - np.exp(biases) - gammaln(y[0] + 1)
        correct = logsumexp(unit_likes.sum(axis=1)) - np.log(2)
        incorrect = np.sum(logsumexp(unit_likes, axis=0) - np.log(2))
        self.assertAlmostEqual(joint, correct)
        self.assertGreater(abs(joint - incorrect), 0.1)

    def test_future_counts_cannot_change_predictions(self):
        model = {'initial': np.array([0.5, 0.5]), 'transition': np.array([[0.8, 0.2], [0.2, 0.8]]), 'biases': np.array([[0.0], [0.5]])}
        y = np.zeros((4, 1))
        before = p.exact_predictive(model, y, np.zeros_like(y))
        y[-1] = 50
        after = p.exact_predictive(model, y, np.zeros_like(y))
        np.testing.assert_array_equal(before[:-1], after[:-1])

    def test_particle_zero_loading_exact_oracle(self):
        model = {'states': 1, 'dimension': 1, 'initial': np.ones(1), 'transition': np.ones((1, 1)),
                 'dynamics': np.zeros((1, 1, 1)), 'biases': np.zeros((1, 2)), 'loadings': np.zeros((2, 1))}
        y = np.array([[0, 1], [2, 0], [1, 1]])
        offset = np.log(np.full_like(y, 0.2, dtype=float))
        expected = (y * offset - np.exp(offset) - gammaln(y + 1)).sum(axis=1)
        for seed in (11, 23):
            np.testing.assert_allclose(p.particle_predictive(model, y, offset, 64, seed), expected)

    def test_gaussian_covariance_and_expected_prior(self):
        mean = np.array([[0.1], [0.2], [0.3]])
        covariance = np.ones((3, 1, 1)) * 0.5
        cross = np.ones((2, 1, 1)) * 0.1
        a = np.array([[[0.3]]])
        likes = p.dynamics_likes(mean, covariance, cross, a)
        expected = -0.5 * (np.log(2*np.pi) + (0.2 - 0.3 * 0.1)**2 + 0.5 + 0.3**2 * 0.5 - 2 * 0.3 * 0.1)
        self.assertAlmostEqual(likes[1, 0], expected)
        model = {'dimension': 1, 'dynamics': a, 'loadings': np.array([[0.1], [0.2]]), 'biases': np.zeros((1, 2))}
        result = p.gaussian_chain(np.ones((3, 2)), np.zeros((3, 2)), np.ones((3, 1)), model, mean, covariance)
        self.assertTrue(result[-1])
        self.assertTrue(np.all(result[1] > 0))

    def test_hmm_training_finite_and_converged(self):
        y = np.array([[[0, 1], [0, 0], [3, 0], [2, 0], [1, 1], [0, 2]]] * 4)
        model = p.fit_hmm(y, np.zeros_like(y), 2, 11, maximum=200)
        self.assertTrue(model['converged'])
        self.assertTrue(np.all(np.diff(model['training_objectives']) >= -1e-8))


if __name__ == '__main__':
    unittest.main()
