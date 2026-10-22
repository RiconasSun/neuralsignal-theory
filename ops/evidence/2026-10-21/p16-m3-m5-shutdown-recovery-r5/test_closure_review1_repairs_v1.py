"""Synthetic-only regressions for the three independent closure-tooling P1s."""
import copy,datetime,importlib.util,json,os,stat,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

E=Path(__file__).resolve().parent;REAL=Path(__file__).resolve().parents[4]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

m=module('r5_repaired_reproducer',E/'reproduce_saved.py')
b=module('r5_repaired_builder',E/'build_archive.py')
outcomes=[]

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,allow_nan=False),encoding='utf8')

def test(name,call,reject=False):
    try:call()
    except (AssertionError,ValueError,KeyError,FileNotFoundError,FileExistsError,RuntimeError) as exc:
        if not reject:raise
        if isinstance(exc,RuntimeError) and str(exc).startswith('FILESYSTEM_TRAP'):
            raise AssertionError('Lexical rejection reached filesystem: '+name) from exc
        outcomes.append({'name':name,'status':'PASS','rejected':type(exc).__name__,'message':str(exc)});return
    if reject:raise AssertionError('Expected denial absent: '+name)
    outcomes.append({'name':name,'status':'PASS'})

parent=E/'REPRO_TOOLING_TEMP';parent.mkdir(exist_ok=True)
holder=tempfile.TemporaryDirectory(prefix='p16_closure_review1_',dir=parent)
root=Path(holder.name).resolve();assert root.parent==parent.resolve() and root.name.startswith('p16_closure_review1_')
try:
    m.R=root;m.P=root/'paper16_development_r5';m.E=root/m.EP;m.P.mkdir(parents=True);m.E.mkdir(parents=True)
    def reject_tail(surface):
        path=m.P/(surface+'.jsonl');path.write_bytes(b'{"event":"COMPLETED"}')
        return m.lines(path)
    for surface in ['FG','TASK_TERMINAL','DIAGNOSTIC','INITIALIZER']:
        test('LF_required_'+surface,lambda surface=surface:reject_tail(surface),True)
    path=m.P/'prefix.jsonl';path.write_bytes(b'{"event":"RESERVED_BEFORE_EVALUATION"}\n')
    test('complete_line_partial_reservation_prefix_accepted',lambda:m.lines(path))
    path.write_bytes(b'{"event":"ATTEMPTED"}\n{"event":"COMPLETED"}')
    def torn_prefix():
        issues=[];rows=m.lines(path,True,issues)
        assert rows==[{'event':'ATTEMPTED'}] and len(issues)==1 and issues[0]['suffix_is_valid_JSON_without_LF'] is True and issues[0]['suffix_counted_as_complete'] is False
    test('valid_JSON_torn_tail_not_atomic_completion',torn_prefix)
    path.write_bytes(b'{"event":"ATTEMPTED"}\n{"event":')
    def invalid_tail():
        issues=[];rows=m.lines(path,True,issues)
        assert len(rows)==1 and issues[0]['suffix_is_valid_JSON_without_LF'] is False and issues[0]['uncommitted_suffix_bytes']>0
    test('invalid_torn_tail_preserved_with_unknown_status',invalid_tail)

    def stop(kind,message):
        return {'type':kind,'message':message,'scientific_status':m.stop_category(kind,message),'no_retry':True,'all_later_tasks_not_executed':True,'E_access':False,'Final_C_access':False,'Final_D_access':False}
    native={'returncode':1,'killed_at_deadline':False,'completed_before_deadline':True,'native_job_tree_enforced':True,'assigned_before_resume':True,'job_name':'Local\\P16_R5_42_123','clock_failure':None}
    failed={'t':{'type':'NumericalStop','message':'Synthetic required gate','retry':False}}
    numeric=stop('NumericalStop','Synthetic required gate')
    test('STOP_exact_atomic_worker_failure',lambda:m.validate_stop(numeric,native,failed))
    swapped=copy.deepcopy(numeric);swapped['scientific_status']='STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'
    test('STOP_denies_swapped_category',lambda:m.validate_stop(swapped,native,failed),True)
    test('STOP_denies_unmatched_FAILED_exception',lambda:m.validate_stop(stop('NumericalStop','Other'),native,failed),True)
    zero=copy.deepcopy(native);zero['returncode']=0
    test('STOP_denies_numerical_worker_failure_with_zero_exit',lambda:m.validate_stop(numeric,zero,failed),True)
    killed=copy.deepcopy(native);killed.update(killed_at_deadline=True,completed_before_deadline=False)
    test('STOP_native_deadline_exact',lambda:m.validate_stop(stop('BudgetStop','Native whole-Job stage deadline'),killed,{}))
    test('STOP_preserves_earlier_worker_failure_before_later_native_kill',lambda:m.validate_stop(numeric,killed,failed))
    clock=copy.deepcopy(native);clock.update(clock_failure='Synthetic stale clock',completed_before_deadline=False)
    test('STOP_native_clock_exact',lambda:m.validate_stop(stop('ResourceStop','Synthetic stale clock'),clock,{}))
    boot=copy.deepcopy(clock);boot['clock_failure']='Changed Windows boot epoch'
    test('STOP_native_boot_uses_original_classifier',lambda:m.validate_stop(stop('ResourceStop','Changed Windows boot epoch'),boot,{}))
    both=copy.deepcopy(clock);both['killed_at_deadline']=True
    test('STOP_denies_clock_label_when_native_killed_precedence_applies',lambda:m.validate_stop(stop('ResourceStop','Synthetic stale clock'),both,{}),True)
    test('STOP_native_process_exact',lambda:m.validate_stop(stop('ProcessStop','Native worker exit 1; see actual supervision receipt'),native,{}))
    test('STOP_native_zero_exit_missing_completion_exact',lambda:m.validate_stop(stop('ImplementationStop','Native zero exit without complete independently accepted M4 receipt'),zero,{}))
    trace='Traceback (most recent call last):\n  File "controller.py", line 1, in worker\nAccessStop: Synthetic bootstrap\n'
    test('STOP_worker_bootstrap_trace_and_native_corrobation',lambda:m.validate_stop(stop('AccessStop','Synthetic bootstrap'),native,{},trace))
    ntrace=trace.replace('AccessStop: Synthetic bootstrap','NumericalStop: Synthetic required gate')
    test('STOP_numerical_trace_alone_cannot_replace_FAILED_row',lambda:m.validate_stop(numeric,native,{},ntrace),True)
    def unknown_stop():
        decision=m.validate_stop(numeric,native,{},'',issues=[{'status':'TORN_SUFFIX_NOT_AN_ATOMIC_RECORD'}])
        assert decision['status']=='INCOMPLETE' and decision['verified_scientific_status'] is None
    test('STOP_torn_failure_provenance_is_unknown_not_PASS',unknown_stop)

    phase={'mission':m.MISSION,'phase':'B_A_M4','no_reset':True,'start_UTC':'2020-01-01T00:00:00+00:00','deadline_UTC':'2020-01-03T00:00:00+00:00','start_monotonic':1.,'deadline_monotonic':172801.,'windows_boot_UTC':'SYNTHETIC_BOOT'}
    write(m.P/'results/STAGE_CLAIM.json',phase);write(m.P/'PHASE_A_CLAIM.json',{'windows_boot_UTC':'SYNTHETIC_BOOT'})
    sup={'stage_sha256':m.sha(m.P/'results/STAGE_CLAIM.json'),'supervisor_pid':42,'job_name':'Local\\P16_R5_42_123'}
    write(m.P/'results/SUPERVISOR.json',sup);write(m.P/'results/SUPERVISION.json',native)
    test('native_exact_typed_PID_Job_stage',m.stage_and_native)
    for field,value in [('supervisor_pid','42'),('supervisor_pid',True),('supervisor_pid',-1),('job_name','INVALID_PRODUCER_JOB'),('job_name','Local\\P16_R5_43_123'),('job_name','Local\\P16_R5_42_notdigits'),('stage_sha256','mismatch')]:
        bad=copy.deepcopy(sup);bad[field]=value;write(m.P/'results/SUPERVISOR.json',bad)
        test('deny_native_identity_'+field+'_'+str(value),m.stage_and_native,True)
    write(m.P/'results/SUPERVISOR.json',sup)

    b.R=root;b.P=m.P;b.E=m.E
    badnames=['//synthetic-host/share/data.json','C:/outside/data.json','../escape','x/../y','x/./y','x:stream','x\\y','/absolute']
    for name in badnames:
        with patch.object(Path,'resolve',side_effect=RuntimeError('FILESYSTEM_TRAP resolve')),patch.object(Path,'lstat',side_effect=RuntimeError('FILESYSTEM_TRAP stat')),patch.object(Path,'open',side_effect=RuntimeError('FILESYSTEM_TRAP open')),patch.object(b,'sha',side_effect=RuntimeError('FILESYSTEM_TRAP hash')):
            test('builder_lexical_denial_before_filesystem_'+name,lambda name=name:b.local(name),True)
    for name in ['//synthetic-host/share/data.json','C:/outside/data.json','../escape','x/../y']:
        with patch.object(Path,'resolve',side_effect=RuntimeError('FILESYSTEM_TRAP resolve')):
            test('builder_relative_denial_before_resolve_'+name,lambda name=name:b.relative(Path(name)),True)
    for label,mode,attrs in [('symbolic',stat.S_IFLNK,0),('junction',stat.S_IFDIR,stat.FILE_ATTRIBUTE_REPARSE_POINT)]:
        fake=SimpleNamespace(st_mode=mode,st_file_attributes=attrs)
        with patch.object(Path,'lstat',return_value=fake),patch.object(Path,'resolve',side_effect=RuntimeError('FILESYSTEM_TRAP resolve')):
            test('builder_'+label+'_denied_before_resolve',lambda:b.local('redirect'),True)
            test('reproducer_'+label+'_denied_before_resolve',lambda:m.local('redirect'),True)

    # Positive builder integration uses only synthetic terminal metadata and source text.
    (b.E/'reproduce_saved.py').write_text((E/'reproduce_saved.py').read_text(),encoding='utf8')
    write(root/m.Q/'RECOVERY_TASK_PLAN.json',{'tasks':[{'task':{'id':'t0'}}]})
    (b.P/'results/FIT_JOURNAL.jsonl').write_bytes(b'')
    write(b.P/'results/SCIENTIFIC_STOP.json',stop('ProcessStop','Native worker exit 1; see actual supervision receipt'))
    for ref in [b.P/'INDEPENDENT_R5_PROTECTED_HASH_READBACK.json',b.P/'PREFIT_FREEZE_MANIFEST_V3.json']:write(ref,{'files':[]})
    test('builder_synthetic_terminal_archive_integration',b.build)
    test('builder_manifest_create_only',b.build,True)
    wrong=stop('ProcessStop','Native worker exit 1; see actual supervision receipt');wrong['scientific_status']='STOP_NUMERICAL_REQUIRED_GATE'
    write(b.P/'results/SCIENTIFIC_STOP.json',wrong)
    test('builder_denies_contradictory_scientific_STOP',b.build,True)
    write(b.P/'results/SCIENTIFIC_STOP.json',stop('ProcessStop','Native worker exit 1; see actual supervision receipt'))
    bad=copy.deepcopy(sup);bad['supervisor_pid']='42';write(b.P/'results/SUPERVISOR.json',bad)
    test('builder_denies_string_supervisor_PID',b.build,True);write(b.P/'results/SUPERVISOR.json',sup)
    # Verify the actual reference loop calls lexical validation before any resolution.
    badref='//synthetic-host/share/forbidden.json';write(b.P/'PREFIT_FREEZE_MANIFEST_V3.json',{'files':[{'path':badref,'sha256':'not-real'}]})
    original_local=b.local
    def trapped_local(name):
        if name==badref:
            with patch.object(Path,'resolve',side_effect=RuntimeError('FILESYSTEM_TRAP reference resolve')):return original_local(name)
        return original_local(name)
    with patch.object(b,'local',side_effect=trapped_local):test('builder_reference_loop_lexical_denial_before_resolve',b.build,True)
finally:
    assert root.parent==parent.resolve() and root.name.startswith('p16_closure_review1_')
    holder.cleanup()

m.R=REAL;m.P=REAL/'paper16_development_r5';m.E=E
record={'mission':m.MISSION,'scope':'SYNTHETIC_CLOSURE_REVIEW1_REPAIRS_ONLY','completed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':outcomes,'passed':len(outcomes),'failed':0,'reproducer_sha256':m.sha(E/'reproduce_saved.py'),'builder_sha256':m.sha(E/'build_archive.py'),'test_sha256':m.sha(__file__),'real_saved_state_audits':0,'full_real_reproduction_executed':False,'scientific_model_gradient_score_calls':0,'running_journal_writes':0,'M4_or_scientific_PASS_claimed':False}
target=E/'REPRO_TOOLING_REVIEW1_REPAIR_TEST_RESULT_1.json'
with target.open('x',encoding='utf8',newline='\n') as f:json.dump(record,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'focused_synthetic_tests_passed':len(outcomes),'real_reproduction_executed':False,'result_sha256':m.sha(target)}))
