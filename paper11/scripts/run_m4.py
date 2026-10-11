"""M4 train/validation model gates; fail closed before final holdout evaluation."""
import json
import subprocess
import sys
import time
from pathlib import Path
import numpy as np

import run_m3 as m3
import poisson_regimes as regimes

PAPER, RESULTS = m3.PAPER, m3.PAPER / 'results/M4'
SPEC = PAPER / 'data_manifest/M4/model_spec.json'


class ScientificGateFailure(RuntimeError):
    pass


def serial(model):
    return {name: value.tolist() if isinstance(value, np.ndarray) else value.item() if isinstance(value, np.generic) else value for name, value in model.items()}


def restore(model):
    fields = ('initial', 'transition', 'biases', 'dynamics', 'loadings')
    return {name: np.asarray(value) if name in fields else value for name, value in model.items()}


def prerequisite():
    m3.prerequisite()
    gate = m3.m2.m1.m0.load(m3.RESULTS / 'gate_result.json')
    if gate['gate'] != 'PASS' or gate['tests_exit_code'] != 0:
        raise ValueError('M3 PASS required before M4')
    for name, digest in gate['source_sha256'].items():
        m3.m2.require_hash(PAPER / name, digest)
    return gate


def contract():
    lock = PAPER / 'data_manifest/M4/model_contract_lock.v3.json'
    sources = [SPEC, PAPER / 'scripts/poisson_regimes.py', PAPER / 'scripts/run_m4.py']
    inputs = [m3.RESULTS / 'gate_result.json', m3.RESULTS / 'qc_report.json', PAPER / 'data_manifest/M3/selection_contract_lock.json']
    inputs += sorted((m3.RESULTS / 'sessions').glob('*.json'))
    identity = {str(path.relative_to(PAPER)): m3.m2.m1.digest(path) for path in sources + inputs}
    if lock.exists():
        result = m3.m2.m1.m0.load(lock)
        if result['sha256'] != identity:
            raise ValueError('M4 frozen fitting/selection contract changed; no silent post-access repair')
        return result
    result = {'frozen_at_utc': m3.m2.m1.now(), 'before_model_fitting': True, 'sha256': identity,
              'final_test_count_access': False}
    m3.m2.m1.write_json(lock, result)
    return result


def observations(key):
    data, validation, validation_ids, sizes, total = m3.arrays_for_session(key)
    training = np.asarray(data['counts'])
    baseline = m3.m2.m1.m0.load(m3.RESULTS / 'sessions' / (key.replace('/', '_') + '.json'))
    chosen = m3.models.choose([row for row in baseline['candidates'] if row['family'] == 'combined'])
    fit = baseline['fits'][chosen['candidate']]
    fit = {name: np.asarray(value) if name in ('coefficients', 'train_mean', 'train_scale') else value for name, value in fit.items()}
    offsets = []
    for counts, ids in [(training, data['trial_ids']), (validation, validation_ids)]:
        x, names = m3.models.design(counts, ids, [sizes[t] for t in ids], total, 'combined')
        standardized = (x - fit['train_mean']) / fit['train_scale']
        offsets.append(np.einsum('tbup,up->tbu', standardized, fit['coefficients']) + np.log(0.1))
    return training, validation, offsets, fit, data, validation_ids


def grid():
    protocol = m3.m2.m1.m0.load(PAPER / 'protocol/protocol.json')
    return ([('discrete', k, 0) for k in protocol['models']['discrete']['states']]
            + [('continuous', 1, d) for d in protocol['models']['continuous']['latent_dimensions']]
            + [('hybrid', k, d) for k in protocol['models']['hybrid']['states'] for d in protocol['models']['hybrid']['latent_dimensions']])


def predictive_trials(model, counts, offsets, particles, seed):
    scores = []
    for index, (trial, offset) in enumerate(zip(counts, offsets)):
        values = (regimes.exact_predictive(model, trial, offset) if model['family'] == 'discrete'
                  else regimes.particle_predictive(model, trial, offset, particles, seed + index * 1009))
        scores.append(values.sum() / trial.size)
    return np.array(scores)


