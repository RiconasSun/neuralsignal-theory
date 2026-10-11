"""Independent scalar/path oracles; import has no test or fit side effects.

numerical_audit() is explicitly invoked by the registered parent runner.
All inputs here are synthetic numerical evidence, never scientific findings.
"""
import itertools
import math
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import predictive_models as models


def scalar_poisson(y, eta):
    if eta == -math.inf:
        return 0. if y == 0 else -math.inf
    return int(y) * float(eta) - math.exp(float(eta)) - math.lgamma(int(y) + 1)


def scalar_logsum(values):
    top = max(values)
    return top + math.log(math.fsum(math.exp(v - top) for v in values))


def fixture():
    y = np.array([[[0, 1], [2, 0], [1, 3]], [[1, 0], [0, 2], [3, 1]]], dtype=float)
    x = np.broadcast_to(np.array([[0., 1.], [.5, 0.], [1., 0.]]), (2, 3, 2)).copy()
    offset = np.array([[[-.4, -.2], [-.3, -.1], [-.2, 0.]],
                       [[-.1, -.3], [0., -.2], [.1, -.1]]])
    return y, x, offset


def glm_oracle(theta, design, y):
    n, t, u = y.shape
    f = design.shape[-1]
    scores = np.zeros((n, t))
    for trial in range(n):
        for bin_id in range(t):
            for unit in range(u):
                eta = math.fsum(float(design[trial, bin_id, unit, j]) * float(theta[unit * f + j]) for j in range(f))
                scores[trial, bin_id] += scalar_poisson(y[trial, bin_id, unit], eta)
    return scores


def state_oracle(theta, y, offset, states, lags, prefixes=True):
    """Enumerate every hidden path, independently of production inference."""
    k, u = states, y.shape[-1]
    init_logits = list(map(float, theta[:k - 1])) + [0.]
    pi_norm = scalar_logsum(init_logits)
    log_pi = [v - pi_norm for v in init_logits]
    cursor = k - 1
    log_p = []
    for state in range(k):
        row = list(map(float, theta[cursor:cursor + k - 1])) + [0.]
        cursor += k - 1
        norm = scalar_logsum(row)
        log_p.append([v - norm for v in row])
    biases = theta[cursor:cursor + k * u].reshape(k, u)
    cursor += k * u
    ar = theta[cursor:].reshape(k, u, lags)
    scores = np.zeros(y.shape[:2])
    totals = []
    for n in range(len(y)):
        emissions = []
        for t in range(y.shape[1]):
            row = []
            for state in range(k):
                terms = []
                for unit in range(u):
                    eta = float(offset[n, t, unit] + biases[state, unit])
                    for lag in range(1, lags + 1):
                        if t >= lag:
                            eta += float(ar[state, unit, lag - 1]) * math.log1p(float(y[n, t - lag, unit]))
                    terms.append(scalar_poisson(y[n, t, unit], eta))
                row.append(math.fsum(terms))
            emissions.append(row)
        previous = 0.
        lengths = range(1, y.shape[1] + 1) if prefixes else [y.shape[1]]
        for length in lengths:
            paths = []
            for path in itertools.product(range(k), repeat=length):
                log_weight = log_pi[path[0]]
                for t, state in enumerate(path):
                    log_weight += emissions[t][state]
                    if t:
                        log_weight += log_p[path[t - 1]][state]
                paths.append(log_weight)
            prefix = scalar_logsum(paths)
            scores[n, length - 1] = prefix - previous
            previous = prefix
        totals.append(previous)
    return scores if prefixes else math.fsum(totals)


def recurrent_oracle(theta, y, x, offset, dimension):
    """Scalar-loop causal recursion, with independent parameter indexing."""
    d, u, xd = dimension, y.shape[-1], x.shape[-1]
    cursor = 0
    blocks = []
    for rows, cols in [(d, d), (d, u), (d, xd), (u, d)]:
        blocks.append([[float(theta[cursor + i * cols + j]) for j in range(cols)] for i in range(rows)])
        cursor += rows * cols
    a, b, context, c = blocks
    scores = np.zeros(y.shape[:2])
    for n in range(len(y)):
        previous = [0.] * d
        for t in range(y.shape[1]):
            hidden = []
            for i in range(d):
                value = math.fsum(a[i][j] * previous[j] for j in range(d))
                if t:
                    value += math.fsum(b[i][j] * math.log1p(float(y[n, t - 1, j])) for j in range(u))
                value += math.fsum(context[i][j] * float(x[n, t, j]) for j in range(xd))
                hidden.append(math.tanh(value))
            for unit in range(u):
                eta = float(offset[n, t, unit]) + math.fsum(c[unit][j] * hidden[j] for j in range(d))
                scores[n, t] += scalar_poisson(y[n, t, unit], eta)
            previous = hidden
    return scores


