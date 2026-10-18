"""Frozen selected-policy C calibration; no Final search or D data path."""
import argparse
import datetime
import json
import os
import time
import numpy as np
from scipy.optimize import minimize
from .source import R,P,E,read,dump,sha,frozen_definitions,source_rows
from .metadata_access import local_path
from .features import observed_arrays,nuisance,design,dct_state
from .models import Model,pg
from .independent_ad import coordinate_check

SOLVER=dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)


def admitted():
    gate=read(P/'results/FINAL_C_QC_GATE.json')
    assert gate['C_QC_completed'] and gate['descriptive_cohort_eligible']
    return [r['subject'] for r in gate['subjects'] if r['admitted']]


def configurations():
    frozen_definitions()
    selection=read(R/'paper15_r1/SELECTION_FREEZE.json')
    path=R/'paper15_r1/results/B_CANDIDATE_SCORES.json';assert sha(path)==selection['candidates_sha256']
    candidates=read(path);out=[]
    for family in ['B0','B1','B2','B3','B4','C','D','S']:
        cid=selection['selected'][family]
        if cid is None:continue
        row=next(r for r in candidates if r['id']==cid)
        assert row['available'] and all(c['family']==family for c in row['configurations'])
        out.extend(row['configurations'])
    assert len(out)==12 and [c['seed'] for c in out if c['family']=='D']==[11,23,37]
    assert [c['seed'] for c in out if c['family']=='S']==[11,23,37]
    return out


def c_export(subject):
    if subject not in admitted():raise PermissionError('Not admitted C mouse')
    qc=read(P/'results'/(subject+'_C_QC.json'))
    path=P/'work/C_exports'/(subject+'.npz');assert sha(path)==qc['C_export_sha256']
    with np.load(path,allow_pickle=False) as f:return {k:f[k] for k in f.files}


def wheel(row):
    paths={f['role']:local_path(row,f) for f in row['files'] if f['role'] in ('wheel_times','wheel_position')}
    return tuple(np.load(paths[k],allow_pickle=False) for k in ('wheel_times','wheel_position'))


def prepare():
    assert not (P/'results/C_FEATURE_PREPARATION.json').exists()
    records=[]
    for subject in admitted():
        state=read(P/'metadata'/(subject+'_task.json'));qc=read(P/'results'/(subject+'_C_QC.json'))
        export=c_export(subject);units=qc['selected_unit_ids'];ids=export['trial_ids']
        stimuli=np.array([state['trials'][i]['stimOn_times'] for i in ids])
        y,h,b,epoch,warm=observed_arrays(export['times'],export['labels'],units,stimuli)
        row=next(r for r in source_rows() if r['subject']==subject);wt,wp=wheel(row)
        raw=nuisance(state['trials'],ids,b,epoch,wt,wp);x,scales,active=design(raw,h,warm)
        arrays=dict(x=x,y=y,active=active,trial_ids=ids);cscales={}
        # Only the already selected rank/tau is calibrated; no additional policy is chosen.
        config=next(c for c in configurations() if c['family']=='C')
        key=f"C_r{config['rank']}_tau{config['tau']}"
        q,qs=dct_state(y,config['rank'],config['tau'],warm)
        arrays[key]=q;arrays[key+'_active']=np.asarray(qs['q_scale']['active']);cscales[key]=qs
        target=P/'work/C_features'/(subject+'.npz');target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists()
        np.savez_compressed(target,**arrays)
        modelstate=dict(subject=subject,role='C',units=units,unit_uuids=qc['selected_unit_uuids'],trial_ids=ids.tolist(),
            scales=scales,C_scales=cscales,active=active.tolist(),warm_bins=warm,delta=.05,
            actual_score_population_bins=int(len(ids)*10),actual_score_unit_bins=int(len(ids)*80),
            QC_sha256=sha(P/'results'/(subject+'_C_QC.json')),task_sha256=sha(P/'metadata'/(subject+'_task.json')),
            C_export_sha256=qc['C_export_sha256'],C_features_sha256=sha(target),
            M1_freeze_sha256=sha(R/'paper15_m1/PROTOCOL_FREEZE.json'),
            B_selection_sha256=sha(R/'paper15_r1/SELECTION_FREEZE.json'),
            model_parameters_from_Development=False,D_neural_scientific_access=False)
        path=P/'states'/(subject+'_C_PREPROCESSING.json');assert not path.exists();dump(path,modelstate)
        records.append(dict(subject=subject,state_sha256=sha(path),epochs=len(ids),unit_bins=len(ids)*80))
        print(subject,'C features/scales frozen',len(ids),'epochs',flush=True)
    dump(P/'results/C_FEATURE_PREPARATION.json',dict(subjects=records,real_fits=0,D_neural_access=False))


