"""Independent saved main endpoint/initialization/ledger arithmetic; no neural loading."""
import collections
import datetime
import hashlib
import json
import math
import socket
import sys
from pathlib import Path

import numpy as np

E = Path(__file__).resolve().parent
R = E.parents[3]
P = R / 'paper15_r1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def denied(*args, **kwargs):
    raise AssertionError('Review forbids neural arrays/network/model objective/derivatives/fits')


def run():
    assert (P / 'results/DYNAMIC_ATTEMPTS_COMPLETE.json').exists(), 'Wait for all attempts to terminate'
    np.load = denied
    socket.create_connection = denied
    socket.socket.connect = denied
    sys.path.insert(0, str(R))
    import paper15_r1.training as training
    import paper15_r1.independent_ad as derivative
    from paper15_r1.models import Model
    from paper15_r1.saved_audit import numerical_record
    from paper15_r1.production_admission import verify
    training.minimize = denied
    derivative.ad_function = denied
    derivative.coordinate_check = denied
    for method in ['__init__', 'initialize', 'objective', 'value', 'prebin_logmasses']:
        setattr(Model, method, denied)
    plan = read(P / 'A_FIT_PLAN.json')
    gate = read(P / 'PRODUCTION_GATE.json')
    readback = read(E / 'ACTUAL_PRODUCTION_GATE_READBACK.json')
    assert sha(P / 'PRODUCTION_GATE.json') == readback['gate_sha256']
    assert len(gate['hashes']) == readback['source_and_input_files_verified'] == 64
    for rel, value in gate['hashes'].items():
        assert rel.endswith(('.py', '.json')), 'No array payload reads in this review'
        assert sha(P / rel) == value, rel
    verify(gate, plan)
    assert len(plan['subjects']) == 10 and len(plan['configurations']) == 61 and plan['total_main'] == 610
    paths = list((P / 'fits').glob('*/*.json'))
    expected = {(s, c['id']) for s in plan['subjects'] for c in plan['configurations']}
    assert len(paths) == len(expected) == 610 and {(f.parent.name, f.stem) for f in paths} == expected
    markers = {b: read(P / 'results' / name) for b, name in [(True, 'BASELINE_ATTEMPTS_COMPLETE.json'), (False, 'DYNAMIC_ATTEMPTS_COMPLETE.json')]}
    hashes = {}
    for baseline, marker in markers.items():
        subset = {s + '/' + c['id'] for s in plan['subjects'] for c in plan['configurations'] if c['family'].startswith('B') == baseline}
        assert set(marker['attempt_hashes']) == subset
        assert marker['attempted'] == marker['completed'] == len(subset)
        hashes.update(marker['attempt_hashes'])
    counts = collections.Counter()
    families = collections.Counter()
    statuses_by_stage = {True: collections.Counter(), False: collections.Counter()}
    all_rows = []
    max_pg = max_ad = max_fd = 0.
    total_calls = total_iterations = trajectory_increases = 0
    baseline_completion_times = []
    dynamic_start_times = []
    for subject in plan['subjects']:
        prep = read(P / 'states' / (subject + '_A_PREPROCESSING.json'))
        assert prep['subject'] == subject and prep['role'] == 'A' and len(prep['units']) == 8
        assert prep['delta'] == .05 and prep['warm_bins'] == 10
        base_initial = np.asarray(read(P / 'fits' / subject / 'B0.json')['initial'])
        assert base_initial.shape == (8,) and np.isfinite(base_initial).all()
        subject_initials = {}
        for config in plan['configurations']:
            cid = config['id']; family = config['family']; baseline = family.startswith('B')
            path = P / 'fits' / subject / (cid + '.json')
            assert sha(path) == hashes[subject + '/' + cid]
            row = read(path)
            assert row['subject'] == subject and row['configuration'] == config and row['attempt'] == 1
            assert row['nominal_family'] == family and row['production_gate_sha256'] == sha(P / 'PRODUCTION_GATE.json')
            assert row['A_preprocessing_sha256'] == sha(P / 'states' / (subject + '_A_PREPROCESSING.json'))
            assert row['B_E_fit_data'] is False and row['Final_access'] is False
            assert row['status'] in ('NUMERICAL_PASS', 'NUMERICAL_FAIL'), 'No active/interrupted corrected attempt allowed'
            start = datetime.datetime.fromisoformat(row['started_at'])
            complete = datetime.datetime.fromisoformat(row['completed_at'])
            assert complete >= start and start >= datetime.datetime.fromisoformat(gate['frozen_at'])
            (baseline_completion_times if baseline else dynamic_start_times).append(complete if baseline else start)
            active = np.asarray(prep['active'], bool)
            if family == 'C':
                active = np.r_[active, prep['C_scales'][f"C_r{config['rank']}_tau{config['tau']}"]['q_scale']['active']]
            mask = np.ones((len(active), 8), bool)
            if family == 'B0':
                mask[1:] = False
            elif family == 'B1':
                mask[38:] = False
            elif family in ('B2', 'B3'):
                mask[38:] = False
                for v in range(8):
                    for u in range(8):
                        if (v == u) == (family == 'B2'):
                            mask[38 + 4 * v:38 + 4 * (v + 1), u] = True
            mask &= active[:, None]; mask[0] = True
            nlin = int(mask.sum())
            expected_initial = list(base_initial) + [0.] * (nlin - 8)
            bounds = [(-8., 8.)] * 8 + [(-1., 1.)] * (nlin - 8)
            if family in ('D', 'S'):
                k = config['k']
                expected_initial += np.random.Generator(np.random.PCG64(config['seed'])).uniform(-.05, .05, (k - 1) * 8).tolist()
                bounds += [(-2., 2.)] * ((k - 1) * 8)
                if family == 'D':
                    expected_initial += [2. * (i == j) - 2. * (i == k - 1) for i in range(k) for j in range(k - 1)]
                    bounds += [(-4., 4.)] * (k * (k - 1))
                expected_initial += [0.] * (k - 1)
                bounds += [(-4., 4.)] * (k - 1)
            np.testing.assert_array_equal(row['initial'], expected_initial)
            np.testing.assert_array_equal(row['bounds'], bounds)
            assert row['free_parameters'] == len(bounds)
            theta = np.asarray(row['coefficients']); g = np.asarray(row['independent']['analytic_gradient'])
            b = np.asarray(bounds); pg_vector = g.copy()
            pg_vector[((theta == b[:, 0]) & (g > 0)) | ((theta == b[:, 1]) & (g < 0))] = 0
            assert row['PG'] == float(np.max(np.abs(pg_vector)))
            numerical_record(row)
            check = row['independent']; ad = np.asarray(check['AD_gradient'])
            assert theta.shape == g.shape == ad.shape == (len(bounds),)
            assert np.isfinite(theta).all() and np.isfinite(g).all() and np.isfinite(ad).all()
            assert (theta >= b[:, 0]).all() and (theta <= b[:, 1]).all()
            assert check['AD_max_scaled'] == float(np.max(np.abs(g - ad) / np.maximum(1., np.maximum(np.abs(g), np.abs(ad)))))
            assert [d['step'] for d in check['FD']] == [1e-4, 1e-5, 1e-6]
            for fd in check['FD']:
                v = np.asarray(fd['numerical_gradient'])
                assert v.shape == theta.shape and np.isfinite(v).all()
                assert fd['max_scaled'] == float(np.max(np.abs(g - v) / np.maximum(1., np.maximum(np.abs(g), np.abs(v)))))
            assert row['budget_exhausted'] == (row['optimizer_status'] == 1)
            assert row['iterations'] <= 2000 and row['optimizer_objective_calls'] <= 80000
            history = row['optimizer_history']
            assert len(history) == row['iterations']
            for i, item in enumerate(history):
                assert item['iteration'] == i + 1 and 0 < item['calls'] <= row['optimizer_objective_calls']
                assert all(math.isfinite(item[k]) for k in ['objective', 'PG', 'full_gradient_inf'])
                assert 0 <= item['PG'] <= item['full_gradient_inf']
                if i:
                    assert item['calls'] > history[i - 1]['calls']
                    trajectory_increases += item['objective'] > history[i - 1]['objective']
            if history:
                assert abs(history[-1]['objective'] - row['objective']) < 1e-12
                assert history[-1]['PG'] == row['PG'] and history[-1]['full_gradient_inf'] == row['full_gradient_inf']
            else:
                assert family == 'B0' and row['optimizer_objective_calls'] == 1
            assert row['training_population_bins'] == prep['actual_score_population_bins']
            assert row['training_unit_bins'] == prep['actual_score_unit_bins'] == 8 * row['training_population_bins']
            penalty = np.r_[np.zeros(8), np.ones(len(theta) - 8)]
            reconstructed_objective = -row['training_score_LL'] / row['training_population_bins'] + config['ridge'] / 2 * np.sum(penalty * theta ** 2)
            assert abs(row['objective'] - reconstructed_objective) < 1e-12
            counts[row['status']] += 1; families[family] += 1; statuses_by_stage[baseline][row['status']] += 1
            max_pg = max(max_pg, row['PG']); max_ad = max(max_ad, check['AD_max_scaled'])
            max_fd = max(max_fd, max(x['max_scaled'] for x in check['FD']))
            total_calls += row['optimizer_objective_calls']; total_iterations += row['iterations']
            all_rows.append(row)
    assert max(baseline_completion_times) < min(dynamic_start_times)
    for baseline, marker in markers.items():
        assert marker['numerical_pass'] == statuses_by_stage[baseline]['NUMERICAL_PASS']
        assert len(marker['failures']) == statuses_by_stage[baseline]['NUMERICAL_FAIL']
    old_e = R / 'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'
    preservation = read(E / 'PRESERVATION_REGISTRATION.json')
    for name, value in preservation['historical_evidence'].items():
        assert sha(old_e / name) == value
    seal = read(old_e / 'INTERRUPTION_SEAL.json')
    assert len(seal['attempt_rows']) == 359 and seal['completed'] == 358 and seal['interrupted'] == 1 and seal['unattempted'] == 251
    old_counts = collections.Counter()
    for item in seal['attempt_rows']:
        path = R / 'paper15_dev/fits' / item['subject'] / (item['configuration'] + '.json')
        assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes']
        old_counts[item['status']] += 1
        if item['status'] == 'STARTED':
            residue = read(path)
            assert residue['status'] == 'STARTED' and residue['optimizer_history'] == [] and 'coefficients' not in residue
    assert old_counts == {'NUMERICAL_PASS': 358, 'STARTED': 1}
    assert not list((P / 'sensitivity_fits').glob('*/*/*.json'))
    assert not (P / 'SELECTION_FREEZE.json').exists() and not (P / 'E_BATCH_CLAIM.json').exists()
    saved = read(P / 'results/MAIN_SAVED_VERIFICATION.json')
    assert saved['attempted'] == saved['completed'] == 610 and saved['numerical_pass'] == counts['NUMERICAL_PASS']
    assert saved['ledger']['NEW_MAIN_ATTEMPTS'] == 610 and saved['ledger']['TOTAL_CUMULATIVE_ATTEMPTS'] == 969
    assert saved['ledger']['NEW_SENSITIVITY_ATTEMPTS'] == 0 and saved['ledger']['new_interrupted_or_active'] == 0
    assert saved['max_PG_passed'] == max_pg and saved['max_AD_scaled_passed'] == max_ad and saved['max_FD_scaled_passed'] == max_fd
    result = dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1', reviewer='/root/gradient_review',
                  time=datetime.datetime.now(datetime.timezone.utc).isoformat(), status='SAVED_MAIN_NUMERICAL_REVIEW_PASS',
                  attempted=610, completed=610, statuses=dict(counts), families=dict(families), historical_started=359,
                  historical_completed=358, historical_interrupted=1, historical_unattempted=251, new_sensitivity=0, cumulative_started=969,
                  all_610_initial_bounds_coordinate_errors_trajectories_and_hashes_verified=True, initialization_intercepts_reference='Same-subject saved B0 original initializer; raw count formula not reevaluated',
                  max_PG=max_pg, max_AD_scaled=max_ad, max_fixed_FD_scaled=max_fd, completed_objective_calls=total_calls,
                  completed_iterations=total_iterations, accepted_history_objective_increases=trajectory_increases,
                  fit_hashes=hashes, production_gate_sha256=sha(P / 'PRODUCTION_GATE.json'),
                  input_and_runtime_gate_files_rehashed=64, historical_fit_hashes_preserved=359,
                  evidence_hashes={n: sha(P / n) for n in ['A_FIT_PLAN.json', 'results/BASELINE_ATTEMPTS_COMPLETE.json', 'results/DYNAMIC_ATTEMPTS_COMPLETE.json', 'results/MAIN_SAVED_VERIFICATION.json', 'training.py', 'models.py', 'saved_audit.py']},
                  script_sha256=sha(Path(__file__)), real_fits=0, neural_arrays_loaded=0, real_likelihood_derivative_evaluations=0,
                  B_E_Final_access=False, scope='Saved main numerical integrity and ledger review, not B selection/E scientific outcome or Final admission')
    target = E / 'MAIN_NUMERICAL_REVIEW_1_RECEIPT.json'
    assert not target.exists()
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['fit_hashes', 'evidence_hashes']}, indent=2))
    print('review_receipt_sha256=' + sha(target))


if __name__ == '__main__':
    run()
