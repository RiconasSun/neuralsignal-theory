"""Saved-evidence checks only. Never loads neural sources or calls a model."""
import argparse,hashlib,json,math,socket
from pathlib import Path
from unittest.mock import patch
import numpy as np

R=Path(__file__).resolve().parents[1];P=R/'paper16_development_r2'

def load(path):return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(path):return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines()] if path.exists() else []
def require(ok,message):
    if not ok:raise RuntimeError(message)

def certificate(folder):
    """Independently recompute saved coordinate errors/PG, without derivatives."""
    diag=load(folder/'DIAGNOSTICS.json');state=diag['coordinate_state']
    require(sha(R/state['path'])==state['sha256'],'Coordinate state hash')
    p=diag['free_coordinates']
    require((diag['FD_objective_calls'],diag['AD_calls'],diag['analytic_checkpoint_calls'])==(24*p,3,3),'Diagnostic budgets')
    checks=[]
    with np.load(R/state['path'],allow_pickle=False) as a:
        for name,row in zip(['initial','halfway','endpoint'],diag['checkpoints']):
            g=a[name+'_analytic'];ad=a[name+'_AD'];err=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
            require(g.shape==ad.shape==(p,) and np.isfinite(g).all() and np.isfinite(ad).all(),'Saved gradient shapes/finiteness')
            require(np.array_equal(err,a[name+'_AD_error']),'Saved AD coordinate errors')
            require(float(err.max())==row['AD_scaled_coordinate_error_max'],'AD error summary')
            errors={}
            for h in [0.001,0.0001,0.00001,0.000001]:
                fd=a[name+'_FD_'+str(h)]
                delta=np.abs(fd-g)/np.maximum(1,np.maximum(np.abs(fd),np.abs(g)))
                require(np.isfinite(fd).all() and np.array_equal(delta,a[name+'_FD_error_'+str(h)]),'Saved FD coordinates')
                require(float(delta.max())==row['FD_scaled_coordinate_errors'][str(h)],'FD error summary')
                errors[str(h)]=float(delta.max())
            passed=bool(np.isclose(row['objective'],row['AD_objective'],atol=1e-10,rtol=1e-12) and err.max()<=1e-8 and errors['1e-05']<=2e-5)
            require(row['checkpoint']==name and row['pass']==passed,'Checkpoint gate')
            checks.append(passed)
        endpoint=a['endpoint_x'].copy();g=a['endpoint_analytic'].copy()
    require(diag['all_checkpoints_pass']==all(checks),'Certificate conjunction')
    return endpoint,g,all(checks)

