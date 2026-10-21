"""Create prospective indices from already-published JSON only; no science imports."""
import csv
import datetime
import hashlib
import io
import json
import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=Path(__file__).resolve().parent
BASE='5ed9a6854248cd250a097a9e657519ad0a057f64'
pins={}
def original(name):
    raw=(R/name).read_bytes()
    saved=subprocess.check_output(['git','-C',str(R),'show',BASE+':'+name])
    assert saved==raw,'Published input bytes changed: '+name
    pins[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    return raw
def load(name):return json.loads(original(name))
def write(name,obj):
    with (P/name).open('x',encoding='utf8',newline='\n') as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
full=load('paper16_development_r3/results/TASK_PLAN.json')['tasks']
by={t['id']:t for t in full};assert len(by)==len(full)==6471
outcomes=load('paper16_development_r4/TASK_OUTCOMES.json')['tasks']
new=load('paper16_development_r4/NEW_TASK_PLAN_CANDIDATE.json')['tasks']
assert len(new)==len(outcomes)==5519 and [r['task'] for r in outcomes]==new
old=load('paper16_development_r4/STATE_COMPATIBILITY_MATRIX.json')['states']
b0=load('paper16_development_r4/B0_COMPATIBILITY_MATRIX.json')['states']
assert len(old)==952 and len(b0)==216
journal=[json.loads(line) for line in original('paper16_development_r4/results/FIT_JOURNAL.jsonl').splitlines()]
term={r['task']['id']:r for r in journal if r['event']=='COMPLETED'}
assert len(term)==3040
targets=[]
for i,row in enumerate(old):
    assert row['status']=='COMPATIBLE' and row['historical_ftol']==1e-12
    targets.append({'task':by[row['task_id']],'origin':'R3','historical_ftol':1e-12,'published_matrix_index':i,'result_path':row['result_path'],'result_sha256':row['result_sha256'],'R5_admitted':False,'R5_audit':'NOT_EXECUTED'})
remaining=[]
for index,row in enumerate(outcomes):
    task=row['task'];assert by[task['id']]==task
    if row['status']=='NUMERICAL_PASS':
        receipt=term[task['id']]
        targets.append({'task':task,'origin':'R4','historical_ftol':0.0,'published_outcome_index':index,'result_path':receipt['result_path'],'result_sha256':receipt['result_sha256'],'R5_admitted':False,'R5_audit':'NOT_EXECUTED'})
    else:
        assert row['status'] in ['UNATTEMPTED','INTERRUPTED_INCOMPLETE']
        remaining.append({'task':task,'original_R4_outcome_index':index,'original_status':row['status'],'start':'ORIGINAL_FROZEN_INITIALIZER_ONLY','scientific_execution_authorized':False})
target_ids={r['task']['id'] for r in targets};remaining_ids={r['task']['id'] for r in remaining}
assert len(targets)==len(target_ids)==3992 and len(remaining)==len(remaining_ids)==2479
assert not target_ids&remaining_ids and target_ids|remaining_ids==set(by)
assert sum(r['original_status']=='UNATTEMPTED' for r in remaining)==2478
assert remaining[0]['task']['id']=='763236014:S02:S:None:11:GLOBAL'
assert remaining[0]['original_status']=='INTERRUPTED_INCOMPLETE'
analytic=[{'mouse_id':r['mouse_id'],'unit_id':r['unit_id'],'origin':'R3_ANALYTIC','historical_ftol':None,'result_path':r['result_path'],'result_sha256':r['result_sha256'],'R5_admitted':False,'R5_audit':'NOT_EXECUTED'} for r in b0]
write('REUSE_TARGETS.json',{'base':BASE,'optimizer_target_count':3992,'R3_optimizer':952,'R4_optimizer':3040,'B0_analytic_target_count':216,'R5_admitted_count':0,'audit_executed':False,'optimizer_targets':targets,'B0_targets':analytic})
write('RECOVERY_TASK_PLAN.json',{'base':BASE,'count':2479,'unattempted':2478,'interrupted':1,'ordering':'R4_NEW_TASK_PLAN_ORIGINAL_ORDER_FILTER_NOT_COMPLETED','all_original_initialization':True,'tasks':remaining})
policy=load('paper16_development_r4/UNIFORM_NUMERICAL_AMENDMENT.json')['policy']
assert policy['options']['ftol']==0.0 and policy['maximum_parameters']['max_sensitivity_C']==368
account=load('paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')
development=[r['source'] for r in account['sources'] if r['selection']['admitted']]
cohort=list(csv.DictReader(io.StringIO(original('paper16_m1/FROZEN_COHORT.csv').decode('utf8'))))
final=[r for r in cohort if r['role']=='Final_candidate']
assert len(development)==len(final)==27
assert sum(r['protocol']=='brain_observatory_1.1' for r in development)==5
assert sum(r['protocol']=='functional_connectivity' for r in development)==22
write('ROSTER_IDENTITIES.json',{'Development':[{'mouse_id':r['mouse_id'],'session_id':r['session_id'],'probe_id':r['probe_id'],'protocol':r['protocol']} for r in development],'Final_locked':[{'mouse_id':r['mouse_id'],'session_id':r['session_id'],'probe_id':r['probe_id'],'protocol':r['protocol']} for r in final],'neural_values_accessed':False})
for name in [
 'paper16_m1/M1_SCIENTIFIC_PROTOCOL.md','paper16_m1/FEATURE_AND_MODEL_EQUATIONS.md','paper16_m1/NUMERICAL_POLICY.json','paper16_m1/STATISTICAL_ANALYSIS_PLAN.md','paper16_m1/FALSIFICATION_AND_SENSITIVITY_PLAN.md','paper16_m1/SOURCE_OBSERVATION_QC.md','paper16_m1/EVALUATION_BOUNDARY.md','paper16_m1/controls.json',
 'paper16_development_r3/SCIENTIFIC_CLOSEOUT.md','paper16_development_r3/PROTECTED_STATE_MANIFEST.json',
 'paper16_development_r4/RESOURCE_REGISTRATION.json','paper16_development_r4/PREFIT_FREEZE_MANIFEST.json','paper16_development_r4/SOURCE_PINS.json','paper16_development_r4/PROTECTED_STATE_MANIFEST.json','paper16_development_r4/PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json','paper16_development_r4/PARTIAL_ATTEMPT_MANIFEST.json','paper16_development_r4/EXECUTION_FACTS.json','paper16_development_r4/SCIENTIFIC_CLOSEOUT.md','paper16_development_r4/RUNTIME_IDENTITY.json',
 'ops/daily-operations.md','ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/FINAL_SCIENTIFIC_REVIEW_1.md','ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/FINAL_SCIENTIFIC_REVIEW_BINDING_1.json','ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/INDEPENDENT_BUDGET_SEMANTICS_REVIEW.md','ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/INDEPENDENT_PARTIAL_IDENTITY.json']:
    original(name)
write('SOURCE_PINS.json',{'base':BASE,'scope':'Published BASE files only; no protected work bundle read','files':pins})
write('PROPOSED_EXECUTION_POLICY.json',{
 'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','base':BASE,'status':'DRAFT_PROTOCOL_NOT_EXECUTED','scientific_execution_authorized':False,'saved_private_reuse_audit_executed':False,'R5_admitted_count':0,
 'preflight_wall_seconds':86400,'real_A_and_complete_M4_wall_seconds':172800,'total_phase_wall_ceiling_seconds':259200,'max_optimizer_workers':1,'new_attempts_max':2479,'FG_per_attempt_max':6000,'accepted_per_attempt_max':1500,'FG_total_max':2479*6000,'accepted_total_max':2479*1500,'FD_per_attempt':'24P','FD_total_max_from_inherited_P_ceiling':24*368*2479,'AD_per_attempt_max':3,'AD_total_max':3*2479,'analytic_checkpoint_per_attempt_max':3,'analytic_checkpoint_total_max':3*2479,
 'inherit_exact_policy_from':'paper16_development_r4/UNIFORM_NUMERICAL_AMENDMENT.json','options':policy['options'],'PG_max':1e-5,'AD_scaled_error_max':1e-8,'FD_acceptance_h':1e-5,'FD_scaled_error_max':2e-5,'FD_scan_steps':policy['FD_steps'],'checkpoints':policy['checkpoints'],'lambda':1.0,'lambda_origin':'HISTORICAL_R3_B1_SELECTION','DS_seeds':[11,23,37],'DS_selection':policy['DS_selection'],
 'all_new_tasks_original_initializer':True,'new_stage_claims':1,'optimizer_retries':0,'reset_old_stage':False,'new_stage_restart_after_shutdown':False,'postfailure_budget_extension':False,'only_existing_verified_saved_Development_A':True,'new_neural_source_requests_authorized':False,'new_B_selection_authorized':False,
 'full_M4_requires_all_6471_optimizer_task_accountability_and_216_B0':True,'E_authorized':False,'E_requires_separate_owner_authorization_after_full_M4_independent_acceptance':True,'E_max_if_later_authorized':1,'Final_C_D_authorized':False,'M6_P17_authorized':False,'future_implementation_approval':'NOT_EXECUTED','future_independent_reuse_approval':'NOT_EXECUTED','future_synthetic_certification':'NOT_EXECUTED','historical_STOPS_unchanged':True})
print(json.dumps({'protocol_metadata_built':True,'optimizer_reuse_targets_pending':3992,'B0_targets_pending':216,'remaining':2479,'full_optimizer_partition':6471,'source_pin_count':len(pins),'private_state_audit':False,'new_fits':0,'new_derivatives_or_scores':0}))
