"""Synthetic specification oracles only; no real-data reader or optimizer."""
import hashlib,itertools
import numpy as np
from scipy.special import gammaln,logsumexp

def parameter_counts(u,k=2,r=1):
    b4=u*(38+4*u)
    return dict(B0=u,B1=38*u,B2=42*u,B3=u*(38+4*(u-1)),B4=b4,
        D=b4+(k-1)*u+k*(k-1)+k-1,C=b4+u*r,S=b4+k*u+k)

def poisson_log_mass(y,eta,exposure):
    y=np.asarray(y);eta=np.asarray(eta)
    assert (y>=0).all() and np.equal(y,np.floor(y)).all() and exposure>0
    return y*(np.log(exposure)+eta)-exposure*np.exp(eta)-gammaln(y+1)

def glm_objective_gradient(theta,x,y,exposure,ridge):
    """x includes leading intercept; sum over units divided by population bins T."""
    t,q=x.shape;u=y.shape[1];w=np.asarray(theta).reshape(q,u)
    eta=x@w;pen=w.copy();pen[0]=0
    j=-poisson_log_mass(y,eta,exposure).sum()/t+ridge/2*np.sum(pen**2)
    g=x.T@(exposure*np.exp(eta)-y)/t+ridge*pen
    return float(j),g.ravel()

def projected_gradient(theta,g,lower,upper):
    theta=np.asarray(theta);g=np.asarray(g).copy()
    assert (theta>=lower).all() and (theta<=upper).all()
    g[((theta==lower)&(g>0))|((theta==upper)&(g<0))]=0
    return g

def partition_trials(n,final=False):
    cuts=[0,int(.6*n),n] if final else [0,int(.6*n),int(.8*n),n]
    names=['C','D'] if final else ['A','B','E']
    guard={i for c in cuts[1:-1] for i in (c-1,c) if 0<=i<n}
    return {name:[i for i in range(a,b) if i not in guard] for name,a,b in zip(names,cuts[:-1],cuts[1:])}

def causal_lags(y,lags=4,resets=None,valid=None):
    y=np.asarray(y);n,u=y.shape;resets=np.zeros(n,bool) if resets is None else np.asarray(resets,bool)
    valid=np.ones(n,bool) if valid is None else np.asarray(valid,bool)
    out=np.full((n,lags,u),np.nan);start=0
    for t in range(n):
        if resets[t] or (t and not valid[t-1]):start=t
        if not valid[t]:continue
        out[t]=0
        for j in range(1,lags+1):
            if t-j>=start:out[t,j-1]=y[t-j]
    return out

def past_lookup(times,values,b):
    times=np.asarray(times);i=np.searchsorted(times,b,side='left')-1
    if i<0:raise ValueError('No strictly past observation')
    return values[i]

def dct_projection(u,r):
    out=np.cos(np.pi*(np.arange(u)[:,None]+.5)*np.arange(r)[None,:]/u)*np.sqrt(2/u)
    out[:,0]=1/np.sqrt(u);return out

def fixed_state(y,r=2,tau=.1,reset=None):
    lag=causal_lags(y,10,resets=reset);weights=np.exp(-np.arange(10)*.05/tau);weights/=weights.sum()
    return np.einsum('tju,j,ur->tr',lag,weights,dct_projection(y.shape[1],r))

def hmm_forward(log_emissions,pi,transition,warmup=0):
    e=np.asarray(log_emissions);a=np.asarray(pi,float);ll=0.
    for t,row in enumerate(e):
        joint=np.log(a)+row;z=logsumexp(joint)
        if t>=warmup:ll+=z
        a=np.exp(joint-z)@transition
    return float(ll)

def hmm_enumeration(log_emissions,pi,transition,warmup=0):
    e=np.asarray(log_emissions);n,k=e.shape
    def marginal(length):
        if not length:return 0.
        terms=[]
        for path in itertools.product(range(k),repeat=length):
            value=np.log(pi[path[0]])+sum(e[t,path[t]] for t in range(length))
            value+=sum(np.log(transition[path[t-1],path[t]]) for t in range(1,length))
            terms.append(value)
        return logsumexp(terms)
    return float(marginal(n)-marginal(warmup))

def iid_mixture(log_emissions,pi,warmup=0):
    return float(logsumexp(np.asarray(log_emissions)[warmup:]+np.log(pi),axis=1).sum())

def sign_flip_p(effects,two_sided=False):
    d=np.asarray(effects,float);assert len(d)>0 and np.isfinite(d).all()
    obs=abs(d.mean()) if two_sided else d.mean();count=0
    for s in itertools.product([-1,1],repeat=len(d)):
        z=np.mean(d*s);z=abs(z) if two_sided else z
        count+=z>=obs-1e-14
    return count/(2**len(d))

def holm(p):
    p=np.asarray(p,float);idx=np.argsort(p,kind='stable');ordered=np.maximum.accumulate(p[idx]*(len(p)-np.arange(len(p))))
    out=np.empty_like(p);out[idx]=np.minimum(1,ordered);return out

def control_seed(suite,subject,partition,replicate):
    s=f'P15-M1|150107|{suite}|{subject}|{partition}|{replicate}'
    return int.from_bytes(hashlib.sha256(s.encode('utf8')).digest()[:8],'big')

def rotate_counts(y,rng):
    y=np.asarray(y);assert len(y)>=2
    return np.roll(y,int(rng.integers(1,len(y))),axis=0)

def thinning_seed(subject,unit_uuid,role):
    assert role in ['A','B','E','C','D']
    value=f'P15-M1|150108|S07|{subject}|{unit_uuid}|{role}'
    return int.from_bytes(hashlib.sha256(value.encode('utf8')).digest()[:8],'big')

def wheel_stratum(times,values,epoch_start,training_median):
    magnitude=abs(past_lookup(times,values,epoch_start)-past_lookup(times,values,epoch_start-.5))
    return int(magnitude>training_median)
