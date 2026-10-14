"""Source-grounded test repair; no fit, mask, threshold or selection change."""
import shutil
import launch
import study as r
def main():
    phase='preflight_corrected'
    if (r.HERE/(phase+'_execution_registration.json')).exists():raise RuntimeError('NO_RETRY')
    a=launch.security();old=r.load(r.HERE/'preflight_execution_registration.json')
    code=r.HERE/'exports/code_preflight_corrected';shutil.copytree(r.HERE/'exports/code_preflight',code)
    for name in ('worker.py','selection.py','test_selection.py'):
        (code/name).unlink();shutil.copy2(r.HERE/name,code/name)
    a.protect(code);hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/(phase+'_execution_registration.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'phase':phase,'test_bug_repair':'Frozen manifest masks, not assumed 360/240 trial counts; unchanged conditions minimum24/16','new_fits':0,'parent_execution_registration_sha256':r.sha(r.HERE/'preflight_execution_registration.json'),'original_failure_receipt_sha256':r.sha(r.HERE/'results/preflight_launch_receipt.json'),'observability_failure_receipt_sha256':r.sha(r.HERE/'results/preflight_observed_launch_receipt.json'),'code_sha256':hashes,'source_sha256':{n:r.sha(r.HERE/n) for n in ('worker.py','selection.py','test_selection.py','corrected_preflight.py')},'AB_manifest_sha256':old['AB_manifest_sha256'],'runtime_sha256':old['runtime_sha256'],'protocol_sha256':r.sha(r.HERE/'PROTOCOL.md'),'final_access':False})
    launch.native(phase,r.HERE/'exports/development_AB',code,hashes,a)
if __name__=='__main__':main()
