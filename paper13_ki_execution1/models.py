"""New frozen P13-v2 GLM, exact-forward HMM, and fixed leaky history math."""
import numpy as np
from scipy.special import gammaln,logsumexp

WARMUP=5

def pg(theta,gradient):
    theta=np.asarray(theta);gradient=np.asarray(gradient)
    if not np.isfinite(theta).all() or not np.isfinite(gradient).all() or np.any(theta< -8) or np.any(theta>8):raise ValueError('Nonfinite/out-of-bounds endpoint')
    z=gradient.copy();z[(theta==-8)&(gradient>0)]=0;z[(theta==8)&(gradient<0)]=0
    return float(np.max(np.abs(z),initial=0))

def histories(y):
    y=np.asarray(y,dtype=float);E,T,U=y.shape;out=np.zeros((E,T,U,3))
    for j,lags in enumerate([[1],[2,3],[4,5]]):
        for lag in lags:out[:,lag:,:,j]+=y[:,:T-lag,:]
    return out

def raw_features(y,q,name):
    y=np.asarray(y);E,T,U=y.shape;h=histories(y);targets=[];sources=[]
    for u in range(U):
        terms=[np.ones((E,T,1))];src=[-1]
        if name in {'B1','B4'}:terms.append(q);src += [-1]*11
        if name in {'B2','B4'}:terms.append(h[:,:,u,:]);src += [u]*3
        if name in {'B3','B4'}:
            others=[v for v in range(U) if v!=u]
            terms.append(h[:,:,others,:].reshape(E,T,-1));src += [v for v in others for _ in range(3)]
        if name not in {'B0','B1','B2','B3','B4'}:raise ValueError('Unknown baseline')
        targets.append(np.concatenate(terms,axis=-1));sources.append(src)
    return np.stack(targets,axis=2),np.asarray(sources)

def fit_scale(x):
    # Deterministically all A/C60x30bins, including unscored warm-up. No B/E/Drows.
    mean=x.mean(axis=(0,1));sd=x.std(axis=(0,1),ddof=0)
    mean[:,0]=0;sd[:,0]=1
    return {'mean':mean,'sd':sd}

def scale(x,state):
    mean=state['mean'];sd=state['sd']
    return np.divide(x-mean,sd,out=np.zeros_like(x,dtype=float),where=sd!=0)

def glm_predict(theta,x,offset=None):
    U,K=x.shape[-2:];eta=np.einsum('etuk,uk->etu',x,np.asarray(theta).reshape(U,K))
    if offset is not None:eta=eta+offset
    return eta

def poisson_scores(y,eta):return y*eta-np.exp(eta)-gammaln(y+1)

def glm_eval(theta,x,y,ridge,*,offset=None,penalize_intercept=False,gradient=True):
    U,K=x.shape[-2:];b=np.asarray(theta).reshape(U,K);eta=glm_predict(theta,x,offset)
    loss=-float(poisson_scores(y[:,5:],eta[:,5:]).mean())
    mask=np.ones_like(b)
    if not penalize_intercept:mask[:,0]=0
    loss += ridge/(2*U)*float(np.sum((b*mask)**2))
    if not gradient:return loss
    residual=(np.exp(eta[:,5:])-y[:,5:])/y[:,5:].size
    g=np.einsum('etu,etuk->uk',residual,x[:,5:])+ridge/U*b*mask
    return loss,g.ravel()

def glm_initial(x,y,seed):
    U,K=x.shape[-2:];b=np.random.default_rng(seed).normal(0,.01,(U,K))
    b[:,0]=np.log((y[:,5:].sum(axis=(0,1))+.5)/(y[:,5:].shape[0]*y[:,5:].shape[1]+.5))
    return np.clip(b,-8,8).ravel()

def projection(seed,U=8):
    q,r=np.linalg.qr(np.random.default_rng(seed).normal(size=(U,2)))
    return q*np.where(np.diag(r)>=0,1,-1)[None,:]

