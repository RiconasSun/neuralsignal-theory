"""One externally bounded R2 scientific stage; actual certificates gate B and E."""
import hashlib,json,math,os,sys,time
from dataclasses import replace
import numpy as np
from .core import *
from . import source,features,models,optimizer,panels,controls
from paper16_dev_r3.run_m2 import supervise_child

def task_folder(task):return P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()

def verify_prefit():
    verify_pins();approval=load(E/'PREFIT_APPROVAL.json');manifest=load(P/'PREFIT_FREEZE_MANIFEST.json')
    if approval.get('decision')!='ACCEPTED_R2_PRODUCTION_PREFIT' or approval.get('open_P0')!=0 or approval.get('open_P1')!=0:raise AccessStop('Actual independent production prefit acceptance required')
    if sha(E/'PREFIT_REVIEW.md')!=approval['review_sha256'] or sha(P/'PREFIT_FREEZE_MANIFEST.json')!=approval['manifest_sha256']:raise AccessStop('Prefit acceptance identity')
    for row in manifest['files']:
        if sha(R/row['path'])!=row['sha256']:raise AccessStop('Reviewed production/test/registration changed: '+row['path'])
    required={'core.py','source.py','features.py','models.py','optimizer.py','optim_child.py','controller.py','panels.py','controls.py','test_production.py','certify.py','ACCESS_REGISTRATION.json','SOURCE_PINS.json'}
    if not {'paper16_development_r2/'+x for x in required}<={x['path'] for x in manifest['files']}:raise AccessStop('Incomplete production approval coverage')
    cert=load(P/'PRODUCTION_NUMERICAL_CERTIFICATION.json')
    if not cert['mandatory_tests_pass'] or cert['real_fits_executed']!=0:raise AccessStop('Actual synthetic production certification required before real stage')
    return approval

def verify_completed(tasks):
    for task in tasks:
        folder=task_folder(task);result=load(folder/'RESULT.json');diag=load(folder/'DIAGNOSTICS.json')
        if result['task']!=task or not result['numerical_pass'] or result['projected_gradient_inf']>1e-5:raise AccessStop('Missing/failed exact numerical fit certificate')
        if result['external_value_gradient_pairs']>6000 or result['external_accepted_iterations']>1500:raise AccessStop('Fit external budget certificate')
        if sha(folder/'DIAGNOSTICS.json')!=result['diagnostic_state_sha256'] or sha(R/result['endpoint_state']['path'])!=result['endpoint_state']['sha256']:raise AccessStop('Numerical endpoint/diagnostics state changed')
        if not diag['all_checkpoints_pass'] or len(diag['checkpoints'])!=3 or diag['FD_objective_calls']!=24*diag['free_coordinates'] or diag['AD_calls']!=3 or diag['analytic_checkpoint_calls']!=3:raise AccessStop('Incomplete frozen diagnostics')
        if sha(R/diag['coordinate_state']['path'])!=diag['coordinate_state']['sha256']:raise AccessStop('Coordinate diagnostics changed')
        for check in diag['checkpoints']:
            if check['AD_scaled_coordinate_error_max']>1e-8 or check['frozen_FD_scaled_error']>2e-5 or not check['pass']:raise AccessStop('Frozen gradient gate failed')

