"""One R4 stage: audited reuse, bounded new A fits, reviewed seal, then one E."""
import math, os, sys, time, hashlib
from functools import lru_cache
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from .core import *
from . import features, models, optimizer, panels, controls, source
from paper16_dev_r3.run_m2 import supervise_child

OLD=R/'paper16_development_r3'

def review_binding(name,decision,manifest):
    approval=load(E/name)
    if approval['decision']!=decision or approval['open_P0'] or approval['open_P1']:raise AccessStop('Independent gate not accepted: '+name)
    path=R/approval['review_path']
    if not path.resolve().is_relative_to(E.resolve()) or sha(path)!=approval['review_sha256']:raise AccessStop('Review identity')
    if sha(manifest)!=approval['manifest_sha256']:raise AccessStop('Reviewed manifest identity')
    for row in load(manifest)['files']:
        if sha(R/row['path'])!=row['sha256']:raise AccessStop('Reviewed artifact changed: '+row['path'])
    return approval

def verify_prefit():
    verify_pins()
    reuse=load(E/'REUSE_ADMISSION_APPROVAL.json')
    if reuse['decision']!='ACCEPTED_HISTORICAL_STATE_ADMISSION_ONLY' or reuse['P0'] or reuse['P1']:raise AccessStop('Independent complete reuse approval required')
    if not {(E/'REUSE_REVIEW_1.md').relative_to(R).as_posix(),(E/'INDEPENDENT_REUSE_CHECK_RESULT.json').relative_to(R).as_posix()}<={r['path'] for r in reuse['files']}:raise AccessStop('Incomplete independent reuse binding')
    for row in reuse['files']:
        if sha(R/row['path'])!=row['sha256']:raise AccessStop('Admitted state audit changed')
    approval=review_binding('PREFIT_APPROVAL.json','ACCEPTED_R4_PRODUCTION_PREFIT',P/'PREFIT_FREEZE_MANIFEST.json')
    cert=load(P/'PRODUCTION_NUMERICAL_CERTIFICATION.json')
    if not cert['mandatory_tests_pass'] or cert['real_fits_executed']!=0:raise AccessStop('Synthetic production gate')
    audit=load(P/'STATE_REUSE_AUDIT_RESULT.json')
    if not audit['required_gate_pass'] or (audit['compatible_optimizer_states'],audit['compatible_B0_states'])!=(952,216):raise AccessStop('All952+216 mandatory')
    return approval

@lru_cache(maxsize=1)
def admitted_lookup():
    return {r['task_id']:r for r in load(P/'STATE_COMPATIBILITY_MATRIX.json')['states'] if r['status']=='COMPATIBLE'}

def task_folder(task):
    old=admitted_lookup()
    return (R/old[task['id']]['result_path']).parent if task['id'] in old else P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()

def verify_completed(tasks):
    for task in tasks:
        folder=task_folder(task);result=load(folder/'RESULT.json');diag=load(folder/'DIAGNOSTICS.json')
        if result['task']!=task or not result['numerical_pass'] or result['projected_gradient_inf']>1e-5:raise AccessStop('Required task/certificate')
        if result['external_value_gradient_pairs']>6000 or result['external_accepted_iterations']>1500:raise AccessStop('External budget')
        if sha(folder/'DIAGNOSTICS.json')!=result['diagnostic_state_sha256'] or sha(R/result['endpoint_state']['path'])!=result['endpoint_state']['sha256']:raise AccessStop('Endpoint identity')
        if not diag['all_checkpoints_pass'] or len(diag['checkpoints'])!=3:raise AccessStop('Required diagnostics')