def gradient_error(model, theta, oracle_total, ridge=.1):
    loss, analytic = model.objective(theta, ridge)
    reference_loss = -oracle_total(theta) / model.y.size + .5 * ridge * float(theta @ theta)
    if abs(loss - reference_loss) > 1e-10:
        raise AssertionError('Normalized ridge objective differs from independent oracle')
    fd = np.empty(len(theta))
    step = 1e-5
    for j in range(len(theta)):
        plus, minus = theta.copy(), theta.copy()
        plus[j] += step
        minus[j] -= step
        def independent_objective(p):
            return -oracle_total(p) / model.y.size + .5 * ridge * float(p @ p)
        fd[j] = (independent_objective(plus) - independent_objective(minus)) / (2 * step)
    absolute = np.abs(fd - analytic)
    relative_or_absolute = absolute / np.maximum(1., np.maximum(np.abs(fd), np.abs(analytic)))
    return float(relative_or_absolute.max()), float(absolute.max())


def causal_checks():
    y, x, offset = fixture()
    checks = 0
    for kind in ['stationary', 'history', 'event', 'drift', 'combined', 'population']:
        original = models.make_design(y, x, kind, trial_position=np.array([0., 1.]))
        changed = y.copy()
        changed[0, 1:] += 7
        altered = models.make_design(changed, x, kind, trial_position=np.array([0., 1.]))
        np.testing.assert_array_equal(original[0, :2], altered[0, :2])
        np.testing.assert_array_equal(original[1], altered[1])
        checks += 1
    for k, lag in itertools.product([1, 2, 4], [0, 1, 5]):
        model = models.StatePoisson(y, offset, k, lag)
        theta = np.linspace(-.2, .2, model.n_parameters)
        eta, prior = model.predictions(theta)
        for changed_bin in [0, 1, 2]:
            changed = y.copy()
            changed[0, changed_bin:] += 7
            other = models.StatePoisson(changed, offset, k, lag)
            new_eta, new_prior = other.predictions(theta)
            np.testing.assert_array_equal(eta[0, :changed_bin + 1], new_eta[0, :changed_bin + 1])
            np.testing.assert_allclose(prior[0, :changed_bin + 1], new_prior[0, :changed_bin + 1], atol=1e-14, rtol=0)
            np.testing.assert_allclose(model.score_bins(theta)[0, :changed_bin], other.score_bins(theta)[0, :changed_bin], atol=1e-12, rtol=0)
            np.testing.assert_array_equal(eta[1], new_eta[1])
            np.testing.assert_array_equal(prior[1], new_prior[1])
            checks += 1
        separate = models.StatePoisson(y[1:], offset[1:], k, lag)
        np.testing.assert_allclose(model.score_bins(theta)[1:], separate.score_bins(theta), atol=1e-12, rtol=0)
        checks += 1
    for dim in [1, 2, 4]:
        model = models.RecurrentPoisson(y, x, offset, dim)
        theta = np.linspace(-.2, .2, model.n_parameters)
        eta = model.log_means(theta)
        for changed_bin in [0, 1, 2]:
            changed = y.copy()
            changed[0, changed_bin:] += 7
            other = models.RecurrentPoisson(changed, x, offset, dim)
            np.testing.assert_array_equal(eta[0, :changed_bin + 1], other.log_means(theta)[0, :changed_bin + 1])
            np.testing.assert_array_equal(eta[1], other.log_means(theta)[1])
            np.testing.assert_allclose(model.score_bins(theta)[0, :changed_bin], other.score_bins(theta)[0, :changed_bin], atol=1e-12, rtol=0)
            checks += 1
        separate = models.RecurrentPoisson(y[1:], x[1:], offset[1:], dim)
        np.testing.assert_array_equal(model.log_means(theta)[1:], separate.log_means(theta))
        checks += 1
    return checks


