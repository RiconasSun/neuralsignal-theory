"""Same frozen models/optimizer, with exact batch-parallel state inference."""
import numpy as np
from scipy.special import logsumexp

import predictive_models as frozen
from predictive_models_code1 import RecurrentPoisson

PoissonGLM = frozen.PoissonGLM
make_design = frozen.make_design
fit_model = frozen.fit_model
fit_stationary = frozen.fit_stationary
poisson_logpmf = frozen.poisson_logpmf


def batch_inference(emissions, initial, transition, posterior=False):
    e = frozen._finite(emissions, 'emissions')
    if e.ndim != 3 or e.shape[1] < 1:
        raise ValueError('Expected nonempty [trial,time,state] emissions')
    n, t, k = e.shape
    if initial.shape != (k,) or transition.shape != (k,k):
        raise ValueError('Inconsistent state probabilities')
    if not np.isclose(logsumexp(initial), 0, atol=1e-12, rtol=0) or not np.allclose(logsumexp(transition,axis=1),0,atol=1e-12,rtol=0):
        raise ValueError('State probabilities not normalized')
    f, increments = np.empty_like(e), np.empty((n,t))
    prior = np.broadcast_to(initial,(n,k))
    for j in range(t):
        joint = prior+e[:,j]
        increments[:,j] = logsumexp(joint,axis=1)
        f[:,j] = joint-increments[:,j,None]
        prior = logsumexp(f[:,j,:,None]+transition[None,:,:],axis=1)
    if not posterior:
        return increments
    b = np.zeros_like(e)
    for j in range(t-2,-1,-1):
        b[:,j] = logsumexp(transition[None,:,:]+e[:,j+1,None,:]+b[:,j+1,None,:],axis=2)-increments[:,j+1,None]
    log_gamma = f+b
    gamma = np.exp(log_gamma-logsumexp(log_gamma,axis=2,keepdims=True))
    xi_log = f[:,:-1,:,None]+transition[None,None,:,:]+e[:,1:,None,:]+b[:,1:,None,:]
    xi = np.exp(xi_log-logsumexp(xi_log,axis=(2,3),keepdims=True))
    return increments,gamma,xi


class StatePoisson(frozen.StatePoisson):
    def score_bins(self,theta):
        p,a,_,_ = self.unpack(theta)
        e = poisson_logpmf(self.y[:,:,None,:],self.log_means(theta)).sum(axis=-1)
        return batch_inference(e,p,a)

    def _likelihood_gradient(self,theta):
        p,a,_,_ = self.unpack(theta)
        eta = self.log_means(theta)
        e = poisson_logpmf(self.y[:,:,None,:],eta).sum(axis=-1)
        increments,gamma,xi = batch_inference(e,p,a,posterior=True)
        initial = gamma[:,0].sum(axis=0)-len(self.y)*np.exp(p)
        transition = xi.sum(axis=(0,1))-gamma[:,:-1].sum(axis=(0,1))[:,None]*np.exp(a)
        with np.errstate(over='raise',invalid='raise'):
            residual = gamma[:,:,:,None]*(self.y[:,:,None,:]-np.exp(eta))
        bias = residual.sum(axis=(0,1))
        ar = np.einsum('ntku,ntul->kul',residual,self.history)
        grad = np.concatenate([initial[:-1],transition[:,:-1].ravel(),bias.ravel(),ar.ravel()])
        return float(increments.sum()),grad
