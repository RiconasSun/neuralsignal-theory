"""Independent scalar likelihoods: no production inference, unpack or gradients."""
import itertools
import math
import numpy as np

def pmf(y,eta):
    factorial=np.array([math.lgamma(float(v)+1) for v in y.ravel()]).reshape(y.shape)
    return y*eta-np.exp(eta)-factorial

def state_parts(theta,y,offset,k,lags):
    u=y.shape[-1];cut=k-1;end=cut+k*(k-1)
    initial=np.r_[theta[:cut],0.];initial-=np.logaddexp.reduce(initial)
    transition=np.c_[theta[cut:end].reshape(k,k-1),np.zeros(k)]
    transition-=np.logaddexp.reduce(transition,axis=1)[:,None]
    bias=theta[end:end+k*u].reshape(k,u)
    ar=theta[end+k*u:].reshape(k,u,lags)
    eta=np.broadcast_to(offset[:,:,None,:],y.shape[:2]+(k,u)).copy()+bias[None,None]
    for lag in range(1,lags+1):
        if lag<y.shape[1]:
            eta[:,lag:]+=np.log1p(y[:,:-lag,None,:])*ar[None,None,:,:,lag-1]
    emission=pmf(np.broadcast_to(y[:,:,None,:],eta.shape),eta).sum(axis=-1)
    return initial,transition,emission

def scalar_ll(theta,family,y,x,offset,size,exhaustive=False):
    if family!='Continuous':
        initial,transition,e=state_parts(theta,y,offset,size,5 if family=='Hybrid' else 0)
        if exhaustive:
            total=0.
            for trial in e:
                values=[]
                for path in itertools.product(range(size),repeat=y.shape[1]):
                    v=initial[path[0]]+trial[0,path[0]]
                    for t in range(1,len(path)):v+=transition[path[t-1],path[t]]+trial[t,path[t]]
                    values.append(v)
                total+=np.logaddexp.reduce(values)
            return float(total)
        joint=initial[None,:]+e[:,0]
        for t in range(1,y.shape[1]):
            joint=np.logaddexp.reduce(joint[:,:,None]+transition[None,:,:],axis=1)+e[:,t]
        return float(np.logaddexp.reduce(joint,axis=1).sum())
    u=y.shape[-1];f=x.shape[-1];d=size;i=0;arrays=[]
    for shape in ((d,d),(d,u),(d,f),(u,d)):
        end=i+math.prod(shape);arrays.append(theta[i:end].reshape(shape));i=end
    a,b,c,w=arrays
    h=np.zeros((len(y),d));eta=np.empty_like(y,dtype=float)
    for t in range(y.shape[1]):
        past=np.zeros((len(y),u)) if t==0 else np.log1p(y[:,t-1])
        h=np.tanh(np.einsum('ij,nj->ni',a,h)+np.einsum('ij,nj->ni',b,past)+np.einsum('ij,nj->ni',c,x[:,t]))
        eta[:,t]=offset[:,t]+np.einsum('ij,nj->ni',w,h)
    return float(pmf(y,eta).sum())

def scalar_objective(theta,model,ridge,family,size):
    x=model.x if family=='Continuous' else np.empty(model.y.shape[:2]+(0,))
    return -scalar_ll(theta,family,model.y,x,model.offset,size)/(model.y.shape[0]*model.y.shape[1])+ridge*float(theta@theta)/2

def check_gradient(theta,model,ridge,family,size,coordinates):
    from model_math import objective
    value,g=objective(theta,model,ridge)
    reference=scalar_objective(theta,model,ridge,family,size)
    errors=[]
    for i in coordinates:
        step=1e-5*max(1.,abs(float(theta[i])));p=theta.copy();m=theta.copy();p[i]+=step;m[i]-=step
        fd=(scalar_objective(p,model,ridge,family,size)-scalar_objective(m,model,ridge,family,size))/(2*step)
        errors.append(abs(float(g[i])-fd)/max(1.,abs(float(g[i])),abs(fd)))
    error=float(max(errors));scalar_error=abs(value-reference)
    return dict(coordinates=[int(i) for i in coordinates],scaled_gradient_error=error,
                independent_objective_error=scalar_error,passed=error<=1e-5 and scalar_error<=1e-10)

def synthetic_cases():
    from model_math import make
    rng=np.random.default_rng(20261013);y=rng.poisson(.7,(2,4,2));x=rng.normal(0,.3,(2,4,3));offset=np.full(y.shape,-.3)
    for family,sizes in (('Discrete',(2,3,4)),('Continuous',(1,2,4)),('Hybrid',(2,3,4))):
        for size in sizes:
            for ridge in (.001,.01,.1,1.):
                for seed in (11,23,37):
                    model=make(family,y,x,offset,size);theta=model.initial(seed)
                    yield family,size,ridge,seed,model,theta
