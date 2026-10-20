"""Saved-value arithmetic only; no production scientific modules are imported."""
import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_pg_forensics_r1'
OLD = R / 'paper16_development_r3'
BASE = '1ab5a7b2077f9f8526bf5d5028b042da199f6bc6'
STEPS = [0.001, 0.0001, 1e-5, 1e-6]
CHECKS = ['initial', 'halfway', 'endpoint']


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def lines(path):
    return [json.loads(x) for x in Path(path).read_text(encoding='utf8').splitlines()]


def outward(x, g, lo, hi):
    """Independent implementation of the frozen outward-gradient definition."""
    x, g, lo, hi = map(np.asarray, (x, g, lo, hi))
    require(x.shape == g.shape == lo.shape == hi.shape, 'PG shape mismatch')
    require(all(np.isfinite(a).all() for a in (x, g, lo, hi)), 'PG nonfinite')
    require(np.all(lo <= hi) and np.all(x >= lo-1e-12) and np.all(x <= hi+1e-12), 'PG bounds')
    return np.where(((x <= lo+1e-12) & (g > 0)) | ((x >= hi-1e-12) & (g < 0)), 0., g)


def read_members(path, allowed, pins):
    """npz is lazy: read only named, hashed members, never iterate over values."""
    path = Path(path).resolve()
    rel = path.relative_to(R).as_posix()
    require(rel in pins and sha(path) == pins[rel], 'Unpinned or changed NPZ: '+rel)
    allowed = set(allowed)
    safe = {'x0', 'lo', 'hi', 'x', 'gradient', 'unit_ids', 'active', 'mean', 'scale'}
    safe |= {n+s for n in CHECKS for s in ['_x', '_analytic', '_AD', '_AD_error']}
    safe |= {n+s+str(h) for n in CHECKS for s in ['_FD_', '_FD_error_'] for h in STEPS}
    require(allowed <= safe, 'Forbidden NPZ member request')
    if '/prepared/' in rel:
        require(rel == 'paper16_development_r3/work/prepared/733457989/S02/state.npz', 'Only registered A S02 metadata')
        require(allowed <= {'unit_ids', 'active', 'mean', 'scale'}, 'A metadata only')
    else:
        require(rel.startswith('paper16_development_r3/work/fits/'), 'Only saved optimizer certificates')
    with np.load(path, allow_pickle=False) as data:
        require(allowed <= set(data.files), 'Missing saved NPZ member')
        result = {k: data[k].copy() for k in sorted(allowed)}
    require(all(np.isfinite(v).all() for v in result.values()), 'Nonfinite saved member')
    return result


def verify_inputs():
    pins = load(P/'SOURCE_PINS.json')
    require(pins['BASE'] == BASE, 'Exact BASE')
    runtime = load(P/'RUNTIME_SOURCE_PIN.json')
    require(runtime['scipy_version'] == '1.16.3' and sha(R/runtime['path']) == runtime['sha256'], 'Pinned static SciPy source identity')
    for name, digest in pins['files'].items():
        require(sha(R/name) == digest, 'Original source/evidence identity: '+name)
    protected = load(OLD/'PROTECTED_STATE_MANIFEST.json')['files']
    index = dict(pins['files'])
    for row in protected:
        path = R/row['path']
        require(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'Protected identity: '+row['path'])
        if row['path'] in index:
            require(index[row['path']] == row['sha256'], 'Conflicting source pin')
        index[row['path']] = row['sha256']
    require(len(protected) == 10717, 'Protected denominator')
    return pins, protected, index