def validate_m4_freeze(freeze,plan):
    prepared=load(P/'results/A_PREPROCESSING_STATES.json');panel_plan=load(P/'results/PANEL_PREFIT_PLAN.json')
    if plan!=panels.task_plan(source.admitted(),panel_plan):raise AccessStop('Task schedule no longer equals all required models/seeds/panels')
    expected_keys={(str(r['source']['mouse_id']),'MAIN') for r in source.admitted()}
    expected_keys|={(mouse,panel['panel']) for mouse,rows in panel_plan.items() for panel in rows if panel['status']=='AVAILABLE'}
    if {(r['key'].split('/')[0],r['panel']) for r in prepared}!=expected_keys or len(prepared)!=len(expected_keys):raise AccessStop('Incomplete A/scaler/panel state manifest')
    expected={row['path'] for row in prepared}
    expected|={(P/'results'/name).relative_to(R).as_posix() for name in ['TASK_PLAN.json','PANEL_PREFIT_PLAN.json','NONREFIT_COVERAGE_PLAN.json','A_PREPROCESSING_STATES.json','FIT_JOURNAL.jsonl','B_SELECTION.json']}
    expected|={r['score_state']['path'] for r in load(P/'results/B_SELECTION.json')['records']}
    for task in plan['tasks']:
        folder=task_folder(task)
        needed=['ATTEMPT.json','RESULT.json','DIAGNOSTICS.json','endpoint.npz','coordinate_certificates.npz','initial.npz','CLIENT.json','CLIENT_STDERR.log','CALLS.jsonl']
        if load(folder/'RESULT.json')['external_accepted_iterations']>0:needed.append('ACCEPTED.jsonl')
        expected|={(folder/n).relative_to(R).as_posix() for n in needed}
    for record in source.admitted():
        mouse=record['source']['mouse_id']
        for uid in record['selection']['selected_unit_ids']:
            folder=P/'work/B0'/mouse/str(uid);result=load(folder/'RESULT.json');diag=load(folder/'DIAGNOSTICS.json')
            if not result['numeric_pass'] or result['projected_gradient_inf']>1e-5 or not diag['all_checkpoints_pass']:raise AccessStop('Incomplete/failed required analytic B0 state')
            expected|={(folder/n).relative_to(R).as_posix() for n in ['RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz']}
    if {r['path'] for r in freeze['states']}!=expected or len(freeze['states'])!=len(expected):raise AccessStop('Full M4 state/file completeness mismatch')
    for row in freeze['states']:
        if sha(R/row['path'])!=row['sha256']:raise AccessStop('Frozen model/preprocessing/journal state changed')
    expected_latent={(key[0],key[1],model) for key in expected_keys for model in ['D','S']}
    if {(r['mouse_id'],r['panel'],r['model']) for r in freeze['selected_seeds']}!=expected_latent:raise AccessStop('Missing D/S seed-selection states')
    for row in freeze['selected_seeds']:
        if analysis_oracles.select_seed(row['all_seeds'])!=row['seed']:raise AccessStop('Training-only seed selection differs')

def require_phase(role):
    if role not in ['A','B','E']:raise AccessStop('Final/unregistered phase denied')
    verify_prefit();stage=load(P/'results/STAGE_CLAIM.json');verify_stage_environment(stage)
    claim=load(P/'results/SUPERVISOR.json');require_job(claim['job_name'])
    if os.environ.get('P16_R2_JOB')!=claim['job_name']:raise AccessStop('Wrong scientific worker Job identity')
    if role in ['B','E']:
        plan=load(P/'results/TASK_PLAN.json');tasks=plan['tasks']
        selection=[t for t in tasks if t['panel']=='MAIN' and t['model']=='B1' and t['lambda'] in GRID]
        if len(selection)!=648:raise AccessStop('Exact all-mouse B1 A-grid completeness')
        verify_completed(selection)
        if role=='E':
            freeze=load(P/'results/M4_SELECTION_FREEZE.json');verify_completed(tasks)
            if freeze['task_plan_sha256']!=sha(P/'results/TASK_PLAN.json') or freeze['B_selection_sha256']!=sha(P/'results/B_SELECTION.json') or freeze['panel_plan_sha256']!=sha(P/'results/PANEL_PREFIT_PLAN.json'):raise AccessStop('M4 selection/plan freeze changed')
            validate_m4_freeze(freeze,plan)
            if not (P/'results/E_BATCH_CLAIM.json').exists():raise AccessStop('One E batch not claimed')
            if load(P/'results/E_BATCH_CLAIM.json')['selection_freeze_sha256']!=sha(P/'results/M4_SELECTION_FREEZE.json'):raise AccessStop('E claim/freeze identity changed')