def leaky(y,tau,q,count_mean,count_sd):
    E,T,U=y.shape;z=np.divide(y-count_mean,count_sd,out=np.zeros_like(y,dtype=float),where=count_sd!=0)
    rho=np.exp(-.1/np.asarray(tau));h=np.zeros((E,T,2))
    for t in range(1,T):h[:,t]=rho*h[:,t-1]+(1-rho)*(z[:,t-1]@q)
    return h

def continuous_features(y,tau,seed,state=None):
    if state is None:
        q=projection(seed,y.shape[-1]);mean=y.mean(axis=(0,1));sd=y.std(axis=(0,1))
        h=leaky(y,tau,q,mean,sd)
        state={'Q':q,'count_mean':mean,'count_sd':sd,'h_mean':h.mean(axis=(0,1)),'h_sd':h.std(axis=(0,1))}
    else:h=leaky(y,tau,state['Q'],state['count_mean'],state['count_sd'])
    h=np.divide(h-state['h_mean'],state['h_sd'],out=np.zeros_like(h),where=state['h_sd']!=0)
    x=np.broadcast_to(h[:,:,None,:],(*y.shape,2)).copy()
    return x,state

def hmm_eval(theta,y,offset,p,ridge,*,gradient=True,return_scores=False):
    E,T,U=y.shape;delta=np.asarray(theta).reshape(2,U);P=2*U
    trans=np.array([[p,1-p],[1-p,p]]);logA=np.log(trans)
    lp=np.full((E,2),-np.log(2.));jp=np.zeros((E,2,P)) if gradient else None
    scores=np.empty((E,T));g=np.zeros(P)
    for t in range(T):
        eta=offset[:,t,None,:]+delta[None,:,:];mu=np.exp(eta)
        emission=(y[:,t,None,:]*eta-mu-gammaln(y[:,t,None,:]+1)).sum(axis=2)
        joint=lp+emission;norm=logsumexp(joint,axis=1);scores[:,t]=norm
        post=joint-norm[:,None]
        if gradient:
            de=np.zeros((E,2,P));residual=y[:,t,None,:]-mu
            de[:,0,:U]=residual[:,0];de[:,1,U:]=residual[:,1]
            jointj=jp+de;nj=np.einsum('ek,ekp->ep',np.exp(post),jointj)
            if t>=5:g-=nj.sum(axis=0)/(E*(T-5)*U)
            postj=jointj-nj[:,None,:]
        if t+1<T:
            zz=post[:,:,None]+logA[None,:,:];lp=logsumexp(zz,axis=1)
            if gradient:jp=np.einsum('eij,eip->ejp',np.exp(zz-lp[:,None,:]),postj)
    loss=-float(scores[:,5:].sum()/(E*(T-5)*U))+ridge/(2*U)*float(np.sum(delta**2))
    if return_scores:return scores
    if not gradient:return loss
    return loss,g+ridge/U*np.asarray(theta)

def finite_difference(fun,theta,relative_step=1e-4):
    x=np.asarray(theta,dtype=float);result=np.empty_like(x)
    f0=None
    for j in range(len(x)):
        h=relative_step*max(1.,abs(x[j]));a=x.copy();b=x.copy()
        if x[j]-h>=-8 and x[j]+h<=8:
            a[j]+=h;b[j]-=h;result[j]=(fun(a)-fun(b))/(2*h)
        else:
            direction=1 if x[j]+2*h<=8 else -1
            if direction==1:h=min(h,(8-x[j])/2)
            else:h=min(h,(x[j]+8)/2)
            if h<=0:raise ValueError('No inward derivative step')
            if f0 is None:f0=fun(x)
            a[j]+=direction*h;b[j]+=direction*2*h
            result[j]=direction*(-3*f0+4*fun(a)-fun(b))/(2*h)
    return result

def gradient_errors(a,b):
    absolute=np.abs(a-b);relative=absolute/np.maximum(1,np.maximum(np.abs(a),np.abs(b)))
    return {'max_absolute':float(absolute.max(initial=0)),'max_relative':float(relative.max(initial=0)),'coordinate_absolute':absolute.tolist(),'coordinate_relative':relative.tolist()}
