"""Independent unit-local scalar oracles and bounded optimizer instrumentation."""
import math
import time
import numpy as np
from scipy.optimize import minimize
from baseline_fit import objective, projected_gradient

ORIGINAL = dict(ftol=1e-5, gtol=1e-5, maxiter=500, maxfun=20000)
REPAIRED = dict(ftol=1e-10, gtol=1e-5, maxiter=2000, maxfun=80000)


def scalar_unit(theta, y, x, ridge):
    # Separate contraction and scalar factorial oracle, no archived gradient call.
    eta = x.reshape(-1, x.shape[-1]) @ theta
    yy = y.ravel()
    constant = np.fromiter((math.lgamma(float(v)+1) for v in yy), float, yy.size)
    return float(np.sum(np.exp(eta)-yy*eta+constant)/yy.size + ridge*np.dot(theta[1:], theta[1:])/2)


def gradient_check(theta, y, x, ridge, coordinates):
    _, analytical = objective(theta, y, x, ridge, 'per_unit_exposure')
    f = x.shape[-1]; matrix = theta.reshape(y.shape[-1], f)
    errors = []
    for step in (1e-5, 1e-6):
        worst = 0.
        for coordinate in coordinates:
            unit, feature = divmod(int(coordinate), f)
            plus = matrix[unit].copy(); minus = plus.copy()
            plus[feature] += step; minus[feature] -= step
            fd = (scalar_unit(plus, y[..., unit], x[..., unit, :], ridge)-
                  scalar_unit(minus, y[..., unit], x[..., unit, :], ridge))/(2*step)
            worst = max(worst, abs(fd-analytical[coordinate])/max(1., abs(analytical[coordinate])))
        errors.append(worst)
    independent = sum(scalar_unit(matrix[u], y[..., u], x[..., u, :], ridge) for u in range(y.shape[-1]))
    loss = objective(theta, y, x, ridge, 'per_unit_exposure')[0]
    return dict(max_relative_errors=errors, coordinate_count=len(coordinates),
                scalar_objective_error=abs(independent-loss),
                passed=max(errors) <= 1e-5 and abs(independent-loss) <= 1e-8*max(1., abs(loss)))


def run_fit(y, x, ridge, seed, options, verify_gradient=True):
    started = time.perf_counter(); size = y.shape[-1]*x.shape[-1]
    initial = np.random.default_rng(seed).normal(0., .05, size)
    coordinates = sorted(set(range(0, size, x.shape[-1])) | set(
        np.random.default_rng(20261012).choice(size, min(16,size), replace=False).tolist()))
    initial_check = gradient_check(initial, y, x, ridge, coordinates) if verify_gradient else None
    calls = []; iterations = []
    def loss(theta):
        value, gradient = objective(theta, y, x, ridge, 'per_unit_exposure')
        calls.append(dict(loss=value, gradient_inf=float(np.max(np.abs(gradient))),
                          projected_gradient=projected_gradient(theta, gradient),
                          bound_hits=int(np.sum(np.abs(theta)>=8))))
        return value, gradient
    def callback(theta):
        value, gradient = objective(theta,y,x,ridge,'per_unit_exposure')
        iterations.append(dict(loss=value, projected_gradient=projected_gradient(theta,gradient),
                               bound_hits=int(np.sum(np.abs(theta)>=8))))
    result = minimize(loss, initial, jac=True, method='L-BFGS-B', bounds=[(-8.,8.)]*size,
                      callback=callback, options=options)
    value, gradient = objective(result.x,y,x,ridge,'per_unit_exposure')
    terminal_check = gradient_check(result.x,y,x,ridge,coordinates) if verify_gradient else None
    conditioning = []
    matrix = result.x.reshape(y.shape[-1],x.shape[-1])
    for u in range(min(4,y.shape[-1])):
        xx = x[...,u,:].reshape(-1,x.shape[-1]); eta = xx @ matrix[u]
        hessian = xx.T @ (np.exp(eta)[:,None]*xx)/xx.shape[0]
        hessian += np.diag([0.]+[ridge]*(x.shape[-1]-1))
        eigen = np.linalg.eigvalsh(hessian)
        conditioning.append(dict(unit_index=u, minimum_eigenvalue=float(eigen[0]),
            maximum_eigenvalue=float(eigen[-1]), condition_number=float(eigen[-1]/eigen[0])))
    from baseline_features import likelihood_gradient
    pg = projected_gradient(result.x,gradient)
    record = dict(seed=seed,ridge=ridge,optimizer_policy=options,
        optimizer_success=bool(result.success), optimizer_message=str(result.message),
        iterations=int(result.nit),objective_calls=int(result.nfev),
        penalized_training_objective=value,projected_gradient=pg,
        gradient_inf=float(np.max(np.abs(gradient))),bound_hits=int(np.sum(np.abs(result.x)>=8)),
        converged=bool(result.success and pg<=.001),training_LL_nats_per_unit_bin=likelihood_gradient(result.x,y,x)[0]/y.size,
        parameter_count=size,training_unit_bins=int(y.size),initial_gradient_check=initial_check,
        terminal_gradient_check=terminal_check,conditioning=conditioning,
        objective_history=calls,accepted_iteration_history=iterations,
        elapsed_seconds=time.perf_counter()-started)
    return result.x, record
