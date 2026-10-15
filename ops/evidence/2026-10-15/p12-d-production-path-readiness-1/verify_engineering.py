"""Saved native engineering receipt completeness; never opens neural arrays/keys."""
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parent;ROOT=E.parents[3];HERE=ROOT/'paper12_production1'

def read(path):return json.loads(Path(path).read_text())
def require(condition,label):
    if not condition:raise RuntimeError(label)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    output=HERE/read(HERE/'latest_saved_result.json')['path'];run=read(output/'result.json');gate=run['evaluator_gate'];controller=run['controller_gate'];execution=read(output/'execution_registration.json')
    freeze=read(HERE/'source_freeze.json');require(run['source_sha256']==execution['source_sha256']==freeze['source_sha256'],'EXACT_EXECUTED_SOURCE')
    for name,value in freeze['source_sha256'].items():require(sha(HERE/name)==value,'FROZEN_SOURCE:'+name)
    for name,value in read(E/'registration.json')['source_sha256'].items():require(sha(ROOT/name)==value,'ORIGINAL_SOURCE:'+name)
    role_fields={'is_appcontainer','capability_count','source_read_denied','key_read_denied','dacl_regrant_denied','network_status_code','network_denied','custodian_memory_access_denied','pass'}
    for role in ('target','controller'):
        proof=read(output/role/'role_proof.json');receipt=read(output/('native_'+role+'_receipt.json'))
        require(set(proof)==role_fields,'EXACT_ROLE_PROOF_FIELDS:'+role)
        require(all(proof[k] is True for k in role_fields-{'capability_count','network_status_code'}) and proof['capability_count']==0 and proof['network_status_code']==10013,'ACTUAL_ZERO_CAP_SECURITY:'+role)
        require(receipt['exit_code']==0 and receipt['profile_cleanup_hresult']=='0x00000000' and receipt['declared_realm']=='SYNTHETIC_D' and 0<receipt['elapsed_seconds']<43200,'NATIVE_EXIT_CLEANUP_BUDGET:'+role)
        if role=='target':require(receipt['pid']==execution['held_principal']['pid'] and receipt['package_sid']==execution['held_principal']['package_sid'],'ACTUAL_TARGET_RECEIPT_IDENTITY')
        else:require(receipt['package_sid']==execution['controller_sid'],'ACTUAL_CONTROLLER_RECEIPT_IDENTITY')
    for phase in ('pregrant','postgrant'):
        denial=read(output/'target'/(phase+'_denials.json'));require(set(denial)=={'issuer','source','key','ledger'} and all(x is True for x in denial.values()),'EXACT_TARGET_DENIAL_ROSTER:'+phase)
    denial=read(output/'controller/protected_denials.json');require(set(denial)=={'issuer','source','key'} and all(x is True for x in denial.values()),'EXACT_CONTROLLER_DENIAL_ROSTER')
    oracle=read(output/'controller/oracle_tests.json');require(oracle=={'count':29,'passed':True,'skipped':0,'errors':[],'failures':[]},'ORIGINAL_29_NATIVE_ORACLES')
    require(controller['realm']=='SYNTHETIC_D' and controller['production_plan_executed'] is True and controller['consumption_completed'] is True,'ACTUAL_PRODUCTION_CONTROLLER_BRANCH')
    consumed=read(output/'controller/consumed_success.json');completion=run['production_completion'];started=read(output/'target/assessment_started.json')
    require(consumed['principal']==completion['principal']==execution['held_principal'] and consumed['binding']==completion['binding'] and consumed['authorization_id']==completion['authorization_id']==started['authorization_id'],'PRODUCTION_CONSUMPTION_EVALUATION_BINDING')
    ready=read(output/'target/ready.json');require(ready['pid']==execution['held_principal']['pid'] and ready['readonly_binding_and_approval_readable'] is True,'ACTUAL_TARGET_PRECONSUMPTION_READINESS')
    boot=gate['code_bootstrap'];require(boot['fresh_process'] is True and boot['code_files']==len(execution['target_code'])-1 and all(ready[k]==v for k,v in boot.items()),'EXECUTED_CODE_BOOTSTRAP_READINESS_MATCH')
    runtime_files=len(read(ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256']);require(ready['runtime']==gate['runtime']==controller['runtime']=={'files':runtime_files,'verified':True},'EXECUTED_EXACT_RUNTIME_PROOF_MATCH')
    require(started['realm']=='SYNTHETIC_D' and started['D_EVALUATION_EXECUTED'] is False,'SYNTHETIC_ASSESSMENT_START')
    extra={'delivery_duplicate','delivery_concurrent','cipher_tamper','key_tamper'}|{'delivery_crash_'+p for p in ('after_delivery_fence','after_private_export','after_complete_staging','after_acl_grant')}
    require(set(run['delivery_negative_tests'])==extra,'EXACT_EIGHT_DELIVERY_FAILURES')
    for name,v in run['delivery_negative_tests'].items():
        require(v['fail_closed'] is True and v['valid_release'] is False and v['retry_denied'] is True and v['start_signal_absent'] is True and v['REAL_D_capability_granted'] is False,'FAILED_DELIVERY_POISON:'+name)
        require(v['synthetic_capability_granted']==(name=='delivery_crash_after_acl_grant'),'POST_ACL_EXPOSURE_DISCLOSED:'+name)
    require(gate['scored_cases']==208 and gate['mice']==13 and gate['null_cases']==104 and gate['null_replicates_per_case']==999 and gate['null_evaluations']==103896 and gate['count_preserving_checks']==25974 and gate['cache_parity_checks']==156 and gate['new_fits']==0 and gate['elapsed_seconds']<43200,'FULL_FROZEN_SYNTHETIC_DENOMINATORS')
    require(gate['synthetic'] is True and gate['synthetic_evaluator_executed'] is True and gate['D_EVALUATION_EXECUTED'] is False and gate['code_bootstrap']['scientific_cache_empty'] is True and gate['runtime']['verified'] is True,'ACTUAL_CACHELESS_FROZEN_EVALUATOR')
    flags=('REAL_D_AUTHORITY_PROVISIONED','REAL_D_SIGNATURE_ISSUED','D_RELEASE_CONSUMED','D_EVALUATION_EXECUTED','SCIENTIFIC_VALIDATION_PASS')
    require(all(run[k] is False for k in flags),'NO_REAL_OR_SCIENTIFIC_PASS')
    seal=read(E/'C_seal_unchanged.json');require(seal['complete_C_seal_unchanged'] is True and seal['verified_files']==1862 and seal['new_fits']==0 and seal['raw_C_D_count_reads']==0 and seal['real_D_source_key_or_ledger_opens']==0,'EXISTING_REAL_C_SEAL_PRESERVED')
    print(json.dumps({'saved_native_engineering_receipts':'PASS','native_oracles':29,'additional_delivery_failures':8,'production_plan_executed':True,'null_evaluations':103896,'SYNTHETIC_PATH_VERIFIED':True,'PRODUCTION_PATH_READY':False,'readiness_status':'AUTHORITY_PENDING',**dict.fromkeys(flags,False)},sort_keys=True))

if __name__=='__main__':main()