def build_model(arrays,config):
    x=arrays['x'];active=arrays['active']
    if config['family']=='C':
        key=f"C_r{config['rank']}_tau{config['tau']}"
        x=np.concatenate([x,arrays[key]],axis=-1);active=np.r_[active,arrays[key+'_active']]
    return Model(x,arrays['y'],config['family'],ridge=config['ridge'],k=config.get('k',2),active=active)


def register():
    path=P/'C_FIT_PLAN.json';assert not path.exists()
    subjects=admitted();configs=configurations()
    dump(path,dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        subjects=subjects,configurations=configs,per_mouse=12,expected_attempts=12*len(subjects),maximum_main=96,
        maximum_sensitivity=440,max_retries=0,solver=SOLVER,
        historical359=359,R1_corrective1135=1135,cumulative_before_Final=1494,original_M1_aggregate_ceiling=1928,
        current_owner_Final_caps=dict(main=96,sensitivity=440),full_historical_maximum=2030,
        retrospective_original_aggregate_compliance=False,cohort_current_main_cap=12*len(subjects),
        selection_sha256=sha(R/'paper15_r1/SELECTION_FREEZE.json'),
        state_hashes={s:sha(P/'states'/(s+'_C_PREPROCESSING.json')) for s in subjects},
        D_neural_fit_data=False,Development_coefficients_reused=False,
        order='All five baseline families per admitted mouse before dynamic families C,D,S; original roster/configuration order'))


