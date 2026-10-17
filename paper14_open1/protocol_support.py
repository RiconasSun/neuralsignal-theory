"""Inactive prospective policy oracles; no fitted models or real neural values."""
import hashlib
import numpy as np
import pandas as pd

def missing_event_mask(frame):
    valid=np.ones(len(frame),dtype=bool)
    for flag,event in [('is_response','response_time'),('is_rewarded','reward_time')]:
        if flag not in frame or event not in frame:raise ValueError('Missing causal event field')
        values=frame[flag]
        known=values.map(lambda x:isinstance(x,(bool,np.bool_))).to_numpy(dtype=bool)
        observed=values.eq(True).to_numpy(dtype=bool)
        finite=np.isfinite(frame[event].to_numpy(dtype=float))
        valid &= known & (~observed|finite)
    return valid

def masks(frame):
    """Original scheduled six blocks, never reconstruct/merge after exclusions."""
    required=['trial_index','block_index','rewarded_modality','start_time','stim_start_time','stim_stop_time','stop_time','is_opto']
    if any(k not in frame for k in required):raise ValueError('Missing task contract')
    f=frame.reset_index(drop=True);n=len(f)
    if n==0:raise ValueError('No trials')
    ids=f.trial_index.to_numpy(float)
    stim=f.stim_start_time.to_numpy(float)
    if not np.isfinite(ids).all() or np.any(np.diff(ids)<=0) or not np.isfinite(stim).all() or np.any(np.diff(stim)<=0):raise ValueError('Noncausal trial clock/identity')
    blocks=[];positions=[];contexts=[];previous=None
    for row in f.itertuples():
        key=(row.block_index,row.rewarded_modality)
        if key!=previous:
            if not np.isfinite(row.block_index) or int(row.block_index)!=row.block_index or row.rewarded_modality not in {'aud','vis'}:raise ValueError('Unknown scheduled block')
            if row.block_index in blocks:raise ValueError('Reappearing block cannot merge')
            blocks.append(row.block_index);contexts.append(row.rewarded_modality);pos=0
        positions.append(pos);pos+=1;previous=key
    if len(blocks)!=6 or set(contexts)!={'aud','vis'}:raise ValueError('Original six-block design required')
    a=f[['start_time','stim_start_time','stim_stop_time','stop_time']].to_numpy(float)
    valid=np.isfinite(a).all(axis=1)&(a[:,0]<=a[:,1])&(a[:,1]<a[:,2])&(a[:,2]<=a[:,3])&(a[:,1]+.5<=a[:,3])
    valid &= np.array(positions)>=5
    valid &= f.is_opto.map(lambda x:isinstance(x,(bool,np.bool_)) and not x).to_numpy(dtype=bool)
    valid &= missing_event_mask(f)
    half=np.array(['calibration' if blocks.index(x)<3 else 'scoring' for x in f.block_index])
    for block in blocks:
        bm=f.block_index.eq(block).to_numpy()
        if (valid&bm).sum()<15:valid[bm]=False
    counts={(ctx,h):int((valid&f.rewarded_modality.eq(ctx).to_numpy()&(half==h)).sum()) for ctx in ['aud','vis'] for h in ['calibration','scoring']}
    enough_blocks=all(sum(bool((valid&f.block_index.eq(b).to_numpy()).any()) for b,c in zip(blocks,contexts) if c==ctx)>=2 for ctx in ['aud','vis'])
    return valid,half,counts,bool(enough_blocks and min(counts.values())>=60)

def allocate(identities):
    ids=list(identities)
    if len(ids)!=len(set(ids)) or len(ids)<16:raise ValueError('Independent denominator not established')
    if not all(isinstance(x,str) and len(x)==6 and x.isascii() and x.isdigit() for x in ids):raise ValueError('Canonical mouse identity required')
    rank=sorted(ids,key=lambda x:hashlib.sha256(('P14-OPEN-V1|'+x).encode('ascii')).digest())
    cut=len(rank)//2
    return rank[:cut],rank[cut:]

def temporal_definition_fixture(counts,rng):
    """Finite within-unit trial-bin permutation, definition test only.

    This deliberately does not assert exchangeability or biological-null validity.
    Any future scientific null needs the full frozen protocol and review.
    """
    x=np.asarray(counts)
    if x.ndim!=3 or x.shape[1]!=5 or not np.issubdtype(x.dtype,np.integer) or (x<0).any():raise ValueError('Finite trial/five-bin/unit counts required')
    return np.stack([np.stack([x[t,rng.permutation(5),u] for u in range(x.shape[2])],axis=1) for t in range(len(x))])

def ready_gate(*,license_verified,cohort_verified,timing_verified,protocol_frozen,review_accepted):
    values=[license_verified,cohort_verified,timing_verified,protocol_frozen,review_accepted]
    if any(type(v) is not bool for v in values):raise ValueError('Explicit boolean gate states only')
    return all(values)
