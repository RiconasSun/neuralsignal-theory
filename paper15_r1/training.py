"""A-only feature preparation and prospectively bounded production fit execution."""
from .source import load_json
import argparse
import datetime
import hashlib
import json
import os
import time
import numpy as np
from scipy.optimize import minimize
from .source import P, R, dump
from .metadata_access import local_path
from .features import observed_arrays, nuisance, design, dct_state
from .models import Model, pg
from .independent_ad import coordinate_check


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def admitted():
    gate=load_json((P/'results/M2_PHYSIOLOGY_GATE.json').read_text(encoding='utf8'))
    assert gate['M2_SOURCE_QC_PASS']
    return [x['subject'] for x in gate['subjects'] if x['admitted']]


def prepare():
    freeze=load_json((P/'SOURCE_FILE_FREEZE.json').read_text(encoding='utf8'));records=[]
    for subject in admitted():
        state=load_json((P/'metadata'/(subject+'_task.json')).read_text(encoding='utf8'))
        qcpath=P/'results'/(subject+'_A_QC.json');qc=load_json(qcpath.read_text(encoding='utf8'))
        export=P/'work/A_exports'/(subject+'.npz');assert sha(export)==qc['A_export_sha256']
        with np.load(export,allow_pickle=False) as f:
            times=f['times'];labels=f['labels'];ids=f['trial_ids']
        units=qc['selected_unit_ids'];stimuli=np.array([state['trials'][i]['stimOn_times'] for i in ids])
        y,h,b,epoch,warm=observed_arrays(times,labels,units,stimuli)
        entry=next(x for x in freeze['subjects'] if x['subject']==subject)
        paths={x['role']:local_path(entry,x) for x in entry['files'] if x['role'] in ('wheel_times','wheel_position')}
        wt=np.load(paths['wheel_times'],allow_pickle=False);wp=np.load(paths['wheel_position'],allow_pickle=False)
        nx=nuisance(state['trials'],ids,b,epoch,wt,wp)
        x,scales,active=design(nx,h,warm)
        arrays=dict(x=x,y=y,active=active,trial_ids=ids);cscales={}
        for rank in (1,2):
            for tau in (.1,.25):
                key=f'C_r{rank}_tau{tau}'
                q,s=dct_state(y,rank,tau,warm);arrays[key]=q;arrays[key+'_active']=np.asarray(s['q_scale']['active']);cscales[key]=s
        target=P/'work/A_features'/(subject+'.npz');target.parent.mkdir(parents=True,exist_ok=True)
        assert not target.exists(),'Do not overwrite preserved A feature state'
        np.savez_compressed(target,**arrays)
        modelstate=dict(subject=subject,role='A',units=units,unit_uuids=qc['selected_unit_uuids'],trial_ids=ids.tolist(),
            scales=scales,C_scales=cscales,active=active.tolist(),warm_bins=warm,delta=.05,
            actual_score_population_bins=int(len(ids)*10),actual_score_unit_bins=int(len(ids)*10*8),
            QC_sha256=sha(qcpath),task_sha256=sha(P/'metadata'/(subject+'_task.json')),A_export_sha256=sha(export),
            A_features_sha256=sha(target),M1_freeze_sha256=sha(R/'paper15_m1/PROTOCOL_FREEZE.json'),
            feature_implementation_sha256=sha(P/'features.py'),preparation_implementation_sha256=sha(P/'training.py'),
            model_parameters_from_other_mouse=False,B_E_access=False,Final_access=False)
        sp=P/'states'/(subject+'_A_PREPROCESSING.json');assert not sp.exists();dump(sp,modelstate)
        records.append(dict(subject=subject,epochs=len(ids),unit_bins=len(ids)*80,A_features_sha256=sha(target),state_sha256=sha(sp)))
        print(subject,len(ids),'A epochs; features/scales sealed',flush=True)
    dump(P/'results/A_FEATURE_PREPARATION.json',dict(subjects=records,real_fits=0,B_E_access=False,Final_access=False))


def configurations():
    out=[dict(id='B0',family='B0',ridge=0.,seed=11)]
    for family in ('B1','B2','B3','B4'):
        for ridge in (.01,.1,1.):out.append(dict(id=f'{family}_l{ridge}',family=family,ridge=ridge,seed=11))
    for k in (2,3):
        for ridge in (.01,.1,1.):
            for seed in (11,23,37):out.append(dict(id=f'D_k{k}_l{ridge}_s{seed}',family='D',k=k,ridge=ridge,seed=seed))
    for rank in (1,2):
        for tau in (.1,.25):
            for ridge in (.01,.1,1.):out.append(dict(id=f'C_r{rank}_t{tau}_l{ridge}',family='C',rank=rank,tau=tau,ridge=ridge,seed=11))
    for k in (3,4):
        for ridge in (.01,.1,1.):
            for seed in (11,23,37):out.append(dict(id=f'S_k{k}_l{ridge}_s{seed}',family='S',k=k,ridge=ridge,seed=seed))
    assert len(out)==61
    return out


