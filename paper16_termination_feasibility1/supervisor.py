"""Native process-tree enforcement, adapted from pinned original supervisor only."""
import os,subprocess,sys,time
from .common import *
from paper16_dev_r3.windows_job import Job,resume_suspended

def supervise_child(command,stage,log_path,name):
    verify_stage_environment(stage);guard(stage)
    with Path(log_path).open('xb') as log:
        with Job(name) as job:
            proc=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=0x4)
            killed=False;error=None
            try:
                job.assign(proc);resume_suspended(proc)
                while proc.poll() is None:
                    try:guard(stage)
                    except BaseException as exc:error=str(exc);job.terminate();killed=True;break
                    time.sleep(min(.1,max(.001,stage['deadline_monotonic']-time.monotonic())))
                code=proc.wait()
            except BaseException:
                if proc.poll() is None:proc.kill()
                proc.wait();raise
    return {'returncode':code,'killed_at_deadline':killed,'clock_failure':error,'completed_before_deadline':time.monotonic()<stage['deadline_monotonic'],
            'native_job_tree_enforced':True,'assigned_before_resume':True,'job_name':name}

def supervise(mode):
    require(mode in ['synthetic','real'],'Mode')
    if mode=='real':
        require(not (P/'REAL_CLAIM.json').exists(),'Real diagnostic already consumed; no retry')
        verify_prefit();stage=make_stage(7200);claim(P/'REAL_CLAIM.json',{'mission':MISSION,'stage':stage,'attempt_limit':1,'no_retry':True,'prefit_approval_sha256':sha(E/'PREFIT_APPROVAL.json'),'code_freeze_sha256':sha(P/'CODE_FREEZE.json')})
        folder=P/'work/real';folder.mkdir(parents=True,exist_ok=False)
    else:
        verify_code();stage=make_stage(600);folder=P/'work'/('synthetic_'+str(time.time_ns()));folder.mkdir(parents=True,exist_ok=False)
    once(folder/'STAGE.json',stage)
    name=f'Local\\P16_TF1_{mode}_{os.getpid()}_{time.time_ns()}'
    os.environ['P16_TF1_JOB']=name;os.environ['P16_TF1_FOLDER']=str(folder)
    result=supervise_child([sys.executable,'-B','-m','paper16_termination_feasibility1.worker',mode],stage,folder/'EXECUTION.log',name)
    once(folder/'SUPERVISION.json',result);print(json.dumps({'folder':folder.relative_to(R).as_posix(),'supervision':result}),flush=True)
    if result['returncode'] or result['killed_at_deadline'] or not result['completed_before_deadline']:raise BudgetStop('Supervised attempt stopped; no retry or budget extension')

if __name__=='__main__':supervise(sys.argv[1])
