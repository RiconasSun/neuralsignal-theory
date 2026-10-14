"""Forward-mode dual primitives and a separately written Poisson recurrence.

No production model, parameter unpacker, reverse derivative or optimizer import.
"""
import math
import numpy as np

class Dual:
    __array_priority__=1000
    def __init__(self,v,d=None):self.v=np.asarray(v,dtype=np.float64);self.d=d
    @staticmethod
    def lift(x):return x if isinstance(x,Dual) else Dual(x)
    @staticmethod
    def expand(d,shape,p):
        if d is None:return 0.
        return np.broadcast_to(d.reshape((p,)+(1,)*(len(shape)-(d.ndim-1))+d.shape[1:]),(p,)+shape)
    def __add__(self,other):
        b=self.lift(other);v=self.v+b.v
        if self.d is None and b.d is None:return Dual(v)
        p=(self.d if self.d is not None else b.d).shape[0]
        return Dual(v,self.expand(self.d,v.shape,p)+self.expand(b.d,v.shape,p))
    __radd__=__add__
    def __neg__(self):return Dual(-self.v,None if self.d is None else -self.d)
    def __sub__(self,b):return self+-self.lift(b)
    def __rsub__(self,b):return self.lift(b)+-self
    def __mul__(self,other):
        b=self.lift(other);v=self.v*b.v
        if self.d is None and b.d is None:return Dual(v)
        p=(self.d if self.d is not None else b.d).shape[0]
        return Dual(v,self.expand(self.d,v.shape,p)*b.v+self.expand(b.d,v.shape,p)*self.v)
    __rmul__=__mul__
    def __matmul__(self,other):
        b=self.lift(other);v=self.v@b.v;d=None
        if self.d is not None:d=self.d@b.v
        if b.d is not None:
            term=np.einsum('nj,pjk->pnk',self.v,b.d)
            d=term if d is None else d+term
        return Dual(v,d)
    @property
    def T(self):return Dual(self.v.T,None if self.d is None else self.d.transpose(0,2,1))
    def tanh(self):
        v=np.tanh(self.v);return Dual(v,None if self.d is None else self.d*(1-v*v))
    def exp(self):
        v=np.exp(self.v);return Dual(v,None if self.d is None else self.d*v)
    def sum(self):return Dual(self.v.sum(),None if self.d is None else self.d.sum(axis=tuple(range(1,self.d.ndim))))

def layout(units,context,dimension):
    shapes=((dimension,dimension),(dimension,units),(dimension,context),(units,dimension))
    i=0;result=[]
    for name,shape in zip(('recurrent','past_count','context','readout'),shapes):
        end=i+math.prod(shape);result.append((name,i,end,shape));i=end
    return result

def constants(y):
    return np.array([math.lgamma(float(v)+1) for v in y.ravel()]).reshape(y.shape)

def value_gradient(theta,y,x,offset,dimension,ridge):
    n=len(theta);eye=np.eye(n);parts=[]
    for _,i,j,shape in layout(y.shape[-1],x.shape[-1],dimension):
        parts.append(Dual(theta[i:j].reshape(shape),eye[:,i:j].reshape((n,)+shape)))
    a,b,d,c=parts;h=Dual(np.zeros((len(y),dimension)));ll=Dual(0.);factorial=constants(y)
    for t in range(y.shape[1]):
        past=np.zeros((len(y),y.shape[-1])) if t==0 else np.log1p(y[:,t-1])
        h=(h@a.T+Dual(past)@b.T+Dual(x[:,t])@d.T).tanh()
        eta=h@c.T+offset[:,t]
        ll=ll+(eta*y[:,t]-eta.exp()-factorial[:,t]).sum()
    normalized=-ll*(1./(len(y)*y.shape[1]))
    parameters=Dual(theta,eye);penalty=(parameters*parameters).sum()*(ridge/2)
    total=normalized+penalty
    return float(total.v),total.d,dict(normalized_likelihood_gradient=normalized.d,ridge_gradient=penalty.d,normalized_likelihood=float(normalized.v),ridge_value=float(penalty.v))

def vector_losses(vectors,y,x,offset,dimension,ridge,factorial=None):
    """Batched independent forward evaluations; all inputs share one objective."""
    q=len(vectors);parts=[]
    for _,i,j,shape in layout(y.shape[-1],x.shape[-1],dimension):parts.append(vectors[:,i:j].reshape((q,)+shape))
    a,b,d,c=parts;h=np.zeros((q,len(y),dimension));ll=np.zeros(q)
    if factorial is None:factorial=constants(y)
    for t in range(y.shape[1]):
        past=np.zeros((len(y),y.shape[-1])) if t==0 else np.log1p(y[:,t-1])
        h=np.tanh(np.einsum('qij,qnj->qni',a,h)+np.einsum('qij,nj->qni',b,past)+np.einsum('qij,nj->qni',d,x[:,t]))
        eta=offset[None,:,t]+np.einsum('qij,qnj->qni',c,h)
        ll+=(y[None,:,t]*eta-np.exp(eta)-factorial[None,:,t]).sum(axis=(1,2))
    return -ll/(len(y)*y.shape[1])+ridge*(vectors*vectors).sum(axis=1)/2
