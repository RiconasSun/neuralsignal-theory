"""Synthetic and public saved-evidence replay; no real fit/input access."""
import os
import re
import subprocess
import sys
import math
import study as r
from audit_saved import check_endpoint,sha_vector
def main():
    manifest=r.load(r.HERE/'final_manifest.json');before=r.sha(r.HERE/'final_manifest.json')
    for name,digest in manifest['sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FINAL_PUBLIC_CANDIDATE_CHANGED:'+name)
    protocol=r.load(r.HERE/'candidate_protocol.json');scale=r.load(r.HERE/'results/audit/native/scale.json');S=scale['S']
    if len(S)!=384 or sha_vector(S)!=protocol['S_sha256'] or protocol['initial_theta_sha256']!=scale['initial_theta_sha256']:raise RuntimeError('COMMON_INITIAL_SCALE')
    expected=[min(1e4,max(1e-4,1/math.sqrt(max(abs(v),1e-6)))) for v in scale['source_diagonal']]
    if any(not math.isclose(a,b,rel_tol=1e-14,abs_tol=1e-14) for a,b in zip(expected,S)):raise RuntimeError('REGISTERED_SCALE_FORMULA')
    feasible=[];total=0
    for phase in ('audit','A','B','C'):
        public=r.HERE/f'results/{phase}/native';receipt=r.load(r.HERE/f'results/{phase}_launch_receipt.json');proof=r.load(public/'role_proof.json');gate=r.load(public/'gate_result.json');binding=r.load(public/'input_binding.json')
        if receipt['exit_code']!=0 or receipt['timed_out'] or receipt['profile_cleanup_hresult']!='0x00000000' or not receipt['role_proof_pass'] or not proof['pass'] or proof['capability_count']!=0 or gate['gate']!='PASS':raise RuntimeError('COMPLETE_NATIVE_ROLE_PROCESS_GATE:'+phase)
        if binding['validation_access'] or binding['final_access'] or binding['M3_refits'] or binding['offset_refits']:raise RuntimeError('SCIENTIFIC_SCOPE')
        if phase=='audit':
            if gate['new_optimization_fits']!=0 or gate['Hessian_gradient_calls']!=1536:raise RuntimeError('AUDIT_BUDGET')
            canonical=binding
            old=r.load(r.GRAD/'results/diagnostic/native/reproduction.json')
            reference={'training_array_sha256':old['training_array_sha256'],'context_sha256':old['context_sha256'],'offset_sha256':old['offset_sha256'],'A_manifest_sha256':old['data_manifest_sha256'],'data_file_sha256':old['data_file_sha256']}
            if any(canonical[k]!=v for k,v in reference.items()):raise RuntimeError('ORIGINAL_FAILURE_INPUT_IDENTITY')
        else:
            if binding!=canonical:raise RuntimeError('IDENTICAL_INPUTS_FOR_ALL')
            endpoint=r.load(public/'endpoint.json');history=r.load(public/'termination_history.json');policy=next(z for z in protocol['candidates'] if z['id']==phase)
            passed=check_endpoint(endpoint,history,policy,S)
            if passed!=gate['feasible'] or gate['new_optimization_candidates']!=1:raise RuntimeError('ENDPOINT_GATE_CHANGED')
            feasible.append(passed);total+=history['call_count']
    if total>24500:raise RuntimeError('TOTAL_BUDGET')
    outcome='OPTIMIZER_FEASIBILITY' if any(feasible) else 'OPTIMIZATION_INCONCLUSIVE'
    if r.load(r.HERE/'results/study_outcome.json')['scientific_outcome']!=outcome:raise RuntimeError('STUDY_OUTCOME')
    logs=[];counts=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    # Re-executes only small synthetic oracles, including exact policy configs.
    for pattern in ('test_conditioning.py','test_registered_policies.py','test_saved_audit.py'):
        process=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p',pattern,'-v'],capture_output=True,text=True,env=env)
        log=process.stdout+process.stderr
        if process.returncode or 'skipped=' in log:raise RuntimeError('REGRESSION_REPLAY:'+pattern)
        counts.append(int(re.search(r'Ran (\d+) tests?',log)[1]));logs.append((pattern,log))
    if counts!=[17,3,11] or r.sha(r.HERE/'final_manifest.json')!=before:raise RuntimeError('REPLAY_COUNTS_MANIFEST')
    target=r.HERE/'replay'/r.datetime.now(r.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');target.mkdir(parents=True,exist_ok=False)
    for name,log in logs:(target/(name+'.log')).write_text(log,encoding='utf-8')
    r.save(target/'receipt.json',{'passed':True,'utc':r.datetime.now(r.timezone.utc).isoformat(),'manifest_sha256':before,'synthetic_structural_tests':17,'exact_registered_policy_synthetic_tests':3,'saved_corruption_tests':11,'candidate_count':3,'real_objective_gradient_calls':total,'new_real_trials':0,'protected_neural_or_states_read':False,'scientific_outcome':outcome,'historical_failures_unchanged':True,'live_native_isolation_repeated':False})
    print('SAVED_REPRODUCTION_PASS',outcome,'tests31','new_real_trials0','receipt',target/'receipt.json')
if __name__=='__main__':main()
