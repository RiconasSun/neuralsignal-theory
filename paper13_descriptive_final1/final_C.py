"""From-scratch frozen C calibration. No raw source or evaluation array loader."""
import json
import numpy as np
from paper13_ki_execution1.source import ROOT,ALLOCATION,CONFIG,sha
from .common import P,OLD,policies
from paper13_ki_execution1 import baseline_A as b
from paper13_ki_execution1 import models as m
from paper13_ki_execution1.features import nuisance
from paper13_ki_execution1.fit_engine import fit,ScientificStop,digest_arrays
from paper13_ki_execution1.qc import completed_result,durable_record
from paper13_ki_execution1 import sensitivity_plan

SEEDS=[11,23,37]


def approved():
    path=P/'FINAL_C_APPROVAL.json'
    if not path.is_file():raise PermissionError('Independent frozen final C-only review required')
    a=b.read(path)
    if not a.get('accepted'):raise PermissionError('Final C path not accepted')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('Final C source/review mismatch')
    for name,digest in b.read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed final C artifact: '+name)
    return sha(freeze.read_bytes())


def load_C(record,qc):
    if record['role']!='final' or record['QC_partition']!='C' or qc['role']!='final' or qc['partition']!='C' or qc['mouse_id']!=record['mouse_id']:
        raise PermissionError('C worker permits only original final C states')
    path=ROOT/qc['training_state_file']
    if sha(path.read_bytes())!=qc['training_state_sha256']:raise ScientificStop('C training state hash mismatch')
    with np.load(path,allow_pickle=False) as arrays:y=arrays['counts'].copy();ids=arrays['unit_ids'].copy()
    epochs=[e for e in record['epochs'] if e['partition']=='C']
    if y.shape!=(60,30,8) or len(epochs)!=60 or not np.issubdtype(y.dtype,np.integer) or np.any(y<0):raise ScientificStop('Full original60C/8unit count state required')
    if ids.tolist()!=[u['unit_id'] for u in qc['selected_units']]:raise ScientificStop('C unit identity mismatch')
    return y,ids,epochs


def design(y,q,name):
    raw,sources=m.raw_features(y,q,name);scaler=m.fit_scale(raw)
    state={**{k:v.tolist() for k,v in scaler.items()},'baseline':name,'zero_sd':(scaler['sd']==0).tolist(),
        'source_units':sources.tolist(),'parameters':raw.shape[-1]*8,'scaler_rows':'60 C epochs x all30 bins including warm-up; ddof0'}
    return m.scale(raw,scaler),state