def accuracy(model, validation, offset):
    if model['family'] == 'discrete':
        scores = predictive_trials(model, validation, offset, 0, 0)
        return {'gate': 'PASS', 'particles': 0, 'method': 'exact marginal HMM', 'trial_scores': scores.tolist(), 'error_bound_estimate': 0.0}
    reference = {}
    for budget in (16384, 32768):
        reference[budget] = np.array([predictive_trials(model, validation, offset, budget, 2001 + repetition * 100003) for repetition in range(4)])
    high, low = reference[32768].mean(axis=0), reference[16384].mean(axis=0)
    reference_uncertainty = float(np.max(np.abs(high - low) + 1.96 * reference[32768].std(axis=0, ddof=1) / 2))
    comparisons = []
    for budget in (64, 256, 1024):
        estimates = np.array([predictive_trials(model, validation, offset, budget, 1001 + repetition * 100003) for repetition in range(4)])
        bound = single_run_discrepancy(estimates, high, reference_uncertainty)
        comparisons.append({'particles': budget, 'conservative_discrepancy': bound})
        if reference_uncertainty <= 0.001 and bound <= 0.001:
            return {'gate': 'PASS', 'particles': budget, 'method': 'joint bootstrap filter, repeated independent/reference comparison',
                    'trial_scores': estimates[0].tolist(), 'reference_uncertainty': reference_uncertainty,
                    'error_bound_estimate': bound, 'comparisons': comparisons,
                    'estimator': 'single frozen run, seed1001; diagnostic uses worst independent replicate, not mean-SE',
                    'candidate_replicate_trial_scores': estimates.tolist(), 'reference_trial_scores': high.tolist(),
                    'limitation': 'empirical accuracy diagnostic, not a mathematical absolute-error guarantee'}
    return {'gate': 'FAIL', 'reference_uncertainty': reference_uncertainty, 'comparisons': comparisons,
            'candidate_replicate_trial_scores': estimates.tolist(), 'reference_trial_scores': high.tolist(),
            'scientific_verdict': 'INCONCLUSIVE', 'reason': 'prespecified integration accuracy not established'}


def single_run_discrepancy(estimates, reference, reference_uncertainty):
    discrepancy = np.max(np.abs(estimates - reference), axis=0)
    uncertainty = 1.96 * estimates.std(axis=0, ddof=1)
    return float(np.max(discrepancy + uncertainty) + reference_uncertainty)


def parameters(model, common):
    units, dimension, states = model['biases'].shape[1], model['dimension'], model['states']
    extra = states * units + states * (states - 1) + states - 1
    if dimension:
        extra += units * dimension + states * dimension * dimension
    return common + extra


def fit_session(key):
    training, validation, offsets, common_fit, data, validation_ids = observations(key)
    protocol = m3.m2.m1.m0.load(PAPER / 'protocol/protocol.json')
    seeds = protocol['models']['shared']['initialization_seeds']
    candidates, seed_results = [], []
    old_session = RESULTS / 'attempts/accuracy-estimator-mismatch/session_training_snapshot.json'
    prior_rows = {row['candidate']: row for row in m3.m2.m1.m0.load(old_session)['seeds']} if old_session.exists() and key == 'sub-01/ses-01' else {}
    original_lock = PAPER / 'data_manifest/M4/model_contract_lock.v2.json'
    prior_contract = m3.m2.m1.m0.load(original_lock) if original_lock.exists() else {'sha256': {}}
    cache_training_valid = (prior_contract['sha256'].get('scripts/poisson_regimes.py') == m3.m2.m1.digest(PAPER / 'scripts/poisson_regimes.py')
                            and all(m3.m2.m1.digest(PAPER / name) == digest for name, digest in prior_contract['sha256'].items()
                                    if name.startswith('results/M3/') or name.startswith('data_manifest/M3/')))
    for family, states, dimension in grid():
        fitted = []
        for seed in seeds:
            start = time.perf_counter()
            name = f'{family}_k{states}_d{dimension}_seed{seed}'
            model_path = RESULTS / 'models' / key.replace('/', '_') / (name + '.json')
            cached = prior_rows.get(name)
            if cache_training_valid and cached and model_path.exists() and m3.m2.m1.digest(model_path) == cached['model_sha256']:
                model = restore(m3.m2.m1.m0.load(model_path))
            else:
                model = (regimes.fit_hmm(training, offsets[0], states, seed) if family == 'discrete'
                         else regimes.fit_latent(training, offsets[0], states, dimension, seed))
            m3.m2.m1.write_json(model_path, serial(model))
            row = {'session': key, 'candidate': name, 'family': family, 'states': states, 'dimension': dimension, 'seed': seed,
                   'converged': bool(model['converged']), 'iterations': model['iterations'], 'wall_seconds': time.perf_counter() - start,
                   'training_objective': model['training_objectives'][-1], 'model_path': str(model_path.relative_to(PAPER)),
                   'model_sha256': m3.m2.m1.digest(model_path), 'free_parameters': parameters(model, common_fit['parameters'])}
            seed_results.append(row)
            m3.m2.m1.write_json(RESULTS / 'sessions' / (key.replace('/', '_') + '.json'), {'session': key, 'seeds': seed_results, 'candidates': candidates, 'final_test_count_access': False})
            print(json.dumps({k: row[k] for k in ('candidate', 'converged', 'iterations', 'wall_seconds')}), flush=True)
            if not row['converged']:
                raise ScientificGateFailure(f'Required candidate/seed nonconverged: {key}/{name}')
            fitted.append((row, model))
        chosen, model = max(fitted, key=lambda pair: pair[0]['training_objective'])
        diagnostic = accuracy(model, validation, offsets[1])
        m3.m2.m1.write_json(RESULTS / 'accuracy' / key.replace('/', '_') / (chosen['candidate'] + '.json'), diagnostic)
        if diagnostic['gate'] != 'PASS':
            raise ScientificGateFailure(f'Integration accuracy FAIL: {key}/{chosen["candidate"]}')
        scores = np.array(diagnostic['trial_scores'])
        candidates.append({**chosen, 'particles': diagnostic['particles'], 'validation_trial_ids': validation_ids,
                           'validation_mean': float(scores.mean()), 'validation_se': float(scores.std(ddof=1) / np.sqrt(len(scores))),
                           'validation_trial_scores': scores.tolist()})
    selected = {}
    for family in ('discrete', 'continuous', 'hybrid'):
        choices = [row for row in candidates if row['family'] == family]
        best = max(choices, key=lambda row: row['validation_mean'])
        within = [row for row in choices if row['validation_mean'] >= best['validation_mean'] - best['validation_se']]
        selected[family] = min(within, key=lambda row: (row['free_parameters'], row['dimension'], row['states']))
    output = {'session': key, 'seeds': seed_results, 'candidates': candidates, 'selected': selected,
              'final_test_count_access': False, 'matched_complexity_validation': candidates}
    m3.m2.m1.write_json(RESULTS / 'sessions' / (key.replace('/', '_') + '.json'), output)
    return output


