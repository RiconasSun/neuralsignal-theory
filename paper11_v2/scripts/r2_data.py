"""Only the R0 admitted train/development arrays and allowlisted task context."""
import csv
import json
from pathlib import Path

import numpy as np
import run_r0 as base

COHORT = base.STUDY/'results/R0_amendment1_code1'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def event_context(rows,ids,set_sizes,training_ids,epoch_bins=60):
    allowed = set(ids)
    expected = {'Fixation':(-6.,1.),'Stimulus':(-5.,2.),'Maintenance':(-3.,3.)}
    events = {tid:{} for tid in ids}
    for row in rows:
        tid = int(row['trial'])
        if tid not in allowed:
            continue
        label = row['nix_event'].split('_')[0]
        if label not in expected:
            continue  # Probe, response and outcome fields never become features.
        value = (float(row['onset']),float(row['duration']))
        if label in events[tid] or value != expected[label]:
            raise ValueError('Unknown/duplicate/nonfixed task timing, no guessed event schedule')
        events[tid][label] = value
    if any(set(v)!=set(expected) for v in events.values()):
        raise ValueError('Missing known task event observation')
    if epoch_bins != 60:
        raise ValueError('Primary frozen epoch has60bins')
    sizes = np.asarray([set_sizes[tid] for tid in training_ids],float)
    if not np.isin(sizes,[4,6,8]).all():
        raise ValueError('Unknown working-memory set size')
    mean,scale = float(sizes.mean()),float(sizes.std())
    scale = scale if scale>0 else 1.
    time = np.arange(60)/60
    phase = np.arange(60)
    x = np.empty((len(ids),60,6))
    for i,tid in enumerate(ids):
        size = set_sizes[tid]
        if size not in [4,6,8]:
            raise ValueError('Unknown scored trial set size')
        x[i] = np.stack([time,time**2,((phase>=10)&(phase<30)).astype(float),
                        (phase>=30).astype(float),((size-mean)/scale)*(phase>=10),
                        np.isin(phase,[0,10,30]).astype(float)],axis=-1)
    return x,{'load_mean':mean,'load_scale':scale,'source':'scheduled fixation/stimulus/maintenance only; load gated at-5s'}


def train_transforms(train_ids,validation_ids,xtrain,xval):
    low,high = min(train_ids),max(train_ids)
    if high<=low:
        raise ValueError('No training trial-position range')
    mask = np.ptp(xtrain,axis=(0,1))>0
    return (xtrain[:,:,mask],xval[:,:,mask],
            (np.asarray(train_ids)-low)/(high-low),
            (np.asarray(validation_ids)-low)/(high-low),
            {'position_min':low,'position_max':high,'context_columns':np.flatnonzero(mask).tolist()})


def session(key):
    filename = key.replace('/','_')+'.json'
    qc = load(COHORT/'sessions'/filename)
    if not qc['admitted']:
        raise ValueError('Cannot silently admit a new or excluded session')
    feature = COHORT/'features'/filename
    if base.digest(feature)!=qc['feature_sha256']:
        raise ValueError('Frozen count features changed')
    f = load(feature)
    locks = load(base.ROOT/'paper11/data_manifest/M1/trial_splits.json')['sessions'][key]['partitions']
    train_ids,val_ids = f['train_trial_ids'],f['validation_trial_ids']
    if train_ids!=locks['train'] or val_ids!=locks['validation'] or (set(train_ids)|set(val_ids))&set(locks['test']):
        raise ValueError('Frozen partitions or oldtest protection violated')
    ytrain,yval = np.asarray(f['training_counts'],float),np.asarray(f['validation_counts'],float)
    for arr,ids in [(ytrain,train_ids),(yval,val_ids)]:
        if arr.shape!=(len(ids),60,len(f['unit_ids'])) or not np.isfinite(arr).all() or np.any(arr<0) or np.any(arr!=np.floor(arr)):
            raise ValueError('Invalid observed hippocampal counts')
    if len(train_ids)<24 or len(val_ids)<8 or len(f['unit_ids'])<5 or np.any(ytrain.sum(axis=(0,1))<20):
        raise ValueError('Frozen cohort adequacy failed')
    subject,ses = key.split('/')
    rel = f'{key}/ieeg/{subject}_{ses}_task-verbalWM_trialevents.tsv'
    meta = base.ROOT/'paper11/raw/M1/nm000363'/rel
    if base.digest(meta)!=qc['metadata_sha256'][rel]:
        raise ValueError('Task metadata identity changed')
    with meta.open(encoding='utf-8-sig',newline='') as stream:
        rows = list(csv.DictReader(stream,delimiter='\t'))
    sizes = {r['trial']:r['set_size'] for r in f['causal_trial_metadata']}
    xt,scales = event_context(rows,train_ids,sizes,train_ids)
    xv,_ = event_context(rows,val_ids,sizes,train_ids)
    xt,xv,pt,pv,transform = train_transforms(train_ids,val_ids,xt,xv)
    return {'key':key,'subject':subject,'ytrain':ytrain,'yval':yval,'xtrain':xt,'xval':xv,
            'ptrain':pt,'pval':pv,'train_ids':train_ids,'validation_ids':val_ids,
            'unit_ids':f['unit_ids'],'transform':{**scales,**transform},
            'feature_sha256':qc['feature_sha256'],'event_metadata_sha256':qc['metadata_sha256'][rel]}