def certificates(folder, pins):
    result = load(folder/'RESULT.json')
    diag = load(folder/'DIAGNOSTICS.json')
    require(sha(folder/'DIAGNOSTICS.json') == result['diagnostic_state_sha256'], 'Diagnostic result binding')
    state = diag['coordinate_state']
    require(sha(R/state['path']) == state['sha256'], 'Coordinate result binding')
    keys = {n+s for n in CHECKS for s in ['_x', '_analytic', '_AD', '_AD_error']}
    keys |= {n+s+str(h) for n in CHECKS for s in ['_FD_', '_FD_error_'] for h in STEPS}
    a = read_members(R/state['path'], keys, pins)
    initial = read_members(folder/'initial.npz', ['x0', 'lo', 'hi'], pins)
    end = read_members(folder/'endpoint.npz', ['x', 'gradient'], pins)
    require(sha(R/result['endpoint_state']['path']) == result['endpoint_state']['sha256'], 'Endpoint binding')
    require(np.array_equal(a['initial_x'], initial['x0']), 'Initial identity')
    require(np.array_equal(a['endpoint_x'], end['x']) and np.array_equal(a['endpoint_analytic'], end['gradient']), 'Endpoint identity')
    require(np.allclose(result['jac'], end['gradient'], rtol=1e-12, atol=1e-12) and np.array_equal(result['x'], end['x']), 'SciPy/checkpoint endpoint identity')
    require(result['fun'] == result['objective'] == diag['checkpoints'][2]['objective'], 'Endpoint objective identity')
    require((diag['FD_objective_calls'], diag['AD_calls'], diag['analytic_checkpoint_calls']) == (24*len(end['x']), 3, 3), 'Historical certificate budgets')
    for n, check in zip(CHECKS, diag['checkpoints']):
        g, ad = a[n+'_analytic'], a[n+'_AD']
        require(g.shape == ad.shape == initial['lo'].shape, 'Certificate shapes')
        err = np.abs(g-ad)/np.maximum(1, np.maximum(np.abs(g), np.abs(ad)))
        require(np.array_equal(err, a[n+'_AD_error']) and float(err.max()) == check['AD_scaled_coordinate_error_max'], 'Saved AD arithmetic')
        fd_errs = {}
        for h in STEPS:
            fd = a[n+'_FD_'+str(h)]
            error = np.abs(g-fd)/np.maximum(1, np.maximum(np.abs(g), np.abs(fd)))
            require(np.array_equal(error, a[n+'_FD_error_'+str(h)]), 'Saved FD arithmetic')
            fd_errs[str(h)] = float(error.max())
        require(fd_errs == check['FD_scaled_coordinate_errors'], 'Saved FD summaries')
        passed = bool(err.max() <= 1e-8 and fd_errs['1e-05'] <= 2e-5 and np.isclose(check['objective'], check['AD_objective'], atol=1e-10, rtol=1e-12))
        require(check['pass'] == passed and passed, 'Original derivative certificate')
    require(diag['all_checkpoints_pass'], 'Certificate conjunction')
    pg = float(np.max(np.abs(outward(end['x'], end['gradient'], initial['lo'], initial['hi']))))
    require(pg == result['projected_gradient_inf'] and result['numerical_pass'] == (pg <= 1e-5), 'Original scientific PG gate')
    return result, diag, a, initial


def feature_names():
    names = [f'PSTH_color_{c:+d}_time_{100+20*k}_{120+20*k}_ms' for c in [-1, 1] for k in range(6)]
    names += ['previous_color', 'previous_missing', 'previous_gap_over_gap_plus2', 'log1p_prior_samecolor_count_over_log181',
              'ordinal_over179', 'tau', 'tau_squared', 'tau_cubed', 'running_r', 'running_r_squared', 'color_times_running_r', 'running_missing']
    names += ['color_times_repeat', 'previous_color_times_repeat', 'order_squared', 'color_times_order']
    names += [f'{who}_history_{a}_{b}_ms' for who in ['own', 'other_mean'] for a, b in [(0, 20), (20, 60), (60, 100)]]
    names += [f'{who}_continuous_tau_{t}_ms' for who in ['own', 'other_mean'] for t in [40, 100]]
    require(len(names) == 38, 'S02 C feature dictionary')
    return names


