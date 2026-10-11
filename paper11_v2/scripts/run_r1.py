"""Registered R1 controlled numerical verification; no experimental data input."""
import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import run_r0 as base

OUT = base.STUDY / 'results/R1'
SOURCE_NAMES = ['protocol/protocol.json', 'protocol/r0_amendment1.json',
                'protocol/r1_implementation.json', 'requirements.txt', 'scripts/predictive_models.py',
                'scripts/run_r1.py', 'tests/test_r1_models.py', 'tests/test_r1_runner.py',
                'scripts/reproduce-r1.ps1']
PROGRESS = []


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify():
    reg = load(OUT / 'registration.json')
    for key in ['source_sha256', 'preceding_sha256', 'archive_sha256']:
        for rel, sha in reg[key].items():
            if base.digest(base.ROOT / rel) != sha:
                raise RuntimeError(f'R1 integrity violation: {rel}')
    if load(base.STUDY / 'results/R0_amendment1_code1/gate_result.json')['gate_verdict'] != 'PASS':
        raise RuntimeError('R1 prohibited without R0 PASS')
    return reg


def register():
    if (OUT / 'registration.json').exists():
        verify()
        print('R1 existing prospective registration verified.')
        return
    prior = base.STUDY / 'results/R0_amendment1_code1'
    for rel, sha in load(prior / 'artifact_lock.json')['sha256'].items():
        if base.digest(base.ROOT / rel) != sha:
            raise RuntimeError(f'Preceding R0 output changed: {rel}')
    if load(prior / 'gate_result.json')['gate_verdict'] != 'PASS':
        raise RuntimeError('R0 must PASS first')
    subprocess.run([sys.executable, str(base.STUDY / 'scripts/run_r0_amend1_repair.py'), 'verify'], check=True)
    reg0 = load(base.STUDY / 'results/R0/registration.json')
    for rel, sha in reg0['archive_sha256'].items():
        if base.digest(base.ROOT / rel) != sha:
            raise RuntimeError(f'Protected archive changed: {rel}')
    preceding = {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p)
                 for folder in ['R0', 'R0_schema1', 'R0_final', 'R0_amendment1', 'R0_amendment1_code1']
                 for p in (base.STUDY / 'results' / folder).rglob('*') if p.is_file()}
    sources = {f'paper11_v2/{name}': base.digest(base.STUDY / name) for name in SOURCE_NAMES}
    OUT.mkdir(parents=True, exist_ok=True)
    base.save(OUT / 'registration.json', {
        'study': 'P11-v2', 'milestone': 'R1',
        'registered_utc': datetime.now(timezone.utc).isoformat(),
        'base_commit': base.git('rev-parse', 'HEAD'), 'source_sha256': sources,
        'preceding_sha256': preceding, 'archive_sha256': reg0['archive_sha256'],
        'before_R1_tests_and_fits': True, 'real_neural_input': False,
        'scope': 'Controlled implementation verification, not hippocampal findings',
        'policy': load(base.STUDY / 'protocol/r1_implementation.json'),
        'python': platform.python_version()
    }, immutable=True)
    print('Registered R1 before controlled fixture evaluation.')