def subset_batch_inputs(inputs,ids,mask):
    flashes,running,trials,rows,original_ids=inputs
    keep=[j for j,row in enumerate(rows) if mask[row]];columns=[original_ids.tolist().index(uid) for uid in ids]
    return flashes,running,[[trials[j][u] for u in columns] for j in keep],rows[keep],np.asarray(ids,dtype=np.int64)

def make_batch(inputs,role,panel='MAIN',history=True):
    flashes,running,trials,rows,ids=inputs
    return features.build(flashes,running,trials,rows,ids,role,panel,history)

def persist_batch(key,batch,scaler):
    path=P/'work/prepared'/key/'state.npz'
    receipt=arrays(path,raw=batch.raw,y=batch.y,ordinals=batch.ordinals,unit_ids=batch.unit_ids,colors=batch.colors,
        running_missing=batch.running_missing,score_mask=batch.score_mask,
        mean=scaler.mean,scale=scaler.scale,active=scaler.active)
    return {'key':key,'role':'A','panel':batch.panel,'dt':batch.dt,'psth':batch.psth,'b1':batch.b1,**receipt}

def run_fit(task,batch,scaler,lam,stage):
    plan=load(P/'results/TASK_PLAN.json')
    if task not in plan['tasks']:raise AccessStop('Unregistered optimizer task')
    journal=P/'results/FIT_JOURNAL.jsonl';old=source.CacheReader._journal(journal)
    if any(x['event']=='ATTEMPTED' and x['task']['id']==task['id'] for x in old):raise AccessStop('Optimizer attempt already consumed; no retry')
    if sum(x['event']=='ATTEMPTED' for x in old)>=plan['optimizer_attempt_count']:raise BudgetStop('Exact R2 optimizer task allocation exhausted')
    guard(stage);event(journal,event='ATTEMPTED',task=task)
    unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id'])
    try:
        obj=models.Objective(batch,scaler,task['model'],lam,unit,task['seed'])
        x,result=optimizer.fit(obj,task_folder(task),stage,task)
        event(journal,event='COMPLETED',task=task,objective=result['objective'],PG=result['projected_gradient_inf'],
            calls=result['external_value_gradient_pairs'],iterations=result['external_accepted_iterations'],
            result_path=(task_folder(task)/'RESULT.json').relative_to(R).as_posix(),result_sha256=sha(task_folder(task)/'RESULT.json'))
        return obj,x,result
    except BaseException as exc:
        event(journal,event='FAILED',task=task,error_type=type(exc).__name__,message=str(exc),retry=False);raise

def score_bundle(bundle,batch):
    out={}
    for model,state in bundle.items():
        if model=='B0':out[model]=models.stationary_score(state,batch)
        elif model in ['D','S']:out[model]=state[0].score(state[1],batch)
        else:out[model]=sum(obj.score(x,batch) for obj,x in state)
    if not all(np.isfinite(x).all() for x in out.values()):raise NumericalStop('Required finite prediction scores')
    return out