def build_model(arrays,config):
    x=arrays['x'];active=arrays['active']
    if config['family']=='C':
        q=arrays[f"C_r{config['rank']}_tau{config['tau']}"]
        state_rank=arrays[f"C_r{config['rank']}_tau{config['tau']}_active"]
        x=np.concatenate([x,q],axis=-1);active=np.r_[active,state_rank]
    return Model(x,arrays['y'],config['family'],ridge=config['ridge'],k=config.get('k',2),active=active)


def register():
    path=P/'A_FIT_PLAN.json';assert not path.exists()
    configs=configurations();subjects=admitted()
    dump(path,dict(registered_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),subjects=subjects,
        configurations=configs,per_mouse=61,total_main=len(subjects)*61,maximum_main=732,max_retries=0,
        order='All baseline A attempts before dynamic A attempts; within each stage mouse roster and listed configuration order',
        solver=dict(method='L-BFGS-B',maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6),
        numerical=dict(PG_max=.001,AD_max=1e-5,FD_steps=[1e-4,1e-5,1e-6],all_steps_required=True),
        mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',execution_version='EXACT_NATIVE_R1',
        historical_started_attempts=359,historical_completed=358,historical_interrupted=1,
        absolute_new_sensitivity_cap=660,actual_cohort_sensitivity_cap=55*len(subjects),
        historical_coefficients_reused=False,corrective_budget_separate=True,
        B_access_before_A_attempts_sealed=False,E_access_before_B_selection_frozen=False,Final_access=False))


