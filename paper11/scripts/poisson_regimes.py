"""Poisson state-space families with exact HMM and variational Gaussian training."""
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import minimize
from scipy.special import gammaln, logsumexp


def normalize(values):
    values = np.maximum(values, 1e-12)
    return values / values.sum(axis=-1, keepdims=True)


def forward_backward(log_likes, initial, transition):
    times, states = log_likes.shape
    alpha = np.zeros_like(log_likes)
    alpha[0] = np.log(initial) + log_likes[0]
    log_t = np.log(transition)
    for t in range(1, times):
        alpha[t] = log_likes[t] + logsumexp(alpha[t - 1][:, None] + log_t, axis=0)
    normalizer = logsumexp(alpha[-1])
    beta = np.zeros_like(alpha)
    for t in range(times - 2, -1, -1):
        beta[t] = logsumexp(log_t + log_likes[t + 1][None, :] + beta[t + 1][None, :], axis=1)
    gamma = np.exp(alpha + beta - normalizer)
    xi = np.array([np.exp(alpha[t][:, None] + log_t + log_likes[t + 1][None, :] + beta[t + 1][None, :] - normalizer) for t in range(times - 1)])
    return gamma, xi, float(normalizer)


def poisson_likes(y, offset, biases, latent_mean=None, latent_cov=None, loadings=None):
    eta = offset[:, None, :] + biases[None, :, :]
    variance = np.zeros((len(y), y.shape[1]))
    if latent_mean is not None:
        eta = eta + (latent_mean @ loadings.T)[:, None, :]
        variance = np.einsum('ud,tdf,uf->tu', loadings, latent_cov, loadings)
    return np.sum(y[:, None, :] * eta - np.exp(eta + 0.5 * variance[:, None, :]) - gammaln(y[:, None, :] + 1), axis=-1)


def fit_hmm(y, offsets, states, seed, maximum=500, tolerance=1e-5):
    rng = np.random.default_rng(seed)
    units = y.shape[-1]
    model = {'family': 'discrete', 'states': states, 'dimension': 0,
             'initial': np.ones(states) / states, 'transition': normalize(np.eye(states) * 4 + rng.random((states, states))),
             'biases': rng.normal(0, 0.1, (states, units))}
    objectives, stable = [], 0
    for iteration in range(maximum):
        results = [forward_backward(poisson_likes(trial, off, model['biases']), model['initial'], model['transition']) for trial, off in zip(y, offsets)]
        value = sum(row[2] for row in results) / y.size
        objectives.append(value)
        if iteration and abs(value - objectives[-2]) < tolerance:
            stable += 1
        else:
            stable = 0
        if stable >= 5:
            break
        weights = np.array([row[0] for row in results])
        model['initial'] = normalize(weights[:, 0].sum(axis=0))
        model['transition'] = normalize(sum(row[1].sum(axis=0) for row in results))
        numerator = np.einsum('ntk,ntu->ku', weights, y) + 1e-6
        denominator = np.einsum('ntk,ntu->ku', weights, np.exp(offsets)) + 1e-6
        model['biases'] = np.log(numerator / denominator)
    model['converged'] = stable >= 5 and np.all(np.isfinite(objectives))
    model['iterations'], model['training_objectives'] = iteration + 1, objectives
    return model