def _execute():
    import numpy as np
    import scipy
    import predictive_models as models
    sys.path.insert(0, str(base.STUDY / 'tests'))
    import test_r1_models as audit
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(base.STUDY / 'tests'),
                            '-p', 'test_r1*.py', '-v'], capture_output=True, text=True)
    (OUT / 'tests.log').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    failures, rows = [], PROGRESS
    oracle = {}
    if tests.returncode:
        failures.append('Automated model correctness tests failed')
    try:
        oracle = audit.numerical_audit()
        base.save(OUT / 'oracle.json', oracle, immutable=True)
    except Exception as exc:
        failures.append(f'Independent numerical audit: {type(exc).__name__}: {exc}')
    if not failures:
        rng = np.random.default_rng(20261011)
        x = np.broadcast_to(np.stack([np.arange(6)/5, (np.arange(6)==0).astype(float)], axis=-1), (4,6,2)).copy()
        y = rng.poisson(np.broadcast_to(np.exp(-0.3+0.1*x[:,:,0,None]), (4,6,2)))
        pos = np.arange(4, dtype=float)/3
        base.save(OUT / 'controlled_fixture.json', {'synthetic': True, 'seed': 20261011,
                  'counts': y.tolist(), 'context': x.tolist(), 'trial_position': pos.tolist(),
                  'experimental_finding': False}, immutable=True)
        baseline_types = ['stationary', 'history', 'event', 'drift', 'combined', 'population']
        offset, shared_params = None, None
        for kind in baseline_types:
            if kind == 'stationary':
                eta = models.fit_stationary(y)
                score = float(models.poisson_logpmf(y, eta).sum())
                rows.append({'family': kind, 'parameters': 2, 'converged': True,
                             'log_expected_counts': np.asarray(eta).tolist(), 'synthetic_only': True,
                             'total_loglik': score, 'nats_per_unit_bin': score/y.size,
                             'observed_unit_bins': int(y.size)})
                continue
            design = models.make_design(y, x, kind, lags=5, trial_position=pos)
            model = models.PoissonGLM(design, y)
            for ridge in [0.001,0.01,0.1,1.0]:
                for seed in [11,23,37]:
                    try:
                        result = models.fit_model(model, ridge, seed)
                    except Exception as exc:
                        failures.append(f'Baseline failure {kind}/{ridge}/{seed}: {type(exc).__name__}: {exc}')
                        rows.append({'family': kind, 'ridge': ridge, 'seed': seed,
                                     'converged': False, 'error': str(exc)})
                        continue
                    row = {'family': kind, 'ridge': ridge, 'seed': seed,
                           'parameters': model.n_parameters, 'synthetic_only': True, **result,
                           'nats_per_unit_bin': result['total_loglik']/y.size if result['total_loglik'] is not None else None,
                           'observed_unit_bins': int(y.size)}
                    rows.append(row)
                    if not result['converged']:
                        failures.append(f'Baseline nonconvergence {kind}/{ridge}/{seed}')
                    if kind == 'combined' and ridge == 0.1 and seed == 11 and result['converged']:
                        theta = np.asarray(result['theta']).reshape(2, design.shape[-1])
                        offset = np.einsum('ntuf,uf->ntu', design, theta)
                        shared_params = model.n_parameters
        if not failures:
            configs = [('discrete', k, 0) for k in [2,4]]
            configs += [('continuous', d, 0) for d in [1,2,4]]
            configs += [('hybrid', k, lag) for k in [2,4] for lag in [1,5]]
            for family, size, lag in configs:
                for ridge in [0.001,0.01,0.1,1.0]:
                    for seed in [11,23,37]:
                        model = (models.RecurrentPoisson(y, x, offset, size) if family == 'continuous'
                                 else models.StatePoisson(y, offset, size, lags=lag))
                        try:
                            result = models.fit_model(model, ridge, seed)
                            row = {'family': family, 'size': size, 'lags': lag, 'ridge': ridge,
                                   'seed': seed, 'extra_parameters': model.n_parameters,
                                   'shared_parameters': shared_params,
                                   'total_parameters': shared_params+model.n_parameters,
                                   'synthetic_only': True, **result,
                                   'nats_per_unit_bin': result['total_loglik']/y.size if result['total_loglik'] is not None else None,
                                   'observed_unit_bins': int(y.size)}
                            rows.append(row)
                            if not result['converged']:
                                failures.append(f'Model nonconvergence {family}/{size}/{lag}/{ridge}/{seed}')
                        except Exception as exc:
                            failures.append(f'Model failure {family}/{size}/{lag}/{ridge}/{seed}: {type(exc).__name__}: {exc}')
                            rows.append({'family': family, 'size': size, 'lags': lag, 'ridge': ridge,
                                         'seed': seed, 'converged': False, 'error': str(exc)})
        # Preserve every attempted run, including failures. No seed selection or winner.
    base.save(OUT / 'fit_diagnostics.json', {'synthetic_only': True, 'rows': rows,
              'fixture_selection_or_regime_ranking': False}, immutable=True)
    gate = {'study': 'P11-v2', 'milestone': 'R1',
            'gate_verdict': 'FAIL' if failures else 'PASS', 'failures': failures,
            'tests_exit_code': tests.returncode, 'oracle': oracle,
            'controlled_runs': len(rows), 'scientific_verdict': 'NOT_EVALUATED',
            'real_cohort_fitted': False, 'oldtest_accessed': False, 'external_spikes_accessed': False,
            'final_holdout_locked': True, 'R2_executed': False,
            'numpy': np.__version__, 'scipy': scipy.__version__,
            'source_sha256': load(OUT / 'registration.json')['source_sha256']}
    verify()
    base.save(OUT / 'QC.json', gate, immutable=True)
    base.save(OUT / 'gate_result.json', gate, immutable=True)
    lock = {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p)
            for p in OUT.iterdir() if p.is_file()}
    base.save(OUT / 'artifact_lock.json', {'sha256': lock}, immutable=True)
    print(json.dumps(gate, indent=2))
    return 1 if failures else 0


