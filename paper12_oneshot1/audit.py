"""Reproduce the public, stopped final-D prerelease decision without protected access."""
import hashlib
import json
from pathlib import Path
import shutil
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
E = ROOT/'ops/evidence/2026-10-14/p12-predictive-v2-final-d-oneshot'
C = ROOT/'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1'
MISSION = 'P12-PREDICTIVE-V2-FINAL-D-ONESHOT'
BASE = 'e3617caec814df37ad387443f596ceb886dff6c8'

def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def verify_hashes(paths, root=ROOT):
    for name, expected in paths.items():
        if sha(root/name) != expected: raise ValueError('FROZEN_HASH_MISMATCH:'+name)

def identity_checks(animals, trials, partition, manifest):
    final = [a for a in animals if a['group']=='final']
    if len(animals)!=26 or len(final)!=13 or len({a['mouse_id'] for a in animals})!=26: raise ValueError('ORIGINAL_COHORT_REQUIRED')
    mice = [a['mouse_id'] for a in final]
    if manifest['cohort'] != mice: raise ValueError('SEALED_C_COHORT')
    result = []
    for a in final:
        rows = [t for t in trials if t['session_id']==a['session_id'] and t['metadata_admitted']]
        c = [t['trial_id'] for t in rows if t['partition']=='calibration']
        d = [t['trial_id'] for t in rows if t['partition']=='locked_evaluation']
        # Preserve admitted IDs, including the three already-frozen C exclusions.
        cc=Counter(t['condition'] for t in rows if t['partition']=='calibration')
        dc=Counter(t['condition'] for t in rows if t['partition']=='locked_evaluation')
        if len(cc)!=8 or len(dc)!=8 or min(cc.values())<24 or min(dc.values())<16 or set(c)&set(d) or partition['D_trial_ids'].get(a['mouse_id'])!=d: raise ValueError('ORIGINAL_PARTITIONS_REQUIRED')
        cases = [z for z in manifest['cases'] if z['mouse_id']==a['mouse_id']]
        for z in cases:
            if z['session_id']!=a['session_id'] or z['trial_ids']!=c or hashlib.sha256(canonical(c)).hexdigest()!=z['trial_mask_sha256']: raise ValueError('SEALED_C_TRIAL_METADATA')
        result.append({'mouse_id':a['mouse_id'],'session_id':a['session_id'],'C_metadata_trials':len(c),'D_metadata_trials':len(d),'disjoint':True,'sealed_case_count':len(cases)})
    if set(partition['D_trial_ids'])!=set(mice): raise ValueError('D_PARTITION_COHORT')
    return result

def decide(ready):
    reasons = []
    if not ready['pinned_producer']: reasons.append('P1-01_MISSING_FROZEN_REAL_D_CUSTODIAN_PRODUCER')
    if not ready['scientific_evaluator']: reasons.append('P1-02_MISSING_FROZEN_REAL_D_SCIENTIFIC_EVALUATOR')
    if not ready['independent_REAL_D_authority']: reasons.append('P1-03_DESIGNATED_REAL_D_AUTHORITY_SIGNATURE_UNVERIFIED')
    return {'PRE_RELEASE_GATE':'FAIL' if reasons else 'REQUIRES_OTHER_FROZEN_GATES','critical_findings':reasons,'release_permitted':False}

def empty_contrasts():
    return {name:{'CA1_gain':None,'DG_gain':None,'CA1_minus_DG':None,'CI95':None,'raw_p':None,'Holm_p':None,'direction_vs_development':'NOT_ASSESSED','sensitivity_consistency':'NOT_ASSESSED','corrected_nulls':'NOT_EXECUTED','classification':'INCONCLUSIVE DUE TO FAILED REQUIRED GATE'} for name in ('own','population','stimulus_time','combined')}