def worker():
    verify_prefit();claim=load(P/'results/SUPERVISOR.json');require_job(claim['job_name'])
    stage=load(P/'results/STAGE_CLAIM.json');verify_stage_environment(stage)
    records=source.admitted();prepared={};plans={};inputs_by={};state_receipts=[];coverage_plan={}
    try:
        # A features first; exact prefit panel schedule before any model/scaler fit.
        for record in records:
            guard(stage);mouse=record['source']['mouse_id'];inputs=source.saved_A(record);inputs_by[mouse]=inputs
            main=make_batch(inputs,'A');prepared[(mouse,'MAIN')]=main
            arrays(P/'work/prepared_raw'/mouse/'MAIN.npz',raw=main.raw,y=main.y,ordinals=main.ordinals,unit_ids=main.unit_ids)
            plans[mouse]=panels.prefit_plan(record,main,inputs[0],inputs[1])
            flashes,running=inputs[:2];mask=np.asarray(record['selection']['common_mask'],bool)
            running_cells={}
            for role,lo,hi in [('A',0,90),('B',90,120),('E',120,150)]:
                for color in [-1,1]:
                    n=int(np.count_nonzero(mask[lo:hi]&(flashes['color'][lo:hi]==color)&np.any(~running['missing'][lo:hi],axis=1)))
                    running_cells[role+':'+str(color)]={'presentations':n,'minimum':8,'pass':n>=8}
            e_rows=np.flatnonzero(mask&(np.arange(150)>=120))
            coverage_plan[mouse]={'S04':running_cells,'S04_coverage_pass':all(v['pass'] for v in running_cells.values()),
                'N1_stratum_counts':{str(c):int(np.count_nonzero(flashes['color'][e_rows]==c)) for c in [-1,1]},
                'N1_available':all(np.count_nonzero(flashes['color'][e_rows]==c)>=6 for c in [-1,1]),
                'N3_full_flash_support':bool(np.all(panels.full_support(flashes,running)[e_rows])),
                'defined_before_any_optimizer_fit_or_B_E_outcome_access':True}
            for panel in plans[mouse]:
                if panel['status']!='AVAILABLE':continue
                panel_inputs=subset_batch_inputs(inputs,panel['unit_ids'],panel['mask'])
                prepared[(mouse,panel['panel'])]=make_batch(panel_inputs,'A',panel['panel'])
                pb=prepared[(mouse,panel['panel'])]
                arrays(P/'work/prepared_raw'/mouse/(panel['panel']+'.npz'),raw=pb.raw,y=pb.y,ordinals=pb.ordinals,unit_ids=pb.unit_ids)
            event(P/'results/PREPROCESSING.jsonl',mouse_id=mouse,main_A_feature_identity=main.identity(),panels_prepared=[p['panel'] for p in plans[mouse] if p['status']=='AVAILABLE'],real_optimizer_attempts=0)
        once(P/'results/PANEL_PREFIT_PLAN.json',plans)
        once(P/'results/NONREFIT_COVERAGE_PLAN.json',coverage_plan)
        plan=panels.task_plan(records,plans);once(P/'results/TASK_PLAN.json',plan)
        scalers={}
        for (mouse,panel),batch in prepared.items():
            guard(stage);scaler=features.Scaling.fit(batch);scalers[(mouse,panel)]=scaler
            state_receipts.append(persist_batch(mouse+'/'+panel,batch,scaler))
        once(P/'results/A_PREPROCESSING_STATES.json',state_receipts)
        tasks=plan['tasks'];grid_states={};fitted={}
        # All648 relevant A candidates must be certified before any B outcome.
        for task in tasks:
            if task['panel']=='MAIN' and task['model']=='B1':
                mouse=task['mouse_id'];obj,x,_=run_fit(task,prepared[(mouse,'MAIN')],scalers[(mouse,'MAIN')],task['lambda'],stage)
                grid_states.setdefault((mouse,task['lambda']),[]).append((obj,x))
        selection_records=[]
        for record in records:
            guard(stage);mouse=record['source']['mouse_id'];b_inputs=source.native_role(record,'B',stage)
            b=make_batch(b_inputs,'B',history=False)
            for lam in GRID:
                values=sum(obj.score(x,b) for obj,x in grid_states[(mouse,lam)])
                score_state=arrays(P/'work/B_selection'/mouse/(str(lam)+'.npz'),logscore_bins=values,ordinals=b.ordinals,unit_ids=b.unit_ids,mask=b.score_mask)
                selection_records.append({'mouse_id':mouse,'protocol':'BO' if record['source']['protocol']=='brain_observatory_1.1' else 'FC',
                    'lambda':lam,'logscore':float(values.sum()/b.y.size),'actual_valid_unit_bins':int(b.y.size),'score_state':score_state})
        lam=analysis_oracles.select_lambda(selection_records)
        once(P/'results/B_SELECTION.json',{'selected_lambda':lam,'records':selection_records,'selection_information':'B1_UNPENALIZED_ONLY','BO_FC_weights':[.5,.5]})
        for record in records:
            mouse=record['source']['mouse_id'];batch=prepared[(mouse,'MAIN')]
            fitted[(mouse,'MAIN')]={'B1':grid_states[(mouse,lam)]}
            theta=models.stationary(batch)
            for u,uid in enumerate(batch.unit_ids):
                folder=P/'work/B0'/mouse/str(uid);folder.mkdir(parents=True,exist_ok=False)
                objective=models.StationaryObjective(batch,u)
                diagnostic=optimizer.certificate(objective,[objective.x0.copy()]*3,folder,stage)
                with np.load(folder/'coordinate_certificates.npz',allow_pickle=False) as data:g=data['endpoint_analytic'].copy()
                pg=float(np.abs(spec.projected_gradient(objective.x0,g,objective.lo,objective.hi)).max())
                once(folder/'RESULT.json',{'unit_id':int(uid),'projected_gradient_inf':pg,'numeric_pass':pg<=1e-5 and diagnostic['all_checkpoints_pass'],'analytic_MLE_not_optimizer_attempt':True})
                if pg>1e-5 or not diagnostic['all_checkpoints_pass']:raise NumericalStop('Required B0 analytic certificate failed')
            fitted[(mouse,'MAIN')]['B0']=theta
        latent_candidates={}
        for task in tasks:
            if task['panel']=='MAIN' and task['model']=='B1':continue
            key=(task['mouse_id'],task['panel']);bundle=fitted.setdefault(key,{})
            obj,x,result=run_fit(task,prepared[key],scalers[key],lam,stage)
            if task['model'] in ['D','S']:
                latent_candidates.setdefault((key,task['model']),[]).append((obj,x,result))
            else:bundle.setdefault(task['model'],[]).append((obj,x))
        selected_seeds=[]
        for (key,model),candidates in latent_candidates.items():
            rows=[{'seed':c[2]['task']['seed'],'numerical_pass':c[2]['numerical_pass'],'objective':c[2]['objective']} for c in candidates]
            chosen=analysis_oracles.select_seed(rows);obj,x,result=next(c for c in candidates if c[2]['task']['seed']==chosen)
            fitted[key][model]=(obj,x);selected_seeds.append({'mouse_id':key[0],'panel':key[1],'model':model,'seed':chosen,'all_seeds':rows})
        verify_completed(tasks)
        if any(set(fitted[(r['source']['mouse_id'],'MAIN')])!=set(MODELS) for r in records):raise ImplementationStop('Mandatory eight main-model state completeness')
        frozen=[]
        for row in state_receipts:frozen.append({'path':row['path'],'sha256':row['sha256']})
        for task in tasks:
            folder=task_folder(task)
            for path in folder.iterdir():
                if path.is_file():frozen.append({'path':path.relative_to(R).as_posix(),'sha256':sha(path)})
        for path in (P/'work/B0').rglob('*'):
            if path.is_file():frozen.append({'path':path.relative_to(R).as_posix(),'sha256':sha(path)})
        for name in ['TASK_PLAN.json','PANEL_PREFIT_PLAN.json','NONREFIT_COVERAGE_PLAN.json','A_PREPROCESSING_STATES.json','FIT_JOURNAL.jsonl','B_SELECTION.json']:
            path=P/'results'/name;frozen.append({'path':path.relative_to(R).as_posix(),'sha256':sha(path)})
        for row in selection_records:
            frozen.append({'path':row['score_state']['path'],'sha256':row['score_state']['sha256']})
        freeze={'selected_lambda':lam,'selected_seeds':selected_seeds,
            'task_plan_sha256':sha(P/'results/TASK_PLAN.json'),'B_selection_sha256':sha(P/'results/B_SELECTION.json'),
            'panel_plan_sha256':sha(P/'results/PANEL_PREFIT_PLAN.json'),'states':frozen,'all_M4_required_gates_pass':True}
        validate_m4_freeze(freeze,plan);once(P/'results/M4_SELECTION_FREEZE.json',freeze)
        once(P/'results/E_BATCH_CLAIM.json',{'one_batch':True,'selection_freeze_sha256':sha(P/'results/M4_SELECTION_FREEZE.json'),'no_retry':True})
        evaluate_E(records,prepared,scalers,fitted,plans,stage)
        once(P/'results/WORKER_COMPLETE.json',{'M3':True,'M4':True,'M5':True,'selected_lambda':lam,'Final_C_access':False,'Final_D_access':False})
    except BaseException as exc:
        once(P/'results/SCIENTIFIC_STOP.json',{'type':type(exc).__name__,'message':str(exc),
            'scientific_status':'STOP_NUMERICAL_REQUIRED_GATE' if isinstance(exc,NumericalStop) else 'STOP_BUDGET' if isinstance(exc,BudgetStop) else 'STOP_ACCESS_OR_IMPLEMENTATION_REQUIRED_GATE',
            'all_later_tasks_not_executed':True,'no_retry':True,'Final_C_access':False,'Final_D_access':False})
        raise

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
        coverage=load(P/'results/NONREFIT_COVERAGE_PLAN.json')[mouse]
        panel_results.append({'mouse_id':mouse,'panel':'S04','coverage':coverage['S04'],'status':'COMPLETED' if coverage['S04_coverage_pass'] else 'COVERAGE_FAILED',
            'result':controls.all_effects(scores,complete,len(batch.unit_ids)) if np.any(complete) else None})
        run_controls(mouse,inputs,batch,bundle,scores,stage)
        once(P/'results/E_mouse'/str(mouse)/'RESULT.json',summary)
    names=[a+'-'+b for a,b in CONTRASTS];values=np.array([[r['effects'][k] for k in names] for r in main_results])
    draws=np.random.Generator(np.random.PCG64(16042)).integers(0,len(values),size=(10000,len(values)))
    once(P/'results/E_DEVELOPMENT_RESULTS.json',{'mice':main_results,'effect_names':names,'equal_mouse_mean':[math.fsum(values[:,k])/len(values) for k in range(6)],
        'exploratory_whole_mouse_CI95':np.quantile(values[draws].mean(axis=1),[.025,.975],axis=0,method='linear').tolist(),'bootstrap_seed':16042,'bootstrap_replicates':10000,
        'BO_FC':controls.descriptive_groups(main_results),'scope':'EXPLORATORY_DEVELOPMENT_ONLY','Final_gate':'NOT_EXECUTED_FINAL_BOUNDARY'})
    once(P/'results/SENSITIVITY_RESULTS.json',{'refit_and_running':panel_results,
        'S03':'See fixed-policy BO/FC descriptive outputs','S08':'All main B4-B3 and B4-B2 effects retained',
        'S12':'All main D/S/C states, allseeds and D-S/N2/N3 guards retained','Final_claim_gates':'NOT_EXECUTED_FINAL_BOUNDARY'})
    once(P/'results/REFERENCE_CONTROL_RESULTS.json',controls.aggregate_references(main_results,P/'work/controls'))

