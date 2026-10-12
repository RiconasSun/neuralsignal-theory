import unittest
import numpy as np
from baseline_features import design, training_scaler, transform
from baseline_fit import objective, projected_gradient, stationary


class BaselineFitTests(unittest.TestCase):
    def test_intercept_not_penalized(self):
        y = np.ones((2, 20, 1))
        features = design(y, np.array([0, 1]), np.array([0, 599]), 'drift')
        theta = np.array([.2, .3, .4])
        loss0, g0 = objective(theta, y, features, 0.)
        loss1, g1 = objective(theta, y, features, .1)
        self.assertAlmostEqual(loss1 - loss0, .5 * .1 * (.3 ** 2 + .4 ** 2))
        np.testing.assert_allclose(g1 - g0, [0, .03, .04], atol=1e-12)

    def test_penalized_gradient(self):
        y = np.random.default_rng(43).poisson(.4, (2, 20, 2))
        raw = design(y, np.array([0, 7]), np.array([0, 599]), 'combined')
        features = transform(raw, training_scaler(raw))
        theta = np.random.default_rng(44).normal(0, .02, 88)
        for normalization in ('total_unit_bins', 'per_unit_exposure'):
            _, grad = objective(theta, y, features, .1, normalization)
            numeric = []
            for i in range(88):
                lo = theta.copy(); hi = theta.copy(); lo[i] -= 1e-6; hi[i] += 1e-6
                numeric.append((objective(hi, y, features, .1, normalization)[0] - objective(lo, y, features, .1, normalization)[0]) / 2e-6)
            self.assertLess(np.max(np.abs(np.asarray(numeric) - grad) / np.maximum(1., np.abs(grad))), 1e-5)

    def test_projected_boundary_signs(self):
        theta = np.array([-8., -8., 8., 8., 0.])
        gradient = np.array([2., -2., -3., 3., .1])
        self.assertEqual(projected_gradient(theta, gradient), 3.)

    def test_stationary_exact(self):
        y = np.ones((1, 20, 2))
        result = stationary(y, y, 11)
        self.assertEqual(result['training_LL_nats_per_unit_bin'], -1.)
        self.assertTrue(result['converged'])

    def test_stationary_zero_not_hidden(self):
        with np.errstate(divide='ignore'), self.assertRaises(FloatingPointError):
            stationary(np.zeros((1, 20, 1)), np.zeros((1, 20, 1)), 11)


if __name__ == '__main__':
    unittest.main()
