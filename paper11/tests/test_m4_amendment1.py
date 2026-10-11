"""Numerical fixtures are algorithm tests, not neural findings."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.integrate import quad
from scipy.special import gammaln

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_m4_amendment1 as amended


def model():
    return {'family': 'continuous', 'states': 1, 'dimension': 1,
            'initial': np.ones(1), 'transition': np.ones((1, 1)),
            'biases': np.zeros((1, 2)), 'loadings': np.array([[.3], [-.2]]), 'dynamics': np.array([[[.5]]])}


class NumericalTests(unittest.TestCase):
    def test_instrumentation_preserves_original_estimator(self):
        m = model()
        y, offset = np.ones((4, 2)), np.full((4, 2), -1.)
        actual, diagnostic = amended.particle(m, y, offset, 256, 11)
        expected = amended.original.regimes.particle_predictive(m, y, offset, 256, 11)
        np.testing.assert_array_equal(actual, expected)
        self.assertTrue(0 < diagnostic['minimum_ess_fraction'] <= 1)

    def test_no_future_bin_leakage(self):
        y, offset = np.ones((4, 2)), np.full((4, 2), -1.)
        first, _ = amended.particle(model(), y, offset, 256, 11)
        y[-1] = 100
        second, _ = amended.particle(model(), y, offset, 256, 11)
        np.testing.assert_array_equal(first[:-1], second[:-1])

    def test_exact_zero_loading_and_ess(self):
        m = model()
        m['loadings'][:] = 0
        y, offset = np.array([[1., 2.]]), np.array([[-1., -1.]])
        actual, diagnostic = amended.particle(m, y, offset, 64, 11)
        expected = np.sum(y * offset - np.exp(offset) - gammaln(y + 1))
        self.assertAlmostEqual(actual[0], expected)
        self.assertAlmostEqual(diagnostic['minimum_ess_fraction'], 1.)

    def test_nonzero_loading_quadrature(self):
        m = model()
        y, offset = np.array([[1., 2.]]), np.array([[-1., -1.]])
        def integrand(z):
            eta = offset[0] + m['loadings'][:, 0] * z
            return np.exp(np.sum(y[0] * eta - np.exp(eta) - gammaln(y[0] + 1)) - z*z/2) / np.sqrt(2*np.pi)
        exact = np.log(quad(integrand, -12, 12, epsabs=1e-12)[0])
        actual, _ = amended.particle(m, y, offset, 1000000, 11)
        self.assertLess(abs(actual[0] - exact), .004)

    def test_degenerate_normalizer_fails_closed(self):
        m = model()
        with self.assertRaises(amended.original.ScientificGateFailure):
            amended.particle(m, np.ones((1, 2)), np.full((1, 2), 10000.), 64, 11)

    def test_threshold_and_independent_seed_contract(self):
        spec = amended.load(amended.SPEC)
        self.assertEqual(spec['threshold_nats_unit_bin'], .001)
        self.assertEqual(spec['candidate_particles'], [2048, 4096, 8192])
        self.assertEqual(len(set(spec['candidate_seeds'])), 8)
        self.assertFalse(set(spec['candidate_seeds']) & set(spec['reference_seeds']))

    def test_failed_budget_cannot_be_selected(self):
        values = np.array([[0., .01]] * 8)
        with patch.object(amended, 'repetitions', return_value=(values, [], .1)):
            with patch.object(amended.original, 'single_run_discrepancy', return_value=.002):
                result = amended.accuracy(model(), np.ones((2, 1, 2)), np.zeros((2, 1, 2)))
        self.assertEqual(result['gate'], 'FAIL')
        self.assertNotIn('trial_scores', result)
        self.assertEqual(len(result['comparisons']), 3)

    def test_training_grid_and_seed_scope_unchanged(self):
        grid = amended.original.grid()
        self.assertEqual(len(grid), 11)
        self.assertEqual(sum(family == 'hybrid' for family, _, _ in grid), 4)
        protocol = amended.load(amended.PAPER / 'protocol/protocol.json')
        self.assertEqual(len(protocol['models']['shared']['initialization_seeds']), 8)


if __name__ == '__main__':
    unittest.main()
