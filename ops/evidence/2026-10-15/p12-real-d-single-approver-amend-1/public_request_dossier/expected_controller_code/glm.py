"""Registered nested causal Poisson representations; no optimizer selection."""
import math
import numpy as np
from scipy.special import gammaln
MODELS={'O':[0,27,28],'N':list(range(29)),'NH':list(range(34)),'NP':list(range(29))+list(range(34,39)),'F':list(range(39)),'OHP':[0,27,28]+list(range(29,39))}
CONTRASTS={'own':('F','NP'),'population':('F','NH'),'stimulus_time':('F','OHP'),'combined':('F','O'),'joint_history':('F','N')}
def raw(y,c,o):
    y=np.asarray(y,dtype=float);n,t,u=y.shape
    if t!=20 or u<2 or not np.isfinite(y).all() or np.any(y<0) or np.any(y!=np.floor(y)):raise ValueError('COUNTS')
    c=np.asarray(c);o=np.asarray(o)
    if c.shape!=(n,) or o.shape!=(n,) or np.any((c<0)|(c>7)) or np.any((o<0)|(o>599)):raise ValueError('CONTEXT')
    h=np.zeros((n,t,u,5))
    for lag in range(1,6):h[:,lag:,:,lag-1]=np.log1p(y[:,:-lag,:])
    p=(h.sum(axis=2,keepdims=True)-h)/(u-1)
    x=np.ones((n,t,u,39));x[...,1:8]=(c[:,None,None,None]==np.arange(1,8)).astype(float)
    x[...,8:27]=(np.arange(20)[None,:,None,None]==np.arange(1,20)).astype(float)
    x[...,27]=(o/599)[:,None,None];x[...,28]=(o/599)[:,None,None]**2
    x[...,29:34]=h;x[...,34:39]=p;return x
def scale(x):
    m=x.mean(axis=(0,1));s=x.std(axis=(0,1));m[:,0]=0;s[:,0]=1;s[s==0]=1;return m,s
def transform(x,ms):return (x-ms[0][None,None,:,:])/ms[1][None,None,:,:]
def obj(theta,x,y,hessian=False):
    eta=x@theta;mu=np.exp(eta);n=y.size
    f=float(np.sum(mu-y*eta+gammaln(y+1))/n+.05*np.dot(theta[1:],theta[1:]))
    g=x.T@(mu-y)/n;g[1:]+=.1*theta[1:]
    if hessian:
        H=(x.T*mu)@x/n;H.flat[::H.shape[0]+1]+=.1;H[0,0]-=.1;return f,g,H
    return f,g
def pg(theta,g):return float(np.max(np.abs(theta-np.clip(theta-g,-8,8))))
def independent_ad(theta,x,y):
    # Forward-mode derivatives of independent sum/exp primitives, including ridge.
    value=(x*theta[None,:]).sum(axis=1);dvalue=x
    ev=np.exp(value);dev=ev[:,None]*dvalue
    f=float(np.sum(ev-y*value+np.array([math.lgamma(float(v)+1) for v in y]))/len(y)+np.sum(.05*theta[1:]**2))
    derivative=(dev-y[:,None]*dvalue).sum(axis=0)/len(y)
    derivative[1:]+=.1*theta[1:];return f,derivative
def fit(x,y):
    theta=np.zeros(x.shape[1]);theta[0]=np.clip(np.log(max(float(y.mean()),1e-300)),-8,8);history=[];calls=0;success=False
    for iteration in range(101):
        f,g,H=obj(theta,x,y,True);calls+=1;p=pg(theta,g);history.append({'iteration':iteration,'objective':f,'PG':p,'calls':calls})
        if not np.isfinite(f) or not np.isfinite(g).all():raise RuntimeError('NONFINITE_FIT')
        if p<=1e-7:success=True;break
        if iteration==100:break
        free=~(((theta<=-8)&(g>0))|((theta>=8)&(g<0)))
        d=np.zeros_like(theta);d[free]=np.linalg.solve(H[np.ix_(free,free)],-g[free])
        if np.dot(g,d)>=0:d=np.clip(theta-g,-8,8)-theta
        accepted=False
        for step in range(40):
            candidate=np.clip(theta+(2.**-step)*d,-8,8)
            if calls>=4000:raise RuntimeError('REGISTERED_CALL_CAP')
            cf,_=obj(candidate,x,y);calls+=1
            if np.isfinite(cf) and cf<=f+1e-4*np.dot(g,candidate-theta):theta=candidate;accepted=True;break
        if not accepted:break
    f,g=obj(theta,x,y);af,ag=independent_ad(theta,x,y)
    error=float(np.max(np.abs(g-ag)/np.maximum(1,np.maximum(np.abs(g),np.abs(ag)))))
    record={'optimizer_success':success,'iterations':iteration,'objective_calls':calls,'objective':f,'PG':pg(theta,g),'AD_PG':pg(theta,ag),'AD_scaled_error':error,'AD_objective_error':abs(f-af),'finite':bool(np.isfinite(theta).all() and np.isfinite([f,af]).all()),'bounds':bool(np.all(np.abs(theta)<=8)),'history':history}
    record['passed']=bool(success and record['PG']<=.001 and record['AD_PG']<=.001 and error<=1e-5 and record['AD_objective_error']<=1e-10 and record['finite'] and record['bounds'])
    return theta,record
def score(y,x,w):
    eta=np.einsum('ntuf,uf->ntu',x,w)
    value=float(np.sum(y*eta-np.exp(eta)-gammaln(y+1))/y.size)
    if not np.isfinite(value):raise RuntimeError('NONFINITE_SCORE')
    return value
def gains(scores):return {name:scores[a]-scores[b] for name,(a,b) in CONTRASTS.items()}
