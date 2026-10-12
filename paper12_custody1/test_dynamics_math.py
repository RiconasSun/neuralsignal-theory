import itertools
import unittest
import numpy as np
from scipy.special import logsumexp
from dynamics_math import StatePoisson, RecurrentPoisson, core


class DynamicsMathTests(unittest.TestCase):
    def test_exact_discrete_and_hybrid_oracle(self):
        y = np.array([[[0., 1.], [2., 0.], [1., 1.]]])
        for lags in (0, 5):
            model = StatePoisson(y, np.full_like(y, np.log(.3)), 2, lags)
            theta = model.initial(11)
            pi, transition, _, _ = model.unpack(theta)
            emissions = core.poisson_logpmf(y[:, :, None, :], model.log_means(theta)).sum(axis=-1)[0]
            exhaustive = []
            for states in itertools.product(range(2), repeat=3):
                score = pi[states[0]] + sum(emissions[t, s] for t, s in enumerate(states))
                score += sum(transition[states[t-1], states[t]] for t in range(1, 3))
                exhaustive.append(score)
            self.assertLess(abs(logsumexp(exhaustive) - model.score(theta)), 1e-10)

    def test_analytic_gradients(self):
        y = np.random.default_rng(31).poisson(.3, (2, 20, 2)).astype(float)
        offset = np.full_like(y, np.log(.3)); context = np.zeros((2, 20, 28))
        context[..., 0] = 1
        models = [StatePoisson(y, offset, 2, 0), StatePoisson(y, offset, 2, 5),
                  RecurrentPoisson(y, context, offset, 2)]
        for model in models:
            theta = model.initial(23); _, gradient = model._likelihood_gradient(theta)
            numeric = np.empty_like(theta)
            for i in range(len(theta)):
                lo = theta.copy(); hi = theta.copy(); lo[i] -= 1e-6; hi[i] += 1e-6
                numeric[i] = (model.score(hi) - model.score(lo)) / 2e-6
            self.assertLess(np.max(np.abs(numeric-gradient) / np.maximum(1., np.abs(gradient))), 1e-5)

    def test_future_perturbation(self):
        y = np.random.default_rng(35).poisson(.3, (2, 20, 2)).astype(float)
        altered = y.copy(); altered[:, 12:] += 4
        offset = np.full_like(y, np.log(.3)); context = np.zeros((2, 20, 28))
        for factory in (lambda z: StatePoisson(z, offset, 2, 0),
                        lambda z: StatePoisson(z, offset, 2, 5),
                        lambda z: RecurrentPoisson(z, context, offset, 2)):
            model = factory(y); changed = factory(altered); theta = model.initial(37)
            self.assertLess(np.max(np.abs(model.score_bins(theta)[:, :12]-changed.score_bins(theta)[:, :12])), 1e-12)

    def test_batch_order_and_trial_reset(self):
        y = np.random.default_rng(45).poisson(.3, (3, 20, 2)).astype(float)
        def factory(value, kind):
            offset = np.full_like(value, np.log(.3))
            if kind == 'continuous':
                return RecurrentPoisson(value, np.zeros(value.shape[:2]+(28,)), offset, 2)
            return StatePoisson(value, offset, 2, 5 if kind == 'hybrid' else 0)
        for kind in ('discrete', 'continuous', 'hybrid'):
            model = factory(y, kind); theta = model.initial(11)
            score = model.score(theta)
            pieces = sum(factory(y[i:i+1], kind).score(theta) for i in range(3))
            reverse = factory(y[::-1], kind).score(theta)
            self.assertLess(abs(score-pieces), 1e-10)
            self.assertLess(abs(score-reverse), 1e-10)


if __name__ == '__main__':
    unittest.main()