def bound_counts(x, lo, hi):
    return {'lower': int(np.count_nonzero(x <= lo+1e-12)), 'upper': int(np.count_nonzero(x >= hi-1e-12)),
            'interior': int(np.count_nonzero((x > lo+1e-12) & (x < hi-1e-12)))}


def align_history(calls, accepted, checkpoint_objectives):
    require(len(calls) % 2 == 0, 'Paired call journal')
    groups = {}
    fg = []
    last_iterations = 0
    for i in range(0, len(calls), 2):
        before, after = calls[i:i+2]
        require(before['event'] == 'RESERVED_BEFORE_EVALUATION' and after['event'] == 'COMPLETED', 'Call ordering')
        require(before['call'] == after['call'] == i//2+1, 'Contiguous calls')
        n = before['iterations']
        require(n >= last_iterations and n <= len(accepted), 'Iteration grouping')
        last_iterations = n
        row = {'call': after['call'], 'accepted_iterations_before_call': n, 'objective': after['objective'], 'raw_gradient_inf': after['gradient_inf']}
        require(math.isfinite(row['objective']) and math.isfinite(row['raw_gradient_inf']), 'Finite saved trajectory')
        fg.append(row)
        groups.setdefault(n, []).append(row)
    require([a['iteration'] for a in accepted] == list(range(1, len(accepted)+1)), 'Accepted order')
    require(set(groups) == set(range(len(accepted))), 'Complete accepted FG groups')
    associated = [groups[i-1][-1] for i in range(1, len(accepted)+1)]
    for iteration, value in checkpoint_objectives.items():
        actual = fg[0]['objective'] if iteration == 0 else associated[iteration-1]['objective']
        require(actual == value, 'Recorded checkpoint objective cross-check')
    return fg, associated


def describe(values):
    a = np.asarray(values, dtype=float)
    require(len(a) > 0 and np.isfinite(a).all(), 'Nonempty finite descriptive stratum')
    return dict(zip(['min', 'q25', 'median', 'q75', 'q90', 'q95', 'q99', 'max'], np.quantile(a, [0, .25, .5, .75, .9, .95, .99, 1], method='linear').tolist()))


def summarize(records):
    return {'n': len(records), 'PG': describe([r['PG'] for r in records]), 'iterations': describe([r['iterations'] for r in records]),
            'FG_calls': describe([r['calls'] for r in records]), 'termination': dict(Counter(r['termination'] for r in records)),
            'PG_gt_0_5_threshold': sum(r['PG'] > 5e-6 for r in records), 'PG_gt_0_8_threshold': sum(r['PG'] > 8e-6 for r in records),
            'PG_gt_0_9_threshold': sum(r['PG'] > 9e-6 for r in records), 'optimizer_success_true': sum(r['optimizer_success'] for r in records)}


def csv_bytes(records):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode('utf8')


def json_bytes(value):
    return (json.dumps(value, indent=2, allow_nan=False)+'\n').encode('utf8')


def build():
    source, protected, pins = verify_inputs()
    failure = load(OLD/'NUMERICAL_FAILURE_SUMMARY.json')
    require(failure['scientific_verdict'] == 'STOP_NUMERICAL_REQUIRED_GATE', 'Immutable R3 STOP')
    folder = R/failure['folder']
    result, diag, data, initial = certificates(folder, pins)
    require(len(initial['x0']) == 37 and result['task'] == failure['task'], 'Frozen failed task')
    require(result['projected_gradient_inf'] == failure['PG'] > 1e-5, 'Preserved mandatory failure')
    meta = next(r for r in load(OLD/'results/A_PREPROCESSING_STATES.json') if r['key'] == '733457989/S02')
    require(meta['role'] == 'A' and meta['psth'] == 12 and meta['b1'] == 28, 'Registered A metadata')
    scaler = read_members(R/meta['path'], ['unit_ids', 'active', 'mean', 'scale'], pins)
    require(sha(R/meta['path']) == meta['sha256'], 'Scaler state binding')
    unit = np.flatnonzero(scaler['unit_ids'] == 951800892)
    require(len(unit) == 1 and scaler['active'].shape == (8, 38), 'Unit/feature shape')
    u = int(unit[0]); free = np.flatnonzero(scaler['active'][u]); names = feature_names()
    require(len(free) == 37 and np.array_equal(free[:12], np.arange(12)), 'PSTH retained and exact packed map')
    lo, hi = initial['lo'], initial['hi']
    require(np.array_equal(lo, np.r_[np.full(12, -10.), np.full(25, -1.)]) and np.array_equal(hi, -lo), 'Frozen bounds')
    coordinates, all_checkpoints = [], []
    checkpoint_summaries = []
    for n, saved_check in zip(CHECKS, diag['checkpoints']):
        x, g, ad = data[n+'_x'], data[n+'_analytic'], data[n+'_AD']
        pg = outward(x, g, lo, hi)
        checkpoint_summaries.append({'name': n, 'objective': saved_check['objective'], 'PG': float(np.max(np.abs(pg))),
                                     'raw_gradient_inf': float(np.abs(g).max()), 'bounds': bound_counts(x, lo, hi),
                                     'AD_error_max': saved_check['AD_scaled_coordinate_error_max'], 'FD_errors': saved_check['FD_scaled_coordinate_errors']})
        for i, original in enumerate(free):
            row = {'checkpoint': n, 'packed_index': i, 'original_feature_index': int(original), 'feature': names[original],
                   'coefficient': float(x[i]), 'lower': float(lo[i]), 'upper': float(hi[i]), 'analytic_gradient': float(g[i]),
                   'AD_gradient': float(ad[i]), 'outward_PG_component': float(pg[i]),
                   'bound_status': 'LOWER' if x[i] <= lo[i]+1e-12 else 'UPPER' if x[i] >= hi[i]-1e-12 else 'INTERIOR',
                   'A_scaler_mean': float(scaler['mean'][u, original]), 'A_scaler_scale': float(scaler['scale'][u, original])}
            for h in STEPS:
                row['FD_'+str(h)] = float(data[n+'_FD_'+str(h)][i])
            row['AD_absolute_error'] = abs(float(g[i]-ad[i]))
            row['frozen_FD_absolute_error'] = abs(float(g[i]-data[n+'_FD_1e-05'][i]))
            row['AD_scaled_error'] = float(data[n+'_AD_error'][i])
            row['frozen_FD_scaled_error'] = float(data[n+'_FD_error_1e-05'][i])
            all_checkpoints.append(row)
            if n == 'endpoint': coordinates.append(row)
    accepted = lines(folder/'ACCEPTED.jsonl')
    fg, associated = align_history(lines(folder/'CALLS.jsonl'), accepted, {0: diag['checkpoints'][0]['objective'], 127: diag['checkpoints'][1]['objective'], 254: result['objective']})
    require(len(accepted) == result['nit'] == 254 and len(fg) == result['nfev'] == 275, 'Trajectory denominators')
    previous = initial['x0']; objective_previous = fg[0]['objective']; accepted_summaries = []
    for row, frow in zip(accepted, associated):
        x = np.asarray(row['x']); step = x-previous
        require(x.shape == (37,) and np.all(x >= lo-1e-12) and np.all(x <= hi+1e-12), 'Accepted feasible vector')
        reduction = objective_previous-frow['objective']
        accepted_summaries.append({'iteration': row['iteration'], 'associated_FG_call': frow['call'], 'objective_protocol_derived': frow['objective'],
            'objective_reduction_protocol_derived': reduction, 'relative_reduction_protocol_derived': reduction/max(1., abs(objective_previous), abs(frow['objective'])),
            'raw_gradient_inf_protocol_derived': frow['raw_gradient_inf'], 'step_inf': float(np.abs(step).max()), 'step_l2': float(np.linalg.norm(step)),
            'bound_counts': bound_counts(x, lo, hi), 'vector_sha256_float64': hashlib.sha256(x.tobytes()).hexdigest()})
        previous, objective_previous = x, frow['objective']
    require(np.array_equal(previous, data['endpoint_x']) and np.array_equal(np.asarray(accepted[126]['x']), data['halfway_x']), 'Accepted checkpoint vector identity')
    secants = []
    for a, b in [('initial', 'halfway'), ('halfway', 'endpoint'), ('initial', 'endpoint')]:
        s = data[b+'_x']-data[a+'_x']; y = data[b+'_analytic']-data[a+'_analytic']
        secants.append({'from': a, 'to': b, 's_norm2': float(np.linalg.norm(s)), 'y_norm2': float(np.linalg.norm(y)),
                        'long_chord_sTy_over_sTs': float(s@y/(s@s)), 'not_local_Hessian_or_condition_number': True})
    records = []
    attempts = [r for r in lines(OLD/'results/FIT_JOURNAL.jsonl') if r['event'] == 'ATTEMPTED']
    require(len(attempts) == 953 and len({r['task']['id'] for r in attempts}) == 953, 'Every original attempt, no retry')
    for attempt in attempts:
        task = attempt['task']; f = OLD/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
        rr, dd, aa, ii = certificates(f, pins)
        require(rr['task'] == task and (f/'ATTEMPT.json').exists(), 'Original attempt identity')
        if not rr['numerical_pass']:
            require(f == folder, 'Only original failure'); continue
        records.append({'task_id': task['id'], 'mouse': task['mouse_id'], 'panel': task['panel'], 'model': task['model'],
            'unit': task['unit_id'], 'seed': task['seed'], 'lambda_label': task['lambda'], 'PG': rr['projected_gradient_inf'],
            'objective_saved': rr['objective'], 'iterations': rr['nit'], 'calls': rr['nfev'], 'optimizer_success': rr['success'], 'termination': rr['message']})
    require(len(records) == 952, 'Accepted denominator')
    strata = {'all': records, 'C': [r for r in records if r['model'] == 'C'], 'S02': [r for r in records if r['panel'] == 'S02'],
              'S02_C': [r for r in records if r['panel'] == 'S02' and r['model'] == 'C']}
    for m in sorted({r['model'] for r in records}):strata['model_'+m] = [r for r in records if r['model'] == m]
    for panel in sorted({r['panel'] for r in records}):strata['panel_'+panel] = [r for r in records if r['panel'] == panel]
    comparison = {'denominator': 952, 'threshold': 1e-5, 'no_new_scientific_inference': True, 'strata': {k: summarize(v) if v else {'n': 0, 'unavailable': 'No earlier accepted endpoint in this stratum'} for k, v in strata.items()},
        'failed_endpoint': {'PG': result['projected_gradient_inf'], 'iterations': 254, 'calls': 275},
        'comparison_is_censored': 'Sequential STOP after953 attempts. Remaining5518 tasks unavailable; 952 endpoints are neither random nor independent animals.',
        'failed_task_percentiles_descriptive': {key: sum(r[field] <= value for r in records)/952 for key, field, value in [('iterations', 'iterations', 254), ('calls', 'calls', 275)]}}
    trajectory = {'saved_FG_calls': fg, 'accepted_vectors': accepted_summaries, 'checkpoints': checkpoint_summaries,
        'association_method': 'Static pinned SciPy NEW_X invokes callback after accepted FG. Last completed FG at broker accepted-count i-1 is associated with accepted iteration i. Cross-checked at initial,127,254; FG x not journaled, so other pair identities are protocol-derived, not independently saved.',
        'missing_evidence': ['FG parameter vectors/full gradients at every trial', 'L-BFGS correction pairs/internal projected-gradient norm/line-search task state', 'Design matrix or local Hessian audit (not accessed)', 'Any unattempted outcome'],
        'termination': result['message'], 'SciPy_success': result['success'], 'scientific_gate_pass': False,
        'ftol': 1e-12, 'gtol': 2e-6, 'last_accepted_relative_reduction': accepted_summaries[-1]['relative_reduction_protocol_derived'],
        'saved_endpoint_PG': result['projected_gradient_inf'], 'largest_residuals': sorted(coordinates, key=lambda r: -abs(r['outward_PG_component']))[:8],
        'inactive_features': [{'original_index': int(i), 'name': names[i]} for i in np.flatnonzero(~scaler['active'][u])],
        'active_nonPSTH_scaler_scale': describe(scaler['scale'][u, free[12:]]),
        'long_chord_secants_not_condition_estimates': secants,
        'accepted_objective_increase_count_protocol_derived': sum(r['objective_reduction_protocol_derived'] < 0 for r in accepted_summaries),
        'scientific_conclusion': 'Frozen relative-objective termination preceded mandatory PG convergence; conditioning may contribute but is not established by saved evidence.'}
    audit = {'MISSION_ID': 'P16-PG-FAILURE-FORENSICS-R1', 'BASE_SHA': BASE, 'source_pin_files_verified': len(source['files']),
        'R3_BASE_payloads_bound_in_SOURCE_PINS': len(source['R3_BASE_files']), 'protected_files_verified': len(protected), 'protected_bytes_verified': sum(r['bytes'] for r in protected),
        'failed_task': failure['task'], 'original_stop': failure['scientific_verdict'], 'source_pins_sha256': sha(P/'SOURCE_PINS.json'),
        'native_inherited_reproduction': 'PASS, logged separately before analysis', 'new_model_fits': 0, 'new_optimizer_calls': 0, 'new_objective_or_gradient_evaluations': 0,
        'new_scientific_scores': 0, 'B_E_neural_access': False, 'Final_C_access': False, 'Final_D_access': False,
        'decoded_NPZ_scope': 'Only saved optimizer x/bounds/derivative certificates for953 attempts; registered A S02 scaler metadata. No raw/y/timestamp members.',
        'byte_hashing_is_not_neural_value_decoding': True, 'protected_before_and_after': True,
        'historical_warning_preserved': 'R3 numerical required gate failure; scientific STOP remains', 'evidence_limitations': trajectory['missing_evidence']}
    # Recheck every protected byte after reads. No mutations of original evidence allowed.
    for row in protected:require(sha(R/row['path']) == row['sha256'], 'Post-analysis protected identity')
    return {'SOURCE_AND_EVIDENCE_AUDIT.json': json_bytes(audit), 'FAILED_COORDINATE_ANALYSIS.csv': csv_bytes(coordinates),
        'CHECKPOINT_COORDINATE_ANALYSIS.csv': csv_bytes(all_checkpoints), 'SAVED_TRAJECTORY_ANALYSIS.json': json_bytes(trajectory),
        'ACCEPTED_FIT_COMPARISON.json': json_bytes(comparison), 'ACCEPTED_ENDPOINTS.csv': csv_bytes(records)}


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--write', action='store_true');args = parser.parse_args()
    outputs = build()
    for name, payload in outputs.items():
        path = P/name
        if args.write:
            with path.open('xb') as stream:stream.write(payload)
        else:
            require(path.read_bytes() == payload, 'Saved-only report reproduction: '+name)
    print(json.dumps({'forensic_reproduction': 'PASS', 'reports': len(outputs), 'coordinates': 37, 'checkpoints': 111, 'accepted': 952,
        'new_model_fits': 0, 'new_optimizer_calls': 0, 'new_scientific_scores': 0, 'neural_arrays_decoded': 0}))


if __name__ == '__main__':main()
