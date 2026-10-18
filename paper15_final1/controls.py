"""Frozen finite destructive references and role-local thinning; no generative null."""
import hashlib
import numpy as np


def seed(suite,subject,role,replicate):
    if role!='D':raise PermissionError('Final reference schedules are D-only; source access is separately gated')
    return int.from_bytes(hashlib.sha256(f'P15-M1|150107|{suite}|{subject}|{role}|{replicate}'.encode()).digest()[:8],'big')


def thinning_seed(subject,uuid,role):
    if role not in ('C','D'):raise PermissionError('Only original Final role-local thinning schedules')
    return int.from_bytes(hashlib.sha256(f'P15-M1|150108|S07|{subject}|{uuid}|{role}'.encode()).digest()[:8],'big')


def thin_role(times,labels,units,uuids,rates,subject,role):
    retained=np.zeros(len(times),bool);receipts=[]
    for unit,uuid,rate in zip(units,uuids,rates):
        ix=np.flatnonzero(labels==unit);p=min(1.,2./rate);s=thinning_seed(subject,uuid,role)
        rng=np.random.Generator(np.random.PCG64(s));keep=rng.random(len(ix))<p
        retained[ix[keep]]=True
        receipts.append(dict(unit=int(unit),uuid=uuid,role=role,p=p,seed=s,draw_count=len(ix),kept=int(keep.sum())))
    return times[retained],labels[retained],receipts


def stratum_keys(trials,trial_ids,role_bounds,wheel_magnitude=None,wheel_threshold=None):
    keys=[];half=(role_bounds[0]+role_bounds[1])//2
    for j,trial_id in enumerate(trial_ids):
        tr=trials[int(trial_id)]
        left=0. if tr.get('contrastLeft') is None else tr['contrastLeft'];right=0. if tr.get('contrastRight') is None else tr['contrastRight']
        side=0 if left>0 and right==0 else 1 if right>0 and left==0 else 2
        key=(side,int(max(left,right)>.25),int(trial_id>=half))
        if wheel_magnitude is not None:key+= (int(wheel_magnitude[j]>wheel_threshold),)
        keys.append(key)
    return keys


def cyclic_donors(trial_ids,keys,rng):
    donors=np.full(len(trial_ids),-1,int);strata=sorted(set(keys))
    for key in strata:
        ix=np.array([i for i,k in enumerate(keys) if k==key],int)
        ix=ix[np.argsort(np.asarray(trial_ids)[ix],kind='stable')]
        if len(ix)<2:continue
        shift=int(rng.integers(1,len(ix)));donors[ix]=np.roll(ix,shift)
    return donors


def block_donors(trial_ids,role_bounds,rng):
    ids=np.asarray(trial_ids);lookup={int(t):i for i,t in enumerate(ids)};blocks=[]
    for start in range(role_bounds[0],role_bounds[1],5):
        tids=list(range(start,min(start+5,role_bounds[1])))
        if len(tids)==5 and all(t in lookup for t in tids):blocks.append([lookup[t] for t in tids])
    donors=np.full(len(ids),-1,int)
    if len(blocks)<2:return donors
    blocks=np.asarray(blocks);shift=int(rng.integers(1,len(blocks)));donor_blocks=np.roll(blocks,shift,axis=0)
    donors[blocks.ravel()]=donor_blocks.ravel();return donors


def reference(y,suite,trial_ids,rng,keys=None,role_bounds=None):
    y=np.asarray(y);n=len(y)
    if suite=='N1':
        out=np.empty_like(y);offsets=[]
        for i in np.argsort(trial_ids,kind='stable'):
            shift=int(rng.integers(1,20));out[i]=np.roll(y[i],shift,axis=0);offsets.append(dict(trial=int(trial_ids[i]),offset=shift))
        return out,np.arange(n),dict(offsets=offsets,donors=None)
    donors=block_donors(trial_ids,role_bounds,rng) if suite=='N4' else cyclic_donors(trial_ids,keys,rng)
    ix=np.flatnonzero(donors>=0)
    return y[donors[ix]],ix,dict(donors=[dict(target_trial=int(trial_ids[i]),donor_trial=int(trial_ids[donors[i]])) for i in ix])


def coverage(selected,total):
    return len(selected)>=30 and len(selected)>=.6*total


def history_from_microbins(counts):
    counts=np.asarray(counts);n,l,u=counts.shape;out=np.zeros((n,l,u,4))
    for j,(short,long) in enumerate([(0,1),(1,2),(2,4),(4,10)]):
        for t in range(l):
            out[:,t,:,j]=counts[:,max(0,t-long):max(0,t-short)].sum(axis=1)/((long-short)*.05)
    return out.reshape(n,l,u*4)
