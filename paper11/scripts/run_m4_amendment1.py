"""Authorized numerical amendment; original scientific code/results unchanged."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
from scipy.special import gammaln, logsumexp
import run_m4 as original

PAPER = original.PAPER
RESULTS = PAPER / 'results/M4_amendment1'
SPEC = PAPER / 'data_manifest/M4/numerical_amendment1.json'
LOCK = PAPER / 'data_manifest/M4/numerical_amendment1_lock.json'
load, write, digest, now = original.m3.m2.m1.m0.load, original.m3.m2.m1.write_json, original.m3.m2.m1.digest, original.m3.m2.m1.now


def identity():
    paths = [SPEC, Path(__file__), PAPER / 'tests/test_m4_amendment1.py',
             PAPER / 'scripts/reproduce-m4-amendment1.ps1', PAPER / 'REPRODUCE_M4_AMENDMENT1.md']
    paths += list((PAPER / 'results/M4').rglob('*'))
    paths += [PAPER / 'data_manifest/M4/model_contract_lock.v3.json']
    return {path.relative_to(PAPER).as_posix(): digest(path) for path in sorted(paths) if path.is_file()}


def register():
    original.prerequisite()
    original.contract()
    current = identity()
    if LOCK.exists():
        if load(LOCK)['sha256'] != current:
            raise ValueError('Amendment/original evidence changed; no silent repair')
    else:
        write(LOCK, {'id': 'M4-NUM-1', 'registered_at_utc': now(), 'before_revised_evaluation': True,
                     'development_exposure_disclosed': True, 'sha256': current,
                     'split_sha256': digest(original.m3.m2.m1.SPLIT), 'final_holdout_access': False})
    return load(LOCK)


def particle(model, y, offset, count, seed):
    rng = np.random.default_rng(seed)
    states = rng.choice(model['states'], count, p=model['initial'])
    latent = rng.normal(size=(count, model['dimension']))
    scores, ess, largest = [], [], []
    overflow, boundary = 0, 0
    for t in range(len(y)):
        eta = offset[t] + model['biases'][states] + latent @ model['loadings'].T
        if not np.isfinite(eta).all():
            raise original.ScientificGateFailure('Nonfinite particle log rate')
        with np.errstate(over='ignore', under='ignore'):
            rate = np.exp(eta)
        overflow += int(np.isinf(rate).sum())
        likes = np.sum(y[t] * eta - rate - gammaln(y[t] + 1), axis=1)
        normalizer = logsumexp(likes)
        if not np.isfinite(normalizer):
            raise original.ScientificGateFailure('Degenerate particle normalizer')
        scores.append(normalizer - np.log(count))
        weights = np.exp(likes - normalizer)
        ess.append(float(1 / np.sum(weights ** 2)))
        largest.append(float(weights.max()))
        positions = (rng.random() + np.arange(count)) / count
        ancestors = np.searchsorted(np.cumsum(weights), positions, side='right')
        boundary += int((ancestors == count).sum())
        ancestors = np.minimum(ancestors, count - 1)
        states, latent = states[ancestors], latent[ancestors]
        cumulative = np.cumsum(model['transition'][states], axis=1)
        states = (rng.random(count)[:, None] > cumulative).sum(axis=1)
        states = np.minimum(states, model['states'] - 1)
        latent = np.einsum('ndf,nf->nd', model['dynamics'][states], latent) + rng.normal(size=latent.shape)
    return np.asarray(scores), {'minimum_ess_fraction': min(ess) / count,
                               'mean_ess_fraction': float(np.mean(ess)) / count,
                               'maximum_particle_weight': max(largest), 'overflow_rates': overflow,
                               'roundoff_resampling_boundary_count': boundary}


def repetitions(model, validation, offsets, budget, seeds, stride):
    start = time.perf_counter()
    scores, diagnostics = [], []
    for seed in seeds:
        row = []
        for trial, (y, offset) in enumerate(zip(validation, offsets)):
            values, diagnostic = particle(model, y, offset, budget, seed + trial * stride)
            row.append(float(values.sum() / y.size))
            diagnostics.append({'seed': seed, 'trial_index': trial, **diagnostic})
        scores.append(row)
    return np.asarray(scores), diagnostics, time.perf_counter() - start


def accuracy(model, validation, offsets):
    if model['family'] == 'discrete':
        return original_accuracy(model, validation, offsets)
    spec = load(SPEC)
    references, reference_logs = {}, []
    for budget in spec['reference_particles']:
        values, diagnostics, seconds = repetitions(model, validation, offsets, budget, spec['reference_seeds'], spec['trial_seed_stride'])
        references[budget] = values
        reference_logs.append({'particles': budget, 'wall_seconds': seconds, 'trial_scores': values.tolist(), 'diagnostics': diagnostics})
    low, high = [references[budget] for budget in spec['reference_particles']]
    center = high.mean(axis=0)
    uncertainty = float(np.max(np.abs(center - low.mean(axis=0)) + 1.96 * high.std(axis=0, ddof=1) / np.sqrt(len(high))))
    comparisons, accepted = [], []
    for budget in spec['candidate_particles']:
        values, diagnostics, seconds = repetitions(model, validation, offsets, budget, spec['candidate_seeds'], spec['trial_seed_stride'])
        bound = original.single_run_discrepancy(values, center, uncertainty)
        record = {'particles': budget, 'conservative_discrepancy': bound, 'wall_seconds': seconds,
                  'mean_minus_reference_by_trial': (values.mean(axis=0) - center).tolist(),
                  'single_run_sd_by_trial': values.std(axis=0, ddof=1).tolist(),
                  'trial_scores': values.tolist(), 'diagnostics': diagnostics}
        comparisons.append(record)
        if bound <= spec['threshold_nats_unit_bin'] and uncertainty <= spec['threshold_nats_unit_bin']:
            accepted.append(record)
    result = {'gate': 'PASS' if accepted else 'FAIL', 'reference_uncertainty': uncertainty,
              'comparisons': comparisons, 'reference_runs': reference_logs,
              'reference_trial_scores': center.tolist(), 'amendment': 'M4-NUM-1',
              'estimator': 'single first prespecified seed, not ensemble mean or best replica',
              'limitation': 'Empirical budget/repetition agreement cannot prove absolute error or remove Jensen bias'}
    if accepted:
        chosen = accepted[0]
        result.update(particles=chosen['particles'], trial_scores=chosen['trial_scores'][0],
                      error_bound_estimate=chosen['conservative_discrepancy'])
    else:
        result.update(scientific_verdict='INCONCLUSIVE', reason='Amended numerical accuracy not established')
    return result


original_accuracy = original.accuracy
original_fit_session = original.fit_session
original_hmm, original_latent = original.regimes.fit_hmm, original.regimes.fit_latent
current_session = None
receipts = []


def fit_model(family, y, offsets, states, dimension, seed):
    candidate = f'{family}_k{states}_d{dimension}_seed{seed}'
    saved = load(PAPER / 'results/M4/sessions/sub-01_ses-01.json')
    matches = [row for row in saved['seeds'] if row['candidate'] == candidate] if current_session == 'sub-01/ses-01' else []
    if matches:
        row = matches[0]
        path = PAPER / row['model_path'].replace('\\', '/')
        if not row['converged'] or digest(path) != row['model_sha256']:
            raise ValueError('Training cache identity/convergence mismatch')
        receipts.append({'session': current_session, 'candidate': candidate, 'model_sha256': digest(path),
                         'original_training_wall_seconds': row['wall_seconds'], 'reused_training_only': True})
        write(RESULTS / 'cache_receipts.json', receipts)
        return original.restore(load(path))
    return original_hmm(y, offsets, states, seed) if family == 'discrete' else original_latent(y, offsets, states, dimension, seed)


def fit_session(key):
    global current_session
    current_session = key
    return original_fit_session(key)


def pipeline():
    register()
    original.RESULTS = RESULTS
    original.accuracy = accuracy
    original.regimes.fit_hmm = lambda y, offset, states, seed: fit_model('discrete', y, offset, states, 0, seed)
    original.regimes.fit_latent = lambda y, offset, states, dimension, seed: fit_model('continuous' if states == 1 else 'hybrid', y, offset, states, dimension, seed)
    sessions = sorted(original.m3.m2.selection())
    completed, stages = {}, []
    for stage, keys in [('smoke', sessions[:1]), ('small_cohort', [key for key in sessions if key.startswith(('sub-01/', 'sub-02/'))]), ('full_cohort', sessions)]:
        for key in keys:
            if key not in completed:
                completed[key] = fit_session(key)
        stages.append({'stage': stage, 'sessions': len(keys)})
        write(RESULTS / 'progress.json', {'stages': stages, 'completed_sessions': sorted(completed)})
    write(RESULTS / 'selected_models.json', {'sessions': {key: value['selected'] for key, value in completed.items()},
                                           'frozen_at_utc': now(), 'final_holdout_access': False})
    return {'stages': stages, 'validation_sessions': len(completed)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--register', action='store_true')
    args = parser.parse_args()
    if args.register:
        print(json.dumps({'registered': register()['registered_at_utc']}))
        return 0
    RESULTS.mkdir(parents=True, exist_ok=True)
    started, errors, qc = now(), [], {}
    try:
        qc = pipeline()
    except (original.ScientificGateFailure, ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
        errors.append(str(error))
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(PAPER / 'tests'), '-p', 'test_m4_amendment1.py', '-v'], capture_output=True, text=True)
    (RESULTS / 'tests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    if tests.returncode:
        errors.append('Amendment tests failed')
    qc.update(errors=errors, reused_training_seed_count=len(receipts), final_holdout_access=False)
    write(RESULTS / 'qc_report.json', qc)
    write(RESULTS / 'gate_result.json', {'milestone': 'M4', 'amendment': 'M4-NUM-1', 'gate': 'FAIL' if errors else 'PASS',
          'scientific_verdict': 'INCONCLUSIVE' if errors else 'NOT_EVALUATED', 'errors': errors,
          'tests_exit_code': tests.returncode, 'started_at_utc': started, 'finished_at_utc': now(),
          'lock_sha256': digest(LOCK), 'source_sha256': digest(Path(__file__)), 'final_holdout_access': False})
    write(RESULTS / 'claim_audit.json', {'supported': ['Amended development numerical diagnostics only'],
          'unsupported': ['Preferred neural regime', 'Null tests passed', 'Holdout advantage', 'NAP/CWP/primitives validated'], 'errors': errors})
    print(json.dumps({'gate': 'FAIL' if errors else 'PASS', 'errors': errors, 'qc': qc}))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