def run_controls(mouse,inputs,batch,bundle,original,stage):
    flashes,running,trials,rows,ids=inputs;folder=P/'work/controls'/str(mouse);folder.mkdir(parents=True,exist_ok=False)
    names=[a+'-'+b for a,b in CONTRASTS]
    coverage=load(P/'results/NONREFIT_COVERAGE_PLAN.json')[str(mouse)]
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

def supervise():
    verify_prefit();stage=make_stage(172800);once(P/'results/STAGE_CLAIM.json',{'mission':MISSION,**stage})
    name=f'Local\\P16_R2_{os.getpid()}_{time.time_ns()}'
    once(P/'results/SUPERVISOR.json',{'job_name':name,'supervisor_pid':os.getpid(),'original_stage_sha256':sha(P/'results/STAGE_CLAIM.json')})
    os.environ['P16_R2_JOB']=name
    result=supervise_child([sys.executable,'-B','-m','paper16_development_r2.controller','worker'],stage['deadline_monotonic'],E/'SCIENTIFIC_EXECUTION.log',name,stage)
    result['science_complete']=bool(result['returncode']==0 and (P/'results/WORKER_COMPLETE.json').exists())
    once(P/'results/SUPERVISION.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':{'supervise':supervise,'worker':worker}[sys.argv[1]]()
