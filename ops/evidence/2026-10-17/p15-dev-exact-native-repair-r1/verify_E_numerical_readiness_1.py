"""Independent terminated sensitivity/ledger/E-payload saved arithmetic; no neural arrays."""
import collections
import datetime
import hashlib
import importlib.util
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
    raise AssertionError('No neural arrays/network/model/optimization/real derivative evaluation')


def run():
    assert (P / 'results/SENSITIVITY_ATTEMPTS_COMPLETE.json').exists()
    np.load = denied
    socket.create_connection = denied
    socket.socket.connect = denied
    sys.path.insert(0, str(R))
    from paper15_r1.source import load_json
    import paper15_r1.training as training
    import paper15_r1.independent_ad as ad_module
    from paper15_r1.models import Model
    from paper15_r1.saved_audit import numerical_record
    from paper15_r1.sensitivity_fits import verify_plan
    from paper15_r1.sensitivities import CASES
    from paper15_r1.ledger import snapshot
    for method in ['__init__', 'initialize', 'objective', 'value', 'prebin_logmasses']:
        setattr(Model, method, denied)
    training.minimize = denied
    ad_module.ad_function = denied
    ad_module.coordinate_check = denied
    spec = importlib.util.spec_from_file_location('review_sealer', E / 'seal_E_gate.py')
    sealer = importlib.util.module_from_spec(spec); spec.loader.exec_module(sealer)
    initial_payload = sealer.payload_hashes()
    selected = read(P / 'SELECTION_FREEZE.json'); subjects = selected['subjects']
    plan = read(P / 'SENSITIVITY_FIT_PLAN.json'); prep = read(P / 'results/SENSITIVITY_PREPARATION.json')
    candidates = read(P / 'results/B_CANDIDATE_SCORES.json')
    verify_plan(plan, selected, candidates, prep, subjects)
    gate = read(P / 'SENSITIVITY_GATE.json'); gate_sha = sha(P / 'SENSITIVITY_GATE.json')
    for rel, value in gate['hashes'].items():
        assert rel.endswith(('.py', '.json', '.txt'))
        assert sha(P / rel) == value
    for item in gate['independent_review_evidence'].values():
        assert sha(R / item['path']) == item['sha256']
    complete = read(P / 'results/SENSITIVITY_ATTEMPTS_COMPLETE.json')
    assert complete['attempted'] == complete['completed'] == plan['expected_attempts'] == 525
    assert len(complete['records']) == len(plan['attempts']) == 525
    actual = list((P / 'sensitivity_fits').glob('*/*/*.json'))
    expected_paths = {(i['subject'], i['case'], i['family']) for i in plan['attempts']}
    assert len(actual) == len(expected_paths) == 525
    assert {(f.parent.parent.name, f.parent.name, f.stem) for f in actual} == expected_paths
    assert len(prep['records']) == 110
    assert collections.Counter(r['status'] for r in prep['records']) == {'A_PREPROCESSING_SEALED': 105, 'UNAVAILABLE': 5}
    statuses = collections.Counter(); families = collections.Counter(); cases = collections.Counter(); fit_hashes = {}
    max_pg = max_ad = max_fd = 0.
    total_calls = total_iterations = trajectory_increases = 0
    unavailable = []
    for prepared in prep['records']:
        subject = prepared['subject']; cid = prepared['case']
        state_path = P / 'sensitivity_states' / subject / (cid + '.json')
        state = load_json(state_path.read_text())
        assert state['subject'] == subject and state['case'] == next(c for c in CASES if c['id'] == cid)
        assert state['status'] == prepared['status'] and state['B_selection_sha256'] == sha(P / 'SELECTION_FREEZE.json')
        if state['status'] == 'UNAVAILABLE':
            assert state['unavailability_reasons'] == prepared['reasons'] and prepared['reasons']
            assert not list((P / 'sensitivity_fits' / subject / cid).glob('*.json'))
            unavailable.append((subject, cid)); continue
        assert sha(state_path) == prepared['state_sha256']
    for item, marker in zip(plan['attempts'], complete['records']):
        assert marker['item'] == item
        subject, cid, family = item['subject'], item['case'], item['family']
        path = P / 'sensitivity_fits' / subject / cid / (family + '.json')
        assert sha(path) == marker['sha256']; fit_hashes[f'{subject}/{cid}/{family}'] = marker['sha256']
        state_path = P / 'sensitivity_states' / subject / (cid + '.json')
        assert sha(state_path) == item['state_sha256']
        state = load_json(state_path.read_text()); row = read(path)
        assert row['plan_item'] == item and row['attempt'] == 1 and row['status'] == marker['status']
        assert row['status'] in ('NUMERICAL_PASS', 'NUMERICAL_FAIL') and row['sensitivity_gate_sha256'] == gate_sha
        assert row['E_neural_fit_data'] is False and row['Final_access'] is False
        assert datetime.datetime.fromisoformat(row['completed_at']) >= datetime.datetime.fromisoformat(row['started_at']) >= datetime.datetime.fromisoformat(gate['frozen_at'])
        u = len(state['units']); active = np.asarray(state['active'], bool); nuisance = state['nuisance_columns']
        assert nuisance == (41 if cid == 'S10' else 37)
        assert state['delta'] == (.1 if cid == 'S04' else .05)
        assert state['warm'] == (5 if cid in ('S04', 'S05') else 10)
        mask = np.ones((len(active), u), bool); hstart = 1 + nuisance
        if family == 'B0': mask[1:] = False
        elif family == 'B1': mask[hstart:] = False
        elif family in ('B2', 'B3'):
            mask[hstart:] = False
            for v in range(u):
                for target in range(u):
                    if (v == target) == (family == 'B2'): mask[hstart + 4*v:hstart + 4*(v+1), target] = True
        else: assert family == 'B4'
        mask &= active[:, None]; mask[0] = True; nlin = int(mask.sum())
        bounds = np.asarray([(-8., 8.)] * u + [(-1., 1.)] * (nlin-u))
        assert row['free_parameters'] == nlin
        base = read(P / 'sensitivity_fits' / subject / cid / 'B0.json')['initial']
        assert len(base) == u and np.isfinite(base).all()
        np.testing.assert_array_equal(row['initial'], list(base) + [0.] * (nlin-u))
        assert item['seed'] == 11
        copy = dict(row, bounds=bounds.tolist(), budget_exhausted=row['optimizer_status'] == 1)
        numerical_record(copy)
        theta = np.asarray(row['coefficients']); check = row['independent']; g = np.asarray(check['analytic_gradient'])
        assert theta.shape == g.shape == (nlin,) and np.isfinite(theta).all() and np.isfinite(g).all()
        projected = g.copy(); projected[((theta == bounds[:, 0]) & (g > 0)) | ((theta == bounds[:, 1]) & (g < 0))] = 0
        assert row['PG'] == float(np.max(np.abs(projected)))
        assert row['actual_population_bins'] == state['trial_counts']['A'] * int(round(.5/state['delta']))
        assert row['actual_unit_bins'] == row['actual_population_bins'] * u
        assert row['iterations'] <= 2000 and row['objective_calls'] <= 80000
        history = row['optimizer_history']; assert len(history) == row['iterations']
        for i, h in enumerate(history):
            assert h['iteration'] == i+1 and 0 < h['calls'] <= row['objective_calls'] and math.isfinite(h['objective']) and math.isfinite(h['PG']) and h['PG'] >= 0
            if i:
                assert h['calls'] > history[i-1]['calls']
                trajectory_increases += h['objective'] > history[i-1]['objective']
        if history:
            assert abs(history[-1]['objective'] - row['objective']) < 1e-12 and history[-1]['PG'] == row['PG']
        else: assert family == 'B0' and row['objective_calls'] == 1
        statuses[row['status']] += 1; families[family] += 1; cases[cid] += 1
        max_pg = max(max_pg, row['PG']); max_ad = max(max_ad, check['AD_max_scaled']); max_fd = max(max_fd, max(d['max_scaled'] for d in check['FD']))
        total_calls += row['objective_calls']; total_iterations += row['iterations']
    assert statuses == {'NUMERICAL_PASS': 525} and complete['numerical_pass'] == 525
    assert families == {f'B{i}': 105 for i in range(5)}
    assert set(unavailable) == {('SWC_043','S02'), ('PL033','S03'), ('SWC_043','S03'), ('NYU-30','S03'), ('ZFM-01937','S03')}
    saved = read(P / 'results/SENSITIVITY_SAVED_VERIFICATION.json')
    assert saved['attempted'] == saved['completed'] == saved['numerical_pass'] == 525 and saved['failures'] == []
    assert saved['max_PG_passed'] == max_pg and saved['max_AD_scaled_passed'] == max_ad and saved['max_FD_scaled_passed'] == max_fd
    ledger = snapshot()
    assert ledger['NEW_MAIN_ATTEMPTS'] == 610 and ledger['NEW_SENSITIVITY_ATTEMPTS'] == 525 and ledger['TOTAL_CUMULATIVE_ATTEMPTS'] == 1494
    assert ledger['completed'] == ledger['numerical_pass'] == 1135 and ledger['new_interrupted_or_active'] == 0
    main = read(E / 'MAIN_NUMERICAL_REVIEW_1_RECEIPT.json')
    for key, value in main['fit_hashes'].items(): assert sha(P / 'fits' / (key + '.json')) == value
    assert sha(E / 'MAIN_NUMERICAL_REVIEW_1.md') == '3dd535ccc32d81dcac9054c14558e775072994d50af8fe3d73be90f4a647d49a'
    synthetic = read(E / 'FULL_SYNTHETIC_CONTROL_REVIEW_R1_RECEIPT.json')
    for name, value in synthetic['source_hashes'].items(): assert sha(P / name) == value
    for name, value in read(P / 'PRODUCTION_GATE.json')['hashes'].items(): assert sha(P / name) == value
    ref = read(P / 'REFERENCE_METADATA_FREEZE.json'); assert ref['subjects'] == subjects and ref['replicates'] == 999
    coverage = {suite: [] for suite in ['N1','N2','N3','N4']}
    for metadata in ref['records']:
        for suite, c in metadata['coverage'].items():
            assert c['epochs'] == len(c['trial_ids']) and c['total_epochs'] == len(metadata['E_trial_ids'])
            assert c['available'] == (True if suite == 'N1' else c['epochs'] >= 30 and c['epochs'] >= .6*c['total_epochs'])
            if c['available']: coverage[suite].append(metadata['subject'])
    assert [len(coverage[s]) for s in ['N1','N2','N3','N4']] == [10,10,10,5]
    assert set(coverage['N4']) == {'KS046','SWC_043','SWC_038','KS051','ZFM-01937'}
    assert not (P / 'E_EXPLORATORY_GATE.json').exists() and not (P / 'E_BATCH_CLAIM.json').exists()
    final_payload = sealer.payload_hashes(); assert final_payload == initial_payload
    result = dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1', reviewer='/root/gradient_review', time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  numerical_pass=525, numerical_fail=0, active_or_interrupted=0, families=dict(families), cases=dict(cases), unavailable=unavailable,
                  max_PG=max_pg, max_AD_scaled=max_ad, max_fixed_FD_scaled=max_fd, objective_calls=total_calls, accepted_iterations=total_iterations,
                  accepted_history_objective_increases=trajectory_increases, historical_started=359, corrected_main=610, corrected_sensitivity=525,
                  cumulative_started=1494, corrected_numerical_pass=1135, sensitivity_fit_hashes=fit_hashes, payload_hashes=final_payload,
                  payload_count=len(final_payload), metadata_control_coverage={k:len(v) for k,v in coverage.items()}, N4_aggregate_unavailable=True,
                  diagnostic_script_sha256=sha(Path(__file__)), seal_E_gate_sha256=sha(E / 'seal_E_gate.py'),
                  pre_E_limitations_sha256=sha(E / 'PRE_E_COVERAGE_LIMITATIONS.md'),
                  real_fits=0, real_likelihood_AD_FD_evaluations=0, neural_arrays_loaded=0, B_E_Final_neural_access=False)
    target = E / 'E_NUMERICAL_SAVED_CHECKS_1.json'; assert not target.exists()
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['sensitivity_fit_hashes','payload_hashes']}, indent=2))
    print('saved_checks_sha256=' + sha(target))


if __name__ == '__main__': run()
