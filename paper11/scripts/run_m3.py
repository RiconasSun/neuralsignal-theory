"""M3 train-fit/validation-select causal baselines; final test stays opaque."""
import json
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
import scipy

import run_m2 as m2
import baseline_models as models

PAPER, RESULTS = m2.PAPER, m2.PAPER / 'results/M3'
SPEC = PAPER / 'data_manifest/M3/baseline_spec.json'


def prerequisite():
    m2.prerequisite()
    gate = m2.m1.m0.load(m2.RESULTS / 'gate_result.json')
    if gate['gate'] != 'PASS' or gate['tests_exit_code'] != 0:
        raise ValueError('Scientific M2 PASS required before M3')
    for name, digest in gate['source_sha256'].items():
        m2.require_hash(PAPER / name, digest)
    for row in m2.m1.m0.load(m2.MANIFEST / 'features.json')['files']:
        m2.require_hash(PAPER / row['feature_path'], row['sha256'])
    audit = m2.m1.m0.load(m2.RESULTS / 'coverage_audit.json')
    if audit['gate'] != 'PASS' or audit['sessions_verified'] != 23:
        raise ValueError('Coverage audit incomplete')


def freeze_spec():
    lock = PAPER / 'data_manifest/M3/selection_contract_lock.json'
    files = ['data_manifest/M3/baseline_spec.json', 'scripts/baseline_models.py', 'scripts/run_m3.py']
    hashes = {name: m2.m1.digest(PAPER / name) for name in files}
    if lock.exists():
        previous = m2.m1.m0.load(lock)
        if previous['sha256'] != hashes:
            raise ValueError('M3 selection contract changed after validation access; version and disclose any repair')
        return previous
    result = {'frozen_at_utc': m2.m1.now(), 'before_validation_count_access': True, 'sha256': hashes,
              'final_test_timestamp_values_decoded': False}
    m2.m1.write_json(lock, result)
    return result


def arrays_for_session(key):
    subject, session = key.split('/')
    data = m2.m1.m0.load(m2.FEATURES / f'{subject}_{session}_train.json')
    split = m2.m1.m0.load(m2.m1.SPLIT)['sessions'][key]
    stem = m2.m1.DATA / 'nm000363' / subject / session / 'ieeg' / f'{subject}_{session}_task-verbalWM_'
    metadata = m2.m1.rows(Path(str(stem) + 'trials.tsv'))
    set_sizes = {int(row['trial']): int(row['set_size']) for row in metadata}
    validation_ids = split['partitions']['validation']
    validation = m2.extract(Path(str(stem) + 'spikes.tsv'), validation_ids, data['unit_ids'])
    return data, np.asarray(validation), validation_ids, set_sizes, len(metadata)


def fit_session(key, spec):
    data, validation, validation_ids, sizes, total = arrays_for_session(key)
    training = np.asarray(data['counts'])
    candidates, fits = [], {}
    for family in models.FAMILIES:
        train_x, names = models.design(training, data['trial_ids'], [sizes[t] for t in data['trial_ids']], total, family)
        val_x, val_names = models.design(validation, validation_ids, [sizes[t] for t in validation_ids], total, family)
        if names != val_names:
            raise ValueError('Design columns differ between partitions')
        for alpha in ([0.0] if family == 'stationary' else spec['ridge_grid']):
            start = time.perf_counter()
            fit = models.fit_poisson(train_x, training, alpha)
            candidate = f'{family}_ridge{alpha:g}'
            row = {'candidate': candidate, 'family': family, 'alpha': alpha, 'parameters': fit['parameters'],
                   'convergence': fit['convergence'], 'wall_seconds': time.perf_counter() - start,
                   'train_trial_ids': data['trial_ids'], 'validation_trial_ids': validation_ids}
            fits[candidate] = {**{name: value.tolist() for name, value in fit.items() if isinstance(value, np.ndarray)},
                               **{name: value for name, value in fit.items() if not isinstance(value, np.ndarray)}, 'columns': names}
            if not fit['convergence']['success']:
                row['validation_mean'] = None
                candidates.append(row)
                m2.m1.write_json(RESULTS / 'sessions' / (key.replace('/', '_') + '.json'), {'session_key': key, 'candidates': candidates, 'fits': fits, 'failure': 'REQUIRED_BASELINE_NONCONVERGED'})
                raise ValueError(f'Required baseline did not converge: {key}/{candidate}')
            scores = models.score(fit, val_x, validation)
            row.update(validation_trial_scores=scores.tolist(), validation_mean=float(scores.mean()),
                       validation_se=float(scores.std(ddof=1) / np.sqrt(len(scores))))
            candidates.append(row)
    selected = models.choose(candidates)
    output = {'session_key': key, 'subject': key.split('/')[0], 'train_shape': list(training.shape), 'validation_shape': list(validation.shape),
              'candidates': candidates, 'fits': fits, 'selected': selected, 'test_timestamp_values_decoded': False}
    m2.m1.write_json(RESULTS / 'sessions' / (key.replace('/', '_') + '.json'), output)
    print(json.dumps({'session': key, 'selected': selected['candidate'], 'validation_nats_per_unit_bin': selected['validation_mean']}), flush=True)
    return output


