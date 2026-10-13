"""Verified archived exact/causal mathematics with the frozen P12 fit budget."""
import sys
import time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

if not Path(__file__).with_name('predictive_models.py').exists():
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'paper11_v2/scripts'))
from predictive_models import StatePoisson as SequentialState,poisson_logpmf,forward_backward
from r2_models import StatePoisson,RecurrentPoisson


def objective(theta,model,ridge):
    ll,gradient=model._likelihood_gradient(theta)
    denominator=model.y.shape[0]*model.y.shape[1]
    value=-ll/denominator+.5*ridge*np.dot(theta,theta)
    gradient=-gradient/denominator+ridge*theta
    if not np.isfinite(value) or not np.all(np.isfinite(gradient)):raise FloatingPointError('NONFINITE_OBJECTIVE')
    return float(value),gradient


def projected_gradient(theta,gradient):
    gradient=np.asarray(gradient).copy()
    gradient[(theta<=-8)&(gradient>0)]=0
    gradient[(theta>=8)&(gradient<0)]=0
    return float(np.max(np.abs(gradient)))


def fit(model,validation,ridge,seed):
    start=time.perf_counter();theta=model.initial(seed)
    result=minimize(objective,theta,args=(model,ridge),jac=True,method='L-BFGS-B',
        bounds=[(-8.,8.)]*model.n_parameters,
        options=dict(maxiter=500,maxfun=20000,ftol=1e-5,gtol=1e-5))
    loss,gradient=objective(result.x,model,ridge);pg=projected_gradient(result.x,gradient)
    training=model.score(result.x)/model.y.size;valid=validation.score(result.x)/validation.y.size
    return result.x,dict(converged=bool(result.success and pg<=.001 and np.isfinite(training) and np.isfinite(valid)),
        optimizer_success=bool(result.success),optimizer_message=str(result.message),
        iterations=int(result.nit),objective_calls=int(result.nfev),projected_gradient=pg,
        penalized_training_objective=loss,training_LL_nats_per_unit_bin=float(training),
        validation_LL_nats_per_unit_bin=float(valid),model_specific_parameters=model.n_parameters,
        training_unit_bins=int(model.y.size),validation_unit_bins=int(validation.y.size),
        bound_hits=int(np.sum(np.abs(result.x)>=8)),elapsed_seconds=time.perf_counter()-start,
        ridge_normalization='per_unit_exposure')


def make(family,y,context,offset,size):
    if family=='Discrete':return StatePoisson(y,offset,size,0)
    if family=='Hybrid':return StatePoisson(y,offset,size,5)
    if family=='Continuous':return RecurrentPoisson(y,context,offset,size)
    raise ValueError('UNREGISTERED_FAMILY')
