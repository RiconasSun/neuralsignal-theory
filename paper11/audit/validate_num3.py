"""Bind saved NUM3 results to the frozen execution without rerunning numerics."""
import argparse
import sys
from datetime import datetime
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import run_m4_num3 as run


def verify(qc, gate, output_validation, progress, registered, lock_hash):
    if qc['source_sha256'] != registered['sha256']:
        raise ValueError('Saved QC source identity differs from registration')
    if gate['lock_sha256'] != lock_hash:
        raise ValueError('Saved gate registration identity differs')
    if qc['fixtures'] != progress['fixtures'] or qc['errors'] != gate['errors']:
        raise ValueError('Mixed QC/progress/gate attempts')
    if not (datetime.fromisoformat(registered['registered_at_utc']) <= datetime.fromisoformat(gate['started_at_utc'])
            <= datetime.fromisoformat(gate['finished_at_utc']) <= datetime.fromisoformat(output_validation['finished_at_utc'])):
        raise ValueError('Inconsistent registration/execution/report chronology')
    spec = run.load(run.SPEC)
    required = spec['mandatory_fixtures']
    mapped = {'original_K1_D2': 'original_K1_D2', 'original_K2_D2': 'original_K2_D2', 'concentrated_K2_D2': 'concentrated_K2_D2'}
    failed = False
    for index, fixture in enumerate(qc['fixtures']):
        if failed or fixture['fixture'] != mapped[required[index]]:
            raise ValueError('Unexpected fixtures after mandatory failure')
        if fixture['oracle']['gate'] != 'PASS':
            failed = True
            if fixture['evaluations']:
                raise ValueError('Stochastic evaluation after oracle failure')
            continue
        expected = [('mc', spec['mc_comparator_budget'])]+[('rqmc', n) for n in spec['candidate_particles']]
        if [(v['method'], v['particles']) for v in fixture['evaluations']] != expected:
            raise ValueError('Saved budget/method coverage differs from registration')
        for estimate in fixture['evaluations']:
            if len(estimate['scores']) != spec['repetitions'] or [d['seed'] for d in estimate['diagnostics']] != spec['seeds']:
                raise ValueError('Missing or reordered mandatory repetitions')
            recalculated = run.summary(estimate['scores'], np.asarray(fixture['oracle']['scores']),
                np.asarray(fixture['oracle']['sensitivity_nats_unit_bin']), 4)
            for key, expected_value in recalculated.items():
                if key == 'limitation':
                    continue
                if not np.allclose(estimate[key], expected_value, rtol=0, atol=1e-14):
                    raise ValueError('Saved score diagnostic does not match raw replicas: '+key)
        last = fixture['evaluations'][-1]
        failed = (max(last['maximum_bin_discrepancy'], last['trial_discrepancy']) > spec['threshold_nats_unit_bin'] or
                  any(d['laplace_nonconverged_guides'] or d['overflow_rates'] for d in last['diagnostics']))
    expected_gate = 'FAIL' if failed or gate['tests_exit_code'] else 'PASS'
    if not failed and not gate['tests_exit_code'] and len(qc['fixtures']) != len(required):
        raise ValueError('Incomplete fixture coverage cannot PASS')
    if gate['gate'] != expected_gate or gate['real_neural_evaluation'] or gate['final_holdout_access']:
        raise ValueError('Gate verdict or safety flags inconsistent')
    return {'registered_execution_bound': True, 'recomputed_gate': expected_gate,
            'coverage': len(qc['fixtures']), 'fixtures_not_experimental_findings': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--register-audit', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).parent
    audit_lock = root/'num3_audit_lock.json'
    source_names = ['validate_num3.py', 'test_validate_num3.py', 'reproduce-num3-audit.ps1']
    audit_identity = {name: run.digest(root/name) for name in source_names}
    if args.register_audit:
        if audit_lock.exists():
            if run.load(audit_lock)['sha256'] != audit_identity:
                raise ValueError('Audit implementation changed')
        else:
            run.write(audit_lock, {'registered_at_utc': run.now(), 'scope': 'post-execution artifact integrity only; no numerical retesting', 'sha256': audit_identity})
        print('Saved-artifact auditor registered; no numerical choice changed')
        return 0
    if run.load(audit_lock)['sha256'] != audit_identity:
        raise ValueError('Audit implementation changed')
    run.assert_frozen()
    output = run.OUTPUT
    qc = run.load(output/'qc_report.json')
    gate = run.load(output/'gate_result.json')
    original_validation = run.load(output/'output_validation.json')
    if (original_validation['fixture_qc_sha256'] != run.digest(output/'qc_report.json') or
            original_validation['gate_sha256'] != run.digest(output/'gate_result.json')):
        raise ValueError('QC/gate changed since saved-output report generation')
    result = verify(qc, gate, original_validation, run.load(output/'progress.json'), run.load(run.LOCK), run.digest(run.LOCK))
    result.update(audited_at_utc=run.now(), source_sha256=audit_identity,
        numerical_lock_sha256=run.digest(run.LOCK), audit_lock_sha256=run.digest(audit_lock),
        artifact_sha256={name: run.digest(output/name) for name in ('qc_report.json', 'gate_result.json', 'progress.json', 'output_validation.json')},
        numerical_reexecution=False)
    run.write(output/'artifact_integrity_audit.json', result)
    print('PASS saved execution identity, raw-replica diagnostics, coverage, chronology and STOP; numerical '+result['recomputed_gate'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
