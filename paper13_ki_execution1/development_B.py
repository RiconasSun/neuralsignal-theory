"""Separately reviewed B export/selection after every required A fit passes."""
import json
from pathlib import Path
import h5py
import numpy as np
from . import baseline_A as b
from . import models as m
from .source import P,ROOT,ALLOCATION,SourceReader,node,load_unit,cut_windows,sha
from .qc import durable_record
from .features import nuisance
from .selection import ridge_choice,strongest
from .fit_engine import ScientificStop


def approved():
    path=P/'M3_B_APPROVAL.json'
    if not path.is_file():raise PermissionError('Fresh B export/selection review required before B values')
    a=b.read(path)
    if not a.get('accepted'):raise PermissionError('B export/selection not independently accepted')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('B freeze/review identity mismatch')
    for name,digest in b.read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed B artifact/source: '+name)
    return sha(freeze.read_bytes())


def numerical_gate():
    source_hash=b.approval();gate=b.read(P/'results/M3_A_GATE.json');m2,qcs=b.load_m2()
    if gate.get('M3_A_NUMERICS')!='PASS' or gate.get('freeze_sha256')!=source_hash:raise ScientificStop('All A numerical fits must PASS before B')
    mice=m2['eligible_development'];required=39*len(mice)
    if gate['required']!=required or gate['completed']!=required or len(gate['fits'])!=required:raise ScientificStop('Incomplete A fit denominator')
    records={};seen=set()
    for entry in gate['fits']:
        path=ROOT/entry['path']
        if sha(path.read_bytes())!=entry['sha256']:raise ScientificStop('A fit artifact hash mismatch')
        r=b.read(path);i=r['identity'];c=i['configuration'];key=(i['mouse_id'],c['baseline'],c['ridge'],c['seed'])
        if key in seen or i['mouse_id'] not in mice or i['partition']!='A' or not i['real_data']:raise ScientificStop('A fit identity/duplicate error')
        if r['status']!='PASS' or r['source_hash']!=source_hash or r['PG']>.001 or not np.isfinite(r['objective']):raise ScientificStop('Required A numerical failure')
        for checkpoint in ['initial','intermediate_first_callback','endpoint']:
            d=r['derivatives'][checkpoint]
            if not d['pass'] or d['numerical_gate_step']!=1e-4 or d['AD_error']['max_relative']>1e-5 or d['fixed_FD_error']['max_relative']>1e-5:
                raise ScientificStop('Required independent A certificate failure')
        endpoint=r['derivatives']['endpoint']
        if r['theta']!=endpoint['theta'] or m.pg(r['theta'],endpoint['analytical_gradient'])>.001:raise ScientificStop('Endpoint identity/PG mismatch')
        scaler=P/'results/m3_A/preprocessing'/(i['mouse_id']+'_'+c['baseline']+'.json')
        if sha(scaler.read_bytes())!=i['scaler_sha256']:raise ScientificStop('Frozen A scaler mismatch')
        records[key]=r;seen.add(key)
    expected={(mouse,name,ridge,seed) for mouse in mice for name,ridge,seed in b.schedule()}
    if seen!=expected:raise ScientificStop('Required A candidate roster mismatch')
    return m2,qcs,records


def B_windows(record):
    if record['role']!='development':raise PermissionError('B adapter denies every final mouse')
    windows=[e for e in record['epochs'] if e['partition']=='B']
    if len(windows)!=30:raise ScientificStop('Exactly30frozen Bepochs required')
    return windows


