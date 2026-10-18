"""Independent raw-equation AD; never calls the production likelihood/gradient."""
import autograd.numpy as a
from autograd import value_and_grad
from autograd.scipy.special import logsumexp
import numpy as np
from scipy.special import gammaln


def ad_function(model):
    x=a.array(model.x);y=a.array(model.y);constant=a.array(gammaln(model.y+1))
    mapping=np.full(model.mask.shape,model.nlin,int)
    mapping[model.mask]=np.arange(model.nlin)
    penalty=a.array(model.penalty);n=model.y.shape[0];l=model.y.shape[1];u=model.u;k=model.k
    def log_probs(free):
        logits=a.concatenate([free,a.zeros(free.shape[:-1]+(1,))],axis=-1)
        return logits-logsumexp(logits,axis=-1,keepdims=True)
    def objective(theta):
        coefficients=a.concatenate([theta[:model.nlin],a.zeros(1)])[mapping]
        rate=x@coefficients
        if model.family not in ('D','S'):
            ll=(y*(a.log(model.delta)+rate)-model.delta*a.exp(rate)-constant)[:,model.warm:]
            neg=-a.sum(ll)/model.T
        else:
            off=theta[model.nlin:model.nlin+(k-1)*u].reshape((k-1,u))
            off=a.concatenate([a.zeros((1,u)),off],axis=0)
            at=model.nlin+(k-1)*u
            if model.family=='D':
                logP=log_probs(theta[at:at+k*(k-1)].reshape((k,k-1)));at+=k*(k-1)
            logpi=log_probs(theta[at:])
            linear=rate[:,:,None,:]+off[None,None,:,:]
            emissions=a.sum(y[:,:,None,:]*(a.log(model.delta)+linear)-model.delta*a.exp(linear)-constant[:,:,None,:],axis=-1)
            if model.family=='S':
                neg=-a.sum(logsumexp(emissions[:,model.warm:]+logpi[None,None,:],axis=-1))/model.T
            else:
                # Unnormalized log forward marginals; differentiate full minus warm prefix.
                alpha=logpi[None,:]+emissions[:,0,:]
                warm_marginal=logsumexp(alpha,axis=-1) if model.warm==1 else a.zeros(n)
                for t in range(1,l):
                    alpha=emissions[:,t,:]+logsumexp(alpha[:,:,None]+logP[None,:,:],axis=1)
                    if t+1==model.warm:warm_marginal=logsumexp(alpha,axis=-1)
                neg=-a.sum(logsumexp(alpha,axis=-1)-warm_marginal)/model.T
        return neg+model.ridge/2*a.sum(penalty*theta**2)
    return value_and_grad(objective)


def coordinate_check(model,theta,synthetic=False):
    j,g=model.objective(theta);jad,gad=ad_function(model)(theta)
    scale=np.maximum(1.,np.maximum(np.abs(g),np.abs(gad)))
    ad_scaled=np.abs(g-gad)/scale
    errors=[]
    for step in (1e-4,1e-5,1e-6):
        fd=np.empty_like(theta)
        for i in range(len(theta)):
            plus=theta.copy();minus=theta.copy();plus[i]+=step;minus[i]-=step
            fd[i]=(model.value(plus)-model.value(minus))/(2*step)
        absolute=np.abs(fd-g);scaled=absolute/np.maximum(1.,np.maximum(np.abs(fd),np.abs(g)))
        errors.append(dict(step=step,max_absolute=float(absolute.max(initial=0)),max_scaled=float(scaled.max(initial=0)),
            coordinate_absolute=absolute.tolist(),coordinate_scaled=scaled.tolist(),numerical_gradient=fd.tolist()))
    return dict(objective=float(j),AD_objective=float(jad),objective_difference=float(abs(j-jad)),
        analytic_gradient=g.tolist(),AD_gradient=np.asarray(gad).tolist(),
        AD_coordinate_absolute=np.abs(g-gad).tolist(),AD_coordinate_scaled=ad_scaled.tolist(),
        AD_max_scaled=float(ad_scaled.max(initial=0)),FD=errors,
        PASS=abs(j-jad)<=1e-8*max(1,abs(j)) and ad_scaled.max(initial=0)<=(1e-8 if synthetic else 1e-5)
            and all(x['max_scaled']<=1e-5 for x in errors))