def pipeline():
    prerequisite()
    lock = freeze_spec()
    spec = m2.m1.m0.load(SPEC)
    sessions = sorted(m2.selection())
    completed, stages = {}, []
    for stage, keys in [('smoke', sessions[:1]), ('small_cohort', [k for k in sessions if k.startswith(('sub-01/', 'sub-02/'))]), ('full_cohort', sessions)]:
        for key in keys:
            if key not in completed:
                completed[key] = fit_session(key, spec)
        stages.append({'stage': stage, 'sessions': len(keys), 'required_candidates_per_session': 21})
        m2.m1.write_json(RESULTS / 'progress.json', {'stages': stages, 'sessions_completed': sorted(completed)})
    summaries = [{'session_key': key, 'subject': key.split('/')[0], 'selected': output['selected']['candidate'],
                  'validation_mean': output['selected']['validation_mean'], 'candidate_count': len(output['candidates'])} for key, output in completed.items()]
    qc = {'eligible_subjects': 9, 'sessions': len(completed), 'candidates': sum(row['candidate_count'] for row in summaries),
          'families': list(models.FAMILIES), 'selection': summaries, 'stages': stages,
          'selection_contract_sha256': m2.m1.digest(PAPER / 'data_manifest/M3/selection_contract_lock.json'),
          'final_test_count_access': False, 'statistics': 'NOT_EXECUTED', 'software': {'numpy': np.__version__, 'scipy': scipy.__version__}}
    m2.m1.write_json(RESULTS / 'qc_report.json', qc)
    return qc


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    started, errors, qc = m2.m1.now(), [], {}
    try:
        qc = pipeline()
    except (ValueError, OSError, KeyError) as error:
        errors.append(str(error))
        files = sorted((RESULTS / 'sessions').glob('*.json'))
        qc = {'status': 'FAILED_REQUIRED_GATE', 'session_artifacts': len(files),
              'planned_sessions': 23, 'planned_candidates': 483, 'errors': errors,
              'final_test_count_access': False, 'partial_artifacts_retained': True}
        m2.m1.write_json(RESULTS / 'qc_report.json', qc)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(PAPER / 'tests'), '-p', 'test_m3.py', '-v'], capture_output=True, text=True)
    (RESULTS / 'tests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    if tests.returncode:
        errors.append('M3 automated tests failed')
    gate = {'milestone': 'M3', 'gate': 'FAIL' if errors else 'PASS', 'errors': errors, 'tests_exit_code': tests.returncode,
            'preceding_gates': {'M0': 'PASS', 'M1': 'PASS', 'M2': m2.m1.m0.load(m2.RESULTS / 'gate_result.json')['gate']},
            'started_at_utc': started, 'finished_at_utc': m2.m1.now(), 'final_test_count_access': False, 'scientific_verdict': 'NOT_EVALUATED',
            'candidate_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=m2.m1.ROOT).decode().strip(),
            'source_sha256': {name: m2.m1.digest(PAPER / name) for name in ('scripts/baseline_models.py', 'scripts/run_m3.py', 'tests/test_m3.py', 'scripts/reproduce-m3.ps1', 'REPRODUCE_M3.md')},
            'split_sha256': m2.m1.digest(m2.m1.SPLIT)}
    m2.m1.write_json(RESULTS / 'gate_result.json', gate)
    m2.m1.write_json(RESULTS / 'claim_audit.json', {'scientific_verdict': 'NOT_EVALUATED', 'errors': errors,
                  'supported': ['Real train-fitted validation-selected baselines'] if not errors else [],
                  'unsupported': ['Model-family preference', 'Final holdout advantage', 'NAP validated', 'CWP validated']})
    print(json.dumps({'gate': gate['gate'], 'errors': errors, 'qc': qc}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
