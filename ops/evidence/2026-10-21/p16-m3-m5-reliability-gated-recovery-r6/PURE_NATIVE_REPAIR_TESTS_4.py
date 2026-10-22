"""AST-extracted logic only. Never import native sources or invoke WinAPI/Popen."""
import ast,copy,datetime,hashlib,json,math,threading,time,traceback
from pathlib import Path
from types import SimpleNamespace

R=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent;P=R/'paper16_development_r6'
REG=E/'PURE_NATIVE_REPAIR_TEST_REGISTRATION_4.json';OUTPUT=E/'PURE_NATIVE_REPAIR_TEST_RESULT_4.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def extract(path,names,namespace):
    tree=ast.parse(path.read_bytes());selected=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    assert {n.name for n in selected}==set(names)
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path)+'#AST_ONLY','exec'),namespace)
    return tree

reg=json.loads(REG.read_bytes());assert reg['test_source_sha256']==sha(Path(__file__))
for row in reg['source_files']:assert sha(R/row['path'])==row['sha256']
assert sha(P/'PHASE_A_CLAIM.json')==reg['phase_claim_sha256']
phase=json.loads((P/'PHASE_A_CLAIM.json').read_bytes());assert time.monotonic()<phase['deadline_monotonic']
outcomes=[]
def check(name,call):
    call();outcomes.append({'name':name,'status':'PASS'})
def need(value):assert value
def rejects(call,phrase=None):
    try:call()
    except (AssertionError,RuntimeError,OSError,TimeoutError) as exc:
        assert phrase is None or phrase in str(exc);return
    raise AssertionError('Required rejection absent')

