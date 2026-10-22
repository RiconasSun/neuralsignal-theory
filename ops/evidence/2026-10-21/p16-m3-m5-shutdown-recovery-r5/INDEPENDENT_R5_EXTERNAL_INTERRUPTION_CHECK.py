"""Stopped-prefix metadata/hash verification only; never resume numerical audits."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import traceback

R=Path.cwd().resolve();P=R/'paper16_development_r5';E=R/'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5';Q=R/'paper16_shutdown_recovery_r5_protocol'
CONTEXT={'stage':'NOT_STARTED','task':None}

def J(path):return json.loads(Path(path).read_bytes())
def H(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def C(value,message):
    if not value:raise AssertionError(message)
def lines(path):
    raw=Path(path).read_bytes();C(not raw or raw.endswith(b'\n'),'Untorn original journal/ledger: '+str(path))
    return [json.loads(line) for line in raw.split(b'\n')[:-1]] if raw else []
def once(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
def file_row(path):return {'path':path.relative_to(R).as_posix(),'bytes':path.stat().st_size,'sha256':H(path),'last_write_UTC':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()}

def main():
    reg=J(E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_REGISTRATION.json')
    C(H(Path(__file__))==reg['script_sha256'],'Registered stopped-prefix checker')
    for row in reg['bound_files']:C(H(R/row['path'])==row['sha256'],'Original interrupted source/proof binding: '+row['path'])
    source=J(P/'PREFIT_FREEZE_MANIFEST_V3.json')
    for row in source['files']:C(H(R/row['path'])==row['sha256'],'Unchanged V3 producer/runtime/source: '+row['path'])
    stage=J(P/'results/STAGE_CLAIM.json');sup=J(P/'results/SUPERVISOR.json');worker=J(P/'results/WORKER_CLAIM.json');observer=J(E/'INDEPENDENT_R5_M4_OBSERVER_CLAIM.json')
    loss=J(E/'ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json');prior=J(E/'HOST_REATTACH_PROCESS_PROOF_1.json')
    C(H(P/'results/STAGE_CLAIM.json')==loss['stage_sha256']==sup['stage_sha256']==observer['stage_claim_sha256']==reg['stage_claim_sha256'],'Same original StageB claim, never reset')
    C(stage['phase']=='B_A_M4' and stage['no_reset'] is True and worker['no_restart'] is True and worker['single_worker'] is True and observer['one_pass_no_restart'] is True,'Original one-claim/one-worker/one-observer semantics')
    expected_pids=[sup['supervisor_pid'],worker['pid'],observer['pid']]
    C(expected_pids==loss['original_claimed_pids']==[r['ProcessId'] for r in prior['processes']],'Saved present-to-absent original native process identity')
    C(loss['original_pid_matches']==[] and loss['matching_scientific_or_observer_modules']==[],'Actual saved native absence proof')
    C(datetime.datetime.fromisoformat(loss['native_host_boot_UTC'].replace('Z','+00:00'))==datetime.datetime.fromisoformat(stage['windows_boot_UTC']),'Unchanged observed boot identity, no inferred cause')
    C(loss['native_exit_code'] is None and loss['exact_interruption_time'] is None and loss['interruption_cause']=='UNDETERMINED_FROM_SAVED_EVIDENCE','Unknown native exit/time/cause retained')
    C(loss['scientific_process_restart_authorized'] is False and loss['scientific_processes_restarted'] is False and loss['observer_restarted'] is False,'No restarted scientific or observer process')
    absent=[P/'results'/name for name in ['SUPERVISION.json','SCIENTIFIC_STOP.json','WORKER_COMPLETE.json','M4_SELECTION_FREEZE.json','M4_READY_FOR_INDEPENDENT_REVIEW.json']]
    absent += [P/'M4_REVIEW_MANIFEST.json',E/'M4_APPROVAL.json',E/'INDEPENDENT_R5_M4_COMPLETE_SAVED_RESULT.json',E/'INDEPENDENT_R5_M4_AUDIT_FAILURE_1.json']
    C(all(not path.exists() for path in absent),'No invented native terminal, M4 gate, observer completion or numerical-review failure')

    CONTEXT['stage']='EXACT_INTERRUPTED_JOURNAL_PREFIX'
    plan=[row['task'] for row in J(Q/'RECOVERY_TASK_PLAN.json')['tasks']]
    rows=lines(P/'results/FIT_JOURNAL.jsonl');attempts=[];completed=[];active=None
    for row in rows:
        if row['event']=='ATTEMPTED':
            C(active is None and row['task']==plan[len(attempts)] and row['ftol']==0. and row['initializer']=='ORIGINAL_FROZEN_ONLY','Exact ordered no-retry attempt prefix')
            attempts.append(row['task']);active=row['task']
        else:
            C(row['event']=='COMPLETED' and active==row['task'],'Only actual complete terminal, no failure substitution')
            completed.append(row);active=None
    C(len(plan)==2479 and len(attempts)==625 and len(completed)==624 and active==plan[624],'Actual625/624/onepartial/1854unattempted accounting')
    initializers=lines(P/'results/INITIALIZER_IDENTITIES.jsonl')
    C(len(initializers)==625 and [r['task_id'] for r in initializers]==[t['id'] for t in attempts],'Exact original initializer identity prefix')
    consumption=P/'results/attempt_consumption'
    expected_tokens={hashlib.sha256(t['id'].encode()).hexdigest() for t in attempts}
    C({p.name for p in consumption.iterdir() if p.is_file()}==expected_tokens,'Exact625 consumed attempt tokens, no later consumption')
    for task in attempts:C(J(consumption/hashlib.sha256(task['id'].encode()).hexdigest())=={'task':task,'no_retry':True},'Original atomic attempt token')

    CONTEXT['stage']='EXISTING_624_OBSERVER_ATTESTATIONS_AND_FRESH_HASHES'
    ledger_path=E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl';ledger=lines(ledger_path)
    C(len(ledger)==624 and [r['task'] for r in ledger]==attempts[:624],'All and only624 already reviewed states, no resumed audit')
    totals=collections.Counter();all_files={}
    for index,(row,terminal) in enumerate(zip(ledger,completed)):
        CONTEXT['task']=row['task']['id']
        C(row['completed_receipt']==terminal and row['initializer_identity']==initializers[index] and row['origin']=='R5' and row['ftol']==0. and row['status']=='INDEPENDENTLY_QUALIFIED_NEW_STATE' and row['new_evaluations']==0,'Original independent state attestation/terminal/initializer binding')
        C(row['PG']==terminal['PG']<=1e-5 and row['AD_error_max']<=1e-8 and row['fixed_FD_error_max']<=2e-5,'Retain previous independent numerical attestations; no certificate recalculation')
        folder=P/'work/fits'/hashlib.sha256(row['task']['id'].encode()).hexdigest()
        expected={f['path'] for f in row['files']}
        C({p.relative_to(R).as_posix() for p in folder.iterdir() if p.is_file()}==expected,'Exact previously attested state files')
        C(row['result_path']==(folder/'RESULT.json').relative_to(R).as_posix() and H(folder/'RESULT.json')==row['result_sha256'],'Current completed result matches original independent attestation')
        for f in row['files']:
            path=R/f['path'];C(path.stat().st_size==f['bytes'] and H(path)==f['sha256'],'Fresh byte-only attested completed file: '+f['path'])
            C(f['path'] not in all_files,'No duplicate completed file path');all_files[f['path']]=f
        for key in ['FG_pairs','accepted_iterations','FD_reserved','AD_reserved','analytic_checkpoint_reserved']:totals[key]+=row[key]
    maxima={name:max(row[key] for row in ledger) for name,key in [('PG','PG'),('AD','AD_error_max'),('fixed_FD','fixed_FD_error_max')]}

    CONTEXT.update(stage='PRESERVED_PARTIAL_METADATA_ONLY',task=active['id'])
    folder=P/'work/fits'/hashlib.sha256(active['id'].encode()).hexdigest()
    expected_partial={'ACCEPTED.jsonl','ATTEMPT.json','CALLS.jsonl','CLIENT_STDERR.log','CLIENT.json','DIAGNOSTIC_CALLS.jsonl','initial.npz'}
    C({p.name for p in folder.iterdir() if p.is_file()}==expected_partial,'Exact preserved partial files, no terminal/certificate reconstruction')
    attempt=J(folder/'ATTEMPT.json');C(attempt['task']==active and attempt['no_retry'] is True and attempt['parameters']==339,'Actual interrupted task and original parameter count')
    C(H(folder/'initial.npz')==attempt['bounds']['sha256'] and all(attempt['bounds']['arrays'][k]==initializers[-1][k] for k in ['x0','lo','hi']),'Preserved partial original initializer receipt identity; NPZ never decoded')
    calls=lines(folder/'CALLS.jsonl');accepted=lines(folder/'ACCEPTED.jsonl');diagnostic=lines(folder/'DIAGNOSTIC_CALLS.jsonl')
    for index,row in enumerate(calls):C(row['event']==('RESERVED_BEFORE_EVALUATION' if index%2==0 else 'COMPLETED') and row['call']==index//2+1,'Actual partial FG reservation/completion prefix')
    C(all(row['iteration']==i+1 for i,row in enumerate(accepted)),'Actual partial accepted-iteration prefix')
    expected_diag=[];fd=ad=analytic=0;p=attempt['parameters']
    for name in ['initial','halfway','endpoint']:
        analytic+=1;expected_diag.append({'kind':'ANALYTIC_RESERVED','checkpoint':name,'index':analytic})
        ad+=1;expected_diag.append({'kind':'AD_RESERVED','checkpoint':name,'index':ad})
        for h in [.001,.0001,.00001,.000001]:
            for coordinate in range(p):
                for side in ['plus','minus']:
                    fd+=1;expected_diag.append({'kind':'FD_RESERVED','checkpoint':name,'index':fd,'h':h,'coordinate':coordinate,'side':side})
    C(diagnostic==expected_diag[:len(diagnostic)] and len(diagnostic)<len(expected_diag),'Only saved incomplete derivative reservation prefix; no completion inferred')
    partial_counts={'FG_reserved':(len(calls)+1)//2,'FG_completed':len(calls)//2,'accepted_iterations':len(accepted),**dict(collections.Counter(r['kind'] for r in diagnostic))}
    partial_files=[file_row(path) for path in sorted(folder.iterdir()) if path.is_file()]
    result={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','reviewer':'/root/r4_interruption_review','recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'decision':'ACCEPTED_EXTERNAL_INTERRUPTION_EVIDENCE_ONLY','scientific_verdict':'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE',
            'stage_claim_sha256':reg['stage_claim_sha256'],'script_sha256':H(Path(__file__)),'registration_sha256':H(E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_REGISTRATION.json'),
            'attempted':625,'completed':624,'failed_journal_entries':0,'partial':1,'unattempted':1854,'partial_task':active,'partial_parameter_count':339,
            'previously_independently_qualified_completed':624,'completed_prefix_files_fresh_hash_verified':len(all_files),'completed_prefix_counters':dict(totals),'completed_prefix_maxima':maxima,
            'partial_saved_reservation_counts':partial_counts,'partial_derivative_completions_not_inferred':True,'partial_files':partial_files,
            'latest_observed_partial_file_write_UTC':max(row['last_write_UTC'] for row in partial_files),'observer_ledger_sha256':H(ledger_path),'fit_journal_sha256':H(P/'results/FIT_JOURNAL.jsonl'),
            'native_exit_code':None,'exact_interruption_time':None,'interruption_cause':'UNDETERMINED_FROM_SAVED_EVIDENCE','unchanged_boot_does_not_establish_cause':True,
            'M4_complete':False,'M4_approval_issued':False,'observer_restarted':False,'later_state_audits_executed':False,'numerical_certificate_recalculations':0,
            'model_objective_gradient_AD_FD_score_minimize_calls':0,'raw_neural_arrays_decoded':0,'saved_NPZ_arrays_decoded':0,'E_access':False,'Final_C_D_access':False,
            'boundary_basis':'Exact unchanged A-only producer/claim and saved access boundaries; no malicious administrator claim'}
    once(E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_CHECK_RESULT_1.json',result)
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        failure={'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'context':CONTEXT,'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'no_retry_or_later_state_audit':True}
        once(E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_CHECK_FAILURE_1.json',failure)
        print(json.dumps(failure,indent=2),flush=True);raise
