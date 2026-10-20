"""Verify frozen STOP evidence and protected historical inputs; never fit or fetch."""
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
from .audit_base import BASE, E, P, R, load, sha, verify
from .contract_witnesses import witnesses

REQUIRED_REPORTS = {
    'MISSION_SPEC.json', 'BASE_AND_FREEZE_AUDIT.json', 'STOP_RECORD.json',
    'SOURCE_AND_ROLE_ACCESS_LEDGER.json', 'PRODUCTION_NUMERICAL_CERTIFICATION.json',
    'MODEL_AND_FEATURE_IDENTITY_MANIFEST.json', 'A_FITTING_RESULTS.json',
    'B_SELECTION_RESULTS.json', 'FROZEN_SELECTION_MANIFEST.json',
    'E_DEVELOPMENT_RESULTS.json', 'SENSITIVITY_RESULTS.json',
    'REFERENCE_CONTROL_RESULTS.json', 'RESOURCE_LEDGER.json', 'SCIENTIFIC_VERDICT.md',
    'A1_A10_CLAIM_AUDIT.md', 'LIMITATIONS_AND_FAILURES.md', 'INDEPENDENT_REVIEW.md',
    'FINAL_DELIVERY.json', 'README.md', 'reproduce.ps1', 'verify_saved.py',
    'audit_base.py', 'contract_witnesses.py', 'test_saved.py', '.gitignore',
}


def validate_stop(stop, certification, fitting, delivery, resource):
    assert stop['mission'] == delivery['MISSION_ID'] == 'P16-M3-M5-FROZEN-DEVELOPMENT-R1'
    assert stop['BASE'] == delivery['BASE_SHA'] == BASE
    assert stop['scientific_status'] == delivery['SCIENTIFIC_DEVELOPMENT_VERDICT'] == 'STOP_IMPLEMENTATION_REQUIRED_GATE'
    assert stop['execution_terminal_state'] == delivery['FINAL_STATUS'] == 'WAIT_FOR_HUMAN_INPUT'
    assert len(stop['critical_findings']) == stop['warn_count'] == delivery['WARN_COUNT'] == 2
    assert [x['operator'] for x in stop['critical_findings']] == ['S07', 'N4']
    assert stop['bug_count'] == delivery['BUG_COUNT'] == 0
    assert not certification['PASS'] and certification['real_optimizer_attempts'] == 0
    assert not stop['M3_production_numerical_PASS'] and not stop['M3_production_worker_implemented']
    assert not delivery['M3_PRODUCTION_NUMERICAL_PASS']
    for field in ['M4_A_FITS_COMPLETE', 'M4_GLOBAL_B1_LAMBDA_SELECTED', 'M5_E_EXECUTED',
                  'FINAL_C_ACCESS', 'FINAL_D_ACCESS', 'NEXT_STAGE_READY']:
        assert delivery[field] is False, field
    for field in ['MODELS_FITTED', 'OPTIMIZER_ATTEMPTS', 'NUMERICAL_FAILURES',
                  'SENSITIVITIES_COMPLETED', 'SENSITIVITIES_UNAVAILABLE',
                  'CONTROLS_COMPLETED', 'CONTROLS_UNAVAILABLE', 'FINAL_MODEL_FITS', 'FINAL_ASSESSMENTS']:
        assert delivery[field] == 0, field
    for field in ['B_SELECTION_LAMBDA', 'E_PRIMARY_B4_MINUS_B1', 'E_SECONDARY_EFFECTS']:
        assert delivery[field] == 'NOT_EXECUTED', field
    for field in ['model_fits', 'optimizer_attempts', 'completed_attempts', 'failed_attempts', 'analytic_B0_states_fitted']:
        assert fitting[field] == 0, field
    assert fitting['all_real_attempts'] == []
    assert len(fitting['unattempted_source_model_groups']) == 27
    for field in ['new_transport_requests', 'new_payload_bytes', 'new_reserved_bytes',
                  'new_transport_retries', 'source_recovery_reruns', 'real_optimizer_attempts',
                  'optimizer_value_gradient_pairs', 'optimizer_accepted_iterations', 'real_FD_objective_calls',
                  'real_AD_calls', 'real_analytic_checkpoint_calls', 'scientific_stage_active_workers']:
        assert resource[field] == 0, field
    assert resource['science_stage_clock'] == 'NOT_STARTED'
    b = resource['budget_derivation_only_not_permission_to_execute']
    assert b['original_28Dev_loose_allocation'] + b['Final_27_reserved'] == b['full_study_ceiling'] == 16178
    assert b['current_27Dev_main'] == 27*62 == 1674
    assert b['current_27Dev_upper_bound_all_panels_available'] == 27*(62+6*30+2*18) == 7506
    assert b['Final_reserved_reallocated'] == 0 and not b['removed_mouse_and_optional_unused_slots_reused']


