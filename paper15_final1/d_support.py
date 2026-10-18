"""Frozen D feature/predictor components; real extraction requires active batch context."""
from pathlib import Path
import datetime
import os
import numpy as np
from scipy.special import logsumexp
from .source import R,P,read,sha,source_rows
from .calibration import build_model,configurations,wheel
from .models import Model
from .features import observed_arrays,nuisance,design,dct_state,held,scale
from .controls import thin_role,history_from_microbins


class DContext:
    def __init__(self,claim_path,gate_hash,subjects):
        from .admission import verify_pre_D_gate
        gate=verify_pre_D_gate()
        if Path(claim_path).resolve()!=(P/'D_BATCH_CLAIM.json').resolve() or gate_hash!=sha(P/'PRE_D_GATE.json') or list(subjects)!=gate['subjects']:
            raise PermissionError('D context must bind actual reviewed gate and original batch claim')
        self.path=Path(claim_path);self.gate_hash=gate_hash;self.subjects=tuple(subjects);self.active=True
        claim=read(self.path)
        assert claim['status']=='STARTED' and claim['process_id']==os.getpid() and claim['gate_sha256']==gate_hash
        self.started_at=claim['started_at']

    def authorize(self,subject):
        claim=read(self.path)
        if (not self.active or subject not in self.subjects or claim['status']!='STARTED'
            or claim['process_id']!=os.getpid() or claim['gate_sha256']!=self.gate_hash
            or claim['started_at']!=self.started_at):raise PermissionError('No active frozen one-shot D batch')


def project_D(times,labels,start,stop,cluster_count,support,fs):
    if len(times)!=len(labels) or not np.issubdtype(labels.dtype,np.integer):raise ValueError('D_SOURCE_IDENTITY_ERROR')
    ts=[];ls=[]
    for lo in range(0,len(times),1000000):
        chunk=np.asarray(times[lo:lo+1000000])
        if not np.isfinite(chunk).all():raise ValueError('UNASSIGNABLE_SOURCE_TIMESTAMP_D_BATCH')
        mask=(chunk>=start)&(chunk<stop)
        ts.append(chunk[mask]);ls.append(np.asarray(labels[lo:lo+1000000])[mask])
    dt=np.concatenate(ts).astype(np.float64);dl=np.concatenate(ls)
    if len(dt) and (not (np.diff(dt)>=0).all() or dl.min()<0 or dl.max()>=cluster_count):raise ValueError('D_SOURCE_ORDER_OR_LABEL_ERROR')
    if len(dt) and (dt[0]<support[0]-1/fs or dt[-1]>support[1]+1/fs):raise ValueError('D_SOURCE_SUPPORT_ERROR')
    return dt,dl


def raw_D(subject,context):
    if not isinstance(context,DContext):raise PermissionError('D batch context required before any raw-file open')
    context.authorize(subject)
    row=next(r for r in source_rows() if r['subject']==subject);state=read(P/'metadata'/(subject+'_task.json'))
    qc=read(P/'results'/(subject+'_C_QC.json'));paths={}
    for f in row['files']:
        if f['role'] not in ('times','clusters'):continue
        receipt=next(r for r in qc['files'] if r['key']==f['key'])
        path=P/'work/neural'/row['eid']/Path(f['key']).name
        assert path.stat().st_size==receipt['bytes'] and sha(path)==receipt['sha256']
        paths[f['role']]=path
    a,b=state['result']['partitions']['D'];tr=state['trials']
    times,labels=project_D(np.load(paths['times'],mmap_mode='r',allow_pickle=False),np.load(paths['clusters'],mmap_mode='r',allow_pickle=False),
        tr[a]['intervals_0'],tr[b-1]['intervals_1'],len(state['native_uuid_list']),state['result']['recording_sync_support'],state['result']['fs'])
    return times,labels,row,state


def main_arrays(times,labels,state,prep,wt,wp):
    ids=np.flatnonzero(np.asarray(state['valid'])&(np.asarray(state['roles'])=='D'))
    stimuli=np.array([state['trials'][i]['stimOn_times'] for i in ids])
    y,h,b,epoch,warm=observed_arrays(times,labels,prep['units'],stimuli)
    raw=nuisance(state['trials'],ids,b,epoch,wt,wp);x,_,active=design(raw,h,warm,prep['scales'])
    assert active.tolist()==prep['active'] and warm==prep['warm_bins']
    arrays=dict(x=x,y=y,active=active,trial_ids=ids)
    for key,cscales in prep['C_scales'].items():
        # Key and state are frozen on C; no D scale fitting.
        parts=key.split('_');rank=int(parts[1][1:]);tau=float(parts[2][3:])
        q,qs=dct_state(y,rank,tau,warm,cscales)
        arrays[key]=q;arrays[key+'_active']=np.asarray(qs['q_scale']['active'])
    return arrays


