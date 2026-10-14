"""Frozen full null-suite registration; no replacement suite or tuning."""
import shutil
import launch
import study as r
def main():
    phase='nulls'
    if (r.HERE/(phase+'_execution_registration.json')).exists():raise RuntimeError('NO_NULL_RETRY')
    gate=r.load(r.HERE/'results/science/native/gate_result.json');receipt=r.load(r.HERE/'results/science_launch_receipt.json')
    if gate['gate']!='PASS' or receipt['exit_code']!=0 or not receipt['role_proof_pass']:raise RuntimeError('CRITICAL_SCIENCE_STOP')
    a=launch.security();code=r.HERE/'exports/code_nulls';shutil.copytree(r.HERE/'exports/code_preflight_corrected',code)
    (code/'worker.py').unlink();shutil.copy2(r.HERE/'null_worker.py',code/'worker.py')
    for name in ('glm.py','nulls.py','test_nulls.py'):shutil.copy2(r.HERE/name,code/name)
    states=r.HERE/receipt['output_directory']/'primary_states.npz'
    if r.sha(states)!=gate['primary_states_sha256']:raise RuntimeError('EXACT_FROZEN_PRIMARY')
    shutil.copy2(states,code/'primary_states.npz');a.protect(code)
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()};old=r.load(r.HERE/'preflight_execution_registration.json')
    r.save(r.HERE/(phase+'_execution_registration.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_null_evaluation':True,'base':r.BASE,'code_sha256':hashes,'source_sha256':{n:r.sha(r.HERE/n) for n in ('glm.py','nulls.py','null_worker.py','run_nulls.py','test_nulls.py')},'AB_manifest_sha256':old['AB_manifest_sha256'],'runtime_sha256':old['runtime_sha256'],'protocol_registration_sha256':r.sha(r.HERE/'protocol_registration.json'),'science_gate_sha256':r.sha(r.HERE/'results/science/native/gate_result.json'),'primary_states_sha256':gate['primary_states_sha256'],'replicates':999,'new_fits':0,'final_access':False})
    launch.native(phase,r.HERE/'exports/development_AB',code,hashes,a)
if __name__=='__main__':main()
