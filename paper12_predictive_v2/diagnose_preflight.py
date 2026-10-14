"""Observability-only no-fit replay; preserve failed first attempt byte-for-byte."""
import shutil
import launch
import study as r
def main():
    phase='preflight_observed'
    if (r.HERE/(phase+'_execution_registration.json')).exists():raise RuntimeError('NO_RETRY')
    a=launch.security();old=r.load(r.HERE/'preflight_execution_registration.json')
    code=r.HERE/'exports/code_preflight_observed';shutil.copytree(r.HERE/'exports/code_preflight',code)
    # Only newly added exception capture; no scientific computation changes.
    (code/'worker.py').unlink();shutil.copy2(r.HERE/'worker.py',code/'worker.py');a.protect(code)
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/(phase+'_execution_registration.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'phase':phase,'observability_only':True,'before_new_scientific_evaluation':True,'new_fits':0,'failed_attempt_receipt_sha256':r.sha(r.HERE/'results/preflight_launch_receipt.json'),'parent_execution_registration_sha256':r.sha(r.HERE/'preflight_execution_registration.json'),'code_sha256':hashes,'AB_manifest_sha256':old['AB_manifest_sha256'],'runtime_sha256':old['runtime_sha256'],'final_access':False})
    launch.native(phase,r.HERE/'exports/development_AB',code,hashes,a)
if __name__=='__main__':main()
