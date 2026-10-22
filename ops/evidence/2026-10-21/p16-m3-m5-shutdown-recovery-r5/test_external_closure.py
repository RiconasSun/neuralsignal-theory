"""Synthetic metadata/hash fixtures only; never load the real interrupted bundle."""
import argparse,contextlib,copy,hashlib,importlib.util,io,json,stat,tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

E=Path(__file__).resolve().parent;REAL=Path(__file__).resolve().parents[4]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('external_reproducer_fixture',E/'reproduce_saved.py');b=module('external_builder_fixture',E/'build_archive.py')
parser=argparse.ArgumentParser();parser.add_argument('--receipt-id',type=int,required=True);args=parser.parse_args();assert args.receipt_id>=1
outcomes=[]
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,allow_nan=False)+'\n',encoding='utf8')
def journal(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def file(p):return {'path':p.relative_to(m.R).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size}
def pin(p):return file(p)
def edit(p,key,value):
    v=json.loads(p.read_bytes());v[key]=value;write(p,v)
def test(name,call,reject=False):
    buf=io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):call()
    except (AssertionError,ValueError,KeyError,FileNotFoundError,FileExistsError,RuntimeError) as exc:
        if not reject:raise
        if 'FORBIDDEN_NUMERICAL' in str(exc):raise
        outcomes.append({'name':name,'PASS':True,'rejected':type(exc).__name__,'message':str(exc)});return
    assert not reject,'Missing rejection: '+name
    outcomes.append({'name':name,'PASS':True,'synthetic_stdout':buf.getvalue()})

parent=REAL/'_r5_closure_temp';parent.mkdir(exist_ok=True)
holder=tempfile.TemporaryDirectory(prefix='p16_external_',dir=parent);ROOT=Path(holder.name).resolve()
assert ROOT.parent==parent.resolve() and ROOT.name.startswith('p16_external_')
original_pins=copy.deepcopy(m.EXTERNAL_PINS)

