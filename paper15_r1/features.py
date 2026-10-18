"""Exact strictly-past native nuisance/history and fixed finite DCT features."""
import numpy as np


def held(wt,wp,b):
    ix=np.searchsorted(wt,b,side='left')-1
    if np.any(ix<0):raise ValueError('Missing strict-past wheel support')
    return wp[ix],ix


def nuisance(trials,trial_ids,bin_starts,epoch_starts,wt,wp,rich=False):
    wt=np.asarray(wt);wp=np.asarray(wp)
    assert np.isfinite(wt).all() and np.isfinite(wp).all() and (np.diff(wt)>0).all()
    absolute=np.r_[0.,np.cumsum(np.abs(np.diff(wp)))]
    out=[]
    def value(row,name):
        val=row.get(name)
        return np.nan if val is None else float(val)
    for trial_id,bins,epoch in zip(trial_ids,bin_starts,epoch_starts):
        tr=trials[int(trial_id)];b=np.asarray(bins)
        a=value(tr,'intervals_0');s=value(tr,'stimOn_times');g=value(tr,'goCue_times')
        response=value(tr,'response_times');feedback=value(tr,'feedback_times')
        choice=value(tr,'choice');reward=value(tr,'feedbackType')
        if not np.isfinite([a,s,g,feedback,choice,reward]).all():raise ValueError('Essential finite task nuisance missing')
        left=value(tr,'contrastLeft');right=value(tr,'contrastRight')
        if np.isnan(left):left=0.
        if np.isnan(right):right=0.
        e=np.clip(b-a,0,10)/10;seen=s<b;r=seen*np.clip(b-s,0,1)
        prior=[t for t in trials[:int(trial_id)] if t.get('feedback_times') is not None and t.get('response_times') is not None
            and float(t['feedback_times'])<epoch and float(t['response_times'])<epoch]
        prev=prior[-1] if prior else None
        prev_reward=0. if prev is None else value(prev,'feedbackType')
        prev_choice=0. if prev is None else value(prev,'choice')
        if not np.isfinite([prev_reward,prev_choice]).all():raise ValueError('Invalid completed-trial source codes')
        n=len(b);const=lambda z:np.full(n,z,float)
        trial_order=float(trial_id)/1000;hour=b/3600
        response_seen=response<b;feedback_seen=feedback<b
        cols=[e,e**2,r,r**2,r**3,seen*left,seen*right,seen*(left>0),seen*(right>0),seen*left*r,seen*right*r,
            g<b,(g<b)*np.clip(b-g,0,1),response_seen,response_seen*choice,feedback_seen,feedback_seen*reward,
            const(prev_reward),const(prev_choice),const(trial_order),const(trial_order**2),hour,hour**2]
        now,ix=held(wt,wp,b);base,_=held(wt,wp,epoch);cols.append(now-base)
        displacement=[];total=[];square=[]
        for h in [.05,.1,.25,.5]:
            past,jx=held(wt,wp,b-h);d=now-past
            displacement.append(d);total.append(absolute[ix]-absolute[jx]);square.append((d/h)**2)
        cols+=displacement+total+square+[np.abs(displacement[0])>.001]
        if rich:cols += [const(trial_order**3),const(trial_order**4),hour**3,hour**4]
        x=np.stack(cols,axis=-1).astype(np.float64)
        assert x.shape==(len(b),41 if rich else 37) and np.isfinite(x).all()
        out.append(x)
    return np.asarray(out)


def observed_arrays(times,labels,units,stimuli,delta=.05,warmup=.5,history=.5):
    times=np.asarray(times);labels=np.asarray(labels);stimuli=np.asarray(stimuli)
    warm=int(round(warmup/delta));l=warm+int(round(.5/delta))
    micro_step=int(round(delta/.05));micro_warm=int(round(warmup/.05))
    assert micro_step*.05==delta and warm*delta==warmup
    micro_count=int(round((warmup+.5)/.05))
    micro_edges=stimuli[:,None]+(np.arange(micro_count+1)[None,:]-micro_warm)*.05
    micro_edges[:,micro_warm]=stimuli;micro_edges[:,-1]=stimuli+.5
    all_edges=micro_edges[:,np.arange(l+1)*micro_step]
    starts=all_edges[:,:-1]
    epochs=stimuli-warmup
    targets=np.zeros((len(stimuli),l,len(units)),np.int64)
    histories=np.zeros((len(stimuli),l,len(units)*4),float)
    lag_indices=[0,1,2,4,int(round(history/.05))]
    for v,unit in enumerate(units):
        st=times[labels==unit]
        for i,bins in enumerate(starts):
            targets[i,:,v]=np.diff(np.searchsorted(st,all_edges[i],side='left'))
            current=np.arange(l)*micro_step
            for j,(short,long) in enumerate(zip(lag_indices[:-1],lag_indices[1:])):
                lo=micro_edges[i,np.maximum(0,current-long)];hi=micro_edges[i,np.maximum(0,current-short)]
                histories[i,:,v*4+j]=(np.searchsorted(st,hi,side='left')-np.searchsorted(st,lo,side='left'))/((long-short)*.05)
    return targets,histories,starts,epochs,warm


def fit_scale(raw,warm):
    score=raw[:,warm:].reshape(-1,raw.shape[-1])
    means=score.mean(axis=0);sd=score.std(axis=0);active=sd>=1e-8
    return dict(mean=means.tolist(),sd=sd.tolist(),active=active.tolist())


def scale(raw,state):
    mean=np.asarray(state['mean']);sd=np.asarray(state['sd']);active=np.asarray(state['active'])
    return np.where(active,np.clip((raw-mean)/np.where(active,sd,1.),-3,3),0.)


def design(nuisances,histories,warm,state=None):
    raw=np.concatenate([nuisances,histories],axis=-1)
    state=fit_scale(raw,warm) if state is None else state
    x=np.concatenate([np.ones((*raw.shape[:2],1)),scale(raw,state)],axis=-1)
    return x,state,np.r_[True,state['active']]


def dct_state(microcounts,rank,tau,warm=10,state=None):
    """50ms microbins, finite500ms history; outside-epoch standardized state zero."""
    rates=np.asarray(microcounts)/.05;u=rates.shape[-1]
    if state is None:micro_scale=fit_scale(rates,warm)
    else:micro_scale=state['micro_scale']
    # z standardization itself is un-clipped; only resulting q gets ±3 transform.
    mean=np.asarray(micro_scale['mean']);sd=np.asarray(micro_scale['sd']);active=np.asarray(micro_scale['active'])
    z=np.where(active,(rates-mean)/np.where(active,sd,1.),0.)
    R=np.cos(np.pi*(np.arange(u)[:,None]+.5)*np.arange(rank)[None,:]/u)*np.sqrt(2/u);R[:,0]=1/np.sqrt(u)
    weights=np.exp(-np.arange(10)*.05/tau);weights/=weights.sum()
    projected=z@R;q=np.zeros((*z.shape[:2],rank))
    for lag,w in enumerate(weights,1):
        if lag<q.shape[1]:q[:,lag:]+=w*projected[:,:-lag]
    qscale=fit_scale(q,warm) if state is None else state['q_scale']
    return scale(q,qscale),dict(micro_scale=micro_scale,q_scale=qscale,rank=rank,tau=tau,R=R.tolist(),weights=weights.tolist())