def gaussian_chain(y, offset, weights, model, start, covariance):
    times, units = y.shape
    dimension = model['dimension']
    a, c, biases = model['dynamics'], model['loadings'], model['biases']
    prior = np.zeros((times * dimension, times * dimension))
    prior[:dimension, :dimension] = np.eye(dimension)
    for t in range(1, times):
        current = slice(t * dimension, (t + 1) * dimension)
        previous = slice((t - 1) * dimension, t * dimension)
        mean_a = np.einsum('k,kdf->df', weights[t], a)
        aa = np.einsum('k,kdi,kdj->ij', weights[t], a, a)
        prior[current, current] += np.eye(dimension)
        prior[previous, previous] += aa
        prior[current, previous] -= mean_a
        prior[previous, current] -= mean_a.T
    variance = np.einsum('ud,tdf,uf->tu', c, covariance, c)
    offset_rate = np.sum(weights[:, :, None] * np.exp(offset[:, None, :] + biases[None, :, :] + 0.5 * variance[:, None, :]), axis=1)
    def objective(flat):
        latent = flat.reshape(times, dimension)
        rates = offset_rate * np.exp(latent @ c.T)
        value = 0.5 * flat @ prior @ flat + np.sum(rates - y * (latent @ c.T))
        gradient = (prior @ flat).reshape(times, dimension) + (rates - y) @ c
        return value, gradient.ravel()
    optimum = minimize(objective, start.ravel(), method='L-BFGS-B', jac=True,
                       options={'maxiter': 100, 'ftol': 1e-11, 'gtol': 1e-5, 'maxls': 30})
    mean = optimum.x.reshape(times, dimension)
    rates = offset_rate * np.exp(mean @ c.T)
    precision = prior.copy()
    for t in range(times):
        block = slice(t * dimension, (t + 1) * dimension)
        precision[block, block] += (c.T * rates[t]) @ c
    factor = cho_factor(precision)
    joint_cov = cho_solve(factor, np.eye(times * dimension))
    diag = np.array([joint_cov[t * dimension:(t + 1) * dimension, t * dimension:(t + 1) * dimension] for t in range(times)])
    cross = np.array([joint_cov[t * dimension:(t + 1) * dimension, (t - 1) * dimension:t * dimension] for t in range(1, times)])
    logdet_cov = -2 * np.log(np.diag(factor[0])).sum()
    entropy = 0.5 * (times * dimension * (1 + np.log(2 * np.pi)) + logdet_cov)
    return mean, diag, cross, float(entropy), bool(optimum.success)


def dynamics_likes(mean, covariance, cross, dynamics):
    times, dimension = mean.shape
    likes = np.zeros((times, len(dynamics)))
    initial = -0.5 * (dimension * np.log(2 * np.pi) + mean[0] @ mean[0] + np.trace(covariance[0]))
    likes[0] = initial
    for state, a in enumerate(dynamics):
        residual = mean[1:] - mean[:-1] @ a.T
        variance = covariance[1:] + np.einsum('di,tij,fj->tdf', a, covariance[:-1], a)
        variance -= np.einsum('tij,fj->tif', cross, a)
        variance -= np.einsum('di,tji->tdj', a, cross)
        likes[1:, state] = -0.5 * (dimension * np.log(2 * np.pi) + np.sum(residual**2, axis=1) + np.trace(variance, axis1=1, axis2=2))
    return likes


def update_emissions(y, offsets, means, covariances, weights, model):
    states, units = model['biases'].shape
    dimension = model['dimension']
    data = y.reshape(-1, units)
    offset = offsets.reshape(-1, units)
    mean = means.reshape(-1, dimension)
    covariance = covariances.reshape(-1, dimension, dimension)
    weight = weights.reshape(-1, states)
    failures = 0
    for unit in range(units):
        initial = np.r_[model['loadings'][unit], model['biases'][:, unit]]
        def objective(parameters):
            c, bias = parameters[:dimension], parameters[dimension:]
            variance = np.einsum('d,tdf,f->t', c, covariance, c)
            eta = offset[:, unit, None] + (mean @ c)[:, None] + bias[None, :]
            rates = np.exp(eta + 0.5 * variance[:, None])
            expected_rate = (weight * rates).sum(axis=1)
            value = np.sum(weight * (rates - data[:, unit, None] * eta)) / len(data) + 5e-7 * (parameters @ parameters)
            gradient_c = mean.T @ (expected_rate - data[:, unit]) / len(data)
            gradient_c += np.einsum('t,tdf,f->d', expected_rate, covariance, c) / len(data)
            gradient_bias = np.sum(weight * (rates - data[:, unit, None]), axis=0) / len(data)
            return value, np.r_[gradient_c, gradient_bias] + 1e-6 * parameters
        optimum = minimize(objective, initial, method='L-BFGS-B', jac=True,
                           options={'maxiter': 100, 'ftol': 1e-11, 'gtol': 1e-5, 'maxls': 30})
        model['loadings'][unit] = optimum.x[:dimension]
        model['biases'][:, unit] = optimum.x[dimension:]
        failures += int(not optimum.success or not np.isfinite(optimum.fun))
    return failures


