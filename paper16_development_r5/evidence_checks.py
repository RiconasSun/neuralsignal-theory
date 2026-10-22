"""Saved identity and certificate arithmetic only; never evaluate a model."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from .core import *

def need(condition,message):
    if not condition:raise AccessStop(message)

def members(folder,name,receipt):
    path=Path(folder)/name
    need((R/receipt['path']).resolve()==path.resolve(),'Saved member path substitution')
    need(sha(path)==receipt['sha256'],'Saved member file hash')
    with np.load(path,allow_pickle=False) as a:values={k:a[k].copy() for k in a.files}
    need({k:array_id(v) for k,v in values.items()}==receipt['arrays'],'Saved member identities')
    return values

def prepared(row,values,expected):
    need(row==expected,'Frozen A preparation index/source/unit/scaler identity')
    need(row['role']=='A' and {k:array_id(v) for k,v in values.items()}==row['arrays'],'A role/unit/scaler member identity')
    need(np.all((values['ordinals']>=0)&(values['ordinals']<90)),'A observation support')

def frozen_files(rows,stage=None,actual_paths=None):
    need(len({r['path'] for r in rows})==len(rows),'Unique original frozen file inventory')
    if actual_paths is not None:need(set(actual_paths)=={r['path'] for r in rows},'Exact original inventory; no missing or extra files')
    for row in rows:
        if stage is not None:guard(stage)
        need(sha(R/row['path'])==row['sha256'],'Original historical file bytes changed: '+row['path'])

def registered_folder(folder,rows):
    folder=Path(folder)
    expected={R/row['path'] for row in rows if (R/row['path']).parent==folder}
    actual={path for path in folder.iterdir() if path.is_file()}
    need(bool(expected) and actual==expected,'Exact registered historical state folder; no missing or extra files')
    return sorted(expected)

def terminal(task,folder,rows):
    matches=[r for r in rows if r.get('event')=='COMPLETED' and r.get('task',{}).get('id')==task['id']]
    need(len(matches)==1,'Exactly one original terminal completion')
    row=matches[0];path=Path(folder)/'RESULT.json'
    need(row['task']==task and row['result_path']==path.relative_to(R).as_posix() and row['result_sha256']==sha(path),'Completed journal/result original hash join')

def reuse(matrix,targets):
    need(len(matrix)==len(targets) and len({r['task']['id'] for r in matrix})==len(matrix),'Full unique reuse matrix')
    for row,target in zip(matrix,targets):
        need(row['task']==target['task'] and row['origin']==target['origin'] and row['historical_ftol']==target['historical_ftol'],'Original ordered reuse target and policy')
        need(row['status']=='PASS' and row['origin'] in ['R3','R4'],'Failed/partial/diagnostic state cannot be admitted')
        original=R/('paper16_development_r3' if row['origin']=='R3' else 'paper16_development_r4')/'work/fits'/hashlib.sha256(row['task']['id'].encode()).hexdigest()/'RESULT.json'
        need(R/row['result_path']==original and row['result_path']==target['result_path'] and row['result_sha256']==target['result_sha256'],'Canonical completed state; no diagnostic or partial substitution')
        need(row['PG']<=1e-5 and row['AD_error_max']<=1e-8 and row['fixed_FD_error_max']<=2e-5,'All original reuse numerical gates')

def fit(folder,task):
    folder=Path(folder);result=load(folder/'RESULT.json');attempt=load(folder/'ATTEMPT.json');diag=load(folder/'DIAGNOSTICS.json')
    need(not (folder/'FAILURE.json').exists() and result['task']==attempt['task']==task,'Actual complete successful task identity')
    need(sha(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Saved diagnostics binding')
    initial=members(folder,'initial.npz',attempt['bounds']);coordinate=members(folder,'coordinate_certificates.npz',diag['coordinate_state']);endpoint=members(folder,'endpoint.npz',result['endpoint_state'])
    p=len(initial['x0']);need(attempt['parameters']==diag['free_coordinates']==p and (diag['FD_objective_calls'],diag['AD_calls'],diag['analytic_checkpoint_calls'])==(24*p,3,3),'Full original checkpoint dimensions and budgets')
    need(len(diag['checkpoints'])==3 and diag['all_checkpoints_pass'] is True and diag['FD_step_not_selected_post_result'] is True,'Complete original fixed derivative policy')
    for name,row in zip(['initial','halfway','endpoint'],diag['checkpoints']):
        x,g,ad=[coordinate[name+suffix] for suffix in ['_x','_analytic','_AD']]
        need(all(a.shape==(p,) and np.isfinite(a).all() for a in [x,g,ad]),'Finite complete checkpoint coordinates')
        need(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Original checkpoint bounds')
        error=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
        need(np.array_equal(error,coordinate[name+'_AD_error']) and float(error.max())==row['AD_scaled_coordinate_error_max']<=1e-8,'Original coordinate AD gate')
        for h in [.001,.0001,.00001,.000001]:
            fd=coordinate[name+'_FD_'+str(h)];delta=np.abs(fd-g)/np.maximum(1,np.maximum(np.abs(fd),np.abs(g)))
            need(fd.shape==(p,) and np.isfinite(fd).all() and np.array_equal(delta,coordinate[name+'_FD_error_'+str(h)]) and float(delta.max())==row['FD_scaled_coordinate_errors'][str(h)],'Every fixed FD coordinate arithmetic')
        need(row['checkpoint']==name and row['pass'] is True and row['frozen_FD_scaled_error']==row['FD_scaled_coordinate_errors']['1e-05']<=2e-5,'Fixed h1e-5 must pass; favorable step cannot replace it')
        need(np.isfinite(row['objective']) and np.isfinite(row['AD_objective']) and np.isclose(row['objective'],row['AD_objective'],atol=1e-10,rtol=1e-12),'Identical saved objective/AD definition')
    need(np.array_equal(coordinate['initial_x'],initial['x0']) and np.array_equal(endpoint['x'],coordinate['endpoint_x']) and np.array_equal(endpoint['gradient'],coordinate['endpoint_analytic']),'Original checkpoint/endpoint vectors')
    need(np.array_equal(result['x'],endpoint['x']) and np.allclose(result['jac'],endpoint['gradient'],atol=1e-12,rtol=1e-12),'Complete result endpoint vectors')
    pg=float(np.abs(spec.projected_gradient(endpoint['x'],endpoint['gradient'],initial['lo'],initial['hi'])).max())
    need(result['numerical_pass'] is True and result['projected_gradient_inf']==pg<=1e-5,'Original full projected gradient')
    need(result['objective']==result['fun'] and np.isclose(result['objective'],diag['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12),'Saved result objective')
    n,nit=result['external_value_gradient_pairs'],result['external_accepted_iterations']
    need(type(n) is int and type(nit) is int and 1<=n<=6000 and 0<=nit<=1500 and n==result['nfev'] and nit==result['nit'],'Original per-fit caps and actual counters')
    calls=[json.loads(line) for line in (folder/'CALLS.jsonl').read_text(encoding='utf8').splitlines()]
    accepted=[json.loads(line) for line in (folder/'ACCEPTED.jsonl').read_text(encoding='utf8').splitlines()] if (folder/'ACCEPTED.jsonl').exists() else []
    need(len(calls)==2*n and len(accepted)==nit==result['accepted_vector_count'],'Full actual optimizer journals')
    historical_scalar=folder.resolve().is_relative_to((R/'paper16_development_r3/work/fits').resolve())
    for i in range(n):
        before,after=calls[2*i:2*i+2]
        need(before['event']=='RESERVED_BEFORE_EVALUATION' and after['event']=='COMPLETED' and before['call']==after['call']==i+1 and 0<=before['iterations']<=nit,'Full alternating FG reservation/completion order')
        need(np.isfinite(after['objective']) and np.isfinite(after['gradient_inf']),'Finite saved FG scalars')
        if not historical_scalar:
            x,g=np.asarray(before['x']),np.asarray(after['gradient'])
            need(x.shape==g.shape==(p,) and np.isfinite(x).all() and np.isfinite(g).all() and float(np.abs(g).max())==after['gradient_inf'],'Original full FG vectors')
    for i,row in enumerate(accepted):
        need(row['iteration']==i+1 and np.asarray(row['x']).shape==(p,) and np.isfinite(row['x']).all(),'Full accepted vectors')
    mid=accepted[math.ceil(nit/2)-1]['x'] if nit else result['x']
    need(np.array_equal(coordinate['halfway_x'],mid) and result['halfway_accepted_iteration']==math.ceil(nit/2),'Original accepted halfway checkpoint')
    return result
