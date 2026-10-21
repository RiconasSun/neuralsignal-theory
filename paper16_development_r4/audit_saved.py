"""Prospective state admission audit; no optimization, derivatives or scoring."""
import csv
import datetime
import hashlib
import json
import math
import socket
from pathlib import Path
from unittest.mock import patch

import numpy as np

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_development_r4'
OLD = R / 'paper16_development_r3'


def load(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def identities(manifest):
    for row in manifest['files']:
        path = R / row['path']
        require(path.is_file() and sha(path) == row['sha256'], 'Hash: ' + row['path'])
        if 'bytes' in row:
            require(path.stat().st_size == row['bytes'], 'Size: ' + row['path'])


def array_identity(value):
    return {'shape': list(value.shape), 'dtype': value.dtype.str,
            'sha256': hashlib.sha256(value.tobytes()).hexdigest()}


def forbid(*args, **kwargs):
    raise RuntimeError('Saved admission audit forbids model evaluation/optimization/network')


def exact_journal(folder, result, coordinates, initial):
    calls = [json.loads(s) for s in (folder / 'CALLS.jsonl').read_text().splitlines()]
    accepted_path = folder / 'ACCEPTED.jsonl'
    accepted = [json.loads(s) for s in accepted_path.read_text().splitlines()] if accepted_path.exists() else []
    n, nit = result['nfev'], result['nit']
    require(len(calls) == 2*n and n == result['external_value_gradient_pairs'] <= 6000,
            'Complete FG accounting')
    require(len(accepted) == nit == result['external_accepted_iterations'] <= 1500,
            'Complete accepted iterations')
    for index in range(n):
        a, b = calls[2*index:2*index+2]
        require(a['event'] == 'RESERVED_BEFORE_EVALUATION' and b['event'] == 'COMPLETED'
                and a['call'] == b['call'] == index+1, 'FG order')
        require(0 <= a['iterations'] <= nit and math.isfinite(b['objective'])
                and math.isfinite(b['gradient_inf']), 'Finite FG history')
    for index, row in enumerate(accepted):
        x = np.asarray(row['x'])
        require(row['iteration'] == index+1 and x.shape == initial['x0'].shape
                and np.isfinite(x).all() and np.all(x >= initial['lo']-1e-12)
                and np.all(x <= initial['hi']+1e-12), 'Accepted vector/bounds')
    mid = accepted[math.ceil(nit/2)-1]['x'] if accepted else result['x']
    require(np.array_equal(coordinates['initial_x'], initial['x0'])
            and np.array_equal(coordinates['halfway_x'], mid)
            and np.array_equal(coordinates['endpoint_x'], result['x']), 'Exact certificate points')
    require(result['halfway_accepted_iteration'] == math.ceil(nit/2), 'Halfway definition')
    return n, nit


def coordinate_checks(folder):
    diag = load(folder / 'DIAGNOSTICS.json')
    receipt = diag['coordinate_state']
    require(sha(R / receipt['path']) == receipt['sha256'], 'Coordinate file binding')
    with np.load(R / receipt['path'], allow_pickle=False) as saved:
        values = {k: saved[k].copy() for k in saved.files}
    require({k: array_identity(v) for k, v in values.items()} == receipt['arrays'],
            'Coordinate member identities')
    p = diag['free_coordinates']
    require((diag['FD_objective_calls'], diag['AD_calls'], diag['analytic_checkpoint_calls'])
            == (24*p, 3, 3), 'Original certificate budgets')
    require(len(diag['checkpoints']) == 3, 'Three original checkpoints')
    ad_max, fd_max = 0., 0.
    for name, row in zip(['initial', 'halfway', 'endpoint'], diag['checkpoints']):
        x, g, ad = (values[name + suffix] for suffix in ['_x', '_analytic', '_AD'])
        require(all(v.shape == (p,) and np.isfinite(v).all() for v in [x, g, ad]),
                'Finite coordinate points/gradients')
        delta = np.abs(g-ad) / np.maximum(1, np.maximum(np.abs(g), np.abs(ad)))
        require(np.array_equal(delta, values[name+'_AD_error'])
                and float(delta.max()) == row['AD_scaled_coordinate_error_max'], 'AD arithmetic')
        errors = {}
        for h in [.001, .0001, .00001, .000001]:
            fd = values[name+'_FD_'+str(h)]
            require(fd.shape == (p,) and np.isfinite(fd).all(), 'Finite FD vector')
            err = np.abs(fd-g) / np.maximum(1, np.maximum(np.abs(fd), np.abs(g)))
            require(np.array_equal(err, values[name+'_FD_error_'+str(h)])
                    and float(err.max()) == row['FD_scaled_coordinate_errors'][str(h)], 'FD arithmetic')
            errors[str(h)] = float(err.max())
        require(row['checkpoint'] == name and row['pass'] is True
                and math.isfinite(row['objective']) and math.isfinite(row['AD_objective'])
                and np.isclose(row['objective'], row['AD_objective'], atol=1e-10, rtol=1e-12)
                and delta.max() <= 1e-8 and errors['1e-05'] <= 2e-5
                and row['frozen_FD_scaled_error'] == errors['1e-05'], 'Unchanged AD/fixed-FD gate')
        ad_max, fd_max = max(ad_max, float(delta.max())), max(fd_max, errors['1e-05'])
    require(diag['all_checkpoints_pass'] is True and diag['FD_step_not_selected_post_result'] is True,
            'Original certificate conjunction')
    return diag, values, ad_max, fd_max


def projected(x, g, lo, hi):
    return np.where(((x <= lo+1e-12) & (g > 0)) | ((x >= hi-1e-12) & (g < 0)), 0, g)


def prepared_states():
    from paper16_development_r3.features import Batch, Scaling
    states = {}
    for row in load(OLD / 'results/A_PREPROCESSING_STATES.json'):
        require(row['role'] == 'A' and sha(R/row['path']) == row['sha256'], 'A preparation identity')
        with np.load(R/row['path'], allow_pickle=False) as a:
            arrays = {k: a[k].copy() for k in a.files}
        require({k: array_identity(v) for k, v in arrays.items()} == row['arrays'], 'A member identity')
        batch = Batch(**{k: arrays[k] for k in ['raw', 'y', 'ordinals', 'unit_ids', 'colors',
                                               'running_missing', 'score_mask']},
                      dt=row['dt'], psth=row['psth'], b1=row['b1'], role='A', panel=row['panel'])
        require(np.all((batch.ordinals >= 0) & (batch.ordinals < 90))
                and np.all(np.diff(batch.ordinals) > 0) and np.isfinite(batch.raw).all()
                and np.isfinite(batch.y).all(), 'A-only finite original support')
        # Verify the existing scaler; this creates no new fitted or usable state.
        mean = batch.raw.mean(axis=(0, 1)); scale = np.maximum(.25, batch.raw.std(axis=(0, 1)))
        active = batch.raw.var(axis=(0, 1)) > 1e-12
        mean[:, :batch.psth] = 0; scale[:, :batch.psth] = 1; active[:, :batch.psth] = True
        require(all(np.array_equal(arrays[k], v) for k, v in
                    [('mean', mean), ('scale', scale), ('active', active)]), 'Original A scaler definition')
        scaler = Scaling(arrays['mean'], arrays['scale'], arrays['active'], row['psth'])
        require(row['key'] not in states, 'Unique A preparation key')
        states[row['key']] = (batch, scaler, row)
    return states


def run():
    require(load(P/'STATE_REUSE_REGISTRATION.json')['before_saved_state_audit'], 'Prospective reuse policy')
    for path, digest in load(P/'SOURCE_PINS.json')['files'].items():
        require(sha(R/path) == digest, 'Original source/evidence pin: '+path)
    identities(load(OLD/'PROTECTED_STATE_MANIFEST.json'))
    identities(load(OLD/'PREFIT_FREEZE_MANIFEST.json'))
    runtime = load(R/'paper16_termination_feasibility1/RUNTIME_IDENTITY.json')
    for path, digest in runtime['files'].items():
        require(sha(R/path) == digest, 'Pinned mathematical runtime')
    from paper16_development_r3 import models, panels
    from paper16_development_r3.core import spec, dynamics
    records = sorted([r for r in load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources']
                      if r['selection']['admitted']], key=lambda r: int(r['source']['mouse_id']))
    by_mouse = {r['source']['mouse_id']: r for r in records}
    require(len(records) == 27 and sum(r['source']['protocol'] == 'brain_observatory_1.1'
                                     for r in records) == 5, 'Original27/5BO/22FC')
    plan = load(OLD/'results/TASK_PLAN.json')
    require(plan == panels.task_plan(records, load(OLD/'results/PANEL_PREFIT_PLAN.json')),
            'Re-derived exact full task plan')
    require(len(plan['tasks']) == 6471, 'Original6471tasks')
    selection = load(OLD/'results/B_SELECTION.json')
    require(selection['selected_lambda'] == 1. and selection['selection_information'] == 'B1_UNPENALIZED_ONLY',
            'Historical fixed lambda, no reselection')
    journal = [json.loads(s) for s in (OLD/'results/FIT_JOURNAL.jsonl').read_text().splitlines()]
    attempts = [r['task'] for r in journal if r['event'] == 'ATTEMPTED']
    require(len(attempts) == len({t['id'] for t in attempts}) == 953, 'Original953 unique attempts')
    tasks_by_id = {t['id']: t for t in plan['tasks']}
    require(all(tasks_by_id.get(t['id']) == t for t in attempts), 'All attempted tasks exact plan members')
    states = prepared_states()
    admitted, rejected, excluded = [], [], []
    with patch.object(models.Objective, 'analytic', side_effect=forbid), \
         patch.object(models.Objective, 'AD', side_effect=forbid), \
         patch.object(models.Objective, 'score', side_effect=forbid), \
         patch.object(spec, 'glm', side_effect=forbid), \
         patch.object(dynamics, 'objective', side_effect=forbid):
        for task in attempts:
            folder = OLD/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
            result = load(folder/'RESULT.json')
            if result['numerical_pass'] is not True:
                excluded.append({'task': task, 'reason': 'ORIGINAL_FAILED_R3_ENDPOINT_INELIGIBLE',
                                 'original_PG': result['projected_gradient_inf']})
                continue
            row = {'task_id': task['id'], 'mouse_id': task['mouse_id'], 'panel': task['panel'],
                   'model': task['model'], 'unit_id': task['unit_id'], 'seed': task['seed'],
                   'historical_ftol': 1e-12, 'generated_by': 'R3', 'admitted_under': 'R4_STATE_ADMISSIBILITY',
                   'counterfactual_execution_equivalence_claimed': False}
            try:
                record = by_mouse[task['mouse_id']]; batch, scaler, prep = states[task['mouse_id']+'/'+task['panel']]
                unit = None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id'])
                lam = 1. if task['lambda'] == 'GLOBAL' else task['lambda']
                objective = models.Objective(batch, scaler, task['model'], lam, unit, task['seed'])
                attempt = load(folder/'ATTEMPT.json')
                require(attempt['task'] == result['task'] == task and attempt['no_retry'] is True,
                        'Exact task/attempt identity')
                require(sha(folder/'initial.npz') == attempt['bounds']['sha256'], 'Initializer binding')
                with np.load(folder/'initial.npz', allow_pickle=False) as a:
                    initial = {k: a[k].copy() for k in a.files}
                require({k: array_identity(v) for k, v in initial.items()} == attempt['bounds']['arrays'],
                        'Initializer member identities')
                require(all(np.array_equal(initial[k], v) for k, v in
                            [('x0', objective.x0), ('lo', objective.lo), ('hi', objective.hi)]),
                        'Original initializer/packing/bounds from exact A/model/seed')
                diag, coord, ad, fd = coordinate_checks(folder)
                require(sha(folder/'DIAGNOSTICS.json') == result['diagnostic_state_sha256'], 'Diagnostic binding')
                require(sha(R/result['endpoint_state']['path']) == result['endpoint_state']['sha256'],
                        'Endpoint binding')
                with np.load(R/result['endpoint_state']['path'], allow_pickle=False) as a:
                    end = {k: a[k].copy() for k in a.files}
                require({k: array_identity(v) for k, v in end.items()} == result['endpoint_state']['arrays'],
                        'Endpoint member identities')
                x, g = coord['endpoint_x'], coord['endpoint_analytic']
                require(np.array_equal(end['x'], x) and np.array_equal(end['gradient'], g)
                        and np.array_equal(np.asarray(result['x']), x)
                        and np.allclose(result['jac'], g, atol=1e-12, rtol=1e-12), 'Exact endpoint')
                require(np.all(x >= initial['lo']-1e-12) and np.all(x <= initial['hi']+1e-12), 'Endpoint bounds')
                pg = float(np.abs(projected(x, g, initial['lo'], initial['hi'])).max())
                require(pg == result['projected_gradient_inf'] and pg <= 1e-5, 'Original outward PG')
                require(result['success'] is True and result['message'] ==
                        'CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL', 'Original gradient termination')
                require(math.isfinite(result['objective']) and result['objective'] == result['fun']
                        and np.isclose(result['fun'], diag['checkpoints'][-1]['objective'], atol=1e-10, rtol=1e-12),
                        'Original objective/checkpoint')
                calls, iterations = exact_journal(folder, result, coord, initial)
                row.update(status='COMPATIBLE', session_id=record['source']['session_id'],
                           probe_id=record['source']['probe_id'], lambda_used=lam,
                           prepared_A_state=prep['path'], prepared_A_sha256=prep['sha256'],
                           observation_mask_sha256=prep['arrays']['score_mask']['sha256'],
                           feature_identity=prep['arrays']['raw'], scaler_identities={k: prep['arrays'][k] for k in ['mean','scale','active']},
                           unit_identity=prep['arrays']['unit_ids'], original_source=record['source'],
                           result_path=(folder/'RESULT.json').relative_to(R).as_posix(),
                           result_sha256=sha(folder/'RESULT.json'), initial_sha256=sha(folder/'initial.npz'),
                           coordinate_sha256=diag['coordinate_state']['sha256'],
                           endpoint_sha256=result['endpoint_state']['sha256'], objective=result['objective'],
                           PG=pg, AD_error_max=ad, fixed_FD_error_max=fd, FG_calls=calls,
                           accepted_iterations=iterations, termination=result['message'],
                           source_runtime_provenance='Exact historical prefit/source manifests and pinned runtime verified',
                           E_Final_outcome_selection=False)
                admitted.append(row)
            except Exception as exc:
                row.update(status='INCOMPATIBLE', reason=str(exc)); rejected.append(row)
    b0_rows = []
    for record in records:
        mouse = record['source']['mouse_id']; batch, _, prep = states[mouse+'/MAIN']
        for unit, uid in enumerate(batch.unit_ids):
            folder = OLD/'work/B0'/mouse/str(uid)
            row = {'mouse_id': mouse, 'session_id': record['source']['session_id'],
                   'probe_id': record['source']['probe_id'], 'unit_id': int(uid), 'generated_by': 'R3_ANALYTIC'}
            try:
                result = load(folder/'RESULT.json'); diag, coord, ad, fd = coordinate_checks(folder)
                expected = np.array([spec.scored_log_rate(batch.y[:, :, unit].ravel(),
                                                        np.full(batch.y[:, :, unit].size, batch.dt))])
                require(all(np.array_equal(coord[k+'_x'], expected) for k in ['initial','halfway','endpoint']),
                        'B0 analytic MLE exact A score counts/exposure/bounds')
                pg = float(np.abs(projected(expected, coord['endpoint_analytic'], np.array([-10.]), np.array([10.]))).max())
                require(result['unit_id'] == int(uid) and result['analytic_MLE_not_optimizer_attempt'] is True
                        and result['numeric_pass'] is True and pg == result['projected_gradient_inf'] <= 1e-5,
                        'B0 unchanged required gate')
                row.update(status='COMPATIBLE', PG=pg, AD_error_max=ad, fixed_FD_error_max=fd,
                           result_path=(folder/'RESULT.json').relative_to(R).as_posix(),
                           result_sha256=sha(folder/'RESULT.json'), coordinate_sha256=diag['coordinate_state']['sha256'],
                           prepared_A_sha256=prep['sha256'])
            except Exception as exc:
                row.update(status='INCOMPATIBLE', reason=str(exc))
            b0_rows.append(row)
    require(len(excluded) == 1 and len(admitted)+len(rejected) == 952 and len(b0_rows) == 216,
            'Original exact denominators')
    admitted_ids = {row['task_id'] for row in admitted}
    remaining = [t for t in plan['tasks'] if t['id'] not in admitted_ids]
    passed = not rejected and all(row['status'] == 'COMPATIBLE' for row in b0_rows) and len(remaining) == 5519
    once(P/'STATE_COMPATIBILITY_MATRIX.json', {'states': admitted+rejected})
    once(P/'B0_COMPATIBILITY_MATRIX.json', {'states': b0_rows})
    once(P/'NEW_TASK_PLAN_CANDIDATE.json', {'full_task_plan_sha256': sha(OLD/'results/TASK_PLAN.json'),
         'tasks': remaining, 'optimizer_attempt_count': len(remaining), 'scientific_execution_authorized_yet': False})
    for name, rows in [('STATE_COMPATIBILITY_MATRIX.csv', admitted+rejected), ('B0_COMPATIBILITY_MATRIX.csv', b0_rows)]:
        keys = [k for k in rows[0] if not isinstance(rows[0][k], (dict, list))]
        if any('reason' in r for r in rows): keys.append('reason')
        with (P/name).open('x', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore'); writer.writeheader(); writer.writerows(rows)
    result = {'MISSION_ID': 'P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4',
              'completed_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'old_states_audited': 952, 'compatible_optimizer_states': len(admitted),
              'incompatible_optimizer_states': len(rejected), 'B0_audited': 216,
              'compatible_B0_states': sum(r['status'] == 'COMPATIBLE' for r in b0_rows),
              'required_gate_pass': passed, 'admission_pending_independent_approval': True,
              'new_tasks_derived': len(remaining), 'excluded_original_failure': excluded,
              'feasibility_diagnostic_admitted': False, 'new_optimizer_calls': 0,
              'new_likelihood_or_derivative_evaluations': 0, 'B_E_scientific_access': False,
              'Final_C_D_access': False, 'historical_ftol_label_preserved': 1e-12,
              'counterfactual_bitwise_claim': False, 'no_fallback': True}
    once(P/'STATE_REUSE_AUDIT_RESULT.json', result)
    print(json.dumps(result, indent=2))
    return passed


if __name__ == '__main__':
    with patch.object(socket.socket, 'connect', side_effect=forbid):
        raise SystemExit(0 if run() else 2)
