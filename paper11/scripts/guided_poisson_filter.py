"""Defensive Laplace proposals; approximations affect q only, never the target."""
import numpy as np
from scipy.special import gammaln, logsumexp

LOG2PI = np.log(2 * np.pi)


def log_gaussian(value, mean, precision):
    delta = np.asarray(value) - mean
    np.linalg.cholesky(precision)
    sign, logdet = np.linalg.slogdet(precision)
    if sign <= 0:
        raise ValueError('Nonpositive proposal precision')
    return -.5 * (delta.shape[-1] * LOG2PI - logdet + np.einsum('...d,de,...e->...', delta, precision, delta))


def correction(log_likelihood, log_prior_latent, log_proposal_latent, log_prior_state, log_proposal_state):
    return log_likelihood + log_prior_latent - log_proposal_latent + log_prior_state - log_proposal_state


def normalize(log_weights):
    normalizer = logsumexp(log_weights)
    if not np.isfinite(normalizer):
        raise ValueError('Degenerate/nonfinite importance weights')
    weights = np.exp(log_weights - normalizer)
    return normalizer - np.log(len(weights)), weights, float(1 / np.sum(weights ** 2))


def resample(weights, rng):
    if not np.isfinite(weights).all() or np.any(weights < 0) or not np.isclose(weights.sum(), 1):
        raise ValueError('Invalid resampling weights')
    cumulative = np.cumsum(weights)
    cumulative[-1] = 1.
    positions = (rng.random() + np.arange(len(weights))) / len(weights)
    return np.searchsorted(cumulative, positions, side='right')


def draw_states(prior, rng, proposal=None):
    prior = np.asarray(prior)
    proposal = prior if proposal is None else np.asarray(proposal)
    if prior.shape != proposal.shape or np.any(prior < 0) or np.any(proposal < 0):
        raise ValueError('State probability shape/support')
    if np.any((prior > 0) & (proposal == 0)):
        raise ValueError('Proposal loses positive target support')
    if not np.allclose(prior.sum(axis=1), 1, rtol=1e-12, atol=1e-12) or not np.allclose(proposal.sum(axis=1), 1, rtol=1e-12, atol=1e-12):
        raise ValueError('State probabilities not normalized')
    cumulative = np.cumsum(proposal, axis=1)
    cumulative[:, -1] = 1.
    states = (rng.random(len(prior))[:, None] >= cumulative).sum(axis=1)
    indices = np.arange(len(prior))
    with np.errstate(divide='ignore'):
        return states, np.log(prior[indices, states]), np.log(proposal[indices, states])


def laplace(y, offset, bias, loadings, mean, covariance, iterations=30, tolerance=1e-8):
    precision = np.linalg.inv(covariance)
    def objective(z):
        eta = offset + bias + loadings @ z
        with np.errstate(over='ignore'):
            rate = np.exp(eta)
        return float(y @ eta - rate.sum() - .5 * (z - mean) @ precision @ (z - mean))
    z = mean.copy()
    converged = False
    for iteration in range(iterations):
        eta = offset + bias + loadings @ z
        rate = np.exp(eta)
        gradient = loadings.T @ (rate - y) + precision @ (z - mean)
        hessian = precision + loadings.T @ (rate[:, None] * loadings)
        if not np.isfinite(gradient).all() or not np.isfinite(hessian).all():
            raise ValueError('Nonfinite Laplace derivative')
        if np.max(np.abs(gradient)) <= tolerance:
            converged = True
            break
        step = np.linalg.solve(hessian, gradient)
        previous, scale = objective(z), 1.
        for _ in range(20):
            candidate = z - scale * step
            if objective(candidate) >= previous - 1e-12:
                z = candidate
                break
            scale /= 2
        else:
            raise ValueError('Laplace line search failed')
    rate = np.exp(offset + bias + loadings @ z)
    gradient = loadings.T @ (rate - y) + precision @ (z - mean)
    hessian = precision + loadings.T @ (rate[:, None] * loadings)
    np.linalg.cholesky(hessian)
    return z, hessian, {'iterations': iteration + 1, 'gradient_max': float(np.max(np.abs(gradient))),
                       'converged': bool(converged or np.max(np.abs(gradient)) <= tolerance)}