def fit_latent(y, offsets, states, dimension, seed, maximum=500, tolerance=1e-5):
    rng = np.random.default_rng(seed)
    trials, times, units = y.shape
    residual = np.log(y.reshape(-1, units) + 0.5) - offsets.reshape(-1, units)
    _, _, vectors = np.linalg.svd(residual - residual.mean(axis=0), full_matrices=False)
    c = vectors[:dimension].T * 0.1 + rng.normal(0, 0.01, (units, dimension))
    model = {'family': 'continuous' if states == 1 else 'hybrid', 'states': states, 'dimension': dimension,
             'initial': np.ones(states) / states, 'transition': normalize(np.eye(states) * 4 + rng.random((states, states))),
             'dynamics': np.array([np.eye(dimension) * 0.5 + rng.normal(0, 0.03, (dimension, dimension)) for _ in range(states)]),
             'loadings': c, 'biases': rng.normal(0, 0.03, (states, units))}
    means = np.zeros((trials, times, dimension))
    covariances = np.tile(np.eye(dimension), (trials, times, 1, 1))
    weights = np.ones((trials, times, states)) / states
    objectives, stable, inner_failures = [], 0, 0
    for iteration in range(maximum):
        cross_covs, entropies, xis = [], [], []
        for trial in range(trials):
            mean, cov, cross, entropy, success = gaussian_chain(y[trial], offsets[trial], weights[trial], model, means[trial], covariances[trial])
            inner_failures += int(not success)
            means[trial], covariances[trial] = mean, cov
            likes = poisson_likes(y[trial], offsets[trial], model['biases'], mean, cov, model['loadings'])
            likes += dynamics_likes(mean, cov, cross, model['dynamics'])
            gamma, xi, normalizer = forward_backward(likes, model['initial'], model['transition'])
            weights[trial] = gamma
            cross_covs.append(cross)
            xis.append(xi)
            entropies.append(normalizer + entropy)
        value = sum(entropies) / y.size
        objectives.append(value)
        if iteration and abs(value - objectives[-2]) < tolerance:
            stable += 1
        else:
            stable = 0
        if stable >= 5:
            break
        model['initial'] = normalize(weights[:, 0].sum(axis=0))
        model['transition'] = normalize(sum(xi.sum(axis=0) for xi in xis))
        for state in range(states):
            xx = np.eye(dimension) * 1e-6
            next_previous = np.zeros_like(xx)
            for trial in range(trials):
                for t in range(1, times):
                    weight = weights[trial, t, state]
                    xx += weight * (covariances[trial, t - 1] + np.outer(means[trial, t - 1], means[trial, t - 1]))
                    next_previous += weight * (cross_covs[trial][t - 1] + np.outer(means[trial, t], means[trial, t - 1]))
            model['dynamics'][state] = np.linalg.solve(xx, next_previous.T).T
        inner_failures += update_emissions(y, offsets, means, covariances, weights, model)
    model['converged'] = stable >= 5 and inner_failures == 0 and np.all(np.isfinite(objectives))
    model['iterations'], model['training_objectives'], model['inner_failures'] = iteration + 1, objectives, inner_failures
    return model


def exact_predictive(model, y, offset):
    log_probability, state = 0.0, model['initial'].copy()
    scores = []
    for t in range(len(y)):
        if t:
            state = state @ model['transition']
        likes = poisson_likes(y[t:t+1], offset[t:t+1], model['biases'])[0]
        prediction = logsumexp(np.log(state) + likes)
        scores.append(prediction)
        state = np.exp(np.log(state) + likes - prediction)
        log_probability += prediction
    return np.array(scores)


def particle_predictive(model, y, offset, particles, seed):
    rng = np.random.default_rng(seed)
    states, dimension = model['states'], model['dimension']
    state = rng.choice(states, particles, p=model['initial'])
    latent = rng.normal(size=(particles, dimension))
    scores = []
    for t in range(len(y)):
        eta = offset[t] + model['biases'][state] + latent @ model['loadings'].T
        likes = np.sum(y[t] * eta - np.exp(eta) - gammaln(y[t] + 1), axis=1)
        normalizer = logsumexp(likes)
        scores.append(normalizer - np.log(particles))
        weights = np.exp(likes - normalizer)
        positions = (rng.random() + np.arange(particles)) / particles
        ancestors = np.searchsorted(np.cumsum(weights), positions, side='right')
        ancestors = np.minimum(ancestors, particles - 1)
        state, latent = state[ancestors], latent[ancestors]
        cumulative = np.cumsum(model['transition'][state], axis=1)
        state = (rng.random(particles)[:, None] > cumulative).sum(axis=1)
        state = np.minimum(state, states - 1)
        latent = np.einsum('ndf,nf->nd', model['dynamics'][state], latent) + rng.normal(size=latent.shape)
    return np.array(scores)
