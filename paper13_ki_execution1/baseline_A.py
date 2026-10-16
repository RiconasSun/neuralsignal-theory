"""Frozen developmental A-only baseline fitting; no evaluation-source reader."""
import datetime
import hashlib
import json
from pathlib import Path
import numpy as np
from .source import P, ROOT, ALLOCATION, CONFIG, sha, require_access_approval
from .qc import completed_result
from . import models as m
from .features import nuisance
from .fit_engine import fit, ScientificStop, digest_arrays


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')


def schedule():
    # B0 has only unpenalized intercepts: the fixed .1 label adds no ridge term.
    return [(name,ridge,seed) for name in ['B0','B1','B2','B3','B4']
            for ridge in ([.1] if name=='B0' else [.1,1.,10.]) for seed in [11,23,37]]


def approval():
    path=P/'M3_A_APPROVAL.json'
    if not path.is_file():raise PermissionError('Independent M3 A-only implementation approval required')
    a=read(path)
    if not a.get('accepted'):raise PermissionError('M3 A-only implementation not accepted')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('M3 implementation/review hash mismatch')
    for name,digest in read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed M3 source/artifact: '+name)
    return sha(freeze.read_bytes())


def load_m2():
    require_access_approval()
    gate=read(P/'results/M2_GATE.json')
    if gate.get('M2')!='PASS':raise ScientificStop('M2 scientific gate not PASS; no real baseline fit')
    if len(gate['eligible_development'])<8 or len(gate['eligible_final'])<8:raise ScientificStop('M2 coverage contradicts PASS')
    approved=require_access_approval();source_freeze=approved['freeze_sha256'];by_id={}
    for record in ALLOCATION:
        path=P/'results/qc'/(record['mouse_id']+'.json')
        saved=completed_result(path,source_freeze)
        if saved['mouse_id']!=record['mouse_id'] or saved['role']!=record['role'] or saved['partition']!=record['QC_partition']:
            raise ScientificStop('QC identity mismatch')
        attempted=saved['attempts'];units=record['PL_units_numeric_order']
        for index,result in enumerate(attempted):
            if any(result[k]!=units[index][k] for k in ['unit_id','row','label','electrode_row']):
                raise ScientificStop('QC numeric unit order changed')
        first=[{k:r[k] for k in ['unit_id','row','electrode_row','label']} for r in attempted if r['pass']][:8]
        if saved['selected_units']!=first or saved['eligible']!=(len(first)==8):raise ScientificStop('QC admission mismatch')
        by_id[record['mouse_id']]=saved
    for role,key in [('development','eligible_development'),('final','eligible_final')]:
        expected={r['mouse_id'] for r in by_id.values() if r['role']==role and r['eligible']}
        if expected!=set(gate[key]) or len(gate[key])!=len(expected):raise ScientificStop('M2 admission roster mismatch')
    return gate,by_id


def training_state(record,qc):
    # Check role and partition before opening any saved neural-value bundle.
    if record['role']!='development' or record['QC_partition']!='A' or qc['partition']!='A':
        raise PermissionError('Developmental baseline runner permits A only; no C/B/E/D values')
    path=ROOT/qc['training_state_file']
    if sha(path.read_bytes())!=qc['training_state_sha256']:raise ScientificStop('Saved A state hash mismatch')
    with np.load(path,allow_pickle=False) as state:
        y=state['counts'].copy();unit_ids=state['unit_ids'].copy()
    if y.shape!=(60,30,8) or not np.issubdtype(y.dtype,np.integer) or np.any(y<0):raise ScientificStop('Invalid saved A count state')
    if unit_ids.tolist()!=[u['unit_id'] for u in qc['selected_units']]:raise ScientificStop('Saved A selected-unit mismatch')
    epochs=[e for e in record['epochs'] if e['partition']=='A']
    if len(epochs)!=60:raise ScientificStop('Frozen A epoch count mismatch')
    return y,unit_ids,epochs


def save_matching(path,value):
    raw=canonical(value)+b'\n';path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=raw:raise ScientificStop('Saved preprocessing mismatch; no overwrite')
    else:
        with path.open('xb') as f:f.write(raw)
    return sha(raw)


