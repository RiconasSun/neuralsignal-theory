"""Prospective controlled-only NUM3 feasibility; any required failure stops."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
import oracle_m4_num2 as old
import deterministic_poisson_oracle as independent
import rqmc_poisson_filter as evaluator

PAPER = Path(__file__).resolve().parents[1]
SPEC = PAPER/'data_manifest/M4/numerical_amendment3.json'
LOCK = PAPER/'data_manifest/M4/numerical_amendment3_lock.r2.json'
OUTPUT = PAPER/'results/M4_amendment3'


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def identity():
    names = ['data_manifest/M4/numerical_amendment3.json', 'scripts/run_m4_num3.py',
             'scripts/rqmc_poisson_filter.py', 'scripts/deterministic_poisson_oracle.py',
             'scripts/guided_poisson_filter.py', 'scripts/oracle_m4_num2.py',
             'tests/test_m4_num3.py', 'scripts/reproduce-m4-num3.ps1', 'REPRODUCE_M4_NUM3.md']
    names += [f'results/{name}/gate_result.json' for name in ('M0', 'M1', 'M2', 'M3', 'M4', 'M4_amendment1', 'M4_amendment2')]
    names += ['protocol/protocol.json', 'data_manifest/frozen_splits.json']
    # Split filename is recovered from the frozen pipeline constant, never counts.
    names.remove('data_manifest/frozen_splits.json')
    names.append(old.previous.original.m3.m2.m1.SPLIT.relative_to(PAPER).as_posix())
    names += [p.relative_to(PAPER).as_posix() for p in sorted((PAPER/'scripts').glob('*.py'))]
    names += ['environment/environment.json']
    return {name: digest(PAPER/name) for name in sorted(set(names))}


def assert_frozen():
    if load(LOCK)['sha256'] != identity():
        raise ValueError('Final NUM3 source/input identity differs from registration')


def register():
    for milestone in ('M0', 'M1', 'M2', 'M3'):
        if load(PAPER/f'results/{milestone}/gate_result.json')['gate'] != 'PASS':
            raise ValueError(f'{milestone} prerequisite not PASS')
    current = identity()
    if LOCK.exists():
        if load(LOCK)['sha256'] != current:
            raise ValueError('Registered NUM3 source or inputs changed; no silent repair')
    else:
        write(LOCK, {'id': 'M4-NUM-3', 'registered_at_utc': now(), 'before_new_tests': True,
              'controlled_fixtures_only': True, 'final_holdout_access': False,
              'prior_NUM2_exposure_disclosed': True,
              'engineering_revision': 'r2; initial partial NUM3 diagnostics exposed and archived; numerical policy unchanged',
              'original_registration_sha256': digest(PAPER/'data_manifest/M4/numerical_amendment3_lock.json'),
              'sha256': current})
    return load(LOCK)


def fixtures():
    y = np.array([[0, 1, 0, 2], [1, 0, 2, 0], [0, 1, 1, 0]])
    cases = [('original_K1_D2', old.fixture(1), y), ('original_K2_D2', old.fixture(2), y)]
    model = old.fixture(2)
    model['loadings'] = model['loadings']*4
    cases.append(('concentrated_K2_D2', model, np.array([[0, 8, 0, 12], [9, 0, 10, 0], [0, 7, 6, 0]])))
    return [(name, model, counts, np.full(counts.shape, -1.)) for name, model, counts in cases]


def oracle(model, counts, offsets, spec):
    gh, gl, records = [], [], []
    for order in spec['hermite_orders']:
        start = time.perf_counter()
        values = old.quadrature(model, counts, offsets, order)
        gh.append(values)
        records.append({'method': 'Gauss-Hermite', 'order': order, 'scores': values.tolist(), 'wall_seconds': time.perf_counter()-start})
    for order in spec['legendre_orders']:
        start = time.perf_counter()
        values = independent.scores(model, counts, offsets, order, spec['domain_limit'])
        gl.append(values)
        records.append({'method': 'Gauss-Legendre density', 'order': order, 'scores': values.tolist(), 'wall_seconds': time.perf_counter()-start})
    center = gh[-1]
    tail = independent.tail_log_sensitivity(model, gl[-1], spec['domain_limit'])
    # Sum conservative convergence sensitivities; not a mathematical quadrature bound.
    sensitivity = (np.abs(gh[-1]-gh[-2])+np.abs(gh[-2]-gh[-3])+
                   np.abs(gl[-1]-gl[-2])+np.abs(gl[-2]-gl[-3])+np.abs(gh[-1]-gl[-1])+tail)/counts.shape[1]
    passed = bool(np.max(sensitivity) <= spec['oracle_sensitivity_limit'])
    return {'gate': 'PASS' if passed else 'FAIL', 'scores': center.tolist(),
            'sensitivity_nats_unit_bin': sensitivity.tolist(), 'tail_log_sensitivity': tail.tolist(),
            'runs': records, 'absolute_error_proven': False,
            'limitation': 'Independent-method and successive-order agreement are empirical sensitivity, not certified absolute error.'}


def summary(values, target, sensitivity, units):
    values = np.asarray(values)
    errors = (values-target)/units
    sd = errors.std(axis=0, ddof=1)
    bound = np.max(np.abs(errors), axis=0)+1.96*sd+sensitivity
    trial_errors = errors.mean(axis=1)
    trial_bound = float(np.max(np.abs(trial_errors))+1.96*trial_errors.std(ddof=1)+np.mean(sensitivity))
    # Jensen gap is computed for prefix likelihood estimators, not bin ratios.
    prefixes = np.cumsum(values, axis=1)
    log_mean_likelihood = logsumexp(prefixes, axis=0)-np.log(len(values))
    gap = (log_mean_likelihood-prefixes.mean(axis=0))/units
    return {'maximum_bin_discrepancy': float(np.max(bound)), 'bin_discrepancy': bound.tolist(),
            'trial_discrepancy': trial_bound, 'bin_sd': sd.tolist(),
            'bin_mean_minus_oracle': errors.mean(axis=0).tolist(),
            'mean_error_95_halfwidth': (1.96*sd/np.sqrt(len(values))).tolist(),
            'prefix_jensen_gap_nats_unit': gap.tolist(),
            'limitation': 'Finite-replicate confidence is empirical; Jensen gap is not an unbiased estimate of log-score bias.'}


def evaluate(spec, output=OUTPUT):
    rows, errors = [], []
    for name, model, counts, offsets in fixtures():
        assert_frozen()
        reference = oracle(model, counts, offsets, spec)
        record = {'fixture': name, 'oracle': reference, 'evaluations': []}
        rows.append(record)
        write(output/'progress.json', {'fixtures': rows, 'errors': errors, 'final_holdout_access': False})
        if reference['gate'] != 'PASS':
            errors.append(f'Independent oracle unresolved: {name}')
            break
        for method, budgets in [('mc', [spec['mc_comparator_budget']]), ('rqmc', spec['candidate_particles'])]:
            for budget in budgets:
                start = time.perf_counter()
                scores, diagnostics = [], []
                for seed in spec['seeds']:
                    values, diagnostic = evaluator.particle(model, counts, offsets, budget, seed, method)
                    scores.append(values.tolist())
                    diagnostics.append({'seed': seed, **diagnostic})
                result = summary(scores, np.asarray(reference['scores']), np.asarray(reference['sensitivity_nats_unit_bin']), counts.shape[1])
                result.update(method=method, particles=budget, scores=scores, diagnostics=diagnostics,
                              wall_seconds=time.perf_counter()-start)
                record['evaluations'].append(result)
                write(output/'progress.json', {'fixtures': rows, 'errors': errors, 'final_holdout_access': False})
        final = record['evaluations'][-1]
        if (max(final['maximum_bin_discrepancy'], final['trial_discrepancy']) > spec['threshold_nats_unit_bin'] or
                any(d['laplace_nonconverged_guides'] or d['overflow_rates'] for d in final['diagnostics'])):
            errors.append(f'Registered accuracy FAIL: {name}')
            break
    return rows, errors


def report(rows, errors, tests_exit, started):
    assert_frozen()
    gate = {'milestone': 'M4', 'amendment': 'M4-NUM-3', 'stage': 'controlled_numerical_feasibility',
            'gate': 'FAIL' if errors else 'PASS', 'scientific_verdict': 'INCONCLUSIVE' if errors else 'NOT_EVALUATED',
            'errors': errors, 'tests_exit_code': tests_exit, 'final_holdout_access': False,
            'real_neural_evaluation': False, 'started_at_utc': started, 'finished_at_utc': now(),
            'lock_sha256': digest(LOCK), 'threshold_nats_unit_bin': .001}
    write(OUTPUT/'gate_result.json', gate)
    write(OUTPUT/'qc_report.json', {'fixtures': rows, 'errors': errors, 'source_sha256': identity(),
          'fixtures_not_experimental_findings': True, 'final_holdout_access': False})
    write(OUTPUT/'claim_audit.json', {'supported': ['Controlled numerical feasibility diagnostics only'],
          'unsupported': ['Real hippocampal accuracy', 'Preferred regime', 'Absolute error proof', 'NAP/CWP validated', 'Nulls or holdouts passed']})
    lines = ['# NUM3 Numerical Feasibility', '', 'Controlled fixtures only; no experimental finding.',
             'Gate: '+gate['gate']+'. '+('; '.join(errors) or 'All registered controlled fixtures passed.'), '',
             'Independent GH/GL convergence is sensitivity evidence, not certified absolute accuracy.',
             'Prefix Jensen gap, replicate SD and oracle sensitivity are distinct quantities.', '']
    for row in rows:
        lines.append('## '+row['fixture'])
        lines.append('Oracle gate: '+row['oracle']['gate'])
        for result in row['evaluations']:
            lines.append(f"- {result['method']} N={result['particles']}: max bin discrepancy={result['maximum_bin_discrepancy']:.12g}; trial={result['trial_discrepancy']:.12g}")
    lines += ['', 'Prior M4/NUM1/NUM2 failures unchanged. No final holdout access.',
              'Five prior scientific warnings remain OPEN; controlled tests cannot close them.',
              'On FAIL: stop numerical remediation and retain M4 INCONCLUSIVE.']
    (OUTPUT/'QC_REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'gate': gate['gate'], 'errors': errors, 'fixtures': len(rows)}), flush=True)
    return gate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--register', action='store_true')
    args = parser.parse_args()
    registered = register()
    if args.register:
        print(json.dumps({'registered_at_utc': registered['registered_at_utc'], 'source_count': len(registered['sha256'])}))
        return 0
    OUTPUT.mkdir(parents=True, exist_ok=True)
    started = now()
    spec = load(SPEC)
    assert_frozen()
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(PAPER/'tests'), '-p', 'test_m4_num3.py', '-v'], capture_output=True, text=True)
    (OUTPUT/'tests.txt').write_text(tests.stdout+tests.stderr, encoding='utf-8')
    assert_frozen()
    rows, errors = [], []
    if tests.returncode:
        errors.append('NUM3 correctness tests failed')
    else:
        try:
            rows, errors = evaluate(spec)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            if (OUTPUT/'progress.json').exists():
                rows = load(OUTPUT/'progress.json')['fixtures']
            errors.append(str(error))
    gate = report(rows, errors, tests.returncode, started)
    return 1 if gate['gate'] != 'PASS' else 0


if __name__ == '__main__':
    sys.exit(main())