def numerical_audit():
    """Measured errors; raises on any gate failure, without running optimizer fits.

    Gradient metric is |analytic-FD| / max(1, |analytic|, |FD|); the absolute
    maximum is also retained. Score metrics use actual observed unit-bin count.
    """
    y, x, offset = fixture()
    errors = {'max_poisson_score_error': 0., 'max_state_score_error': 0.,
              'max_recurrent_score_error': 0., 'max_gradient_error': 0.,
              'max_gradient_absolute_error': 0., 'case_count': 0}
    def check(model, oracle_bins, oracle_total, metric):
        for seed in [11, 23, 37]:
            theta = model.initial(seed)
            expected = oracle_bins(theta)
            actual = model.score_bins(theta)
            if not np.all(np.isfinite(actual)):
                raise AssertionError('Nonfinite score')
            error = max(abs(model.score(theta) - float(expected.sum())) / y.size,
                        float(np.max(np.abs(actual - expected))) / y.shape[-1])
            errors[metric] = max(errors[metric], error)
            for ridge in [.001, .01, .1, 1.]:
                relative, absolute = gradient_error(model, theta, oracle_total, ridge)
                errors['max_gradient_error'] = max(errors['max_gradient_error'], relative)
                errors['max_gradient_absolute_error'] = max(errors['max_gradient_absolute_error'], absolute)
                errors['case_count'] += 1
    for kind in ['stationary', 'history', 'event', 'drift', 'combined', 'population']:
        design = models.make_design(y, x, kind, trial_position=np.array([0., 1.]))
        model = models.PoissonGLM(design, y)
        check(model, lambda p: glm_oracle(p, design, y),
              lambda p: float(glm_oracle(p, design, y).sum()), 'max_poisson_score_error')
    for states in [1, 2, 4]:
        for lags in [0, 1, 5]:
            model = models.StatePoisson(y, offset, states, lags)
            check(model, lambda p: state_oracle(p, y, offset, states, lags),
                  lambda p: state_oracle(p, y, offset, states, lags, prefixes=False), 'max_state_score_error')
    for dim in [1, 2, 4]:
        model = models.RecurrentPoisson(y, x, offset, dim)
        check(model, lambda p: recurrent_oracle(p, y, x, offset, dim),
              lambda p: float(recurrent_oracle(p, y, x, offset, dim).sum()), 'max_recurrent_score_error')
    for count, eta in [(0, -80.), (1, -40.), (12, 2.), (1000, 7.)]:
        error = abs(float(models.poisson_logpmf(count, eta)) - scalar_poisson(count, eta))
        errors['max_poisson_score_error'] = max(errors['max_poisson_score_error'], error)
        errors['case_count'] += 1
    errors['causal_checks_tested'] = causal_checks()
    errors['finite_checks_passed'] = True
    errors['causal_checks_passed'] = True
    errors['trial_reset_checks_passed'] = True
    errors['gradient_error_definition'] = 'abs(analytic-FD)/max(1,abs(analytic),abs(FD)); step=1e-5'
    for key in ['max_poisson_score_error', 'max_state_score_error', 'max_recurrent_score_error']:
        if errors[key] > 1e-10:
            raise AssertionError(f'{key}: {errors[key]} > 1e-10 nats/unit-bin')
    if errors['max_gradient_error'] > 1e-6:
        raise AssertionError(f'Gradient error {errors["max_gradient_error"]} > 1e-6')
    return errors