def design_state(y,q,name):
    raw,sources=m.raw_features(y,q,name);scaler=m.fit_scale(raw)
    state={'baseline':name,'mean':scaler['mean'].tolist(),'sd':scaler['sd'].tolist(),
           'zero_sd':(scaler['sd']==0).tolist(),'source_units':sources.tolist(),
           'scaler_rows':'60 A epochs x all30 bins, including warm-up; population SD ddof0',
           'parameters':int(raw.shape[-1]*8)}
    return m.scale(raw,scaler),state


def choose_seed(records):
    if len(records)!=3 or {r['identity']['configuration']['seed'] for r in records}!={11,23,37} or any(r['status']!='PASS' for r in records):
        raise ScientificStop('All three required numerical starts must pass')
    best=min(r['objective'] for r in records)
    return min((r for r in records if r['objective']<=best+1e-12),key=lambda r:r['identity']['configuration']['seed'])


def run():
    source_hash=approval();gate,qcs=load_m2()
    out=P/'results/m3_A';out.mkdir(parents=True,exist_ok=True)
    start=out/'execution_start.json'
    if not start.exists():
        with start.open('x',encoding='utf8') as f:json.dump({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze_sha256':source_hash,'source_partitions':['A'],'required_fits_per_mouse':39},f,indent=2)
    elif read(start)['freeze_sha256']!=source_hash:raise ScientificStop('M3 saved execution source mismatch')
    all_records=[];selected={}
    for record in ALLOCATION:
        if record['mouse_id'] not in gate['eligible_development']:continue
        qc=qcs[record['mouse_id']];y,ids,epochs=training_state(record,qc)
        q=nuisance(record,epochs);designs={};scaler_hashes={}
        for name in ['B0','B1','B2','B3','B4']:
            x,state=design_state(y,q,name);designs[name]=x
            scaler_hashes[name]=save_matching(out/'preprocessing'/(record['mouse_id']+'_'+name+'.json'),state)
        for name,ridge,seed in schedule():
            x=designs[name];configuration={'baseline':name,'ridge':ridge,'seed':seed}
            identity={'real_data':True,'mouse_id':record['mouse_id'],'partition':'A','configuration':configuration,
                'unit_ids_sha256':digest_arrays(ids),'epochs_sha256':sha(canonical(epochs)),
                'scaler_sha256':scaler_hashes[name],'protocol_sha256':CONFIG['protocol_sha256'],
                'A_state_sha256':qc['training_state_sha256'],'QC_source_freeze':qc['source_freeze']}
            path=out/'fits'/record['mouse_id']/f'{name}_ridge{ridge:g}_seed{seed}.json'
            result=fit(path,'GLM',{'y':y,'x':x},ridge,m.glm_initial(x,y,seed),identity=identity,source_hash=source_hash)
            all_records.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path.read_bytes()),
                'mouse_id':record['mouse_id'],'configuration':configuration,'PG':result['PG'],
                'objective':result['objective'],'iterations':result['iterations'],'calls':result['calls']})
            print(json.dumps({'M3_A':record['mouse_id'],**configuration,'status':result['status'],'PG':result['PG']}),flush=True)
        selected[record['mouse_id']]={}
        for name in ['B0','B1','B2','B3','B4']:
            for ridge in ([.1] if name=='B0' else [.1,1.,10.]):
                candidates=[read(out/'fits'/record['mouse_id']/f'{name}_ridge{ridge:g}_seed{seed}.json') for seed in [11,23,37]]
                winner=choose_seed(candidates)
                selected[record['mouse_id']][f'{name}_ridge{ridge:g}']={'seed':winner['identity']['configuration']['seed'],'A_objective':winner['objective']}
    required=39*len(gate['eligible_development'])
    if len(all_records)!=required or required>390:raise ScientificStop('M3 A required-fit accounting mismatch')
    summary={'M3_A_NUMERICS':'PASS','M3_full_stage':'PENDING_B_SELECTION_REVIEW',
        'freeze_sha256':source_hash,'M2_gate_sha256':sha((P/'results/M2_GATE.json').read_bytes()),
        'required':required,'completed':len(all_records),'fits':all_records,'A_selected_seeds':selected,
        'B_E_D_accessed':False,'C_values_loaded_by_this_runner':False}
    save_matching(P/'results/M3_A_GATE.json',summary)
    print(json.dumps({'M3_A_NUMERICS':'PASS','fits':required,'B_E_D_accessed':False}),flush=True)


if __name__=='__main__':run()
