"""One registered primary R5 admission pass. Saved arithmetic only, no scientific evaluation."""
import contextlib
import datetime as dt
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

import numpy as np

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
P = R / 'paper16_development_r5'
Q = R / 'paper16_shutdown_recovery_r5_protocol'
O = R / 'paper16_development_r3'
V = R / 'paper16_development_r4'
MISSION = 'P16-M3-M5-SHUTDOWN-RECOVERY-R5'
BASE = 'b7bb1227379462c2c7a1cef40ab0d0e99a6d020b'
ACTIVE = {'kind': 'BOOTSTRAP', 'id': None}
COUNTS = {'optimizer_attempted': 0, 'optimizer_passed': 0, 'B0_attempted': 0, 'B0_passed': 0}
HASHED = {}


def load(p):
    return json.loads(Path(p).read_bytes())


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def once(p, value):
    with Path(p).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def event(value):
    with (P/'PRIMARY_AUDIT_LEDGER.jsonl').open('a', encoding='utf8', newline='\n') as f:
        f.write(json.dumps(value, allow_nan=False)+'\n'); f.flush(); os.fsync(f.fileno())


def forbid(*a, **k):
    raise RuntimeError('R5_PRIMARY_SAVED_ONLY_DENIES_EVALUATION_OPTIMIZATION_SCORE_NETWORK')


def guard():
    now = dt.datetime.now(dt.timezone.utc)
    require(time.monotonic() <= CLAIM['deadline_monotonic'] and now <= dt.datetime.fromisoformat(CLAIM['deadline_UTC']), 'Original Phase A deadline')
    require(time.monotonic() >= CLAIM['start_monotonic'] and now >= dt.datetime.fromisoformat(CLAIM['start_UTC']), 'Phase A clock rollback')
    require(abs((now-dt.datetime.fromisoformat(CLAIM['start_UTC'])).total_seconds()-(time.monotonic()-CLAIM['start_monotonic'])) < 5, 'Phase A monotonic/UTC disagreement')


def identity(path, digest, size=None):
    guard(); path = Path(path); st = path.stat()
    # Within-this-pass cache is tied to immutable size/mtime and never loaded from disk.
    key = str(path.resolve())
    if key not in HASHED:
        HASHED[key] = (sha(path), st.st_size, st.st_mtime_ns)
    actual, n, stamp = HASHED[key]
    require(st.st_size == n and st.st_mtime_ns == stamp and actual == digest and (size is None or n == size), 'File identity: '+str(path.relative_to(R)))


def manifest(path):
    value = load(path)
    for row in value['files']:
        identity(R/row['path'], row['sha256'], row.get('bytes'))
    return value


def pins(path):
    for p, value in load(path)['files'].items():
        identity(R/p, value if isinstance(value, str) else value['sha256'], None if isinstance(value, str) else value.get('bytes'))


def journal(folder, result, coordinates, initial, prior, audit, origin):
    calls = prior.rows(folder/'CALLS.jsonl'); accepted = prior.rows(folder/'ACCEPTED.jsonl')
    n, nit = audit.exact_journal(folder, result, coordinates, initial)
    require(prior.call_prefix(calls, len(initial['x0'])) == (n, n), 'Complete saved FG vector journal')
    assoc = {}
    for pre, post in zip(calls[::2], calls[1::2]):
        require(pre['iterations'] <= nit and np.all(np.asarray(pre['x']) >= initial['lo']-1e-12) and np.all(np.asarray(pre['x']) <= initial['hi']+1e-12), 'FG bounds/counter')
        assoc[pre['iterations']] = (pre, post)
    for i, row in enumerate(accepted):
        require(i in assoc and np.array_equal(row['x'], assoc[i][0]['x']), 'Accepted iterate/FG association')
    if accepted:
        require(np.array_equal(accepted[-1]['x'], result['x']), 'Last accepted endpoint')
    require(assoc[nit-1 if accepted else 0][1]['objective'] == result['objective'], 'Endpoint objective/journal')
    if origin == 'R4':
        counts = prior.diagnostic_prefix(prior.rows(folder/'DIAGNOSTIC_CALLS.jsonl'), len(initial['x0']))
        require(counts == {'FD_RESERVED':24*len(initial['x0']), 'AD_RESERVED':3, 'ANALYTIC_RESERVED':3}, 'Full original R4 derivative reservation journal')
    return n, nit


