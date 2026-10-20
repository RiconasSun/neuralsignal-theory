"""Production packing around unchanged, independently differentiated M1 equations."""
import numpy as np
from scipy.special import gammaln,expit,logsumexp
from .core import spec,dynamics,ImplementationStop

class Objective:
    def __init__(self,batch,scaling,model,lam,unit=None,seed=None):
        if batch.role!='A':raise ImplementationStop('Fitting objective must be A-only')
        self.batch,self.scaling,self.model,self.lam,self.unit=batch,scaling,model,float(lam),unit
        columns=batch.columns(model);self.columns=columns
        self.X=scaling.transform(batch)[...,columns];self.psth=batch.psth;self.y=batch.y
        if model in ['D','S']:
            u,f=self.X.shape[-2:];active=scaling.active[:,columns]
            self.free=np.r_[np.flatnonzero(active.ravel()),u*f+np.arange(u+3)].astype(int)
            self.full_size=u*f+u+3
            lo,hi=dynamics.constraints(u,f,self.psth)
            self.lo,self.hi=lo[self.free],hi[self.free]
            self.x0=dynamics.initial(self.y,batch.dt,f,seed,model,self.psth)[self.free]
        else:
            if unit is None:raise ImplementationStop('Unit GLM identity required')
            self.free=np.flatnonzero(scaling.active[unit,columns]);self.full_size=len(columns)
            self.X=self.X[:,:,unit,self.free].reshape(-1,len(self.free));self.y=batch.y[:,:,unit].ravel()
            self.lo=np.r_[np.full(self.psth,-10.),np.full(len(self.free)-self.psth,-1.)];self.hi=-self.lo
            self.x0=np.r_[np.full(self.psth,spec.scored_log_rate(self.y,np.full(len(self.y),batch.dt))),np.zeros(len(self.free)-self.psth)]
    def expand(self,x):
        out=np.zeros(self.full_size);out[self.free]=x;return out
    def analytic(self,x):
        if self.model in ['D','S']:
            value,g=dynamics.objective(self.expand(x),self.X,self.y,self.batch.dt,self.lam,self.model,self.batch.gates,self.psth)
            return value,g[self.free]
        return spec.glm(x,self.X,self.y,np.full(len(self.y),self.batch.dt),self.lam,self.psth)
    def AD(self,x):
        if self.model in ['D','S']:
            value,g=dynamics.independent_AD(self.expand(x),self.X,self.y,self.batch.dt,self.lam,self.model,self.batch.gates,self.psth)
            return value,g[self.free]
        return spec.independent_AD(x,self.X,self.y,np.full(len(self.y),self.batch.dt),self.lam,self.psth)
    def score(self,x,batch):
        X=self.scaling.transform(batch)[...,self.columns]
        if self.model in ['D','S']:
            return causal_score(self.expand(x),X,batch.y,batch.dt,self.model,batch.gates)[0]
        eta=np.einsum('jtf,f->jt',X[:,:,self.unit,self.free],x);y=batch.y[:,:,self.unit]
        return y*(np.log(batch.dt)+eta)-batch.dt*np.exp(eta)-gammaln(y+1)

def stationary(batch):
    if batch.role!='A':raise ImplementationStop('B0 must be A-fitted')
    return np.array([spec.scored_log_rate(batch.y[:,:,u],np.full(batch.y.shape[:2],batch.dt)) for u in range(len(batch.unit_ids))])

def stationary_score(theta,batch):
    eta=np.asarray(theta)[None,None,:]
    return np.sum(batch.y*(np.log(batch.dt)+eta)-batch.dt*np.exp(eta)-gammaln(batch.y+1),axis=2)

def causal_score(theta,X,y,dt,mode,gates):
    """Prediction uses forward states only; no evaluation gradient or smoothing."""
    j,t,u,f=X.shape;beta,delta,gamma=dynamics.unpack(theta,u,f)
    eta=np.einsum('jtuf,uf->jtu',X,beta)[...,None]+delta[None,None,:,None]*np.arange(2)
    mu=dt*np.exp(eta)
    if mode=='D':
        p=expit(gamma[:2]);transition=np.log(np.c_[1-p,p]);initial=expit(gamma[2])
        prior=np.tile(np.log([1-initial,initial]),(j,1))
    elif mode=='S':
        p=expit(gates@gamma);prior=np.log(np.c_[1-p,p])
    else:raise ImplementationStop('Unregistered latent scorer')
    scores=[];priors=[];means=[]
    for k in range(t):
        priors.append(np.exp(prior));means.append(np.einsum('jz,juz->ju',np.exp(prior),mu[:,k]))
        emission=np.sum(y[:,k,:,None]*(np.log(dt)+eta[:,k])-mu[:,k]-gammaln(y[:,k,:,None]+1),axis=1)
        ll=logsumexp(prior+emission,axis=1);scores.append(ll)
        posterior=prior+emission-ll[:,None]
        prior=logsumexp(posterior[:,:,None]+transition[None,:,:],axis=1) if mode=='D' else posterior
    return np.asarray(scores).T,np.asarray(priors).transpose(1,0,2),np.asarray(means).transpose(1,0,2)

class StationaryObjective:
    def __init__(self,batch,unit):
        self.y=batch.y[:,:,unit].ravel();self.dt=batch.dt;self.X=np.ones((len(self.y),1))
        self.x0=np.array([spec.scored_log_rate(self.y,np.full(len(self.y),self.dt))]);self.lo=np.array([-10.]);self.hi=-self.lo
    def analytic(self,x):return spec.glm(x,self.X,self.y,np.full(len(self.y),self.dt),0.,1)
    def AD(self,x):return spec.independent_AD(x,self.X,self.y,np.full(len(self.y),self.dt),0.,1)