namespace={'math':math,'time':SimpleNamespace(monotonic=lambda:0.),'DETACHED_PROCESS':8,'CREATE_NEW_PROCESS_GROUP':512,'CREATE_BREAKAWAY_FROM_JOB':0x1000000}
ntree=extract(P/'native_process.py',['valid_json','exact_json','classify_terminal','finalize_owned','detached_flags','bounded_wait','OwnershipGate'],namespace)
classify=namespace['classify_terminal'];exact=namespace['exact_json'];finalize=namespace['finalize_owned']
native={'returncode':0,'native_job_tree_enforced':True,'assigned_before_resume':True,'killed_at_deadline':False}
try:
    for label,a,b in [('bool_int',{'a':True},{'a':1}),('int_float',{'n':1},{'n':1.}),('nested_bool',{'s':[False]},{'s':[0]}),('nested_float',{'s':[{'n':1.}]},{'s':[{'n':1}]}),('nan',{'n':math.nan},{'n':math.nan}),('inf',{'n':math.inf},{'n':math.inf}),('nonstringkey',{1:'x'},{1:'x'}),('tuple',{'s':(1,)},{'s':(1,)})]:
        check('strict_reject_'+label,lambda a=a,b=b:need(classify(native,a,b)['decision']=='STOP'))
    check('strict_equal_nested_accepts',lambda:need(classify(native,{'a':[True,1,1.,None,{'x':'y'}]},{'a':[True,1,1.,None,{'x':'y'}]})['decision']=='ACCEPTED_NATIVE_COMPLETION'))
    for field,value in [('returncode',True),('returncode',1.),('returncode',17),('assigned_before_resume',1),('native_job_tree_enforced',1),('killed_at_deadline',None)]:
        check('strict_native_field_'+field+'_'+str(value),lambda field=field,value=value:need(classify({**native,field:value},{'ok':True},{'ok':True})['decision']=='STOP'))
    for bad in [None,{},[],{'n':math.nan}]:
        check('invalid_expected_'+repr(bad),lambda bad=bad:need(classify(native,{'ok':True},bad)['decision']=='STOP'))
    for moment in ['create','write','flush','fsync']:
        def injected(moment=moment):
            calls=[]
            def cancel():calls.append('kernel_cancel');raise OSError('INJECTED_'+moment)
            def cleanup():calls.append('cleanup');return {'all_owned_processes_cleaned':True}
            value=finalize(cancel,cleanup);assert calls==['kernel_cancel','cleanup'] and value['all_finalization_actions_succeeded'] is False and value['failures'][0]['phase']=='cancellation'
        check('cancel_'+moment+'_failure_still_cleans',injected)
    def both_fail():
        calls=[]
        def fail(which):
            calls.append(which);raise OSError(which)
        value=finalize(lambda:fail('cancel'),lambda:fail('cleanup'))
        assert calls==['cancel','cleanup'] and [x['phase'] for x in value['failures']]==['cancellation','cleanup'] and value['all_finalization_actions_succeeded'] is False
    check('cancel_and_cleanup_failures_both_preserved',both_fail)
    flags=namespace['detached_flags']
    check('silent_breakaway_0x3000_omits_explicit_flag',lambda:need(flags({'in_job':True,'limit_flags':0x3000})==520))
    check('explicit_breakaway_only_if_permitted',lambda:need(flags({'in_job':True,'limit_flags':0x2800})==520|0x1000000))
    check('outside_job_no_breakaway_flag',lambda:need(flags({'in_job':False,'limit_flags':None})==520))
    check('unsupported_breakaway_denied_before_Popen',lambda:rejects(lambda:flags({'in_job':True,'limit_flags':0x2000}),'neither silent nor explicit'))
    check('malformed_job_flags_rejected',lambda:rejects(lambda:flags({'in_job':True,'limit_flags':True}),'Unknown inherited'))
    check('zero_deadline_not_extended_by_minimum_wait',lambda:rejects(lambda:namespace['bounded_wait'](0.,3.),'deadline expired'))

    class FakeKernel:
        def __init__(self,state=0):self.state=state;self.actions=[];self.events=set();self.created_events=0
        def CreateMutexW(self,*a):self.actions.append('create_mutex');return 11
        def CreateEventW(self,*a):self.actions.append('create_event');self.created_events+=1;return 11+self.created_events
        def OpenMutexW(self,*a):return 11
        def OpenEventW(self,*a):return 12
        def WaitForSingleObject(self,handle,milliseconds):
            assert 0<=milliseconds<=120000
            return self.state if handle==11 else (0 if handle in self.events else 258)
        def SetEvent(self,handle):self.actions.append('kernel_cancel' if handle==12 else 'kernel_uncertain');self.events.add(handle);return 1
        def ReleaseMutex(self,handle):self.actions.append('release_mutex');return 1
        def CloseHandle(self,handle):self.actions.append('close_'+str(handle));return 1
    def gate_state(state):
        kernel=FakeKernel(state);namespace.update({'k':kernel,'c':SimpleNamespace(set_last_error=lambda x:None,get_last_error=lambda:0),'checked':lambda value:value if value else (_ for _ in ()).throw(RuntimeError('kernel error'))})
        gate=namespace['OwnershipGate']('SYNTHETIC',10.,create=True)
        if state==0:
            with gate:pass
            assert 'release_mutex' in kernel.actions
        else:
            rejects(lambda:gate.__enter__(),'Abandoned' if state==128 else 'unavailable')
            assert 'kernel_cancel' in kernel.actions
            if state==128:assert 'release_mutex' in kernel.actions
            assert gate.uncertain() is True and 'kernel_uncertain' in kernel.actions
            kernel.state=0
            with gate:assert gate.uncertain() is True
        gate.close();assert 'close_11' in kernel.actions and 'close_12' in kernel.actions and 'close_13' in kernel.actions
    for state in [0,128,258,0xffffffff]:check('fake_kernel_mutex_state_'+str(state),lambda state=state:gate_state(state))

    class FakeGate:
        def __init__(self):self.lock=threading.Lock();self.stopped=False;self.actions=[]
        def __enter__(self):self.lock.acquire();return self
        def __exit__(self,*a):self.lock.release()
        def cancelled(self):return self.stopped
        def uncertain(self):return False
        def set_cancel(self):assert self.lock.locked();self.actions.append('kernel_cancel');self.stopped=True
    def spawn_interleaving():
        gate=FakeGate();entered=threading.Event();release=threading.Event();cancel_done=threading.Event();actions=[];errors=[];born=[]
        class FakeProcess:
            def __init__(self,*a,**kwargs):
                assert gate.lock.locked() and kwargs['creationflags']&4 and not kwargs['creationflags']&0x1000000
                self.pid=123;self._handle='STABLE_HANDLE';self.dead=False;born.append(self);actions.append('create_suspended')
            def poll(self):return 0 if self.dead else None
            def kill(self):assert gate.lock.locked();actions.append('kill_stable_handle');self.dead=True
            def wait(self,timeout):assert 0<timeout<=3;return 0
        def identity(handle,pid):assert handle=='STABLE_HANDLE';actions.append('stable_identity');return {'pid':pid,'creation_FILETIME':999,'image':'FAKE.exe'}
        def publish(*args):
            assert gate.lock.locked();actions.append('publish_entered');entered.set();assert release.wait(2.);actions.append('durable_registration')
        def resume(process):assert gate.lock.locked() and 'durable_registration' in actions;actions.append('resume')
        ns={'ownership':lambda:gate,'guard':lambda:None,'subprocess':SimpleNamespace(Popen=FakeProcess,DEVNULL=-1,STDOUT=-2),'native':SimpleNamespace(detached_flags=flags,current_job=lambda:{'in_job':True,'limit_flags':0x3000},handle_identity=identity,resume_suspended=resume,bounded_wait=lambda *a:1.),'LOCAL_CHILDREN':{},'created':publish,'claim':lambda:{'deadline_monotonic':10.}}
        extract(P/'test_native_lifecycle.py',['spawn_owned'],ns)
        def creator():
            try:ns['spawn_owned']('broker',['FAKE'],None,None,detached=True)
            except BaseException as exc:errors.append(str(exc))
        def canceller():
            with gate:gate.set_cancel();actions.append('cancel_after_handoff')
            cancel_done.set()
        a=threading.Thread(target=creator,daemon=True);a.start();assert entered.wait(2.)
        b=threading.Thread(target=canceller,daemon=True);b.start();assert not cancel_done.wait(.02) and 'resume' not in actions
        release.set();a.join(2.);b.join(2.);assert not a.is_alive() and not b.is_alive() and not errors
        assert actions.index('durable_registration')<actions.index('resume')<actions.index('cancel_after_handoff') and len(ns['LOCAL_CHILDREN'])==1
        rejects(lambda:ns['spawn_owned']('broker',['FAKE'],None,None,detached=True),'Cancellation prohibits')
        assert len(born)==1
    check('publication_delay_cancel_serializes_and_forbids_late_birth',spawn_interleaving)
    def cancel_IO():
        gate=FakeGate();calls=[]
        def denied_write(*args):calls.append('fsync_failure');raise OSError('INJECTED_MARKER_IO')
        ns={'ownership':lambda:gate,'once':denied_write,'W':Path('SYNTHETIC_ONLY'),'sha':lambda x:'claim','J':lambda x:{}}
        extract(P/'test_native_lifecycle.py',['cancel'],ns)
        result=finalize(lambda:ns['cancel']('fixture'),lambda:calls.append('cleanup'))
        assert gate.stopped and calls==['fsync_failure','cleanup'] and result['all_finalization_actions_succeeded'] is False
    check('actual_cancel_AST_kernel_event_precedes_disk_failure',cancel_IO)
    fsrc=(P/'test_native_lifecycle.py').read_bytes();ftree=ast.parse(fsrc)
    popens=[n for n in ast.walk(ftree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen']
    check('only_one_Popen_site_inside_spawn_owned',lambda:need(len(popens)==1 and popens[0] in list(ast.walk(next(n for n in ftree.body if isinstance(n,ast.FunctionDef) and n.name=='spawn_owned')))))
    check('native_supervise_has_no_direct_Popen_bypass',lambda:need(not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen' for n in ast.walk(ntree))))
    check('no_PID_taskkill_calls',lambda:need(not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='taskkill' for n in ast.walk(ftree))))
    check('candidate3_names_only',lambda:need(b'native_lifecycle_2' not in fsrc and b'REGISTRATION_2' not in fsrc and b'RESULT_2' not in fsrc))
    result={'mission':reg['mission'],'scope':'AST_ONLY_PREDICATE_AND_IN_MEMORY_FAKE_PROCESS_TESTS','registered_test_sha256':sha(Path(__file__)),'source_files':reg['source_files'],'tests':outcomes,'test_count':len(outcomes),'failures':0,'actual_native_fixture_executed':False,'actual_WinAPI_calls':0,'actual_Popen_calls':0,'protected_state_reads':0,'model_or_scientific_calls':0,'native_candidate_final_freeze_or_approval':False}
except BaseException as exc:
    result={'mission':reg['mission'],'test_count':len(outcomes),'tests':outcomes,'failure_type':type(exc).__name__,'failure':str(exc),'traceback':traceback.format_exc(),'actual_native_fixture_executed':False};raise
finally:
    with OUTPUT.open('x',encoding='utf8',newline='\n') as out:json.dump(result,out,indent=2,allow_nan=False);out.write('\n')
print(json.dumps({'pure_tests_passed':len(outcomes),'result_sha256':sha(OUTPUT),'actual_WinAPI_or_Popen_calls':0}))
