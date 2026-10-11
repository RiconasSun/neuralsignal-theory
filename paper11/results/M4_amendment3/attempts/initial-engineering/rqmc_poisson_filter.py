"""Scrambled-net guided SMC; exact target corrections, no SQMC rate claim."""
import numpy as np
from scipy.special import gammaln, ndtri
from scipy.stats import qmc
import guided_poisson_filter as guided


def uniforms(count, dimension, seed, step, method):
    if count <= 0 or count & (count - 1):
        raise ValueError('Power-of-two particle budget required')
    generator = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(step,)))
    if method == 'rqmc':
        values = qmc.Sobol(dimension, scramble=True, bits=52, rng=generator).random_base2(count.bit_length()-1)
    elif method == 'mc':
        values = generator.random((count, dimension))
    else:
        raise ValueError('Unknown numerical method')
    if np.any(values <= 0) or np.any(values >= 1):
        raise ValueError('Uniform endpoint encountered; do not clip Gaussian quantiles')
    return values


def inverse_cdf(probabilities, values):
    probabilities = np.asarray(probabilities)
    if not np.isfinite(probabilities).all() or np.any(probabilities < 0) or not np.allclose(probabilities.sum(axis=-1), 1, atol=1e-12, rtol=1e-12):
        raise ValueError('Invalid inverse-CDF probabilities')
    cumulative = np.cumsum(probabilities, axis=-1)
    cumulative[..., -1] = 1.
    return (values[:, None] >= cumulative).sum(axis=-1)


def particle(model, y, offsets, count, seed, method='rqmc', defensive=.1):
    if not 0 < defensive < 1:
        raise ValueError('Invalid defensive fraction')
    dimension, states = model['dimension'], model['states']
    loadings = model['loadings']
    cloud, state_cloud, weights = None, None, None
    scores, effective, largest, gradients = [], [], [], []
    nonconverged, overflow = 0, 0
    for step in range(len(y)):
        u = uniforms(count, dimension+3, seed, step, method)
        if step == 0:
            prior_states = np.broadcast_to(model['initial'], (count, states))
            ancestors_latent = np.zeros((count, dimension))
        else:
            # Ordering changes the uniform-to-ancestor map, not the target law.
            order = np.lexsort(tuple(cloud[:, k] for k in range(dimension-1, -1, -1)) + (state_cloud,))
            cloud, state_cloud, weights = cloud[order], state_cloud[order], weights[order]
            ancestors = inverse_cdf(weights, u[:, 0])
            ancestors_latent = cloud[ancestors]
            prior_states = model['transition'][state_cloud[ancestors]]
        sampled = inverse_cdf(prior_states, u[:, 1])
        log_ps = np.log(prior_states[np.arange(count), sampled])
        log_qs = log_ps.copy()  # State proposal equals prior, explicit correction.
        means = (np.zeros((count, dimension)) if step == 0 else
                 np.einsum('ndf,nf->nd', model['dynamics'][sampled], ancestors_latent))
        normal = ndtri(u[:, 3:])
        latent, log_q = np.empty_like(means), np.empty(count)
        for state in range(states):
            chosen = np.flatnonzero(sampled == state)
            if not len(chosen):
                continue
            if not np.any(loadings):
                latent[chosen] = means[chosen]+normal[chosen]
                log_q[chosen] = guided.log_gaussian(latent[chosen], means[chosen], np.eye(dimension))
                continue
            if step == 0:
                mean, covariance = np.zeros(dimension), np.eye(dimension)
            else:
                prior_means = cloud @ model['dynamics'][state].T
                state_weight = weights * model['transition'][state_cloud, state]
                state_weight /= state_weight.sum()
                mean = state_weight @ prior_means
                delta = prior_means-mean
                covariance = np.eye(dimension)+(delta.T*state_weight)@delta
            mode, precision, diagnostic = guided.laplace(y[step], offsets[step], model['biases'][state], loadings, mean, covariance)
            gradients.append(diagnostic['gradient_max'])
            nonconverged += not diagnostic['converged']
            draws = mode+np.linalg.solve(np.linalg.cholesky(precision).T, normal[chosen].T).T
            use_prior = u[chosen, 2] < defensive
            draws[use_prior] = means[chosen][use_prior]+normal[chosen][use_prior]
            latent[chosen] = draws
            prior_density = guided.log_gaussian(draws, means[chosen], np.eye(dimension))
            guided_density = guided.log_gaussian(draws, mode, precision)
            log_q[chosen] = np.logaddexp(np.log1p(-defensive)+guided_density, np.log(defensive)+prior_density)
        eta = offsets[step]+model['biases'][sampled]+latent@loadings.T
        if not np.isfinite(eta).all():
            raise ValueError('Nonfinite log rate')
        with np.errstate(over='ignore'):
            rate = np.exp(eta)
        overflow += int(np.isinf(rate).sum())
        likelihood = np.sum(y[step]*eta-rate-gammaln(y[step]+1), axis=1)
        log_prior = guided.log_gaussian(latent, means, np.eye(dimension))
        log_weight = guided.correction(likelihood, log_prior, log_q, log_ps, log_qs)
        score, weights, ess = guided.normalize(log_weight)
        scores.append(score)
        effective.append(ess/count)
        largest.append(float(weights.max()))
        cloud, state_cloud = latent, sampled
    return np.asarray(scores), {'method': method, 'minimum_ess_fraction': min(effective),
        'maximum_particle_weight': max(largest), 'laplace_gradient_max': max(gradients, default=0.),
        'laplace_nonconverged_guides': int(nonconverged), 'overflow_rates': overflow,
        'importance_correction': 'exact ancestor prior/full mixture q; initial and state correction',
        'resampling': 'weighted inverse CDF of ordered cloud; fresh scramble each time step'}