def execute():
    verify()
    if (OUT / 'execution_started.json').exists() or (OUT / 'gate_result.json').exists():
        raise RuntimeError('R1 namespace already started; use replay, never overwrite evidence')
    base.save(OUT / 'execution_started.json', {'utc': datetime.now(timezone.utc).isoformat(),
              'preserve_all_failures': True}, immutable=True)
    try:
        return _execute()
    except Exception as exc:
        detail = {'exception': type(exc).__name__, 'message': str(exc), 'rows': PROGRESS,
                  'synthetic_only': True, 'holdouts_locked': True}
        base.save(OUT / 'fatal_exception.json', detail, immutable=True)
        if not (OUT / 'gate_result.json').exists():
            gate = {'study': 'P11-v2', 'milestone': 'R1', 'gate_verdict': 'FAIL',
                    'failures': [f'{type(exc).__name__}: {exc}'],
                    'controlled_runs': len(PROGRESS), 'scientific_verdict': 'NOT_EVALUATED',
                    'final_holdout_locked': True, 'real_cohort_fitted': False}
            if not (OUT / 'fit_diagnostics.json').exists():
                base.save(OUT / 'fit_diagnostics.json', detail, immutable=True)
            base.save(OUT / ('failure_QC.json' if (OUT / 'QC.json').exists() else 'QC.json'), gate, immutable=True)
            base.save(OUT / 'gate_result.json', gate, immutable=True)
            lock = {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p)
                    for p in OUT.iterdir() if p.is_file() and p.name != 'artifact_lock.json'}
            base.save(OUT / 'artifact_lock.json', {'sha256': lock}, immutable=True)
        print(json.dumps(detail))
        return 1


def replay():
    verify()
    if (OUT / 'fatal_exception.json').exists():
        print('Preserved fatal execution failure; cannot replay as PASS.')
        return 1
    lock = load(OUT / 'artifact_lock.json')['sha256']
    for rel, sha in lock.items():
        path = base.ROOT / rel
        if not path.is_file() or base.digest(path) != sha:
            raise RuntimeError(f'Missing/corrupt preserved R1 evidence: {rel}')
    gate = load(OUT / 'gate_result.json')
    print(json.dumps({'saved_only': True, 'gate_verdict': gate['gate_verdict'],
                      'scientific_verdict': 'NOT_EVALUATED', 'holdouts_locked': True}))
    return 0 if gate['gate_verdict'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register','execute','verify','replay'])
    action = parser.parse_args().action
    if action == 'register':
        register()
    elif action == 'verify':
        verify()
        print('R1 sources, preceding gates and protected archives verified.')
    else:
        sys.exit(execute() if action == 'execute' else replay())
