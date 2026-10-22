"""External interrupted receipt/snapshot hash joins, no numerical state decoding."""
import datetime,hashlib,json,os
from pathlib import Path
R=Path.cwd().resolve();P=R/'paper16_development_r5';E=R/'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5'
def J(p):return json.loads(p.read_bytes())
def H(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def C(v,message):
    if not v:raise AssertionError(message)
def pin(ref):
    path=R/ref['path'];C(path.resolve().is_relative_to(R),'Repository-bound reference');C(H(path)==ref['sha256'] and path.stat().st_size==ref['bytes'],'Exact receipt reference: '+ref['path']);return path
def unknown(value):
    C('native_worker_exit_code' in value and value['native_worker_exit_code'] is None and 'exact_interruption_UTC' in value and value['exact_interruption_UTC'] is None and value['interruption_cause']=='UNDETERMINED_FROM_SAVED_EVIDENCE','Explicit unknown native fields, never invented or missing')
reg_path=E/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json';snapshot_path=P/'EXTERNAL_INTERRUPTION_SNAPSHOT.json';stop_path=E/'EXTERNAL_SCIENTIFIC_STOP.json'
reg,snapshot,stop=map(J,[reg_path,snapshot_path,stop_path]);own=J(E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_CHECK_RESULT_1.json')
C(H(reg_path)=='8ad2c861fd89245b7a39295c3f096f30a2f2db10de93075e8bcb1df2baac5383','Prospective exact external registration')
C(reg['source_sha256']==H(E/'register_external_closeout.py'),'Original external registration writer')
for v in [reg,snapshot,stop]:
    C(v['mission']=='P16-M3-M5-SHUTDOWN-RECOVERY-R5' and v['base']=='b7bb1227379462c2c7a1cef40ab0d0e99a6d020b','Exact mission/base');unknown(v)
C(snapshot['schema']=='R5_EXTERNAL_INTERRUPTION_SNAPSHOT_V1' and stop['schema']=='R5_EXTERNAL_PROCESS_LOSS_STOP_V1','Distinct externally interrupted schema')
C(stop['origin']=='EXTERNAL_NATIVE_PROCESS_LOSS_CLOSEOUT' and stop['scientific_status']=='STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE','Actual external interruption, never native result')
C(pin(snapshot['registration'])==pin(stop['registration'])==reg_path and pin(stop['snapshot'])==snapshot_path,'External registration/snapshot/STOP exact join')
C(stop['stage_sha256']==reg['stage_sha256']==own['stage_claim_sha256']==H(P/'results/STAGE_CLAIM.json'),'Original unmodified stage claim')
C(pin(reg['native_absence_proof'])==pin(stop['native_absence_proof']) and pin(reg['owned_job_receipt'])==pin(stop['owned_job_receipt']),'Actual native absence and Job receipt bindings')
proof=J(pin(reg['native_absence_proof']));job=J(pin(reg['owned_job_receipt']));job_claim=J(E/'OWNED_JOB_CLOSEOUT_CLAIM_1.json');sup=J(P/'results/SUPERVISOR.json')
C(job['job_opened'] is False and job['open_job_error']==2 and job['termination_requested'] is False and job['actual_native_worker_returncode'] is None,'Exact named Job absent; no claimed kill or native exit')
C(job['job_name']==job_claim['job_name']==sup['job_name'] and job['stage_sha256']==job_claim['stage_sha256']==reg['stage_sha256'],'Exact owned original Job/stage identity')
C(job['claim_sha256']==H(E/'OWNED_JOB_CLOSEOUT_CLAIM_1.json') and job_claim['native_process_loss_evidence_sha256']==H(pin(reg['native_absence_proof'])) and job_claim['native_worker_returncode'] is None and job_claim['restart_authorized'] is False,'Native Job closeout claim binding and unknown exit')
C(proof['original_pid_matches']==proof['matching_scientific_or_observer_modules']==[] and proof['native_exit_code'] is None and proof['exact_interruption_time'] is None,'Native process-loss proof, unknown termination')
for ref in reg['original_claims']:pin(ref)
C(pin(reg['accepted_original_source_freeze'])==P/'PREFIT_FREEZE_MANIFEST_V3.json','No scientific source or policy amendment')
C(all(not (R/name).exists() for name in reg['original_receipts_required_absent']),'Original native/worker/M4/E receipts remain absent')
C(snapshot['roots']==reg['snapshot_roots'] and snapshot['extra_files']==reg['snapshot_extra_files'],'Exact preregistered snapshot topology')
expected={f.relative_to(R).as_posix() for name in reg['snapshot_roots'] for f in (R/name).rglob('*') if f.is_file()}
expected.update(reg['snapshot_extra_files']);expected.update(row['path'] for row in reg['original_claims'])
rows=snapshot['files'];C(type(snapshot['file_count']) is int and snapshot['file_count']==len(rows)==len({r['path'] for r in rows})==7505 and {r['path'] for r in rows}==expected,'Complete exact7505-file snapshot including observer claim, no hidden extras/omissions')
for row in rows:pin(row)
for key,expected_value in [('attempted',625),('completed',624),('failed_journal_entries',0),('partial',1),('unattempted',1854),('independently_qualified_completed_states',624),('partial_parameters',339),('partial_FG_reserved',482),('partial_FG_completed_receipts',482),('partial_accepted_iterations',460)]:C(snapshot[key]==expected_value,'Exact saved snapshot counter '+key)
C(snapshot['partial_task']==own['partial_task'] and snapshot['partial_diagnostic_reservations']=={'ANALYTIC_RESERVED':1,'AD_RESERVED':1,'FD_RESERVED':1176},'Original339P partial reservation prefix, no endpoint/certificate inference')
for key,expected_value in [('new_attempts',625),('new_numerical_passes',624),('recorded_numerical_failures',0),('partial_attempts',1),('unattempted',1854)]:C(stop[key]==expected_value,'External STOP exact actual prefix '+key)
C(snapshot['numerical_audit_repeated'] is False and snapshot['NPZ_decodes']==snapshot['new_fits_derivatives_scores']==0 and snapshot['file_timestamps_are_not_exact_interruption_time'] is True,'Metadata-only external seal, no invented numerical/cause evidence')
C(stop['original_supervision_available'] is False and stop['original_worker_stop_available'] is False and stop['M4_complete'] is False and all(stop[k] is True for k in ['all_later_tasks_not_executed','no_retry','no_restart']) and all(stop[k] is False for k in ['E_access','Final_C_access','Final_D_access']),'Irreversible stopped-only scientific boundary')
parse=lambda value:datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
C(parse(reg['registered_UTC'])<=parse(snapshot['created_UTC'])<=parse(stop['recorded_UTC']),'Prospective registration precedes snapshot and external STOP')
C(parse(snapshot['latest_saved_file_write_UTC'])==parse(own['latest_observed_partial_file_write_UTC']),'Latest partial write corroborates source timestamp, not termination time')
result={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','reviewer':'/root/r4_interruption_review','recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'EXTERNAL_INTERRUPTION_METADATA_AND_BYTE_HASH_ONLY','snapshot_files_verified':len(rows),'registration_sha256':H(reg_path),'snapshot_sha256':H(snapshot_path),'external_stop_sha256':H(stop_path),'native_absence_proof_sha256':H(pin(reg['native_absence_proof'])),'owned_job_receipt_sha256':H(pin(reg['owned_job_receipt'])),'newstate_ledger_sha256':H(E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl'),'independent_prefix_result_sha256':H(E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_CHECK_RESULT_1.json'),'decision':'PASS_EXTERNAL_RECEIPT_AND_SNAPSHOT_BINDINGS_ONLY','NPZ_decodes':0,'numerical_audits_repeated':0,'new_scientific_calls':0,'observer_or_science_restarted':False,'M4_approval_issued':False}
target=E/'INDEPENDENT_EXTERNAL_CLOSEOUT_BINDING_CHECK_RESULT_1.json'
with target.open('x',encoding='utf8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(result,indent=2))
