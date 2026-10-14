"""A-only native replay, fixed-coordinate independent diagnostics; no B scoring."""
import hashlib
import json
from pathlib import Path
import sys
import time

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)];output=Path(output)
    def save(name,value):
        with (output/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('NATIVE_ISOLATION_FAILED')
    import unittest
    suite=unittest.TestLoader().discover(str(Path(__file__).parent),pattern='test_*.py');result=unittest.TestResult();suite.run(result)
    save('oracle_tests.json',dict(count=result.testsRun,passed=result.wasSuccessful(),failures=[str(v) for v in result.failures],errors=[str(v) for v in result.errors]))
    if result.testsRun!=6 or not result.wasSuccessful():raise RuntimeError('SIX_REAL_NUMERICAL_CATEGORIES_REQUIRED')
    import numpy as np
    from scipy.optimize import minimize
    from model_math import make,objective,projected_gradient
    from oracle import check_gradient
    from frozen_offset import fit_offset
    from impossibility import early_failure
    policy=json.loads(Path(__file__).with_name('worker_policy.json').read_text());phase=policy['phase']
    manifest=json.loads((Path(data)/'manifest.json').read_text())
    if manifest['compartments']!=['A'] or manifest['group']!='development' or len(manifest['sessions'])!=13:raise PermissionError('FROZEN_DEVELOPMENT_A_ONLY')
    session=manifest['sessions'][0];path=Path(data)/session['file']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('A_INPUT_CHANGED')
    originals=json.loads(Path(__file__).with_name('original_training_diagnostics.json').read_text())['rows']
    from roster import validate
    validate(originals)
    index={(z['region'],z['family'],z['size'],z['ridge'],z['seed']):z for z in originals}
    rows=[];states={};condition=[];start=time.perf_counter()
    def stop(check,identity,stage):
        save('numerical_failure.json',dict(identity=identity,stage=stage,check=check))
        save('summary.json',dict(rows=rows,conditioning=condition,validation_access=False,final_access=False))
        save('gate_result.json',dict(gate='FAIL',phase=phase,scientific_verdict='NUMERICAL_INCONCLUSIVE',completed_fit_count=len(rows),
            converged_fit_count=sum(z['converged'] for z in rows),gradient_failures=1,failure='INDEPENDENT_NUMERICAL_CHECK_FAILED',validation_access=False,final_access=False))
        sys.exit(2)
    with np.load(path,allow_pickle=False) as arrays:
        if any(k.endswith(('_B','_C','_D')) for k in arrays.files):raise PermissionError('NONTRAINING_ARRAY')
        for region in ('CA1','DG'):
            y=arrays[region+'_A'];c=arrays['conditions_A'];o=arrays['orders_A']
            offset,_,x,_,_=fit_offset(session['session_id'],region,session['parent_AB_sha256'],y,y,c,c,o,o)
            singular=np.linalg.svd(x.reshape(-1,x.shape[-1]),compute_uv=False)
            condition.append(dict(region=region,context_singular_values=singular.tolist(),context_condition_number=float(singular[0]/singular[-1]) if singular[-1]>0 else None,
                history_log1p_max=float(np.max(np.log1p(y))),training_array_sha256=hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()))
            for family,sizes in (('Discrete',(2,3,4)),('Continuous',(1,2,4)),('Hybrid',(2,3,4))):
                for size in sizes:
                    for ridge in (.001,.01,.1,1.):
                        for seed in (11,23,37):
                            model=make(family,y,x,offset,size);initial=model.initial(seed);n=len(initial)
                            coordinates=sorted(set([0,n-1]+np.random.default_rng(20261013).choice(n,min(12,n),replace=False).tolist()))
                            initial_check=check_gradient(initial,model,ridge,family,size,coordinates);calls=[];accepted=[]
                            identity=dict(region=region,family=family,size=size,ridge=ridge,seed=seed)
                            if not initial_check['passed']:stop(initial_check,identity,'initial_before_fit')
                            def loss(theta):
                                value,g=objective(theta,model,ridge)
                                calls.append(dict(objective=value,gradient_inf=float(np.max(np.abs(g))),PG=projected_gradient(theta,g),bound_hits=int(np.sum(np.abs(theta)>=8))))
                                return value,g
                            def callback(theta):
                                value,g=objective(theta,model,ridge);accepted.append(dict(objective=value,PG=projected_gradient(theta,g)))
                            began=time.perf_counter();fit=minimize(loss,initial,jac=True,method='L-BFGS-B',bounds=[(-8.,8.)]*n,options=policy['options'],callback=callback)
                            value,g=objective(fit.x,model,ridge);pg=projected_gradient(fit.x,g)
                            terminal_check=check_gradient(fit.x,model,ridge,family,size,coordinates)
                            row=dict(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,family=family,size=size,ridge=ridge,seed=seed,
                                converged=bool(fit.success and pg<=.001 and np.isfinite(value)),optimizer_success=bool(fit.success),optimizer_message=str(fit.message),
                                iterations=int(fit.nit),objective_calls=int(fit.nfev),projected_gradient=pg,penalized_training_objective=value,
                                gradient_inf=float(np.max(np.abs(g))),bound_hits=int(np.sum(np.abs(fit.x)>=8)),parameter_count=n,
                                initial_gradient_check=initial_check,terminal_gradient_check=terminal_check,objective_history=calls,accepted_iteration_history=accepted,
                                elapsed_seconds=time.perf_counter()-began,validation_access=False,final_access=False)
                            if phase=='diagnosis':
                                old=index[(region,family,size,ridge,seed)]
                                row['original_replay_match']=all(row[k]==old[k] for k in ('converged','optimizer_success','optimizer_message','iterations','objective_calls','projected_gradient','penalized_training_objective','bound_hits'))
                            states[f'{region}_{family}_{size}_{ridge}_{seed}']=fit.x;rows.append(row)
                            save(f'{region}_{family}_{size}_{ridge}_{seed}.json',row)
                            if not terminal_check['passed']:stop(terminal_check,identity,'terminal_before_next_fit')
    errors=[z for z in rows if not z['initial_gradient_check']['passed'] or not z['terminal_gradient_check']['passed']]
    failure,possible=early_failure(rows,[session['session_id']])
    if phase=='diagnosis':
        passed=len(rows)==216 and not errors and all(z['original_replay_match'] for z in rows) and all('RELATIVE REDUCTION' in z['optimizer_message'] for z in rows) and all(z['iterations']<500 and z['objective_calls']<20000 for z in rows)
        verdict='DYNAMICS_AMENDMENT_ELIGIBLE' if passed else 'NUMERICAL_INCONCLUSIVE'
    else:passed=len(rows)==216 and not errors and failure is None;verdict='FIRST_MOUSE_NUMERICAL_PASS' if passed else 'NUMERICAL_INCONCLUSIVE'
    np.savez(output/'fitted_states.npz',**states)
    save('summary.json',dict(rows=rows,conditioning=condition,elapsed_seconds=time.perf_counter()-start,validation_access=False,final_access=False))
    save('gate_result.json',dict(gate='PASS' if passed else 'FAIL',phase=phase,scientific_verdict=verdict,completed_fit_count=len(rows),converged_fit_count=sum(z['converged'] for z in rows),
        gradient_failures=len(errors),possible_configuration_counts=possible,failure=None if passed else (failure if not errors else 'INDEPENDENT_NUMERICAL_CHECK_FAILED'),
        fitted_states_sha256=hashlib.sha256((output/'fitted_states.npz').read_bytes()).hexdigest(),validation_access=False,final_access=False))
    if not passed:sys.exit(2)

if __name__=='__main__':main()
