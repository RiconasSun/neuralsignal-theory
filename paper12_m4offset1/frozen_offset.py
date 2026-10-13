"""Apply immutable training-only all-seed mean weights, never refit on validation."""
import hashlib
import json
from pathlib import Path
import numpy as np
from baseline_features import design,training_scaler,transform


def apply(y,valid,c,vc,o,vo,weights):
    if len(weights)!=3 or any(w.shape!=(y.shape[-1],29) or not np.all(np.isfinite(w)) or np.any(np.abs(w)>8) for w in weights):
        raise RuntimeError('THREE_FROZEN_OFFSET_WEIGHTS_REQUIRED')
    raw=np.concatenate((design(y,c,o,'event'),design(y,c,o,'drift')[...,1:]),axis=-1)
    vr=np.concatenate((design(valid,vc,vo,'event'),design(valid,vc,vo,'drift')[...,1:]),axis=-1)
    scaler=training_scaler(raw);train=transform(raw,scaler);validation=transform(vr,scaler)
    mean=np.mean(weights,axis=0)
    return np.einsum('ntuf,uf->ntu',train,mean),np.einsum('ntuf,uf->ntu',validation,mean),train[:,:,0,1:],validation[:,:,0,1:]


def fit_offset(sid,region,parent_sha,y,valid,c,vc,o,vo):
    root=Path(__file__).parent;bundle=json.loads((root/'offset_bundle.json').read_text())
    states=root/'offset_states.npz';records=root/'offset_records.json'
    if hashlib.sha256(states.read_bytes()).hexdigest()!=bundle['state_sha256'] or hashlib.sha256(records.read_bytes()).hexdigest()!=bundle['records_sha256']:
        raise RuntimeError('FROZEN_TRAINING_OFFSET_ARTIFACT_CHANGED')
    record=json.loads(records.read_text());case=sid+'_'+region;meta=record['meta'][case]
    if meta['parent_AB_sha256']!=parent_sha or meta['training_array_sha256']!=hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest():
        raise RuntimeError('OFFSET_AND_MODEL_TRAINING_DATA_MISMATCH')
    diagnostics=[z for z in record['rows'] if z['session_id']==sid and z['region']==region]
    if len(diagnostics)!=3 or {z['seed'] for z in diagnostics}!={11,23,37} or any(not z['converged'] or z['projected_gradient']>.001 for z in diagnostics):
        raise RuntimeError('ALL_FROZEN_OFFSET_SEEDS_REQUIRED')
    with np.load(states,allow_pickle=False) as z:weights=[z[case+'_'+str(seed)] for seed in (11,23,37)]
    return (*apply(y,valid,c,vc,o,vo,weights),diagnostics)
