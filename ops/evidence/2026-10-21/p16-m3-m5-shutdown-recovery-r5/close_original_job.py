"""Close only the original frozen R5 Job after verified native process loss."""
import ctypes
import datetime
import hashlib
import json
import os
from pathlib import Path

R=Path(__file__).resolve().parents[4]
P=R/'paper16_development_r5'
E=Path(__file__).resolve().parent

def load(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def once(p,v):
    with p.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(v,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())

if __name__=='__main__':
    supervisor=load(P/'results/SUPERVISOR.json')
    stage_sha=sha(P/'results/STAGE_CLAIM.json')
    evidence=load(E/'ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json')
    assert stage_sha==supervisor['stage_sha256']==evidence['stage_sha256']=='bd9516949e54d746371a9e4662ef29d63fe1997420f5dd1beafe2f8072f5315c'
    assert evidence['original_pid_matches']==evidence['matching_scientific_or_observer_modules']==[]
    assert supervisor['supervisor_pid']==15984 and supervisor['job_name']=='Local\\P16_R5_15984_1792603531797695000'
    helper=R/'paper16_dev_r3/windows_job.py'
    assert sha(helper)==load(R/'paper16_development_r4/SOURCE_PINS.json')['files']['paper16_dev_r3/windows_job.py']
    claim={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','reason':'Required process gate failed; close only exact original scientific Job',
           'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'source_sha256':sha(Path(__file__)),'stage_sha256':stage_sha,'job_name':supervisor['job_name'],
           'native_process_loss_evidence_sha256':sha(E/'ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json'),
           'restart_authorized':False,'native_worker_returncode':None}
    once(E/'OWNED_JOB_CLOSEOUT_CLAIM_1.json',claim)
    from paper16_dev_r3.windows_job import k,checked
    handle=k.OpenJobObjectW(12,False,supervisor['job_name'])
    if handle:
        try:
            checked(k.TerminateJobObject(handle,125))
            result={'job_opened':True,'termination_requested':True,'requested_termination_code':125,
                    'actual_native_worker_returncode':None,'reason':'Exact original owned Job terminated after mandatory process loss'}
        finally:checked(k.CloseHandle(handle))
    else:
        error=ctypes.get_last_error()
        if error!=2:raise ctypes.WinError(error)
        result={'job_opened':False,'open_job_error':error,'termination_requested':False,
                'actual_native_worker_returncode':None,'reason':'Exact original named Job no longer exists'}
    result.update({'stage_sha256':stage_sha,'job_name':supervisor['job_name'],
                   'claim_sha256':sha(E/'OWNED_JOB_CLOSEOUT_CLAIM_1.json'),
                   'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'scientific_processes_restarted':False,'E_access':False,'Final_C_D_access':False})
    once(E/'OWNED_JOB_CLOSEOUT_RECEIPT_1.json',result)
    print(json.dumps(result,indent=2))