def case_arrays(subject,case_state,times,labels,wt,wp):
    assert case_state['subject']==subject and case_state['status']=='C_PREPROCESSING_SEALED'
    case=case_state['case'];metadata=case_state['metadata'];units=case_state['units'];thinning=None
    if case.get('thin'):
        metrics={r['cluster_id']:r for r in case_state['physiology']}
        times,labels,thinning=thin_role(times,labels,units,[metadata['native_uuid_list'][u] for u in units],
            [metrics[u]['C_rate_Hz'] for u in units],subject,'D')
    ids=np.flatnonzero(np.asarray(metadata['valid'])&(np.asarray(metadata['roles'])=='D'))
    stimuli=np.array([metadata['trials'][i]['stimOn_times'] for i in ids])
    y,h,b,_,warm=observed_arrays(times,labels,units,stimuli,case_state['delta'],case.get('warmup',.5),case.get('history',.5))
    raw=nuisance(metadata['trials'],ids,b,stimuli-.5,wt,wp,case.get('rich',False))
    x,_,active=design(raw,h,warm,case_state['scales'])
    assert warm==case_state['warm'] and active.tolist()==case_state['active']
    return dict(x=x,y=y,active=active,trial_ids=ids),thinning


def pre_epoch_wheel(metadata,ids,wt,wp):
    epoch=np.array([metadata['trials'][int(i)]['stimOn_times']-.5 for i in ids])
    a,_=held(wt,wp,epoch);b,_=held(wt,wp,epoch-.5)
    return np.abs(a-b)


def control_arrays(main,prep,surrogate,indices,wheel_donors=None):
    ids=np.asarray(indices,int);x=main['x'][ids].copy();y=main['y'][ids];assert surrogate.shape==y.shape
    if wheel_donors is None:
        h=history_from_microbins(surrogate);state={k:prep['scales'][k][37:] for k in ('mean','sd','active')}
        x[:,:,38:]=scale(h,state)
    else:
        donors=np.asarray(wheel_donors,int);assert len(donors)==len(ids);x[:,:,24:38]=main['x'][donors,:,24:38]
    out=dict(x=x,y=y,active=main['active'],trial_ids=main['trial_ids'][ids])
    for key,cscales in prep['C_scales'].items():
        parts=key.split('_');rank=int(parts[1][1:]);tau=float(parts[2][3:])
        if wheel_donors is None:q,qs=dct_state(surrogate,rank,tau,10,cscales)
        else:q=main[key][ids];qs=cscales
        out[key]=q;out[key+'_active']=np.asarray(qs['q_scale']['active'])
    return out


class FrozenPredictors:
    def __init__(self,subject,availability):
        self.configs={};self.parameters={}
        for config in configurations():
            family=config['family']
            if subject not in availability[family]:continue
            path=P/'fits'/subject/(config['id']+'.json');record=read(path)
            assert record['status']=='NUMERICAL_PASS' and record['configuration']==config
            assert record['production_gate_sha256']==sha(P/'C_PRODUCTION_GATE.json')
            self.configs.setdefault(family,[]).append(config);self.parameters.setdefault(family,[]).append(np.asarray(record['coefficients']))

    def score(self,arrays,filter_y=None,families=None):
        out={}
        for family,configs in self.configs.items():
            if families is not None and family not in families:continue
            masses=[]
            for config,theta in zip(configs,self.parameters[family]):
                model=build_model(arrays,config);mass=model.prebin_logmasses(theta,filter_y if family=='D' else None)
                assert np.isfinite(mass).all();masses.append(mass)
            mixture=logsumexp(np.stack(masses),axis=0)-np.log(len(masses))
            out[family]=dict(LL=float(mixture[:,10:].sum()),unit_bins=int(arrays['y'][:,10:].size))
        return out


def case_logmass(arrays,state,family,ridge,theta):
    model=Model(arrays['x'],arrays['y'],family,ridge=ridge,active=arrays['active'],
        warm=state['warm'],delta=state['delta'],nuisance=state['nuisance_columns'])
    masses=model.prebin_logmasses(np.asarray(theta));assert np.isfinite(masses).all()
    return dict(LL=float(masses[:,state['warm']:].sum()),unit_bins=int(arrays['y'][:,state['warm']:].size))


def score_case(subject,state,arrays):
    models={};failed=[]
    for family in ('B0','B1','B2','B3','B4'):
        path=P/'sensitivity_fits'/subject/state['case']['id']/(family+'.json');record=read(path)
        assert record['C_state_sha256']==sha(P/'sensitivity_states'/subject/(state['case']['id']+'.json'))
        assert record['production_gate_sha256']==sha(P/'C_PRODUCTION_GATE.json')
        if record['status']!='NUMERICAL_PASS':failed.append(family);continue
        models[family]=case_logmass(arrays,state,family,record['configuration']['ridge'],record['coefficients'])
    return models,failed
