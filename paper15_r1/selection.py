"""Conditional Development B-only global selection; no Final access or E tuning."""
from .source import load_json
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from .source import P, R, dump
from .reader import project_A
from .metadata_access import local_path
from .features import observed_arrays,nuisance,design,dct_state
from .training import admitted,sha,configurations,build_model,verify_completed_attempt


def groups(configs=None):
    result={}
    for c in configurations() if configs is None else configs:
        key=c['id'].rsplit('_s',1)[0] if c['family'] in ('D','S') else c['id']
        result.setdefault(key,[]).append(c)
    return result


def require_stage(role):
    if role not in ('B','E'):raise PermissionError('Only explicitly staged Development B/E permitted')
    plan=load_json((P/'A_FIT_PLAN.json').read_text(encoding='utf8'))
    assert plan['subjects']==admitted() and plan['configurations']==configurations()
    for name in ['BASELINE_ATTEMPTS_COMPLETE.json','DYNAMIC_ATTEMPTS_COMPLETE.json']:
        marker=load_json((P/'results'/name).read_text(encoding='utf8'))
        baseline=name.startswith('BASELINE')
        expected={s+'/'+c['id'] for s in plan['subjects'] for c in plan['configurations'] if c['family'].startswith('B')==baseline}
        assert set(marker['attempt_hashes'])==expected
        assert marker['attempted']==marker['completed']==len(expected)
        for item,h in marker['attempt_hashes'].items():
            assert sha(P/'fits'/(item+'.json'))==h
        if baseline:assert marker['PRIMARY_BASELINE_NUMERICAL_GATE']
    if role=='E':
        selection=load_json((P/'SELECTION_FREEZE.json').read_text(encoding='utf8'))
        assert selection['subjects']==plan['subjects']
        assert selection['selected']['B1'] and selection['selected']['B4']
        assert selection['candidates_sha256']==sha(P/'results/B_CANDIDATE_SCORES.json')
        candidates=load_json((P/'results/B_CANDIDATE_SCORES.json').read_text(encoding='utf8'))
        for family,cid in selection['selected'].items():
            if cid is not None:
                match=next(x for x in candidates if x['id']==cid)
                assert match['available'] and match['configurations'][0]['family']==family
        e_gate=load_json((P/'E_EXPLORATORY_GATE.json').read_text(encoding='utf8'))
        assert e_gate['approved_for_one_frozen_E_batch']
        required={'SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json','models.py','features.py','training.py','selection.py'}
        assert required<=set(e_gate['hashes']), 'E gate must bind exact B winner/results and production sources'
        for rel,h in e_gate['hashes'].items():assert sha(P/rel)==h


def extract_role(subject,role,units=None,delta=.05,warmup=.5,history=.5,rich=False,metadata=None,scales=None,Cstates=None):
    require_stage(role)
    if subject not in admitted():raise PermissionError('Not an admitted Development mouse')
    source=load_json((P/'SOURCE_FILE_FREEZE.json').read_text(encoding='utf8'))
    row=next(x for x in source['subjects'] if x['subject']==subject)
    assert row['allocation']=='DEVELOPMENT'
    state=load_json((P/'metadata'/(subject+'_task.json')).read_text(encoding='utf8')) if metadata is None else metadata
    prep=load_json((P/'states'/(subject+'_A_PREPROCESSING.json')).read_text(encoding='utf8'))
    units=prep['units'] if units is None else units
    qc=load_json((P/'results'/(subject+'_A_QC.json')).read_text(encoding='utf8'))
    paths={}
    for f in row['files']:
        if f['role'] not in ('times','clusters'):continue
        path=R/'paper15_m0/work/native'/row['eid']/Path(f['key']).name if next(x for x in qc['files'] if x['key']==f['key'])['reuse_M0'] else P/'work/neural'/row['eid']/Path(f['key']).name
        rec=next(x for x in qc['files'] if x['key']==f['key'])
        if 'original_path' in rec:path=R/rec['original_path']
        assert sha(path)==rec['sha256']
        paths[f['role']]=path
    lo,hi=state['result']['partitions'][role];tr=state['trials']
    times,labels=project_A(np.load(paths['times'],mmap_mode='r',allow_pickle=False),np.load(paths['clusters'],mmap_mode='r',allow_pickle=False),
        tr[lo]['intervals_0'],tr[hi-1]['intervals_1'],len(state['native_uuid_list']),state['result']['recording_sync_support'],state['result']['fs'])
    ids=np.flatnonzero(np.asarray(state['valid'])&(np.asarray(state['roles'])==role))
    stimuli=np.array([tr[i]['stimOn_times'] for i in ids]);y,h,b,epoch,warm=observed_arrays(times,labels,units,stimuli,delta,warmup,history)
    wheelpaths={f['role']:local_path(row,f) for f in row['files'] if f['role'] in ('wheel_times','wheel_position')}
    wt=np.load(wheelpaths['wheel_times'],allow_pickle=False);wp=np.load(wheelpaths['wheel_position'],allow_pickle=False)
    nx=nuisance(tr,ids,b,stimuli-.5,wt,wp,rich)
    selected_scale=prep['scales'] if scales is None else scales
    x,_,active=design(nx,h,warm,selected_scale)
    arrays=dict(x=x,y=y,active=active,trial_ids=ids)
    cs=prep['C_scales'] if Cstates is None else Cstates
    if delta==.05 and warmup==.5 and len(units)==8 and not rich:
        for rank in (1,2):
            for tau in (.1,.25):
                key=f'C_r{rank}_tau{tau}';q,qs=dct_state(y,rank,tau,warm,cs[key]);arrays[key]=q;arrays[key+'_active']=np.asarray(qs['q_scale']['active'])
    return arrays,dict(subject=subject,role=role,trial_ids=ids.tolist(),units=list(units),A_preprocessing_sha256=sha(P/'states'/(subject+'_A_PREPROCESSING.json')),
        source_files=[dict(role=f['role'],sha256=f['sha256']) for f in qc['files']],role_only_export=True,Final_access=False)