def fit_mouse(record,qc,m3,m4,source,root,journal):
    mouse=record['mouse_id'];y,ids,epochs=load_C(record,qc);q=nuisance(record,epochs);fit_rows=[]
    common={'real_data':True,'mouse_id':mouse,'partition':'C','role':'final','unit_ids_sha256':digest_arrays(ids),
        'epochs_sha256':sha(b.canonical(epochs)),'C_state_sha256':qc['training_state_sha256'],
        'protocol_sha256':CONFIG['protocol_sha256'],'amendment_sha256':sha((P/'PRE_D_STOPPING_RULE_AMENDMENT.json').read_bytes()),'QC_source_freeze':qc['source_freeze']}
    bundle={'mouse_id':mouse,'training_partition':'C','training_state_sha256':qc['training_state_sha256'],'units':qc['selected_units'],
        'unit_QC':{str(a['unit_id']):a for a in qc['attempts'] if a['pass']},'baseline_thetas':{},'baseline_scalers':{},
        'source_fit_requests':{},'all_C_fit_requests':{},'Bstar':m3['strongest_baseline']['B_star']}
    def execute(key,kind,data,ridge,initial,identity,**kwargs):
        path=root/'fits'/mouse/(key+'.json');durable_record(journal,'C_FIT_START',mouse_id=mouse,configuration=identity['configuration'])
        result=fit(path,kind,data,ridge,initial,identity=identity,source_hash=source,**kwargs)
        fit_rows.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path.read_bytes()),'mouse_id':mouse,
            'configuration':identity['configuration'],'PG':result['PG'],'objective':result['objective'],'iterations':result['iterations'],'calls':result['calls']})
        bundle['all_C_fit_requests'][key]=result['full_request_sha256']
        durable_record(journal,'C_FIT_COMPLETE',mouse_id=mouse,configuration=identity['configuration'],PG=result['PG'])
        print(json.dumps({'final_C':mouse,**identity['configuration'],'PG':result['PG'],'status':result['status']}),flush=True)
        return result
    for name in ['B0','B1','B2','B3','B4']:
        ridge=m3['selected_baselines'][name]['selected_ridge'];x,state=design(y,q,name)
        scaler_hash=b.save_matching(root/'preprocessing'/mouse/(name+'.json'),state)
        records=[]
        for seed in SEEDS:
            configuration={'baseline':name,'ridge':ridge,'seed':seed}
            records.append(execute(f'{name}_ridge{ridge:g}_seed{seed}','GLM',{'y':y,'x':x},ridge,m.glm_initial(x,y,seed),
                {**common,'configuration':configuration,'scaler_sha256':scaler_hash}))
        chosen=b.choose_seed(records);bundle['baseline_thetas'][name]=chosen['theta'];bundle['baseline_scalers'][name]=state
        bundle['source_fit_requests'][name]=chosen['full_request_sha256']
    s=bundle['baseline_scalers']['B4'];raw,_=m.raw_features(y,q,'B4')
    offset=m.glm_predict(bundle['baseline_thetas']['B4'],m.scale(raw,{k:np.asarray(s[k]) for k in ['mean','sd']}))
    common.update(B4_C_full_request_sha256=bundle['source_fit_requests']['B4'],B4_C_offset_sha256=digest_arrays(offset),
        B4_scaler_sha256=sha(b.canonical(s)+b'\n'))
    for name,configuration in [('D',m4['D_selection']['selected_configuration']),('S',{'p':.5,'ridge':m4['S_selection']['selected_ridge']})]:
        p=configuration['p'];ridge=configuration['ridge'];records=[]
        for seed in SEEDS:
            config={'family':name,'p':p,'ridge':ridge,'seed':seed}
            records.append(execute(f'{name}_p{p:g}_ridge{ridge:g}_seed{seed}','HMM',{'y':y},ridge,np.random.default_rng(seed).normal(0,.05,16),
                {**common,'configuration':config,'scaler_sha256':common['B4_scaler_sha256']},p=p,offset=offset))
        chosen=b.choose_seed(records)
        bundle[name]={'theta':chosen['theta'],'p':p,'ridge':ridge,'C_selected_seed':chosen['identity']['configuration']['seed'],
            'reporting_state_order':np.argsort(np.asarray(chosen['theta']).reshape(2,8).sum(axis=1),kind='stable').tolist()}
        bundle['source_fit_requests'][name]=chosen['full_request_sha256']
    configuration=m4['C_selection']['selected_configuration'];tau=configuration['tau'];seed=configuration['seed'];ridge=configuration['ridge']
    x,state=m.continuous_features(y,tau,seed);state={k:v.tolist() for k,v in state.items()}
    scaler_hash=b.save_matching(root/'preprocessing'/mouse/'C_state.json',state)
    chosen=execute(f'C_tau{tau[0]:g}-{tau[1]:g}_ridge{ridge:g}_seed{seed}','C',{'y':y,'x':x},ridge,np.zeros(16),
        {**common,'configuration':{'family':'C','tau':tau,'ridge':ridge,'seed':seed},'scaler_sha256':scaler_hash,
         'fixed_Q_sha256':digest_arrays(np.asarray(state['Q']))},offset=offset)
    bundle['C']={'theta':chosen['theta'],'tau':tau,'seed':seed,'ridge':ridge,'state':state};bundle['source_fit_requests']['C']=chosen['full_request_sha256']
    bundle['sensitivity_unit_masks']=sensitivity_plan.unit_panels(bundle);bundle['sensitivity_metadata']=sensitivity_plan.metadata(record)
    bundle['original_epochs']=record['epochs'];bundle['source_hash']=source;bundle['common_C_identity']=common
    if len(fit_rows)!=22:raise ScientificStop('Exact22required final fits per mouse')
    path=root/'models'/(mouse+'.json');digest=b.save_matching(path,bundle)
    return fit_rows,{'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':digest,'required_fits':22,'C_state_sha256':qc['training_state_sha256']}


def run():
    source=approved();m2,m3,m4=policies();root=P/'results/final_C';root.mkdir(parents=True,exist_ok=True);journal=root/'actions.jsonl'
    with journal.open('xb'):pass
    durable_record(journal,'FINAL_C_START',source_freeze=source,required_fits_per_mouse=22,mouse_order=sorted(m2['eligible_final']))
    rows=[];models={};active=None
    try:
        for record in ALLOCATION:
            mouse=record['mouse_id']
            if mouse not in m2['eligible_final']:continue
            active=mouse
            if record['role']!='final':raise PermissionError('Final admission includes non-final mouse')
            path=OLD/'results/qc'/(mouse+'.json');qc=b.read(path);qc=completed_result(path,qc['source_freeze'])
            new_rows,model=fit_mouse(record,qc,m3,m4,source,root,journal);rows.extend(new_rows);models[mouse]=model
            durable_record(journal,'FINAL_C_MOUSE_COMPLETE',mouse_id=mouse,model_sha256=model['sha256'],completed_required_fits=22)
        required=22*len(m2['eligible_final'])
        if len(rows)!=required or required>198 or set(models)!=set(m2['eligible_final']):raise ScientificStop('Final C admission/budget/state mismatch')
        result={'FINAL_C_NUMERICS':'PASS','source_freeze':source,'required':required,'completed':len(rows),'fits':rows,'models':models,
            'mouse_order':sorted(models),'D_outcomes_accessed':False,'development_coefficients_transferred':False,
            'strict_recent_event_coverage':'FAIL6vs8_RETAINED','associated_broad_claim':'INCONCLUSIVE_LOCKED_BY_PRE_D_AMENDMENT'}
        b.save_matching(P/'results/FINAL_C_GATE.json',result);durable_record(journal,'FINAL_C_COMPLETE',required=required,completed=len(rows))
        print(json.dumps({'FINAL_C_NUMERICS':'PASS','fits':required,'D_outcomes_accessed':False}),flush=True)
    except Exception as exc:
        durable_record(journal,'FINAL_C_ERROR',mouse_id=active,error_type=type(exc).__name__,error=str(exc))
        b.save_matching(P/'results/FINAL_C_GATE.json',{'FINAL_C_NUMERICS':'FAIL','source_freeze':source,'mouse_id':active,'error_type':type(exc).__name__,'error':str(exc),'D_outcomes_accessed':False,'retry_authorized':False})
        raise


if __name__=='__main__':run()
