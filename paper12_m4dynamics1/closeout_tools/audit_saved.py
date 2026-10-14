"""Stdlib-only saved-evidence audit. No neural arrays, models or derivatives."""
import argparse
import csv
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ['mouse_id','session_id','region','family','size','ridge','seed','converged','optimizer_message','iterations','objective_calls','projected_gradient','gradient_inf','bound_hits','parameter_count','elapsed_seconds']

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1048576), b''):
            h.update(part)
    return h.hexdigest()

def require(condition, label):
    if not condition:
        raise ValueError(label)

def identity(row):
    return tuple(row[k] for k in ('mouse_id','session_id','region','family','size','ridge','seed'))

def roster():
    return [('744912849','766640955',region,family,size,ridge,seed)
        for region in ('CA1','DG')
        for family,sizes in (('Discrete',(2,3,4)),('Continuous',(1,2,4)),('Hybrid',(2,3,4)))
        for size in sizes for ridge in (.001,.01,.1,1.) for seed in (11,23,37)]

def validate_rows(rows, phase):
    count = 216 if phase == 'diagnosis' else 61
    require(len(rows) == count, 'EXACT_ROW_COUNT')
    ids = [identity(row) for row in rows]
    require(ids == roster()[:count] and len(set(ids)) == count, 'EXACT_ORDERED_ROSTER')
    for row in rows:
        finite = all(math.isfinite(row[k]) for k in ('penalized_training_objective','projected_gradient'))
        require(row['converged'] == bool(row['optimizer_success'] and finite and row['projected_gradient'] <= .001), 'CONVERGENCE_INCONSISTENT')
        require(row['validation_access'] is False and row['final_access'] is False, 'FORBIDDEN_ACCESS')
        if phase == 'diagnosis':
            require(row['original_replay_match'] is True, 'ORIGINAL_REPLAY_MISMATCH')
    expected = 6 if phase == 'diagnosis' else 59
    require(sum(row['converged'] for row in rows) == expected, 'CONVERGED_COUNT')
    if phase == 'smoke':
        failed = [(row['family'],row['size'],row['ridge'],row['seed']) for row in rows if not row['converged']]
        require(failed == [('Continuous',2,.001,11),('Continuous',4,.001,11)], 'FAILED_IDENTITIES')
        row = rows[-1]
        require(row['iterations'] == 2000 and row['optimizer_success'] is False, 'FROZEN_SOLVER_FAILURE')
        require(row['projected_gradient'] == .692604771056502 and row['bound_hits'] == 0, 'FROZEN_PG_BOUNDS')
        require('ITERATIONS REACHED LIMIT' in row['optimizer_message'], 'FROZEN_TERMINATION')
        check = row['terminal_gradient_check']
        require(check['scaled_gradient_error'] == .00020676306270142608 and check['passed'] is False, 'FROZEN_GRADIENT_FAILURE')
        require(sum(not row['terminal_gradient_check']['passed'] for row in rows) == 1, 'GRADIENT_FAILURE_COUNT')
    return count, expected

def validate_completion(gate, receipt, proof, oracles, phase):
    expected_gate, expected_exit = ('PASS',0) if phase == 'diagnosis' else ('FAIL',2)
    require(gate['gate'] == expected_gate and receipt['exit_code'] == expected_exit, 'NATIVE_EXIT_GATE')
    require(receipt['timed_out'] is False and receipt['profile_cleanup_hresult'] == '0x00000000' and receipt['role_proof_pass'] is True, 'INCOMPLETE_RECEIPT')
    require(receipt['final_values_exposed_to_analysis'] is False and receipt['final_holdout_evaluated'] is False, 'FINAL_EXPOSURE')
    require(proof['pass'] is True and proof['is_appcontainer'] is True and proof['capability_count'] == 0, 'ROLE_PROOF')
    require(oracles['count'] == 6 and oracles['passed'] is True and not oracles['failures'] and not oracles['errors'], 'SAVED_ORACLE_RESULT')
    require(gate['validation_access'] is False and gate['final_access'] is False, 'GATE_ACCESS')

def render(rows):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=COLUMNS, extrasaction='ignore')
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue().encode('utf-8')

