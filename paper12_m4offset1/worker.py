"""Native A-only diagnostics and progressive fixed-offset fitting."""
import hashlib
import json
from pathlib import Path
import sys


def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:]
    sys.path[:0]=[deps,str(Path(__file__).parent)]
    from native_analysis_check import check
    output=Path(output)
    def save(name,x):
        with (output/name).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,allow_nan=False)
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if proof['pass'] is not True:raise PermissionError('NATIVE_ISOLATION_FAILED')
    import unittest
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test_*.py')
    test=unittest.TestResult();suite.run(test)
    save('oracle_tests.json',dict(count=test.testsRun,passed=test.wasSuccessful(),failures=[str(x) for x in test.failures],errors=[str(x) for x in test.errors]))
    if test.testsRun!=12 or not test.wasSuccessful():raise RuntimeError('TWELVE_INDEPENDENT_ORACLES_REQUIRED')
    import numpy as np
    from numerical import run_fit,ORIGINAL,REPAIRED,gradient_check
    from baseline_fit import objective,projected_gradient
    from offset_math import features,array_sha
    from scipy.optimize import minimize
    policy=json.loads(Path(__file__).with_name('worker_policy.json').read_text());phase=policy['phase']
    manifest=json.loads((Path(data)/'manifest.json').read_text())
    if manifest['compartments']!=['A'] or manifest['group']!='development' or len(manifest['sessions'])!=13:
        raise PermissionError('THIRTEEN_FROZEN_DEVELOPMENT_A_ONLY')
    sessions=manifest['sessions'][:1 if phase in ('diagnosis','smoke') else (4 if phase=='small' else 13)]
    rows=[];states={};meta={};failure=None
    previous=Path(__file__).with_name('reuse_states.npz')
    prior=json.loads(Path(__file__).with_name('reuse_records.json').read_text()) if previous.exists() else None
    if prior:
        if hashlib.sha256(previous.read_bytes()).hexdigest()!=policy['reuse_states_sha256']:raise RuntimeError('REUSE_STATE_HASH')
        with np.load(previous,allow_pickle=False) as z:states={k:z[k] for k in z.files}
        rows=prior['rows'];meta=prior['meta']
    for session in sessions:
        path=Path(data)/session['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('FROZEN_TRAINING_HASH')
        with np.load(path,allow_pickle=False) as arrays:
            if any(k.endswith(('_B','_C','_D')) for k in arrays.files):raise PermissionError('NONTRAINING_COMPARTMENT')
            for region in (('CA1',) if phase=='diagnosis' else ('CA1','DG')):
                case=session['session_id']+'_'+region
                if case in meta:continue
                y=arrays[region+'_A'];c=arrays['conditions_A'];o=arrays['orders_A'];x=features(y,c,o)
                if phase=='diagnosis':
                    original=json.loads(Path(__file__).with_name('original_offset_diagnostics.json').read_text())
                    for seed,old in zip((11,23,37),original['seeds']):
                        _,row=run_fit(y,x,.1,seed,ORIGINAL)
                        match=all(row[k]==old[k] for k in ('seed','ridge','projected_gradient','iterations','objective_calls','optimizer_message','optimizer_success','converged'))
                        row.update(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,
                            original_diagnostic_match=match,trace_origin='prospective_A_only_replay',training_array_sha256=array_sha(y))
                        rows.append(row);save(case+'_'+str(seed)+'.json',row)
                    break
                import task_offset
                captured=[];details=[]
                def monitored(f,initial,**kwargs):
                    if kwargs['options']!=REPAIRED:raise RuntimeError('REGISTERED_SINGLE_OFFSET_BUDGET_REQUIRED')
                    yy,xx,ridge,normalization=kwargs['args'];n=initial.size
                    coords=sorted(set(range(0,n,29))|set(np.random.default_rng(20261012).choice(n,min(16,n),replace=False).tolist()))
                    initial_check=gradient_check(initial,yy,xx,ridge,coords);calls=[];accepted=[]
                    def loss(theta,*args):
                        value,g=f(theta,*args);calls.append(dict(loss=value,projected_gradient=projected_gradient(theta,g),gradient_inf=float(np.max(np.abs(g))),bound_hits=int(np.sum(np.abs(theta)>=8))))
                        return value,g
                    def callback(theta):
                        value,g=f(theta,*kwargs['args']);accepted.append(dict(loss=value,projected_gradient=projected_gradient(theta,g)))
                    result=minimize(loss,initial,callback=callback,**kwargs)
                    terminal_check=gradient_check(result.x,yy,xx,ridge,coords)
                    captured.append(result.x.reshape(y.shape[-1],29).copy())
                    details.append(dict(initial_gradient_check=initial_check,terminal_gradient_check=terminal_check,
                        objective_history=calls,accepted_iteration_history=accepted,optimizer_policy=REPAIRED,
                        bound_hits=int(np.sum(np.abs(result.x)>=8)),parameter_count=n,training_unit_bins=int(yy.size)))
                    return result
                task_offset.minimize=monitored
                ot,ov,_,_,diagnostics=task_offset.fit_offset(y,y,c,c,o,o)
                if len(captured)!=3 or len(diagnostics)!=3:raise RuntimeError('ALL_THREE_OFFSET_SEEDS_REQUIRED')
                for seed,record,detail,weight in zip((11,23,37),diagnostics,details,captured):
                    record.update(detail);record.update(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,
                        training_array_sha256=array_sha(y),training_only=True)
                    rows.append(record);save(case+'_'+str(seed)+'.json',record);states[case+'_'+str(seed)]=weight
                meta[case]=dict(training_array_sha256=array_sha(y),parent_AB_sha256=session['parent_AB_sha256'],mouse_id=session['mouse_id'],unit_count=y.shape[-1])
                valid=all(z['converged'] and z['initial_gradient_check']['passed'] and z['terminal_gradient_check']['passed'] for z in rows if z['session_id']==session['session_id'] and z['region']==region)
                if not valid or not np.all(np.isfinite(ot)) or not np.array_equal(ot,ov):failure='MANDATORY_OFFSET_CONVERGENCE_OR_ORACLE_FAILURE';break
        if failure:break
    if phase=='diagnosis':
        valid=len(rows)==3 and all(z['original_diagnostic_match'] and z['initial_gradient_check']['passed'] and z['terminal_gradient_check']['passed'] for z in rows)
        premature=valid and all('RELATIVE REDUCTION' in z['optimizer_message'] and z['iterations']<500 and z['objective_calls']<20000 and z['projected_gradient']>.001 for z in rows)
        gate=dict(gate='PASS' if premature else 'FAIL',phase=phase,scientific_verdict='OFFSET_AMENDMENT_ELIGIBLE' if premature else 'NUMERICAL_INCONCLUSIVE',completed_fit_count=len(rows),original_replay_exact=valid,premature_relative_stopping=premature,final_access=False)
    else:
        expected={'smoke':6,'small':24,'full':78}[phase]
        valid=not failure and len(rows)==expected and len({(z['session_id'],z['region'],z['seed']) for z in rows})==expected and all(z['converged'] for z in rows)
        gate=dict(gate='PASS' if valid else 'FAIL',phase=phase,expected_fit_count=expected,completed_fit_count=len(rows),converged_fit_count=sum(z['converged'] for z in rows),failure=failure,final_access=False)
        if valid:
            np.savez(output/'offset_states.npz',**states)
            save('offset_records.json',dict(rows=rows,meta=meta))
            gate['state_sha256']=hashlib.sha256((output/'offset_states.npz').read_bytes()).hexdigest()
    save('summary.json',dict(rows=rows,validation_access=False,final_access=False));save('gate_result.json',gate)
    if gate['gate']!='PASS':sys.exit(2)


if __name__=='__main__':main()