def claim_attempt(path,record):
    path.parent.mkdir(parents=True,exist_ok=True)
    # A competing invocation or a crash residue cannot acquire this fit twice.
    with path.open('x',encoding='utf8') as handle:
        handle.write(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n')
        handle.flush();os.fsync(handle.fileno())


def verify_completed_attempt(old,config,gate_hash):
    assert old['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL'), 'Interrupted attempt is immutable; stop, do not retry'
    assert old['configuration']==config and old['production_gate_sha256']==gate_hash


def baseline_availability(records,subjects):
    baseline=[x for x in configurations() if x['family'].startswith('B')]
    by={(x['subject'],x['configuration']['id']):x for x in records}
    assert len(by)==len(records)==len(subjects)*13
    assert all((s,c['id']) in by for s in subjects for c in baseline)
    assert all(x['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL') for x in records)
    available={family:[] for family in ('B0','B1','B2','B3','B4')}
    for c in baseline:
        if all(by[(s,c['id'])]['status']=='NUMERICAL_PASS' for s in subjects):available[c['family']].append(c['id'])
    return dict(available=available,PRIMARY_BASELINE_NUMERICAL_GATE=bool(available['B0'] and available['B1'] and available['B4']))


def execute(stage):
    gate=load_json((P/'PRODUCTION_GATE.json').read_text(encoding='utf8'));assert gate['PRODUCTION_NUMERICAL_PASS']
    for rel,h in gate['hashes'].items():assert sha(P/rel)==h,rel
    plan=load_json((P/'A_FIT_PLAN.json').read_text(encoding='utf8'))
    from .production_admission import verify
    verify(gate,plan)
    assert plan['subjects']==admitted() and plan['per_mouse']==61 and plan['total_main']<=732
    if stage=='dynamic':
        assert (P/'results/BASELINE_ATTEMPTS_COMPLETE.json').exists()
        marker=load_json((P/'results/BASELINE_ATTEMPTS_COMPLETE.json').read_text(encoding='utf8'))
        baseline_records=[]
        for subject in plan['subjects']:
            for config in plan['configurations']:
                if not config['family'].startswith('B'):continue
                bp=P/'fits'/subject/(config['id']+'.json');br=load_json(bp.read_text(encoding='utf8'))
                verify_completed_attempt(br,config,sha(P/'PRODUCTION_GATE.json'))
                assert marker['attempt_hashes'][subject+'/'+config['id']]==sha(bp)
                baseline_records.append(br)
        assert baseline_availability(baseline_records,plan['subjects'])['PRIMARY_BASELINE_NUMERICAL_GATE'], 'Required global B1/B4 baseline unavailable: STOP before dynamic fits'
    for subject in plan['subjects']:
        feature_path=P/'work/A_features'/(subject+'.npz')
        prep=load_json((P/'states'/(subject+'_A_PREPROCESSING.json')).read_text(encoding='utf8'))
        assert sha(feature_path)==prep['A_features_sha256']
        with np.load(feature_path,allow_pickle=False) as file:arrays={k:file[k] for k in file.files}
        for config in plan['configurations']:
            if (config['family'] in ('D','C','S'))!=(stage=='dynamic'):continue
            path=P/'fits'/subject/(config['id']+'.json')
            if path.exists():
                old=load_json(path.read_text(encoding='utf8'))
                verify_completed_attempt(old,config,sha(P/'PRODUCTION_GATE.json'))
                continue
            model=build_model(arrays,config);initial=model.initialize(config['seed'])
            record=dict(subject=subject,configuration=config,status='STARTED',attempt=1,initial=initial.tolist(),
                nominal_family=config['family'],free_parameters=model.size,A_preprocessing_sha256=sha(P/'states'/(subject+'_A_PREPROCESSING.json')),
                production_gate_sha256=sha(P/'PRODUCTION_GATE.json'),started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                optimizer_history=[],B_E_fit_data=False,Final_access=False)
            claim_attempt(path,record);started=time.perf_counter();last={};calls=0
            def objective(theta):
                nonlocal calls
                result=model.objective(theta);calls+=1;last.update(theta=theta.copy(),objective=result[0],gradient=result[1].copy())
                return result
            def callback(theta):
                if not np.array_equal(theta,last['theta']):objective(theta)
                record['optimizer_history'].append(dict(iteration=len(record['optimizer_history'])+1,objective=float(last['objective']),
                    PG=pg(theta,last['gradient'],model.bounds),full_gradient_inf=float(np.max(np.abs(last['gradient']))),calls=calls))
            try:
                if config['family']=='B0':
                    theta=np.clip(np.log(np.maximum(model.y[:,10:].sum(axis=(0,1)),np.finfo(float).tiny)/(model.T*.05)),-8,8)
                    value,gradient=objective(theta);iterations=0;success=True;status=0;message='Frozen constrained closed-form stationary MLE'
                else:
                    fit=minimize(objective,initial,method='L-BFGS-B',jac=True,bounds=model.bounds,callback=callback,
                        options={k:v for k,v in plan['solver'].items() if k!='method'})
                    theta=fit.x;value,gradient=model.objective(theta);iterations=int(fit.nit);success=bool(fit.success);status=int(fit.status);message=str(fit.message)
                projected=pg(theta,gradient,model.bounds)
                # Required endpoint comparison uses identical original parameters/objective for every method.
                independent=coordinate_check(model,theta)
                bounds=np.asarray(model.bounds);valid_bounds=bool(((theta>=bounds[:,0])&(theta<=bounds[:,1])).all())
                exhausted=(status==1)
                passed=valid_bounds and projected<=.001 and independent['PASS'] and not exhausted
                record.update(status='NUMERICAL_PASS' if passed else 'NUMERICAL_FAIL',optimizer_success=success,
                    optimizer_status=status,termination=message,iterations=iterations,optimizer_objective_calls=calls,
                    objective=float(value),PG=projected,full_gradient_inf=float(np.max(np.abs(gradient))),
                    coefficients=theta.tolist(),bounds=model.bounds,independent=independent,budget_exhausted=exhausted,
                    training_score_LL=float(model.prebin_logmasses(theta)[:,10:].sum()),
                    training_population_bins=model.T,training_unit_bins=model.T*model.u,
                    wall_seconds=time.perf_counter()-started,completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            except Exception as exc:
                record.update(status='NUMERICAL_FAIL',error=type(exc).__name__+': '+str(exc),wall_seconds=time.perf_counter()-started)
                dump(path,record)
                raise
            dump(path,record)
            print(subject,config['id'],record['status'],'PG',record.get('PG'),'sec',round(time.perf_counter()-started,2),flush=True)
    expected=[(s,c['id']) for s in plan['subjects'] for c in plan['configurations'] if (c['family'] in ('D','C','S'))==(stage=='dynamic')]
    records=[load_json((P/'fits'/s/(cid+'.json')).read_text(encoding='utf8')) for s,cid in expected]
    summary=dict(stage=stage,attempted=len(records),completed=sum(x['status']!='STARTED' for x in records),
            numerical_pass=sum(x['status']=='NUMERICAL_PASS' for x in records),failures=[dict(subject=x['subject'],configuration=x['configuration'],reason=x.get('error',x.get('termination'))) for x in records if x['status']!='NUMERICAL_PASS'],
            attempt_hashes={s+'/'+cid:sha(P/'fits'/s/(cid+'.json')) for s,cid in expected},B_E_access=False,Final_access=False)
    if stage=='baseline':summary.update(baseline_availability(records,plan['subjects']))
    dump(P/'results'/('DYNAMIC_ATTEMPTS_COMPLETE.json' if stage=='dynamic' else 'BASELINE_ATTEMPTS_COMPLETE.json'),summary)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','register','baselines','dynamic']);action=ap.parse_args().action
    if action=='prepare':prepare()
    elif action=='register':register()
    else:execute('baseline' if action=='baselines' else 'dynamic')
