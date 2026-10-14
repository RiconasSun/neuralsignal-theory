"""One immutable A-only fit replay and bounded diagnostic examination."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)];out=Path(output)
    def save(name,obj):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('NATIVE_ROLE_REQUIRED')
    policy=json.loads(Path(__file__).with_name('protocol.json').read_text())
    import unittest
    result=unittest.TestResult();unittest.TestLoader().discover(str(Path(__file__).parent),pattern='test_diagnostics.py').run(result)
    synthetic=dict(count=result.testsRun,passed=result.wasSuccessful(),skips=len(result.skipped),failures=[str(x) for x in result.failures],errors=[str(x) for x in result.errors]);save('synthetic_tests.json',synthetic)
    if not result.wasSuccessful() or result.skipped or result.testsRun!=13:raise RuntimeError('INDEPENDENT_ORACLES_REQUIRED')
    import numpy as np
    from scipy.optimize import minimize
    from model_math import make,objective,projected_gradient
    from frozen_offset import fit_offset
    from oracle import check_gradient
    from diagnostics import inspect_vector,decide
    manifest=json.loads((Path(data)/'manifest.json').read_text())
    if manifest['group']!='development' or manifest['compartments']!=['A']:raise PermissionError('TRAINING_A_ONLY')
    session=manifest['sessions'][0]
    if session['mouse_id']!='744912849' or session['session_id']!='766640955':raise RuntimeError('EXACT_MOUSE_SESSION')
    file=Path(data)/session['file']
    if hashlib.sha256(file.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('INPUT_HASH_MISMATCH')
    with np.load(file,allow_pickle=False) as z:
        if any(k.endswith(('_B','_C','_D')) for k in z.files):raise PermissionError('NON_A_ARRAY')
        y=z['CA1_A'];conditions=z['conditions_A'];orders=z['orders_A']
        offset,_,context,_,_=fit_offset(session['session_id'],'CA1',session['parent_AB_sha256'],y,y,conditions,conditions,orders,orders)
    model=make('Continuous',y,context,offset,4);theta=model.initial(11);accepted=[];accepted_history=[];history=[]
    def loss(t):
        v,g=objective(t,model,.001);history.append(dict(objective=v,gradient_inf=float(np.abs(g).max()),PG=projected_gradient(t,g),bound_hits=int((np.abs(t)>=8).sum())));return v,g
    def callback(t):
        v,g=objective(t,model,.001);accepted.append(t.copy());accepted_history.append(dict(objective=v,PG=projected_gradient(t,g)))
        if len(accepted)%50==0:save('fit_progress_'+str(len(accepted))+'.json',dict(accepted_iterations=len(accepted),objective=v,PG=projected_gradient(t,g),validation_access=False,final_access=False))
    start=time.perf_counter();fit=minimize(loss,theta,jac=True,method='L-BFGS-B',bounds=[(-8.,8.)]*len(theta),options=policy['options'],callback=callback)
    loss_value,g=objective(fit.x,model,.001);coordinates=json.loads(Path(__file__).with_name('preserved_failure.json').read_text())['terminal_gradient_check']['coordinates']
    original=check_gradient(fit.x,model,.001,'Continuous',4,coordinates)
    initial_check=check_gradient(theta,model,.001,'Continuous',4,coordinates)
    endpoint=dict(iterations=int(fit.nit),objective_calls=int(fit.nfev),projected_gradient=projected_gradient(fit.x,g),penalized_training_objective=loss_value,optimizer_success=bool(fit.success),optimizer_message=str(fit.message),bound_hits=int((np.abs(fit.x)>=8).sum()),parameter_count=len(theta),terminal_gradient_check=original,initial_gradient_check=initial_check)
    old=json.loads(Path(__file__).with_name('preserved_failure.json').read_text())
    exact_fields=('iterations','objective_calls','projected_gradient','penalized_training_objective','optimizer_success','optimizer_message','bound_hits','parameter_count','terminal_gradient_check','initial_gradient_check')
    exact={k:endpoint[k]==old[k] for k in exact_fields};exact['objective_history']=history==old['objective_history'];exact['accepted_iteration_history']=accepted_history==old['accepted_iteration_history']
    # Parameter vectors were not saved by the old early-stop worker; recover only here.
    midpoint=len(accepted)//2;vectors=[theta,accepted[midpoint],fit.x];names=['initial','intermediate','endpoint']
    np.savez(out/'diagnostic_states.npz',**dict(zip(names,vectors)));np.savez(out/'accepted_states.npz',accepted=np.array(accepted))
    receipt=dict(target=policy['target'],data_manifest_sha256=hashlib.sha256((Path(data)/'manifest.json').read_bytes()).hexdigest(),data_file_sha256=session['sha256'],training_array_sha256=hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest(),context_sha256=hashlib.sha256(np.ascontiguousarray(context).tobytes()).hexdigest(),offset_sha256=hashlib.sha256(np.ascontiguousarray(offset).tobytes()).hexdigest(),endpoint=endpoint,exact_reproduction=exact,all_exact=all(exact.values()),accepted_iterates=len(accepted),intermediate_index=midpoint,elapsed_fit_seconds=time.perf_counter()-start,state_sha256=hashlib.sha256((out/'diagnostic_states.npz').read_bytes()).hexdigest(),validation_access=False,final_access=False,real_fits=1,M3_refits=0,offset_refits=0)
    save('reproduction.json',receipt)
    if not receipt['all_exact']:
        save('gate_result.json',dict(gate='FAIL',verdict='INCONCLUSIVE',reason='EXACT_FAILURE_REPRODUCTION_MISMATCH',validation_access=False,final_access=False));return
    stages=[];csvpath=out/'gradient_scan.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as f:
        writer=None
        for name,vector in zip(names,vectors):
            def progress(stage,scale,count):save('scan_'+stage+'_'+str(scale)+'.json',dict(stage=stage,completed_scale=scale,coordinate_rows=count,validation_access=False,final_access=False))
            summary,rows=inspect_vector(vector,model,.001,name,policy['scales'],policy['batch'],progress);stages.append(summary)
            if writer is None:writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
            writer.writerows(rows);save(name+'_audit.json',summary)
            save(name+'_progress.json',dict(completed_stage=name,rows=len(rows),validation_access=False,final_access=False))
    decision=decide(stages,original,endpoint,synthetic['passed']);save('decision.json',decision)
    save('gate_result.json',dict(gate='PASS',diagnostic_completed=True,verdict=decision['verdict'],coordinate_rows=len(theta)*len(policy['scales'])*3,real_fits=1,gradient_threshold=1e-5,PG_threshold=.001,original_scientific_failure_unchanged=True,validation_access=False,final_access=False,CSV_sha256=hashlib.sha256(csvpath.read_bytes()).hexdigest(),stages=stages))

if __name__=='__main__':main()