def execute():
    global CLAIM
    CLAIM = load(P/'PHASE_A_CLAIM.json')
    require(CLAIM['mission'] == MISSION and CLAIM['phase'] == 'A_PREFLIGHT' and CLAIM['no_reset'] is True and CLAIM['new_real_A_optimization_authorized'] is False and CLAIM['E_authorized'] is False and CLAIM['Final_authorized'] is False, 'Original Phase A authority')
    require(abs((CLAIM['deadline_monotonic']-CLAIM['start_monotonic'])-86400) <= 1e-6, 'Original 24 hour cap')
    guard()
    boot = subprocess.check_output(['powershell','-NoProfile','-Command', '(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString("o")'], text=True).strip()
    require(abs((dt.datetime.fromisoformat(boot)-dt.datetime.fromisoformat(CLAIM['windows_boot_UTC'])).total_seconds()) < .001, 'Same original Windows boot')
    require(subprocess.check_output(['git','rev-parse','HEAD'], cwd=R, text=True).strip() == BASE, 'Execution BASE identity')
    registration = {'mission':MISSION, 'role':'PRIMARY_SAVED_ONLY_FULL_REUSE_AUDIT', 'registered_UTC':dt.datetime.now(dt.timezone.utc).isoformat(), 'script_path':Path(__file__).relative_to(R).as_posix(), 'script_sha256':sha(__file__), 'phase_claim_sha256':sha(P/'PHASE_A_CLAIM.json'), 'owner_request_sha256':sha(E/'OWNER_REQUEST.txt'), 'targets_sha256':sha(Q/'REUSE_TARGETS.json'), 'helper_sources':{p:sha(R/p) for p in ['paper16_development_r4/audit_saved.py','paper16_termination_feasibility1/reproduce.py']}, 'optimizer_targets':3992, 'B0_targets':216, 'one_primary_pass':True, 'stop_first_required_failure':True, 'new_objective_derivative_optimizer_score_calls':0, 'network_denied':True, 'constructor_only_initializer_verification':True, 'windows_boot_UTC':boot}
    once(E/'PRIMARY_AUDIT_REGISTRATION.json', registration)
    require(not (P/'PRIMARY_AUDIT_LEDGER.jsonl').exists(), 'Fresh primary ledger')
    event({'event':'STARTED', 'registration_sha256':sha(E/'PRIMARY_AUDIT_REGISTRATION.json')})
    ACTIVE.update(kind='INVENTORY', id=None)
    pins(Q/'SOURCE_PINS.json'); pins(V/'SOURCE_PINS.json'); pins(O/'SOURCE_PINS.json')
    for path in [O/'PROTECTED_STATE_MANIFEST.json', O/'PREFIT_FREEZE_MANIFEST.json', V/'PREFIT_FREEZE_MANIFEST.json']:
        manifest(path)
    first = manifest(V/'PROTECTED_STATE_MANIFEST.json'); sup = manifest(V/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json')
    require(sup['original_manifest_sha256'] == sha(V/'PROTECTED_STATE_MANIFEST.json'), 'Append-only R4 supplement binding')
    union = first['files']+sup['files']; names = [r['path'] for r in union]
    actual = {p.relative_to(R).as_posix() for d in [V/'work',V/'results'] for p in d.rglob('*') if p.is_file()}
    require(len(names) == len(set(names)) and set(names) == actual, 'Exact original plus supplement inventory union')
    # R3 has no separate runtime receipt; its source/prefit pins are verified above,
    # while the feasibility and R4 receipts bind the same retained numeric runtime.
    for path in [V/'RUNTIME_IDENTITY.json', R/'paper16_termination_feasibility1/RUNTIME_IDENTITY.json']:
        runtime = load(path)
        for p, digest in runtime['files'].items():identity(R/p, digest)
        identity(R/runtime['runtime_executable'], runtime['python_launcher_sha256'])
        require(runtime['versions']['Python'] == '.'.join(map(str,sys.version_info[:3])), 'Python runtime version')
        for name, version in runtime['versions'].items():
            if name != 'Python':require(importlib.metadata.version(name) == version, 'Runtime package version: '+name)
    from paper16_development_r4 import audit_saved as audit
    from paper16_termination_feasibility1 import reproduce as prior
    from paper16_development_r3 import models as models3, panels
    from paper16_development_r4 import models as models4
    from paper16_development_r3.core import spec, dynamics
    import scipy.optimize
    records = sorted([r for r in load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']], key=lambda r:int(r['source']['mouse_id']))
    require(len(records) == 27 and sum(r['source']['protocol']=='brain_observatory_1.1' for r in records) == 5, 'Original 27 mice 5 BO/22 FC')
    by_mouse = {r['source']['mouse_id']:r for r in records}
    plan = load(O/'results/TASK_PLAN.json'); require(plan == panels.task_plan(records,load(O/'results/PANEL_PREFIT_PLAN.json')) and len(plan['tasks'])==6471, 'Exact original full task plan')
    by_task = {t['id']:t for t in plan['tasks']}
    require(load(O/'results/B_SELECTION.json')['selected_lambda']==1.0 and load(O/'results/B_SELECTION.json')['selection_information']=='B1_UNPENALIZED_ONLY', 'Historical lambda only')
    targets = load(Q/'REUSE_TARGETS.json'); require(len(targets['optimizer_targets'])==3992 and len(targets['B0_targets'])==216, 'Registered target denominator')
    require(all(t['R5_admitted'] is False and t['R5_audit']=='NOT_EXECUTED' for t in targets['optimizer_targets']+targets['B0_targets']), 'No inherited new admission')
    require(len({t['task']['id'] for t in targets['optimizer_targets']})==3992 and sum(t['origin']=='R3' for t in targets['optimizer_targets'])==952 and sum(t['origin']=='R4' for t in targets['optimizer_targets'])==3040, 'Exact origins no duplicates')
    r3journal = prior.rows(O/'results/FIT_JOURNAL.jsonl'); r4journal = prior.rows(V/'results/FIT_JOURNAL.jsonl')
    require(sum(x['event']=='ATTEMPTED' for x in r3journal)==953 and sum(x['event']=='ATTEMPTED' for x in r4journal)==3041, 'Historical attempts retained')
    r4term = {x['task']['id']:x for x in r4journal if x['event']=='COMPLETED'}
    require(len(r4term)==3040 and {t['task']['id'] for t in targets['optimizer_targets'] if t['origin']=='R4'}==set(r4term), 'All and only completed R4 states')
    with contextlib.ExitStack() as stack:
        for mod in [models3,models4]:
            for cls in [mod.Objective,mod.StationaryObjective]:
                for name in ['analytic','AD','score']:
                    if hasattr(cls,name):stack.enter_context(patch.object(cls,name,side_effect=forbid))
            for name in ['stationary_score','causal_score']:stack.enter_context(patch.object(mod,name,side_effect=forbid))
        for mod,names0 in [(spec,['glm','independent_AD']),(dynamics,['objective','independent_AD']),(scipy.optimize,['minimize']),(socket.socket,['connect','connect_ex'])]:
            for name in names0:stack.enter_context(patch.object(mod,name,side_effect=forbid))
        states = audit.prepared_states(); require(len(states)==215, 'All original215 A preparations')
        optimizer=[]; b0=[]
        for target in targets['optimizer_targets']:
            guard(); task=target['task']; origin=target['origin']; ACTIVE.update(kind='OPTIMIZER',id=task['id']); COUNTS['optimizer_attempted']+=1
            event({'event':'STATE_ATTEMPTED','kind':'optimizer','task_id':task['id'],'index':COUNTS['optimizer_attempted']})
            require(by_task.get(task['id'])==task and target['historical_ftol']==(1e-12 if origin=='R3' else 0.0), 'Task and historical ftol')
            folder=(R/target['result_path']).parent
            require(folder==(O if origin=='R3' else V)/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest(), 'Original exact task folder')
            identity(folder/'RESULT.json',target['result_sha256']); result=load(folder/'RESULT.json'); attempt=load(folder/'ATTEMPT.json')
            require(result['task']==attempt['task']==task and attempt['no_retry'] is True and result['numerical_pass'] is True, 'Original accepted task identity')
            if origin=='R4':require(r4term[task['id']]['result_sha256']==target['result_sha256'] and r4term[task['id']]['result_path']==target['result_path'] and r4term[task['id']]['PG']==result['projected_gradient_inf'], 'R4 terminal journal binding')
            record=by_mouse[task['mouse_id']]; batch,scaler,prep=states[task['mouse_id']+'/'+task['panel']]
            unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id']); lam=1. if task['lambda']=='GLOBAL' else task['lambda']
            constructor=(models3 if origin=='R3' else models4).Objective(batch,scaler,task['model'],lam,unit,task['seed'])
            identity(folder/'initial.npz',attempt['bounds']['sha256'])
            with np.load(folder/'initial.npz',allow_pickle=False) as f:initial={k:f[k].copy() for k in f.files}
            require({k:audit.array_identity(v) for k,v in initial.items()}==attempt['bounds']['arrays'], 'Initial member identities')
            require(all(np.array_equal(initial[k],v) for k,v in [('x0',constructor.x0),('lo',constructor.lo),('hi',constructor.hi)]), 'Exact original initializer/free-coordinate packing/bounds')
            diag,coord,ad,fd=audit.coordinate_checks(folder)
            identity(folder/'DIAGNOSTICS.json',result['diagnostic_state_sha256']);identity(R/result['endpoint_state']['path'],result['endpoint_state']['sha256'])
            require(R/result['endpoint_state']['path']==folder/'endpoint.npz' and R/diag['coordinate_state']['path']==folder/'coordinate_certificates.npz', 'Certificate in exact state folder')
            with np.load(folder/'endpoint.npz',allow_pickle=False) as f:end={k:f[k].copy() for k in f.files}
            require({k:audit.array_identity(v) for k,v in end.items()}==result['endpoint_state']['arrays'], 'Endpoint member identity')
            x,g=coord['endpoint_x'],coord['endpoint_analytic']; require(np.array_equal(end['x'],x) and np.array_equal(end['gradient'],g) and np.array_equal(result['x'],x) and np.allclose(result['jac'],g,atol=1e-12,rtol=1e-12), 'Identical full endpoint')
            for name in ['initial','halfway','endpoint']:require(np.all(coord[name+'_x']>=initial['lo']-1e-12) and np.all(coord[name+'_x']<=initial['hi']+1e-12), 'All checkpoint bounds')
            pg=float(np.abs(audit.projected(x,g,initial['lo'],initial['hi'])).max());require(pg==result['projected_gradient_inf'] and pg<=1e-5, 'Frozen full outward PG')
            require(result['success'] is True and result['message']=='CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL', 'Original actual gradient termination')
            require(math.isfinite(result['objective']) and result['objective']==result['fun'] and np.isclose(result['fun'],diag['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12), 'Saved identical objective/checkpoint')
            calls,nit=journal(folder,result,coord,initial,prior,audit,origin)
            row={'task':task,'origin':origin,'historical_ftol':target['historical_ftol'],'status':'PASS','R5_admitted':False,'admission_pending_independent_review':True,'session_id':record['source']['session_id'],'probe_id':record['source']['probe_id'],'original_source':record['source'],'lambda_used':lam,'prepared_A':prep,'parameter_count':len(x),'free_coordinate_identity':audit.array_identity(constructor.free),'column_identity':audit.array_identity(constructor.columns),'result_path':target['result_path'],'result_sha256':target['result_sha256'],'initial_sha256':sha(folder/'initial.npz'),'coordinate_sha256':diag['coordinate_state']['sha256'],'endpoint_sha256':result['endpoint_state']['sha256'],'PG':pg,'AD_error_max':ad,'fixed_FD_error_max':fd,'objective':result['objective'],'FG_calls':calls,'accepted_iterations':nit,'termination':result['message'],'three_saved_checkpoints':True,'all_saved_coordinates_checked':True,'original_mathematics_source_pins_verified':True,'counterfactual_execution_equivalence_claimed':False}
            optimizer.append(row);COUNTS['optimizer_passed']+=1;event({'event':'STATE_PASS','kind':'optimizer','task_id':task['id'],'result_sha256':target['result_sha256']})
            if COUNTS['optimizer_passed']%100==0:print(json.dumps(COUNTS),flush=True)
        for target in targets['B0_targets']:
            guard(); mouse=target['mouse_id']; uid=target['unit_id'];ACTIVE.update(kind='B0',id=f'{mouse}:{uid}');COUNTS['B0_attempted']+=1;event({'event':'STATE_ATTEMPTED','kind':'B0','mouse_id':mouse,'unit_id':uid})
            require(target['origin']=='R3_ANALYTIC' and target['historical_ftol'] is None,'B0 analytic origin')
            folder=O/'work/B0'/mouse/str(uid); require(R/target['result_path']==folder/'RESULT.json','Exact B0 folder');identity(folder/'RESULT.json',target['result_sha256'])
            batch,scaler,prep=states[mouse+'/MAIN'];unit=batch.unit_ids.tolist().index(uid);result=load(folder/'RESULT.json');diag,coord,ad,fd=audit.coordinate_checks(folder)
            expected=models3.StationaryObjective(batch,unit).x0
            require(all(np.array_equal(coord[name+'_x'],expected) for name in ['initial','halfway','endpoint']),'B0 identical analytic MLE labels')
            pg=float(np.abs(audit.projected(expected,coord['endpoint_analytic'],np.array([-10.]),np.array([10.]))).max())
            require(result['unit_id']==uid and result['analytic_MLE_not_optimizer_attempt'] is True and result['numeric_pass'] is True and result['projected_gradient_inf']==pg<=1e-5,'B0 original certificate gate')
            row={**target,'status':'PASS','admission_pending_independent_review':True,'prepared_A':prep,'session_id':by_mouse[mouse]['source']['session_id'],'probe_id':by_mouse[mouse]['source']['probe_id'],'coordinate_sha256':diag['coordinate_state']['sha256'],'PG':pg,'AD_error_max':ad,'fixed_FD_error_max':fd,'optimizer_attempt':False,'all_saved_coordinates_checked':True}; b0.append(row);COUNTS['B0_passed']+=1;event({'event':'STATE_PASS','kind':'B0','mouse_id':mouse,'unit_id':uid,'result_sha256':target['result_sha256']})
    guard(); require(COUNTS=={'optimizer_attempted':3992,'optimizer_passed':3992,'B0_attempted':216,'B0_passed':216},'Complete all-or-STOP denominator')
    once(P/'PRIMARY_OPTIMIZER_MATRIX.json',{'mission':MISSION,'states':optimizer})
    once(P/'PRIMARY_B0_MATRIX.json',{'mission':MISSION,'states':b0})
    summary={'mission':MISSION,'completed_UTC':dt.datetime.now(dt.timezone.utc).isoformat(),'primary_saved_audit':'PASS','independent_review_pending':True,**COUNTS,'full_current_pass_hashed_files':len(HASHED),'R4_inventory_union_files':len(names),'prepared_A_states':len(states),'new_optimizer_objective_derivative_score_calls':0,'new_raw_source_requests':0,'E_Final_access':False,'registration_sha256':sha(E/'PRIMARY_AUDIT_REGISTRATION.json'),'matrix_sha256':sha(P/'PRIMARY_OPTIMIZER_MATRIX.json'),'B0_matrix_sha256':sha(P/'PRIMARY_B0_MATRIX.json'),'ledger_sha256':sha(P/'PRIMARY_AUDIT_LEDGER.jsonl'),'old_failures_preserved':True}
    once(P/'PRIMARY_AUDIT_RESULT.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    try:
        with patch.object(socket.socket,'connect',side_effect=forbid),patch.object(socket.socket,'connect_ex',side_effect=forbid):execute()
    except BaseException as exc:
        stop={'mission':MISSION,'stop':'STOP_REUSE_REQUIRED_GATE','UTC':dt.datetime.now(dt.timezone.utc).isoformat(),'active':ACTIVE,'counts':COUNTS,'error_type':type(exc).__name__,'message':str(exc),'remaining_optimizer_unattempted':3992-COUNTS['optimizer_attempted'],'remaining_B0_unattempted':216-COUNTS['B0_attempted'],'later_scientific_audit_stopped':True,'no_retry_or_recalculation':True}
        if not (P/'PRIMARY_AUDIT_STOP.json').exists():once(P/'PRIMARY_AUDIT_STOP.json',stop)
        print(json.dumps(stop,indent=2),flush=True);traceback.print_exc();raise
