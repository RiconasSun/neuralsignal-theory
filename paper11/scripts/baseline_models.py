"""Causal Poisson baselines. Fitting inputs are training arrays only."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln

FAMILIES = ('stationary', 'history', 'task', 'timing', 'drift', 'combined')


def design(counts, trial_ids, set_sizes, total_trials, family):
    y = np.asarray(counts, dtype=float)
    trials, bins, units = y.shape
    if bins != 60 or len(trial_ids) != trials or len(set_sizes) != trials:
        raise ValueError('Count/metadata shape mismatch')
    t = np.arange(60)
    columns = [np.ones((trials, bins, units))]
    names = ['intercept']
    encoding = ((t >= 10) & (t < 30)).astype(float)
    maintenance = (t >= 30).astype(float)
    def common(values, name):
        columns.append(np.broadcast_to(np.asarray(values)[..., None], y.shape).copy())
        names.append(name)
    if family in ('task', 'combined'):
        for phase, indicator in [('encoding', encoding), ('maintenance', maintenance)]:
            common(np.broadcast_to(indicator, (trials, bins)), phase)
            for load in (4, 8):
                common((np.asarray(set_sizes) == load)[:, None] * indicator[None, :], phase + '_load' + str(load))
    if family in ('timing', 'combined'):
        if family == 'timing':
            common(np.broadcast_to(encoding, (trials, bins)), 'encoding')
            common(np.broadcast_to(maintenance, (trials, bins)), 'maintenance')
        for harmonic in range(1, 7):
            common(np.broadcast_to(np.sin(2 * np.pi * harmonic * t / bins), (trials, bins)), f'sin{harmonic}')
            common(np.broadcast_to(np.cos(2 * np.pi * harmonic * t / bins), (trials, bins)), f'cos{harmonic}')
    if family in ('drift', 'combined'):
        position = np.asarray(trial_ids) / total_trials
        common(np.broadcast_to(position[:, None], (trials, bins)), 'trial_position')
        common(np.broadcast_to(position[:, None] ** 2, (trials, bins)), 'trial_position_squared')
    if family in ('history', 'combined'):
        for lag in range(1, 6):
            history = np.zeros_like(y)
            history[:, lag:, :] = np.log1p(y[:, :-lag, :])
            columns.append(history)
            names.append(f'past_count_lag{lag}')
    if family not in FAMILIES:
        raise ValueError('Unknown baseline family')
    return np.stack(columns, axis=-1), names


def fit_poisson(x, counts, alpha, maxiter=500):
    x = np.asarray(x, dtype=float)
    y = np.asarray(counts, dtype=float).reshape(-1, np.shape(counts)[-1])
    x = x.reshape(y.shape[0], y.shape[1], -1)
    mean, scale = x.mean(axis=0), x.std(axis=0)
    mean[:, 0], scale[:, 0] = 0, 1
    scale[scale < 1e-12] = 1
    standardized = (x - mean) / scale
    coefficients = np.zeros((y.shape[1], x.shape[-1]))
    coefficients[:, 0] = np.log(y.mean(axis=0) / 0.1)
    if np.any(~np.isfinite(coefficients)):
        raise ValueError('Training unit has no spikes')
    def objective(flat):
        beta = flat.reshape(coefficients.shape)
        eta = np.einsum('nup,up->nu', standardized, beta) + np.log(0.1)
        with np.errstate(over='ignore'):
            rate = np.exp(eta)
        value = np.sum(rate - y * eta) / len(y) + alpha / 2 * np.sum(beta[:, 1:] ** 2)
        gradient = np.einsum('nup,nu->up', standardized, rate - y) / len(y)
        gradient[:, 1:] += alpha * beta[:, 1:]
        return value, gradient.ravel()
    if x.shape[-1] == 1:
        result = {'success': True, 'iterations': 0, 'gradient_max': 0.0, 'message': 'exact stationary MLE'}
    else:
        optimum = minimize(objective, coefficients.ravel(), method='L-BFGS-B', jac=True,
                           options={'maxiter': maxiter, 'ftol': 1e-12, 'gtol': 1e-6, 'maxls': 40})
        coefficients = optimum.x.reshape(coefficients.shape)
        value, gradient = objective(optimum.x)
        gradient_max = float(np.max(np.abs(gradient)))
        result = {'success': bool(optimum.success and np.isfinite(value) and gradient_max <= 1e-4),
                  'iterations': int(optimum.nit), 'gradient_max': gradient_max, 'message': str(optimum.message)}
    return {'coefficients': coefficients, 'train_mean': mean, 'train_scale': scale,
            'alpha': alpha, 'parameters': int(coefficients.size), 'convergence': result}


def score(model, x, counts):
    y = np.asarray(counts, dtype=float)
    standardized = (np.asarray(x) - model['train_mean']) / model['train_scale']
    eta = np.einsum('tbup,up->tbu', standardized, model['coefficients']) + np.log(0.1)
    values = y * eta - np.exp(eta) - gammaln(y + 1)
    if not np.all(np.isfinite(values)):
        raise ValueError('Nonfinite predictive Poisson score')
    return values.mean(axis=(1, 2))


def choose(candidates):
    best = max(candidates, key=lambda row: row['validation_mean'])
    threshold = best['validation_mean'] - best['validation_se']
    eligible = [row for row in candidates if row['validation_mean'] >= threshold]
    return min(eligible, key=lambda row: (row['parameters'], -row['alpha'], row['family']))
