"""Preserve failed controller receipt; certify saved synthetic states without refitting."""
import shutil
import study as r
from native import security,prepare_job,launch
def main():
    r.verify();a=security();original=r.HERE/'jobs/synthetic_C_1';output=next((original/'exports').glob('P12Analysis.*/output'))
    r.save(r.HERE/'results/synthetic_launch_failure.json',{'phase':'synthetic_C_1','host_exception':'TypeError: save() takes 2 positional arguments but 3 were given',
        'original_worker_gate':r.load(output/'gate_result.json'),'original_exit_code':'UNPUBLISHED','original_cleanup_hresult':'UNPUBLISHED',
        'state_output_directory':str(output.relative_to(r.HERE)),'new_scientific_retry_fits':0,
        'security_precondition_attempt':{'exception':'FileNotFoundError: results/synthetic_C.json','before_job_or_release':True}})
    job=prepare_job('synthetic_certificate_1');data=job/'exports/saved';shutil.copytree(r.HERE/'exports/synthetic_state_validation_1',data)
    r.save(data/'prior_execution.json',{'original_gate':r.load(output/'gate_result.json'),'original_oracles':r.load(output/'oracle_tests.json'),'original_role':r.load(output/'role_proof.json')})
    code=job/'exports/code';code.mkdir()
    for name,source in {'worker.py':r.HERE/'synthetic_certificate_worker.py','release_control.py':r.HERE/'release_control.py','native_analysis_check.py':r.OLD/'native_analysis_check.py'}.items():shutil.copy2(source,code/name)
    a.protect(data);a.protect(code)
    r.save(r.HERE/'synthetic_certificate_execution_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_execution':True,
        'source_sha256':{p.name:r.sha(p) for p in r.HERE.glob('*.py')},'code_sha256':{p.name:r.sha(p) for p in code.iterdir()},
        'data_sha256':{p.name:r.sha(p) for p in data.iterdir()},'new_fits':0,'original_exit_cleanup_unpublished':True})
    receipt,gate=launch('certificate',job,data,code)
    r.save(r.HERE/'results/synthetic_C.json',{'job':str(original.relative_to(r.HERE)),'state_output_directory':str(output.relative_to(r.HERE)),
        'original_receipt':'UNPUBLISHED; serialization failure retained','gate':r.load(output/'gate_result.json'),
        'certificate_job':str(job.relative_to(r.HERE)),'certificate_receipt':receipt,'certificate_gate':gate})
    if receipt['exit_code']!=0 or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000' or not gate or gate['gate']!='PASS':raise RuntimeError('FRESH_CERTIFICATE_GATE')
    print({'saved_synthetic_certificate':'PASS','new_fits':0,'original_exit_cleanup':'UNPUBLISHED'})
if __name__=='__main__':main()
