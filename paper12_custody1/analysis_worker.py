"""Restricted native-role M3 runner. Only exported development A/B are inputs."""
import json
from pathlib import Path
import sys
import hashlib


def main():
    security_only = '--security-only' in sys.argv
    deps, data, output, source, key, hostpid, sddl = [x for x in sys.argv[1:] if x != '--security-only']
    sys.path.insert(0, deps)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from native_analysis_check import check
    output = Path(output); output.mkdir(exist_ok=True)
    proof = check(source, key, hostpid, sddl)
    (output / 'role_proof.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
    if not proof['pass']:
        raise PermissionError('ACTUAL_ANALYSIS_ISOLATION_FAILED')
    if security_only:
        import unittest
        suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent), pattern='test_baseline*.py')
        result = unittest.TestResult(); suite.run(result)
        receipt = dict(synthetic_only=True, tests_run=result.testsRun, failures=len(result.failures),
                       errors=len(result.errors), pass_all=result.wasSuccessful(),
                       final_values_exposed_to_analysis=False, final_holdout_evaluated=False)
        (output / 'fixture_tests.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        if not receipt['pass_all'] or receipt['tests_run'] != 14:
            sys.exit(1)
        return
    import numpy as np
    from baseline_features import design, training_scaler, transform
    from baseline_fit import fit, stationary
    manifest = json.loads((Path(data) / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['group'] != 'development' or manifest['compartments'] != ['A', 'B']:
        raise PermissionError('INPUT_PARTITIONS_NOT_DEVELOPMENT_AB')
    normalization = manifest['ridge_normalization']
    if normalization not in ('total_unit_bins', 'per_unit_exposure'):
        raise PermissionError('RIDGE_NORMALIZATION_NOT_FROZEN')
    if len(manifest['sessions']) < 8 or len({x['mouse_id'] for x in manifest['sessions']}) != len(manifest['sessions']):
        raise RuntimeError('DEVELOPMENT_MOUSE_ADMISSION_FAILED')
    results = []
    for session in manifest['sessions']:
        path = Path(data) / session['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != session['sha256']:
            raise RuntimeError('EXPORTED_INPUT_HASH_MISMATCH')
        with np.load(path, allow_pickle=False) as saved:
            for compartment in ('A', 'B'):
                if saved['trial_ids_' + compartment].tolist() != session['trial_ids'][compartment]:
                    raise RuntimeError('INPUT_FROZEN_TRIAL_IDENTITY_MISMATCH')
            for region in ('CA1', 'DG'):
                if saved[region + '_unit_ids'].tolist() != session['unit_ids'][region]:
                    raise RuntimeError('INPUT_FROZEN_UNIT_IDENTITY_MISMATCH')
                y = saved[region + '_A']; validation = saved[region + '_B']
                if y.shape[-1] != validation.shape[-1] or not 5 <= y.shape[-1] <= 32:
                    raise RuntimeError('FROZEN_UNIT_ADMISSION_FAILED')
                for kind in ('stationary', 'history', 'population', 'event', 'drift', 'combined'):
                    raw = design(y, saved['conditions_A'], saved['orders_A'], kind)
                    scaler = training_scaler(raw); train_x = transform(raw, scaler); del raw
                    valid_x = transform(design(validation, saved['conditions_B'], saved['orders_B'], kind), scaler)
                    ridges = [None] if kind == 'stationary' else [.001, .01, .1, 1.]
                    for ridge in ridges:
                        for seed in (11, 23, 37):
                            entry = dict(mouse_id=session['mouse_id'], session_id=session['session_id'],
                                         region=region, family='baseline', kind=kind, ridge=ridge, seed=seed,
                                         data_sha256=session['sha256'])
                            try:
                                entry.update(stationary(y, validation, seed) if kind == 'stationary' else
                                             fit(y, train_x, validation, valid_x, ridge, seed, normalization))
                            except Exception as exc:
                                entry.update(converged=False, error_type=type(exc).__name__,
                                             error_code='BASELINE_FIT_OR_SCORE_FAILED')
                            results.append(entry)
                            name = '%s_%s_%s_%s_%s.json' % (session['session_id'], region, kind, ridge, seed)
                            (output / name).write_text(json.dumps(entry, indent=2, allow_nan=False), encoding='utf-8')
                    del train_x, valid_x
        print(json.dumps(dict(session_id=session['session_id'], completed_baseline_fits=126)), flush=True)
    expected = len(manifest['sessions']) * 2 * 21 * 3
    available = {}
    for region in ('CA1', 'DG'):
        available[region] = {}
        for kind in ('stationary', 'history', 'population', 'event', 'drift', 'combined'):
            ridges = [None] if kind == 'stationary' else [.001, .01, .1, 1.]
            eligible = []
            for ridge in ridges:
                subset = [r for r in results if r['region'] == region and r['kind'] == kind and r['ridge'] == ridge]
                if len(subset) == len(manifest['sessions']) * 3 and all(r['converged'] for r in subset):
                    eligible.append(ridge)
            available[region][kind] = eligible
    complete = len(results) == expected and all(available[region][kind] for region in available for kind in available[region])
    gate = dict(gate='PASS' if complete else 'FAIL', scientific_verdict='BASELINES_EXECUTED' if complete else 'INCONCLUSIVE',
                expected_fit_count=expected, completed_fit_count=len(results),
                converged_fit_count=sum(r['converged'] for r in results), eligible_ridges=available,
                mouse_count=len(manifest['sessions']), final_values_exposed_to_analysis=False,
                final_holdout_evaluated=False, preferred_regime_claim=False)
    (output / 'gate_result.json').write_text(json.dumps(gate, indent=2), encoding='utf-8')
    if not complete:
        sys.exit(2)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps(dict(aborted=True, error_type=type(exc).__name__, error_code='RESTRICTED_ANALYSIS_ABORT')), flush=True)
        sys.exit(1)
