"""Production frozen Poisson B0-B4/C, conditional HMM D and IID mixture S."""
import numpy as np
from scipy.special import gammaln, logsumexp


def pg(theta,gradient,bounds):
    b=np.asarray(bounds);g=np.asarray(gradient).copy()
    g[((theta==b[:,0])&(g>0))|((theta==b[:,1])&(g<0))]=0
    return float(np.max(np.abs(g),initial=0.))


def log_softmax_reference(x):
    a=np.concatenate((x,np.zeros((*x.shape[:-1],1))),axis=-1)
    return a-logsumexp(a,axis=-1,keepdims=True)


def prefix_posteriors(emissions,logpi,logP):
    n,l,k=emissions.shape
    alpha=np.empty_like(emissions);normalizers=np.empty((n,l))
    pre=np.broadcast_to(logpi,(n,k)).copy()
    for t in range(l):
        joint=pre+emissions[:,t];z=logsumexp(joint,axis=1)
        alpha[:,t]=joint-z[:,None];normalizers[:,t]=z
        pre=logsumexp(alpha[:,t,:,None]+logP[None,:,:],axis=1)
    beta=np.zeros((n,k));gamma=np.empty_like(emissions);trans=np.zeros((k,k))
    for t in range(l-1,-1,-1):
        gamma[:,t]=np.exp(alpha[:,t]+beta)
        if t:
            xi=np.exp(alpha[:,t-1,:,None]+logP[None,:,:]+emissions[:,t,None,:]+beta[:,None,:]-normalizers[:,t,None,None])
            trans+=xi.sum(axis=0)
            beta=logsumexp(logP[None,:,:]+emissions[:,t,None,:]+beta[:,None,:],axis=2)-normalizers[:,t,None]
    return float(normalizers.sum()),gamma,trans,gamma[:,0].sum(axis=0),normalizers