def fixture():
    root=ROOT/str(len(list(ROOT.iterdir())));root.mkdir()
    m.R=root;m.P=root/'paper16_development_r5';m.E=root/m.EP;m.P.mkdir();m.E.mkdir(parents=True)
    b.R=root;b.P=m.P;b.E=m.E
    (m.E/'reproduce_saved.py').write_bytes((E/'reproduce_saved.py').read_bytes());m.__file__=str(m.E/'reproduce_saved.py')
    for filename in ['register_external_closeout.py','close_original_job.py','INDEPENDENT_R5_M4_MONITOR.py','INDEPENDENT_EXTERNAL_CLOSEOUT_REVIEW_1.md']:
        (m.E/filename).write_bytes(b'SYNTHETIC ONLY\n')
    for filename in ['INDEPENDENT_R5_EXTERNAL_INTERRUPTION_CHECK_RESULT_1.json','INDEPENDENT_EXTERNAL_CLOSEOUT_BINDING_CHECK_RESULT_1.json','INDEPENDENT_OBSERVER_SESSION_READBACK_1.json']:
        write(m.E/filename,{'SYNTHETIC_ONLY':True})
    phase={'mission':m.MISSION,'phase':'B_A_M4','no_reset':True,'start_UTC':'2020-01-01T00:00:00+00:00','deadline_UTC':'2020-01-03T00:00:00+00:00','start_monotonic':1.,'deadline_monotonic':172801.,'windows_boot_UTC':'2019-12-01T00:00:00+00:00'}
    write(m.P/'results/STAGE_CLAIM.json',phase);write(m.P/'PHASE_A_CLAIM.json',{'windows_boot_UTC':phase['windows_boot_UTC']})
    stage=digest(m.P/'results/STAGE_CLAIM.json')
    job='Local\\P16_R5_42_123';write(m.P/'results/SUPERVISOR.json',{'supervisor_pid':42,'job_name':job,'stage_sha256':stage})
    write(m.P/'results/WORKER_CLAIM.json',{'pid':43,'no_restart':True,'single_worker':True})
    prefit=m.P/'PREFIT_FREEZE_MANIFEST_V3.json';write(prefit,{'files':[]})
    write(m.P/'INDEPENDENT_R5_PROTECTED_HASH_READBACK.json',{'files':[]})
    observer_reg={'script_path':m.EP+'/INDEPENDENT_R5_M4_MONITOR.py','script_sha256':digest(m.E/'INDEPENDENT_R5_M4_MONITOR.py'),'stage_claim_sha256':stage,'bound_files':[file(prefit)]}
    write(m.E/'INDEPENDENT_R5_M4_REGISTRATION.json',observer_reg)
    write(m.E/'INDEPENDENT_R5_M4_OBSERVER_CLAIM.json',{'pid':44,'registration_sha256':digest(m.E/'INDEPENDENT_R5_M4_REGISTRATION.json'),'script_sha256':observer_reg['script_sha256'],'stage_claim_sha256':stage,'one_pass_no_restart':True})
    plan=[{'id':'SYNTHETIC_TASK_'+str(i),'model':'D'} for i in range(2479)]
    write(root/m.Q/'RECOVERY_TASK_PLAN.json',{'tasks':[{'task':t} for t in plan]})
    m.EXTERNAL_COUNTS=(2,1,1,2477)
    fg=[{'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]},{'event':'COMPLETED','call':1,'objective':0.,'gradient_inf':0.,'gradient':[0.]}]
    init={'origin':'ORIGINAL_FROZEN_CONSTRUCTOR','no_warm_start':True,**{k:{'shape':[1],'dtype':'<f8','sha256':'SYNTHETIC_'+k} for k in ['x0','lo','hi']}}
    folders=[];initializers=[]
    for task in plan[:2]:
        folder=m.P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest();folder.mkdir(parents=True);folders.append(folder)
        (folder/'initial.npz').write_bytes(b'SYNTHETIC UNDECODABLE NPZ')
        write(folder/'ATTEMPT.json',{'task':task,'no_retry':True,'parameters':1,'bounds':{**file(folder/'initial.npz'),'arrays':{k:init[k] for k in ['x0','lo','hi']}}})
        write(folder/'CLIENT.json',{'SYNTHETIC':True});(folder/'CLIENT_STDERR.log').write_bytes(b'')
        journal(folder/'CALLS.jsonl',fg);journal(folder/'ACCEPTED.jsonl',[])
        journal(folder/'DIAGNOSTIC_CALLS.jsonl',[next(m.diagnostic_sequence(1))])
        write(m.P/'results/attempt_consumption'/folder.name,{'task':task,'no_retry':True})
        initializers.append({'task_id':task['id'],**copy.deepcopy(init)})
    for name in ['RESULT.json','DIAGNOSTICS.json']:write(folders[0]/name,{'SYNTHETIC':True})
    for name in ['endpoint.npz','coordinate_certificates.npz']:(folders[0]/name).write_bytes(b'SYNTHETIC UNDECODABLE NPZ')
    completed={'event':'COMPLETED','task':plan[0],'result_path':file(folders[0]/'RESULT.json')['path'],'result_sha256':digest(folders[0]/'RESULT.json')}
    def attempt(task):return {'event':'ATTEMPTED','task':task,'ftol':0.,'initializer':'ORIGINAL_FROZEN_ONLY'}
    journal(m.P/'results/FIT_JOURNAL.jsonl',[attempt(plan[0]),completed,attempt(plan[1])])
    journal(m.P/'results/INITIALIZER_IDENTITIES.jsonl',initializers)
    ledger={'task':plan[0],'origin':'R5','status':'INDEPENDENTLY_QUALIFIED_NEW_STATE','new_evaluations':0,'completed_receipt':completed,'initializer_identity':initializers[0],'result_path':completed['result_path'],'result_sha256':completed['result_sha256'],'files':[file(p) for p in sorted(folders[0].iterdir())]}
    ledger_path=m.E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl';journal(ledger_path,[ledger])
    for name in ['SCIENTIFIC_EXECUTION.log','INDEPENDENT_R5_M4_MONITOR_EXECUTION_1.log']:(m.E/name).write_bytes(b'SYNTHETIC ONLY\n')
    proof={'original_claimed_pids':[42,43,44],'original_pid_matches':[],'matching_scientific_or_observer_modules':[],'native_host_boot_UTC':phase['windows_boot_UTC'],'stage_sha256':stage,'native_exit_code':None,'exact_interruption_time':None,'interruption_cause':'UNDETERMINED_FROM_SAVED_EVIDENCE',**{k:False for k in ['original_supervision_receipt_available','original_worker_stop_available','scientific_process_restart_authorized','scientific_processes_restarted','observer_restarted','E_access','Final_C_D_access']}}
    proof_path=m.E/'ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json';write(proof_path,proof)
    claim_path=m.E/'OWNED_JOB_CLOSEOUT_CLAIM_1.json';write(claim_path,{'source_sha256':digest(m.E/'close_original_job.py'),'native_process_loss_evidence_sha256':digest(proof_path),'stage_sha256':stage,'job_name':job,'restart_authorized':False,'native_worker_returncode':None})
    job_path=m.E/'OWNED_JOB_CLOSEOUT_RECEIPT_1.json';write(job_path,{'claim_sha256':digest(claim_path),'stage_sha256':stage,'job_name':job,'job_opened':False,'open_job_error':2,'termination_requested':False,'actual_native_worker_returncode':None,'scientific_processes_restarted':False,'E_access':False,'Final_C_D_access':False})
    claims=[file(m.P/'results'/n) for n in ['STAGE_CLAIM.json','SUPERVISOR.json','WORKER_CLAIM.json']]+[file(m.E/'INDEPENDENT_R5_M4_OBSERVER_CLAIM.json')]
    roots=['paper16_development_r5/work/fits','paper16_development_r5/results'];extras=[m.EP+'/'+n for n in ['INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl','INDEPENDENT_R5_M4_MONITOR_EXECUTION_1.log','SCIENTIFIC_EXECUTION.log']]
    unknown={'native_worker_exit_code':None,'exact_interruption_UTC':None,'interruption_cause':'UNDETERMINED_FROM_SAVED_EVIDENCE'}
    base={'mission':m.MISSION,'base':m.BASE};status='STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'
    paths={k:root/v[0] for k,v in original_pins.items()}
    reg={**base,**unknown,'schema':'R5_EXTERNAL_PROCESS_LOSS_REGISTRATION_V1','source_sha256':digest(m.E/'register_external_closeout.py'),'scientific_status':status,'stage_sha256':stage,'original_claims':claims,'native_absence_proof':pin(proof_path),'owned_job_receipt':pin(job_path),'original_receipts_required_absent':m.EXTERNAL_ABSENT,'snapshot_path':str(paths['snapshot'].relative_to(root).as_posix()),'external_stop_path':str(paths['external_stop'].relative_to(root).as_posix()),'snapshot_roots':roots,'snapshot_extra_files':extras,'accepted_original_source_freeze':pin(prefit),'scientific_policy_amended':False,'budget_reset_allowed':False,'scientific_process_restarts_allowed':0,'additional_fits_allowed':0,'new_derivative_or_score_calls_allowed':0}
    write(paths['registration'],reg)
    snapshot_files={file(p)['path']:file(p) for rt in roots for p in m.walk_files(root/rt)}
    for record in claims+[file(root/name) for name in extras]:snapshot_files[record['path']]=record
    snapshot={**base,**unknown,'schema':'R5_EXTERNAL_INTERRUPTION_SNAPSHOT_V1','registration':pin(paths['registration']),'roots':roots,'extra_files':extras,'files':list(snapshot_files.values()),'file_count':len(snapshot_files),'attempted':2,'completed':1,'partial':1,'unattempted':2477,'failed_journal_entries':0,'independently_qualified_completed_states':1,'partial_task':plan[1],'partial_parameters':1,'partial_FG_reserved':1,'partial_FG_completed_receipts':1,'partial_accepted_iterations':0,'partial_diagnostic_reservations':{'ANALYTIC_RESERVED':1},'file_timestamps_are_not_exact_interruption_time':True,'numerical_audit_repeated':False,'NPZ_decodes':0,'new_fits_derivatives_scores':0}
    write(paths['snapshot'],snapshot)
    stop={**base,**unknown,'schema':'R5_EXTERNAL_PROCESS_LOSS_STOP_V1','scientific_status':status,'origin':'EXTERNAL_NATIVE_PROCESS_LOSS_CLOSEOUT','registration':pin(paths['registration']),'snapshot':pin(paths['snapshot']),'stage_sha256':stage,'native_absence_proof':pin(proof_path),'owned_job_receipt':pin(job_path),'new_attempts':2,'new_numerical_passes':1,'partial_attempts':1,'unattempted':2477,'recorded_numerical_failures':0,**{k:False for k in ['M4_complete','original_supervision_available','original_worker_stop_available','E_access','Final_C_access','Final_D_access']},**{k:True for k in ['no_retry','no_restart','all_later_tasks_not_executed']}}
    write(paths['external_stop'],stop)
    acceptance={**base,**unknown,'decision':'ACCEPTED_EXTERNAL_PROCESS_LOSS_CLOSEOUT','open_P0':0,'open_P1':0,'review_path':m.EP+'/INDEPENDENT_EXTERNAL_CLOSEOUT_REVIEW_1.md','review_sha256':digest(m.E/'INDEPENDENT_EXTERNAL_CLOSEOUT_REVIEW_1.md'),'stage_claim_sha256':stage,'new_attempts':2,'new_completed':1,'partial_attempts':1,'unattempted':2477,'M4_complete':False,'M4_approval_issued':False,'scientific_status':status}
    acceptance.update({'independent_prefix_result_sha256':digest(m.E/'INDEPENDENT_R5_EXTERNAL_INTERRUPTION_CHECK_RESULT_1.json'),'independent_binding_result_sha256':digest(m.E/'INDEPENDENT_EXTERNAL_CLOSEOUT_BINDING_CHECK_RESULT_1.json'),'independent_checks_actual_exit_codes':[0,0],'observer_operator_session_readback_path':m.EP+'/INDEPENDENT_OBSERVER_SESSION_READBACK_1.json','observer_operator_session_readback_sha256':digest(m.E/'INDEPENDENT_OBSERVER_SESSION_READBACK_1.json')})
    for key,path in list(paths.items())[:3]+[('native_absence_proof',proof_path),('owned_job_receipt',job_path),('newstate_ledger',ledger_path)]:
        acceptance[key+'_path']=path.relative_to(root).as_posix();acceptance[key+'_sha256']=digest(path)
    write(paths['acceptance'],acceptance)
    m.EXTERNAL_PINS={key:(path.relative_to(root).as_posix(),digest(path)) for key,path in paths.items()}
    return paths,folders

def forbidden(*a,**k):raise AssertionError('FORBIDDEN_NUMERICAL')
def rebind_synthetic_authority(paths):
    """Re-sign ONLY fixture pins to exercise semantics beyond the hash barrier.

    This helper never exists in production tooling and cannot read the real bundle.
    """
    assert m.R.is_relative_to(ROOT) and m.R!=REAL
    reg=json.loads(paths['registration'].read_bytes())
    reg['original_claims']=[file(m.R/r['path']) for r in reg['original_claims']]
    for key in ['native_absence_proof','owned_job_receipt','accepted_original_source_freeze']:reg[key]=file(m.R/reg[key]['path'])
    write(paths['registration'],reg)
    snapshot=json.loads(paths['snapshot'].read_bytes());snapshot['registration']=pin(paths['registration'])
    snapshot['files']=[file(m.R/r['path']) for r in snapshot['files']];write(paths['snapshot'],snapshot)
    stop=json.loads(paths['external_stop'].read_bytes());stop['registration']=pin(paths['registration']);stop['snapshot']=pin(paths['snapshot'])
    for key in ['native_absence_proof','owned_job_receipt']:stop[key]=reg[key]
    write(paths['external_stop'],stop)
    acceptance=json.loads(paths['acceptance'].read_bytes())
    for key in ['registration','snapshot','external_stop']:acceptance[key+'_sha256']=digest(paths[key])
    for key in ['native_absence_proof','owned_job_receipt']:acceptance[key+'_sha256']=reg[key]['sha256']
    acceptance['newstate_ledger_sha256']=digest(m.E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl');write(paths['acceptance'],acceptance)
    m.EXTERNAL_PINS={key:(p.relative_to(m.R).as_posix(),digest(p)) for key,p in paths.items()}
try:
    paths,folders=fixture()
    with patch.object(m.np,'load',forbidden),patch.object(m,'reuse',forbidden),patch.object(m,'coordinates',forbidden),patch.object(m,'receipt',forbidden):
        def good():
            r=m.validate_external_terminal();assert r['native'] is None and r['NPZ_decodes']==0 and r['numerical_certificate_audits_repeated']==0 and len(r['completed'])==1
        test('accepted_external_metadata_only_no_NPZ_or_certificate_audit',good)
    for key in original_pins:
        def altered(key=key):
            paths,_=fixture();paths[key].write_bytes(paths[key].read_bytes()+b' ');m.validate_external_terminal()
        test('deny_changed_pinned_'+key,altered,True)
        def missing(key=key):
            paths,_=fixture();paths[key].unlink();m.validate_external_terminal()
        test('deny_missing_pinned_'+key,missing,True)
    for name in m.EXTERNAL_ABSENT+['paper16_development_r5/results/M4_SELECTION_FREEZE.json']:
        def fabricated(name=name):
            fixture();write(m.R/name,{'FAKE':True});m.validate_external_terminal()
        test('deny_fabricated_original_or_M4_'+Path(name).name,fabricated,True)
    for name in ['ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json','OWNED_JOB_CLOSEOUT_RECEIPT_1.json','OWNED_JOB_CLOSEOUT_CLAIM_1.json','INDEPENDENT_R5_M4_OBSERVER_CLAIM.json','INDEPENDENT_R5_M4_REGISTRATION.json','INDEPENDENT_EXTERNAL_CLOSEOUT_REVIEW_1.md','close_original_job.py','register_external_closeout.py']:
        def tampered(name=name):
            fixture();p=m.E/name;p.write_bytes(p.read_bytes()+b' ');m.validate_external_terminal()
        test('deny_tampered_native_role_source_or_review_'+name,tampered,True)
    for filename in ['RESULT.json','DIAGNOSTICS.json','endpoint.npz','FAILURE.json']:
        def partialpass(filename=filename):
            _,folders=fixture();(folders[1]/filename).write_bytes(b'FAKE');m.validate_external_terminal()
        test('deny_partial_with_'+filename,partialpass,True)
    def extrafile():
        fixture();(m.P/'results/unregistered').write_bytes(b'EXTRA');m.validate_external_terminal()
    test('deny_snapshot_unregistered_extra_file',extrafile,True)
    for name in ['CALLS.jsonl','DIAGNOSTIC_CALLS.jsonl','initial.npz']:
        def lost(name=name):
            _,folders=fixture();(folders[1]/name).unlink();m.validate_external_terminal()
        test('deny_partial_missing_'+name,lost,True)
    def changed_ledger():
        fixture();p=m.E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl';row=m.lines(p)[0];row['result_sha256']='FORGED';journal(p,[row]);m.validate_external_terminal()
    test('deny_changed_accepted_observer_binding',changed_ledger,True)
    for key,val in [('native_worker_exit_code',0),('exact_interruption_UTC','2020-01-01T00:00:00Z'),('interruption_cause','SHUTDOWN'),('M4_complete',True)]:
        def invented(key=key,val=val):
            paths,_=fixture();edit(paths['external_stop'],key,val);m.validate_external_terminal()
        test('deny_invented_external_'+key,invented,True)
    semantic_cases=[
        ('external_stop','native_worker_exit_code',0),('external_stop','exact_interruption_UTC','2020-01-01T00:00:00Z'),('external_stop','interruption_cause','SHUTDOWN'),('external_stop','M4_complete',True),
        ('external_stop','scientific_status','M4_COMPLETE_INDEPENDENTLY_ACCEPTED'),
        ('snapshot','completed',2),('snapshot','partial_diagnostic_reservations',{'ANALYTIC_RESERVED':1,'AD_RESERVED':1}),('snapshot','partial_FG_completed_receipts',2),('snapshot','partial_accepted_iterations',1),
        ('acceptance','open_P1',1),('acceptance','review_sha256','FORGED'),('acceptance','decision','M4_PASS'),
        ('ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json','original_pid_matches',[42]),('ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json','matching_scientific_or_observer_modules',['replacement']),('ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json','original_claimed_pids',[42,43,999]),
        ('OWNED_JOB_CLOSEOUT_RECEIPT_1.json','job_name','Local\\P16_R5_999_123'),('OWNED_JOB_CLOSEOUT_RECEIPT_1.json','termination_requested',True),('OWNED_JOB_CLOSEOUT_RECEIPT_1.json','actual_native_worker_returncode',0),('OWNED_JOB_CLOSEOUT_RECEIPT_1.json','open_job_error',5),
        ('INDEPENDENT_R5_M4_OBSERVER_CLAIM.json','one_pass_no_restart',False)]
    for location,key,val in semantic_cases:
        def semantic(location=location,key=key,val=val):
            paths,_=fixture();p=paths[location] if location in paths else m.E/location;edit(p,key,val);rebind_synthetic_authority(paths);m.validate_external_terminal()
        test('deny_semantic_after_fixture_repin_'+location+'_'+key,semantic,True)
    def wrong_ledger_receipt():
        paths,_=fixture();p=m.E/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl';row=m.lines(p)[0];row['completed_receipt']['result_sha256']='FORGED';journal(p,[row]);rebind_synthetic_authority(paths);m.validate_external_terminal()
    test('deny_semantic_accepted_ledger_wrong_completion_receipt',wrong_ledger_receipt,True)
    for entry,call in [('reproducer',lambda:m.validate_terminal_metadata()),('builder',lambda:b.build())]:
        for redirected in ['symlink','reparse']:
            def route_denial(entry=entry,call=call,redirected=redirected):
                fixture();leaf=m.E/'EXTERNAL_SCIENTIFIC_STOP.json';original_lstat=Path.lstat;original_exists=Path.exists;calls=[]
                def guarded_lstat(path,*a,**k):
                    if path==leaf:
                        calls.append('leaf_lstat')
                        return SimpleNamespace(st_mode=stat.S_IFLNK if redirected=='symlink' else stat.S_IFREG,st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT if redirected=='reparse' else 0)
                    return original_lstat(path,*a,**k)
                def trapped_exists(path,*a,**k):
                    if path==leaf:raise AssertionError('EXTERNAL_ROUTE_TARGET_ACCESS_BEFORE_REJECTION')
                    return original_exists(path,*a,**k)
                try:
                    with patch.object(Path,'lstat',guarded_lstat),patch.object(Path,'exists',trapped_exists):call()
                except (AssertionError,ValueError) as exc:
                    assert 'EXTERNAL_ROUTE_TARGET_ACCESS_BEFORE_REJECTION' not in str(exc) and calls==['leaf_lstat']
                    assert 'Symbolic/junction/reparse' in str(exc)
                    return
                raise AssertionError('Redirected leaf was accepted')
            test('route_rejects_'+entry+'_'+redirected+'_before_exists',route_denial)
    for entry in ['external_validator','builder']:
        for redirected in ['symlink','reparse']:
            def workE_denial(entry=entry,redirected=redirected):
                fixture();leaf=m.P/'work/E';original_lstat=Path.lstat;original_exists=Path.exists;calls=[]
                def guarded_lstat(path,*a,**k):
                    if path==leaf:
                        calls.append('leaf_lstat')
                        return SimpleNamespace(st_mode=stat.S_IFLNK if redirected=='symlink' else stat.S_IFREG,st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT if redirected=='reparse' else 0)
                    return original_lstat(path,*a,**k)
                def trapped_exists(path,*a,**k):
                    if path==leaf:raise AssertionError('EXTERNAL_ROUTE_TARGET_ACCESS_BEFORE_REJECTION')
                    return original_exists(path,*a,**k)
                try:
                    with patch.object(b,'metadata_policy',lambda:m),patch.object(Path,'lstat',guarded_lstat),patch.object(Path,'exists',trapped_exists):
                        m.validate_external_terminal() if entry=='external_validator' else b.build()
                except (AssertionError,ValueError) as exc:
                    assert 'EXTERNAL_ROUTE_TARGET_ACCESS_BEFORE_REJECTION' not in str(exc) and calls==['leaf_lstat']
                    assert 'Symbolic/junction/reparse' in str(exc)
                    return
                raise AssertionError('Redirected E leaf was accepted')
            test('route_rejects_workE_'+entry+'_'+redirected+'_before_exists',workE_denial)
    def synthetic_archive():
        fixture()
        with patch.object(b,'metadata_policy',lambda:m),patch.object(m.np,'load',forbidden),patch.object(m,'reuse',forbidden),patch.object(m,'coordinates',forbidden),patch.object(m,'receipt',forbidden):
            b.build();r=m.run(m.P/'LOCAL_ARCHIVE_MANIFEST.json')
            assert r['closure_branch']=='EXTERNAL_PROCESS_LOSS' and r['M4_complete'] is False and r['partial_numerical_status']=='INCOMPLETE_NOT_PASSED' and r['native_worker_exit_code'] is None and r['partial_diagnostic_completed_counts'] is None and r['saved_only_verification']=='PASS'
            assert len(b.ANNEXES)==len(m.ANNEXES)==10 and b.ANNEXES==m.ANNEXES
            try:b.build()
            except FileExistsError:return
            raise AssertionError('Archive was overwritten')
    test('builder_to_reproducer_external_fixture_create_only_no_numerical',synthetic_archive)
    fixture()
    with patch.object(b,'metadata_policy',lambda:m):
        edit(m.E/'EXTERNAL_SCIENTIFIC_STOP.json','M4_complete',True)
        test('builder_denies_invalid_external_branch',b.build,True)
    report={'mission':m.MISSION,'scope':'SYNTHETIC_METADATA_ONLY_EXTERNAL_CLOSURE','tests':outcomes,'test_count':len(outcomes),'failed':0,'real_saved_bundle_reads':0,'real_archive_or_reproduction_runs':0,'new_fits_derivatives_scores':0,'NPZ_decodes':0,'source_sha256':{n:digest(E/n) for n in ['reproduce_saved.py','build_archive.py','test_external_closure.py']}}
    output=E/('EXTERNAL_TOOLING_SYNTHETIC_TEST_RESULT_'+str(args.receipt_id)+'.json')
    with output.open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'test_count':len(outcomes),'failed':0,'result':str(output),'sha256':digest(output)}))
finally:
    holder.cleanup()