def export_B(record,qc,source_hash):
    windows=B_windows(record)
    if source_hash!=approved():raise PermissionError('B export source identity does not match independent approval')
    gate=b.read(P/'results/M3_A_GATE.json')
    if gate.get('M3_A_NUMERICS')!='PASS' or gate.get('completed')!=gate.get('required') or gate.get('completed')!=390:
        raise ScientificStop('Complete frozen A baseline numerical gate required before B export')
    if qc!=b.read(P/'results/qc'/(record['mouse_id']+'.json')):raise PermissionError('Only canonical reviewed A unit selection may enter B')
    if qc['mouse_id']!=record['mouse_id'] or qc['role']!='development' or qc['partition']!='A' or len(qc['selected_units'])!=8:
        raise PermissionError('Only original8A-selected units may enter B')
    root=P/'results/development_B';root.mkdir(parents=True,exist_ok=True)
    result_path=root/(record['mouse_id']+'.json');journal=root/(record['mouse_id']+'.attempts.jsonl')
    if result_path.exists():
        result=b.read(result_path);rows=[json.loads(x) for x in journal.read_text(encoding='utf8').splitlines()]
        if result['source_freeze']!=source_hash or rows[-1]['event']!='B_EXPORT_COMPLETE' or rows[-1]['result_sha256']!=sha(result_path.read_bytes()):
            raise ScientificStop('Incomplete/changed B export; no implicit repeat')
        if sha((ROOT/result['state_file']).read_bytes())!=result['state_sha256']:raise ScientificStop('B saved state mismatch')
        return result
    with journal.open('xb'):pass
    durable_record(journal,'B_EXPORT_START',mouse_id=record['mouse_id'],source_freeze=source_hash,
                   unit_ids=[x['unit_id'] for x in qc['selected_units']],partition='B')
    state=P/'work/development_B'/(record['mouse_id']+'.npz');state.parent.mkdir(parents=True,exist_ok=True)
    arrays={};values=[];active_unit=None
    try:
        reader=SourceReader(record)
        with h5py.File(reader,'r') as h:
            for j,unit in enumerate(qc['selected_units']):
                durable_record(journal,'B_UNIT_START',mouse_id=record['mouse_id'],unit_id=unit['unit_id'])
                active_unit=unit['unit_id']
                if int(node(h,'/units/id')[unit['row']])!=unit['unit_id']:raise ScientificStop('Selected B unit identity changed')
                times=cut_windows(load_unit(h,unit['row']),windows)
                counts=np.stack([np.histogram(ts,bins=np.arange(31)/10)[0] for ts in times])
                values.append(counts);arrays[f'unit{j}_times']=np.concatenate(times);arrays[f'unit{j}_ends']=np.cumsum([len(ts) for ts in times],dtype=np.int64)
                durable_record(journal,'B_UNIT_COMPLETE',mouse_id=record['mouse_id'],unit_id=unit['unit_id'],counts_sha256=b.digest_arrays(counts))
                active_unit=None
        arrays.update(counts=np.stack(values,axis=-1).astype(np.int64),unit_ids=np.array([u['unit_id'] for u in qc['selected_units']],dtype=np.int64))
        with state.open('xb') as f:np.savez_compressed(f,**arrays)
        result={'mouse_id':record['mouse_id'],'partition':'B','unit_ids':arrays['unit_ids'].tolist(),'epochs_sha256':sha(b.canonical(windows)),
            'source_freeze':source_hash,'A_QC_source_freeze':qc['source_freeze'],'state_file':str(state.relative_to(ROOT)).replace('\\','/'),
            'state_sha256':sha(state.read_bytes()),'QC_or_scaling_on_B':False,'E_D_exported':False}
        with result_path.open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
        durable_record(journal,'B_EXPORT_COMPLETE',mouse_id=record['mouse_id'],result_sha256=sha(result_path.read_bytes()),state_sha256=result['state_sha256'])
        return result
    except Exception as exc:
        if active_unit is not None:durable_record(journal,'B_UNIT_ERROR',mouse_id=record['mouse_id'],unit_id=active_unit,error_type=type(exc).__name__)
        durable_record(journal,'B_EXPORT_ERROR',mouse_id=record['mouse_id'],error_type=type(exc).__name__)
        raise


