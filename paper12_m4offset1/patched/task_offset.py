"""All three seeds/ridge .1, training only; one shared mean log-rate predictor."""
import time
import numpy as np
from scipy.optimize import minimize
from baseline_features import design,training_scaler,transform,likelihood_gradient
from baseline_fit import objective,projected_gradient


def fit_offset(y,validation,conditions,validation_conditions,orders,validation_orders):
    train=np.concatenate((design(y,conditions,orders,'event'),design(y,conditions,orders,'drift')[...,1:]),axis=-1)
    valid=np.concatenate((design(validation,validation_conditions,validation_orders,'event'),design(validation,validation_conditions,validation_orders,'drift')[...,1:]),axis=-1)
    scaler=training_scaler(train);train=transform(train,scaler);valid=transform(valid,scaler)
    if train.shape[-1]!=29:raise RuntimeError('OFFSET_FEATURE_DEFINITION_CHANGED')
    weights=[];diagnostics=[]
    for seed in (11,23,37):
        start=time.perf_counter();theta=np.random.default_rng(seed).normal(0,.05,y.shape[-1]*29)
        result=minimize(objective,theta,args=(y,train,.1,'per_unit_exposure'),jac=True,method='L-BFGS-B',
            bounds=[(-8.,8.)]*len(theta),options=dict(maxiter=2000,maxfun=80000,ftol=1e-10,gtol=1e-5))
        loss,gradient=objective(result.x,y,train,.1,'per_unit_exposure');pg=projected_gradient(result.x,gradient)
        passed=bool(result.success and pg<=.001 and np.isfinite(loss))
        diagnostics.append(dict(seed=seed,ridge=.1,converged=passed,projected_gradient=pg,
            optimizer_success=bool(result.success),optimizer_message=str(result.message),
            objective_calls=int(result.nfev),iterations=int(result.nit),elapsed_seconds=time.perf_counter()-start,
            validation_used_for_selection=False))
        weights.append(result.x.reshape(y.shape[-1],29))
    average=np.mean(weights,axis=0)
    training_offset=np.einsum('ntuf,uf->ntu',train,average)
    validation_offset=np.einsum('ntuf,uf->ntu',valid,average)
    # Context is known stimulus/time/order, with no duplicated output intercept.
    context=train[:,:,0,1:];valid_context=valid[:,:,0,1:]
    return training_offset,validation_offset,context,valid_context,diagnostics
