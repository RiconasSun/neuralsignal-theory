"""Closed-stage saved-only R4 verification. Never calls objectives or scorers."""
import hashlib
import json
import math
import socket
from pathlib import Path
from unittest.mock import patch
import numpy as np
from paper16_termination_feasibility1 import reproduce as prior

R=Path(__file__).resolve().parents[1]
P=R/'paper16_development_r4'
OLD=R/'paper16_development_r3'
load,sha,require,rows=prior.load,prior.sha,prior.require,prior.rows


def identities(manifest):
    for row in manifest['files']:
        path=R/row['path']
        require(path.is_file() and sha(path)==row['sha256'],'Saved identity: '+row['path'])
        if 'bytes' in row:require(path.stat().st_size==row['bytes'],'Saved byte size')


def strict_journal(journal):
    attempts=[];terminals={};active=None;stopped=False
    for row in journal:
        event=row.get('event');task=row.get('task',{});tid=task.get('id')
        require(event in ['ATTEMPTED','COMPLETED','FAILED'] and isinstance(tid,str),'Typed fit event')
        if event=='ATTEMPTED':
            require(active is None and not stopped and tid not in {r['task']['id'] for r in attempts},'Serial one-attempt/no work after failure')
            attempts.append(row);active=task
        else:
            require(active==task and tid not in terminals,'Terminal event exact active task')
            terminals[tid]=row;active=None
            if event=='FAILED':
                require(row.get('retry') is False and bool(row.get('error_type')) and isinstance(row.get('message'),str),'Actual typed failure')
                stopped=True
    return attempts,terminals,active


def abnormal(sup):
    require(type(sup.get('returncode')) is int and type(sup.get('killed_at_deadline')) is bool
            and type(sup.get('completed_before_deadline')) is bool,'Typed actual native supervision')
    require(sup.get('native_job_tree_enforced') is True and sup.get('assigned_before_resume') is True,
            'Actual assign-before-resume native Job evidence')
    return sup['returncode']!=0 or sup['killed_at_deadline'] or not sup['completed_before_deadline'] or bool(sup.get('clock_failure'))


def accepted_prefix(calls,accepted,initial):
    p=len(initial['x0']);nr,nd=prior.call_prefix(calls,p)
    require(all(initial[k].shape==(p,) and np.isfinite(initial[k]).all() for k in ['x0','lo','hi'])
            and np.all(initial['lo']<=initial['x0']) and np.all(initial['x0']<=initial['hi']),'Valid saved initializer/bounds')
    require([r['iteration'] for r in accepted]==list(range(1,len(accepted)+1))
            and len(accepted)<=1500 and len(accepted)<=nd,'Accepted prefix accounting')
    assoc={}
    for i in range(nd):
        a,b=calls[2*i:2*i+2];x=np.asarray(a['x'])
        require(a['iterations']<=len(accepted) and np.all(x>=initial['lo']-1e-12)
                and np.all(x<=initial['hi']+1e-12),'Saved FG prefix bounds/counter')
        assoc[a['iterations']]=x
    for index,row in enumerate(accepted):
        x=np.asarray(row['x'])
        require(x.shape==(p,) and np.isfinite(x).all() and np.all(x>=initial['lo']-1e-12)
                and np.all(x<=initial['hi']+1e-12) and index in assoc and np.array_equal(x,assoc[index]),
                'Saved accepted vector exact completed FG association')
    return nr,nd


def pre_fit_prefix(folder):
    forbidden=['CLIENT.json','CALLS.jsonl','ACCEPTED.jsonl','DIAGNOSTIC_CALLS.jsonl',
               'DIAGNOSTICS.json','coordinate_certificates.npz','endpoint.npz','RESULT.json']
    require(not any((folder/name).exists() for name in forbidden),'Pre-fit interruption cannot hide existing evaluations/endpoints')


def scalar_effects(row,models,names):
    require(set(row['absolute'])==set(models) and set(row['effects'])==set(names),'Exact registered model/contrast keys')
    require(all(math.isfinite(v) for v in row['absolute'].values())
            and all(math.isfinite(v) for v in row['effects'].values()),'Finite saved model scores/effects')
    for name in names:
        a,b=name.split('-')
        require(abs(row['effects'][name]-(row['absolute'][a]-row['absolute'][b]))<=1e-12,
                'Saved effect agrees with absolute score differences')


