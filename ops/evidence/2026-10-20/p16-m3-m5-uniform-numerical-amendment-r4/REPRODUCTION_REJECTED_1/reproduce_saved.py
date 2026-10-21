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


def facts():
    sup=load(P/'results/SUPERVISION.json')
    stage=load(P/'results/STAGE_CLAIM.json')
    require(stage['no_reset'] and stage['mission']=='P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4'
            and stage['deadline_monotonic']-stage['start_monotonic']==172800,'Original one48h stage')
    require(sha(P/'results/STAGE_CLAIM.json')==load(P/'results/SUPERVISOR.json')['original_stage_sha256'],
            'Original stage claim identity')
    journal=rows(P/'results/FIT_JOURNAL.jsonl');attempts=[r for r in journal if r['event']=='ATTEMPTED']
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
        require(load(folder/'ATTEMPT.json')['task']==task,'New attempt identity')
        with np.load(folder/'initial.npz',allow_pickle=False) as a:p=len(a['x0'])
        nr,nd=prior.call_prefix(rows(folder/'CALLS.jsonl'),p)
        accepted=rows(folder/'ACCEPTED.jsonl');require([r['iteration'] for r in accepted]==list(range(1,len(accepted)+1)) and len(accepted)<=1500,'Accepted prefix')
        diag=prior.diagnostic_prefix(rows(folder/'DIAGNOSTIC_CALLS.jsonl'),p)
        out['FG_reserved']+=nr;out['FG_completed']+=nd;out['accepted_iterations']+=len(accepted)
        out['FD_reserved']+=diag['FD_RESERVED'];out['AD_reserved']+=diag['AD_RESERVED'];out['analytic_reserved']+=diag['ANALYTIC_RESERVED']
        if (folder/'RESULT.json').exists():
            result,_=prior.check_fit(folder);require(result['task']==task,'Result task binding')
            out['complete_saved_endpoints']+=1;out['new_numerical_passes']+=int(result['numerical_pass'])
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
        all_states.append(row)
    stop_path=P/'results/SCIENTIFIC_STOP.json';out['scientific_stop']=load(stop_path) if stop_path.exists() else None
    if out['scientific_stop']:
        require(out['scientific_stop']['no_retry'] and out['scientific_stop']['all_later_tasks_not_executed'],'Mandatory stop preserved')
    access=rows(P/'results/ACCESS.jsonl')
    require(all(r['role'] in ['A','E'] for r in access),'No B reselection/Final export')
    out['E_exports']=len({r['session_id'] for r in access if r['role']=='E'})
    out['E_claimed']=(P/'results/E_BATCH_CLAIM.json').exists()
    out['E_complete']=(P/'results/E_DEVELOPMENT_RESULTS.json').exists()
    out['M4_seal_candidate']=(P/'results/M4_SELECTION_FREEZE.json').exists()
    m4_review=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/M4_APPROVAL.json'
    out['M4_complete']=out['M4_seal_candidate'] and m4_review.exists() and load(m4_review)['decision']=='ACCEPTED_R4_COMPLETE_M4'
    if not out['M4_complete']:
        require(not out['E_claimed'] and out['E_exports']==0 and not out['E_complete'],'No E before complete M4')
    if out['E_claimed']:
        gate=load(m4_review)
        require(gate['decision']=='ACCEPTED_R4_COMPLETE_M4','Independent M4 approval before E')
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