def fit(folder):
    result=load(folder/'RESULT.json');x,g,passed=certificate(folder)
    require(sha(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Result diagnostic binding')
    require(sha(R/result['endpoint_state']['path'])==result['endpoint_state']['sha256'],'Endpoint binding')
    with np.load(folder/'initial.npz',allow_pickle=False) as a:lo=a['lo'];hi=a['hi'];x0=a['x0']
    with np.load(folder/'endpoint.npz',allow_pickle=False) as a:
        require(np.array_equal(x,a['x']) and np.array_equal(g,a['gradient']),'Endpoint coordinate identity')
    require(np.isfinite(x).all() and np.all(x>=lo-1e-12) and np.all(x<=hi+1e-12),'Endpoint bounds')
    projected=g.copy();projected[(x<=lo+1e-12)&(g>0)]=0;projected[(x>=hi-1e-12)&(g<0)]=0
    pg=float(np.abs(projected).max())
    require(pg==result['projected_gradient_inf'],'Saved outward PG')
    calls=rows(folder/'CALLS.jsonl');reserved=[r for r in calls if r['event']=='RESERVED_BEFORE_EVALUATION'];completed=[r for r in calls if r['event']=='COMPLETED']
    accepted=rows(folder/'ACCEPTED.jsonl')
    require(len(reserved)==len(completed)==result['external_value_gradient_pairs']<=6000,'External objective call budget')
    require(len(accepted)==result['external_accepted_iterations']<=1500,'External iteration budget')
    require([r['call'] for r in reserved]==list(range(1,len(reserved)+1))==[r['call'] for r in completed],'Call sequence')
    with np.load(folder/'coordinate_certificates.npz',allow_pickle=False) as a:
        mid=np.asarray(accepted[math.ceil(len(accepted)/2)-1]['x']) if accepted else x
        require(np.array_equal(x0,a['initial_x']) and np.array_equal(mid,a['halfway_x']),'Frozen initial/first halfway accepted vectors')
    require(result['numerical_pass']==bool(pg<=1e-5 and passed),'Combined unchanged gate')
    return result

def recompute_statistics(records,cohort):
    names=['B4-B1','B4-B2','B4-B3','D-B4','C-B4','D-S']
    ids=[r['mouse_id'] for r in records]
    require(ids==sorted(cohort,key=int) and len(ids)==27 and len(set(ids))==27,'Exact frozen E mouse set/order')
    require(all(r['protocol']==cohort[r['mouse_id']] for r in records),'Frozen BO/FC membership')
    values=np.array([[r['effects'][k] for k in names] for r in records])
    require(values.shape==(27,6) and np.isfinite(values).all(),'Saved mouse effect shape/finiteness')
    draws=np.random.Generator(np.random.PCG64(16042)).integers(0,27,size=(10000,27))
    result={'effect_names':names,'equal_mouse_mean':[math.fsum(values[:,k])/27 for k in range(6)],
        'exploratory_whole_mouse_CI95':np.quantile(values[draws].mean(axis=1),[.025,.975],axis=0,method='linear').tolist(),
        'bootstrap_seed':16042,'bootstrap_replicates':10000,'scope':'EXPLORATORY_DEVELOPMENT_ONLY',
        'Final_gate':'NOT_EXECUTED_FINAL_BOUNDARY','BO_FC':{}}
    for group,seed,n in [('BO',16043,5),('FC',16044,22)]:
        rows=[r for r in records if r['protocol']==group]
        require(len(rows)==n,'Frozen BO/FC denominator')
        v=np.array([[r['effects'][k] for k in names] for r in rows])
        indices=np.random.Generator(np.random.PCG64(seed)).integers(0,n,size=(10000,n))
        result['BO_FC'][group]={'mouse_ids':[r['mouse_id'] for r in rows],'n':n,
            'equal_mouse_mean':[math.fsum(v[:,k])/n for k in range(6)],'effect_names':names,
            'CI95':np.quantile(v[indices].mean(axis=1),[.025,.975],axis=0,method='linear').tolist(),
            'bootstrap_replicates':10000,'seed':seed,'causal_protocol_effect':False,
            'absolute_model_means':{m:math.fsum(r['absolute'][m] for r in rows)/n for m in ['B0','B1','B2','B3','B4','C','D','S']},
            'actual_unit_bins_sum_descriptive_not_inference_n':sum(r['actual_valid_unit_bins'] for r in rows)}
    return result

def verify_statistics(summary,cohort):
    expected=recompute_statistics(summary['mice'],cohort)
    for key,value in expected.items():require(summary[key]==value,'Saved descriptive statistics: '+key)

def facts():
    journal=rows(P/'results/FIT_JOURNAL.jsonl');attempts=[r for r in journal if r['event']=='ATTEMPTED']
    require(len({r['task']['id'] for r in attempts})==len(attempts),'No optimizer retry')
    result={'optimizer_attempts':len(attempts),'completed_optimizer_tasks':0,'numerically_failed_optimizer_tasks':0,
        'incomplete_optimizer_tasks':0,'analytic_B0_certificates':0,'B_access_sessions':0,'E_access_sessions':0,
        'Final_C_access':False,'Final_D_access':False,'Final_model_fits':0,'Final_assessments':0}
    for row in attempts:
        task=row['task'];folder=P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
        if (folder/'RESULT.json').exists():
            state=fit(folder);require(state['task']==task,'Attempt task identity')
            result['completed_optimizer_tasks']+=1
            result['numerically_failed_optimizer_tasks']+=not state['numerical_pass']
        else:result['incomplete_optimizer_tasks']+=1
    for path in (P/'work/B0').glob('*/*/RESULT.json'):
        state=load(path);x,g,good=certificate(path.parent)
        pg=float(np.abs(np.where(((x<=-10+1e-12)&(g>0))|((x>=10-1e-12)&(g<0)),0,g)).max())
        require(pg==state['projected_gradient_inf'] and state['numeric_pass']==bool(pg<=1e-5 and good),'B0 saved gate')
        result['analytic_B0_certificates']+=1
    access=rows(P/'results/ACCESS.jsonl')
    require(all(r['role'] in ['A','B','E'] for r in access),'No Final access')
    for role in ['B','E']:result[role+'_access_sessions']=len({r['session_id'] for r in access if r['role']==role})
    if (P/'results/TASK_PLAN.json').exists():
        plan=load(P/'results/TASK_PLAN.json');ids={r['id'] for r in plan['tasks']}
        require(all(r['task']['id'] in ids for r in attempts),'Frozen exact task membership')
        require(len(attempts)<=plan['optimizer_attempt_count']<=7506,'Development allocation')
        result['planned_optimizer_tasks']=len(ids);result['unattempted_optimizer_tasks']=sorted(ids-{r['task']['id'] for r in attempts})
    if (P/'results/B_SELECTION.json').exists():
        selection=load(P/'results/B_SELECTION.json')
        from paper16_m1.code.analysis_oracles import select_lambda
        for row in selection['records']:
            state=row['score_state'];require(sha(R/state['path'])==state['sha256'],'B score hash')
            with np.load(R/state['path'],allow_pickle=False) as a:
                score=float(a['logscore_bins'].sum()/row['actual_valid_unit_bins'])
                require(score==row['logscore'],'Saved B1 unpenalized scoring summary')
        require(select_lambda(selection['records'])==selection['selected_lambda'],'Frozen global lambda')
        result['selected_lambda']=selection['selected_lambda']
    if (P/'results/E_DEVELOPMENT_RESULTS.json').exists():
        summary=load(P/'results/E_DEVELOPMENT_RESULTS.json');names=summary['effect_names']
        for row in summary['mice']:
            with np.load(P/'work/E'/row['mouse_id']/'main_scores.npz',allow_pickle=False) as a:
                for model,value in row['absolute'].items():require(float(a[model].sum()/row['actual_valid_unit_bins'])==value,'Saved E absolute score')
                for pair,value in row['effects'].items():
                    left,right=pair.split('-');require(float((a[left]-a[right]).sum()/row['actual_valid_unit_bins'])==value,'Saved E paired effect')
        actual=[math.fsum(r['effects'][k] for r in summary['mice'])/len(summary['mice']) for k in names]
        require(actual==summary['equal_mouse_mean'],'Equal mouse means')
        cohort={str(r['source']['mouse_id']):'BO' if r['source']['protocol']=='brain_observatory_1.1' else 'FC'
            for r in load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']}
        verify_statistics(summary,cohort)
        from .controls import aggregate_references
        require(aggregate_references(summary['mice'],P/'work/controls')==load(P/'results/REFERENCE_CONTROL_RESULTS.json'),'Saved reference summaries')
        result['E_results_recomputed_from_saved_scores_only']=True
        result['pooled_and_BO_FC_descriptive_intervals_verified']=True
    result['scientific_stop']=load(P/'results/SCIENTIFIC_STOP.json') if (P/'results/SCIENTIFIC_STOP.json').exists() else None
    return result

def verify():
    archive=load(P/'ARCHIVE_MANIFEST.json')
    for row in archive['files']:
        require(sha(R/row['path'])==row['sha256'] and (R/row['path']).stat().st_size==row['bytes'],'Archive identity: '+row['path'])
    for name,digest in load(P/'SOURCE_PINS.json')['files'].items():require(sha(R/name)==digest,'Inherited source identity')
    result=facts()
    require(result==load(P/'EXECUTION_FACTS.json'),'Saved execution facts changed')
    print(json.dumps({'saved_only_reproduction':'PASS','files_verified':len(archive['files']),
        'new_fits':0,'new_derivative_experiments':0,'new_source_requests':0,'Final_access':False,'execution_facts':result},indent=2))

if __name__=='__main__':
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('Saved-only reproduction denies network')):verify()
