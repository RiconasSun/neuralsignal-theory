"""Saved-only verification: no objective/gradient/optimizer/score imports or calls."""
import csv,hashlib,json,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];P=R/'paper16_termination_feasibility1'
def load(p):return json.loads(Path(p).read_bytes())
def rows(p):return [json.loads(s) for s in Path(p).read_text(encoding='utf8').splitlines()] if Path(p).exists() else []
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def projected(x,g,lo,hi):return np.where(((x<=lo+1e-12)&(g>0))|((x>=hi-1e-12)&(g<0)),0,g)
def check_incomplete(folder,summary):
    """Validate an observed consumed STOP; never invent its missing endpoint."""
    require(summary['REAL_A_DIAGNOSTIC_ATTEMPTS']==1,'Consumed attempt cannot be hidden')
    require(summary['REAL_A_NUMERICAL_PASS'] is None and summary['DIAGNOSTIC_VERDICT'] in ['INCONCLUSIVE','INCONCLUSIVE / STOP'],'No numerical result from incomplete evidence')
    require(not (folder/'WORKER_COMPLETE.json').exists(),'Incomplete cannot claim worker complete')
    require(any((folder/n).exists() for n in ['STOP.json','SUPERVISION.json','EXECUTION_FAILURE.json']),'Observed interruption/STOP evidence required')
    calls=rows(folder/'fit/CALLS.jsonl');reserved=[r for r in calls if r['event']=='RESERVED_BEFORE_EVALUATION'];done=[r for r in calls if r['event']=='COMPLETED']
    require(len(reserved)<=6000 and len(done)<=len(reserved),'Incomplete FG cap/accounting')
    require([r['call'] for r in reserved]==list(range(1,len(reserved)+1)),'Incomplete reservations contiguous')
    require([r['call'] for r in done]==list(range(1,len(done)+1)) and len(reserved)-len(done)<=1,'At most one interrupted reserved pair')
    accepted=rows(folder/'fit/ACCEPTED.jsonl');require([r['iteration'] for r in accepted]==list(range(1,len(accepted)+1)) and len(accepted)<=1500,'Incomplete accepted iteration cap')
    diagnostics=rows(folder/'fit/DIAGNOSTIC_CALLS.jsonl')
    counts={k:sum(r['kind']==k for r in diagnostics) for k in ['FD_RESERVED','AD_RESERVED','ANALYTIC_RESERVED']}
    require(counts['FD_RESERVED']<=888 and counts['AD_RESERVED']<=3 and counts['ANALYTIC_RESERVED']<=3,'Incomplete diagnostic cap')
    access=rows(folder/'ACCESS.jsonl');require(all(r['role']=='A' for r in access) and len(access)<=2,'Incomplete A-only access')
    return {'attempts_preserved':1,'reserved_FG':len(reserved),'completed_FG':len(done),'accepted':len(accepted),'diagnostic_reservations':counts,'missing_endpoint_not_reconstructed':True}
