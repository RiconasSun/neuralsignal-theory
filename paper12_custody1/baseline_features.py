"""Frozen P12 baseline features and train-only scaling, without fit-policy choices."""
import numpy as np
from scipy.special import gammaln


def counts(value):
    value = np.asarray(value, dtype=float)
    if value.ndim != 3 or min(value.shape) < 1 or value.shape[1] != 20:
        raise ValueError('COUNTS_REQUIRE_TRIAL_20BIN_UNIT')
    if not np.all(np.isfinite(value)) or np.any(value < 0) or np.any(value != np.floor(value)):
        raise ValueError('INVALID_COUNTS')
    return value


def history(value):
    value = counts(value)
    result = np.zeros(value.shape + (5,))
    for lag in range(1, 6):
        result[:, lag:, :, lag - 1] = np.log1p(value[:, :-lag, :])
    return result


def design(value, conditions, trial_order, kind):
    value = counts(value)
    n, t, u = value.shape
    conditions = np.asarray(conditions)
    order = np.asarray(trial_order, dtype=float)
    if conditions.shape != (n,) or conditions.dtype.kind not in 'iu' or np.any((conditions < 0) | (conditions > 7)):
        raise ValueError('FROZEN_CONDITION_ID_REQUIRED')
    if order.shape != (n,) or not np.all(np.isfinite(order)) or np.any((order < 0) | (order > 599)) or np.any(order != np.floor(order)):
        raise ValueError('FROZEN_TRIAL_ORDER_REQUIRED')
    own = history(value)
    population = np.broadcast_to(own.reshape(n, t, 1, u * 5), (n, t, u, u * 5))
    stimulus = (conditions[:, None] == np.arange(1, 8)[None, :]).astype(float)
    bins = (np.arange(t)[:, None] == np.arange(1, 20)[None, :]).astype(float)
    context = np.concatenate((np.broadcast_to(stimulus[:, None, :], (n, t, 7)),
                              np.broadcast_to(bins[None, :, :], (n, t, 19))), axis=-1)
    context = np.broadcast_to(context[:, :, None, :], (n, t, u, 26))
    position = order / 599.
    drift = np.broadcast_to(np.stack((position, position ** 2), axis=-1)[:, None, None, :], (n, t, u, 2))
    one = np.ones((n, t, u, 1))
    parts = dict(stationary=[one], history=[one, own], population=[one, population],
                 event=[one, context], drift=[one, drift],
                 combined=[one, own, population, context, drift])
    if kind not in parts:
        raise ValueError('UNREGISTERED_BASELINE')
    return np.concatenate(parts[kind], axis=-1)


def training_scaler(training_design):
    value = np.asarray(training_design, dtype=float)
    if value.ndim != 4 or not np.all(np.isfinite(value)) or not np.all(value[..., 0] == 1):
        raise ValueError('DESIGN_INTERCEPT_INVALID')
    mean = value.mean(axis=(0, 1))
    scale = value.std(axis=(0, 1))
    mean[:, 0] = 0.; scale[:, 0] = 1.
    scale[scale == 0] = 1.
    return mean, scale


def transform(value, scaler):
    mean, scale = scaler
    return (value - mean[None, None, :, :]) / scale[None, None, :, :]


def poisson_ll(value, eta):
    value = counts(value)
    eta = np.broadcast_to(np.asarray(eta, dtype=float), value.shape)
    if not np.all(np.isfinite(eta)):
        raise ValueError('INVALID_LOG_MEANS')
    with np.errstate(over='raise', invalid='raise'):
        return value * eta - np.exp(eta) - gammaln(value + 1)


def likelihood_gradient(weights, value, features):
    value = counts(value)
    features = np.asarray(features, dtype=float)
    if features.ndim != 4 or features.shape[:3] != value.shape or not np.all(np.isfinite(features)):
        raise ValueError('DESIGN_SHAPE_OR_VALUES_INVALID')
    weights = np.asarray(weights, dtype=float).reshape(value.shape[-1], features.shape[-1])
    eta = np.einsum('ntuf,uf->ntu', features, weights)
    likelihood = poisson_ll(value, eta)
    gradient = np.einsum('ntuf,ntu->uf', features, value - np.exp(eta))
    return float(likelihood.sum()), gradient.ravel()
