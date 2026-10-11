"""Exact predictive count models; inputs are fully observed [trial, bin, unit].

Offsets are fixed log expected counts per bin, including exposure, not log Hz.
Context is supplied by the caller and must be known at prediction time. No
transform is fitted here. Each trial resets all history and hidden state.
Caller retains every seed (11, 23, 37) and ridge (.001, .01, .1, 1) run.
"""
import time

import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp


def _counts(y):
    y = np.asarray(y, dtype=float)
    if y.ndim != 3 or min(y.shape) < 1:
        raise ValueError('Counts must have nonempty shape [N,T,U]')
    if not np.all(np.isfinite(y)) or np.any(y < 0) or np.any(y != np.floor(y)):
        raise ValueError('Counts must be finite nonnegative integers')
    return y.copy()


def _finite(value, name):
    value = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(value)):
        raise ValueError(f'{name} must be finite')
    return value


def poisson_logpmf(y, log_expected_counts):
    """Exact count PMF, including the zero-rate/zero-count boundary; no clipping."""
    y, eta = np.broadcast_arrays(np.asarray(y, float), np.asarray(log_expected_counts, float))
    if np.any(y < 0) or np.any(y != np.floor(y)) or not np.all(np.isfinite(y)):
        raise ValueError('Invalid Poisson counts')
    if np.any(np.isnan(eta)) or np.any(np.isposinf(eta)):
        raise ValueError('Invalid log expected counts')
    product = np.zeros(y.shape, dtype=float)
    np.multiply(y, eta, out=product, where=y != 0)
    with np.errstate(over='raise', invalid='raise'):
        return product - np.exp(eta) - gammaln(y + 1)


def history(y, lags=5):
    y = _counts(y)
    if not isinstance(lags, (int, np.integer)) or lags < 0:
        raise ValueError('lags must be a nonnegative integer')
    h = np.zeros(y.shape + (lags,))
    for lag in range(1, lags + 1):
        if lag < y.shape[1]:
            h[:, lag:, :, lag - 1] = np.log1p(y[:, :-lag, :])
    return h


def make_design(y, x, kind, lags=5, trial_position=None):
    """Return [N,T,U,F]; intercept, causal history, known context and drift.

    population uses all units' lagged counts plus the same context/drift as
    combined. Caller context must omit an intercept to avoid redundant columns.
    n_parameters counts trainable coefficients, not empirical design rank;
    short fixtures may have zero history columns, which are never dropped.
    """
    y = _counts(y)
    n, t, u = y.shape
    x = _finite(x, 'context')
    if x.ndim != 3 or x.shape[:2] != (n, t):
        raise ValueError('Context must have shape [N,T,X]')
    pos = np.arange(n, dtype=float) if trial_position is None else _finite(trial_position, 'trial_position')
    if pos.shape != (n,):
        raise ValueError('trial_position must have shape [N]')
    one = np.ones((n, t, u, 1))
    context = np.broadcast_to(x[:, :, None, :], (n, t, u, x.shape[-1]))
    drift = np.broadcast_to(pos[:, None, None, None], (n, t, u, 1))
    own = history(y, lags)
    population = np.broadcast_to(own.reshape(n, t, 1, u * lags), (n, t, u, u * lags))
    components = {'stationary': [one], 'history': [one, own],
                  'event': [one, context], 'drift': [one, drift],
                  'combined': [one, own, context, drift],
                  'population': [one, population, context, drift]}
    if kind not in components:
        raise ValueError(f'Unknown baseline kind: {kind}')
    return np.concatenate(components[kind], axis=-1).copy()


def fit_stationary(y):
    """Unpenalized per-unit log mean count; an all-zero unit has log rate -inf."""
    mean = _counts(y).mean(axis=(0, 1))
    with np.errstate(divide='ignore'):
        return np.log(mean)