def pipeline():
    prerequisite()
    contract()
    sessions = sorted(m3.m2.selection())
    completed = {}
    stages = []
    for stage, keys in [('smoke', sessions[:1]), ('small_cohort', [k for k in sessions if k.startswith(('sub-01/', 'sub-02/'))]), ('full_cohort', sessions)]:
        for key in keys:
            if key not in completed:
                completed[key] = fit_session(key)
        stages.append({'stage': stage, 'sessions': len(keys)})
        m3.m2.m1.write_json(RESULTS / 'progress.json', {'stages': stages, 'completed': sorted(completed)})
    m3.m2.m1.write_json(PAPER / 'data_manifest/M4/selected_models.json', {'sessions': {key: result['selected'] for key, result in completed.items()},
                        'frozen_at_utc': m3.m2.m1.now(), 'before_final_test_count_access': True})
    return {'validation_selection_sessions': len(completed), 'subjects': 9, 'stages': stages,
            'final_test_count_access': False, 'next_step': 'locked final predictive evaluation required before any regime claim'}


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    started, errors, qc, scientific_failure = m3.m2.m1.now(), [], {}, False
    try:
        qc = pipeline()
    except ScientificGateFailure as error:
        errors.append(str(error))
        scientific_failure = True
    except (ValueError, OSError, KeyError, TypeError, np.linalg.LinAlgError) as error:
        errors.append(str(error))
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(PAPER / 'tests'), '-p', 'test_m4.py', '-v'], capture_output=True, text=True)
    (RESULTS / 'tests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    if tests.returncode:
        errors.append('M4 tests failed')
    qc.update(errors=errors, scientific_failure=scientific_failure, final_test_count_access=False,
              model_artifacts=len(list((RESULTS / 'models').rglob('*.json'))))
    m3.m2.m1.write_json(RESULTS / 'qc_report.json', qc)
    gate = {'milestone': 'M4', 'gate': 'FAIL' if errors else 'PASS', 'errors': errors, 'tests_exit_code': tests.returncode,
            'scientific_verdict': 'INCONCLUSIVE' if scientific_failure else 'NOT_EVALUATED',
            'started_at_utc': started, 'finished_at_utc': m3.m2.m1.now(), 'final_test_count_access': False,
            'preceding_gates': {'M0': 'PASS', 'M1': 'PASS', 'M2': 'PASS', 'M3': 'PASS'},
            'source_sha256': {name: m3.m2.m1.digest(PAPER / name) for name in ('scripts/poisson_regimes.py', 'scripts/run_m4.py', 'tests/test_m4.py', 'scripts/reproduce-m4.ps1', 'REPRODUCE_M4.md')},
            'split_sha256': m3.m2.m1.digest(m3.m2.m1.SPLIT)}
    m3.m2.m1.write_json(RESULTS / 'gate_result.json', gate)
    m3.m2.m1.write_json(RESULTS / 'claim_audit.json', {'scientific_verdict': gate['scientific_verdict'], 'errors': errors,
                        'supported': ['Protocol-bounded training/validation numerical assessment only'],
                        'unsupported': ['Preferred regime', 'Final holdout statistics', 'NAP validated', 'CWP validated', 'Null tests passed']})
    print(json.dumps({'gate': gate['gate'], 'errors': errors, 'qc': qc}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