def claim_attempt(path,record):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        f.write(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def fit_one(model,config,target,binding,state_hash):
    initial=model.initialize(config['seed'])
    record=dict(configuration=config,status='STARTED',attempt=1,initial=initial.tolist(),free_parameters=model.size,
        C_state_sha256=state_hash,production_gate_sha256=binding,optimizer_history=[],
        started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),fit_role='C',D_neural_fit_data=False,
        Development_coefficients_reused=False)
    claim_attempt(target,record);started=time.perf_counter();last={};calls=0
    def objective(theta):
        nonlocal calls
        value,gradient=model.objective(theta);calls+=1
        last.update(theta=theta.copy(),value=value,gradient=gradient.copy());return value,gradient
    def callback(theta):
        if not np.array_equal(theta,last['theta']):objective(theta)
        record['optimizer_history'].append(dict(iteration=len(record['optimizer_history'])+1,
            objective=float(last['value']),PG=pg(theta,last['gradient'],model.bounds),
            full_gradient_inf=float(np.max(np.abs(last['gradient']))),calls=calls))
    try:
        if config['family']=='B0':
            theta=np.clip(np.log(np.maximum(model.y[:,model.warm:].sum(axis=(0,1)),np.finfo(float).tiny)/(model.T*model.delta)),-8,8)
            value,g=objective(theta);iterations=0;status=0;success=True;message='Frozen constrained stationary MLE'
        else:
            opt=minimize(objective,initial,method='L-BFGS-B',jac=True,bounds=model.bounds,callback=callback,options=SOLVER)
            theta=opt.x;value,g=model.objective(theta);iterations=int(opt.nit);status=int(opt.status);success=bool(opt.success);message=str(opt.message)
        independent=coordinate_check(model,theta);projected=pg(theta,g,model.bounds);bounds=np.asarray(model.bounds)
        masses=model.prebin_logmasses(theta)
        finite=bool(np.isfinite(theta).all() and np.isfinite(g).all() and np.isfinite(value) and np.isfinite(masses).all())
        valid_bounds=bool(((theta>=bounds[:,0])&(theta<=bounds[:,1])).all())
        passed=finite and valid_bounds and projected<=.001 and independent['PASS'] and status!=1
        record.update(status='NUMERICAL_PASS' if passed else 'NUMERICAL_FAIL',coefficients=theta.tolist(),bounds=model.bounds,
            objective=float(value),PG=projected,full_gradient_inf=float(np.max(np.abs(g))),iterations=iterations,
            optimizer_objective_calls=calls,optimizer_status=status,optimizer_success=success,termination=message,
            independent=independent,finite_all=finite,exact_bounds=valid_bounds,budget_exhausted=status==1,
            training_score_LL=float(masses[:,model.warm:].sum()),training_population_bins=model.T,training_unit_bins=model.T*model.u,
            wall_seconds=time.perf_counter()-started,completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    except Exception as exc:
        record.update(status='NUMERICAL_FAIL',error=type(exc).__name__+': '+str(exc),wall_seconds=time.perf_counter()-started)
    dump(target,record)
    return record


def check_production_gate(gate):
    required={'calibration.py','models.py','independent_ad.py','features.py','source.py','C_FIT_PLAN.json',
              'results/FINAL_C_QC_GATE.json','results/C_FEATURE_PREPARATION.json','sensitivities.py','controls.py','SENSITIVITY_FIT_PLAN.json',
              'sensitivity_calibration.py','METADATA_SOURCE_EXTERNAL_FREEZE.json','C_READER_GATE.json'}
    if not gate.get('approved_selected_C_calibration') or not required<=set(gate.get('hashes',{})):
        raise PermissionError('Complete reviewed C production admission required')
    for rel,h in gate['hashes'].items():
        if sha(P/rel)!=h:raise PermissionError('Frozen C production input mismatch: '+rel)
    item=gate['independent_review'];receipt=read(R/item['path'])
    if (sha(R/item['path'])!=item['sha256'] or receipt['decision']!='ACCEPTED_FROZEN_C_CALIBRATION'
        or type(receipt['open_P0']) is not int or receipt['open_P0']!=0
        or type(receipt['open_P1']) is not int or receipt['open_P1']!=0
        or receipt['hashes']!=gate['hashes'] or receipt['approved_selected_C_calibration'] is not True):
        raise PermissionError('C production review does not accept this exact state')
    if sha(R/receipt['report_path'])!=receipt['report_sha256']:raise PermissionError('C production review report changed')
    from .reader import verify_external_dependencies
    verify_external_dependencies(read(P/'METADATA_SOURCE_EXTERNAL_FREEZE.json')['hashes'])
    frozen_definitions()


def execute_main():
    gate=read(P/'C_PRODUCTION_GATE.json');check_production_gate(gate)
    plan=read(P/'C_FIT_PLAN.json');assert plan['subjects']==admitted() and plan['configurations']==configurations()
    assert plan['per_mouse']==12 and plan['expected_attempts']==12*len(admitted())<=96 and plan['max_retries']==0
    allrows=[]
    for dynamic in [False,True]:
        for subject in admitted():
            prep=read(P/'states'/(subject+'_C_PREPROCESSING.json'));assert sha(P/'states'/(subject+'_C_PREPROCESSING.json'))==plan['state_hashes'][subject]
            path=P/'work/C_features'/(subject+'.npz');assert sha(path)==prep['C_features_sha256']
            with np.load(path,allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
            for config in plan['configurations']:
                if (config['family'] in ('C','D','S'))!=dynamic:continue
                target=P/'fits'/subject/(config['id']+'.json')
                record=fit_one(build_model(arrays,config),config,target,sha(P/'C_PRODUCTION_GATE.json'),plan['state_hashes'][subject])
                allrows.append(dict(subject=subject,configuration=config,status=record['status'],sha256=sha(target)))
                print(subject,config['id'],record['status'],'PG',record.get('PG'),'sec',round(record['wall_seconds'],2),flush=True)
                if record['status']!='NUMERICAL_PASS' and config['family'].startswith('B'):
                    dump(P/'results/C_MAIN_REQUIRED_STOP.json',dict(reason='MANDATORY_BASELINE_NUMERICAL_FAILURE',failed=allrows[-1],attempts=allrows,D_executed=False))
                    return
    dump(P/'results/C_MAIN_ATTEMPTS_COMPLETE.json',dict(attempts=allrows,attempted=len(allrows),
        numerical_pass=sum(r['status']=='NUMERICAL_PASS' for r in allrows),D_neural_fit_data=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','register','run'])
    action=parser.parse_args().action
    {'prepare':prepare,'register':register,'run':execute_main}[action]()