def particle(model, y, offsets, particles, seed, defensive=.1):
    if not 0 < defensive < 1:
        raise ValueError('Defensive fraction must preserve both mixture components')
    rng = np.random.default_rng(seed)
    dimension, states = model['dimension'], model['states']
    loadings = model['loadings']
    previous_states = previous_latent = None
    scores, ess, largest, gradients, convergences = [], [], [], [], []
    overflow = 0
    for t in range(len(y)):
        state_prior = (np.broadcast_to(model['initial'], (particles, states)) if t == 0
                       else model['transition'][previous_states])
        sampled, log_ps, log_qs = draw_states(state_prior, rng)
        means = (np.zeros((particles, dimension)) if t == 0 else
                 np.einsum('ndf,nf->nd', model['dynamics'][sampled], previous_latent))
        latent = np.empty_like(means)
        log_q = np.empty(particles)
        for state in range(states):
            chosen = np.flatnonzero(sampled == state)
            if not len(chosen):
                continue
            if not np.any(loadings):
                latent[chosen] = means[chosen] + rng.normal(size=(len(chosen), dimension))
                log_q[chosen] = log_gaussian(latent[chosen], means[chosen], np.eye(dimension))
                continue
            if t == 0:
                predictive_mean, predictive_covariance = np.zeros(dimension), np.eye(dimension)
            else:
                prior_means = previous_latent @ model['dynamics'][state].T
                state_weights = state_prior[:, state] / state_prior[:, state].sum()
                predictive_mean = state_weights @ prior_means
                delta = prior_means - predictive_mean
                predictive_covariance = np.eye(dimension) + (delta.T * state_weights) @ delta
            mode, precision, diagnostic = laplace(y[t], offsets[t], model['biases'][state], loadings,
                                                  predictive_mean, predictive_covariance)
            gradients.append(diagnostic['gradient_max'])
            convergences.append(diagnostic['converged'])
            chol = np.linalg.cholesky(precision)
            draws = mode + np.linalg.solve(chol.T, rng.normal(size=(dimension, len(chosen)))).T
            prior_component = rng.random(len(chosen)) < defensive
            draws[prior_component] = means[chosen][prior_component] + rng.normal(size=(int(prior_component.sum()), dimension))
            latent[chosen] = draws
            log_guided = log_gaussian(draws, mode, precision)
            log_prior = log_gaussian(draws, means[chosen], np.eye(dimension))
            log_q[chosen] = np.logaddexp(np.log1p(-defensive) + log_guided, np.log(defensive) + log_prior)
        eta = offsets[t] + model['biases'][sampled] + latent @ loadings.T
        if not np.isfinite(eta).all():
            raise ValueError('Nonfinite proposed log rate')
        with np.errstate(over='ignore', under='ignore'):
            rate = np.exp(eta)
        overflow += int(np.isinf(rate).sum())
        likes = np.sum(y[t] * eta - rate - gammaln(y[t] + 1), axis=1)
        log_prior = log_gaussian(latent, means, np.eye(dimension))
        log_weights = correction(likes, log_prior, log_q, log_ps, log_qs)
        score, weights, effective = normalize(log_weights)
        scores.append(score)
        ess.append(effective / particles)
        largest.append(float(weights.max()))
        ancestors = resample(weights, rng)
        previous_states, previous_latent = sampled[ancestors], latent[ancestors]
    return np.asarray(scores), {'minimum_ess_fraction': min(ess), 'mean_ess_fraction': float(np.mean(ess)),
        'maximum_particle_weight': max(largest), 'overflow_rates': overflow, 'roundoff_resampling_boundary_count': 0,
        'laplace_gradient_max': max(gradients, default=0), 'laplace_nonconverged_guides': sum(not x for x in convergences),
        'state_proposal': 'original prior; state log correction evaluated explicitly',
        'latent_proposal': '90% shared state Laplace guide +10% ancestor-specific transition prior; full mixture density correction'}