def validate_phase(root, phase):
    folder = root / 'results' / phase / 'native'
    summary = load(folder/'summary.json'); rows = summary['rows']
    counts = validate_rows(rows, phase)
    gate = load(folder/'gate_result.json'); receipt = load(root/'results'/f'{phase}_launch_receipt.json')
    proof = load(folder/'role_proof.json'); oracles = load(folder/'oracle_tests.json')
    validate_completion(gate, receipt, proof, oracles, phase)
    require(gate['completed_fit_count'] == counts[0] and gate['converged_fit_count'] == counts[1], 'GATE_COUNTS')
    for row in rows:
        name = f"{row['region']}_{row['family']}_{row['size']}_{row['ridge']}_{row['seed']}.json"
        require(load(folder/name) == row, 'INDIVIDUAL_ROW_MISMATCH:' + name)
    if phase == 'smoke':
        failure = load(folder/'numerical_failure.json')
        require(failure['stage'] == 'terminal_before_next_fit' and failure['check'] == rows[-1]['terminal_gradient_check'], 'FAILURE_CHECK_BINDING')
        require(failure['identity'] == {k:rows[-1][k] for k in ('region','family','size','ridge','seed')}, 'FAILURE_IDENTITY_BINDING')
        require(gate['scientific_verdict'] == 'NUMERICAL_INCONCLUSIVE' and gate['gradient_failures'] == 1 and gate['failure'] == 'INDEPENDENT_NUMERICAL_CHECK_FAILED', 'SCIENTIFIC_STOP_CHANGED')
    bindings = {name:sha(path) for name,path in {'gate':folder/'gate_result.json','receipt':root/'results'/f'{phase}_launch_receipt.json','proof':folder/'role_proof.json','oracles':folder/'oracle_tests.json','summary':folder/'summary.json'}.items()}
    return rows, bindings

