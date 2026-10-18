"""Frozen five-baseline sensitivity refits after B selection; no new grid or retry."""
from .source import load_json
import argparse
import datetime
import json
import time
import numpy as np
from scipy.optimize import minimize
from .source import P,dump
from .training import sha,claim_attempt,admitted
from .models import Model,pg
from .independent_ad import coordinate_check
from .sensitivities import prepare,CASES


def verify_plan(plan,selection,candidates,preparation,subjects):
    assert preparation['cases']==CASES
    expected_cases={(s,c['id']) for s in subjects for c in CASES}
    actual_cases=[(r['subject'],r['case']) for r in preparation['records']]
    assert len(actual_cases)==len(expected_cases) and set(actual_cases)==expected_cases
    assert len(subjects)==len(set(subjects))
    assert plan['solver']==dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)
    assert plan['maximum_Development']==550 and plan['maximum_all_registered_sensitivities']==1100
    chosen={family:next(x for x in candidates if x['id']==cid) for family,cid in selection['selected'].items() if cid is not None}
    assert all(chosen[f]['available'] for f in ['B0','B1','B2','B3','B4'])
    winner={family:entry['configurations'][0] for family,entry in chosen.items()}
    assert all(winner[f]['family']==f for f in ['B0','B1','B2','B3','B4'])
    expected=[]
    for row in preparation['records']:
        assert row['subject'] in subjects and row['case'] in {x['id'] for x in CASES}
        assert row['status'] in ('A_PREPROCESSING_SEALED','UNAVAILABLE')
        if row['status']=='UNAVAILABLE':
            assert row['reasons'];continue
        for family in ['B0','B1','B2','B3','B4']:
            expected.append(dict(subject=row['subject'],case=row['case'],family=family,ridge=winner[family]['ridge'],
                seed=11,state_sha256=row['state_sha256']))
    assert plan['attempts']==expected and len(expected)==plan['expected_attempts']<=550
    assert plan['max_retries']==0 and plan['new_hyperparameter_search'] is False and plan['Final_fits']==0


def register():
    selected=load_json((P/'SELECTION_FREEZE.json').read_text(encoding='utf8'))
    candidates=load_json((P/'results/B_CANDIDATE_SCORES.json').read_text(encoding='utf8'))
    winner={f:next(x['configurations'][0] for x in candidates if x['id']==cid) for f,cid in selected['selected'].items() if cid is not None}
    prep=load_json((P/'results/SENSITIVITY_PREPARATION.json').read_text(encoding='utf8'));attempts=[]
    for row in prep['records']:
        if row['status']!='A_PREPROCESSING_SEALED':continue
        for family in ['B0','B1','B2','B3','B4']:
            path=P/'sensitivity_states'/row['subject']/(row['case']+'.json')
            attempts.append(dict(subject=row['subject'],case=row['case'],family=family,
                ridge=winner[family]['ridge'],seed=11,state_sha256=sha(path)))
    assert len(attempts)<=550
    target=P/'SENSITIVITY_FIT_PLAN.json';assert not target.exists()
    dump(target,dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),attempts=attempts,
        B_selection_sha256=sha(P/'SELECTION_FREEZE.json'),expected_attempts=len(attempts),maximum_Development=550,
        maximum_all_registered_sensitivities=1100,new_hyperparameter_search=False,max_retries=0,Final_fits=0,
        solver=dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)))