class _Model:
    def _theta(self, theta):
        theta = _finite(theta, 'theta')
        if theta.shape != (self.n_parameters,):
            raise ValueError('Incorrect parameter-vector length')
        return theta

    def initial(self, seed):
        return np.random.default_rng(seed).normal(0, .05, self.n_parameters)

    def objective(self, theta, ridge):
        theta = self._theta(theta)
        if not np.isfinite(ridge) or ridge < 0:
            raise ValueError('ridge must be finite and nonnegative')
        ll, gradient = self._likelihood_gradient(theta)
        loss = -ll / self.y.size + .5 * ridge * np.dot(theta, theta)
        gradient = -gradient / self.y.size + ridge * theta
        if not np.isfinite(loss) or not np.all(np.isfinite(gradient)):
            raise FloatingPointError('Nonfinite objective/analytic gradient')
        return float(loss), gradient

    def score(self, theta):
        value = float(np.sum(self.score_bins(theta)))
        if not np.isfinite(value):
            raise FloatingPointError('Nonfinite predictive score')
        return value


class PoissonGLM(_Model):
    def __init__(self, design, y):
        self.y = _counts(y)
        self.design = _finite(design, 'design').copy()
        if self.design.ndim != 4 or self.design.shape[:3] != self.y.shape or self.design.shape[-1] < 1:
            raise ValueError('Design must have shape [N,T,U,F]')
        self.n_parameters = self.y.shape[-1] * self.design.shape[-1]

    def log_means(self, theta):
        weights = self._theta(theta).reshape(self.y.shape[-1], self.design.shape[-1])
        return np.einsum('ntuf,uf->ntu', self.design, weights)

    def score_bins(self, theta):
        return poisson_logpmf(self.y, self.log_means(theta)).sum(axis=-1)

    def _likelihood_gradient(self, theta):
        eta = self.log_means(theta)
        with np.errstate(over='raise', invalid='raise'):
            residual = self.y - np.exp(eta)
        grad = np.einsum('ntuf,ntu->uf', self.design, residual).ravel()
        return float(poisson_logpmf(self.y, eta).sum()), grad


def forward_backward(log_emissions, log_initial, log_transition):
    """Exact normalized log-space inference for one trial, O(T*K*K).

    Returns log-score increments, posterior gamma/xi, and predictive state
    probabilities computed before assimilating the current observed count.
    """
    e = _finite(log_emissions, 'log_emissions')
    p = _finite(log_initial, 'log_initial')
    a = _finite(log_transition, 'log_transition')
    if e.ndim != 2 or p.shape != (e.shape[1],) or a.shape != (e.shape[1], e.shape[1]):
        raise ValueError('Invalid forward/backward dimensions')
    if len(e) == 0 or not np.isclose(logsumexp(p), 0, atol=1e-12, rtol=0) or not np.allclose(logsumexp(a, axis=1), 0, atol=1e-12, rtol=0):
        raise ValueError('State probabilities must be normalized')
    t, k = e.shape
    filtered, predictive = np.empty_like(e), np.empty_like(e)
    increments = np.empty(t)
    prior = p.copy()
    for i in range(t):
        predictive[i] = np.exp(prior)
        joint = prior + e[i]
        increments[i] = logsumexp(joint)
        filtered[i] = joint - increments[i]
        if i + 1 < t:
            prior = logsumexp(filtered[i, :, None] + a, axis=0)
    beta = np.zeros_like(e)
    for i in range(t - 2, -1, -1):
        beta[i] = logsumexp(a + e[i + 1, None, :] + beta[i + 1, None, :], axis=1) - increments[i + 1]
    log_gamma = filtered + beta
    gamma = np.exp(log_gamma - logsumexp(log_gamma, axis=1, keepdims=True))
    xi = np.empty((t - 1, k, k))
    for i in range(t - 1):
        value = filtered[i, :, None] + a + e[i + 1, None, :] + beta[i + 1, None, :]
        xi[i] = np.exp(value - logsumexp(value))
    return increments, gamma, xi, predictive


