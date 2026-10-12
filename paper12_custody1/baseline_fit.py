"""Bounded P12 Poisson baseline fitting; no source, final data or selection access."""
import time
import numpy as np
from scipy.optimize import minimize
from baseline_features import likelihood_gradient, poisson_ll


def projected_gradient(theta, gradient):
    value = np.asarray(gradient, float).copy()
    value[(theta <= -8) & (value > 0)] = 0
    value[(theta >= 8) & (value < 0)] = 0
    return float(np.max(np.abs(value)))


def objective(theta, y, features, ridge, normalization='total_unit_bins'):
    likelihood, gradient = likelihood_gradient(theta, y, features)
    mask = np.ones((y.shape[-1], features.shape[-1])); mask[:, 0] = 0
    penalty = mask.ravel() * theta
    if normalization not in ('total_unit_bins', 'per_unit_exposure'):
        raise ValueError('RIDGE_NORMALIZATION_UNRESOLVED')
    denominator = y.size if normalization == 'total_unit_bins' else y.shape[0] * y.shape[1]
    loss = -likelihood / denominator + .5 * ridge * np.dot(penalty, penalty)
    grad = -gradient / denominator + ridge * penalty
    if not np.isfinite(loss) or not np.all(np.isfinite(grad)):
        raise FloatingPointError('NONFINITE_BASELINE_OBJECTIVE')
    return float(loss), grad


def fit(y, features, validation_y, validation_features, ridge, seed, normalization):
    start = time.perf_counter()
    size = y.shape[-1] * features.shape[-1]
    theta = np.random.default_rng(seed).normal(0., .05, size)
    result = minimize(objective, theta, args=(y, features, ridge, normalization), jac=True,
                      method='L-BFGS-B', bounds=[(-8., 8.)] * size,
                      options=dict(maxiter=500, maxfun=20000, ftol=1e-5, gtol=1e-5))
    loss, gradient = objective(result.x, y, features, ridge, normalization)
    pg = projected_gradient(result.x, gradient)
    train_ll = likelihood_gradient(result.x, y, features)[0] / y.size
    validation_ll = likelihood_gradient(result.x, validation_y, validation_features)[0] / validation_y.size
    return dict(seed=seed, ridge=ridge, ridge_normalization=normalization,
                converged=bool(result.success and pg <= .001 and
                np.isfinite(train_ll) and np.isfinite(validation_ll)),
                optimizer_success=bool(result.success), optimizer_message=str(result.message),
                iterations=int(result.nit), objective_calls=int(result.nfev),
                projected_gradient=pg, penalized_training_objective=loss,
                training_LL_nats_per_unit_bin=train_ll,
                validation_LL_nats_per_unit_bin=validation_ll,
                parameter_count=size, training_unit_bins=int(y.size),
                validation_unit_bins=int(validation_y.size),
                bound_hits=int(np.sum(np.abs(result.x) >= 8.)),
                elapsed_seconds=time.perf_counter() - start)


def stationary(y, validation_y, seed):
    start = time.perf_counter()
    mean = np.asarray(y, dtype=float).mean(axis=(0, 1))
    eta = np.log(mean)
    if not np.all(np.isfinite(eta)) or np.any(np.abs(eta) > 8):
        raise FloatingPointError('STATIONARY_BOUND_OR_FINITE_FAILURE')
    return dict(seed=seed, ridge=None, converged=True, optimizer_success=True,
                optimizer_message='Exact interior constant-rate Poisson MLE',
                iterations=0, objective_calls=1, projected_gradient=0.,
                training_LL_nats_per_unit_bin=float(poisson_ll(y, eta).sum() / y.size),
                validation_LL_nats_per_unit_bin=float(poisson_ll(validation_y, eta).sum() / validation_y.size),
                parameter_count=y.shape[-1], training_unit_bins=int(y.size),
                validation_unit_bins=int(validation_y.size), bound_hits=0,
                elapsed_seconds=time.perf_counter() - start)
