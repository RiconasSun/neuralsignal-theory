"""Descriptive audit of saved development results; never loads neural data."""
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PAPER = Path(__file__).resolve().parents[1]
OUTPUT = PAPER / 'results/M3_M4_scope_audit'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def table(path, rows):
    if not rows:
        raise ValueError('Empty required table')
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['subject'], row['candidate'])].append(row)
    return [{'subject': subject, 'candidate': candidate,
             'family': group[0]['family'], 'alpha': group[0]['alpha'],
             'sessions': len(group), 'validation_mean_nats_unit_bin':
             float(np.mean([row['validation_mean_nats_unit_bin'] for row in group])),
             'mean_parameters_per_session': float(np.mean([row['parameters'] for row in group])),
             'total_fit_wall_seconds': sum(row['wall_seconds'] for row in group),
             'weighting': 'equal session weight within subject; descriptive development scores'}
            for (subject, candidate), group in sorted(groups.items())]


def certified_scores(session):
    rows = []
    for row in session['candidates']:
        scores = np.asarray(row['validation_trial_scores'])
        if not row['converged'] or not np.isfinite(scores).all():
            raise ValueError('Invalid certified candidate')
        rows.append({'session': session['session'], 'candidate': row['candidate'],
                     'family': row['family'], 'free_parameters': row['free_parameters'],
                     'validation_mean_nats_unit_bin': float(scores.mean()),
                     'trial_se_descriptive': float(scores.std(ddof=1) / np.sqrt(len(scores))),
                     'fit_wall_seconds_chosen_seed': row['wall_seconds'],
                     'score_status': 'certified exact HMM; partial smoke, not fair full competition'})
    return rows


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    inputs = {}
    def read(relative):
        path = PAPER / relative
        inputs[relative] = digest(path)
        return load(path)
    gates = {f'M{i}': read(f'results/M{i}/gate_result.json') for i in range(5)}
    if any(gates[f'M{i}']['gate'] != 'PASS' for i in range(4)):
        raise ValueError('M0-M3 PASS required')
    for relative in ('data_manifest/M3/selection_contract_lock.json',
                     'data_manifest/M4/model_contract_lock.v3.json'):
        lock = read(relative)
        for name, expected in lock['sha256'].items():
            path = PAPER / name.replace('\\', '/')
            if digest(path) != expected:
                raise ValueError(f'Frozen scientific contract changed: {name}')
    for milestone in ('M2', 'M3', 'M4'):
        for name, expected in gates[milestone]['source_sha256'].items():
            path = PAPER / name.replace('\\', '/')
            if milestone == 'M4' and name == 'tests/test_m4.py':
                continue
            if digest(path) != expected:
                raise ValueError(f'Changed scientific source: {name}')
    # Locate the canonical split from the frozen M1 runner, not a new partition.
    import run_m1
    split = run_m1.SPLIT
    if digest(split) != gates['M3']['split_sha256'] or digest(split) != gates['M4']['split_sha256']:
        raise ValueError('Frozen split changed')
    inputs[str(split.relative_to(PAPER)).replace('\\', '/')] = digest(split)
    rows = []
    for path in sorted((PAPER / 'results/M3/sessions').glob('*.json')):
        session = read(path.relative_to(PAPER).as_posix())
        for row in session['candidates']:
            scores = np.asarray(row['validation_trial_scores'])
            if not row['convergence']['success'] or not np.isfinite(scores).all():
                raise ValueError('Baseline failure: retained gate must not be overwritten')
            rows.append({'subject': session['subject'], 'session': session['session_key'],
                         'candidate': row['candidate'], 'family': row['family'], 'alpha': row['alpha'],
                         'parameters': row['parameters'], 'validation_trials': len(scores),
                         'validation_mean_nats_unit_bin': float(scores.mean()),
                         'trial_se_descriptive': float(scores.std(ddof=1) / np.sqrt(len(scores))),
                         'converged': row['convergence']['success'],
                         'iterations': row['convergence']['iterations'], 'wall_seconds': row['wall_seconds']})
    if len(rows) != 483 or len({row['subject'] for row in rows}) != 9:
        raise ValueError('Frozen cohort/candidate scope mismatch')
    table(OUTPUT / 'baseline_session_candidates.csv', rows)
    subjects = summarize(rows)
    table(OUTPUT / 'baseline_subject_candidates.csv', subjects)
    session = read('results/M4/sessions/sub-01_ses-01.json')
    scores = certified_scores(session)
    baseline = read('results/M3/sessions/sub-01_ses-01.json')
    constant = next(row for row in baseline['candidates'] if row['family'] == 'stationary')
    for row, candidate in zip(scores, session['candidates']):
        if candidate['validation_trial_ids'] != constant['validation_trial_ids']:
            raise ValueError('Unmatched validation trial IDs')
        row['delta_vs_constant_nats_unit_bin'] = row['validation_mean_nats_unit_bin'] - constant['validation_mean']
    table(OUTPUT / 'model_validation_certified_partial.csv', scores)
    training = [{key: row[key] for key in ('session', 'candidate', 'family', 'states', 'dimension', 'seed',
                                         'converged', 'iterations', 'wall_seconds', 'training_objective', 'free_parameters')}
                for row in session['seeds']]
    table(OUTPUT / 'model_training_current_run.csv', training)
    accuracy = read('results/M4/accuracy/sub-01_ses-01/continuous_k1_d1_seed71.json')
    table(OUTPUT / 'integration_accuracy.csv', accuracy['comparisons'])
    completeness = [
        {'family': 'discrete', 'completed_current_smoke_seeds': sum(row['family'] == 'discrete' for row in training),
         'certified_validation_configurations': len(scores), 'status': 'PARTIAL_SMOKE_ONLY'},
        {'family': 'continuous', 'completed_current_smoke_seeds': sum(row['family'] == 'continuous' for row in training),
         'certified_validation_configurations': 0, 'status': 'ACCURACY_FAIL_NOT_SCIENTIFICALLY_COMPARABLE'},
        {'family': 'hybrid', 'completed_current_smoke_seeds': sum(row['family'] == 'hybrid' for row in training),
         'certified_validation_configurations': 0, 'status': 'NOT_EXECUTED_AFTER_CRITICAL_GATE_FAIL'}]
    table(OUTPUT / 'model_completeness.csv', completeness)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout='constrained')
    for family, color in [('history', '#24766a'), ('task', '#b94163'), ('timing', '#3b74a0'), ('drift', '#92712c'), ('combined', '#766795')]:
        subset = [row for row in subjects if row['family'] == family and row['alpha'] == 1.0]
        constant = {row['subject']: row['validation_mean_nats_unit_bin'] for row in subjects if row['family'] == 'stationary'}
        axes[0].scatter([family] * len(subset), [row['validation_mean_nats_unit_bin'] - constant[row['subject']] for row in subset],
                        color=color, alpha=.8)
    axes[0].axhline(0, color='#596471', linewidth=1)
    axes[0].set(title='Baseline descriptive development scores', ylabel='Delta vs constant (nats/unit-bin)')
    axes[0].tick_params(axis='x', rotation=30)
    budgets = [row['particles'] for row in accuracy['comparisons']]
    values = [row['conservative_discrepancy'] for row in accuracy['comparisons']]
    axes[1].plot([str(value) for value in budgets], values, 'o-', color='#b94163')
    axes[1].axhline(.001, color='#24766a', linestyle='--', label='Frozen threshold 0.001')
    axes[1].set(yscale='log', title='PLDS smoke: integration accuracy FAIL', xlabel='Particles', ylabel='Diagnostic discrepancy (nats/unit-bin)')
    axes[1].legend(fontsize=9)
    fig.suptitle('Nine subjects; ridge=1 shown without tuning. No valid three-family competition.', fontsize=11)
    fig.savefig(OUTPUT / 'development_diagnostics.png', dpi=160)
    fig.savefig(OUTPUT / 'development_diagnostics.pdf')
    plt.close(fig)
    spec = read('data_manifest/M3/baseline_spec.json')
    write_json(OUTPUT / 'scope_audit.json', {
        'B0': 'stationary exact constant-rate Poisson executed',
        'B1': 'history: rate intercept plus causal own-unit log1p spike history executed',
        'B2': 'task and timing separately executed; joint event-timing/task-only model NOT_EXECUTED',
        'B3': 'ridge history is own-unit five-lag Poisson autoregression, not cross-unit/raw-count AR; definition decision pending',
        'frozen_families': spec['families'], 'new_baseline_fit': False,
        'model_competition_complete': False, 'final_test_count_access': False, 'external_holdout_access': False})
    write_json(OUTPUT / 'qc_report.json', {'baseline_candidate_rows': len(rows), 'subjects': 9,
        'subject_candidate_rows': len(subjects), 'current_smoke_seed_rows': len(training),
        'certified_HMM_configuration_rows': len(scores), 'integration_gate': accuracy['gate'],
        'uncertainty': 'Trial SE descriptive only; no independent-neuron/window inference; validation selection bias remains',
        'coverage': 'Existing M2 PASS; no new raw acquisitions or holdout reads', 'input_sha256': inputs})
    test_report = OUTPUT / 'tests.txt'
    if not test_report.exists() or not test_report.read_text(encoding='utf-8-sig').rstrip().endswith('OK'):
        raise ValueError('Fresh report test suite PASS required; use reproduce-m3-m4-audit.ps1')
    write_json(OUTPUT / 'gate_result.json', {'report_generation': 'PASS', 'requested_M3_M4_execution_gate': 'FAIL',
        'scientific_verdict': 'INCONCLUSIVE', 'original_milestone_gates': {key: value['gate'] for key, value in gates.items()},
        'blockers': ['Requested joint B2 not in frozen baseline scope', 'M4 frozen integration accuracy not established'],
        'final_test_count_access': False, 'external_holdout_access': False,
        'tests_exit_code': 0, 'tests_sha256': digest(test_report),
        'finished_at_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': digest(Path(__file__)),
        'reproduction_sha256': digest(PAPER / 'scripts/reproduce-m3-m4-audit.ps1'),
        'test_source_sha256': digest(PAPER / 'tests/test_report_audit.py')})
    write_json(OUTPUT / 'claim_audit.json', {'supported': ['Descriptive baseline development scores and computational costs',
        'M4 partial HMM validation and documented continuous numerical failure'],
        'unsupported': ['B2 joint model completed', 'Complete fair D1/D2/D3 competition',
        'Subject-consistent regime preference', 'Final holdout advantage', 'NAP validation', 'CWP validation', 'Neural primitives validated']})
    print(json.dumps({'baseline_rows': len(rows), 'subject_rows': len(subjects), 'training_rows': len(training),
                      'certified_model_rows': len(scores), 'scientific_gate': 'FAIL', 'report_only': True}))


if __name__ == '__main__':
    main()