class Model:
    def __init__(self,x,y,family,ridge=.1,k=2,warm=10,delta=.05,active=None,nuisance=37):
        self.x=np.asarray(x,np.float64);self.y=np.asarray(y,np.float64)
        assert self.x.ndim==self.y.ndim==3 and self.x.shape[:2]==self.y.shape[:2]
        assert np.isfinite(self.x).all() and np.isfinite(self.y).all()
        assert (self.y>=0).all() and np.equal(self.y,np.floor(self.y)).all()
        self.family=family;self.ridge=float(ridge);self.k=k;self.warm=warm;self.delta=delta
        n,l,p=self.x.shape;u=self.y.shape[-1];self.u=u;self.p=p;self.T=n*(l-warm)
        assert self.T>0 and delta>0 and 0<=warm<l
        mask=np.ones((p,u),bool);hstart=1+nuisance
        if family=='B0':mask[1:]=False
        elif family=='B1':mask[hstart:]=False
        elif family in ('B2','B3'):
            mask[hstart:]=False
            for v in range(u):
                for unit in range(u):
                    if (v==unit)==(family=='B2'):mask[hstart+4*v:hstart+4*(v+1),unit]=True
        elif family not in ('B4','C','D','S'):raise ValueError(family)
        if active is not None:
            mask&=np.asarray(active,bool)[:,None]
        mask[0]=True;self.mask=mask;self.nlin=int(mask.sum())
        self.penalty=np.ones(self.nlin+(k-1)*u+(k*(k-1) if family=='D' else 0)+(k-1) if family in ('D','S') else self.nlin)
        self.penalty[:self.nlin]=np.broadcast_to((np.arange(p)>0)[:,None],(p,u))[mask]
        self.bounds=[(-8.,8.) if j<u else (-1.,1.) for j in np.flatnonzero(mask.ravel())]
        if family in ('D','S'):
            self.bounds += [(-2.,2.)]*((k-1)*u)
            if family=='D':self.bounds += [(-4.,4.)]*(k*(k-1))
            self.bounds += [(-4.,4.)]*(k-1)
        self.size=len(self.bounds);assert self.size==len(self.penalty)
        self.factorial=gammaln(self.y+1)

    def unpack(self,theta):
        theta=np.asarray(theta,np.float64);assert theta.shape==(self.size,)
        w=np.zeros((self.p,self.u));w[self.mask]=theta[:self.nlin]
        if self.family not in ('D','S'):return w,None,None,None
        at=self.nlin;offset=np.vstack((np.zeros((1,self.u)),theta[at:at+(self.k-1)*self.u].reshape(self.k-1,self.u)));at+=(self.k-1)*self.u
        logP=None
        if self.family=='D':
            logP=log_softmax_reference(theta[at:at+self.k*(self.k-1)].reshape(self.k,self.k-1));at+=self.k*(self.k-1)
        logpi=log_softmax_reference(theta[at:])
        return w,offset,logP,logpi

    def initialize(self,seed=11):
        w=np.zeros((self.p,self.u))
        counts=self.y[:,self.warm:].sum(axis=(0,1))
        w[0]=np.clip(np.log((counts+.5)/(self.T*self.delta)),-8,8)
        theta=list(w[self.mask])
        if self.family in ('D','S'):
            rng=np.random.Generator(np.random.PCG64(seed));theta.extend(rng.uniform(-.05,.05,(self.k-1)*self.u))
            if self.family=='D':
                logits=np.array([[2.*(i==j)-2.*(i==self.k-1) for j in range(self.k-1)] for i in range(self.k)])
                theta.extend(logits.ravel())
            theta.extend(np.zeros(self.k-1))
        return np.asarray(theta,float)

    def objective(self,theta):
        w,offset,logP,logpi=self.unpack(theta);eta=self.x@w
        if self.family not in ('D','S'):
            mu=self.delta*np.exp(eta);ll=self.y*(np.log(self.delta)+eta)-mu-self.factorial
            residual=(mu-self.y).copy();residual[:,:self.warm]=0
            grad=(np.einsum('nlp,nlu->pu',self.x,residual)/self.T)[self.mask]
            loss=-float(ll[:,self.warm:].sum())/self.T
        else:
            state_eta=eta[:,:,None,:]+offset[None,None,:,:]
            mu=self.delta*np.exp(state_eta)
            emission=(self.y[:,:,None,:]*(np.log(self.delta)+state_eta)-mu-self.factorial[:,:,None,:]).sum(axis=-1)
            if self.family=='S':
                joint=emission+logpi[None,None,:];z=logsumexp(joint,axis=-1)
                weights=np.exp(joint-z[:,:,None]);weights[:,:self.warm]=0
                ll=float(z[:,self.warm:].sum())
                pi_grad=weights.sum(axis=(0,1))-self.T*np.exp(logpi)
                transition_grad=[]
            else:
                ll,weights,trans,initial,_=prefix_posteriors(emission,logpi,logP)
                if self.warm:
                    warmll,warmweights,warmtrans,warminit,_=prefix_posteriors(emission[:,:self.warm],logpi,logP)
                    ll-=warmll;weights[:,:self.warm]-=warmweights;trans-=warmtrans;initial-=warminit
                pi_grad=initial-initial.sum()*np.exp(logpi)
                transition_grad=(trans-trans.sum(axis=1,keepdims=True)*np.exp(logP))[:,:-1].ravel()
            deta=weights[:,:,:,None]*(self.y[:,:,None,:]-mu)
            linear=np.einsum('nlp,nlu->pu',self.x,deta.sum(axis=2))
            offsets=deta.sum(axis=(0,1))[1:].ravel()
            grad=-np.concatenate((linear[self.mask],offsets,np.asarray(transition_grad),pi_grad[:-1]))/self.T
            loss=-ll/self.T
        loss+=self.ridge/2*float(np.sum(self.penalty*theta**2))
        grad+=self.ridge*self.penalty*theta
        assert np.isfinite(loss) and np.isfinite(grad).all(), 'Nonfinite frozen mathematical objective'
        return loss,grad

    def prebin_logmasses(self,theta,filter_y=None):
        w,offset,logP,logpi=self.unpack(theta);eta=self.x@w
        if self.family not in ('D','S'):
            return (self.y*(np.log(self.delta)+eta)-self.delta*np.exp(eta)-self.factorial).sum(axis=-1)
        eta=eta[:,:,None,:]+offset[None,None,:,:];mu=self.delta*np.exp(eta)
        e=(self.y[:,:,None,:]*(np.log(self.delta)+eta)-mu-self.factorial[:,:,None,:]).sum(axis=-1)
        if self.family=='S':return logsumexp(e+logpi[None,None,:],axis=-1)
        fy=self.y if filter_y is None else np.asarray(filter_y)
        fe=e if filter_y is None else (fy[:,:,None,:]*(np.log(self.delta)+eta)-mu-gammaln(fy[:,:,None,:]+1)).sum(axis=-1)
        out=np.empty(self.y.shape[:2]);pre=np.broadcast_to(logpi,(len(self.y),self.k)).copy()
        for t in range(self.y.shape[1]):
            out[:,t]=logsumexp(pre+e[:,t],axis=1)
            joint=pre+fe[:,t];post=joint-logsumexp(joint,axis=1,keepdims=True)
            pre=logsumexp(post[:,:,None]+logP[None,:,:],axis=1)
        return out

    def value(self,theta):
        """The identical objective without reverse/posterior gradient computation."""
        if self.family not in ('D','S'):
            w=self.unpack(theta)[0];eta=self.x@w
            ll=(self.y*(np.log(self.delta)+eta)-self.delta*np.exp(eta)-self.factorial)[:,self.warm:].sum()
        else:
            masses=self.prebin_logmasses(theta)
            ll=masses.sum()-masses[:,:self.warm].sum() if self.family=='D' else masses[:,self.warm:].sum()
        return -float(ll)/self.T+self.ridge/2*float(np.sum(self.penalty*theta**2))