def run():
    gate=load_json((P/'SENSITIVITY_GATE.json').read_text(encoding='utf8'));assert gate['approved_for_fixed_A_sensitivity_refits']
    required={'SENSITIVITY_FIT_PLAN.json','SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json','results/SENSITIVITY_PREPARATION.json',
        'models.py','independent_ad.py','features.py','sensitivities.py','sensitivity_fits.py','PRODUCTION_GATE.json'}
    assert required<=set(gate['hashes']), 'Sensitivity gate must bind its complete frozen plan, B winners and numerical sources'
    for rel,h in gate['hashes'].items():assert sha(P/rel)==h
    plan=load_json((P/'SENSITIVITY_FIT_PLAN.json').read_text(encoding='utf8'));assert len(plan['attempts'])==plan['expected_attempts']<=550
    assert plan['B_selection_sha256']==sha(P/'SELECTION_FREEZE.json')
    verify_plan(plan,load_json((P/'SELECTION_FREEZE.json').read_text(encoding='utf8')),
        load_json((P/'results/B_CANDIDATE_SCORES.json').read_text(encoding='utf8')),
        load_json((P/'results/SENSITIVITY_PREPARATION.json').read_text(encoding='utf8')),admitted())
    for item in plan['attempts']:
        subject=item['subject'];case=item['case'];family=item['family']
        statepath=P/'sensitivity_states'/subject/(case+'.json');assert sha(statepath)==item['state_sha256']
        state=load_json(statepath.read_text(encoding='utf8'))
        arraypath=P/'work/sensitivity_A'/subject/(case+'.npz');assert sha(arraypath)==state['A_features_sha256']
        with np.load(arraypath,allow_pickle=False) as f:x=f['x'];y=f['y'];active=f['active']
        model=Model(x,y,family,ridge=item['ridge'],active=active,warm=state['warm'],delta=state['delta'],nuisance=state['nuisance_columns'])
        target=P/'sensitivity_fits'/subject/case/(family+'.json')
        if target.exists():
            old=load_json(target.read_text(encoding='utf8'));assert old['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL') and old['plan_item']==item
            assert old['sensitivity_gate_sha256']==sha(P/'SENSITIVITY_GATE.json');continue
        initial=model.initialize(11);record=dict(plan_item=item,status='STARTED',initial=initial.tolist(),attempt=1,
            sensitivity_gate_sha256=sha(P/'SENSITIVITY_GATE.json'),started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            optimizer_history=[],E_neural_fit_data=False,Final_access=False)
        claim_attempt(target,record);start=time.perf_counter();last={};calls=0
        def objective(v):
            nonlocal calls
            val,g=model.objective(v);calls+=1;last.update(theta=v.copy(),value=val,gradient=g.copy());return val,g
        def callback(v):
            if not np.array_equal(v,last['theta']):objective(v)
            record['optimizer_history'].append(dict(iteration=len(record['optimizer_history'])+1,objective=last['value'],PG=pg(v,last['gradient'],model.bounds),calls=calls))
        try:
            if family=='B0':
                v=np.clip(np.log(np.maximum(y[:,model.warm:].sum(axis=(0,1)),np.finfo(float).tiny)/(model.T*model.delta)),-8,8)
                value,g=objective(v);iterations=0;status=0;success=True;message='Registered constrained stationary MLE'
            else:
                opt=minimize(objective,initial,method='L-BFGS-B',jac=True,bounds=model.bounds,callback=callback,options=plan['solver'])
                v=opt.x;value,g=model.objective(v);iterations=int(opt.nit);status=int(opt.status);success=bool(opt.success);message=str(opt.message)
            independent=coordinate_check(model,v);projected=pg(v,g,model.bounds);bounds=np.asarray(model.bounds)
            passed=bool(((v>=bounds[:,0])&(v<=bounds[:,1])).all()) and projected<=.001 and independent['PASS'] and status!=1
            record.update(status='NUMERICAL_PASS' if passed else 'NUMERICAL_FAIL',coefficients=v.tolist(),free_parameters=model.size,
                objective=float(value),PG=projected,full_gradient_inf=float(np.max(np.abs(g))),iterations=iterations,objective_calls=calls,
                optimizer_status=status,optimizer_success=success,termination=message,independent=independent,
                actual_population_bins=model.T,actual_unit_bins=model.T*model.u,wall_seconds=time.perf_counter()-start,
                completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        except Exception as exc:
            record.update(status='NUMERICAL_FAIL',error=type(exc).__name__+': '+str(exc));dump(target,record);raise
        dump(target,record);print(subject,case,family,record['status'],'PG',record['PG'],flush=True)
    rows=[dict(item=item,sha256=sha(P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json')),
        status=load_json((P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json')).read_text(encoding='utf8'))['status']) for item in plan['attempts']]
    dump(P/'results/SENSITIVITY_ATTEMPTS_COMPLETE.json',dict(attempted=len(rows),completed=len(rows),numerical_pass=sum(x['status']=='NUMERICAL_PASS' for x in rows),records=rows,Final_access=False,E_neural_access=False))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','register','run']);action=ap.parse_args().action
    if action=='prepare':prepare()
    elif action=='register':register()
    else:run()
