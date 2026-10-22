"""Closed-archive saved-only R5 verification. Never import or evaluate models."""
import argparse,collections,datetime,hashlib,json,math,os,socket,stat
from pathlib import Path,PurePosixPath,PureWindowsPath
import numpy as np

R=Path(__file__).resolve().parents[4];P=R/'paper16_development_r5';E=Path(__file__).resolve().parent
EP=E.relative_to(R).as_posix();MISSION='P16-M3-M5-SHUTDOWN-RECOVERY-R5'
BASE='b7bb1227379462c2c7a1cef40ab0d0e99a6d020b';Q='paper16_shutdown_recovery_r5_protocol'
ROOTS=['paper16_development_r5',EP]
REFERENCES=['paper16_development_r5/INDEPENDENT_R5_PROTECTED_HASH_READBACK.json','paper16_development_r5/PREFIT_FREEZE_MANIFEST_V3.json']
ANNEXES={
 'paper16_development_r5/LOCAL_ARCHIVE_MANIFEST.json':'Create-only inventory self reference',
 'paper16_development_r5/PUBLICATION_MANIFEST.json':'Separate prospective publication annex; no transmission authorized',
 **{EP+'/'+n:'Postarchive saved-only closure annex; independently bound by final review' for n in
 ['SAVED_REPRODUCTION.log','SAVED_REPRODUCTION_RECEIPT.json','FINAL_REVIEW.md','review.md','FINAL_REVIEW_BINDING.json','verdict.md','REQUIREMENT_VERIFICATION.json','LOCAL_COMMIT_RECEIPT.json']}}
CACHE_REASON='Nonpublication cache or local Git closure receipt, excluded explicitly at freeze'
CAPS={'FG_reserved':14874000,'accepted_iterations':3718500,'FD_RESERVED':21894528,'AD_RESERVED':7437,'ANALYTIC_RESERVED':7437}

def need(value,message):
    if not value:raise AssertionError(message)