def n2_invariant(reference,observed):
    require(all(math.isfinite(reference['absolute'][model])
                and abs(reference['absolute'][model]-observed['absolute'][model])<=1e-12
                for model in ['B0','B1','B2','B3','B4','D','S']),
            'Independently verified saved N2 invariant model summaries')


def exports(access,account):
    observed=[r for r in access if r['role']=='E'];by={r['source']['session_id']:r for r in account.values()}
    require(len(observed)==len({r['session_id'] for r in observed}) and all(r['session_id'] in by for r in observed),
            'No duplicate/unregistered E source export')
    for row in observed:
        record=by[row['session_id']];mask=np.asarray(record['selection']['common_mask'],bool)
        ordinals=np.flatnonzero(mask&(np.arange(150)>=120));ids=np.asarray(record['selection']['selected_unit_ids'],dtype=np.int64)
        require(row['event']=='SCOPED_NATIVE_EXPORT' and row['units']==ids.tolist()
                and row['ordinals']==ordinals.tolist() and row['exported_other_roles'] is False,'Exact frozen E export support')
        capture=row['protected_role_capture'];path=P/'work/roles'/str(row['session_id'])/'E.npz'
        require(R/capture['path']==path and sha(path)==capture['sha256'],'E capture exact path/hash without decoding neural values')
        for key,value in [('original_ordinals',ordinals),('unit_ids',ids)]:
            require(capture['arrays'][key]['sha256']==hashlib.sha256(value.tobytes()).hexdigest()
                    and capture['arrays'][key]['shape']==list(value.shape),'E capture ordinal/unit identities')
        audit=load(P/'results/source_access'/str(row['session_id'])/'E.json')
        require(audit['role']=='E' and audit['original_ordinals']==ordinals.tolist(),'Source access journal export join')
    return len(observed)


def checked_review(name,decision,manifest):
    e=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4'
    a=load(e/name)
    require(a['decision']==decision and a['open_P0']==a['open_P1']==0,'Actual independent gate acceptance')
    path=R/a['review_path'];require(path.resolve().is_relative_to(e.resolve()) and sha(path)==a['review_sha256'],'Independent review identity')
    require(sha(manifest)==a['manifest_sha256'],'Review/manifest binding');identities(load(manifest))
    return a


def verify_m4():
    checked_review('M4_APPROVAL.json','ACCEPTED_R4_COMPLETE_M4',P/'M4_REVIEW_MANIFEST.json')
    freeze=load(P/'results/M4_SELECTION_FREEZE.json');plan=load(OLD/'results/TASK_PLAN.json')
    require(freeze['task_plan_sha256']==sha(OLD/'results/TASK_PLAN.json') and freeze['selected_lambda']==1.
            and freeze['lambda_origin']=='HISTORICAL_R3_B1_SELECTION','Original full plan/consumed lambda')
    origins=freeze['task_origins'];require(len(origins)==6471 and {r['task_id'] for r in origins}=={r['id'] for r in plan['tasks']},'All6471 unique task origins')
    old={r['task_id']:r for r in load(P/'STATE_COMPATIBILITY_MATRIX.json')['states'] if r['status']=='COMPATIBLE'}
    required=set();latent={}
    for task in plan['tasks']:
        origin=next(r for r in origins if r['task_id']==task['id'])
        expected=(R/old[task['id']]['result_path']).parent if task['id'] in old else P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
        path=R/origin['result_path'];require(path==expected/'RESULT.json' and sha(path)==origin['result_sha256'],'Every exact M4 result binding')
        require(origin['origin']==('R3_GENERATED_FTOL1E-12_ADMITTED_R4' if task['id'] in old else 'R4_FTOL0'),'Historical execution labels')
        result=load(path);require(result['task']==task and result['numerical_pass'] is True and result['projected_gradient_inf']<=1e-5,'All M4 required numerical gates')
        names=['ATTEMPT.json','initial.npz','CLIENT.json','CLIENT_STDERR.log','CALLS.jsonl','RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz','endpoint.npz']
        if result['nit']>0:names.append('ACCEPTED.jsonl')
        if task['id'] not in old:names.append('DIAGNOSTIC_CALLS.jsonl')
        required.update((expected/name).relative_to(R).as_posix() for name in names)
        if task['model'] in ['D','S']:latent.setdefault((task['mouse_id'],task['panel'],task['model']),[]).append(result)
    preps=load(OLD/'results/A_PREPROCESSING_STATES.json');required.update(r['path'] for r in preps)
    b0=load(P/'B0_COMPATIBILITY_MATRIX.json')['states'];require(len(b0)==216 and all(r['status']=='COMPATIBLE' for r in b0),'All216 admitted B0')
    for row in b0:
        folder=(R/row['result_path']).parent
        required.update((folder/name).relative_to(R).as_posix() for name in ['RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz'])
    states=freeze['states'];actual={r['path'] for r in states};require(len(actual)==len(states) and required<=actual,'Complete M4 state inventory')
    identities({'files':states})
    chosen={(r['mouse_id'],r['panel'],r['model']):r for r in freeze['selected_seeds']}
    require(len(chosen)==len(freeze['selected_seeds']) and set(chosen)==set(latent),'All D/S panel seeds')
    for key,results in latent.items():
        all_seeds=[{'seed':r['task']['seed'],'numerical_pass':r['numerical_pass'],'objective':r['objective']} for r in results]
        require(sorted(r['seed'] for r in all_seeds)==[11,23,37] and chosen[key]['all_seeds']==all_seeds,'All3 required seed attempts')
        minimum=min(r['objective'] for r in all_seeds);expected=min(r['seed'] for r in all_seeds if r['objective']<=minimum+1e-12)
        require(chosen[key]['seed']==expected,'Original A objective/tie seed rule')
    return freeze