def nominal(config,u=8):
    family=config['family'];base=u*(38+4*u)
    if family=='B0':return u
    if family=='B1':return 38*u
    if family=='B2':return 42*u
    if family=='B3':return (38+4*(u-1))*u
    if family=='B4':return base
    if family=='C':return base+u*config['rank']
    if family=='D':return base+(config['k']-1)*u+config['k']*(config['k']-1)+config['k']-1
    return base+(config['k']-1)*u+config['k']-1


def tie_key(candidate):
    c=candidate['configurations'][0]
    return (nominal(c),-c['ridge'],c.get('k',c.get('rank',0)),c.get('tau',0),candidate['id'])


def choose(candidates):
    candidates=[x for x in candidates if x['available']]
    if not candidates:return None
    best=max(x['equal_mouse_LL_per_unit_bin'] for x in candidates)
    return min((x for x in candidates if best-x['equal_mouse_LL_per_unit_bin']<=1e-6),key=tie_key)


def score_group(arrays,subject,configs):
    masses=[];fits=[]
    for c in configs:
        path=P/'fits'/subject/(c['id']+'.json');record=load_json(path.read_text(encoding='utf8'))
        verify_completed_attempt(record,c,sha(P/'PRODUCTION_GATE.json'));assert record['status']=='NUMERICAL_PASS'
        model=build_model(arrays,c);theta=np.asarray(record['coefficients']);assert model.size==len(theta)
        mass=model.prebin_logmasses(theta);assert np.isfinite(mass).all();masses.append(mass);fits.append(sha(path))
    mixture=logsumexp(np.stack(masses),axis=0)-np.log(len(masses))
    ll=float(mixture[:,10:].sum());q=int(arrays['y'][:,10:].size)
    return dict(LL=ll,unit_bins=q,LL_per_unit_bin=ll/q,fit_hashes=fits,seed_logmass_ensemble=len(masses))


def select():
    require_stage('B');outpath=P/'SELECTION_FREEZE.json';assert not outpath.exists(),'No repeat B tuning'
    candidates=[];subjects=admitted();config_groups=groups()
    data={}
    for subject in subjects:
        arrays,receipt=extract_role(subject,'B');path=P/'work/B_exports'/(subject+'.npz');path.parent.mkdir(parents=True,exist_ok=True)
        assert not path.exists();np.savez_compressed(path,**arrays)
        receipt['export_sha256']=sha(path);dump(P/'results'/(subject+'_B_EXPORT.json'),receipt);data[subject]=arrays
    for cid,configs in config_groups.items():
        valid=all(load_json((P/'fits'/s/(c['id']+'.json')).read_text(encoding='utf8'))['status']=='NUMERICAL_PASS' for s in subjects for c in configs)
        entry=dict(id=cid,configurations=configs,available=valid,mouse_scores=[],nominal_parameters=nominal(configs[0]))
        if valid:
            for subject in subjects:entry['mouse_scores'].append(dict(subject=subject,**score_group(data[subject],subject,configs)))
            entry['equal_mouse_LL_per_unit_bin']=float(np.mean([x['LL_per_unit_bin'] for x in entry['mouse_scores']]))
        candidates.append(entry)
    selected={}
    for family in ['B0','B1','B2','B3','B4','D','C']:
        winner=choose([x for x in candidates if x['configurations'][0]['family']==family]);selected[family]=winner['id'] if winner else None
    d=next((x for x in candidates if x['id']==selected['D']),None)
    s=choose([x for x in candidates if x['configurations'][0]['family']=='S' and d is not None and x['configurations'][0]['k']==d['configurations'][0]['k']+1])
    selected['S']=s['id'] if s else None
    assert selected['B1'] and selected['B4'],'No global valid primary candidate: STOP before E'
    dump(P/'results/B_CANDIDATE_SCORES.json',candidates)
    dump(outpath,dict(frozen_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        subjects=subjects,selected=selected,candidates_sha256=sha(P/'results/B_CANDIDATE_SCORES.json'),
        rule='Equal-mouse B LL/unit-bin, within1e-6 ties fewer nominal params,stronger ridge,smallerK/r,tau,lexicalID',
        C_states_fit_on='A_ONLY',E_neural_access=False,Final_neural_access=False,
        source_hashes={n:sha(P/n) for n in ['models.py','independent_ad.py','features.py','training.py','selection.py','PRODUCTION_GATE.json']}))
    print(json.dumps(selected,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['select']);ap.parse_args();select()