def local(name):
    """Reject UNC, drives, ADS, traversal and redirects before filesystem access."""
    need(isinstance(name,str) and name and '\\' not in name and ':' not in name,'Canonical local relative path required')
    p=PurePosixPath(name)
    need(not p.is_absolute() and not PureWindowsPath(name).drive and name==p.as_posix() and all(x not in ['.','..'] for x in p.parts),'Noncanonical/external path')
    path=R.joinpath(*p.parts)
    cursor=R
    for part in p.parts:
        cursor=cursor/part
        try:entry=cursor.lstat()
        except FileNotFoundError:break
        need(not stat.S_ISLNK(entry.st_mode) and not (getattr(entry,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT),'Symbolic/junction/reparse archive path denied')
    need(path.resolve()==path.absolute() and path.resolve().is_relative_to(R.resolve()),'Redirected/nonlocal archive path')
    return path

def rel(path):return Path(path).absolute().relative_to(R).as_posix()
def walk_files(root):
    """Check each entry without following redirects before descending into it."""
    root=local(rel(root))
    for entry in os.scandir(root):
        record=entry.stat(follow_symlinks=False)
        need(not stat.S_ISLNK(record.st_mode) and not (getattr(record,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT),'Symbolic/junction/reparse inventory entry denied')
        path=Path(entry.path)
        if stat.S_ISDIR(record.st_mode):yield from walk_files(path)
        elif stat.S_ISREG(record.st_mode):yield path
        else:need(False,'Unsupported inventory entry type')
def load(path):return json.loads(local(rel(path)).read_bytes())
def sha(path):
    with local(rel(path)).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def integer(value,lo,hi):return type(value) is int and lo<=value<=hi
def lines(path,allow_torn=False,issues=None):
    p=local(rel(path))
    if not p.exists():return []
    raw=p.read_bytes()
    if raw and not raw.endswith(b'\n'):
        need(allow_torn and issues is not None,'Nonempty closed journal requires terminal LF')
        cut=raw.rfind(b'\n')+1;tail=raw[cut:]
        try:json.loads(tail.decode('utf8'));valid=True
        except (ValueError,UnicodeDecodeError):valid=False
        issues.append({'path':rel(p),'status':'TORN_SUFFIX_NOT_AN_ATOMIC_RECORD','file_sha256':hashlib.sha256(raw).hexdigest(),'complete_prefix_bytes':cut,'uncommitted_suffix_bytes':len(tail),'suffix_sha256':hashlib.sha256(tail).hexdigest(),'suffix_is_valid_JSON_without_LF':valid,'suffix_counted_as_complete':False})
        raw=raw[:cut]
    values=raw[:-1].split(b'\n') if raw else []
    need(all(x.strip() for x in values),'Blank/torn journal entry')
    return [json.loads(x.decode('utf8')) for x in values]
def identity(a):return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}

def verify_rows(rows):
    need(isinstance(rows,list),'File inventory list');names=[r['path'] for r in rows]
    need(len(names)==len(set(names)),'Unique file inventory')
    for row in rows:
        p=local(row['path']);need(p.is_file() and sha(p)==row['sha256'],'Saved file identity: '+row['path'])
        if 'bytes' in row:need(p.stat().st_size==row['bytes'],'Saved file size')
    return set(names)

def check_archive(manifest):
    a=load(manifest)
    need(a['schema']=='R5_LOCAL_ARCHIVE_V1' and a['mission']==MISSION and a['base']==BASE,'Exact archive mission/base/schema')
    need(a['inventory_roots']==ROOTS and a['historical_reference_manifests']==REFERENCES,'Exact archive roots/references')
    need(a.get('public_manifest') is None,'Public annex must not create an archive hash cycle')
    exclusions=a['exclusions'];names=[x['path'] for x in exclusions]
    need(len(names)==len(set(names)) and set(ANNEXES)<=set(names),'Exact fixed annex exclusions required')
    for row in exclusions:
        path=local(row['path']);name=row['path']
        if name in ANNEXES:need(row['reason']==ANNEXES[name],'Frozen fixed-annex reason')
        else:
            need(row['reason']==CACHE_REASON and path.is_file(),'Only actually discovered cache/local-only exclusions')
            need('__pycache__' in PurePosixPath(name).parts or path.is_relative_to(E/'LOCAL_ONLY'),'Arbitrary exclusion forbidden')
            need(any(path.is_relative_to(local(root)) for root in ROOTS),'Exclusion outside declared roots')
    inventory=set()
    for root in ROOTS:
        for path in walk_files(local(root)):
            name=rel(path)
            if name not in names:inventory.add(name)
    reference_names=set()
    for reference in REFERENCES:
        for row in load(local(reference))['files']:
            local(row['path']);reference_names.add(row['path']);need(row['path'] not in names,'Frozen reference cannot be excluded')
    expected=inventory|reference_names;actual={row['path'] for row in a['files']}
    need(actual==expected and a['file_count']==len(a['files'])==len(expected),'Complete exact closed archive inventory')
    verify_rows(a['files']);index={row['path']:row for row in a['files']}
    for reference in REFERENCES:
        for row in load(local(reference))['files']:need(index[row['path']]['sha256']==row['sha256'],'Frozen external reference identity')
    return a,index

def receipt(folder,name,row):
    path=local(row['path']);need(path==Path(folder)/name,'Exact expected same-folder state receipt')
    need(sha(path)==row['sha256'],'Saved state file hash')
    expected={'initial.npz':{'x0','lo','hi'},'endpoint.npz':{'x','gradient'}}.get(name)
    if name=='coordinate_certificates.npz':expected={n+s for n in ['initial','halfway','endpoint'] for s in ['_x','_analytic','_AD','_AD_error']+['_FD_'+str(h) for h in [.001,.0001,.00001,.000001]]+['_FD_error_'+str(h) for h in [.001,.0001,.00001,.000001]]}
    need(expected is not None and set(row['arrays'])==expected,'Only exact registered saved-fit array members')
    with np.load(path,allow_pickle=False) as z:
        need(set(z.files)==expected,'Unexpected NPZ member denied before array decode')
        values={k:z[k].copy() for k in z.files}
    need({k:identity(v) for k,v in values.items()}==row['arrays'],'Saved array-member hashes');return values

def projected(x,g,lo,hi):return np.where(((x<=lo+1e-12)&(g>0))|((x>=hi-1e-12)&(g<0)),0,g)

def diagnostic_sequence(p):
    fd=ad=analytic=0
    for name in ['initial','halfway','endpoint']:
        analytic+=1;yield {'kind':'ANALYTIC_RESERVED','checkpoint':name,'index':analytic}
        ad+=1;yield {'kind':'AD_RESERVED','checkpoint':name,'index':ad}
        for h in [.001,.0001,.00001,.000001]:
            for k in range(p):
                for side in ['plus','minus']:
                    fd+=1;yield {'kind':'FD_RESERVED','checkpoint':name,'index':fd,'h':h,'coordinate':k,'side':side}

def diagnostic_journal(rows,p,complete):
    expected=diagnostic_sequence(p);counts=collections.Counter()
    for row in rows:
        original=next(expected,None)
        need(row==original and all(type(row[k]) is type(v) for k,v in original.items()),'Exact typed diagnostic reservation sequence/prefix')
        counts[row['kind']]+=1
    if complete:need(next(expected,None) is None,'Complete 24P/3/3 diagnostic journal')
    return counts

def fg_journal(calls,accepted,p,lo,hi,origin,complete,result=None):
    need(len(calls)<=12000 and len(accepted)<=1500,'Original per-fit journal caps');assoc={}
    for k,row in enumerate(calls):
        before=k%2==0
        need(row['event']==('RESERVED_BEFORE_EVALUATION' if before else 'COMPLETED') and type(row['call']) is int and row['call']==k//2+1,'Strict alternating FG journal')
        if before:
            need(integer(row['iterations'],0,len(accepted)),'FG accepted counter prefix')
            if origin!='R3':
                x=np.asarray(row['x']);need(x.shape==(p,) and np.isfinite(x).all() and np.all(x>=lo-1e-12) and np.all(x<=hi+1e-12),'Finite bounded full FG vector')
        else:
            need(math.isfinite(row['objective']) and math.isfinite(row['gradient_inf']),'Finite saved FG scalars')
            if origin!='R3':
                g=np.asarray(row['gradient']);need(g.shape==(p,) and np.isfinite(g).all() and row['gradient_inf']==float(np.abs(g).max()),'Full FG gradient/norm identity')
            assoc[calls[k-1]['iterations']]=(calls[k-1],row)
    for i,row in enumerate(accepted):
        x=np.asarray(row['x']);need(type(row['iteration']) is int and row['iteration']==i+1 and x.shape==(p,) and np.isfinite(x).all() and np.all(x>=lo-1e-12) and np.all(x<=hi+1e-12),'Ordered finite bounded accepted vectors')
        if origin!='R3':need(i in assoc and np.array_equal(x,assoc[i][0]['x']),'Accepted/FG vector association')
    if complete:
        n,nit=result['nfev'],result['nit']
        need(integer(n,1,6000) and integer(nit,0,1500) and len(calls)==2*n and len(accepted)==nit and result['external_value_gradient_pairs']==n and result['external_accepted_iterations']==nit and result['accepted_vector_count']==nit,'Complete exact external counters')
        if accepted:need(np.array_equal(accepted[-1]['x'],result['x']),'Last accepted endpoint')
        if origin!='R3':need(assoc[nit-1 if nit else 0][1]['objective']==result['objective'],'Endpoint objective/FG association')
    return {'FG_reserved':(len(calls)+1)//2,'FG_completed':len(calls)//2,'accepted_iterations':len(accepted)}

def coordinates(folder,result,origin,required_pass=True,b0=False):
    d=load(folder/'DIAGNOSTICS.json')
    if not b0:need(sha(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Diagnostics/result hash')
    c=receipt(folder,'coordinate_certificates.npz',d['coordinate_state'])
    if b0:initial={'x0':c['initial_x'],'lo':np.array([-10.]),'hi':np.array([10.])};end={'x':c['endpoint_x'],'gradient':c['endpoint_analytic']}
    else:
        attempt=load(folder/'ATTEMPT.json');need(attempt['task']==result['task'] and attempt['no_retry'] is True,'Attempt/result task/no-retry')
        initial=receipt(folder,'initial.npz',attempt['bounds']);end=receipt(folder,'endpoint.npz',result['endpoint_state'])
    p=len(initial['x0']);lo,hi=initial['lo'],initial['hi']
    need(integer(p,1,368) and all(x.shape==(p,) and x.dtype==np.dtype('float64') and np.isfinite(x).all() for x in [initial['x0'],lo,hi]) and np.all(lo<=hi),'Original finite float64 packing/bounds')
    if not b0:need(attempt['parameters']==p,'Attempt/free-coordinate identity')
    need(d['free_coordinates']==p and len(d['checkpoints'])==3,'Three complete checkpoints')
    need((d['FD_objective_calls'],d['AD_calls'],d['analytic_checkpoint_calls'])==(24*p,3,3) and d['FD_step_not_selected_post_result'] is True,'Original fixed diagnostic policy/budgets')
    passes=[];pgs={}
    for name,row in zip(['initial','halfway','endpoint'],d['checkpoints']):
        x,g,ad=[c[name+k] for k in ['_x','_analytic','_AD']]
        need(all(a.shape==(p,) and a.dtype==np.dtype('float64') and np.isfinite(a).all() for a in [x,g,ad]),'Finite float64 full coordinates')
        need(np.all(x>=lo-1e-12) and np.all(x<=hi+1e-12),'Original checkpoint bounds')
        error=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
        need(c[name+'_AD_error'].dtype==np.dtype('float64') and np.array_equal(error,c[name+'_AD_error']) and float(error.max())==row['AD_scaled_coordinate_error_max'],'Saved float64 AD coordinate arithmetic')
        for h in [.001,.0001,.00001,.000001]:
            fd=c[name+'_FD_'+str(h)];delta=np.abs(fd-g)/np.maximum(1,np.maximum(np.abs(fd),np.abs(g)))
            need(fd.shape==(p,) and fd.dtype==c[name+'_FD_error_'+str(h)].dtype==np.dtype('float64') and np.isfinite(fd).all() and np.array_equal(delta,c[name+'_FD_error_'+str(h)]) and float(delta.max())==row['FD_scaled_coordinate_errors'][str(h)],'Saved float64 four-scale FD arithmetic')
        need(row['checkpoint']==name and row['frozen_FD_scaled_error']==row['FD_scaled_coordinate_errors']['1e-05'],'Original fixed h1e-5 acceptance')
        need(math.isfinite(row['objective']) and math.isfinite(row['AD_objective']),'Finite saved checkpoint objectives')
        passed=bool(np.isclose(row['objective'],row['AD_objective'],atol=1e-10,rtol=1e-12) and row['AD_scaled_coordinate_error_max']<=1e-8 and row['frozen_FD_scaled_error']<=2e-5)
        need(type(row['pass']) is bool and row['pass']==passed,'Exact original checkpoint pass formula');passes.append(passed);pgs[name]=float(np.abs(projected(x,g,lo,hi)).max())
    need(type(d['all_checkpoints_pass']) is bool and d['all_checkpoints_pass']==all(passes),'Original checkpoint conjunction')
    need(all(a.dtype==np.dtype('float64') and a.shape==(p,) for a in end.values()) and np.array_equal(c['initial_x'],initial['x0']) and np.array_equal(c['endpoint_x'],end['x']) and np.array_equal(c['endpoint_analytic'],end['gradient']),'Float64 initial/full endpoint identities')
    passed=bool(pgs['endpoint']<=1e-5 and all(passes))
    if b0:
        need(result['analytic_MLE_not_optimizer_attempt'] is True and type(result['numeric_pass']) is bool and result['numeric_pass']==passed and all(np.array_equal(c[name+'_x'],initial['x0']) for name in ['initial','halfway','endpoint']),'Original B0 analytic labels')
    else:
        need(np.array_equal(result['x'],end['x']) and np.allclose(result['jac'],end['gradient'],atol=1e-12,rtol=1e-12),'Result/full endpoint identity')
        need(result['objective']==result['fun'] and np.isclose(result['objective'],d['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12),'Saved identical objective')
        need(type(result['numerical_pass']) is bool and result['numerical_pass']==passed and type(result['success']) is bool and isinstance(result['message'],str),'Numerical gate independent of solver success')
    need(result['projected_gradient_inf']==pgs['endpoint'] and (not required_pass or passed),'Original full PG/AD/fixed-FD gate')
    if not b0:
        accepted=lines(folder/'ACCEPTED.jsonl');mid=accepted[math.ceil(len(accepted)/2)-1]['x'] if accepted else result['x']
        need(np.array_equal(c['halfway_x'],mid) and result['halfway_accepted_iteration']==math.ceil(len(accepted)/2),'Original halfway accepted iterate')
        fg_journal(lines(folder/'CALLS.jsonl'),accepted,p,lo,hi,origin,True,result)
        if origin!='R3':diagnostic_journal(lines(folder/'DIAGNOSTIC_CALLS.jsonl'),p,True)
    return {'p':p,'PG':pgs['endpoint'],'checkpoint_PG':pgs,'passed':passed}

def strict_tasks(rows,plan):
    attempts=[];completed={};failed={};active=None;stopped=False
    for row in rows:
        event=row['event'];task=row['task'];tid=task['id'];need(event in ['ATTEMPTED','COMPLETED','FAILED'] and not stopped,'Typed serial tasks/no work after failure')
        if event=='ATTEMPTED':
            need(active is None and len(attempts)<len(plan) and task==plan[len(attempts)] and row['ftol']==0. and row['initializer']=='ORIGINAL_FROZEN_ONLY','Exact ordered once-only task/policy')
            attempts.append(task);active=task
        else:
            need(active==task and tid not in completed and tid not in failed,'Terminal/active exact task')
            if event=='COMPLETED':completed[tid]=row
            else:
                need(row['retry'] is False and isinstance(row['type'],str) and isinstance(row['message'],str),'Actual typed no-retry failure');failed[tid]=row;stopped=True
            active=None
    return attempts,completed,failed,active

def approval(name,decision,manifest):
    a=load(E/name);need(a['mission']==MISSION and a['decision']==decision and a['open_P0']==a['open_P1']==0,'Independent exact approval')
    need(a['manifest_sha256']==sha(manifest),'Approval/manifest hash')
    if 'manifest_path' in a:need(local(a['manifest_path'])==manifest,'Approval/manifest exact path')
    review=local(a['review_path']);need(review.is_relative_to(E) and sha(review)==a['review_sha256'],'Independent review local identity')
    verify_rows(load(manifest)['files']);return a

def reuse():
    prefit=approval('PREFIT_APPROVAL.json','ACCEPTED_R5_PRODUCTION_AND_COMPLETE_REUSE',P/'PREFIT_FREEZE_MANIFEST_V3.json')
    admission=load(P/'REUSE_ADMISSION.json');phase=load(P/'PHASE_A_CLAIM.json')
    need(admission['mission']==MISSION and admission['required_gate_pass'] is True and (admission['optimizer_states_admitted'],admission['B0_certificates_admitted'])==(3992,216),'Complete reuse admission')
    need(prefit['phase_A_claim_sha256']==admission['phase_A_claim_sha256']==sha(P/'PHASE_A_CLAIM.json') and phase['no_reset'] is True and abs(phase['deadline_monotonic']-phase['start_monotonic']-86400)<=1e-6,'Original Phase A binding/cap')
    acc=load(E/'INDEPENDENT_R5_REUSE_MATRIX_ACCEPTANCE.json')
    need(sha(E/'INDEPENDENT_R5_REUSE_MATRIX_ACCEPTANCE.json')==admission['independent_matrix_acceptance_sha256'] and acc['decision']=='ACCEPTED_COMPLETE_3992_216_REUSE_MATRIX' and acc['open_P0']==acc['open_P1']==0,'Complete independent reuse qualification')
    review=local(acc['review_path']);need(review.is_relative_to(E) and sha(review)==acc['review_sha256'],'Independent complete-matrix review identity')
    need(acc['phase_A_claim_sha256']==admission['phase_A_claim_sha256'] and acc['independent_result_sha256']==admission['independent_result_sha256']==sha(E/'INDEPENDENT_R5_REUSE_RESULT.json'),'Independent qualification/Phase A result bindings')
    need(sha(local(acc['B0_field_addendum_path']))==acc['B0_field_addendum_sha256'],'Preserved B0 status-field clarification binding')
    primary=load(P/'PRIMARY_AUDIT_V2_RESULT.json')
    need(sha(P/'PRIMARY_AUDIT_V2_RESULT.json')==admission['primary_result_sha256'] and primary['primary_saved_audit']=='PASS','Original primary result')
    need(primary['matrix_sha256']==acc['primary_optimizer_matrix_sha256']==sha(P/'PRIMARY_OPTIMIZER_V2_MATRIX.json') and primary['B0_matrix_sha256']==acc['primary_B0_matrix_sha256']==sha(P/'PRIMARY_B0_V2_MATRIX.json'),'Qualified primary matrices')
    targets=load(local(Q+'/REUSE_TARGETS.json'));matrix=load(P/'PRIMARY_OPTIMIZER_V2_MATRIX.json')['states']
    need(len(matrix)==3992 and len(targets['optimizer_targets'])==3992 and len(targets['B0_targets'])==216,'Full reuse denominator');lookup={}
    for row,target in zip(matrix,targets['optimizer_targets']):
        tid=target['task']['id'];origin=target['origin']
        need(tid not in lookup and row['task']==target['task'] and row['status']=='PASS' and row['origin']==origin and origin in ['R3','R4'] and row['historical_ftol']==target['historical_ftol']==(1e-12 if origin=='R3' else 0.),'Original distinct target/policy')
        expected='paper16_development_'+origin.lower()+'/work/fits/'+hashlib.sha256(tid.encode()).hexdigest()+'/RESULT.json'
        need(row['result_path']==target['result_path']==expected and row['result_sha256']==target['result_sha256']==sha(local(expected)),'Canonical qualified historical endpoint');lookup[tid]=target
    need(collections.Counter(t['origin'] for t in lookup.values())=={'R3':952,'R4':3040},'Historical origin counts')
    b0=load(P/'PRIMARY_B0_V2_MATRIX.json')['states'];need(len(b0)==216,'All B0 rows')
    for row,target in zip(b0,targets['B0_targets']):
        need(row['status']=='PASS' and row['mouse_id']==target['mouse_id'] and row['unit_id']==target['unit_id'] and row['result_path']==target['result_path'] and row['result_sha256']==target['result_sha256']==sha(local(target['result_path'])),'Qualified original B0 endpoint')
    return lookup,targets['B0_targets']

def stage_and_native():
    stage=load(P/'results/STAGE_CLAIM.json');sup=load(P/'results/SUPERVISOR.json');native=load(P/'results/SUPERVISION.json')
    need(stage['mission']==MISSION and stage['phase']=='B_A_M4' and stage['no_reset'] is True,'Original Phase B claim')
    first=datetime.datetime.fromisoformat(stage['start_UTC']);last=datetime.datetime.fromisoformat(stage['deadline_UTC'])
    need(first.utcoffset()==last.utcoffset()==datetime.timedelta(0) and abs((last-first).total_seconds()-172800)<=1e-6 and abs(stage['deadline_monotonic']-stage['start_monotonic']-172800)<=1e-6,'Exact original 48-hour interval')
    need(stage['windows_boot_UTC']==load(P/'PHASE_A_CLAIM.json')['windows_boot_UTC'],'Original same-boot Phase B')
    need(type(sup.get('supervisor_pid')) is int and sup['supervisor_pid']>0 and isinstance(sup.get('job_name'),str)
         and sup['job_name'].startswith('Local\\P16_R5_'+str(sup['supervisor_pid'])+'_')
         and sup['job_name'][len('Local\\P16_R5_'+str(sup['supervisor_pid'])+'_'):].isascii()
         and sup['job_name'][len('Local\\P16_R5_'+str(sup['supervisor_pid'])+'_'):].isdigit()
         and sup['stage_sha256']==sha(P/'results/STAGE_CLAIM.json'),'Original typed supervisor PID/exact Job/stage binding')
    need(type(native['returncode']) is int and type(native['killed_at_deadline']) is bool and type(native['completed_before_deadline']) is bool and native['native_job_tree_enforced'] is True and native['assigned_before_resume'] is True and native['job_name']==sup['job_name'],'Actual typed native Job terminal receipt')
    need(native.get('clock_failure') is None or isinstance(native['clock_failure'],str) and bool(native['clock_failure']),'Typed actual native clock outcome')
    if native.get('clock_failure'):need(native['completed_before_deadline'] is False,'Clock failure cannot be completed-before-deadline')
    return stage,native

def stop_category(type_name,message):
    """Pure transcription of the frozen producer's stop_category, no class imports."""
    if type_name=='NumericalStop':return 'STOP_NUMERICAL_REQUIRED_GATE'
    if type_name=='ProcessStop':return 'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'
    if type_name=='ResourceStop':return 'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE' if 'boot' in message.lower() else 'STOP_BUDGET_REQUIRED_GATE'
    if type_name=='BudgetStop':return 'STOP_BUDGET_REQUIRED_GATE'
    return 'STOP_ACCESS_OR_IMPLEMENTATION_REQUIRED_GATE'

def native_stop(native):
    # Frozen record_supervision precedence: killed, clock, returncode, zero/no completion.
    if native['killed_at_deadline']:return ('BudgetStop','Native whole-Job stage deadline')
    if native.get('clock_failure'):return ('ResourceStop',native['clock_failure'])
    if native['returncode']!=0:return ('ProcessStop','Native worker exit '+str(native['returncode'])+'; see actual supervision receipt')
    return ('ImplementationStop','Native zero exit without complete independently accepted M4 receipt')

def validate_stop(stop,native,failed,execution_log='',issues=()):
    kind=stop.get('type');message=stop.get('message')
    need(isinstance(kind,str) and bool(kind) and isinstance(message,str),'Typed original STOP exception')
    need(stop.get('scientific_status')==stop_category(kind,message),'STOP label must match frozen exception classifier')
    need(stop.get('no_retry') is True and stop.get('all_later_tasks_not_executed') is True
         and all(stop.get(k) is False for k in ['E_access','Final_C_access','Final_D_access']),'Irreversible original STOP boundary fields')
    pair=(kind,message);basis=None
    need(len(failed)<=1,'At most one actual FAILED terminal')
    if failed:
        row=next(iter(failed.values()))
        if pair==(row['type'],row['message']):
            need(native['returncode']!=0 or kind=='SystemExit' and message=='0','Unhandled worker failure cannot have successful native exit')
            basis='EXACT_ATOMIC_FAILED_TASK_EXCEPTION'
    if basis is None and pair==native_stop(native):basis='EXACT_NATIVE_PARENT_STOP_PRECEDENCE'
    if basis is None:
        tail=kind+': '+message
        logged=('Traceback (most recent call last):' in execution_log and 'controller.py' in execution_log
                and execution_log.rstrip('\r\n').endswith(tail))
        if native['returncode']!=0 and logged and kind!='NumericalStop':basis='EXACT_WORKER_EXCEPTION_TRACE_BOOTSTRAP_OR_INTERTASK'
    if basis is None:
        need(bool(issues),'STOP has no matching actual FAILED/native/worker-bootstrap evidence')
        return {'status':'INCOMPLETE','reported_scientific_status':stop['scientific_status'],'verified_scientific_status':None,'basis':'UNKNOWN_DUE_TO_TORN_JOURNAL_SUFFIX'}
    return {'status':'INCOMPLETE' if issues else 'VERIFIED','reported_scientific_status':stop['scientific_status'],
            'verified_scientific_status':stop['scientific_status'],'basis':basis}

def validate_terminal_metadata():
    """Metadata only, shared by builder and reproducer; never decode fitted arrays."""
    stop_path=local('paper16_development_r5/results/SCIENTIFIC_STOP.json');complete_path=local('paper16_development_r5/results/WORKER_COMPLETE.json')
    need(stop_path.exists()!=complete_path.exists(),'Exactly one actual terminal scientific state')
    stage,native=stage_and_native();issues=[]
    plan=[r['task'] for r in load(local(Q+'/RECOVERY_TASK_PLAN.json'))['tasks']]
    rows=lines(P/'results/FIT_JOURNAL.jsonl',allow_torn=stop_path.exists(),issues=issues)
    attempts,completed,failed,active=strict_tasks(rows,plan)
    if complete_path.exists():
        out=load(complete_path)
        need(out['M4'] is True and out['E'] is False and out['Final_C_D_access'] is False
             and native['returncode']==0 and not native['killed_at_deadline'] and native['completed_before_deadline']
             and native.get('clock_failure') is None and not failed and active is None,'Successful native/worker terminal consistency')
        need(len(plan)==2479 and attempts==plan and len(completed)==2479,'Actual complete-M4 task terminal coverage')
        approval('M4_APPROVAL.json','ACCEPTED_R5_COMPLETE_M4',P/'M4_REVIEW_MANIFEST.json')
        need(load(P/'M4_REVIEW_MANIFEST.json')['files']==[{'path':'paper16_development_r5/results/M4_SELECTION_FREEZE.json','sha256':sha(P/'results/M4_SELECTION_FREEZE.json')}],'Metadata approval binds exact M4 freeze')
        decision={'status':'VERIFIED','verified_scientific_status':'M4_COMPLETE_INDEPENDENTLY_ACCEPTED','reported_scientific_status':'M4_COMPLETE_INDEPENDENTLY_ACCEPTED','basis':'NATIVE_AND_WORKER_COMPLETE_PENDING_M4_BINDING'}
    else:
        log_path=local(EP+'/SCIENTIFIC_EXECUTION.log')
        text=log_path.read_bytes().decode('utf8',errors='replace') if log_path.exists() else ''
        decision=validate_stop(load(stop_path),native,failed,text,issues)
    return {'stage':stage,'native':native,'attempts':attempts,'completed':completed,'failed':failed,'active':active,
            'issues':issues,'decision':decision,'stopped':stop_path.exists()}

def check_m4(old,results,fullplan,index):
    approval('M4_APPROVAL.json','ACCEPTED_R5_COMPLETE_M4',P/'M4_REVIEW_MANIFEST.json')
    need(load(P/'M4_REVIEW_MANIFEST.json')['files']==[{'path':'paper16_development_r5/results/M4_SELECTION_FREEZE.json','sha256':sha(P/'results/M4_SELECTION_FREEZE.json')}],'Independent approval must bind the exact complete M4 freeze')
    freeze=load(P/'results/M4_SELECTION_FREEZE.json')
    need(freeze['mission']==MISSION and freeze['selected_lambda']==1. and freeze['lambda_origin']=='HISTORICAL_R3_B1_SELECTION' and freeze['task_plan_sha256']==sha(local('paper16_development_r3/results/TASK_PLAN.json')) and freeze['B0_count']==216 and freeze['all_original_thresholds_unchanged'] is True and freeze['E_authorized'] is False and freeze['Final_authorized'] is False,'Exact original complete M4 scope')
    origins=freeze['task_origins'];need(len(origins)==6471 and [x['task_id'] for x in origins]==[t['id'] for t in fullplan],'All original ordered M4 tasks');groups={};required=set()
    for task,origin in zip(fullplan,origins):
        tid=task['id'];folder=local(old[tid]['result_path']).parent if tid in old else P/'work/fits'/hashlib.sha256(tid.encode()).hexdigest()
        need(origin['origin']==(old[tid]['origin'] if tid in old else 'R5') and local(origin['result_path'])==folder/'RESULT.json' and origin['result_sha256']==sha(folder/'RESULT.json'),'Every exact state origin/result')
        result=results[tid];need(result['numerical_pass'] is True,'All selected/nonselected states pass');required.update(rel(x) for x in folder.iterdir() if x.is_file())
        if task['model'] in ['D','S']:groups.setdefault((task['mouse_id'],task['panel'],task['model']),[]).append({'seed':task['seed'],'numerical_pass':True,'objective':result['objective']})
    for row in load(local(Q+'/REUSE_TARGETS.json'))['B0_targets']:
        required.update(rel(x) for x in local(row['result_path']).parent.iterdir() if x.is_file())
    required.update(x['path'] for x in load(local('paper16_development_r3/results/A_PREPROCESSING_STATES.json')))
    required.update(x['path'] for x in load(P/'PREFIT_FREEZE_MANIFEST_V3.json')['files'])
    required.update(['paper16_development_r5/PREFIT_FREEZE_MANIFEST_V3.json','paper16_development_r5/REUSE_ADMISSION.json','paper16_development_r3/results/B_SELECTION.json','paper16_development_r3/results/A_PREPROCESSING_STATES.json','paper16_development_r3/results/PANEL_PREFIT_PLAN.json','paper16_development_r5/results/FIT_JOURNAL.jsonl','paper16_development_r5/results/INITIALIZER_IDENTITIES.jsonl','paper16_development_r5/results/STAGE_CLAIM.json','paper16_development_r5/results/SUPERVISOR.json'])
    rows=freeze['states'];need(required<={x['path'] for x in rows},'Complete M4 fit/B0/preparation/provenance evidence');verify_rows(rows)
    for row in rows:need(row['path'] in index and index[row['path']]['sha256']==row['sha256'],'Every M4 state archived')
    selected={(r['mouse_id'],r['panel'],r['model']):r for r in freeze['selected_seeds']};need(len(selected)==len(freeze['selected_seeds']) and set(selected)==set(groups),'All D/S panel seed groups')
    for key,rows in groups.items():
        need(sorted(x['seed'] for x in rows)==[11,23,37] and selected[key]['all_seeds']==rows,'All three unchanged seeds')
        minimum=min(x['objective'] for x in rows);winner=min(x['seed'] for x in rows if x['objective']<=minimum+1e-12);need(selected[key]['seed']==winner,'Original saved A-objective/tie rule')

def run(manifest):
    manifest=local(rel(Path(manifest).absolute()));need(manifest==P/'LOCAL_ARCHIVE_MANIFEST.json','Exact local closed archive path')
    archive,index=check_archive(manifest);stop_path=local('paper16_development_r5/results/SCIENTIFIC_STOP.json');complete_path=local('paper16_development_r5/results/WORKER_COMPLETE.json')
    terminal_meta=validate_terminal_metadata();native=terminal_meta['native'];issues=terminal_meta['issues'];stopped=terminal_meta['stopped'];decision=terminal_meta['decision']
    old,b0=reuse();plan=[r['task'] for r in load(local(Q+'/RECOVERY_TASK_PLAN.json'))['tasks']];fullplan=load(local('paper16_development_r3/results/TASK_PLAN.json'))['tasks']
    need(len(plan)==2479 and len(fullplan)==6471 and len({t['id'] for t in fullplan})==6471 and not set(old)&{t['id'] for t in plan} and set(old)|{t['id'] for t in plan}=={t['id'] for t in fullplan},'Exact disjoint6471 task accountability')
    attempts,completed,failed,active=[terminal_meta[k] for k in ['attempts','completed','failed','active']]
    initializers=lines(P/'results/INITIALIZER_IDENTITIES.jsonl',allow_torn=stopped,issues=issues)
    need([x['task_id'] for x in initializers]==[t['id'] for t in attempts[:len(initializers)]] and len(initializers)<=len(attempts),'Ordered original initializer ledger')
    totals=collections.Counter();results={};passed=0;max_pg=0.;saved_endpoints=0;nonpassing_saved_endpoints=0
    for i,task in enumerate(attempts):
        folder=P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest();tid=task['id'];consumption=P/'results/attempt_consumption'/folder.name
        need(load(consumption)=={'task':task,'no_retry':True},'Atomic original attempt consumption');terminal=completed.get(tid);result=load(folder/'RESULT.json') if (folder/'RESULT.json').exists() else None
        if result:
            need(result['task']==task,'Exact current task/result');checks=coordinates(folder,result,'R5',required_pass=bool(terminal))
            saved_endpoints+=1;nonpassing_saved_endpoints+=int(not checks['passed'])
            if terminal:
                need(terminal['result_path']==rel(folder/'RESULT.json') and terminal['result_sha256']==sha(folder/'RESULT.json') and terminal['PG']==checks['PG'] and not (folder/'FAILURE.json').exists(),'Exact terminal/result/gate')
                passed+=1;max_pg=max(max_pg,checks['PG']);results[tid]=result
        if (folder/'ATTEMPT.json').exists():
            attempt=load(folder/'ATTEMPT.json');need(attempt['task']==task and attempt['no_retry'] is True,'Partial/full original attempt');initial=receipt(folder,'initial.npz',attempt['bounds']);p=len(initial['x0'])
            need(i<len(initializers),'Every allocated state has initializer proof');initrow=initializers[i]
            need(initrow['origin']=='ORIGINAL_FROZEN_CONSTRUCTOR' and initrow['no_warm_start'] is True and all(initrow[k]==identity(initial[k]) for k in ['x0','lo','hi']),'Original initializer/packing/bounds ledger')
            partial=stopped and not result and not terminal
            calls=lines(folder/'CALLS.jsonl',allow_torn=partial,issues=issues);accepted=lines(folder/'ACCEPTED.jsonl',allow_torn=partial,issues=issues)
            diagnostics=lines(folder/'DIAGNOSTIC_CALLS.jsonl',allow_torn=partial,issues=issues)
            totals.update(fg_journal(calls,accepted,p,initial['lo'],initial['hi'],'R5',bool(result),result));totals.update(diagnostic_journal(diagnostics,p,bool(result)))
        else:
            actual={x.name for x in folder.glob('*')}
            need(not terminal and actual<={'initial.npz'} and not lines(folder/'CALLS.jsonl',allow_torn=stopped,issues=issues) and not lines(folder/'DIAGNOSTIC_CALLS.jsonl',allow_torn=stopped,issues=issues),'Only a genuine pre-ATTEMPT partial prefix is admissible')
            if 'initial.npz' in actual:
                need(i<len(initializers),'Pre-ATTEMPT initial bundle needs original identity ledger')
                with np.load(folder/'initial.npz',allow_pickle=False) as z:
                    need(set(z.files)=={'x0','lo','hi'},'Exact partial initial member set')
                    need(all(identity(z[k])==initializers[i][k] for k in ['x0','lo','hi']),'Preserved partial initializer identities; no reconstruction')
        if tid in failed and (folder/'FAILURE.json').exists():
            f=load(folder/'FAILURE.json');need(f['task']==task and f['type']==failed[tid]['type'] and f['message']==failed[tid]['message'] and f['retry_authorized'] is False,'Actual failure receipt/journal join')
        if terminal:need(result is not None,'Completed state cannot be missing')
    for key,cap in CAPS.items():need(totals[key]<=cap,'Original global cap '+key)
    for tid,target in old.items():
        folder=local(target['result_path']).parent;result=load(folder/'RESULT.json');need(result['task']==target['task'],'Historical exact task');coordinates(folder,result,target['origin']);results[tid]=result
    for target in b0:
        folder=local(target['result_path']).parent;result=load(folder/'RESULT.json');need(result['unit_id']==target['unit_id'],'Original B0 unit');coordinates(folder,result,'R3',b0=True)
    if complete_path.exists():
        out=load(complete_path);need(out['M4'] is True and out['E'] is False and out['Final_C_D_access'] is False,'M4-only worker completion')
        need(passed==2479 and len(attempts)==2479 and not failed and active is None and native['returncode']==0 and not native['killed_at_deadline'] and native['completed_before_deadline'] and not native.get('clock_failure'),'Complete actual within-budget native outcome')
        check_m4(old,results,fullplan,index);verdict='M4_COMPLETE_INDEPENDENTLY_ACCEPTED';decision['basis']='COMPLETE_M4_APPROVAL_NUMERICAL_CERTIFICATES_AND_SEEDS_VERIFIED'
    else:
        text=(E/'SCIENTIFIC_EXECUTION.log').read_bytes().decode('utf8',errors='replace') if local(EP+'/SCIENTIFIC_EXECUTION.log').exists() else ''
        decision=validate_stop(load(stop_path),native,failed,text,issues);verdict=decision['verified_scientific_status']
    need(not (P/'results/E_BATCH_CLAIM.json').exists() and not (P/'work/E').exists(),'No E entitlement/export artifacts')
    preps=load(local('paper16_development_r3/results/A_PREPROCESSING_STATES.json'));need(len(preps)==215 and all(x['role']=='A' and x['path'] in index and index[x['path']]['sha256']==x['sha256'] for x in preps),'Complete original A-only state identities; no raw arrays decoded')
    task_count_unknown=any(x['path']=='paper16_development_r5/results/FIT_JOURNAL.jsonl' for x in issues)
    return {'mission':MISSION,'saved_only_verification':'INCOMPLETE' if issues else 'PASS','scientific_verdict':verdict,'reported_scientific_verdict':load(stop_path)['scientific_status'] if stopped else verdict,'terminal_validation':decision,'journal_issues':issues,'counts_scope':'Observed LF-terminated atomic prefixes only' if issues else 'Complete archived journals','new_attempted':None if task_count_unknown else len(attempts),'observed_atomic_attempt_records':len(attempts),'new_journal_completed':len(completed),'new_complete_saved_endpoints':saved_endpoints,'new_partial_saved_attempts':None if task_count_unknown else len(attempts)-saved_endpoints,'new_numerical_passes':passed,'new_nonpassing_saved_endpoints':nonpassing_saved_endpoints,'new_failed_journal_entries':len(failed),'partial_active_task':active,'unattempted':None if task_count_unknown else 2479-len(attempts),'historical_optimizer_certificates_verified':len(old),'B0_certificates_verified':len(b0),'max_completed_PG':max_pg if passed else None,'resources':dict(totals),'resource_totals_complete':not issues,'partial_diagnostic_completed_counts':'Not inferred; reservations are not completion logs','archive_manifest_sha256':sha(manifest),'reproducer_sha256':sha(__file__),'scientific_model_imports':0,'new_fits_derivatives_scores':0,'raw_neural_arrays_decoded':0,'E_access':False,'Final_C_D_access':False,'boundary_basis':'Exact frozen producer/prefit/A-only identities and no E entitlement/export artifacts; no malicious-administrator claim','publication_annex':'Separate future final-review-bound annex; no publication authorization implied'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',default=str(P/'LOCAL_ARCHIVE_MANIFEST.json'));args=parser.parse_args()
    def denied(*a,**k):raise RuntimeError('Saved-only reproduction forbids network')
    socket.socket.connect=denied;socket.socket.connect_ex=denied;socket.create_connection=denied
    print(json.dumps(run(Path(args.manifest)),indent=2,allow_nan=False))
