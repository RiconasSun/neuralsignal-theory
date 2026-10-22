"""Independent metadata/source-only verification; no scientific imports or calls."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import time

R = Path.cwd().resolve()
P = R / 'paper16_development_r5'
E = R / 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5'
Q = R / 'paper16_shutdown_recovery_r5_protocol'
PHASE_SHA = 'ea5bd6523dec17593e0de559e774e33afa2735a4a998543322c83fdca18e466e'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def bound(path):
    value = (R / path).resolve()
    require(value.is_relative_to(R), 'Repository-bound identity: ' + str(path))
    return value

def rows_check(rows):
    require(len({row['path'] for row in rows}) == len(rows), 'Unique identity rows')
    for row in rows:
        path = bound(row['path'])
        require(digest(path) == row['sha256'], 'Fresh source/artifact hash: ' + row['path'])
    return len(rows)

def run(manifest_name, certification_name, number, output_name):
    phase_path = P / 'PHASE_A_CLAIM.json'
    require(digest(phase_path) == PHASE_SHA, 'Original Phase-A claim')
    phase = read(phase_path)
    now = dt.datetime.now(dt.timezone.utc)
    first, last = [dt.datetime.fromisoformat(phase[key]) for key in ['start_UTC', 'deadline_UTC']]
    require((last - first).total_seconds() == 86400 and first <= now < last,
            'Same unextended, unexpired original 24-hour Phase A')
    require(0 < phase['deadline_monotonic'] - phase['start_monotonic'] <= 86400,
            'Original monotonic Phase-A ceiling')
    require(phase['start_monotonic'] <= time.monotonic() < phase['deadline_monotonic'],
            'Live monotonic Phase-A interval')
    require(phase['no_reset'] is True and phase['E_authorized'] is False and phase['Final_authorized'] is False,
            'Original irreversible phase and denied outcome roles')

    manifest_path = P / manifest_name
    manifest = read(manifest_path)
    require(manifest['phase_A_claim_sha256'] == PHASE_SHA and manifest['before_new_real_fits'] is True,
            'Final exact prefit manifest semantics')
    file_count = rows_check(manifest['files'])
    source_by_path = {row['path']: row['sha256'] for row in manifest['files']}
    required = ['core.py', 'controller.py', 'evidence_checks.py', 'features.py', 'models.py',
                'optimizer.py', 'optim_child.py', 'panels.py', 'controls.py', 'certify.py', 'test_recovery.py']
    for name in required:
        require('paper16_development_r5/' + name in source_by_path, 'Final production/test coverage: ' + name)

    certificate_path = P / certification_name
    certificate = read(certificate_path)
    require(certificate['mandatory_tests_pass'] is True and certificate['real_fits_executed'] == 0,
            'Final actual synthetic-only certification')
    result_path, registration_path = [bound(certificate[key]) for key in ['test_result_path', 'registration_path']]
    require(digest(result_path) == certificate['test_result_sha256'], 'Actual result binding')
    require(digest(registration_path) == certificate['registration_sha256'], 'Actual prospective source/method registration')
    result, registration = read(result_path), read(registration_path)
    require(result['candidate_registration_sha256'] == digest(registration_path), 'Worker checked actual registration')
    require(registration['phase_A_claim_sha256'] == PHASE_SHA and registration['real_fits_authorized'] is False,
            'Synthetic-only prospective registration')
    require(result['source_files'] == registration['source_files'], 'Same registered and executed sources')
    rows_check(result['source_files'])
    for row in result['source_files']:
        require(source_by_path.get(row['path']) == row['sha256'], 'Tested source included in final freeze')
    require(result['unique_registered_methods'] == registration['methods'], 'Actual exact method inventory')
    methods = registration['methods']
    require(len(methods) == len(set(methods)) == result['tests_run'], 'Every registered method actually counted')
    require(result['failures'] == result['errors'] == result['skipped'] == 0 and result['mandatory_tests_pass'] is True,
            'No errors, failures, skips or partial method acceptance')
    require(result['real_fits_executed'] == 0 and result['E_real_access'] is False and result['Final_access'] is False,
            'Actual synthetic-only result')
    native_path = P / ('CERTIFICATION_' + str(number) + '_SUPERVISION.json')
    native = read(native_path)
    require(digest(native_path) == certificate['supervision_sha256'], 'Actual native supervision binding')
    require(native['returncode'] == 0 and native['killed_at_deadline'] is False
            and native['completed_before_deadline'] is True and native['clock_failure'] is None
            and native['native_job_tree_enforced'] is True and native['assigned_before_resume'] is True,
            'Actual native Windows Job complete receipt')
    log_path = E / ('CERTIFICATION_' + str(number) + '.log')
    log = log_path.read_text(encoding='utf-8-sig')
    require(re.search(r'Ran\s+' + str(len(methods)) + r'\s+tests\s+in\s+[0-9.]+s', log) is not None,
            'Actual native unittest count in log')
    require(log.rstrip().endswith('OK'), 'Actual native test log successful terminus')

    for row in read(P / 'MATHEMATICAL_COPY_PROOF.json')['files']:
        original, current = bound(row['source']), bound(row['target'])
        require(digest(original) == row['source_sha256'] and digest(current) == row['target_sha256'],
                'Original/final mathematical identity')
        expected = original.read_bytes()
        if row['permitted_replacements']:
            expected = expected.replace(b'paper16_development_r4', b'paper16_development_r5').replace(b'P16_R4_JOB', b'P16_R5_JOB')
        require(current.read_bytes() == expected, 'Only registered namespace/Job substitutions')
    pins = read(Q / 'SOURCE_PINS.json')['files']
    for name, row in pins.items():
        require(digest(bound(name)) == row['sha256'] and bound(name).stat().st_size == row['bytes'],
                'Original protocol pin ' + name)

    admission = read(P / 'REUSE_ADMISSION.json')
    require(admission['required_gate_pass'] is True and admission['optimizer_states_admitted'] == 3992
            and admission['B0_certificates_admitted'] == 216, 'Complete actual reuse admission')
    acceptance = read(E / 'INDEPENDENT_R5_REUSE_MATRIX_ACCEPTANCE.json')
    require(acceptance['decision'] == 'ACCEPTED_COMPLETE_3992_216_REUSE_MATRIX'
            and acceptance['open_P0'] == acceptance['open_P1'] == 0,
            'Independent complete reuse acceptance')
    require(digest(P / 'PRIMARY_OPTIMIZER_V2_MATRIX.json') == acceptance['primary_optimizer_matrix_sha256']
            and digest(P / 'PRIMARY_B0_V2_MATRIX.json') == acceptance['primary_B0_matrix_sha256']
            and digest(E / 'INDEPENDENT_R5_REUSE_RESULT.json') == acceptance['independent_result_sha256'],
            'Final matrices remain the independently compared exact originals')
    require(len(read(Q / 'RECOVERY_TASK_PLAN.json')['tasks']) == 2479, 'Original exact recovery denominator')
    for name in ['STAGE_CLAIM.json', 'WORKER_CLAIM.json', 'FIT_JOURNAL.jsonl', 'M4_READY_FOR_INDEPENDENT_REVIEW.json', 'WORKER_COMPLETE.json']:
        require(not (P / 'results' / name).exists(), 'No preapproval real execution/complete-M4 receipt: ' + name)
    require(not (P / 'work/fits').exists(), 'No preapproval new real fit workspace')

    report = {
        'mission': 'P16-M3-M5-SHUTDOWN-RECOVERY-R5', 'reviewer': '/root/r4_interruption_review',
        'recorded_UTC': now.isoformat(), 'metadata_only': True, 'scientific_imports': 0,
        'objective_gradient_AD_FD_score_minimize_calls': 0, 'raw_neural_source_access': False,
        'protected_saved_state_reaudit_executed': False, 'E_access': False, 'Final_access': False,
        'phase_A_claim_sha256': PHASE_SHA, 'manifest_path': str(manifest_path.relative_to(R)).replace('\\', '/'),
        'manifest_sha256': digest(manifest_path), 'fresh_manifest_rows_verified': file_count,
        'certification_path': str(certificate_path.relative_to(R)).replace('\\', '/'),
        'certification_sha256': digest(certificate_path), 'registered_and_executed_methods': len(methods),
        'actual_native_result_sha256': digest(result_path), 'actual_native_registration_sha256': digest(registration_path),
        'actual_native_supervision_sha256': digest(native_path), 'actual_native_log_sha256': digest(log_path),
        'protocol_pins_verified': len(pins), 'no_new_real_A_before_approval': True,
        'decision': 'PASS_METADATA_BINDINGS_ONLY', 'review_source_sha256': digest(Path(__file__)),
    }
    output_path = E / output_name
    with output_path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True), flush=True)

if __name__ == '__main__':
    run(*sys.argv[1:])