def verify_E():
    freeze=verify_m4();claim=load(P/'results/E_BATCH_CLAIM.json')
    require(claim['one_batch'] is True and claim['no_retry'] is True
            and claim['selection_freeze_sha256']==sha(P/'results/M4_SELECTION_FREEZE.json'),'One E claim exact accepted M4 binding')
    summary=load(P/'results/E_DEVELOPMENT_RESULTS.json');records=summary['mice']
    account={r['source']['mouse_id']:r for r in load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']}
    require(len(records)==27 and [r['mouse_id'] for r in records]==sorted(account,key=int),'Every original27 E mouse')
    models=['B0','B1','B2','B3','B4','C','D','S'];names=['B4-B1','B4-B2','B4-B3','D-B4','C-B4','D-S']
    require(summary['effect_names']==names,'All6 fixed effects')
    for row in records:
        record=account[row['mouse_id']];ids=record['selection']['selected_unit_ids'];mask=np.asarray(record['selection']['common_mask'],bool)
        ordinals=np.flatnonzero(mask & (np.arange(150)>=120)).tolist()
        require(row['unit_ids']==ids and row['original_presentations']==ordinals
                and row['actual_valid_unit_bins']==len(ids)*len(ordinals)*6,'Exact E targets/unit-bin denominator')
        scalar_effects(row,models,names)
        with np.load(P/'work/E'/row['mouse_id']/'main_scores.npz',allow_pickle=False) as a:
            require(set(a.files)==set(models),'Complete saved E score bundle')
            for model in models:
                require(a[model].shape==(len(ordinals),6) and np.isfinite(a[model]).all()
                        and float(a[model].sum()/row['actual_valid_unit_bins'])==row['absolute'][model],'Saved E scores/aggregate')
            for pair in names:
                first,second=pair.split('-')
                require(float((a[first]-a[second]).sum()/row['actual_valid_unit_bins'])==row['effects'][pair],'Saved matched E effect')
    from paper16_development_r3.reproduce import verify_statistics
    cohort={m:'BO' if r['source']['protocol']=='brain_observatory_1.1' else 'FC' for m,r in account.items()}
    verify_statistics(summary,cohort)
    from paper16_m1.code.analysis_oracles import statistics
    values=np.asarray([[r['effects'][n] for n in names] for r in records]);stats=statistics(values)
    saved=load(P/'results/E_REGISTERED_STATISTICS.json');require(saved['effect_names']==names,'Registered statistics labels')
    for k,v in stats.items():require(saved[k]==(v.tolist() if isinstance(v,np.ndarray) else v),'Original signflip/Holm/CI/LOMO saved arithmetic')
    panel_plan=load(OLD/'results/PANEL_PREFIT_PLAN.json');sensitivity=load(P/'results/SENSITIVITY_RESULTS.json')
    sens=sensitivity['refit_and_running'];by={(r['mouse_id'],r['panel']):r for r in sens}
    expected={(m,r['panel']) for m,panels in panel_plan.items() for r in panels}|{(m,'S04') for m in account}
    require(len(by)==len(sens) and set(by)==expected,'All original sensitivity cells; no dropped unavailable panels')
    for m,panels in panel_plan.items():
        for panel in panels:
            row=by[(m,panel['panel'])]
            if panel['status']!='AVAILABLE':require(row=={'mouse_id':m,**panel},'Original unavailable panel reason preserved')
            else:
                bins=12 if panel['panel']=='S01' else 6;dt=.01 if bins==12 else .02
                denominator=int(np.count_nonzero(np.asarray(panel['mask'])[120:]))*bins*len(panel['unit_ids'])
                require(row['status']=='COMPLETED' and row['actual_valid_unit_bins']==denominator
                        and row['bin_seconds']==dt and set(row['absolute'])=={'B1','B4','C','D','S'},'All applicable frozen panel scores/denominator')
                scalar_effects(row,['B1','B4','C','D','S'],['B4-B1','D-B4','C-B4','D-S'])
                require(all(math.isfinite(v) for v in row['effects'].values())
                        and row['nats_per_unit_second']=={k:v/dt for k,v in row['effects'].items()},'Panel finite effects/units')
    coverage=load(OLD/'results/NONREFIT_COVERAGE_PLAN.json')
    # Only frozen non-neural timing/running metadata is read to reconstruct S04 masks.
    from paper16_m1.code import spec
    from paper16_development_r3.controls import running_panels
    for row in records:
        m=row['mouse_id'];record=account[m];sid=record['source']['session_id'];s04=by[(m,'S04')]
        require(s04['coverage']==coverage[m]['S04'] and s04['status']==('COMPLETED' if coverage[m]['S04_coverage_pass'] else 'COVERAGE_FAILED'),'Original S04 coverage/status')
        source_result=load(R/record['result']['path']);pins=source_result['source_metadata_pins']
        metadata=R/pins['metadata_path'];require(sha(metadata)==pins['metadata_sha256'] and sha(metadata.with_suffix('.npz'))==pins['flash_array_sha256'],'Frozen non-neural flash metadata')
        with np.load(metadata.with_suffix('.npz'),allow_pickle=False) as a:starts=a['start'].copy()
        bundle=load(R/'paper16_running_r2/results'/str(sid)/'RESULT.json')['derived_bundle']
        require(sha(R/bundle['path'])==bundle['sha256'],'Frozen non-neural running bundle')
        with np.load(R/bundle['path'],allow_pickle=False) as a:running={k:a[k].copy() for k in a.files}
        missing=np.zeros((len(row['original_presentations']),6),bool)
        for j,ordinal in enumerate(row['original_presentations']):
            edges=spec.grid(float(starts[ordinal]))
            for k in range(6):missing[j,k]=bool(spec.past_rotation(running['start'],running['end'],running['net_rotation_promoted'],edges[5+k],running.get('invalid',()))[1])
        with np.load(P/'work/E'/m/'main_scores.npz',allow_pickle=False) as a:scores={k:a[k].copy() for k in models}
        expected_running=running_panels(scores,np.ones(missing.shape,bool),missing,len(row['unit_ids']),.02)
        require(all(s04[k]==v for k,v in expected_running.items()),'Exact saved S04 available/missing partitions and score arithmetic')
    from paper16_development_r3.controls import aggregate_references
    references=aggregate_references(records,P/'work/controls')
    require(references==load(P/'results/REFERENCE_CONTROL_RESULTS.json'),'All saved N1-N4 aggregate arithmetic')
    for m in account:
        folder=P/'work/controls'/m;receipt=load(P/'results/control_mouse'/m/'RESULT.json')
        for operator,reps in [('N1',999),('N2',16),('N3',999)]:
            unavailable=(operator=='N1' and not coverage[m]['N1_available']) or (operator=='N3' and not coverage[m]['N3_full_flash_support'])
            if unavailable:require((folder/(operator+'_UNAVAILABLE.json')).exists() and receipt[operator+'_replicates']==0,'Original reference unavailable coverage')
            else:
                journal=rows(folder/(operator+'.jsonl'));require(len(journal)==reps and [r['replicate'] for r in journal]==list(range(reps)),'Complete single reference replicate journal')
                with np.load(folder/(operator+'.npz'),allow_pickle=False) as a:
                    require(a['effects'].shape==(reps,6) and a['absolute'].shape==(reps,8)
                            and np.array_equal(a['effects'],[[r['effects'][n] for n in names] for r in journal])
                            and np.array_equal(a['absolute'],[[r['absolute'][n] for n in models] for r in journal]),'Saved reference arrays/journal identity')
                require(receipt[operator+'_replicates']==reps,'Reference completion receipt')
                for ref in journal:
                    scalar_effects(ref,models,names)
                    if operator=='N2':
                        observed=next(r for r in records if r['mouse_id']==m)
                        n2_invariant(ref,observed)
        maps=load(folder/'N4.json');operators=load(R/'paper16_precision_contract_r1/PRECISION_CONTRACT.json')['N4']['operators']
        require(maps['refit'] is False and len(maps['operators'])==11
                and [{k:r[k] for k in operators[0]} for r in maps['operators']]==operators,'All11 frozen N4 operators')
        require(all(math.isfinite(r['B1_logscore']) for r in maps['operators']),'Finite N4 score outcomes')
    return True


def facts():
    sup=load(P/'results/SUPERVISION.json')
    stage=load(P/'results/STAGE_CLAIM.json')
    require(stage['no_reset'] and stage['mission']=='P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4'
            and abs((stage['deadline_monotonic']-stage['start_monotonic'])-172800)<=1e-6,'Original one48h stage')
    require(sha(P/'results/STAGE_CLAIM.json')==load(P/'results/SUPERVISOR.json')['original_stage_sha256'],
            'Original stage claim identity')
    is_abnormal=abnormal(sup)
    journal=rows(P/'results/FIT_JOURNAL.jsonl');attempts,terminals,active=strict_journal(journal)
    require(active is None or is_abnormal,'Incomplete last attempt needs actual abnormal supervision')
    permitted={t['id']:t for t in load(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks']}
    require(len(permitted)==5519 and len(attempts)<=5519 and len({r['task']['id'] for r in attempts})==len(attempts),'Exact5519 allocation/no retry')
    out={'new_optimizer_attempts':len(attempts),'new_numerical_passes':0,'new_numerical_failures':0,
         'complete_saved_endpoints':0,'incomplete_attempted_tasks':0,'attempt_failures':0,
         'unattempted_tasks':5519-len(attempts),'FG_reserved':0,'FG_completed':0,'accepted_iterations':0,
         'FD_reserved':0,'AD_reserved':0,'analytic_reserved':0,'Final_C_access':False,'Final_D_access':False}
    all_states=[]
    for attempt in attempts:
        task=attempt['task'];require(permitted.get(task['id'])==task and attempt['ftol']==0.0,'Exact new task/policy')
        folder=P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
        row={'task':task,'folder':folder.relative_to(R).as_posix()}
        terminal=terminals.get(task['id'])
        if not (folder/'ATTEMPT.json').exists() or not (folder/'initial.npz').exists():
            require(is_abnormal and (terminal is None or terminal['event']=='FAILED'),'Consumed pre-folder interruption needs actual evidence')
            pre_fit_prefix(folder)
            out['incomplete_attempted_tasks']+=1;out['attempt_failures']+=int(terminal is not None)
            row.update(numerical_pass=None,missing_pre_fit_files_preserved=True);all_states.append(row);continue
        require(load(folder/'ATTEMPT.json')['task']==task,'New attempt identity')
        with np.load(folder/'initial.npz',allow_pickle=False) as a:initial={k:a[k].copy() for k in a.files}
        p=len(initial['x0']);accepted=rows(folder/'ACCEPTED.jsonl')
        nr,nd=accepted_prefix(rows(folder/'CALLS.jsonl'),accepted,initial)
        diag=prior.diagnostic_prefix(rows(folder/'DIAGNOSTIC_CALLS.jsonl'),p)
        out['FG_reserved']+=nr;out['FG_completed']+=nd;out['accepted_iterations']+=len(accepted)
        out['FD_reserved']+=diag['FD_RESERVED'];out['AD_reserved']+=diag['AD_RESERVED'];out['analytic_reserved']+=diag['ANALYTIC_RESERVED']
        if (folder/'RESULT.json').exists():
            result,_=prior.check_fit(folder);require(result['task']==task,'Result task binding')
            out['complete_saved_endpoints']+=1
            if terminal and terminal['event']=='COMPLETED':
                require(terminal['result_path']==(folder/'RESULT.json').relative_to(R).as_posix()
                        and terminal['result_sha256']==sha(folder/'RESULT.json')
                        and terminal['PG']==result['projected_gradient_inf'] and result['numerical_pass'] is True,'Exact completed journal/result join')
                out['new_numerical_passes']+=1
            else:require(is_abnormal,'No completion journal requires genuine failed/interrupted stage')
            out['new_numerical_failures']+=int(not result['numerical_pass'])
            row.update(numerical_pass=result['numerical_pass'],objective=result['objective'],PG=result['projected_gradient_inf'],
                       message=result['message'],FG_calls=result['nfev'],iterations=result['nit'])
        else:
            out['incomplete_attempted_tasks']+=1
            require((folder/'FAILURE.json').exists() or sup['returncode']!=0 or sup['killed_at_deadline'],
                    'Incomplete saved attempt requires actual failure/interruption')
            row.update(numerical_pass=None,endpoint_missing_not_reconstructed=True)
        if (folder/'FAILURE.json').exists():
            failure=load(folder/'FAILURE.json');require(failure['task']==task and failure['retry_authorized'] is False,'Actual no-retry failure')
            out['attempt_failures']+=1;row['failure']=failure
            require(terminal is not None and terminal['event']=='FAILED' and terminal['error_type']==failure['type']
                    and terminal['message']==failure['message'],'Failure journal/record exact join')
        if terminal and terminal['event']=='FAILED':require((folder/'FAILURE.json').exists() or is_abnormal,'Actual failed attempt evidence')
        all_states.append(row)
    stop_path=P/'results/SCIENTIFIC_STOP.json';out['scientific_stop']=load(stop_path) if stop_path.exists() else None
    if out['scientific_stop']:
        require(out['scientific_stop']['no_retry'] and out['scientific_stop']['all_later_tasks_not_executed'],'Mandatory stop preserved')
        require(is_abnormal,'STOP cannot be a normal successful worker')
    access=rows(P/'results/ACCESS.jsonl')
    require(all(r['role'] in ['A','E'] for r in access),'No B reselection/Final export')
    account={r['source']['mouse_id']:r for r in load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']}
    out['E_exports']=exports(access,account)
    out['E_claimed']=(P/'results/E_BATCH_CLAIM.json').exists()
    out['E_complete']=(P/'results/E_DEVELOPMENT_RESULTS.json').exists()
    out['M4_seal_candidate']=(P/'results/M4_SELECTION_FREEZE.json').exists()
    m4_review=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/M4_APPROVAL.json'
    out['M4_complete']=out['M4_seal_candidate'] and m4_review.exists() and load(m4_review)['decision']=='ACCEPTED_R4_COMPLETE_M4'
    if out['M4_complete']:verify_m4()
    if not out['M4_complete']:
        require(not out['E_claimed'] and out['E_exports']==0 and not out['E_complete'],'No E before complete M4')
    if out['E_claimed']:
        verify_m4();claim=load(P/'results/E_BATCH_CLAIM.json')
        require(claim['one_batch'] and claim['no_retry'] and claim['selection_freeze_sha256']==sha(P/'results/M4_SELECTION_FREEZE.json'),'Exactly one accepted E entitlement')
    if out['E_complete']:verify_E()
    complete=P/'results/WORKER_COMPLETE.json'
    if not is_abnormal:
        require(not out['scientific_stop'] and complete.exists() and out['new_numerical_passes']==5519
                and out['attempt_failures']==out['incomplete_attempted_tasks']==0
                and out['M4_complete'] and out['E_complete'] and out['E_exports']==27,'Normal stage completion must prove every scientific gate')
        require(load(complete)=={'M4':True,'E':True,'Final_C_D_access':False},'Actual complete worker receipt')
    else:require(not complete.exists(),'Failed/interrupted stage cannot claim complete worker')
    return out,all_states


def verify():
    for path,digest in load(P/'SOURCE_PINS.json')['files'].items():require(sha(R/path)==digest,'Historical source preservation')
    identities(load(OLD/'PROTECTED_STATE_MANIFEST.json'))
    identities(load(P/'PREFIT_FREEZE_MANIFEST.json'))
    identities(load(P/'PROTECTED_STATE_MANIFEST.json'))
    if (P/'ARCHIVE_MANIFEST.json').exists():identities(load(P/'ARCHIVE_MANIFEST.json'))
    observed,_=facts();require(observed==load(P/'EXECUTION_FACTS.json'),'Exact closed-stage facts')
    require(load(OLD/'results/SCIENTIFIC_STOP.json')['scientific_status']=='STOP_NUMERICAL_REQUIRED_GATE','R3 STOP immutable')
    require(load(P/'STATE_REUSE_AUDIT_RESULT.json')['compatible_optimizer_states']==952,'Saved reuse audit')
    print(json.dumps({'saved_only_reproduction':'PASS','new_fits':0,'new_derivatives':0,'new_likelihood_or_scores':0,
                      'new_source_requests':0,'Final_access':False,'facts':observed},indent=2))


if __name__=='__main__':
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('Saved-only denies network')):verify()