def check_fit(folder):
    result=load(folder/'RESULT.json');diag=load(folder/'DIAGNOSTICS.json')
    require(sha(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Diagnostic hash')
    require(sha(R/diag['coordinate_state']['path'])==diag['coordinate_state']['sha256'],'Coordinate hash')
    require(sha(R/result['endpoint_state']['path'])==result['endpoint_state']['sha256'],'Endpoint hash')
    with np.load(folder/'initial.npz',allow_pickle=False) as z:lo=z['lo'];hi=z['hi'];x0=z['x0']
    with np.load(folder/'endpoint.npz',allow_pickle=False) as z:x=z['x'];g=z['gradient']
    p=len(x);checks=[];coordinate_rows=[]
    with np.load(R/diag['coordinate_state']['path'],allow_pickle=False) as z:
        require(np.array_equal(x,z['endpoint_x']) and np.array_equal(g,z['endpoint_analytic']) and np.array_equal(x0,z['initial_x']),'Saved vector identity')
        for name,c in zip(['initial','halfway','endpoint'],diag['checkpoints']):
            a=z[name+'_analytic'];ad=z[name+'_AD'];xx=z[name+'_x']
            require(np.isfinite(xx).all() and np.isfinite(a).all() and np.isfinite(ad).all() and np.all(xx>=lo-1e-12) and np.all(xx<=hi+1e-12),'Finite/bounded saved checkpoint')
            err=np.abs(a-ad)/np.maximum(1,np.maximum(np.abs(a),np.abs(ad)));require(np.array_equal(err,z[name+'_AD_error']),'AD arithmetic')
            require(float(err.max())==c['AD_scaled_coordinate_error_max'],'AD max')
            fd_errors={}
            for h in [.001,.0001,1e-5,1e-6]:
                fd=z[name+'_FD_'+str(h)];delta=np.abs(a-fd)/np.maximum(1,np.maximum(np.abs(a),np.abs(fd)))
                require(np.isfinite(fd).all() and np.array_equal(delta,z[name+'_FD_error_'+str(h)]),'FD arithmetic');fd_errors[str(h)]=float(delta.max())
            require(fd_errors==c['FD_scaled_coordinate_errors'],'All fixed FD scale errors')
            passed=bool(np.isclose(c['objective'],c['AD_objective'],atol=1e-10,rtol=1e-12) and err.max()<=1e-8 and fd_errors['1e-05']<=2e-5)
            require(c['pass']==passed,'Checkpoint pass formula');checks.append(passed)
            pg=projected(xx,a,lo,hi)
            for i in range(p):
                row={'checkpoint':name,'index':i,'x':float(xx[i]),'lo':float(lo[i]),'hi':float(hi[i]),'analytic':float(a[i]),'AD':float(ad[i]),'PG':float(pg[i]),'AD_error':float(err[i])}
                for h in [.001,.0001,1e-5,1e-6]:row['FD_'+str(h)]=float(z[name+'_FD_'+str(h)][i])
                coordinate_rows.append(row)
        accepted=rows(folder/'ACCEPTED.jsonl');mid=np.array(accepted[math.ceil(len(accepted)/2)-1]['x']) if accepted else x
        require(np.array_equal(mid,z['halfway_x']),'Original accepted halfway checkpoint')
    require(diag['all_checkpoints_pass']==all(checks),'Diagnostic conjunction')
    require((diag['FD_objective_calls'],diag['AD_calls'],diag['analytic_checkpoint_calls'])==(24*p,3,3),'Diagnostic totals')
    pg=float(np.abs(projected(x,g,lo,hi)).max());require(pg==result['projected_gradient_inf'],'PG independently recomputed')
    require(result['numerical_pass']==bool(pg<=1e-5 and all(checks)),'Scientific gate independent of success')
    require(np.array_equal(x,result['x']) and np.allclose(g,result['jac'],atol=1e-12,rtol=1e-12),'Solver/certificate identity')
    calls=rows(folder/'CALLS.jsonl');require(len(calls)%2==0,'Complete FG pairs');require(len(calls)//2==result['nfev']<=6000,'External FG budget')
    require([r['iteration'] for r in accepted]==list(range(1,result['nit']+1)) and len(accepted)<=1500,'External accepted budget')
    assoc={}
    for k in range(0,len(calls),2):
        pre,post=calls[k:k+2];require(pre['event']=='RESERVED_BEFORE_EVALUATION' and post['event']=='COMPLETED' and pre['call']==post['call']==k//2+1,'FG journal sequence')
        require(np.isfinite(pre['x']).all() and np.isfinite(post['gradient']).all() and np.isfinite(post['objective']),'Finite complete FG journal')
        require(float(np.abs(post['gradient']).max())==post['gradient_inf'],'Journal gradient norm')
        assoc[pre['iterations']]=(pre,post)
    for i,row in enumerate(accepted):require(np.array_equal(row['x'],assoc[i][0]['x']),'Accepted vector/FG identity')
    if accepted:require(np.array_equal(accepted[-1]['x'],x),'Endpoint/last accepted identity')
    require(assoc[result['nit']-1 if accepted else 0][1]['objective']==result['objective'],'Saved endpoint objective identity')
    d=rows(folder/'DIAGNOSTIC_CALLS.jsonl');require(sum(r['kind']=='FD_RESERVED' for r in d)==24*p and sum(r['kind']=='AD_RESERVED' for r in d)==3 and sum(r['kind']=='ANALYTIC_RESERVED' for r in d)==3,'Diagnostic reservations')
    return result,coordinate_rows
def verify():
    archive=load(P/'ARCHIVE_MANIFEST.json')
    for row in archive['files']:require(sha(R/row['path'])==row['sha256'] and (R/row['path']).stat().st_size==row['bytes'],'Archive identity: '+row['path'])
    for name,digest in load(P/'SOURCE_PINS.json')['files'].items():require(sha(R/name)==digest,'Historical preservation: '+name)
    protected=load(R/'paper16_development_r3/PROTECTED_STATE_MANIFEST.json')['files']
    for row in protected:require(sha(R/row['path'])==row['sha256'],'Old protected state identity')
    for row in load(P/'NEW_SAVED_STATE_MANIFEST.json')['files']:require(sha(R/row['path'])==row['sha256'],'New saved state identity')
    cert=load(P/'SYNTHETIC_CERTIFICATION.json');require(cert['mandatory_tests_pass'] and cert['real_A_attempts']==0,'Synthetic gate')
    expected=load(P/'SYNTHETIC_OUTCOMES.json')['outcomes']
    for row in expected:
        result,_=check_fit(R/cert['run_folder']/row['fixture'])
        require(result['numerical_pass']==row['numerical_pass'],'Saved fixture outcome')
    summary=load(P/'NUMERICAL_OUTCOME.json')
    if summary['REAL_A_DIAGNOSTIC_ATTEMPTS']:
        claim=load(P/'REAL_CLAIM.json');require(claim['no_retry'] and claim['attempt_limit']==1,'One-shot authorization')
        require(claim['stage']['deadline_monotonic']-claim['stage']['start_monotonic']<=7200,'Wall budget')
        if summary['SAVED_STATE_COMPLETE']:
            result,_=check_fit(P/'work/real/fit')
            require(result['projected_gradient_inf']==summary['ENDPOINT_PG'],'Saved real result identity')
            access=rows(P/'work/real/ACCESS.jsonl');require(len(access)==2 and all(x['role']=='A' for x in access),'A-only accesses')
            sup=load(P/'work/real/SUPERVISION.json')
            fullpass=bool(result['numerical_pass'] and result['success'] and result['message'].startswith('CONVERGENCE:') and sup['completed_before_deadline'] and not sup['killed_at_deadline'] and sup['returncode']==0 and (P/'work/real/WORKER_COMPLETE.json').exists())
            require(fullpass==summary['REAL_A_NUMERICAL_PASS'],'Full execution and numerical conjunction')
        else:check_incomplete(P/'work/real',summary)
    print(json.dumps({'saved_only_reproduction':'PASS','original_files':len(protected),'historical_pins':len(load(P/'SOURCE_PINS.json')['files']),'synthetic_fixtures':len(expected),'real_A_attempts_saved':summary['REAL_A_DIAGNOSTIC_ATTEMPTS'],'real_A_numerical_pass_saved':summary['REAL_A_NUMERICAL_PASS'],'new_fits':0,'new_derivative_evaluations':0,'B_E_Final_neural_access':False}))
if __name__=='__main__':verify()
