"""Saved-only R1 fidelity, historical preservation and budget audit."""
import ast
import hashlib
import math
import struct
import importlib
from .source import P,R,load_json
from .training import sha
from .ledger import snapshot
from .native_table import records

def audit_corrective():
    E=R/'ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1'
    reg=load_json((E/'PRESERVATION_REGISTRATION.json').read_text())
    assert reg['original_fits_verified']==359 and reg['historical_complete']==358 and reg['historical_interrupted']==1
    assert sha(R/'paper15_dev/STOP_ARCHIVE_FREEZE.json')==reg['historical_package_freeze_sha256']
    for name,h in reg['historical_evidence'].items():assert sha(R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'/name)==h
    audit=load_json((P/'results/FULL_A_SOURCE_REVALIDATION.json').read_text());wheel=load_json((P/'results/EXACT_WHEEL_INDEX_VERIFICATION.json').read_text())
    assert audit['candidates']==len(audit['rows'])==12 and audit['FULL_A_SOURCE_REVALIDATION']
    assert wheel['PL033_trial224']['predecessor_index']==394299 and wheel['PL033_trial224']['equal_event_excluded']
    finite=0
    for row in audit['rows']:
        state=load_json((P/'metadata'/(row['subject']+'_task.json')).read_text());assert sha(P/'metadata'/(row['subject']+'_task.json'))==row['corrected_task_sha256']
        derived=records(state['native_table']);assert len(derived)==len(state['trials'])==row['original_trial_rows']
        for i,tr in enumerate(derived):
            for field,v in tr.items():
                actual=state['trials'][i][field]
                if isinstance(v,float):
                    assert struct.pack('>d',v)==struct.pack('>d',actual)
                    if math.isfinite(v):finite+=1
                else:assert v==actual
        assert row['all_native_bits_verified'] and row['independent_role_and_mask_agreement']
    assert finite==sum(r['finite_bit_patterns'] for r in audit['rows'])==96642
    continuity=load_json((P/'results/A_PREPARATION_SOURCE_CONTINUITY.json').read_text())
    saved=P/'source_snapshots/training_A_preparation.py';assert sha(saved)==continuity['preparation_source_snapshot_sha256']
    def prepare(path):return ast.dump(next(x for x in ast.parse(path.read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='prepare'),include_attributes=False)
    assert prepare(saved)==prepare(P/'training.py')
    ledger=snapshot();status=load_json((P/'results/DEVELOPMENT_STATUS.json').read_text())
    for key in ['NEW_MAIN_ATTEMPTS','NEW_SENSITIVITY_ATTEMPTS','TOTAL_CUMULATIVE_ATTEMPTS']:assert ledger[key]==status[key]
    assert ledger['NEW_MAIN_ATTEMPTS']==ledger['main_cap'] and not ledger['new_interrupted_or_active']
    assert all(status[k] for k in ['EXACT_NATIVE_REPAIR_PASS','NATIVE_TIME_BITWISE_VERIFICATION','STRICT_PAST_WHEEL_GATE',
        'FULL_A_SOURCE_REVALIDATION','ORIGINAL_ATTEMPTS_PRESERVED','B_SELECTION_FROZEN','DEVELOPMENT_E_COMPLETE'])
    assert status['FINAL_C_ACCESS'] is status['FINAL_D_ACCESS'] is False
    assert status['HISTORICAL_COMPLETED_ROUNDED_INPUT_NUMERICAL_PASS']==358 and status['HISTORICAL_INTERRUPTED_WITHOUT_ENDPOINT']==1
    sensitivity_gate=load_json((P/'SENSITIVITY_GATE.json').read_text())
    for item in sensitivity_gate['independent_review_evidence'].values():
        assert sha(R/item['path'])==item['sha256']
    prefix='ops.evidence.2026-10-17.p15-dev-exact-native-repair-r1.'
    sensitivity_guard=importlib.import_module(prefix+'seal_sensitivity_gate')
    sensitivity_guard.validate_review(load_json((E/'SENSITIVITY_ADMISSION_REVIEW_RECEIPT_2.json').read_text()),
        sensitivity_gate['hashes'],sha(E/'SENSITIVITY_ADMISSION_REVIEW_2.md'))
    e_gate=load_json((P/'E_EXPLORATORY_GATE.json').read_text())
    e_guard=importlib.import_module(prefix+'seal_E_gate')
    for item in e_gate['independent_review_evidence'].values():
        assert sha(R/item['path'])==item['sha256'] and sha(R/item['receipt_path'])==item['receipt_sha256']
        e_guard.validate_review(load_json((R/item['receipt_path']).read_text()),e_gate['hashes'],item['sha256'])
    limitation=e_gate['pre_E_coverage_limitations']
    assert sha(R/limitation['path'])==limitation['sha256']
    reference=load_json((P/'REFERENCE_METADATA_FREEZE.json').read_text())
    expected_coverage={suite:[r['subject'] for r in reference['records'] if r['coverage'][suite]['available']]
        for suite in ['N1','N2','N3','N4']}
    assert status['PRE_E_REFERENCE_ELIGIBLE_SUBJECTS']==expected_coverage
    assert status['N4_AGGREGATE_REFERENCE_METADATA_COVERAGE']==(len(expected_coverage['N4'])>=6)
    assert status['PERSISTENT_STATE_INTERPRETATION'].startswith('WITHHELD')
    primary=load_json((P/'results/E_CONTROL_SUMMARY.json').read_text())['B4-B1']
    assert status['PRIMARY_REFERENCE_N1_GATE']==primary['N1']['descriptive_disruption_gate']
    assert status['PRIMARY_REFERENCE_N2_GATE']==primary['N2']['descriptive_disruption_gate']
    assert status['ROBUST_POSITIVE_PRIMARY_CLAIM'] is False
    return dict(finite_binary64_cells=finite,historical_attempts=359,new_main=ledger['NEW_MAIN_ATTEMPTS'],
        new_sensitivity=ledger['NEW_SENSITIVITY_ATTEMPTS'],cumulative=ledger['TOTAL_CUMULATIVE_ATTEMPTS'],
        accepted_review_receipts_verified=3,pre_E_coverage_limitation_verified=True,Final_access=False)
