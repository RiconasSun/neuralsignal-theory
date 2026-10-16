"""Independent Autograd functional objectives; does not call analytical model code."""
import importlib.metadata
import numpy as np

def library():
    if importlib.metadata.version('autograd')!='1.8.0':raise RuntimeError('IndependentADversion mismatch')
    import autograd.numpy as anp
    from autograd import grad
    from autograd.scipy.special import logsumexp,gammaln
    return anp,grad,logsumexp,gammaln

def glm(theta,x,y,ridge,offset=None,penalize_intercept=False):
    anp,grad,_,gammaln=library();U,K=x.shape[-2:]
    def objective(w):
        b=anp.reshape(w,(U,K));eta=anp.sum(x*b[None,None,:,:],axis=-1)
        if offset is not None:eta=eta+offset
        nll=anp.mean(anp.exp(eta[:,5:])-y[:,5:]*eta[:,5:]+gammaln(y[:,5:]+1))
        penalized=b if penalize_intercept else b[:,1:]
        return nll+ridge/(2*U)*anp.sum(penalized*penalized)
    return float(objective(theta)),np.asarray(grad(objective)(theta))

def hmm(theta,y,offset,p,ridge):
    anp,grad,logsumexp,gammaln=library();E,T,U=y.shape
    logtransition=anp.log(anp.array([[p,1-p],[1-p,p]]))
    def objective(w):
        shifts=anp.reshape(w,(2,U));belief=anp.ones((E,2))*(-anp.log(2.));total=0.
        for t in range(T):
            logmean=offset[:,t,None,:]+shifts[None,:,:]
            emission=anp.sum(y[:,t,None,:]*logmean-anp.exp(logmean)-gammaln(y[:,t,None,:]+1),axis=2)
            joint=belief+emission;normal=logsumexp(joint,axis=1)
            if t>=5:total=total+anp.sum(normal)
            posterior=joint-normal[:,None]
            belief=logsumexp(posterior[:,:,None]+logtransition[None,:,:],axis=1)
        return -total/(E*(T-5)*U)+ridge/(2*U)*anp.sum(w*w)
    return float(objective(theta)),np.asarray(grad(objective)(theta))
