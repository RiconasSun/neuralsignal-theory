"""Temporary synthetic saved-artifact parser tests; no model or real-state execution."""
import argparse,ast,copy,datetime,importlib.util,json,os,tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np

E=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r5_saved_tooling',E/'reproduce_saved.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
outcomes=[]
parser=argparse.ArgumentParser();parser.add_argument('--receipt-id',type=int,default=1);args=parser.parse_args()
assert args.receipt_id>=1

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,allow_nan=False),encoding='utf8')

def test(name,call,reject=False):
    try:call()
    except (AssertionError,KeyError,ValueError,FileNotFoundError) as exc:
        if not reject:raise
        outcomes.append({'name':name,'status':'PASS','observed_rejection':type(exc).__name__});return
    if reject:raise AssertionError('Required rejection absent: '+name)
    outcomes.append({'name':name,'status':'PASS'})

def npz(path,arrays):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:np.savez_compressed(f,**arrays)
    return {'path':m.rel(path),'sha256':m.sha(path),'arrays':{k:m.identity(v) for k,v in arrays.items()}}

temp_parent=E/'REPRO_TOOLING_TEMP'
temp_parent.mkdir(exist_ok=True)
holder=tempfile.TemporaryDirectory(prefix='p16_r5_saved_tooling_',dir=temp_parent)
root=Path(holder.name).resolve()
assert root.name.startswith('p16_r5_saved_tooling_') and root.parent==temp_parent.resolve()
try:
    m.R=root;m.P=root/'paper16_development_r5';m.E=root/m.EP
    m.P.mkdir(parents=True);m.E.mkdir(parents=True)
    test('local_relative_path',lambda:m.local('paper16_development_r5/example.json'))
    for i,name in enumerate(['../escape','x/../y','x/./y','/absolute','C:/outside','//host/share','\\\\host\\share','x:stream','x\\y']):
        test('deny_nonlocal_path_'+str(i),lambda name=name:m.local(name),True)
    tasks=[{'id':'t0'},{'id':'t1'}]
    att=lambda t:{'event':'ATTEMPTED','task':t,'ftol':0.,'initializer':'ORIGINAL_FROZEN_ONLY'}
    done=lambda t:{'event':'COMPLETED','task':t}
    fail=lambda t:{'event':'FAILED','task':t,'type':'SyntheticFailure','message':'injected','retry':False}
    test('serial_task_complete_prefix',lambda:m.strict_tasks([att(tasks[0]),done(tasks[0]),att(tasks[1])],tasks))
    test('serial_task_actual_failure',lambda:m.strict_tasks([att(tasks[0]),fail(tasks[0])],tasks))
    test('deny_parallel_attempts',lambda:m.strict_tasks([att(tasks[0]),att(tasks[1])],tasks),True)
    test('deny_wrong_terminal',lambda:m.strict_tasks([att(tasks[0]),done(tasks[1])],tasks),True)
    test('deny_work_after_failure',lambda:m.strict_tasks([att(tasks[0]),fail(tasks[0]),att(tasks[1])],tasks),True)
    drows=list(m.diagnostic_sequence(1))
    test('full_derivative_reservation_sequence',lambda:m.diagnostic_journal(drows,1,True))
    test('partial_derivative_reservation_prefix',lambda:m.diagnostic_journal(drows[:5],1,False))
    test('deny_missing_derivative_reservations',lambda:m.diagnostic_journal(drows[:5],1,True),True)
    test('deny_reordered_derivative_reservations',lambda:m.diagnostic_journal(drows[1:]+drows[:1],1,True),True)
    boolrows=copy.deepcopy(drows);boolrows[0]['index']=True
    test('deny_boolean_diagnostic_counter',lambda:m.diagnostic_journal(boolrows,1,True),True)
    lo=np.array([-1.]);hi=np.array([1.]);calls=[{'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]},{'event':'COMPLETED','call':1,'objective':0.,'gradient_inf':0.,'gradient':[0.]}]
    accepted=[{'iteration':1,'x':[0.]}]
    result={'nfev':1,'nit':1,'external_value_gradient_pairs':1,'external_accepted_iterations':1,'accepted_vector_count':1,'x':[0.],'objective':0.}
    test('R5_full_FG_association',lambda:m.fg_journal(calls,accepted,1,lo,hi,'R5',True,result))
    scalar=[{k:v for k,v in calls[0].items() if k!='x'},{k:v for k,v in calls[1].items() if k!='gradient'}]
    test('R3_original_scalar_schema_preserved',lambda:m.fg_journal(scalar,accepted,1,lo,hi,'R3',True,result))
    test('deny_R5_scalar_substitution',lambda:m.fg_journal(scalar,accepted,1,lo,hi,'R5',True,result),True)
    test('partial_reserved_FG_not_completed',lambda:m.fg_journal(calls[:1],[],1,lo,hi,'R5',False))
    test('deny_reordered_FG',lambda:m.fg_journal(calls[::-1],accepted,1,lo,hi,'R5',True,result),True)
    test('deny_wrong_accepted_association',lambda:m.fg_journal(calls,[{'iteration':1,'x':[.2]}],1,lo,hi,'R5',True,result),True)
    test('deny_boolean_accepted_counter',lambda:m.fg_journal(calls,[{'iteration':True,'x':[0.]}],1,lo,hi,'R5',True,result),True)
    folder=m.P/'synthetic_fit';folder.mkdir();task={'id':'fixture'}
    init=npz(folder/'initial.npz',{'x0':np.array([0.]),'lo':lo,'hi':hi})
    end=npz(folder/'endpoint.npz',{'x':np.array([0.]),'gradient':np.array([0.])})
    values={};checkpoints=[]
    for name in ['initial','halfway','endpoint']:
        for key in ['_x','_analytic','_AD','_AD_error']:values[name+key]=np.array([0.])
        errs={}
        for h in [.001,.0001,.00001,.000001]:
            values[name+'_FD_'+str(h)]=np.array([0.]);values[name+'_FD_error_'+str(h)]=np.array([0.]);errs[str(h)]=0.
        checkpoints.append({'checkpoint':name,'objective':0.,'AD_objective':0.,'AD_scaled_coordinate_error_max':0.,'FD_scaled_coordinate_errors':errs,'frozen_FD_scaled_error':0.,'pass':True})
    coord=npz(folder/'coordinate_certificates.npz',values)
    diag={'coordinate_state':coord,'free_coordinates':1,'checkpoints':checkpoints,'FD_objective_calls':24,'AD_calls':3,'analytic_checkpoint_calls':3,'FD_step_not_selected_post_result':True,'all_checkpoints_pass':True}
    write(folder/'DIAGNOSTICS.json',diag);write(folder/'ATTEMPT.json',{'task':task,'parameters':1,'no_retry':True,'bounds':init})
    result.update(task=task,jac=[0.],fun=0.,success=True,message='SYNTHETIC_SAVED_CERTIFICATE',halfway_accepted_iteration=1,numerical_pass=True,projected_gradient_inf=0.,endpoint_state=end,diagnostic_state_sha256=m.sha(folder/'DIAGNOSTICS.json'))
    for filename,rows in [('CALLS.jsonl',calls),('ACCEPTED.jsonl',accepted),('DIAGNOSTIC_CALLS.jsonl',drows)]:
        (folder/filename).write_text(''.join(json.dumps(row)+'\n' for row in rows),encoding='utf8')
    test('synthetic_full_saved_coordinate_certificate',lambda:m.coordinates(folder,result,'R5'))
    altered=copy.deepcopy(result);altered['x']=[.2]
    test('deny_RESULT_endpoint_substitution',lambda:m.coordinates(folder,altered,'R5'),True)
    bad=copy.deepcopy(diag);bad['FD_step_not_selected_post_result']=False;write(folder/'DIAGNOSTICS.json',bad)
    altered=copy.deepcopy(result);altered['diagnostic_state_sha256']=m.sha(folder/'DIAGNOSTICS.json')
    test('deny_favorable_FD_policy_flag',lambda:m.coordinates(folder,altered,'R5'),True)
    write(folder/'DIAGNOSTICS.json',diag)
    badreceipt=copy.deepcopy(coord);badreceipt['path']='//outside/share/state.npz'
    with patch.object(m.np,'load',side_effect=RuntimeError('NPZ must not be reached')):
        test('deny_UNC_before_NPZ_read',lambda:m.receipt(folder,'coordinate_certificates.npz',badreceipt),True)
        badreceipt['path']=m.rel(folder/'initial.npz')
        test('deny_same_repository_receipt_substitution_before_read',lambda:m.receipt(folder,'coordinate_certificates.npz',badreceipt),True)
        hidden=copy.deepcopy(coord);hidden['arrays']['raw_neural_counts']={'shape':[1],'dtype':'<f8','sha256':'irrelevant'}
        test('deny_unregistered_NPZ_members_before_decode',lambda:m.receipt(folder,'coordinate_certificates.npz',hidden),True)
    review=m.E/'SYNTHETIC_REVIEW.md';review.write_text('Synthetic parser fixture, not actual approval')
    approval_manifest=m.P/'SYNTHETIC_REVIEW_MANIFEST.json';write(approval_manifest,{'files':[]})
    valid_approval={'mission':m.MISSION,'decision':'SYNTHETIC_ACCEPTED','open_P0':0,'open_P1':0,'manifest_path':m.rel(approval_manifest),'manifest_sha256':m.sha(approval_manifest),'review_path':m.rel(review),'review_sha256':m.sha(review)}
    approval_path=m.E/'SYNTHETIC_APPROVAL.json';write(approval_path,valid_approval)
    test('approval_exact_bindings',lambda:m.approval('SYNTHETIC_APPROVAL.json','SYNTHETIC_ACCEPTED',approval_manifest))
    for key,value in [('decision','REJECTED'),('open_P1',1),('manifest_sha256','wrong'),('review_sha256','wrong')]:
        bad=copy.deepcopy(valid_approval);bad[key]=value;write(approval_path,bad)
        test('deny_invalid_approval_'+key,lambda:m.approval('SYNTHETIC_APPROVAL.json','SYNTHETIC_ACCEPTED',approval_manifest),True)
    write(approval_path,valid_approval)
    phase={'mission':m.MISSION,'phase':'B_A_M4','no_reset':True,'start_UTC':'2020-01-01T00:00:00+00:00','deadline_UTC':'2020-01-03T00:00:00+00:00','start_monotonic':1.,'deadline_monotonic':172801.,'windows_boot_UTC':'SYNTHETIC_BOOT'}
    write(m.P/'results/STAGE_CLAIM.json',phase);write(m.P/'PHASE_A_CLAIM.json',{'windows_boot_UTC':'SYNTHETIC_BOOT'})
    write(m.P/'results/SUPERVISOR.json',{'stage_sha256':m.sha(m.P/'results/STAGE_CLAIM.json'),'supervisor_pid':42,'job_name':'Local\\P16_R5_42_123'})
    native={'returncode':1,'killed_at_deadline':False,'completed_before_deadline':True,'native_job_tree_enforced':True,'assigned_before_resume':True,'job_name':'Local\\P16_R5_42_123','clock_failure':None}
    write(m.P/'results/SUPERVISION.json',native);test('native_typed_stage_binding',m.stage_and_native)
    for key,value in [('returncode',True),('job_name','OTHER'),('assigned_before_resume',False)]:
        bad=copy.deepcopy(native);bad[key]=value;write(m.P/'results/SUPERVISION.json',bad)
        test('deny_native_'+key,m.stage_and_native,True)
    write(m.P/'results/SUPERVISION.json',native)
    frozen=root/'paper16_m1/code/frozen.txt';frozen.parent.mkdir(parents=True);frozen.write_text('synthetic source only')
    for reference in m.REFERENCES:write(m.local(reference),{'files':[{'path':m.rel(frozen),'sha256':m.sha(frozen)}]})
    def archive():
        paths={p for base in m.ROOTS for p in m.local(base).rglob('*') if p.is_file() and m.rel(p) not in m.ANNEXES};paths.add(frozen)
        rows=[{'path':m.rel(p),'sha256':m.sha(p),'bytes':p.stat().st_size} for p in sorted(paths)]
        return {'schema':'R5_LOCAL_ARCHIVE_V1','mission':m.MISSION,'base':m.BASE,'inventory_roots':m.ROOTS,'historical_reference_manifests':m.REFERENCES,'public_manifest':None,'exclusions':[{'path':p,'reason':r} for p,r in sorted(m.ANNEXES.items())],'files':rows,'file_count':len(rows)}
    manifest=m.P/'LOCAL_ARCHIVE_MANIFEST.json';a=archive();write(manifest,a)
    test('exact_closed_archive_inventory',lambda:m.check_archive(manifest))
    bad=copy.deepcopy(a);bad['files']=[];bad['file_count']=0;write(manifest,bad)
    test('deny_empty_archive',lambda:m.check_archive(manifest),True)
    bad=copy.deepcopy(a);bad['exclusions'].append({'path':m.rel(folder/'initial.npz'),'reason':m.CACHE_REASON});write(manifest,bad)
    test('deny_arbitrary_protected_exclusion',lambda:m.check_archive(manifest),True)
    write(manifest,a);(m.P/'unlisted.json').write_text('{}')
    test('deny_unlisted_later_file',lambda:m.check_archive(manifest),True)
    # No run() call: real terminal/archive and protected states are deliberately absent.
finally:
    assert root.resolve().parent==temp_parent.resolve() and root.name.startswith('p16_r5_saved_tooling_')
    holder.cleanup()

real_root=Path(__file__).resolve().parents[4]
m.R=real_root;m.P=real_root/'paper16_development_r5';m.E=E
tree=ast.parse((E/'reproduce_saved.py').read_text())
imports=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]+[n.name for node in ast.walk(tree) if isinstance(node,ast.Import) for n in node.names]
assert all(not x.startswith(('paper16','scipy','torch','jax','requests')) for x in imports)
frozen=json.loads((real_root/'paper16_development_r5/PREFIT_FREEZE_MANIFEST_V3.json').read_bytes())
producer_names={'paper16_development_r5/'+n for n in ['controller.py','core.py','optimizer.py','models.py','features.py','evidence_checks.py']}
producer_rows=[row for row in frozen['files'] if row['path'] in producer_names]
assert len(producer_rows)==6 and all(m.sha(real_root/row['path'])==row['sha256'] for row in producer_rows)
record={'mission':m.MISSION,'scope':'SYNTHETIC_SAVED_TOOLING_ONLY','completed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':outcomes,'passed':len(outcomes),'failed':0,'reproducer_sha256':m.sha(E/'reproduce_saved.py'),'test_sha256':m.sha(__file__),'source_imports':imports,'frozen_producer_sources_unchanged':producer_rows,'full_real_reproduction_executed':False,'real_state_reads':0,'scientific_model_calls':0,'new_fits_derivatives_scores':0,'scientific_or_M4_PASS_claimed':False}
target=E/('REPRO_TOOLING_SYNTHETIC_TEST_RESULT_'+str(args.receipt_id)+'.json')
with target.open('x',encoding='utf8',newline='\n') as f:json.dump(record,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'synthetic_saved_tooling_tests_passed':len(outcomes),'real_reproduction_executed':False,'result_sha256':m.sha(target)}))
