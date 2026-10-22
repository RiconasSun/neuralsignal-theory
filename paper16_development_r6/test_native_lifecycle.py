"""Candidate4: real stdlib PE, exact atomic ownership, bounded cleanup."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from . import native_process as native

R = Path(__file__).resolve().parents[1]
P = R/'paper16_development_r6'
E = R/'ops/evidence/2026-10-21/p16-m3-m5-reliability-gated-recovery-r6'
W = P/'work/native_lifecycle_4'
REG = E/'NATIVE_LIFECYCLE_REGISTRATION_4.json'
MODULE = 'paper16_development_r6.test_native_lifecycle'
FIXTURE_PYTHON=Path(r'C:\Users\85993\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe')
FIXTURE_PYTHON_SHA256='28d2965d061656abbe3a46100bd3342d1152185289445d489782a21a8cfe9b57'
ROLES = {'launcher','broker','supervisor','worker_normal','worker_nonzero',
         'worker_empty_zero','worker_tree','worker_grandchild',
         'worker_loss_tree','worker_grandchild_loss'}
OWNERSHIP=None
LOCAL_CHILDREN={}


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def J(path):
    return json.loads(path.read_bytes())


def once(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False)
        f.write('\n');f.flush();os.fsync(f.fileno())


def claim():
    return J(W/'EXERCISE_CLAIM.json')


def verify_fixture_runtime(reg):
    expected={'path':str(FIXTURE_PYTHON),'sha256':FIXTURE_PYTHON_SHA256}
    assert reg['fixture_runtime']==expected,'Exact prospective stdlib fixture PE binding'
    assert reg['runtime_loader_evidence_sha256']==sha(E/'RUNTIME_LOADER_READONLY_RESULT_1.json')
    loader=J(E/'RUNTIME_LOADER_READONLY_RESULT_1.json')
    assert loader['sys_base_executable']['path']==expected['path'] and loader['sys_base_executable']['sha256']==expected['sha256']
    assert tuple(sys.version_info[:3])==(3,11,15) and loader['version'].startswith('3.11.15 '),'Frozen stdlib fixture version'
    assert sha(FIXTURE_PYTHON)==expected['sha256'],'Verified real PE bytes changed'
    assert os.path.normcase(os.path.abspath(sys.executable))==os.path.normcase(str(FIXTURE_PYTHON)),'Venv redirector is not an owned fixture runtime'
    assert sys.flags.no_site==1 and sys.flags.dont_write_bytecode==1,'Frozen -B -S stdlib-only fixture command'
    assert os.path.normcase(native.own_identity()['image'])==os.path.normcase(str(FIXTURE_PYTHON)),'Driver/role image differs from the registered real PE'


def ownership(*,create=False):
    global OWNERSHIP
    if OWNERSHIP is None:
        OWNERSHIP=native.OwnershipGate('Local\\P16_R6_OWNERSHIP_'+sha(W/'EXERCISE_CLAIM.json'),
                                      claim()['deadline_monotonic'],create=create)
    elif create:
        raise RuntimeError('Ownership gate cannot be recreated')
    return OWNERSHIP


def remaining(*,cleanup=False):
    # Five seconds of the original120 are reserved for cleanup; never extended.
    end=claim()['deadline_monotonic']-(0 if cleanup else 5)
    return max(0.,end-time.monotonic())


def guard(allow_unstarted=False):
    reg=J(REG)
    verify_fixture_runtime(reg)
    assert reg['phase_claim_sha256']==sha(P/'PHASE_A_CLAIM.json')
    phase=J(P/'PHASE_A_CLAIM.json')
    assert phase['start_monotonic']<=time.monotonic()<phase['deadline_monotonic']
    assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(phase['deadline_UTC'])
    for row in reg['source_files']:
        assert sha(R/row['path'])==row['sha256']
    if not allow_unstarted:
        assert remaining()>0,'Original fixture deadline; no extension'
        assert not ownership().cancelled(),'Kernel ownership cancellation; no further work'
        assert not ownership().uncertain(),'Prior ownership uncertainty cannot be cleared'
        assert not (W/'CANCELLED.json').exists(),'Owned fixture cancelled; no further launch'
    return reg


def command(role,*args):
    return [str(FIXTURE_PYTHON),'-B','-S','-m',MODULE,role,*args]


def receipt(role):
    assert role in ROLES
    with ownership() as gate:
        assert not gate.cancelled()
        guard()
        value={'role':role,'identity':native.own_identity(),
               'exercise_claim_sha256':sha(W/'EXERCISE_CLAIM.json'),
               'registration_sha256':sha(REG)}
        assert os.path.normcase(value['identity']['image'])==os.path.normcase(str(FIXTURE_PYTHON))
        once(W/('IDENTITY_'+role+'.json'),value)
    return value


def created(role,process,identity,job_name):
    """Called only under the ownership mutex while the child is suspended."""
    assert role in ROLES
    value={'role':role,'identity':identity,'exercise_claim_sha256':sha(W/'EXERCISE_CLAIM.json'),
           'registration_sha256':sha(REG),'created_suspended':True,
           'durable_registration_before_resume':True,'assigned_job_before_resume':job_name}
    once(W/('CREATED_'+role+'_'+str(process.pid)+'.json'),value)


def spawn_owned(role,cmd,cwd,stdout,*,detached=False,env=None,job=None,job_name=None):
    """The only fixture Popen site; mutex covers birth through durable handoff."""
    gate=ownership()
    with gate:
        assert cmd[:5]==[str(FIXTURE_PYTHON),'-B','-S','-m',MODULE],'Only exact registered real-PE fixture children'
        assert not gate.cancelled(),'Cancellation prohibits every later birth'
        assert not gate.uncertain(),'Uncertain ownership prohibits every later birth'
        guard()
        flags=0x4|(native.detached_flags(native.current_job()) if detached else 0)
        process=subprocess.Popen(cmd,cwd=cwd,stdin=subprocess.DEVNULL,stdout=stdout,
                                 stderr=subprocess.STDOUT,env=env,close_fds=True,creationflags=flags)
        try:
            identity=native.handle_identity(process._handle,process.pid)
            LOCAL_CHILDREN[process.pid]=(process,identity)
            assert os.path.normcase(identity['image'])==os.path.normcase(str(FIXTURE_PYTHON)),'Immediate Popen image must equal the executing real PE'
            if job is not None:
                assert isinstance(job_name,str) and job_name
                job.assign(process)
            created(role,process,identity,job_name)
            # No child instruction or further spawn precedes stable publication.
            native.resume_suspended(process)
            return process
        except BaseException:
            try:gate.set_cancel()
            finally:
                try:
                    if process.poll() is None:process.kill()
                finally:process.wait(timeout=native.bounded_wait(claim()['deadline_monotonic'],3.))
            raise


def wait_file(path,seconds=15):
    end=min(time.monotonic()+seconds,claim()['deadline_monotonic']-5)
    while True:
        guard()
        if path.exists():
            raw=path.read_bytes()
            if raw.endswith(b'\n'):
                return json.loads(raw)
        if time.monotonic()>=end:
            raise TimeoutError('Required immutable synthetic receipt missing: '+path.name)
        time.sleep(.02)


def cancel(reason):
    with ownership() as gate:
        # Kernel cancellation is authoritative even if marker IO/fsync fails.
        gate.set_cancel()
        try:
            once(W/'CANCELLED.json',{'reason':reason,'no_more_launches':True,
                 'exercise_claim_sha256':sha(W/'EXERCISE_CLAIM.json')})
        except FileExistsError:
            marker=J(W/'CANCELLED.json')
            assert marker['no_more_launches'] is True and marker['exercise_claim_sha256']==sha(W/'EXERCISE_CLAIM.json')
        if gate.uncertain():raise RuntimeError('Sticky ownership uncertainty; cancellation cannot clear it')


def cleanup():
    """One locked quiescent registry, not a timed pair of published snapshots."""
    results={};identities={}
    with ownership() as gate:
        gate.set_cancel()  # Same mutex as every spawn: no in-flight or late birth.
        records=sorted(W.glob('CREATED_*.json'))
        for path in records:
            row=J(path)
            assert row['role'] in ROLES and row['exercise_claim_sha256']==sha(W/'EXERCISE_CLAIM.json')
            assert row['registration_sha256']==sha(REG)
            identity=row['identity']
            assert row['created_suspended'] is True and row['durable_registration_before_resume'] is True
            key=(identity['pid'],identity['creation_FILETIME'])
            assert key not in identities or identities[key]==identity
            identities[key]=identity
        for path in W.glob('IDENTITY_*.json'):
            row=J(path);identity=row['identity'];key=(identity['pid'],identity['creation_FILETIME'])
            assert row['exercise_claim_sha256']==sha(W/'EXERCISE_CLAIM.json') and row['registration_sha256']==sha(REG)
            assert key in identities and identities[key]==identity,'Executing role lacks durable ownership handoff'
        for process,identity in LOCAL_CHILDREN.values():
            key=(identity['pid'],identity['creation_FILETIME'])
            assert identity==native.handle_identity(process._handle,process.pid)
            identities[key]=identity
        for key,identity in identities.items():
            if identity['pid']==os.getpid():
                results[str(key)]='CALLER_EXIT_STILL_PENDING'
                continue
            try:
                with native.OwnedProcess(identity,allow_terminate=True) as process:
                    process.terminate()
                    process.wait(native.bounded_wait(claim()['deadline_monotonic'],1.))
                results[str(key)]='VERIFIED_HANDLE_TERMINATED_OR_EXITED'
            except native.OriginalProcessGone:
                results[str(key)]='ORIGINAL_PROCESS_ALREADY_GONE_NO_PID_KILL'
            except Exception as exc:
                results[str(key)]='CLEANUP_UNVERIFIED:'+type(exc).__name__
        certain=not gate.uncertain()
        return {'ownership_quiescence_verified':certain,'kernel_cancellation_set':gate.cancelled(),
                'ownership_uncertainty':not certain,
                'registered_processes':len(identities),'processes':results,
                'all_owned_processes_cleaned':certain and all(v in ['VERIFIED_HANDLE_TERMINATED_OR_EXITED','ORIGINAL_PROCESS_ALREADY_GONE_NO_PID_KILL'] for v in results.values())}


def expected_completion(mode,job):
    return {'schema':'R6_SYNTHETIC_COMPLETE_V1','fixture':mode,'job_name':job,
            'exercise_claim_sha256':sha(W/'EXERCISE_CLAIM.json')}


def launcher():
    receipt('launcher')
    with (W/'BROKER_STDOUT.log').open('xb') as log:
        proc=spawn_owned('broker',command('broker'),R,log,detached=True)
        try:
            code=proc.wait(timeout=min(15.,remaining()))
        except BaseException:
            with ownership() as gate:
                gate.set_cancel();proc.kill()
                proc.wait(timeout=native.bounded_wait(claim()['deadline_monotonic'],2.))
            raise
    once(W/'LAUNCHER_COMPLETE.json',{'broker_native_pid':proc.pid,'broker_actual_exit_code':code})
    return code


def broker():
    own=receipt('broker');context=native.current_job()
    assert context['in_job'] is False,'Broker remains in inherited tool Job'
    with (W/'SUPERVISOR_STDOUT.log').open('xb') as log:
        proc=spawn_owned('supervisor',command('supervisor'),R,log,detached=True)
    once(W/'BROKER_COMPLETE.json',{'broker_identity':own['identity'],'supervisor_native_pid':proc.pid,
                                  'outside_inherited_job':True,'broker_handle_not_retained':True})
    return 0


def worker(mode):
    receipt('worker_'+mode)
    native.require_job(os.environ['P16_R6_SYNTHETIC_JOB'])
    if mode=='normal':
        once(W/'NORMAL_DONE.json',expected_completion(mode,os.environ['P16_R6_SYNTHETIC_JOB']))
        return 0
    if mode=='nonzero':
        return 17
    if mode=='empty_zero':
        return 0
    if mode in ['grandchild','grandchild_loss']:
        once(W/(mode.upper()+'.json'),{'identity':native.own_identity()})
        while True:
            guard();time.sleep(.02)
    if mode in ['tree','loss_tree']:
        childmode='grandchild' if mode=='tree' else 'grandchild_loss'
        proc=spawn_owned('worker_'+childmode,command('worker',childmode),R,subprocess.DEVNULL)
        once(W/(mode.upper()+'.json'),{'identity':native.own_identity(),'grandchild_native_pid':proc.pid})
        while True:
            guard();time.sleep(.02)
    raise ValueError('Unregistered worker fixture')


def supervisor():
    own=receipt('supervisor');context=native.current_job()
    assert context['in_job'] is False,'Supervisor remains in inherited tool Job'
    broker=wait_file(W/'IDENTITY_broker.json')
    launcher=wait_file(W/'IDENTITY_launcher.json')
    native.wait_identity_dead(broker['identity'],min(10.,remaining()))
    native.wait_identity_dead(launcher['identity'],min(10.,remaining()))
    once(W/'DETACHED_LIVENESS.json',{'identity':own['identity'],'broker_identity':broker['identity'],
         'launcher_identity':launcher['identity'],'broker_dead':True,'launcher_dead':True,**context})
    wait_file(W/'CONTINUE_SYNTHETIC.json')
    outcomes={};decisions={}
    for mode in ['normal','nonzero','empty_zero','tree']:
        guard()
        job='Local\\P16_R6_SYNTHETIC_'+str(os.getpid())+'_'+mode
        outcomes[mode]=native.supervise(command('worker',mode),R,W/(mode+'.log'),job,
                     2. if mode=='tree' else 10.,total_deadline=claim()['deadline_monotonic'],guard=guard,
                     ownership=ownership(),
                     spawn=lambda cmd,cwd,log,**kwargs:spawn_owned('worker_'+mode,cmd,cwd,log,**kwargs))
        complete=J(W/'NORMAL_DONE.json') if mode=='normal' else None
        decisions[mode]=native.classify_terminal(outcomes[mode],complete,expected_completion(mode,job))
    tree=wait_file(W/'IDENTITY_worker_tree.json')
    grandchild=wait_file(W/'IDENTITY_worker_grandchild.json')
    native.wait_identity_dead(tree['identity'],min(5.,remaining()))
    native.wait_identity_dead(grandchild['identity'],min(5.,remaining()))
    valid=expected_completion('normal',outcomes['normal']['job_name'])
    tampered={**valid,'exercise_claim_sha256':'0'*64}
    malformed_decisions=[native.classify_terminal(outcomes['normal'],v,valid)
                         for v in [None,[],{'fake':True},tampered]]
    all_pass=(decisions['normal']['native_completion_accepted']
              and all(decisions[k]['decision']=='STOP' for k in ['nonzero','empty_zero','tree'])
              and all(v['decision']=='STOP' for v in malformed_decisions)
              and outcomes['tree']['killed_at_deadline'])
    once(W/'CONTAINMENT_CASES.json',{'outcomes':outcomes,'terminal_decisions':decisions,
          'malformed_completion_decisions':malformed_decisions,'all_cases_pass':all_pass})
    wait_file(W/'INJECT_SUPERVISOR_LOSS.json')
    native.supervise(command('worker','loss_tree'),R,W/'loss_tree.log',
                     'Local\\P16_R6_SYNTHETIC_'+str(os.getpid())+'_loss',15.,
                     total_deadline=claim()['deadline_monotonic'],guard=guard,
                     ownership=ownership(),
                     spawn=lambda cmd,cwd,log,**kwargs:spawn_owned('worker_loss_tree',cmd,cwd,log,**kwargs))
    raise RuntimeError('Injected owned supervisor loss did not happen')


def exercise():
    reg=guard(allow_unstarted=True)
    assert not W.exists()
    W.mkdir(parents=True)
    start=time.monotonic();wall=datetime.datetime.now(datetime.timezone.utc)
    phase=J(P/'PHASE_A_CLAIM.json')
    deadline=min(start+120,phase['deadline_monotonic'])
    once(W/'EXERCISE_CLAIM.json',{'registration_sha256':sha(REG),
         'phase_claim_sha256':reg['phase_claim_sha256'],'driver_identity':native.own_identity(),
         'one_exercise':True,'synthetic_only':True,'retries':0,'start_monotonic':start,
         'deadline_monotonic':deadline,'start_UTC':wall.isoformat(),
         'deadline_UTC':(wall+datetime.timedelta(seconds=deadline-start)).isoformat()})
    result={'schema':'R6_NATIVE_LIFECYCLE_RESULT_V4','mission':reg['mission'],
            'registration_sha256':sha(REG),'driver_context':native.current_job(),
            'synthetic_only':True,'real_A_calls':0,'E_Final_access':False,
            'OS_settings_modified':False,'scientific_stage_started':False,'host_capability_pass':False}
    error=None
    try:
        ownership(create=True)
        with (W/'LAUNCHER_STDOUT.log').open('xb') as log:
            proc=spawn_owned('launcher',command('launcher'),R,log)
            try:
                code=proc.wait(timeout=min(30.,remaining()))
            except BaseException:
                with ownership() as gate:
                    gate.set_cancel();proc.kill()
                    proc.wait(timeout=native.bounded_wait(claim()['deadline_monotonic'],2.))
                raise
        result['launcher_actual_exit_code']=code
        if (W/'BREAKAWAY_DENIAL.json').exists():
            result.update(mandatory_host_gate='FAIL',failure=J(W/'BREAKAWAY_DENIAL.json'),
                          remaining_cases_executed=False,scientific_status='STOP_HOST_RELIABILITY_REQUIRED_GATE')
        else:
            assert code==0
            live=wait_file(W/'DETACHED_LIVENESS.json')
            assert live['launcher_dead'] and live['broker_dead'] and not live['in_job']
            # Retain this verified handle through liveness and injected termination.
            with native.OwnedProcess(live['identity'],allow_terminate=True) as supervisor_handle:
                assert supervisor_handle.alive()
                once(W/'CONTINUE_SYNTHETIC.json',{'live_identity':live['identity']})
                cases=wait_file(W/'CONTAINMENT_CASES.json',30)
                assert cases['all_cases_pass']
                once(W/'INJECT_SUPERVISOR_LOSS.json',{'owned_identity':live['identity']})
                child=wait_file(W/'IDENTITY_worker_loss_tree.json')
                grandchild=wait_file(W/'IDENTITY_worker_grandchild_loss.json')
                # Injection cannot kill a creator midway through durable handoff.
                with ownership():
                    supervisor_handle.terminate()
                    actual_exit=supervisor_handle.wait(native.bounded_wait(claim()['deadline_monotonic'],5.))
            native.wait_identity_dead(child['identity'],min(5.,remaining()))
            native.wait_identity_dead(grandchild['identity'],min(5.,remaining()))
            loss_outcome={'returncode':actual_exit,'killed_at_deadline':False,
                          'assigned_before_resume':True,'native_job_tree_enforced':True}
            loss_decision=native.classify_terminal(loss_outcome,None,{'complete':True})
            assert loss_decision['decision']=='STOP'
            once(W/'INJECTED_LOSS_STOP.json',{'actual_exit':actual_exit,'terminal_decision':loss_decision,
                                            'injected_synthetic_loss':True,'retry_performed':False})
            try:
                once(W/'EXERCISE_CLAIM.json',{})
            except FileExistsError:
                duplicate_denied=True
            else:
                duplicate_denied=False
            assert duplicate_denied
            result.update(host_capability_pass=True,mandatory_host_gate='PASS_TESTED_CAPABILITIES_ONLY',
                          detached_liveness=live,containment=cases,injected_loss_failclosed=True,
                          duplicate_claim_denied=True)
    except BaseException as exc:
        error=exc
        result.update(mandatory_host_gate='UNACCEPTED_FIXTURE_ERROR',fixture_error_type=type(exc).__name__,
                      fixture_error=str(exc),host_capability_pass=False)
    finally:
        finalization=native.finalize_owned(lambda:cancel('Fixture complete or exception'),cleanup)
        result['finalization']=finalization
        clean=finalization['cleanup']
        cleanup_ok=(finalization['all_finalization_actions_succeeded'] and type(clean) is dict
                    and clean.get('ownership_quiescence_verified') is True
                    and clean.get('kernel_cancellation_set') is True
                    and clean.get('all_owned_processes_cleaned') is True)
        result['all_owned_processes_cleaned']=cleanup_ok
        if not cleanup_ok:
            result['host_capability_pass']=False
            result['mandatory_host_gate']='UNACCEPTED_CLEANUP'
        result['original_total_deadline_exceeded']=time.monotonic()>claim()['deadline_monotonic']
        if result['original_total_deadline_exceeded']:
            result['host_capability_pass']=False
            result['mandatory_host_gate']='UNACCEPTED_TOTAL_DEADLINE'
        result['files']=[{'path':f.relative_to(R).as_posix(),'sha256':sha(f),'bytes':f.stat().st_size}
                         for f in sorted(W.iterdir()) if f.is_file()]
        result['completed_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        once(E/'NATIVE_LIFECYCLE_RESULT_4.json',result)
    print(json.dumps({'host_capability_pass':result['host_capability_pass'],
                      'mandatory_host_gate':result['mandatory_host_gate'],
                      'fixture_error':None if error is None else type(error).__name__,
                      'result_sha256':sha(E/'NATIVE_LIFECYCLE_RESULT_4.json')},indent=2))
    return 0 if result['host_capability_pass'] else 19


def run_role(role):
    try:
        return worker(sys.argv[2]) if role=='worker' else {'launcher':launcher,'broker':broker,'supervisor':supervisor}[role]()
    except BaseException as exc:
        # Any role error cancels further launches; driver still owns final result.
        try:
            once(W/('FAILURE_'+role+'_'+str(os.getpid())+'.json'),
                 {'type':type(exc).__name__,'message':str(exc),'identity':native.own_identity()})
        finally:
            finalization=native.finalize_owned(lambda:cancel('Abnormal owned role exit'),cleanup)
            print(json.dumps({'role_primary_error':type(exc).__name__,'finalization':finalization}),file=sys.stderr,flush=True)
        raise


if __name__=='__main__':
    raise SystemExit(exercise() if sys.argv[1]=='exercise' else run_role(sys.argv[1]))