class ModelTests(unittest.TestCase):
    def test_independent_numerical_audit(self):
        audit = numerical_audit()
        self.assertGreaterEqual(audit['case_count'], 200)
        self.assertGreater(audit['causal_checks_tested'], 0)

    def test_parameter_accounting_and_gauge(self):
        y, x, offset = fixture()
        for k, lag in itertools.product([1, 2, 4], [0, 1, 5]):
            model = models.StatePoisson(y, offset, k, lag)
            self.assertEqual(model.n_parameters, k - 1 + k * (k - 1) + k * 2 + k * 2 * lag)
            p, a, _, _ = model.unpack(model.initial(11))
            self.assertAlmostEqual(float(np.exp(p).sum()), 1., places=14)
            np.testing.assert_allclose(np.exp(a).sum(axis=1), 1., atol=1e-14, rtol=0)
        for d in [1, 2, 4]:
            model = models.RecurrentPoisson(y, x, offset, d)
            self.assertEqual(model.n_parameters, d*d + d*2 + d*2 + 2*d)
        for kind in ['stationary', 'history', 'event', 'drift', 'combined', 'population']:
            design = models.make_design(y, x, kind)
            self.assertEqual(models.PoissonGLM(design, y).n_parameters, 2 * design.shape[-1])

    def test_history_and_design_independent_indexing(self):
        y, x, _ = fixture()
        history = models.history(y, 5)
        for n, t, u, lag in itertools.product(range(2), range(3), range(2), range(1, 6)):
            expected = math.log1p(y[n, t-lag, u]) if t >= lag else 0.
            self.assertAlmostEqual(history[n, t, u, lag-1], expected, places=14)
        widths = {'stationary': 1, 'history': 6, 'event': 3, 'drift': 2, 'combined': 9, 'population': 14}
        for kind, width in widths.items():
            design = models.make_design(y, x, kind, trial_position=np.array([.2, .8]))
            self.assertEqual(design.shape, (2, 3, 2, width))
            np.testing.assert_array_equal(design[..., 0], 1.)
        population = models.make_design(y, x, 'population')
        np.testing.assert_array_equal(population[0, 1, 0, 1:11], history[0, 1].reshape(-1))

    def test_state_reductions(self):
        y, _, offset = fixture()
        reference = np.array([[math.fsum(scalar_poisson(v, e) for v, e in zip(row, eta))
                               for row, eta in zip(trial, offsets)] for trial, offsets in zip(y, offset)])
        for k in [1, 2, 4]:
            model = models.StatePoisson(y, offset, k)
            np.testing.assert_allclose(model.score_bins(np.zeros(model.n_parameters)), reference, atol=1e-12, rtol=0)
        for k in [2, 4]:
            hmm = models.StatePoisson(y, offset, k)
            theta = hmm.initial(23)
            for lag in [1, 5]:
                ar = models.StatePoisson(y, offset, k, lag)
                expanded = np.concatenate([theta, np.zeros(k * 2 * lag)])
                np.testing.assert_allclose(ar.score_bins(expanded), hmm.score_bins(theta), atol=1e-12, rtol=0)

    def test_recurrent_zero_readout_reduction(self):
        y, x, offset = fixture()
        for d in [1, 2, 4]:
            model = models.RecurrentPoisson(y, x, offset, d)
            theta = model.initial(37)
            theta[-2*d:] = 0
            self.assertAlmostEqual(model.score(theta), float(models.poisson_logpmf(y, offset).sum()), places=12)

    def test_stationary_exact_mle_and_zero_rate(self):
        y, _, _ = fixture()
        eta = models.fit_stationary(y)
        np.testing.assert_allclose(np.exp(eta), y.mean(axis=(0, 1)), atol=1e-14, rtol=0)
        self.assertEqual(float(models.poisson_logpmf(0, -np.inf)), 0.)
        self.assertEqual(float(models.poisson_logpmf(1, -np.inf)), -np.inf)
        self.assertTrue(np.all(np.isneginf(models.fit_stationary(np.zeros((1, 2, 2))))))

    def test_no_clipping_and_invalid_inputs(self):
        self.assertLess(abs(float(models.poisson_logpmf(0, 25.))/(-math.exp(25.)) - 1), 1e-14)
        y, x, offset = fixture()
        for bad in [np.array([[1.]]), y - 4, y + .5, y * np.nan]:
            with self.assertRaises(ValueError):
                models.StatePoisson(bad, offset, 2)
        with self.assertRaises(ValueError):
            models.RecurrentPoisson(y, x[:, :2], offset, 1)
        with self.assertRaises(ValueError):
            models.make_design(y, x, 'unknown')

    def test_seed_reproducibility_and_objective_normalization(self):
        y, x, offset = fixture()
        for model in [models.PoissonGLM(models.make_design(y, x, 'combined'), y),
                      models.StatePoisson(y, offset, 2, 1), models.RecurrentPoisson(y, x, offset, 2)]:
            theta = model.initial(11)
            np.testing.assert_array_equal(theta, model.initial(11))
            self.assertFalse(np.array_equal(theta, model.initial(23)))
            loss, _ = model.objective(theta, .1)
            self.assertAlmostEqual(loss, -model.score(theta)/y.size + .05*float(theta@theta), places=12)

    def test_controlled_glm_optimizer(self):
        y, x, _ = fixture()
        model = models.PoissonGLM(models.make_design(y, x, 'event'), y)
        result = models.fit_model(model, .1, 11)
        self.assertTrue(result['converged'], result['message'])
        self.assertLessEqual(result['iterations'], 500)
        theta = np.asarray(result['theta'])
        self.assertTrue(np.all(np.abs(theta) <= 8))
        self.assertLessEqual(result['loss'], model.objective(model.initial(11), .1)[0])
        self.assertAlmostEqual(result['total_loglik'], model.score(theta), places=12)

    def test_numerical_failure_is_retained(self):
        y, x, _ = fixture()
        model = models.PoissonGLM(models.make_design(y, x, 'event'), y)
        def failing_optimizer(fun, initial, args, **kwargs):
            self.assertEqual(kwargs['method'], 'L-BFGS-B')
            self.assertEqual(kwargs['bounds'], [(-8., 8.)] * model.n_parameters)
            self.assertEqual(kwargs['options'], {'maxiter': 500, 'ftol': 1e-5, 'gtol': 1e-5})
            return fun(initial, *args)
        with patch.object(models, 'minimize', side_effect=failing_optimizer):
            with patch.object(model, 'objective', side_effect=FloatingPointError('synthetic failure')):
                result = models.fit_model(model, .1, 23)
        self.assertFalse(result['converged'])
        self.assertEqual(result['nfev'], 1)
        self.assertIsNone(result['loss'])
        self.assertIsNone(result['total_loglik'])
        self.assertIn('synthetic failure', result['error'])
        np.testing.assert_array_equal(result['theta'], model.initial(23))


if __name__ == '__main__':
    unittest.main()
