import unittest
import numpy as np
from scipy.special import gammaln
from baseline_features import design, training_scaler, transform, likelihood_gradient, poisson_ll


class BaselineFeaturesTests(unittest.TestCase):
    def setUp(self):
        self.y = np.random.default_rng(17).poisson(.2, (3, 20, 2))
        self.conditions = np.array([0, 1, 7])
        self.order = np.array([0, 30, 599])

    def feature(self, kind, y=None):
        return design(self.y if y is None else y, self.conditions, self.order, kind)

    def test_exact_frozen_feature_counts(self):
        for kind, size in dict(stationary=1, history=6, population=11, event=27, drift=3, combined=44).items():
            self.assertEqual(self.feature(kind).shape, (3, 20, 2, size))

    def test_causal_and_reset(self):
        changed = self.y.copy(); changed[:, 12:] += 5
        for kind in ('history', 'population', 'combined'):
            self.assertTrue(np.array_equal(self.feature(kind)[:, :13], self.feature(kind, changed)[:, :13]))
        self.assertTrue(np.all(self.feature('history')[:, 0, :, 1:] == 0))

    def test_own_five_lags(self):
        self.assertEqual(self.feature('history')[0, 8, 1, 5], np.log1p(self.y[0, 3, 1]))

    def test_drift_known_order_not_subset_position(self):
        self.assertTrue(np.array_equal(self.feature('drift')[:, 0, 0, 1], self.order / 599.))
        self.assertTrue(np.array_equal(self.feature('drift')[:, 0, 0, 2], (self.order / 599.) ** 2))

    def test_scaler_train_only_and_intercept(self):
        train = self.feature('combined')
        scaler = training_scaler(train)
        before = tuple(x.copy() for x in scaler)
        transform(self.feature('combined', self.y + 100), scaler)
        self.assertTrue(all(np.array_equal(x, y) for x, y in zip(scaler, before)))
        self.assertTrue(np.all(transform(train, scaler)[..., 0] == 1))

    def test_analytic_poisson(self):
        y = np.zeros((1, 20, 1)); y[0, 0, 0] = 2
        expected = 2 * np.log(.7) - 20 * .7 - gammaln(3)
        self.assertLess(abs(poisson_ll(y, np.log(.7)).sum() - expected), 1e-12)

    def test_gradient(self):
        features = transform(self.feature('combined'), training_scaler(self.feature('combined')))
        w = np.random.default_rng(19).normal(0, .02, 88)
        _, gradient = likelihood_gradient(w, self.y, features)
        numeric = np.empty_like(w)
        for i in range(len(w)):
            lo = w.copy(); hi = w.copy(); lo[i] -= 1e-6; hi[i] += 1e-6
            numeric[i] = (likelihood_gradient(hi, self.y, features)[0] - likelihood_gradient(lo, self.y, features)[0]) / 2e-6
        self.assertLess(np.max(np.abs(numeric - gradient) / np.maximum(1., np.abs(gradient))), 1e-5)

    def test_trial_order_and_batch_invariance(self):
        features = self.feature('history'); w = np.zeros(12)
        total, _ = likelihood_gradient(w, self.y, features)
        split = sum(likelihood_gradient(w, self.y[i:i+1], features[i:i+1])[0] for i in range(3))
        reversed_score = likelihood_gradient(w, self.y[::-1], features[::-1])[0]
        self.assertLess(abs(total - split), 1e-10)
        self.assertLess(abs(total - reversed_score), 1e-10)

    def test_invalid_counts_and_conditions_rejected(self):
        with self.assertRaises(ValueError):
            self.feature('history', self.y + .5)
        with self.assertRaises(ValueError):
            design(self.y, np.array([0, 8, 1]), self.order, 'event')


if __name__ == '__main__':
    unittest.main()
