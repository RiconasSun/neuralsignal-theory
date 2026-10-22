"""One saved-only independent audit of new completed R5 states; no evaluations."""
import collections
import contextlib
import datetime
import hashlib
import importlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

import numpy as np

R = Path.cwd().resolve()
P = R / 'paper16_development_r5'
E = R / 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5'
Q = R / 'paper16_shutdown_recovery_r5_protocol'
OLD = R / 'paper16_development_r3'
FOUR = R / 'paper16_development_r4'
PREFIX = 'ops.evidence.2026-10-21.p16-m3-m5-shutdown-recovery-r5.'
CONTEXT = {'stage': 'NOT_STARTED', 'task': None}
COUNTS = collections.Counter()
REG = None
OLD_HELPER = None
STATE_FILES = {}

def J(path): return json.loads(Path(path).read_bytes())
def H(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def C(ok, message):
    if not ok: raise AssertionError(message)
def once(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
def append(path, value):
    with Path(path).open('a', encoding='utf8', newline='\n') as stream:
        stream.write(json.dumps(value, allow_nan=False) + '\n'); stream.flush(); os.fsync(stream.fileno())
def ID(a): return {'shape': list(a.shape), 'dtype': a.dtype.str, 'sha256': hashlib.sha256(a.tobytes()).hexdigest()}
def deny(*args, **kwargs): raise AssertionError('M4 observer forbids objective/gradient/AD/FD/score/minimize/network')

def guard():
    path = P / 'results/STAGE_CLAIM.json'
    C(H(path) == REG['stage_claim_sha256'], 'Exact original Stage-B claim, no restart/reset')
    stage = J(path)
    C(stage['phase'] == 'B_A_M4' and stage['no_reset'] is True, 'One bounded A/M4 phase')
    first, last = [datetime.datetime.fromisoformat(stage[k]) for k in ['start_UTC', 'deadline_UTC']]
    C(0 < stage['deadline_monotonic'] - stage['start_monotonic'] <= 172800
      and (last - first).total_seconds() == 172800, 'Unextended original 48-hour ceilings')
    C(stage['start_monotonic'] <= time.monotonic() < stage['deadline_monotonic']
      and first <= datetime.datetime.now(datetime.timezone.utc) < last, 'Independent review within original48h')

def live_lines(path):
    path = Path(path)
    if not path.exists(): return []
    raw = path.read_bytes()
    # A live append may be observed between write and newline/fsync. Only completed
    # lines are visible here; final composition requires the entire file untorn.
    if raw and not raw.endswith(b'\n'): raw = raw[:raw.rfind(b'\n') + 1] if b'\n' in raw else b''
    return [json.loads(line) for line in raw.splitlines()]

def source_check():
    C(H(Path(__file__)) == REG['script_sha256'], 'Registered independent observer source')
    for row in REG['bound_files']:
        C(H(R / row['path']) == row['sha256'], 'Exact registered identity: ' + row['path'])
    manifest = J(P / 'PREFIT_FREEZE_MANIFEST_V3.json')
    for i, row in enumerate(manifest['files']):
        C(H(R / row['path']) == row['sha256'], 'Exact V3 production/runtime/source: ' + row['path'])
        if i % 20 == 0: guard()
    for name, row in J(Q / 'SOURCE_PINS.json')['files'].items():
        C(H(R / name) == row['sha256'] and (R / name).stat().st_size == row['bytes'], 'Original protocol pin ' + name)
    for name, digest in J(FOUR / 'SOURCE_PINS.json')['files'].items():
        C(H(R / name) == digest, 'Original full source/provenance pin ' + name)
    for frozen in [OLD / 'PREFIT_FREEZE_MANIFEST.json', FOUR / 'PREFIT_FREEZE_MANIFEST.json']:
        for row in J(frozen)['files']:
            C(H(R / row['path']) == row['sha256'], 'Original producer source freeze ' + row['path'])
    C(subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip() == REG['execution_base'], 'Exact execution BASE')
    runtime = J(P / 'RUNTIME_IDENTITY.json')
    C(Path(sys.executable).resolve() == (R / runtime['runtime_executable']).resolve()
      and H(sys.executable) == runtime['python_launcher_sha256'], 'Actual pinned observer Python launcher')
    versions = {'Python': platform.python_version(), **{name: importlib.metadata.version(name) for name in ['numpy', 'scipy', 'h5py', 'requests']}}
    C(versions == runtime['versions'], 'Actual independent numerical arithmetic runtime')
    return versions

def state_files(folder):
    return {p.relative_to(R).as_posix(): {'path': p.relative_to(R).as_posix(), 'bytes': p.stat().st_size, 'sha256': H(p)}
            for p in folder.iterdir() if p.is_file()}

def get_preparation(task, preps, cache, features):
    key = task['mouse_id'] + '/' + task['panel']
    if key in cache: cache.move_to_end(key); return cache[key]
    prep = preps[key]
    C(prep['role'] == 'A', 'A-only saved preparation')
    z = OLD_HELPER.receipt(prep)
    C(np.all((z['ordinals'] >= 0) & (z['ordinals'] < 90)) and np.all(np.diff(z['ordinals']) > 0), 'Original A observations only')
    C(np.isfinite(z['raw']).all() and np.isfinite(z['y']).all(), 'Finite saved A features/counts')
    batch = features.Batch(**{k: z[k] for k in ['raw', 'y', 'ordinals', 'unit_ids', 'colors', 'running_missing', 'score_mask']},
                           dt=prep['dt'], psth=prep['psth'], b1=prep['b1'], role='A', panel=prep['panel'])
    scaler = features.Scaling(z['mean'], z['scale'], z['active'], prep['psth'])
    cache[key] = (prep, z, batch, scaler)
    if len(cache) > 2: cache.popitem(last=False)
    return cache[key]

def audit_new(task, terminal, initial_row, preps, cache, models, features):
    guard(); CONTEXT.update(stage='NEW_COMPLETED_STATE', task=task['id'])
    folder = P / 'work/fits' / hashlib.sha256(task['id'].encode()).hexdigest()
    C(terminal['task'] == task and terminal['result_path'] == (folder / 'RESULT.json').relative_to(R).as_posix(), 'Canonical new task/result path')
    before = state_files(folder)
    C(terminal['result_sha256'] == H(folder / 'RESULT.json'), 'Actual COMPLETED result bytes')
    result, attempt, client = [J(folder / name) for name in ['RESULT.json', 'ATTEMPT.json', 'CLIENT.json']]
    C(result['task'] == attempt['task'] == task and attempt['no_retry'] is True and not (folder / 'FAILURE.json').exists(), 'Complete new attempt identity, no failure/retry')
    initial = OLD_HELPER.receipt(attempt['bounds']); endpoint = OLD_HELPER.receipt(result['endpoint_state'])
    C(all(np.array_equal(client[k], initial[k]) for k in ['x0', 'lo', 'hi']), 'Actual client uses original initializer/bounds')
    prep, z, batch, scaler = get_preparation(task, preps, cache, features)
    unit = None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id'])
    lam = 1. if task['lambda'] == 'GLOBAL' else task['lambda']
    C(lam == 1., 'Original historical lambda1 only')
    objective = models.Objective(batch, scaler, task['model'], lam, unit, task['seed'])
    C(all(np.array_equal(initial[k], value) for k, value in [('x0', objective.x0), ('lo', objective.lo), ('hi', objective.hi)]), 'Original same-A/scaler/packing/seed initializer, never warm start')
    C(initial_row == {'task_id': task['id'], 'x0': ID(initial['x0']), 'lo': ID(initial['lo']), 'hi': ID(initial['hi']), 'origin': 'ORIGINAL_FROZEN_CONSTRUCTOR', 'no_warm_start': True}, 'Actual initializer journal matches independently reconstructed original')
    if task['id'] == '763236014:S02:S:None:11:GLOBAL':
        path = FOUR / 'work/fits' / folder.name / 'initial.npz'
        with np.load(path, allow_pickle=False) as original:
            C(all(np.array_equal(original[k], initial[k]) for k in ['x0', 'lo', 'hi']), 'Interrupted task preserved original initializer, not partial vector')
    d, coords, errors = OLD_HELPER.cert(folder)
    C(attempt['parameters'] == len(objective.x0) == d['free_coordinates'] and 0 < len(objective.x0) <= 368, 'Original parameter packing and resource ceiling')
    C(H(folder / 'DIAGNOSTICS.json') == result['diagnostic_state_sha256'], 'Complete original diagnostic hash binding')
    x, g = endpoint['x'], endpoint['gradient']
    C(np.array_equal(x, coords['endpoint_x']) and np.array_equal(g, coords['endpoint_analytic']) and np.array_equal(x, result['x']) and np.allclose(g, result['jac'], atol=1e-12, rtol=1e-12), 'Endpoint/certificate/result identity')
    C(np.all(x >= initial['lo'] - 1e-12) and np.all(x <= initial['hi'] + 1e-12), 'Original endpoint bounds')
    projected = OLD_HELPER.pg(x, g, initial['lo'], initial['hi'])
    C(projected == result['projected_gradient_inf'] == terminal['PG'] <= 1e-5 and result['numerical_pass'] is True, 'Independent outward PG and all frozen numerical gates')
    C(type(result['success']) is bool and isinstance(result['message'], str), 'Actual optimizer termination retained; success flag is not the gate')
    C(math.isfinite(result['objective']) and result['objective'] == result['fun'] and np.isclose(result['fun'], d['checkpoints'][-1]['objective'], atol=1e-10, rtol=1e-12), 'Same frozen objective/AD normalization certificate')
    fg, nit = OLD_HELPER.journals(folder, result, coords, initial, 'R4')
    C((folder / 'CLIENT_STDERR.log').stat().st_size == 0, 'No completed client stderr')
    after = state_files(folder); C(before == after, 'Every completed-state byte unchanged during independent audit')
    STATE_FILES.update(after)
    row = {'task': task, 'origin': 'R5', 'ftol': 0., 'status': 'INDEPENDENTLY_QUALIFIED_NEW_STATE',
           'result_path': terminal['result_path'], 'result_sha256': terminal['result_sha256'], 'initial_sha256': H(folder / 'initial.npz'),
           'coordinate_sha256': d['coordinate_state']['sha256'], 'endpoint_sha256': result['endpoint_state']['sha256'],
           'prepared_A_path': prep['path'], 'prepared_A_sha256': prep['sha256'], 'unit_identity': prep['arrays']['unit_ids'],
           'mask_identity': prep['arrays']['score_mask'], 'scaler_identities': {k: prep['arrays'][k] for k in ['mean', 'scale', 'active']},
           'parameter_count': len(objective.x0), 'PG': projected, 'AD_error_max': errors['AD'], 'fixed_FD_error_max': errors['FD'],
           'FG_pairs': fg, 'accepted_iterations': nit, 'FD_reserved': d['FD_objective_calls'], 'AD_reserved': d['AD_calls'],
           'analytic_checkpoint_reserved': d['analytic_checkpoint_calls'], 'objective': result['objective'],
           'optimizer_success': result['success'], 'termination': result['message'], 'new_evaluations': 0,
           'completed_receipt': terminal, 'initializer_identity': initial_row,
           'files': list(after.values())}
    append(E / 'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl', row)
    for key, value in [('new_states', 1), ('FG_pairs', fg), ('accepted_iterations', nit), ('FD_reserved', d['FD_objective_calls']), ('AD_reserved', 3), ('analytic_checkpoint_reserved', 3)]: COUNTS[key] += value
    guard(); return row

def journal_state(plan):
    rows = live_lines(P / 'results/FIT_JOURNAL.jsonl')
    active = None; attempted = []; complete = []
    for row in rows:
        if row['event'] == 'ATTEMPTED':
            C(active is None and len(attempted) < 2479 and row['task'] == plan[len(attempted)], 'Original ordered unique attempts without retry')
            C(row['ftol'] == 0. and row['initializer'] == 'ORIGINAL_FROZEN_ONLY', 'Frozen new optimizer policy')
            attempted.append(row['task']); active = row['task']
        else:
            C(row['event'] in ['COMPLETED', 'FAILED'] and active == row['task'], 'Exact active attempt/terminal join')
            if row['event'] == 'FAILED': return rows, attempted, complete, row
            complete.append(row); active = None
    return rows, attempted, complete, None

def final_composition(new_rows, plan, versions):
    CONTEXT.update(stage='FINAL_COMPLETE_M4_COMPOSITION', task=None); guard(); source_check()
    roots = J(P / 'INDEPENDENT_R5_PROTECTED_HASH_READBACK.json')['files']
    expected_r4 = {row['path'] for row in roots if row['path'].startswith('paper16_development_r4/')}
    actual_r4 = {f.relative_to(R).as_posix() for base in [FOUR / 'work', FOUR / 'results'] for f in base.rglob('*') if f.is_file()}
    C(actual_r4 == expected_r4, 'Exact unchanged original R4 protected union')
    for i, row in enumerate(roots):
        C(H(R / row['path']) == row['sha256'], 'Final fresh historical protected hash: ' + row['path'])
        if i % 200 == 0: guard()
    for i, row in enumerate(STATE_FILES.values()):
        C(H(R / row['path']) == row['sha256'], 'Final fresh new-state byte hash: ' + row['path'])
        if i % 100 == 0: guard()
    historical = J(P / 'INDEPENDENT_R5_OPTIMIZER_QUALIFICATION.json')['states']
    b0 = J(P / 'INDEPENDENT_R5_B0_QUALIFICATION.json')['states']
    full = J(OLD / 'results/TASK_PLAN.json')['tasks']
    C(len(new_rows) == 2479 and len(historical) == 3992 and len(b0) == 216 and len(full) == 6471, 'All mandatory composition denominators')
    byid = {row['task']['id']: row for row in historical + new_rows}
    C(len(byid) == 6471 and [byid[t['id']]['task'] for t in full] == full, 'Exact full original task coverage without substitution')
    freeze_path = P / 'results/M4_SELECTION_FREEZE.json'; freeze = J(freeze_path)
    C(freeze['selected_lambda'] == 1. and freeze['lambda_origin'] == 'HISTORICAL_R3_B1_SELECTION'
      and freeze['B0_count'] == 216 and freeze['all_original_thresholds_unchanged'] is True
      and freeze['E_authorized'] is False and freeze['Final_authorized'] is False
      and freeze['independent_M4_acceptance_pending'] is True, 'Frozen M4 selection and denied E/Final boundaries')
    expected_origins = [{'task_id': t['id'], 'origin': byid[t['id']]['origin'], 'result_path': byid[t['id']]['result_path'], 'result_sha256': byid[t['id']]['result_sha256']} for t in full]
    C(freeze['task_origins'] == expected_origins and freeze['task_plan_sha256'] == H(OLD / 'results/TASK_PLAN.json'), 'Exact 952R3+3040R4+2479R5 provenance origins')
    expected_groups = {(r['key'].split('/')[0], r['panel'], m) for r in J(OLD / 'results/A_PREPROCESSING_STATES.json') for m in ['D', 'S']}
    groups = collections.defaultdict(list)
    for t in full:
        if t['model'] in ['D', 'S']:
            result = J(R / byid[t['id']]['result_path'])
            groups[(t['mouse_id'], t['panel'], t['model'])].append({'seed': t['seed'], 'numerical_pass': result['numerical_pass'], 'objective': result['objective']})
    C(set(groups) == expected_groups, 'All D/S panel groups')
    selected = []
    for (mouse, panel, model), rows in sorted(groups.items()):
        C(sorted(row['seed'] for row in rows) == [11, 23, 37] and all(row['numerical_pass'] for row in rows), 'All three mandatory seeds independently pass')
        best = min(row['objective'] for row in rows); seed = min(row['seed'] for row in rows if row['objective'] <= best + 1e-12)
        selected.append({'mouse_id': mouse, 'panel': panel, 'model': model, 'all_seeds': rows, 'seed': seed})
    C(freeze['selected_seeds'] == selected, 'Original A penalized-objective seed selection/tie rule, no coefficient mean')
    expected = {}
    protected_by_folder = collections.defaultdict(list)
    for row in roots: protected_by_folder[(R / row['path']).parent].append(row)
    for row in historical + b0:
        folder = (R / row['result_path']).parent
        registered = protected_by_folder[folder]
        C({p for p in folder.iterdir() if p.is_file()} == {R / r['path'] for r in registered}, 'Only exact admitted historical folder members')
        expected.update({r['path']: r['sha256'] for r in registered})
    expected.update({name: row['sha256'] for name, row in STATE_FILES.items()})
    expected.update({row['path']: row['sha256'] for row in J(OLD / 'results/A_PREPROCESSING_STATES.json')})
    for path in [P / 'PREFIT_FREEZE_MANIFEST_V3.json', P / 'REUSE_ADMISSION.json', OLD / 'results/B_SELECTION.json', OLD / 'results/A_PREPROCESSING_STATES.json', OLD / 'results/PANEL_PREFIT_PLAN.json', P / 'results/FIT_JOURNAL.jsonl', P / 'results/INITIALIZER_IDENTITIES.jsonl', P / 'results/STAGE_CLAIM.json', P / 'results/SUPERVISOR.json']:
        expected[path.relative_to(R).as_posix()] = H(path)
    expected.update({row['path']: row['sha256'] for row in J(P / 'PREFIT_FREEZE_MANIFEST_V3.json')['files']})
    C(len(freeze['states']) == len({r['path'] for r in freeze['states']}) and {r['path']: r['sha256'] for r in freeze['states']} == expected, 'Exact complete M4 state/source/preprocessing/selection manifest')
    for i, row in enumerate(freeze['states']):
        C(H(R / row['path']) == row['sha256'], 'Full sealed state manifest fresh hash')
        if i % 100 == 0: guard()
    manifest_path = P / 'M4_REVIEW_MANIFEST.json'; manifest = J(manifest_path)
    C(manifest == {'files': [{'path': freeze_path.relative_to(R).as_posix(), 'sha256': H(freeze_path)}]}, 'Exact external M4 review manifest binding')
    C(J(P / 'results/M4_READY_FOR_INDEPENDENT_REVIEW.json') == {'all_new_fits_complete': True, 'E_not_accessed': True, 'deadline_unchanged': True}, 'Readiness is not independent acceptance')
    C(not (P / 'results/SCIENTIFIC_STOP.json').exists() and not (P / 'results/WORKER_COMPLETE.json').exists()
      and not (E / 'M4_APPROVAL.json').exists(), 'No premature acceptance or required STOP')
    raw = (P / 'results/FIT_JOURNAL.jsonl').read_bytes(); C(raw.endswith(b'\n'), 'Final untorn actual attempt journal')
    C((P / 'results/INITIALIZER_IDENTITIES.jsonl').read_bytes().endswith(b'\n')
      and live_lines(P / 'results/INITIALIZER_IDENTITIES.jsonl') == [row['initializer_identity'] for row in new_rows],
      'Exact full original initializer journal, no missing/extra/replaced rows')
    guard()
    result = {'mission': 'P16-M3-M5-SHUTDOWN-RECOVERY-R5', 'reviewer': '/root/r4_interruption_review',
              'completed_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'stage_claim_sha256': REG['stage_claim_sha256'],
              'script_sha256': H(Path(__file__)), 'all_new_2479_saved_states_independently_qualified': True,
              'historical_optimizer_admitted': 3992, 'R3': 952, 'R4': 3040, 'new_R5': 2479, 'full_optimizer_count': 6471, 'B0': 216,
              'historical_numerical_reaudit_executed': False, 'historical_fresh_hashes': len(roots),
              'new_state_fresh_hashes': len(STATE_FILES), 'M4_manifest_sha256': H(manifest_path), 'selection_freeze_sha256': H(freeze_path),
              'M4_full_state_manifest_files': len(freeze['states']), 'seed_groups': len(groups), 'counters': dict(COUNTS),
              'maxima': {key: max(row[field] for row in new_rows) for key, field in [('PG', 'PG'), ('AD', 'AD_error_max'), ('fixed_FD', 'fixed_FD_error_max')]},
              'runtime_versions': versions, 'new_objective_gradient_AD_FD_score_optimizer_calls': 0, 'new_neural_source_requests': 0,
              'E_access': False, 'Final_C_D_access': False, 'decision': 'COMPLETE_SAVED_M4_AUDIT_READY_FOR_FINAL_INDEPENDENT_REVIEW',
              'M4_APPROVAL_issued': False}
    once(E / 'INDEPENDENT_R5_M4_COMPLETE_SAVED_RESULT.json', result)
    print(json.dumps(result, indent=2), flush=True)

def main():
    global REG, OLD_HELPER
    REG = J(E / 'INDEPENDENT_R5_M4_REGISTRATION.json'); guard()
    once(E / 'INDEPENDENT_R5_M4_OBSERVER_CLAIM.json', {'pid': os.getpid(), 'script_sha256': H(Path(__file__)), 'registration_sha256': H(E / 'INDEPENDENT_R5_M4_REGISTRATION.json'), 'stage_claim_sha256': REG['stage_claim_sha256'], 'one_pass_no_restart': True})
    versions = source_check()
    OLD_HELPER = importlib.import_module(PREFIX + 'INDEPENDENT_R5_REUSE_AUDIT')
    from paper16_development_r5 import models, features
    from paper16_m1.code import spec, dynamics
    from scipy import optimize
    import requests
    with contextlib.ExitStack() as stack:
        for cls in [models.Objective, models.StationaryObjective]:
            for name in ['analytic', 'AD']: stack.enter_context(patch.object(cls, name, side_effect=deny))
        for name in ['score']: stack.enter_context(patch.object(models.Objective, name, side_effect=deny))
        for name in ['stationary', 'stationary_score', 'causal_score']: stack.enter_context(patch.object(models, name, side_effect=deny))
        for mod, names in [(spec, ['glm', 'independent_AD']), (dynamics, ['objective', 'independent_AD'])]:
            for name in names: stack.enter_context(patch.object(mod, name, side_effect=deny))
        stack.enter_context(patch.object(optimize, 'minimize', side_effect=deny))
        stack.enter_context(patch.object(socket.socket, 'connect', side_effect=deny)); stack.enter_context(patch.object(socket.socket, 'connect_ex', side_effect=deny))
        stack.enter_context(patch.object(socket, 'create_connection', side_effect=deny)); stack.enter_context(patch.object(requests.sessions.Session, 'request', side_effect=deny))
        plan = [r['task'] for r in J(Q / 'RECOVERY_TASK_PLAN.json')['tasks']]
        C(len(plan) == len({t['id'] for t in plan}) == 2479 and plan[0]['id'] == '763236014:S02:S:None:11:GLOBAL', 'Exact original ordered recovery plan')
        preps = {r['key']: r for r in J(OLD / 'results/A_PREPROCESSING_STATES.json')}; C(len(preps) == 215, 'Original complete saved A prep index')
        cache = collections.OrderedDict(); qualified = []
        while True:
            guard()
            if (P / 'results/SCIENTIFIC_STOP.json').exists():
                once(E / 'INDEPENDENT_R5_M4_OBSERVER_ROOT_STOP.json', {'recorded_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'root_stop': J(P / 'results/SCIENTIFIC_STOP.json'), 'qualified_new_states': len(qualified), 'counters': dict(COUNTS), 'later_states_audited': False, 'M4_APPROVAL_issued': False})
                print('ROOT_SCIENTIFIC_STOP_OBSERVED; no later state audit or approval.', flush=True); return
            rows, attempts, completed, failure = journal_state(plan)
            C(failure is None, 'Actual mandatory scientific FAILED attempt; no later audit')
            C(completed[:len(qualified)] == [r['completed_receipt'] for r in qualified], 'Previously qualified complete terminal prefix preserved')
            for terminal in completed[len(qualified):]:
                if (P / 'results/SCIENTIFIC_STOP.json').exists(): break
                initials = live_lines(P / 'results/INITIALIZER_IDENTITIES.jsonl')
                task = plan[len(qualified)]; matches = [row for row in initials if row['task_id'] == task['id']]
                C(len(matches) == 1, 'Exactly one original initializer journal identity')
                qualified.append(audit_new(task, terminal, matches[0], preps, cache, models, features))
                print(json.dumps({'independent_new_states_qualified': len(qualified), 'total': 2479, 'task': task['id'], 'PG': qualified[-1]['PG']}), flush=True)
                if len(qualified) % 100 == 0: source_check()
            if len(qualified) == 2479 and (P / 'results/M4_READY_FOR_INDEPENDENT_REVIEW.json').exists():
                C(len(attempts) == len(completed) == 2479, 'Every actual attempt complete exactly once')
                final_composition(qualified, plan, versions); return
            time.sleep(5.)

if __name__ == '__main__':
    try: main()
    except BaseException as exc:
        failure = {'recorded_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'context': CONTEXT,
                   'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc(), 'counters': dict(COUNTS),
                   'automatic_retry': False, 'later_states_audited_after_failure': False, 'M4_APPROVAL_issued': False}
        once(E / 'INDEPENDENT_R5_M4_AUDIT_FAILURE_1.json', failure)
        print(json.dumps(failure, indent=2), flush=True); raise