def load_prepared():
    prepared={};scalers={}
    for row in load(OLD/'results/A_PREPROCESSING_STATES.json'):
        if row['role']!='A' or sha(R/row['path'])!=row['sha256']:raise AccessStop('Exact saved A only')
        with np.load(R/row['path'],allow_pickle=False) as a:values={k:a[k].copy() for k in a.files}
        if {k:array_id(v) for k,v in values.items()}!=row['arrays']:raise AccessStop('A member identity')
        b=features.Batch(**{k:values[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=row['dt'],psth=row['psth'],b1=row['b1'],role='A',panel=row['panel'])
        if np.any(b.ordinals>=90) or np.any(b.ordinals<0):raise AccessStop('A partition')
        key=tuple(row['key'].split('/'));prepared[key]=b
        scalers[key]=features.Scaling(values['mean'],values['scale'],values['active'],row['psth'])
    return prepared,scalers

def require_phase(role):
    if role not in ['A','E']:raise AccessStop('B reselection and Final/unknown roles forbidden')
    verify_prefit();stage=load(P/'results/STAGE_CLAIM.json');verify_stage_environment(stage);guard(stage)
    job=load(P/'results/SUPERVISOR.json')['job_name'];require_job(job)
    if os.environ.get('P16_R4_JOB')!=job:raise AccessStop('Wrong stage Job')
    if role=='E':
        review_binding('M4_APPROVAL.json','ACCEPTED_R4_COMPLETE_M4',P/'M4_REVIEW_MANIFEST.json')
        freeze=load(P/'results/M4_SELECTION_FREEZE.json');validate_m4_freeze(freeze,load(OLD/'results/TASK_PLAN.json'))
        claim=load(P/'results/E_BATCH_CLAIM.json')
        if claim['selection_freeze_sha256']!=sha(P/'results/M4_SELECTION_FREEZE.json'):raise AccessStop('E onebatch/freeze identity')

def run_fit(task,batch,scaler,lam,stage):
    if task not in load(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks']:raise AccessStop('Only5519 exact new tasks')
    journal=P/'results/FIT_JOURNAL.jsonl';old=source.CacheReader._journal(journal)
    if any(r.get('task',{}).get('id')==task['id'] for r in old):raise AccessStop('Consumed optimizer task; no retry')
    if sum(r['event']=='ATTEMPTED' for r in old)>=5519:raise BudgetStop('New task cap')
    guard(stage);event(journal,event='ATTEMPTED',task=task,ftol=0.0)
    try:
        unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id'])
        objective=models.Objective(batch,scaler,task['model'],lam,unit,task['seed'])
        x,result=optimizer.fit(objective,task_folder(task),stage,task)
        event(journal,event='COMPLETED',task=task,result_path=(task_folder(task)/'RESULT.json').relative_to(R).as_posix(),result_sha256=sha(task_folder(task)/'RESULT.json'),PG=result['projected_gradient_inf'])
        return result
    except BaseException as exc:
        event(journal,event='FAILED',task=task,error_type=type(exc).__name__,message=str(exc),retry=False)
        raise

def bundles(prepared,scalers):
    fitted={};latent={};seed_choices=[]
    for task in load(OLD/'results/TASK_PLAN.json')['tasks']:
        if task['panel']=='MAIN' and task['model']=='B1' and task['lambda']!=1.:continue
        key=(task['mouse_id'],task['panel']);batch=prepared[key]
        unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id'])
        obj=models.Objective(batch,scalers[key],task['model'],1.,unit,task['seed'])
        result=load(task_folder(task)/'RESULT.json')
        with np.load(R/result['endpoint_state']['path'],allow_pickle=False) as a:x=a['x'].copy()
        if task['model'] in ['D','S']:latent.setdefault((key,task['model']),[]).append((obj,x,result))
        else:fitted.setdefault(key,{}).setdefault(task['model'],[]).append((obj,x))
    for (key,model),states in latent.items():
        rows=[{'seed':r['task']['seed'],'numerical_pass':r['numerical_pass'],'objective':r['objective']} for _,_,r in states]
        seed=analysis_oracles.select_seed(rows);obj,x,_=next(s for s in states if s[2]['task']['seed']==seed)
        fitted.setdefault(key,{})[model]=(obj,x);seed_choices.append({'mouse_id':key[0],'panel':key[1],'model':model,'seed':seed,'all_seeds':rows})
    for record in source.admitted():
        mouse=record['source']['mouse_id'];theta=[]
        for uid in record['selection']['selected_unit_ids']:
            with np.load(OLD/'work/B0'/mouse/str(uid)/'coordinate_certificates.npz',allow_pickle=False) as a:theta.append(float(a['endpoint_x'][0]))
        fitted[(mouse,'MAIN')]['B0']=np.asarray(theta)
    return fitted,seed_choices

def validate_m4_freeze(freeze,plan):
    if not {'task_plan_sha256','task_origins','states','selected_seeds'}<=freeze.keys():raise AccessStop('Incomplete M4 manifest')
    if freeze['task_plan_sha256']!=sha(OLD/'results/TASK_PLAN.json') or len(freeze['task_origins'])!=6471:raise AccessStop('Full M4 task count/identity')
    if {r['task_id'] for r in freeze['task_origins']}!={t['id'] for t in plan['tasks']}:raise AccessStop('Missing M4 task')
    for row in freeze['states']:
        if sha(R/row['path'])!=row['sha256']:raise AccessStop('Frozen state changed')
    actual={r['path'] for r in freeze['states']}
    required=set()
    for task in plan['tasks']:
        folder=task_folder(task)
        names=['ATTEMPT.json','initial.npz','CLIENT.json','CLIENT_STDERR.log','CALLS.jsonl','RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz','endpoint.npz']
        if load(folder/'RESULT.json')['nit']>0:names.append('ACCEPTED.jsonl')
        if folder.is_relative_to(P):names.append('DIAGNOSTIC_CALLS.jsonl')
        required.update((folder/name).relative_to(R).as_posix() for name in names)
    for record in source.admitted():
        for uid in record['selection']['selected_unit_ids']:
            folder=OLD/'work/B0'/record['source']['mouse_id']/str(uid)
            required.update((folder/name).relative_to(R).as_posix() for name in ['RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz'])
    required.update(r['path'] for r in load(OLD/'results/A_PREPROCESSING_STATES.json'))
    if len(actual)!=len(freeze['states']) or not required<=actual:raise AccessStop('Incomplete M4 certificate/scaler state inventory')
    verify_completed(plan['tasks'])
    expected={(r['key'].split('/')[0],r['panel'],m) for r in load(OLD/'results/A_PREPROCESSING_STATES.json') for m in ['D','S']}
    if {(r['mouse_id'],r['panel'],r['model']) for r in freeze['selected_seeds']}!=expected:raise AccessStop('D/S all panel selections')
    for row in freeze['selected_seeds']:
        if len(row['all_seeds'])!=3 or analysis_oracles.select_seed(row['all_seeds'])!=row['seed']:raise AccessStop('All3 original seed rule')

def seal(prepared,scalers):
    plan=load(OLD/'results/TASK_PLAN.json');verify_completed(plan['tasks'])
    fitted,selected=bundles(prepared,scalers);paths=set();origins=[]
    for task in plan['tasks']:
        folder=task_folder(task);historical=folder.is_relative_to(OLD)
        origins.append({'task_id':task['id'],'origin':'R3_GENERATED_FTOL1E-12_ADMITTED_R4' if historical else 'R4_FTOL0',
                        'result_path':(folder/'RESULT.json').relative_to(R).as_posix(),'result_sha256':sha(folder/'RESULT.json')})
        paths.update(x for x in folder.iterdir() if x.is_file())
    paths.update(x for x in (OLD/'work/B0').rglob('*') if x.is_file())
    paths.update(R/r['path'] for r in load(OLD/'results/A_PREPROCESSING_STATES.json'))
    paths.update([P/'STATE_COMPATIBILITY_MATRIX.json',P/'B0_COMPATIBILITY_MATRIX.json',P/'UNIFORM_NUMERICAL_AMENDMENT.json',P/'results/FIT_JOURNAL.jsonl',OLD/'results/B_SELECTION.json',OLD/'results/PANEL_PREFIT_PLAN.json',OLD/'results/A_PREPROCESSING_STATES.json'])
    freeze={'selected_lambda':1.,'lambda_origin':'HISTORICAL_R3_B1_SELECTION','selected_seeds':selected,'task_plan_sha256':sha(OLD/'results/TASK_PLAN.json'),
            'task_origins':origins,'states':[{'path':f.relative_to(R).as_posix(),'sha256':sha(f)} for f in sorted(paths)],'all_M4_required_gates_pass':True}
    validate_m4_freeze(freeze,plan);once(P/'results/M4_SELECTION_FREEZE.json',freeze)
    once(P/'M4_REVIEW_MANIFEST.json',{'files':[{'path':(P/'results/M4_SELECTION_FREEZE.json').relative_to(R).as_posix(),'sha256':sha(P/'results/M4_SELECTION_FREEZE.json')}]})
    once(P/'results/M4_READY_FOR_INDEPENDENT_REVIEW.json',{'all_new_fits_complete':True,'E_not_accessed':True,'deadline_unchanged':True})
    return fitted

def worker():
    stage=load(P/'results/STAGE_CLAIM.json');require_phase('A')
    try:
        prepared,scalers=load_prepared()
        with patch('socket.socket.connect',side_effect=AccessStop('A fitting forbids network')):
            for task in load(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks']:
                key=(task['mouse_id'],task['panel']);run_fit(task,prepared[key],scalers[key],1.,stage)
        fitted=seal(prepared,scalers)
        while not (E/'M4_APPROVAL.json').exists():guard(stage);time.sleep(1.)
        review_binding('M4_APPROVAL.json','ACCEPTED_R4_COMPLETE_M4',P/'M4_REVIEW_MANIFEST.json')
        once(P/'results/E_BATCH_CLAIM.json',{'one_batch':True,'no_retry':True,'selection_freeze_sha256':sha(P/'results/M4_SELECTION_FREEZE.json')})
        evaluate_E(source.admitted(),prepared,scalers,fitted,load(OLD/'results/PANEL_PREFIT_PLAN.json'),stage)
        once(P/'results/WORKER_COMPLETE.json',{'M4':True,'E':True,'Final_C_D_access':False})
    except BaseException as exc:
        once(P/'results/SCIENTIFIC_STOP.json',{'type':type(exc).__name__,'message':str(exc),'scientific_status':
            'STOP_NUMERICAL_REQUIRED_GATE' if isinstance(exc,NumericalStop) else 'STOP_BUDGET' if isinstance(exc,BudgetStop) else 'STOP_ACCESS_OR_IMPLEMENTATION_REQUIRED_GATE',
            'all_later_tasks_not_executed':True,'no_retry':True,'Final_C_access':False,'Final_D_access':False})
        raise

def supervise():
    verify_prefit();stage=make_stage(172800);once(P/'results/STAGE_CLAIM.json',{'mission':MISSION,**stage})
    name=f'Local\\P16_R4_{os.getpid()}_{time.time_ns()}'
    once(P/'results/SUPERVISOR.json',{'job_name':name,'supervisor_pid':os.getpid(),'original_stage_sha256':sha(P/'results/STAGE_CLAIM.json')})
    os.environ['P16_R4_JOB']=name
    outcome=supervise_child([sys.executable,'-B','-m','paper16_development_r4.controller','worker'],stage['deadline_monotonic'],E/'SCIENTIFIC_EXECUTION.log',name,stage)
    once(P/'results/SUPERVISION.json',outcome);print(json.dumps(outcome),flush=True)


def subset_batch_inputs(inputs,ids,mask):
    flashes,running,trials,rows,original_ids=inputs
    keep=[j for j,row in enumerate(rows) if mask[row]];columns=[original_ids.tolist().index(uid) for uid in ids]
    return flashes,running,[[trials[j][u] for u in columns] for j in keep],rows[keep],np.asarray(ids,dtype=np.int64)

def make_batch(inputs,role,panel='MAIN',history=True):
    flashes,running,trials,rows,ids=inputs
    return features.build(flashes,running,trials,rows,ids,role,panel,history)

def score_bundle(bundle,batch):
    out={}
    for model,state in bundle.items():
        if model=='B0':out[model]=models.stationary_score(state,batch)
        elif model in ['D','S']:out[model]=state[0].score(state[1],batch)
        else:out[model]=sum(obj.score(x,batch) for obj,x in state)
    if not all(np.isfinite(x).all() for x in out.values()):raise NumericalStop('Required finite prediction scores')
    return out

def evaluate_E(records,prepared,scalers,fitted,plans,stage):
    import csv
    with (R/'paper16_m1/FROZEN_COHORT.csv').open(encoding='utf8',newline='') as f:cohort={r['mouse_id']:r for r in csv.DictReader(f)}
    main_results=[];panel_results=[]
    for record in records:
        guard(stage);mouse=record['source']['mouse_id'];inputs=source.native_role(record,'E',stage);batch=make_batch(inputs,'E')
        bundle=fitted[(mouse,'MAIN')];scores=score_bundle(bundle,batch);summary=controls.all_effects(scores,batch.score_mask,len(batch.unit_ids))
        summary.update({'mouse_id':mouse,'protocol':'BO' if record['source']['protocol']=='brain_observatory_1.1' else 'FC',
            'unit_ids':batch.unit_ids.tolist(),'original_presentations':batch.ordinals.tolist(),'score_exposure_seconds_per_unit':float(batch.score_mask.sum()*batch.dt),
            'source_composition':cohort[mouse],'source_observation_limit':'Curated source support, not AP packet or absence-of-unknown-artifact certification'})
        main_results.append(summary)
        arrays(P/'work/E'/mouse/'main_scores.npz',**scores)
        for panel in plans[mouse]:
            if panel['status']!='AVAILABLE':panel_results.append({'mouse_id':mouse,**panel});continue
            pi=subset_batch_inputs(inputs,panel['unit_ids'],panel['mask']);pb=make_batch(pi,'E',panel['panel'])
            ps=score_bundle(fitted[(mouse,panel['panel'])],pb)
            pr=controls.all_effects(ps,pb.score_mask,len(pb.unit_ids))
            panel_results.append({'mouse_id':mouse,'panel':panel['panel'],'status':'COMPLETED',
                'bin_seconds':pb.dt,'score_exposure_seconds_per_unit':float(pb.score_mask.sum()*pb.dt),
                'nats_per_unit_second':{k:v/pb.dt for k,v in pr['effects'].items()},
                'unit_bin_results_not_interchanged_across_bin_sizes':True,**pr})
        # Fixed-model running complete cases retain causal filter past counts.
        complete=~batch.running_missing
        coverage=load(OLD/'results/NONREFIT_COVERAGE_PLAN.json')[mouse]
        panel_results.append({'mouse_id':mouse,'panel':'S04','coverage':coverage['S04'],'status':'COMPLETED' if coverage['S04_coverage_pass'] else 'COVERAGE_FAILED',
            **controls.running_panels(scores,batch.score_mask,batch.running_missing,len(batch.unit_ids),batch.dt)})
        run_controls(mouse,inputs,batch,bundle,scores,stage)
        once(P/'results/E_mouse'/str(mouse)/'RESULT.json',summary)
    names=[a+'-'+b for a,b in CONTRASTS];values=np.array([[r['effects'][k] for k in names] for r in main_results])
    draws=np.random.Generator(np.random.PCG64(16042)).integers(0,len(values),size=(10000,len(values)))
    once(P/'results/E_DEVELOPMENT_RESULTS.json',{'mice':main_results,'effect_names':names,'equal_mouse_mean':[math.fsum(values[:,k])/len(values) for k in range(6)],
        'exploratory_whole_mouse_CI95':np.quantile(values[draws].mean(axis=1),[.025,.975],axis=0,method='linear').tolist(),'bootstrap_seed':16042,'bootstrap_replicates':10000,
        'BO_FC':controls.descriptive_groups(main_results),'scope':'EXPLORATORY_DEVELOPMENT_ONLY','Final_gate':'NOT_EXECUTED_FINAL_BOUNDARY'})
    stats=analysis_oracles.statistics(values)
    once(P/'results/E_REGISTERED_STATISTICS.json',{'effect_names':names,
        **{k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in stats.items()},
        'scope':'Exploratory Development; original sign-flip assumptions, Holm5 and LOMO retained; no Final claim classification'})
    once(P/'results/SENSITIVITY_RESULTS.json',{'refit_and_running':panel_results,
        'S03':'See fixed-policy BO/FC descriptive outputs','S08':'All main B4-B3 and B4-B2 effects retained',
        'S12':'All main D/S/C states, allseeds and D-S/N2/N3 guards retained','Final_claim_gates':'NOT_EXECUTED_FINAL_BOUNDARY'})
    once(P/'results/REFERENCE_CONTROL_RESULTS.json',controls.aggregate_references(main_results,P/'work/controls'))

def run_controls(mouse,inputs,batch,bundle,original,stage):
    flashes,running,trials,rows,ids=inputs;folder=P/'work/controls'/str(mouse);folder.mkdir(parents=True,exist_ok=False)
    names=[a+'-'+b for a,b in CONTRASTS]
    coverage=load(OLD/'results/NONREFIT_COVERAGE_PLAN.json')[str(mouse)]
    for operator,reps in [('N1',999),('N2',16),('N3',999)]:
        rng=controls.rng_for(mouse,operator);out=[]
        if operator=='N1' and not coverage['N1_available']:
            once(folder/'N1_UNAVAILABLE.json',{'reason':'Frozen stratum coverage below six before fitting','not_a_numerical_failure':True});continue
        if operator=='N3' and not coverage['N3_full_flash_support']:
            once(folder/'N3_UNAVAILABLE.json',{'reason':'Full original flash support not certified before fitting for all fixed target presentations','not_a_numerical_failure':True});continue
        for rep in range(reps):
            guard(stage)
            if operator=='N1':changed=controls.history_derangement(batch,controls.donor_map(batch,rng))
            else:
                transformed=controls.jitter_trials(flashes,trials,rows,rng) if operator=='N2' else controls.shift_trials(flashes,trials,rows,rng)
                changed=features.build(flashes,running,transformed,rows,ids,'E')
            score=score_bundle(bundle,changed)
            if operator=='N2':controls.n2_check(batch,changed,original,score)
            result=controls.all_effects(score,changed.score_mask,len(ids));out.append(result)
            event(folder/(operator+'.jsonl'),replicate=rep,**result)
        arrays(folder/(operator+'.npz'),effects=np.array([[r['effects'][k] for k in names] for r in out]),absolute=np.array([[r['absolute'][k] for k in MODELS] for r in out]))
    n4=[]
    contract=load(R/'paper16_precision_contract_r1/PRECISION_CONTRACT.json')
    for mapping in contract['N4']['operators']:
        guard(stage);changed=replace(batch,raw=features.wrong_map(batch,mapping['color_flip'],mapping['time_rotation']))
        score=score_bundle({'B1':bundle['B1']},changed)
        n4.append({**mapping,'B1_logscore':float(score['B1'].sum()/batch.y.size)})
    once(folder/'N4.json',{'operators':n4,'refit':False,'p_value':'NOT_APPLICABLE'})
    once(P/'results/control_mouse'/str(mouse)/'RESULT.json',{'mouse_id':mouse,'N1_replicates':0 if (folder/'N1_UNAVAILABLE.json').exists() else 999,'N2_replicates':16,
        'N3_replicates':0 if (folder/'N3_UNAVAILABLE.json').exists() else 999,'N4_operators':11,'N1_N3_are_approximate_descriptive_references':True})



if __name__=='__main__':{'supervise':supervise,'worker':worker}[sys.argv[1]]()