def score_fixed(y,q,baseline,record,scaler):
    raw,_=m.raw_features(y,q,baseline)
    state={'mean':np.asarray(scaler['mean']),'sd':np.asarray(scaler['sd'])}
    x=m.scale(raw,state);eta=m.glm_predict(record['theta'],x)
    score=m.poisson_scores(y[:,5:],eta[:,5:])
    if not np.isfinite(eta).all() or not np.isfinite(score).all():raise ScientificStop('Nonfinite frozen baseline B score')
    return float(score.mean())


def run():
    source_hash=approved();m2,qcs,records=numerical_gate()
    root=P/'results';journal=root/'M3_B_actions.jsonl';scores={};identities={}
    for record in ALLOCATION:
        mouse=record['mouse_id']
        if mouse not in m2['eligible_development']:continue
        qc=qcs[mouse];export=export_B(record,qc,source_hash)
        with np.load(ROOT/export['state_file'],allow_pickle=False) as state:
            y=state['counts'].copy();ids=state['unit_ids'].copy()
        if y.shape!=(30,30,8) or ids.tolist()!=[u['unit_id'] for u in qc['selected_units']]:raise ScientificStop('Frozen B bundle identity/shape mismatch')
        q=nuisance(record,B_windows(record));scores[mouse]={};identities[mouse]={}
        for name in ['B0','B1','B2','B3','B4']:
            scaler=b.read(P/'results/m3_A/preprocessing'/(mouse+'_'+name+'.json'))
            for ridge in ([.1] if name=='B0' else [.1,1.,10.]):
                candidates=[records[(mouse,name,ridge,seed)] for seed in [11,23,37]]
                chosen=b.choose_seed(candidates);key=f'{name}_ridge{ridge:g}'
                durable_record(journal,'B_SCORE_START',mouse_id=mouse,configuration=key,A_selected_seed=chosen['identity']['configuration']['seed'])
                try:score=score_fixed(y,q,name,chosen,scaler)
                except Exception as exc:
                    durable_record(journal,'B_SCORE_ERROR',mouse_id=mouse,configuration=key,error_type=type(exc).__name__);raise
                scores[mouse][key]=score
                identities[mouse][key]={'A_selected_seed':chosen['identity']['configuration']['seed'],'A_objective':chosen['objective'],
                    'A_full_request_sha256':chosen['full_request_sha256'],'A_scaler_sha256':chosen['identity']['scaler_sha256'],'B_state_sha256':export['state_sha256'],'nominal_unit_bins':6000}
                durable_record(journal,'B_SCORE_COMPLETE',mouse_id=mouse,configuration=key,score_nats_per_unit_bin=score,nominal_unit_bins=6000)
        print(json.dumps({'development_B_scored':mouse,'configurations':13,'QC_or_scaling_on_B':False}),flush=True)
    mice=sorted(m2['eligible_development']);selection={};chosen_scores={}
    for name in ['B0','B1','B2','B3','B4']:
        ridges=[.1] if name=='B0' else [.1,1.,10.]
        matrix=np.array([[scores[mouse][f'{name}_ridge{ridge:g}'] for ridge in ridges] for mouse in mice])
        selected=ridge_choice(matrix,ridges);selection[name]=selected
        chosen_scores[name]=matrix[:,selected['selected_index']]
    star=strongest(chosen_scores)
    result={'M3':'PASS','B_only_selection':True,'source_freeze':source_hash,'mouse_order':mice,
        'all_candidate_scores':scores,'score_identities':identities,'selected_baselines':selection,'strongest_baseline':star,
        'all390A_numerical_fits_required':True,'scalers_fitted_on_A_only':True,'C_E_D_scores_used':False,
        'science':'Development selection exploratory; no final validation or dynamical family claim'}
    b.save_matching(P/'results/M3_BASELINE_SELECTION.json',result)
    print(json.dumps({'M3':'PASS','B_star':star['B_star'],'B4_ridge':selection['B4']['selected_ridge'],'D_outcomes_accessed':False}),flush=True)


if __name__=='__main__':run()