class StatePoisson(_Model):
    def __init__(self, y, offset, states, lags=0):
        self.y = _counts(y)
        self.offset = _finite(offset, 'offset').copy()
        if self.offset.shape != self.y.shape:
            raise ValueError('Offset must match counts exactly')
        if not isinstance(states, (int, np.integer)) or states < 1:
            raise ValueError('states must be a positive integer')
        self.states, self.lags = states, lags
        self.history = history(self.y, lags)
        self.n_units = self.y.shape[-1]
        self.n_parameters = (states - 1) + states * (states - 1) + states * self.n_units * (1 + lags)

    def unpack(self, theta):
        theta = self._theta(theta)
        k, u, l = self.states, self.n_units, self.lags
        cut = k - 1
        init = np.concatenate([theta[:cut], [0.]])
        end = cut + k * (k - 1)
        transition = np.concatenate([theta[cut:end].reshape(k, k - 1), np.zeros((k, 1))], axis=1)
        bias_end = end + k * u
        return (init - logsumexp(init), transition - logsumexp(transition, axis=1, keepdims=True),
                theta[end:bias_end].reshape(k, u), theta[bias_end:].reshape(k, u, l))

    def log_means(self, theta):
        _, _, biases, ar = self.unpack(theta)
        return self.offset[:, :, None, :] + biases[None, None, :, :] + np.einsum('ntul,kul->ntku', self.history, ar)

    def predictions(self, theta):
        p, a, _, _ = self.unpack(theta)
        eta = self.log_means(theta)
        emissions = poisson_logpmf(self.y[:, :, None, :], eta).sum(axis=-1)
        return eta, np.stack([forward_backward(e, p, a)[3] for e in emissions])

    def score_bins(self, theta):
        p, a, _, _ = self.unpack(theta)
        emissions = poisson_logpmf(self.y[:, :, None, :], self.log_means(theta)).sum(axis=-1)
        return np.stack([forward_backward(e, p, a)[0] for e in emissions])

    def _likelihood_gradient(self, theta):
        p, a, _, _ = self.unpack(theta)
        eta = self.log_means(theta)
        emissions = poisson_logpmf(self.y[:, :, None, :], eta).sum(axis=-1)
        initial_grad = np.zeros(self.states)
        transition_grad = np.zeros((self.states, self.states))
        bias_grad = np.zeros((self.states, self.n_units))
        ar_grad = np.zeros((self.states, self.n_units, self.lags))
        ll = 0.
        for n, e in enumerate(emissions):
            increments, gamma, xi, _ = forward_backward(e, p, a)
            ll += increments.sum()
            initial_grad += gamma[0] - np.exp(p)
            transition_grad += xi.sum(axis=0) - gamma[:-1].sum(axis=0)[:, None] * np.exp(a)
            with np.errstate(over='raise', invalid='raise'):
                residual = gamma[:, :, None] * (self.y[n, :, None, :] - np.exp(eta[n]))
            bias_grad += residual.sum(axis=0)
            ar_grad += np.einsum('tku,tul->kul', residual, self.history[n])
        grad = np.concatenate([initial_grad[:-1], transition_grad[:, :-1].ravel(), bias_grad.ravel(), ar_grad.ravel()])
        return float(ll), grad