def validate_manifest(manifest, root=R):
    rows = manifest['files']
    paths = [row['path'] for row in rows]
    assert len(paths) == len(set(paths)) == manifest['payload_count']
    required = {'paper16_development_r1/' + x for x in REQUIRED_REPORTS}
    assert required.issubset(paths), required.difference(paths)
    assert manifest['scientific_status'] == 'STOP_IMPLEMENTATION_REQUIRED_GATE'
    assert manifest['not_a_scientific_or_numerical_PASS'] is True
    for row in rows:
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert '/work/' not in row['path'] and relative.suffix.lower() not in {'.npz', '.npy', '.h5', '.nwb'}
        path = root / relative
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
    return len(rows)


def verify_records():
    assert REQUIRED_REPORTS.issubset({p.name for p in P.iterdir() if p.is_file()})
    stop = load(P / 'STOP_RECORD.json')
    validate_stop(stop, load(P/'PRODUCTION_NUMERICAL_CERTIFICATION.json'),
        load(P/'A_FITTING_RESULTS.json'), load(P/'FINAL_DELIVERY.json'), load(P/'RESOURCE_LEDGER.json'))
    assert sha(E/'STATIC_CONTRACT_REVIEW_1.md') == stop['independent_static_review_sha256']
    assert json.loads((E/'SYNTHETIC_CONTRACT_WITNESSES.json').read_bytes()) == witnesses()
    for filename, keys in [('SENSITIVITY_RESULTS.json', ['S%02d'%n for n in range(1,13)]),
                           ('REFERENCE_CONTROL_RESULTS.json', ['N%d'%n for n in range(1,5)])]:
        report = load(P/filename)
        assert report['completed'] == report['unavailable'] == 0
        assert [x['id'] for x in report['panels_or_controls']] == keys
        for row in report['panels_or_controls']:
            assert row['status'] == 'NOT_EXECUTED_PRECEDING_GATE'
            assert row['Final_specific_gate'] == 'NOT_EXECUTED_FINAL_BOUNDARY'
            assert not row['coverage_assessed'] and row['fit_or_score_attempts'] == 0
    baseline = load(E/'REQUIREMENT_BASELINE.json')
    trace = load(E/'REQUIREMENT_TRACE.json')
    assert len(baseline['items']) == len(trace['trace']) == trace['baseline_requirement_count'] == 399
    assert not trace['full_contract_satisfied'] and trace['required_items_silently_omitted'] == 0
    assert len({x['requirement_id'] for x in trace['trace']}) == 399
    for a, b in zip(baseline['items'], trace['trace']):
        assert (a['id'], a['owner_line'], a['requirement']) == (b['requirement_id'], b['owner_line'], b['requirement'])
        assert not b['scientific_requirement_waived']
        assert all((R/path).exists() for path in b['evidence'])
    assert trace['verified_baseline_count'] == sum(x['status']=='VERIFIED_PREREQUISITE' for x in trace['trace']) < 399
    role = load(P/'SOURCE_AND_ROLE_ACCESS_LEDGER.json')
    assert not role['B_neural_access'] and not role['E_neural_access']
    assert not role['Final_C_access'] and not role['Final_D_access']
    assert role['new_source_HTTP'] == {'requests': 0, 'payload_bytes': 0, 'reserved_bytes': 0, 'retries': 0}
    return {'scientific_status': stop['scientific_status'], 'M3_PASS': False,
        'real_optimizer_attempts': 0, 'B_E_scientific_access': False,
        'Final_C_access': False, 'Final_D_access': False, 'trace_entries': 399,
        'verified_prerequisite_requirements': trace['verified_baseline_count'],
        'full_mission_contract_satisfied': False, 'warnings_preserved': 2}


def verify_all():
    base = verify()
    records = verify_records()
    manifest = P/'FINAL_FREEZE_MANIFEST.json'
    assert manifest.exists(), 'Final freeze manifest required; no weaker replay fallback'
    count = validate_manifest(load(manifest))
    # Explicit source-identity verification precedes import of the historical
    # saved-only implementation, whose complete code is itself R4-bound.
    from paper16_source_r4.verify_saved import verify_saved as verify_r4
    inherited = verify_r4()
    assert inherited['total_complete_sources'] == 28 and inherited['admitted_complete_sources'] == 27
    assert inherited['frozen_payloads_verified'] == 8248
    assert inherited['admitted_BO'] == 5 and inherited['admitted_FC'] == 22
    assert inherited['MODEL_FITS_EXECUTED'] == inherited['new_HTTP_requests_by_replay'] == 0
    return {'mission': 'P16-M3-M5-FROZEN-DEVELOPMENT-R1',
        'saved_only_integrity_reproduction': 'PASS', 'scientific_mission_PASS': False,
        'current_frozen_payloads_verified': count,
        'BASE': base['BASE'], 'inherited_R4_saved_reproduction': inherited,
        'STOP_records_verified': records,
        'scope': 'Saved hashes/private historical A QC/STOP reporting; no source requests, optimization, B/E scoring or Final access',
        'public_clone_alone_sufficient': False}


if __name__ == '__main__':
    with patch('socket.socket.connect', side_effect=RuntimeError('Saved-only STOP reproduction: network forbidden')):
        print(json.dumps(verify_all(), sort_keys=True, allow_nan=False))