def compute():
    registration=read(E/'registration.json');verify_hashes(registration['source_sha256'])
    # Published previous bytes remain verified; daily closure uses its exact archived suffix.
    previous=read(C/'final_manifest.json')
    for name, expected in previous['sha256'].items():
        path=E/'daily_at_registration.bin' if name=='ops/daily-operations.md' else ROOT/name
        if sha(path)!=expected: raise ValueError('PRIOR_C_SEAL_PUBLIC_EVIDENCE_DRIFT:'+name)
    verify_hashes(read(C/'host_snapshot.json')['sha256'])
    manifest=read(C/'complete_C_state_manifest.json');receipt=read(C/'complete_C_sealing_receipt.json');inventory=read(C/'complete_seal_inventory.json')
    if inventory['files']!=1862 or len(inventory['sha256'])!=1862 or hashlib.sha256(canonical(manifest)).hexdigest()!=receipt['C_manifest_sha256']:raise ValueError('PUBLIC_C_SEAL_BINDING')
    if sha(C/'complete_C_state_manifest.json')!=receipt['C_manifest_file_sha256']:raise ValueError('PUBLIC_C_MANIFEST_FILE_HASH')
    if not set(manifest['artifact_sha256'])<=set(inventory['sha256']) or any(inventory['sha256'][n]!=v for n,v in manifest['artifact_sha256'].items()):raise ValueError('PUBLIC_C_ARTIFACT_INVENTORY')
    if len(manifest['cases'])!=290 or len(manifest['seed_certificates'])!=104 or any(v!=13 for v in manifest['coverage'].values()):raise ValueError('SAVED_C_COVERAGE_METADATA')
    if any(set(c['models'])!={'O','N','NH','NP','F','OHP'} or any(m['shape']!=[len(c['unit_ids']),39] for m in c['models'].values()) for c in manifest['cases']):raise ValueError('SAVED_C_MODEL_IDENTITY')
    identities=identity_checks(read(ROOT/'paper12_curated_v1/locks/animals.json'),read(ROOT/'paper12_curated_v1/locks/trials.json'),read(ROOT/'paper12_controls1/final_D_partition_manifest.json'),manifest)
    roster=(E/'original_git_tree.txt').read_text(encoding='utf-8').splitlines();tracked=[line.split('\t',1)[1] for line in roster]
    producer=[n for n in tracked if Path(n).name=='custodian_producer.py']
    target=(ROOT/'paper12_controls1/target_worker.py').read_text(encoding='utf-8')
    bridge=(ROOT/'paper12_controls1/real_D_broker.py').read_text(encoding='utf-8')
    issuer=(ROOT/'paper12_controls1/run_security.py').read_text(encoding='utf-8')
    if 'Native synthetic final-analysis principal. No model/data evaluation.' not in target or 'No REAL_D approval issuer exists in this mission.' not in issuer or 'PINNED_CUSTODIAN_PRODUCER_REQUIRED' not in bridge:raise ValueError('REVIEWED_EXECUTABLE_FACTS_CHANGED')
    readiness={'pinned_producer':bool(producer),'scientific_evaluator':False,'independent_REAL_D_authority':False}
    decision=decide(readiness)
    return {'mission':MISSION,'base':BASE,**decision,'REAL_D_AUTHORIZATION_VERIFIED':False,'D_RELEASE_CONSUMED':False,'D_CAPABILITY_DELIVERED':False,'D_PROCESS_EXECUTED':False,'D_EVALUATION_EXECUTED':False,'D_EXECUTION_COMPLETED':False,'COMPLETE_FINAL_STATISTICS':False,'NULL_SUITE_STATUS':'NOT_EXECUTED','SCIENTIFIC_VALIDATION_VERDICT':'INCONCLUSIVE DUE TO FAILED REQUIRED GATE','MANUSCRIPT_COMPLETE':False,'final_contrasts':empty_contrasts(),'prerelease_public_evidence':{'frozen_source_hashes':'PASS','prior_C_public_manifest_hashes':'PASS','original26_and13identities':'PASS','C_D_partition_metadata':'PASS','public_C_seal_files':1862,'saved_calibration_counts':read(C/'saved_state_audit.json')['verified_counts'],'saved_calibration_gate_scope':'Original PASS receipts verified; protected C model payload not reopened by this stopped mission','protected_C_reverification':'NOT_EXECUTED_AFTER_CRITICAL_STOP','current_actual_final_principal_test':'NOT_EXECUTED_NO_PRODUCTION_EVALUATOR','historical_native_security_receipts':'PRESERVED_NOT_FRESH_REAL_D_CERTIFICATION','operational_readiness':'NOT_ESTABLISHED_WITHOUT_FROZEN_EXECUTABLE'},'identities':identities,'readiness':readiness,'producer_matches_in_BASE':producer,'authority_status':'Not established by frozen public artifacts; no private issuer/key search and no self-designation','new_C_fits':0,'raw_C_D_neural_array_reads':0,'protected_C_model_payload_reads':0,'D_key_reads':0,'controller_consumption_calls':0,'REAL_D_signatures_created':0,'entitlements_created':0,'host_disk_free_bytes_observed':shutil.disk_usage(ROOT).free,'resource_claim':'Disk metadata only; no capacity PASS for absent executable','bug_count':3,'warn_count':3,'warnings':['Full protected C payload gate deferred after critical STOP','Current actual REAL_D principal/denial proofs unavailable','Operational resource budget not verifiable without frozen production evaluator'],'authorization':{'conditional_human_permission':True,'human_text_equals_independent_signature':False},'next_required_action':'Separately authorize production prerelease preparation and designate/provision the independent REAL_D approval authority; no D consumption during preparation'}