class RecurrentPoisson(_Model):
    def __init__(self, y, x, offset, dimension):
        self.y = _counts(y)
        self.x = _finite(x, 'context').copy()
        self.offset = _finite(offset, 'offset').copy()
        if self.x.ndim != 3 or self.x.shape[:2] != self.y.shape[:2] or self.offset.shape != self.y.shape:
            raise ValueError('Context/offset dimensions do not match counts')
        if not isinstance(dimension, (int, np.integer)) or dimension < 1:
            raise ValueError('dimension must be a positive integer')
        self.dimension = dimension
        d, u, xdim = dimension, self.y.shape[-1], self.x.shape[-1]
        self.shapes = [(d, d), (d, u), (d, xdim), (u, d)]
        self.n_parameters = sum(int(np.prod(s)) for s in self.shapes)

    def unpack(self, theta):
        theta = self._theta(theta)
        arrays, start = [], 0
        for shape in self.shapes:
            end = start + int(np.prod(shape))
            arrays.append(theta[start:end].reshape(shape))
            start = end
        return tuple(arrays)

    def _states(self, theta):
        a, b, d, c = self.unpack(theta)
        states = np.zeros(self.y.shape[:2] + (self.dimension,))
        past = np.zeros_like(self.y)
        past[:, 1:] = np.log1p(self.y[:, :-1])
        previous = np.zeros((len(self.y), self.dimension))
        for t in range(self.y.shape[1]):
            previous = np.tanh(previous @ a.T + past[:, t] @ b.T + self.x[:, t] @ d.T)
            states[:, t] = previous
        eta = self.offset + np.einsum('ntd,ud->ntu', states, c)
        return states, past, eta

    def log_means(self, theta):
        return self._states(theta)[2]

    def score_bins(self, theta):
        return poisson_logpmf(self.y, self.log_means(theta)).sum(axis=-1)

    def _likelihood_gradient(self, theta):
        a, b, d, c = self.unpack(theta)
        h, past, eta = self._states(theta)
        with np.errstate(over='raise', invalid='raise'):
            residual = self.y - np.exp(eta)
        ga, gb, gd = np.zeros_like(a), np.zeros_like(b), np.zeros_like(d)
        gc = np.einsum('ntu,ntd->ud', residual, h)
        carry = np.zeros((len(self.y), self.dimension))
        for t in range(self.y.shape[1] - 1, -1, -1):
            adjoint = (residual[:, t] @ c + carry) * (1 - h[:, t] ** 2)
            previous = h[:, t - 1] if t else np.zeros_like(carry)
            ga += adjoint.T @ previous
            gb += adjoint.T @ past[:, t]
            gd += adjoint.T @ self.x[:, t]
            carry = adjoint @ a
        grad = np.concatenate([v.ravel() for v in (ga, gb, gd, gc)])
        return float(poisson_logpmf(self.y, eta).sum()), grad


def fit_model(model, ridge, seed):
    """One registered candidate/seed; retain failures without fallback or clipping."""
    start = time.perf_counter()
    theta = model.initial(seed)
    result = None
    error = None
    evaluations = 0
    last_theta = theta.copy()
    def counted_objective(candidate, penalty):
        nonlocal evaluations, last_theta
        evaluations += 1
        last_theta = candidate.copy()
        return model.objective(candidate, penalty)
    try:
        result = minimize(counted_objective, theta, args=(ridge,), jac=True,
                          method='L-BFGS-B', bounds=[(-8., 8.)] * model.n_parameters,
                          options={'maxiter': 500, 'ftol': 1e-5, 'gtol': 1e-5})
        theta = result.x
        loss, grad = model.objective(theta, ridge)
        ll = model.score(theta)
        finite = np.isfinite(loss) and np.isfinite(ll) and np.all(np.isfinite(grad))
    except (FloatingPointError, OverflowError, ValueError) as exc:
        error = f'{type(exc).__name__}: {exc}'
        if result is None:
            theta = last_theta
        loss, ll, grad, finite = None, None, None, False
    return {'theta': theta.tolist(), 'converged': bool(result is not None and result.success and finite),
            'iterations': int(result.nit) if result is not None else 0,
            'nfev': int(result.nfev) if result is not None else evaluations,
            'loss': float(loss) if finite else None, 'total_loglik': float(ll) if finite else None,
            'gradient_norm': float(np.linalg.norm(grad, ord=np.inf)) if finite else None,
            'bound_hits': int(np.count_nonzero(np.isclose(np.abs(theta), 8., atol=1e-8, rtol=0))),
            'elapsed_seconds': time.perf_counter() - start,
            'status': int(result.status) if result is not None else None,
            'message': str(result.message) if result is not None else error,
            'error': error, 'seed': int(seed), 'ridge': float(ridge)}
