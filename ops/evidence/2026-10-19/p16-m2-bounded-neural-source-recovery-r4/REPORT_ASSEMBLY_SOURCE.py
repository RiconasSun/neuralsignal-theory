"""Saved-only one-use report assembly; never imports an acquisition runner."""
from pathlib import Path
import json,hashlib,datetime
from collections import Counter,defaultdict
from unittest.mock import patch
R=Path.cwd();P=R/'paper16_source_r4';S=R/'paper16_dev_r3';E=R/'ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def text(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(v)
def ident(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
with patch('socket.socket.connect',side_effect=RuntimeError('Report assembly denies source network')):
 from paper16_source_r4.verify_saved import verify_saved
 saved=verify_saved()
for phase in ['fourth','remaining']:
 if (P/'results'/f'WORKER_{phase}.claim.json').exists():assert (P/'results'/f'SUPERVISION_{phase}.json').exists(),'Do not assemble while a source worker is active'
reg=load(P/'ACCESS_REGISTRATION.json');mission=load(P/'MISSION_SPEC.json').get('mission_id','P16-M2-BOUNDED-NEURAL-SOURCE-RECOVERY-R4')
if not isinstance(mission,str):mission='P16-M2-BOUNDED-NEURAL-SOURCE-RECOVERY-R4'
assert (P/'results/SUPERVISION_remaining.json').exists() or (P/'results/SUPERVISION_fourth.json').exists()
assert not any((P/'results'/f'SUPERVISION_{phase}.json').exists() and not (P/'results'/f'WORKER_{phase}.json').exists() and load(P/'results'/f'SUPERVISION_{phase}.json')['valid_completed_worker'] for phase in ['fourth','remaining'])
decision=load(P/'results/M2_DECISION.json') if (P/'results/M2_DECISION.json').exists() else None
failures=list((P/'results/sources').glob('*/FAILURE.json'))
assert decision is not None or failures or any(not load(f)['valid_completed_worker'] for f in (P/'results').glob('SUPERVISION_*.json'))
verdict=decision['verdict'] if decision else load(failures[0])['verdict'] if failures else 'RESOURCE_LIMIT' if any(load(f).get('killed_at_deadline') or load(f).get('clock_failure') for f in (P/'results').glob('SUPERVISION_*.json')) else 'STOP_SOURCE'
passed=verdict=='M2_SOURCE_AND_PHYSIOLOGY_PASS';sources=[];captures=[];passing_candidates=0;examined=0;new_examined=0;selected=[];physiology_excluded=0;support_excluded=0
for index,item in enumerate(reg['objects']):
 folder=(S if index<3 else P)/'results/sources'/str(item['session_id']);result_path=folder/'RESULT.json';qc=folder/'UNIT_QC.jsonl'
 rows=[json.loads(s) for s in qc.read_text(encoding='utf8').splitlines()] if qc.exists() else []
 result=load(result_path) if result_path.exists() else None
 failure=load(folder/'FAILURE.json') if (folder/'FAILURE.json').exists() else None
 passing=sum(row['A_physiology']['pass'] and row['individual_source_coverage_pass'] for row in rows)
 examined+=len(rows);passing_candidates+=passing;physiology_excluded+=sum(not row['A_physiology']['pass'] for row in rows);support_excluded+=sum(not row['individual_source_coverage_pass'] for row in rows)
 state='COMPLETE' if result else 'FAILED_INCOMPLETE' if failure else 'UNATTEMPTED'
 source={'original_order':index+1,'source':item,'disposition':state,'reused_complete_R3_source':index<3,'candidate_count_registered':len(item['candidate_unit_ids']),'candidate_states_retained':len(rows),'A_qualified_supported_units':passing,'selection':None if result is None else result['selection'],'failure':failure,'QC':None if not qc.exists() else ident(qc),'result':None if result is None else ident(result_path)}
 sources.append(source)
 for row in rows:
  capture=row['private_A_capture'];captures.append({'session_id':item['session_id'],'unit_id':row['unit_id'],'A_only':True,**capture})
  if capture['private_path'].startswith('paper16_source_r4/'):new_examined+=1
 if result and result['selection']['admitted']:
  selected.append({'source':item,'selected_unit_ids':result['selection']['selected_unit_ids'],'common_mask':result['selection']['common_mask'],'coverage':result['selection']['coverage'],'running_coverage':result['selection']['running_coverage'],'source_result':ident(result_path),'QC':ident(qc),'native_metadata_pins':result['source_metadata_pins'],'scalers_fitted':False,'fitted_model_states':0})
assert len(captures)==examined and new_examined==saved['new_R4_A_states_replayed']
if decision:assert len(sources)==28 and all(x['disposition']=='COMPLETE' for x in sources) and examined==1983
write(P/'SOURCE_AND_PHYSIOLOGY_ACCOUNT.json',{'mission':mission,'verdict':verdict,'source_denominator':28,'source_protocol_denominators':{'BO':5,'FC':23},'final_untouched':27,'full_cohort_decision_available':decision is not None,'sources':sources,'candidate_states_retained':examined,'A_qualified_supported_candidates':passing_candidates,'all_candidate_qualification_exclusions':examined-passing_candidates,'physiological_candidate_exclusions':physiology_excluded,'individual_source_support_exclusions':support_excluded,'R3_original_states_reused':228,'new_R4_states_retained':new_examined,'admitted_mice':len(selected),'admitted_BO':saved['admitted_BO'],'admitted_FC':saved['admitted_FC'],'no_partial_mouse_credit':True,'M3_fitting_authorized':False})
write(P/'A_ONLY_STATE_MANIFEST.json',{'mission':mission,'scope':'Saved A-only observation/scaling INPUTS; no fitted scaler or model','all_candidate_states':captures,'selected_mouse_inputs':selected,'native_running_inputs':'Original paper16_running_r2 saved states and original M1 masks; never reacquired','source_identity_registration':ident(P/'ACCESS_REGISTRATION.json'),'frozen_scientific_contract':ident(R/'paper16_m1/M1_FREEZE_MANIFEST.json'),'model_fits':0,'scalers_fitted':0,'B_E_outcome_arrays':False,'Final_C_D_access':False})
private=[ident(f) for f in sorted((P/'work/private').rglob('*')) if f.is_file()]
write(P/'PRIVATE_STATE_INVENTORY.json',{'mission':mission,'files':private,'original_R3_679_files_bound_by':ident(P/'R3_REUSE_MANIFEST.json'),'public_clone_without_private_raw_cannot_replay_QC':True})
journal=[json.loads(s) for s in (P/'results/TRANSPORT.jsonl').read_text().splitlines()];events=Counter(row['event'] for row in journal);by=defaultdict(lambda:Counter())
for row in journal:
 tally=by[str(row['session_id'])]
 if row['event']=='RESERVED':tally['requests']+=1;tally['reserved_bytes']+=row['reserved_bytes']
 if row['event']=='PAYLOAD':tally['payload_bytes']+=row['bytes']
 if row['event']=='RETRY_SLOT_RESERVED':tally['recovery_slots']+=1
 if row['event']=='HTTP_SENT':tally[row['method']+'_requests']+=1;tally['actual_second_requests']+=int(row.get('attempt')==2)
 if row['event']=='REQUEST_FAILED':tally['failed_requests']+=1
 if row['event']=='RECOVERED_R4_TIMEOUT':tally['recovered_timeouts']+=1
stage=load(P/'results/STAGE_CLAIM.json')
snapshot=P/'results/BUDGET_FOURTH.jsonl'
assert (P/'results/TRANSPORT.jsonl').read_bytes().startswith(snapshot.read_bytes())
if (E/'FOURTH_SOURCE_APPROVAL.json').exists():assert sha(snapshot)==load(E/'FOURTH_SOURCE_APPROVAL.json')['reviewed_hashes']['paper16_source_r4/results/TRANSPORT.jsonl']
write(P/'RESOURCE_LEDGER.json',{'mission':mission,'new_R4':{'events':dict(events),'per_source':dict(by),'requests':saved['R4_source_requests'],'payload_bytes':saved['R4_new_payload_bytes'],'reserved_bytes':saved['R4_reserved_bytes'],'transport_retries':saved['R4_transport_retries'],'timeout_slots_consumed':saved['R4_timeout_recovery_slots'],'historical_R3_range_repairs':events['RECOVERED_HISTORICAL_R3_RANGE'],'maximum_payload':8589934592,'per_source_max':536870912,'maximum_source_workers':1,'stage':stage,'last_transport_elapsed_seconds':max(row['monotonic'] for row in journal)-stage['start_monotonic']},'R3_historical_unchanged':ident(S/'RESOURCE_LEDGER.json'),'R3_payload_bytes':236470272,'R3_requests':226,'R3_original_failures':1,'R3_retries':0,'R2_and_earlier_historical_separate':ident(R/'paper16_running_r2/RESOURCE_LEDGER.json'),'fourth_reviewed_journal_snapshot':ident(snapshot),'current_journal_preserves_reviewed_fourth_prefix':True,'fourth_gate_hash_semantics':'Fourth acceptance bound the pre-remaining journal; its exact bytes remain BUDGET_FOURTH and unchanged current journal prefix. No repeated phase authorization.','historical_counters_never_refunded_or_merged':True,'optimizer_attempts':0,'running_reacquisition_calls':0})
write(E/'SAVED_VERIFICATION_RESULT.json',saved)
write(P/'TERMINAL_FIELDS.json',{'MISSION_ID':mission,'FINAL_STATUS':'CONTINUE_EXECUTION','PENDING_CLOSURE':'Final independent review, exact normal commit/push, remote blob readback and clean gate','SCIENTIFIC_VERDICT':verdict,'R3_STOP_PRESERVED':True,'RECOVERED_RANGE_VERIFIED':saved['recovered_range_verified'],'FOURTH_SOURCE_COMPLETED':(P/'results/sources/763673393/RESULT.json').exists(),'ORIGINAL_COMPLETED_SOURCES_REUSED':3,'R4_SOURCE_ATTEMPTS':saved['R4_sources_attempted'],'R4_TRANSPORT_RETRIES':saved['R4_transport_retries'],'R4_TRANSFER_BYTES':saved['R4_new_payload_bytes'],'TOTAL_DEVELOPMENT_SOURCES_COMPLETED':saved['total_complete_sources'],'DEVELOPMENT_ADMITTED_MICE':len(selected),'DEVELOPMENT_ADMITTED_BO':saved['admitted_BO'],'DEVELOPMENT_ADMITTED_FC':saved['admitted_FC'],'ADMISSION_DENOMINATOR_CAVEAT':None if decision else 'Complete-source prefix only; full28 cohort not established','A_ONLY_PHYSIOLOGY_PASS':passed,'M2_SCIENTIFIC_GATE':verdict,'M3_READY':passed,'M3_READY_MEANING':'Source/physiology readiness to consider a separately authorized mission only; no production numerical or predictive claim','MODEL_FITS_EXECUTED':0,'B_E_NEURAL_SCIENTIFIC_ACCESS':False,'FINAL_C_ACCESS':False,'FINAL_D_ACCESS':False,'BUG_COUNT':0,'WARN_COUNT':0 if passed else 1,'INDEPENDENT_REVIEW':'Preaccess/fourth accepted; final review pending, not preclaimed','SAVED_REPRODUCTION':'Native PowerShell saved-only PASS before final freeze; postfreeze replay and review required','GIT_COMMIT':None,'REMOTE_VERIFICATION':'Pending postcommit work/FINAL_HANDOFF_RECEIPT.json; no precommit remote success claim'})
print(json.dumps({'assembled_saved_reports':True,'verdict':verdict,'sources':len(sources),'complete':saved['total_complete_sources'],'retained_candidates':examined,'new_R4_states':new_examined,'private_files':len(private)}))
# Only saved-derived documentation is published by this final assembly.
table=['|Order|Mouse|Session|Protocol|Disposition|Candidates retained / registered|A-qualified supported|Admission|','|---:|---|---|---|---|---:|---:|---|']
for row in sources:
 item=row['source'];selection=row['selection'];admission='UNESTABLISHED' if selection is None else 'ADMITTED' if selection['admitted'] else selection['reason']+' ('+str(selection['passing_units'])+' qualifying)'
 table.append('|'+str(row['original_order'])+'|'+str(item['mouse_id'])+'|'+str(item['session_id'])+'|'+('BO' if item['protocol']=='brain_observatory_1.1' else 'FC')+'|'+row['disposition']+'|'+str(row['candidate_states_retained'])+'/'+str(row['candidate_count_registered'])+'|'+str(row['A_qualified_supported_units'])+'|'+admission+'|')
body=f'''# R4 current source-only handoff

Mission: P16-M2-BOUNDED-NEURAL-SOURCE-RECOVERY-R4. Exact BASE: d60e913c528feecfaaab9397ba1a6157c511526d.

Scientific source verdict: **{verdict}**. Complete original sources: **{saved['total_complete_sources']}/28**. Physiologically admitted mice: **{len(selected)}**, BO **{saved['admitted_BO']}**, FC **{saved['admitted_FC']}**. Original cohort floors remain14overall/3BO/10FC, with all28 complete dispositions required. No original source/probe/unit/mouse is replaced.

R3 remains its original3complete/1failedpartial/24unattempted historical STOP. R4 reuses the3complete sources and all228 saved A states by frozen file/native-array/QC identity. Fourth source763673393 has19 historical states plus54 new states; its independent complete-source acceptance preceded any remaining source. Prefix540672bytes SHA256eeff268eac3c0857dc2e96e5fd8bade7cd65e1b7cf1f2a56a77a5abeabd536c6 plus exact507904-byte suffix reconstructs1048576bytes, SHA25621c564dc7152d98186d73ec8ecc4cb0fa22700093b4c6cfd1224e2d02369cbd6. The digest establishes retained range integrity/provenance, not an independent upstream whole-file digest.

Retained candidate A states: **{examined}** ({new_examined}newR4 +228originalR3). Individually A-qualified/source-supported candidates: **{passing_candidates}**. Physiology rejects: **{physiology_excluded}**; individual source-support rejects: **{support_excluded}**; overlapping reasons are not double-counted as extra units. Every reached failed candidate and every physiological mouse exclusion remains in per-source UNIT_QC and the account below. Partial sources never receive mouse admission credit.

New R4 transport: **{saved['R4_sources_attempted']} source attempts**, **{saved['R4_source_requests']} HTTP requests**, **{saved['R4_new_payload_bytes']} actual payload bytes**, **{saved['R4_transport_retries']} second requests**, **{saved['R4_timeout_recovery_slots']} timeout slots**. Historical R3 remains226requests/236470272payloadbytes/one failed range/zero retries; R2 and earlier ledgers remain separately bound. See RESOURCE_LEDGER for exact source counters, reservation totals, original same-boot UTC/monotonic deadline, and the reviewed fourth-journal snapshot/prefix proof. No budget reset, refund, alternate source, bulk fallback or optimizer budget occurred.

**MODEL_FITS_EXECUTED=0; B_E_NEURAL_SCIENTIFIC_ACCESS=false; FINAL_C_ACCESS=false; FINAL_D_ACCESS=false.** Only A observation/scaling INPUTS are sealed; no fitted scaler/model state is claimed. M3_READY={str(passed).lower()} means source/physiology readiness to consider a separately authorized mission. It is not production numerical certification, fitting authorization, B selection, E evaluation or a predictive scientific result.

## Full original source dispositions

'''+ '\n'.join(table)+'''

## Evidence and interpretation

SOURCE_AND_PHYSIOLOGY_ACCOUNT.json records all original source dispositions and denominator arithmetic. A_ONLY_STATE_MANIFEST.json binds all retained A/native-array identities and selected observation/scaling inputs; PRIVATE_STATE_INVENTORY.json accounts for actual private bodies/caches/A files. Raw neural arrays and range bytes stay private and are not redistributed in Git. SOURCE_ONLY_LIMITATIONS.md and A1_A10_CLAIM_AUDIT.md distinguish source evidence from all unexecuted science. The trusted row-integrity exception, curated-observation limitations, original source terms, and BO/FC imbalance remain explicit.

37source/transport/native-reader/Windows/controller/integration synthetic tests plus8archive tests and7original-cohort-boundary tests give52unique tests, not52real-source experiments. Initial failed fixture/CLI/sandbox attempts and all historical unsuccessful reviews remain preserved. No repeated scientific source phase or new model attempt is permitted. The active source/transport/QC implementation remains exactly the independently accepted preaccess candidate; later tests and saved-only archive tools do not modify that surface.

Independent preaccess and complete-fourth reviews are accepted. Final acceptance is recorded separately in ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/review.md after checking the frozen complete handoff; no pre-review success is claimed by this pre-review payload. FINAL_APPROVAL binds that report and the final manifest. Git/remote/clean values are inherently postcommit and are resolved by paper16_source_r4/work/FINAL_HANDOFF_RECEIPT.json and the final user-facing report; TERMINAL_FIELDS retains explicit precommit pending values rather than inventing a commit SHA.

Native saved-only reproduction from this repository root:

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\paper16_source_r4\\reproduce.ps1
```

The command needs the existing protected private R3/R4 states and pinned runtime, denies network, verifies saved hashes/native arrays/QC/selection/ledger/reconstructed range, and performs no fit or source reacquisition. A public clone without those private arrays cannot repeat that QC. Exact Git identity/readback is a separate archive check.

STOP after the reviewed origin/test archive. M3_M5_HANDOFF.md supplies frozen references only. No M3-M5, new scientific control, B/E evaluation or Final access begins automatically.
'''
text(P/'CURRENT_HANDOFF.md',body)
print('CURRENT_HANDOFF.md saved-derived complete disposition table published.')