def audit(root, evidence):
    repo = root.parent
    original = load(evidence/'original_inventory.json')['original_sha256']
    narratives = {'MILESTONE_STATUS.md','CLAIM_AUDIT.md','ROOT_CAUSE.md'}
    for name, digest in original.items():
        path = repo/name
        if path.parent == root and path.name in narratives:
            path = root/'closeout_originals'/path.name
        require(sha(path) == digest, 'ORIGINAL_BYTES_CHANGED:' + name)
    prior = load(root/'registration.json')['prior_sha256']
    for name, digest in prior.items():
        path = repo/name
        if name == 'ops/daily-operations.md' and (root/'closeout_originals/ops_daily_operations.md').exists():
            original_ops = root/'closeout_originals/ops_daily_operations.md'
            require(path.read_bytes().endswith(original_ops.read_bytes()), 'OPS_HISTORY_NOT_EXACT_SUFFIX')
            path = original_ops
        require(sha(path) == digest, 'PRIOR_BYTES_CHANGED:' + name)
    for name,digest in load(root/'implementation_registration3.json')['sha256'].items():
        require(sha(root/name) == digest, 'REGISTERED_SOURCE_CHANGED:' + name)
    repair = load(root/'harness_repair_registration.json')
    for name,digest in repair['sha256'].items():
        require(sha(root/name) == digest, 'REPAIR_BINDING_CHANGED:' + name)
    original_oracle = root/'oracle_v1.py.txt'
    require(sha(original_oracle) == load(root/'registration.json')['implementation_sha256']['paper12_m4dynamics1/oracle.py'], 'ORIGINAL_ORACLE_BINDING')
    require(original_oracle.read_bytes().replace(b"('Hybrid',(2,3,4)):\n",b"('Hybrid',(2,3,4))):\n",1) == (root/'oracle.py').read_bytes(), 'EXACT_REPAIR')
    reports = {}; tables = {}
    for phase in ('diagnosis','smoke'):
        rows,bindings = validate_phase(root,phase)
        tables[phase] = render(rows)
        name = 'diagnosis_216_fit_table.csv' if phase == 'diagnosis' else 'smoke_61_fit_table.csv'
        require((root/name).read_bytes() == tables[phase], 'CSV_PARITY:' + name)
        reports[phase] = dict(completed=len(rows),converged=sum(r['converged'] for r in rows),bindings=bindings)
    amendment = load(root/'optimizer_amendment.json')
    require(amendment['diagnosis_bindings'] == reports['diagnosis']['bindings'], 'AMENDMENT_BINDINGS')
    require(amendment['options'] == dict(ftol=1e-10,gtol=1e-5,maxiter=2000,maxfun=80000), 'OPTIONS_CHANGED')
    require(amendment['before_new_fits'] is True and amendment['no_validation_guidance'] is True, 'AMENDMENT_TIMING')
    for phase in ('diagnosis','smoke'):
        reg = load(root/f'{phase}_execution_registration.json')
        require(reg['before_real_fits'] is True and reg['final_access'] is False and reg['validation_access'] is False, 'EXECUTION_SCOPE')
        require(reg['controller_sha256'] == sha(root/'launch.py'), 'EXECUTION_CONTROLLER')
    diagnosis_reg = load(root/'diagnosis_execution_registration.json')
    smoke_reg = load(root/'smoke_execution_registration.json')
    preparation = load(root/'results/preparation_receipt.json')
    require(diagnosis_reg['preceding_bindings'] is None and smoke_reg['preceding_bindings'] == reports['diagnosis']['bindings'], 'EXECUTION_PRECEDING_BINDINGS')
    require(diagnosis_reg['A_manifest_sha256'] == smoke_reg['A_manifest_sha256'] == preparation['A_manifest_sha256'], 'A_MANIFEST_BINDING')
    require(diagnosis_reg['runtime_sha256'] == smoke_reg['runtime_sha256'] == preparation['runtime_sha256'], 'RUNTIME_BINDING')
    archived = load(repo/'paper12_m4offset1/M4_registration.json')['code_sha256']
    offset_gate = load(repo/'paper12_m4offset1/results/full/native/gate_result.json')
    require(offset_gate['records_sha256'] == sha(repo/'paper12_m4offset1/results/full/native/offset_records.json'), 'OFFSET_RECORD_BINDING')
    for phase,reg in (('diagnosis',diagnosis_reg),('smoke',smoke_reg)):
        code = reg['code_sha256']
        for name in ('worker.py','roster.py','original_training_diagnostics.json','test_oracle.py','test_hybrid_history.py'):
            require(code[name] == sha(root/name), 'EXECUTION_SOURCE:' + name)
        for name in ('model_math.py','predictive_models.py','predictive_models_code1.py','r2_models.py','baseline_features.py','frozen_offset.py','impossibility.py','native_analysis_check.py'):
            require(code[name] == archived[name], 'ARCHIVED_MODEL_SOURCE:' + name)
        require(code['offset_records.json'] == offset_gate['records_sha256'] and code['offset_states.npz'] == offset_gate['state_sha256'], 'OFFSET_STATE_BINDING')
        oracle_name = 'oracle.py' if phase == 'diagnosis' else 'oracle_cached.py'
        require(code['oracle.py'] == sha(root/oracle_name), 'EXECUTION_ORACLE')
        if phase == 'smoke': require(code['oracle_original.py'] == sha(root/'oracle.py'), 'ORIGINAL_ORACLE_COPY')
    adapter = load(root/'smoke_adapter_registration.json')
    require(adapter['adapter_sha256'] == sha(root/'launch_smoke.py') and adapter['original_launcher_sha256'] == sha(root/'launch.py'), 'SMOKE_ADAPTER_CHANGED')
    require(adapter['before_new_fits'] is True and adapter['final_access'] is False and adapter['diagnostic_bindings'] == reports['diagnosis']['bindings'], 'ADAPTER_PRECEDING_BINDINGS')
    require(adapter['optimizer_amendment_sha256'] == sha(root/'optimizer_amendment.json') and adapter['cache_registration_sha256'] == sha(root/'cache_registration2.json'), 'ADAPTER_AMENDMENT_CACHE')
    cache = load(root/'cache_registration2.json')
    for name,digest in cache['sha256'].items(): require(sha(root/name) == digest, 'CACHE_SOURCE:' + name)
    protocol = load(root/'protocol.json')
    require(protocol['convergence'] == dict(projected_gradient_max=.001,optimizer_success_required=True,finite_required=True,bounds=[-8,8]), 'FROZEN_CONVERGENCE')
    require(protocol['numerical_checks']['gradient_scaled_error_limit'] == 1e-5 and protocol['numerical_checks']['forward_absolute_error_limit'] == 1e-10 and protocol['numerical_checks']['finite_difference_step'] == 1e-5, 'FROZEN_NUMERICAL_THRESHOLDS')
    require(protocol['conditional_amendment']['maxiter'] == 2000 and protocol['conditional_amendment']['maxfun'] == 80000 and protocol['conditional_amendment']['ftol'] == 1e-10 and protocol['conditional_amendment']['gtol'] == 1e-5, 'FROZEN_AMENDMENT_OPTIONS')
    manifest = root/'closeout_manifest.json'; manifest_hash = sha(manifest)
    for name,digest in load(manifest)['sha256'].items():
        require(sha(repo/name) == digest, 'CANDIDATE_CHANGED:' + name)
    return reports,tables,manifest_hash

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--prepare',action='store_true')
    args = parser.parse_args(); root = Path(__file__).resolve().parent.parent
    evidence = root.parent/'ops/evidence/2026-10-13/p12-m4-dynamics-numerical-recovery-1-closeout'
    if args.prepare:
        rows,_ = validate_phase(root,'smoke')
        with (root/'smoke_61_fit_table.csv').open('xb') as f: f.write(render(rows))
        print('SAVED_TABLE_PREPARED',len(rows)); return
    reports,tables,before = audit(root,evidence)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = root/'closeout_replay'/stamp; out.mkdir(parents=True,exist_ok=False)
    for phase,data in tables.items(): (out/(phase+'.csv')).write_bytes(data)
    require(sha(root/'closeout_manifest.json') == before, 'MANIFEST_CHANGED_DURING_REPLAY')
    receipt = dict(utc=stamp,passed=True,candidate_manifest_sha256=before,phases=reports,attempted=61,completed=61,converged=59,nonconverged=2,unexecuted=155,evidenced_interrupted=0,new_fits=0,gradient_experiments=0,neural_access=False,final_access=False,historical_scientific_verdict='NUMERICAL_INCONCLUSIVE')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('SAVED_ONLY_AUDIT_PASS diagnosis=216/6 smoke=61/59 unexecuted=155 receipt='+str(out/'receipt.json'))

if __name__ == '__main__': main()
