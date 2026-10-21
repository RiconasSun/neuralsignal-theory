"""Protocol metadata consistency only. No private arrays or scientific modules."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=Path(__file__).resolve().parent
BASE='5ed9a6854248cd250a097a9e657519ad0a057f64'
def load(p):return json.loads(p.read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(R),*args])
def verify():
    pins=load(P/'SOURCE_PINS.json');assert pins['base']==BASE
    for name,entry in pins['files'].items():
        assert '/work/' not in name and Path(name).suffix in ['.json','.jsonl','.md','.csv']
        raw=(R/name).read_bytes()
        assert len(raw)==entry['bytes'] and sha(raw)==entry['sha256']
        assert git('show',BASE+':'+name)==raw
    reuse=load(P/'REUSE_TARGETS.json');remaining=load(P/'RECOVERY_TASK_PLAN.json')
    full=load(R/'paper16_development_r3/results/TASK_PLAN.json')['tasks']
    all_by={t['id']:t for t in full}
    original=load(R/'paper16_development_r4/TASK_OUTCOMES.json')['tasks']
    expected_remaining=[r for r in original if r['status']!='NUMERICAL_PASS']
    assert len(remaining['tasks'])==len(expected_remaining)==2479
    assert [r['task'] for r in remaining['tasks']]==[r['task'] for r in expected_remaining]
    assert [r['original_status'] for r in remaining['tasks']]==[r['status'] for r in expected_remaining]
    assert sum(r['original_status']=='UNATTEMPTED' for r in remaining['tasks'])==2478
    assert sum(r['original_status']=='INTERRUPTED_INCOMPLETE' for r in remaining['tasks'])==1
    assert remaining['tasks'][0]['task']['id']=='763236014:S02:S:None:11:GLOBAL'
    assert all(r['start']=='ORIGINAL_FROZEN_INITIALIZER_ONLY' and r['scientific_execution_authorized'] is False for r in remaining['tasks'])
    targets=reuse['optimizer_targets'];b0=reuse['B0_targets']
    assert len(targets)==3992 and len(b0)==216 and reuse['R5_admitted_count']==0 and reuse['audit_executed'] is False
    assert sum(r['origin']=='R3' and r['historical_ftol']==1e-12 for r in targets)==952
    assert sum(r['origin']=='R4' and r['historical_ftol']==0.0 for r in targets)==3040
    assert all(r['historical_ftol'] is None for r in b0)
    assert all(r['R5_admitted'] is False and r['R5_audit']=='NOT_EXECUTED' for r in targets+b0)
    target_ids={r['task']['id'] for r in targets};todo_ids={r['task']['id'] for r in remaining['tasks']}
    assert len(target_ids)==3992 and len(todo_ids)==2479 and not target_ids&todo_ids
    assert target_ids|todo_ids==set(all_by) and len(all_by)==6471
    assert all(all_by[r['task']['id']]==r['task'] for r in targets+remaining['tasks'])
    policy=load(P/'PROPOSED_EXECUTION_POLICY.json')
    inherited=load(R/'paper16_development_r4/UNIFORM_NUMERICAL_AMENDMENT.json')['policy']
    assert policy['options']==inherited['options'] and policy['checkpoints']==inherited['checkpoints']
    assert policy['FD_scan_steps']==inherited['FD_steps'] and policy['DS_selection']==inherited['DS_selection']
    assert policy['only_existing_verified_saved_Development_A'] is True
    assert policy['E_requires_separate_owner_authorization_after_full_M4_independent_acceptance'] is True
    for k,v in {'scientific_execution_authorized':False,'saved_private_reuse_audit_executed':False,'R5_admitted_count':0,'preflight_wall_seconds':86400,'real_A_and_complete_M4_wall_seconds':172800,'total_phase_wall_ceiling_seconds':259200,'max_optimizer_workers':1,'new_attempts_max':2479,'FG_per_attempt_max':6000,'accepted_per_attempt_max':1500,'FG_total_max':14874000,'accepted_total_max':3718500,'FD_total_max_from_inherited_P_ceiling':21894528,'AD_total_max':7437,'analytic_checkpoint_total_max':7437,'PG_max':1e-5,'AD_scaled_error_max':1e-8,'FD_acceptance_h':1e-5,'FD_scaled_error_max':2e-5,'lambda':1.0,'optimizer_retries':0,'E_authorized':False,'E_max_if_later_authorized':1,'Final_C_D_authorized':False,'M6_P17_authorized':False,'new_B_selection_authorized':False,'new_neural_source_requests_authorized':False,'new_stage_restart_after_shutdown':False,'reset_old_stage':False,'postfailure_budget_extension':False}.items():assert policy[k]==v,k
    roster=load(P/'ROSTER_IDENTITIES.json');assert len(roster['Development'])==len(roster['Final_locked'])==27
    assert not {r['mouse_id'] for r in roster['Development']}&{r['mouse_id'] for r in roster['Final_locked']}
    baseline=load(R/'ops/evidence/2026-10-21/p16-shutdown-recovery-r5-protocol/REQUIREMENT_BASELINE.json')
    spec=load(P/'MISSION_SPEC.json');assert len(baseline['items'])==40
    assert [r['requirement'] for r in baseline['items']]==spec['instructions']['requirements']
    allowed={'ast','csv','datetime','hashlib','io','json','subprocess','pathlib'}
    for name in ['build_protocol_metadata.py','verify_protocol.py']:
        tree=ast.parse((P/name).read_text(encoding='utf8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):assert all(a.name.split('.')[0] in allowed for a in node.names)
            if isinstance(node,ast.ImportFrom):assert node.module.split('.')[0] in allowed
    print(json.dumps({'protocol_metadata_verification':'PASS','source_pins_checked':len(pins['files']),'optimizer_reuse_targets_pending':3992,'B0_reuse_targets_pending':216,'R5_admitted':0,'recovery_tasks_exact':2479,'full_optimizer_partition':6471,'scientific_execution':'NOT_AUTHORIZED_NOT_EXECUTED','private_state_audits':0,'synthetic_numerical_tests':0,'new_fits':0,'new_objective_gradient_AD_FD_or_score_calls':0,'neural_source_requests':0,'E_access':False,'Final_access':False}))
if __name__=='__main__':verify()
