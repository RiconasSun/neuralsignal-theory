"""Register and inventory an externally interrupted R5 run, saved metadata only."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

R=Path(__file__).resolve().parents[4];P=R/'paper16_development_r5';E=Path(__file__).resolve().parent
MISSION='P16-M3-M5-SHUTDOWN-RECOVERY-R5';BASE='b7bb1227379462c2c7a1cef40ab0d0e99a6d020b'
def load(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def pin(p):return {'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size}
def once(p,v):
    with p.open('x',encoding='utf8',newline='\n') as f:
        json.dump(v,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def journal(p):
    raw=p.read_bytes() if p.exists() else b''
    assert not raw or raw.endswith(b'\n'),'Do not silently complete a torn journal'
    return [json.loads(line) for line in raw.splitlines()]

if __name__=='__main__':
    original=[P/'results'/n for n in ['SUPERVISION.json','SCIENTIFIC_STOP.json','WORKER_COMPLETE.json',
             'M4_READY_FOR_INDEPENDENT_REVIEW.json','E_BATCH_CLAIM.json']]+[P/'M4_REVIEW_MANIFEST.json',E/'M4_APPROVAL.json']
    assert all(not p.exists() for p in original)
    proof=E/'ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json';job=E/'OWNED_JOB_CLOSEOUT_RECEIPT_1.json'
    claims=[P/'results/STAGE_CLAIM.json',P/'results/SUPERVISOR.json',P/'results/WORKER_CLAIM.json',
            E/'INDEPENDENT_R5_M4_OBSERVER_CLAIM.json']
    registration={'schema':'R5_EXTERNAL_PROCESS_LOSS_REGISTRATION_V1','mission':MISSION,'base':BASE,
      'registered_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'scientific_status':'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE','source_sha256':sha(Path(__file__)),
      'stage_sha256':sha(claims[0]),'original_claims':[pin(p) for p in claims],
      'native_absence_proof':pin(proof),'owned_job_receipt':pin(job),
      'original_receipts_required_absent':[rel(p) for p in original],
      'snapshot_path':rel(P/'EXTERNAL_INTERRUPTION_SNAPSHOT.json'),
      'external_stop_path':rel(E/'EXTERNAL_SCIENTIFIC_STOP.json'),
      'snapshot_roots':[rel(P/'work/fits'),rel(P/'results')],
      'snapshot_extra_files':[rel(E/n) for n in ['INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl',
          'INDEPENDENT_R5_M4_MONITOR_EXECUTION_1.log','SCIENTIFIC_EXECUTION.log']],
      'accepted_original_source_freeze':pin(P/'PREFIT_FREEZE_MANIFEST_V3.json'),
      'saved_only_verification_scope':'Exact file hashes, original ordered metadata journals and already accepted independent certificates; no repeat numerical certificate audit or NPZ decoding',
      'closure_tooling_changes_allowed':['Add a separately tagged externally interrupted saved-state branch','Bind this registration, snapshot, original claims, absence proof and missing-original-receipt facts','Preserve unknown native exit, interruption time and cause','Add synthetic regression coverage and independent tooling review'],
      'native_worker_exit_code':None,'exact_interruption_UTC':None,'interruption_cause':'UNDETERMINED_FROM_SAVED_EVIDENCE',
      'scientific_process_restarts_allowed':0,'additional_fits_allowed':0,'new_derivative_or_score_calls_allowed':0,
      'scientific_policy_amended':False,'budget_reset_allowed':False,'E_authorized':False,'Final_C_D_authorized':False}
    once(E/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json',registration)
    proof_value=load(proof);job_value=load(job)
    assert proof_value['original_pid_matches']==proof_value['matching_scientific_or_observer_modules']==[]
    assert proof_value['stage_sha256']==registration['stage_sha256']==job_value['stage_sha256']
    assert job_value['job_opened'] is False and job_value['open_job_error']==2
    paths={p for root in registration['snapshot_roots'] for p in (R/root).rglob('*') if p.is_file()}
    paths.update(R/name for name in registration['snapshot_extra_files'])
    paths.update(claims)
    snapshot_rows=[]
    for p in sorted(paths):
        row=pin(p);row['last_write_UTC']=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()
        snapshot_rows.append(row)
    fit_rows=journal(P/'results/FIT_JOURNAL.jsonl')
    attempts=[r['task'] for r in fit_rows if r['event']=='ATTEMPTED']
    completed=[r for r in fit_rows if r['event']=='COMPLETED']
    failed=[r for r in fit_rows if r['event']=='FAILED']
    plan=[r['task'] for r in load(R/'paper16_shutdown_recovery_r5_protocol/RECOVERY_TASK_PLAN.json')['tasks']]
    independent=journal(E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl')
    assert attempts==plan[:len(attempts)] and len(attempts)==625 and len(completed)==len(independent)==624 and not failed
    assert [r['task'] for r in completed]==attempts[:-1]==[r['task'] for r in independent]
    partial=attempts[-1];folder=P/'work/fits'/hashlib.sha256(partial['id'].encode()).hexdigest()
    assert all(not (folder/n).exists() for n in ['RESULT.json','DIAGNOSTICS.json','endpoint.npz','FAILURE.json'])
    calls=journal(folder/'CALLS.jsonl');accepted=journal(folder/'ACCEPTED.jsonl');diagnostics=journal(folder/'DIAGNOSTIC_CALLS.jsonl')
    reserved=[r for r in calls if r['event']=='RESERVED_BEFORE_EVALUATION'];done=[r for r in calls if r['event']=='COMPLETED']
    assert len(reserved)==len(done)==482 and len(accepted)==460
    snapshot={'schema':'R5_EXTERNAL_INTERRUPTION_SNAPSHOT_V1','mission':MISSION,'base':BASE,
      'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'registration':pin(E/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json'),'roots':registration['snapshot_roots'],
      'extra_files':registration['snapshot_extra_files'],'files':snapshot_rows,'file_count':len(snapshot_rows),
      'attempted':625,'completed':624,'failed_journal_entries':0,'partial':1,'unattempted':1854,
      'independently_qualified_completed_states':624,'partial_task':partial,'partial_parameters':load(folder/'ATTEMPT.json')['parameters'],
      'partial_FG_reserved':len(reserved),'partial_FG_completed_receipts':len(done),'partial_accepted_iterations':len(accepted),
      'partial_diagnostic_reservations':dict(collections.Counter(r['kind'] for r in diagnostics)),
      'partial_diagnostic_completed_calls':'Unknown; reservations do not establish completed checks',
      'latest_saved_file_write_UTC':max(r['last_write_UTC'] for r in snapshot_rows),
      'file_timestamps_are_not_exact_interruption_time':True,'native_worker_exit_code':None,
      'exact_interruption_UTC':None,'interruption_cause':'UNDETERMINED_FROM_SAVED_EVIDENCE',
      'numerical_audit_repeated':False,'NPZ_decodes':0,'new_fits_derivatives_scores':0}
    once(P/'EXTERNAL_INTERRUPTION_SNAPSHOT.json',snapshot)
    stop={'schema':'R5_EXTERNAL_PROCESS_LOSS_STOP_V1','mission':MISSION,'base':BASE,
      'scientific_status':'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE','origin':'EXTERNAL_NATIVE_PROCESS_LOSS_CLOSEOUT',
      'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'registration':pin(E/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json'),'snapshot':pin(P/'EXTERNAL_INTERRUPTION_SNAPSHOT.json'),
      'stage_sha256':registration['stage_sha256'],'native_absence_proof':pin(proof),'owned_job_receipt':pin(job),
      'native_worker_exit_code':None,'original_supervision_available':False,'original_worker_stop_available':False,
      'exact_interruption_UTC':None,'interruption_cause':'UNDETERMINED_FROM_SAVED_EVIDENCE',
      'new_attempts':625,'new_numerical_passes':624,'recorded_numerical_failures':0,'partial_attempts':1,'unattempted':1854,
      'M4_complete':False,'all_later_tasks_not_executed':True,'no_retry':True,'no_restart':True,
      'E_access':False,'Final_C_access':False,'Final_D_access':False}
    once(E/'EXTERNAL_SCIENTIFIC_STOP.json',stop)
    print(json.dumps({'registration':pin(E/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json'),'snapshot':pin(P/'EXTERNAL_INTERRUPTION_SNAPSHOT.json'),
                     'external_stop':pin(E/'EXTERNAL_SCIENTIFIC_STOP.json'),'partial_parameters':snapshot['partial_parameters'],
                     'partial_diagnostic_reservations':snapshot['partial_diagnostic_reservations'],
                     'latest_saved_file_write_UTC':snapshot['latest_saved_file_write_UTC']},indent=2))
