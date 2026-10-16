"""Pure frozen scoring, including registered source masks and donor histories."""
import numpy as np
from scipy.special import gammaln,logsumexp
from . import models as m


def unit_mask(units=None):
    mask=np.ones(8,dtype=bool) if units is None else np.asarray(units,dtype=bool)
    if mask.shape!=(8,) or not mask.any():raise ValueError('Nonempty original8unit mask required')
    return mask


def baseline_eta(driver,q,bundle,name,units=None):
    mask=unit_mask(units);s=bundle['baseline_scalers'][name]
    raw,sources=m.raw_features(driver,q,name)
    if not np.array_equal(sources,np.asarray(s['source_units'])):raise ValueError('Frozen baseline source-coordinate mismatch')
    mean=np.asarray(s['mean']);sd=np.asarray(s['sd'])
    x=np.divide(raw-mean,sd,out=np.zeros_like(raw,dtype=float),where=sd!=0)
    omitted=(sources>=0)&~mask[np.maximum(sources,0)]
    x=np.where(omitted[None,None,:,:],0.,x)
    theta=np.asarray(bundle['baseline_thetas'][name]).reshape(8,-1)
    return np.einsum('etuk,uk->etu',x,theta)[:,:,mask]


def C_features(driver,configuration,units=None):
    mask=unit_mask(units);state=configuration['state'];q=np.asarray(state['Q'])
    mean=np.asarray(state['count_mean']);sd=np.asarray(state['count_sd'])
    z=np.divide(driver-mean,sd,out=np.zeros_like(driver,dtype=float),where=sd!=0)
    z[:,:,~mask]=0.
    rho=np.exp(-.1/np.asarray(configuration['tau']));h=np.zeros((*driver.shape[:2],2))
    for t in range(1,driver.shape[1]):h[:,t]=rho*h[:,t-1]+(1-rho)*(z[:,t-1]@q)
    hm=np.asarray(state['h_mean']);hs=np.asarray(state['h_sd'])
    h=np.divide(h-hm,hs,out=np.zeros_like(h),where=hs!=0)
    return np.broadcast_to(h[:,:,None,:],(*driver.shape,2))[:,:,mask,:].copy()


def hmm_scores(outcomes,filter_counts,offset,theta,p):
    E,T,U=outcomes.shape;delta=np.asarray(theta).reshape(2,U)
    if filter_counts.shape!=outcomes.shape or offset.shape!=outcomes.shape:raise ValueError('HMM target/filter/offset shape mismatch')
    if p not in [.5,.9,.98]:raise ValueError('Transition outside frozen grid')
    logA=np.log([[p,1-p],[1-p,p]]);lp=np.full((E,2),-np.log(2.));scores=np.empty((E,T))
    for t in range(T):
        eta=offset[:,t,None,:]+delta[None,:,:]
        observed=(outcomes[:,t,None,:]*eta-np.exp(eta)-gammaln(outcomes[:,t,None,:]+1)).sum(axis=2)
        scores[:,t]=logsumexp(lp+observed,axis=1)
        filtering=(filter_counts[:,t,None,:]*eta-np.exp(eta)-gammaln(filter_counts[:,t,None,:]+1)).sum(axis=2)
        joint=lp+filtering;post=joint-logsumexp(joint,axis=1)[:,None]
        if t+1<T:lp=logsumexp(post[:,:,None]+logA[None,:,:],axis=1)
    return scores


def evaluate(y,q,bundle,*,units=None,history_driver=None,filter_driver=None,return_sequences=False):
    y=np.asarray(y);q=np.asarray(q);mask=unit_mask(units)
    driver=y if history_driver is None else np.asarray(history_driver)
    filtering=y if filter_driver is None else np.asarray(filter_driver)
    if y.ndim!=3 or y.shape[-1]!=8 or y.shape[1]<=5 or q.shape!=(*y.shape[:2],11) or driver.shape!=y.shape or filtering.shape!=y.shape:
        raise ValueError('Paired fixed8unit counts, nuisance and donor arrays required')
    if any(not np.isfinite(a).all() for a in [y,q,driver,filtering]) or any(np.any(a<0) or not np.equal(a,np.floor(a)).all() for a in [y,driver,filtering]):
        raise ValueError('Nonfinite/negative predictive inputs; no silent cleaning')
    target=y[:,:,mask];denominator=int(target[:,5:].size);scores={};sequences={};etas={}
    for name in ['B0','B1','B2','B3','B4']:
        eta=baseline_eta(driver,q,bundle,name,mask);etas[name]=eta
        values=m.poisson_scores(target,eta);sequences[name]=values.sum(axis=2)
        scores[name]=float(values[:,5:].sum()/denominator)
    offset=etas['B4']
    for name in ['D','S']:
        model=bundle[name];delta=np.asarray(model['theta']).reshape(2,8)[:,mask]
        values=hmm_scores(target,filtering[:,:,mask],offset,delta.ravel(),model['p'])
        sequences[name]=values;scores[name]=float(values[:,5:].sum()/denominator)
    model=bundle['C'];x=C_features(driver,model,mask)
    W=np.asarray(model['theta']).reshape(8,2)[mask]
    eta=offset+np.einsum('etuk,uk->etu',x,W)
    values=m.poisson_scores(target,eta);sequences['C']=values.sum(axis=2)
    scores['C']=float(values[:,5:].sum()/denominator)
    scores['Bstar']=scores[bundle['Bstar']];sequences['Bstar']=sequences[bundle['Bstar']]
    if not all(np.isfinite(value) for value in scores.values()):raise ValueError('Required finite predictive-score gate failed')
    result={'scores':scores,'nominal_unit_bins':denominator,'retained_units':int(mask.sum()),
        'epochs':len(y),'warmup_bins':5,'scored_bins_per_epoch':y.shape[1]-5}
    if return_sequences:result['joint_bin_log_scores']=sequences
    return result
