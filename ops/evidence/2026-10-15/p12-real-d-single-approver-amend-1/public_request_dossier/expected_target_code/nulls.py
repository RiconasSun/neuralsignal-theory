"""Fixed-predictor disruptions; neither refit nulls nor causal inference."""
import hashlib
import numpy as np
from scipy.special import gammaln
from glm import MODELS,CONTRASTS
NAMES=list(MODELS)
PRIMARY=list(CONTRASTS)[:4]
def rng(sid,region,suite,replicate):
    text=f'P12-PREDICTIVE-STRUCTURE-V2|{sid}|{region}|{suite}|{replicate}'
    return np.random.default_rng(int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big'))
def eta(y,c,o,w,ms,bins=None):
    n,t,u=y.shape;m,s=ms;beta=w/s[None,:,:];bias=beta[:,:,0]-np.sum(beta[:,:,1:]*m[None,:,1:],axis=-1)
    h=np.zeros((n,t,u,5))
    for lag in range(1,6):h[:,lag:,:,lag-1]=np.log1p(y[:,:-lag,:])
    p=(h.sum(axis=2,keepdims=True)-h)/(u-1)
    cs=(c[:,None]==np.arange(1,8)).astype(float)
    context=np.einsum('nc,muc->mnu',cs,beta[:,:,1:8])
    oo=o/599;context+=beta[:,:,27][:,None,:]*oo[None,:,None]+beta[:,:,28][:,None,:]*oo[None,:,None]**2
    if bins is None:bins=np.broadcast_to(np.arange(20),(n,20))
    timebeta=np.concatenate((np.zeros((len(w),u,1)),beta[:,:,8:27]),axis=-1)
    tt=np.stack([np.take(timebeta[i],bins,axis=1).transpose(1,2,0) for i in range(len(w))])
    hh=np.einsum('ntuf,muf->mntu',h,beta[:,:,29:34])+np.einsum('ntuf,muf->mntu',p,beta[:,:,34:39])
    return bias[:,None,None,:]+context[:,:,None,:]+tt+hh
def get_gains(y,prediction):
    ll=(y[None,:,:,:]*prediction-np.exp(prediction)-gammaln(y+1)[None,:,:,:]).mean(axis=(1,2,3))
    if not np.isfinite(ll).all():raise RuntimeError('NONFINITE_NULL_SCORE')
    return np.array([ll[NAMES.index(CONTRASTS[k][0])]-ll[NAMES.index(CONTRASTS[k][1])] for k in PRIMARY])
def temporal(y,neta,random):
    total=y.sum(axis=1).astype(int);mu=np.exp(neta).transpose(0,2,1);prob=mu/mu.sum(axis=-1,keepdims=True)
    new=random.multinomial(total,prob).transpose(0,2,1)
    if not np.array_equal(new.sum(axis=1),y.sum(axis=1)):raise RuntimeError('COUNT_PRESERVING_NULL')
    return new
def permute_labels(c,o,suite,random):
    c=c.copy();o=o.copy();bins=None
    if suite=='S':
        for b in np.unique(o//100):
            idx=np.where(o//100==b)[0];c[idx]=random.permutation(c[idx])
    elif suite=='B':bins=np.stack([random.permutation(20) for i in range(len(c))])
    elif suite=='O':
        for cc in range(8):
            idx=np.where(c==cc)[0];o[idx]=random.permutation(o[idx])
    else:raise ValueError('SUITE')
    return c,o,bins
