"""Register final numerical source before new GLM scientific evaluation."""
import shutil
import launch
import study as r
def main():
    phase='science'
    if (r.HERE/(phase+'_execution_registration.json')).exists():raise RuntimeError('NO_FIT_RETRY')
    gate=r.load(r.HERE/'results/preflight_corrected/native/gate_result.json')
    receipt=r.load(r.HERE/'results/preflight_corrected_launch_receipt.json')
    if gate['gate']!='PASS' or not gate['scientific_coverage_pass'] or receipt['exit_code']!=0 or not receipt['role_proof_pass']:raise RuntimeError('CRITICAL_PREFLIGHT_STOP')
    protocol=r.load(r.HERE/'protocol_registration.json')
    if r.sha(r.HERE/'PROTOCOL.md')!=protocol['protocol_sha256']:raise RuntimeError('FROZEN_PROTOCOL')
    a=launch.security();code=r.HERE/'exports/code_science';shutil.copytree(r.HERE/'exports/code_preflight_corrected',code)
    (code/'worker.py').unlink();shutil.copy2(r.HERE/'fit_worker.py',code/'worker.py')
    for name in ('glm.py','test_glm.py'):shutil.copy2(r.HERE/name,code/name)
    a.protect(code);hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()};old=r.load(r.HERE/'preflight_execution_registration.json')
    r.save(r.HERE/(phase+'_execution_registration.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_new_fits':True,'base':r.BASE,'code_sha256':hashes,'source_sha256':{n:r.sha(r.HERE/n) for n in ('glm.py','test_glm.py','fit_worker.py','run_science.py','selection.py')},'AB_manifest_sha256':old['AB_manifest_sha256'],'runtime_sha256':old['runtime_sha256'],'protocol_registration_sha256':r.sha(r.HERE/'protocol_registration.json'),'preflight_gate_sha256':r.sha(r.HERE/'results/preflight_corrected/native/gate_result.json'),'final_access':False,'no_fit_retries':True})
    launch.native(phase,r.HERE/'exports/development_AB',code,hashes,a)
if __name__=='__main__':main()
