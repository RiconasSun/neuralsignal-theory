"""Frozen Development E batch building blocks; no optimization or Final reader."""
from .source import load_json
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from .source import P,R
from .training import admitted,sha,build_model,verify_completed_attempt
from .selection import require_stage
from .reader import project_A
from .features import observed_arrays,nuisance,design,dct_state,held
from .metadata_access import local_path
from .controls import thin_role,history_from_microbins
from .models import Model


def read_json(path):
    return load_json(path.read_text(encoding='utf8'))


def source_state(subject):
    if subject not in admitted():raise PermissionError('Only admitted Development animals')
    row=next(x for x in read_json(P/'SOURCE_FILE_FREEZE.json')['subjects'] if x['subject']==subject)
    assert row['allocation']=='DEVELOPMENT'
    return row,read_json(P/'metadata'/(subject+'_task.json'))


def wheel(row):
    paths={f['role']:local_path(row,f) for f in row['files'] if f['role'] in ('wheel_times','wheel_position')}
    return tuple(np.load(paths[k],allow_pickle=False) for k in ('wheel_times','wheel_position'))


def raw_E(subject):
    require_stage('E');row,state=source_state(subject)
    qc=read_json(P/'results'/(subject+'_A_QC.json'));paths={}
    for f in row['files']:
        if f['role'] not in ('times','clusters'):continue
        receipt=next(x for x in qc['files'] if x['key']==f['key'])
        path=R/'paper15_m0/work/native'/row['eid']/Path(f['key']).name if receipt['reuse_M0'] else P/'work/neural'/row['eid']/Path(f['key']).name
        if 'original_path' in receipt:path=R/receipt['original_path']
        assert sha(path)==receipt['sha256'];paths[f['role']]=path
    start,stop=state['result']['partitions']['E'];tr=state['trials']
    times,labels=project_A(np.load(paths['times'],mmap_mode='r',allow_pickle=False),np.load(paths['clusters'],mmap_mode='r',allow_pickle=False),
        tr[start]['intervals_0'],tr[stop-1]['intervals_1'],len(state['native_uuid_list']),state['result']['recording_sync_support'],state['result']['fs'])
    return times,labels


def case_arrays(subject,case_state,times,labels,wt,wp):
    assert case_state['subject']==subject and case_state['status']=='A_PREPROCESSING_SEALED'
    case=case_state['case'];metadata=case_state['metadata'];units=case_state['units']
    thinning=None
    if case.get('thin'):
        qc=read_json(P/'results'/(subject+'_A_QC.json'));metrics={x['cluster_id']:x for x in qc['physiology']}
        times,labels,thinning=thin_role(times,labels,units,[metadata['native_uuid_list'][u] for u in units],
            [metrics[u]['A_rate_Hz'] for u in units],subject,'E')
    ids=np.flatnonzero(np.asarray(metadata['valid'])&(np.asarray(metadata['roles'])=='E'))
    stimuli=np.array([metadata['trials'][i]['stimOn_times'] for i in ids])
    y,h,b,_,warm=observed_arrays(times,labels,units,stimuli,case_state['delta'],case.get('warmup',.5),case.get('history',.5))
    nx=nuisance(metadata['trials'],ids,b,stimuli-.5,wt,wp,case.get('rich',False))
    x,_,active=design(nx,h,warm,case_state['scales'])
    assert warm==case_state['warm'] and active.tolist()==case_state['active']
    return dict(x=x,y=y,active=active,trial_ids=ids),thinning


def pre_epoch_wheel(metadata,ids,wt,wp):
    epoch=np.array([metadata['trials'][int(i)]['stimOn_times']-.5 for i in ids])
    a,_=held(wt,wp,epoch);b,_=held(wt,wp,epoch-.5)
    return np.abs(a-b)


def control_arrays(main,prep,surrogate,indices,wheel_donors=None):
    """Original targets/task, donor past counts; only N3 replaces wheel inputs."""
    ids=np.asarray(indices,int);x=main['x'][ids].copy();y=main['y'][ids]
    assert surrogate.shape==y.shape
    if wheel_donors is None:
        from .features import scale
        raw_h=history_from_microbins(surrogate)
        state={k:prep['scales'][k][37:] for k in ('mean','sd','active')}
        x[:,:,38:]=scale(raw_h,state)
    else:
        donors=np.asarray(wheel_donors,int)
        assert len(donors)==len(ids)
        # 1-based nuisance columns24..37 -> design indices24..37 inclusive.
        x[:,:,24:38]=main['x'][donors,:,24:38]
    out=dict(x=x,y=y,active=main['active'],trial_ids=main['trial_ids'][ids])
    for rank in (1,2):
        for tau in (.1,.25):
            key=f'C_r{rank}_tau{tau}'
            if wheel_donors is None:q,qs=dct_state(surrogate,rank,tau,10,prep['C_scales'][key])
            else:q=main[key][ids];qs=prep['C_scales'][key]
            out[key]=q;out[key+'_active']=np.asarray(qs['q_scale']['active'])
    return out


class FrozenPredictors:
    def __init__(self,subject,selection,candidates):
        self.parameters={};self.configs={}
        for family,cid in selection['selected'].items():
            if cid is None:continue
            entry=next(x for x in candidates if x['id']==cid);assert entry['available']
            self.configs[family]=entry['configurations'];self.parameters[family]=[]
            for config in self.configs[family]:
                path=P/'fits'/subject/(config['id']+'.json');record=read_json(path)
                verify_completed_attempt(record,config,sha(P/'PRODUCTION_GATE.json'));assert record['status']=='NUMERICAL_PASS'
                self.parameters[family].append(np.asarray(record['coefficients']))

    def score(self,arrays,filter_y=None,families=None):
        out={}
        for family,configs in self.configs.items():
            if families is not None and family not in families:continue
            masses=[]
            for config,theta in zip(configs,self.parameters[family]):
                model=build_model(arrays,config)
                mass=model.prebin_logmasses(theta,filter_y if family=='D' else None)
                assert np.isfinite(mass).all();masses.append(mass)
            mixture=logsumexp(np.stack(masses),axis=0)-np.log(len(masses))
            out[family]=dict(LL=float(mixture[:,10:].sum()),unit_bins=int(arrays['y'][:,10:].size))
        return out


def score_case(subject,state,arrays):
    out={};failures=[]
    for family in ['B0','B1','B2','B3','B4']:
        path=P/'sensitivity_fits'/subject/state['case']['id']/(family+'.json');record=read_json(path)
        assert record['plan_item']['state_sha256']==sha(P/'sensitivity_states'/subject/(state['case']['id']+'.json'))
        assert record['sensitivity_gate_sha256']==sha(P/'SENSITIVITY_GATE.json')
        if record['status']!='NUMERICAL_PASS':failures.append(family);continue
        model=Model(arrays['x'],arrays['y'],family,ridge=record['plan_item']['ridge'],active=arrays['active'],
            warm=state['warm'],delta=state['delta'],nuisance=state['nuisance_columns'])
        mass=model.prebin_logmasses(np.asarray(record['coefficients']))
        assert np.isfinite(mass).all()
        out[family]=dict(LL=float(mass[:,state['warm']:].sum()),unit_bins=int(arrays['y'][:,state['warm']:].size))
    return out,failures
