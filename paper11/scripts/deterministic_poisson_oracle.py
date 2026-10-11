"""Independent finite-domain density quadrature, not Laplace or particle code."""
import itertools
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import gammaln, erfc


def scores(model, counts, offsets, order, limit=10., block=256):
    roots, weights = leggauss(order)
    indices = np.asarray(list(itertools.product(range(order), repeat=model['dimension'])))
    points = limit*roots[indices]
    volume = np.prod(limit*weights[indices], axis=1)
    initial_density = np.exp(-.5*np.sum(points**2, axis=1))/(2*np.pi)**(model['dimension']/2)
    filtered, values = None, []
    for t in range(len(counts)):
        if t == 0:
            predicted = model['initial'][:, None]*initial_density*volume
        else:
            masses = model['transition'].T@filtered
            predicted = np.zeros_like(filtered)
            for state in range(model['states']):
                means = points@model['dynamics'][state].T
                for begin in range(0, len(points), block):
                    destination = points[begin:begin+block]
                    distance = destination[None, :, :]-means[:, None, :]
                    density = np.exp(-.5*np.sum(distance**2, axis=2))/(2*np.pi)**(model['dimension']/2)
                    predicted[state, begin:begin+block] = (masses[state]@density)*volume[begin:begin+block]
        unnormalized = np.empty_like(predicted)
        for state in range(model['states']):
            eta = offsets[t]+model['biases'][state]+points@model['loadings'].T
            log_like = np.sum(counts[t]*eta-np.exp(eta)-gammaln(counts[t]+1), axis=1)
            unnormalized[state] = predicted[state]*np.exp(log_like)
        evidence = unnormalized.sum()
        if evidence <= 0 or not np.isfinite(evidence):
            raise ValueError('Unresolved deterministic oracle normalizer')
        values.append(np.log(evidence))
        filtered = unnormalized/evidence
    return np.asarray(values)


def tail_log_sensitivity(model, scores, limit=10.):
    # Stable contraction bounds covariance for every switching state sequence.
    contraction = max(np.linalg.norm(a, 2) for a in model['dynamics'])
    if contraction >= 1:
        raise ValueError('Tail bound requires stable contraction')
    variance = 1/(1-contraction**2)
    prefix = np.arange(1, len(scores)+1)
    tail = prefix*model['dimension']*erfc(limit/np.sqrt(2*variance))
    relative = tail/np.exp(np.cumsum(scores))
    if np.any(relative >= 1):
        raise ValueError('Tail bound unresolved relative to prefix evidence')
    log_bound = -np.log1p(-relative)
    return np.asarray([log_bound[t]+(log_bound[t-1] if t else 0) for t in range(len(scores))])
