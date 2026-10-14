"""Native A-only conditioning or exactly one preregistered candidate."""
import hashlib
import json
from pathlib import Path
import sys
import time

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)];out=Path(output);code=Path(__file__).parent
    def save(name,value):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('ZERO_CAPABILITY_ROLE_REQUIRED')
    import unittest
    tests=unittest.TestResult();unittest.TestLoader().discover(str(code),pattern='test_conditioning.py').run(tests)
    save('synthetic_tests.json',{'passed':tests.wasSuccessful(),'count':tests.testsRun,'skips':len(tests.skipped),'errors':[str(z) for z in tests.errors],'failures':[str(z) for z in tests.failures]})
    expected_tests=15 if json.loads((code/'policy.json').read_text())['phase']=='audit' else 17
    if not tests.wasSuccessful() or tests.skipped or tests.testsRun!=expected_tests:raise RuntimeError('SYNTHETIC_METHOD_SUPPORT_REQUIRED')
    import numpy as np
    from model_math import make,objective,projected_gradient
    from frozen_offset import fit_offset
    from independent_ad import value_gradient
    from conditioning import digest,blocks,hessian,spectrum,scale_from_diagonal,saturation
    policy=json.loads((code/'policy.json').read_text());manifest=json.loads((Path(data)/'manifest.json').read_text())
    if manifest['group']!='development' or manifest['compartments']!=['A']:raise PermissionError('TRAINING_A_ONLY')
    session=manifest['sessions'][0];file=Path(data)/session['file']
    if session['mouse_id']!='744912849' or session['session_id']!='766640955' or hashlib.sha256(file.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('EXACT_FROZEN_A_TARGET')
    with np.load(file,allow_pickle=False) as z:
        if any(k.endswith(('_B','_C','_D')) for k in z.files):raise PermissionError('NON_A_INPUT')
        y=z['CA1_A'];conditions=z['conditions_A'];orders=z['orders_A']
        offset,_,context,_,_=fit_offset(session['session_id'],'CA1',session['parent_AB_sha256'],y,y,conditions,conditions,orders,orders)
    model=make('Continuous',y,context,offset,4);saved=json.loads((code/'saved_vectors.json').read_text());vectors={name:np.array(v,dtype=float) for name,v in saved['vectors'].items()}
    for name,v in vectors.items():
        if len(v)!=384 or digest(v)!=saved['theta_sha256'][name]:raise RuntimeError('SAVED_VECTOR_IDENTITY')
    def array_digest(v):return hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()
    bindings={'training_array_sha256':array_digest(y),'context_sha256':array_digest(context),'offset_sha256':array_digest(offset),'A_manifest_sha256':hashlib.sha256((Path(data)/'manifest.json').read_bytes()).hexdigest(),'data_file_sha256':session['sha256'],'parameters':384,'ridge':.001,'physical_bounds':[-8,8],'offset_refits':0,'M3_refits':0,'validation_access':False,'final_access':False}
    save('input_binding.json',bindings)
    start=time.perf_counter()
    if policy['phase']=='audit':
        states={};gradients={}
        for name,t in vectors.items():
            f,g=objective(t,model,.001);adf,adg,_=value_gradient(t,y,context,offset,4,.001)
            states[name]={'theta_sha256':digest(t),'objective':f,'PG':projected_gradient(t,g),'AD_PG':projected_gradient(t,adg),'AD_scaled_error':float((np.abs(g-adg)/np.maximum(1,np.maximum(np.abs(g),np.abs(adg)))).max()),'objective_error':abs(f-adf),'blocks':blocks(t,g,y.shape[-1],context.shape[-1],4),'tanh':saturation(t,y,context,4)}
            gradients[name]=g
            if states[name]['AD_scaled_error']>1e-5 or states[name]['objective_error']>1e-10:raise RuntimeError('BASE_GRADIENT_IDENTITY_REQUIRED')
        matrices={};curvature={};calls=0;t=vectors['endpoint']
        def fun(v):
            nonlocal calls
            if calls>=1536:raise RuntimeError('AUDIT_BUDGET')
            calls+=1;return objective(v,model,.001)
        for scale in policy['hessian_scales']:
            H,cross=hessian(t,fun,scale);matrices[str(scale)]=H
            curvature[str(scale)]={'spectrum':spectrum(H),'diagonal':np.diag(H).tolist(),'symmetric_probe_crossing_columns':cross,'gradient_calls':768}
            save('curvature_'+str(scale)+'.json',curvature[str(scale)])
        chosen=matrices[str(1e-7)];other=matrices[str(1e-8)];S=scale_from_diagonal(np.diag(chosen));g=gradients['endpoint']
        states['endpoint']['blocks']=blocks(t,g,y.shape[-1],context.shape[-1],4,np.diag(chosen))
        dominant=max(states['endpoint']['blocks'],key=lambda name:states['endpoint']['blocks'][name]['physical_PG'])
        np.savez(out/'audit_matrices.npz',H_1e7=chosen,H_1e8=other)
        save('scale.json',{'formula':policy['scale_rule'],'S':S.tolist(),'S_sha256':digest(S),'initial_theta_sha256':digest(t),'source_diagonal':np.diag(chosen).tolist()})
        summary={'stages':states,'curvature':curvature,'scale_disagreement_inf_relative':float(np.linalg.norm(chosen-other,np.inf)/max(1.,np.linalg.norm(chosen,np.inf))),'endpoint_PG_dominant_block':dominant,'Hessian_gradient_calls':calls,'new_optimization_fits':0,'real_data_scope':'DevelopmentTrainingA','elapsed_seconds':time.perf_counter()-start}
        save('conditioning_audit.json',summary);save('gate_result.json',{'gate':'PASS','audit_completed':True,'new_optimization_fits':0,'Hessian_gradient_calls':calls,'gradient_checks_passed':True,'validation_access':False,'final_access':False});return
    if policy['phase']!='candidate' or policy['candidate']['id'] not in ('A','B','C'):raise RuntimeError('REGISTERED_PHASE_REQUIRED')
    from policies import run,Coordinates
    from oracle import check_gradient
    scale_info=json.loads((code/'scale.json').read_text());S=np.array(scale_info['S']);initial=vectors['endpoint'];candidate=policy['candidate']
    if digest(S)!=policy['S_sha256'] or digest(initial)!=policy['initial_theta_sha256']:raise RuntimeError('EXACT_REGISTERED_INITIAL_SCALE')
    def progress(entry):save('progress_'+str(entry['accepted'])+'.json',dict(candidate=candidate['id'],**entry,validation_access=False,final_access=False))
    result=run(candidate,initial,S,lambda t:objective(t,model,.001),progress);theta=result.pop('theta')
    save('termination_history.json',result);np.savez(out/'endpoint.npz',theta=theta)
    f,g=objective(theta,model,.001);adf,adg,parts=value_gradient(theta,y,context,offset,4,.001)
    coordinates=Coordinates(S);recovered=coordinates.forward(coordinates.inverse(theta));transformed_f,transformed_g=objective(recovered,model,.001)
    error=float((np.abs(g-adg)/np.maximum(1,np.maximum(np.abs(g),np.abs(adg)))).max());bounds=bool(np.all(theta>=-8) and np.all(theta<=8));finite=bool(np.isfinite(theta).all() and np.isfinite(f) and np.isfinite(g).all() and np.isfinite(adg).all());PG=projected_gradient(theta,g);ADPG=projected_gradient(theta,adg)
    old=json.loads((code/'preserved_failure.json').read_text());historical=check_gradient(theta,model,.001,'Continuous',4,old['terminal_gradient_check']['coordinates'])
    transform_gradient_error=float(np.abs(S*g-S*transformed_g).max())
    independent=finite and bounds and error<=1e-5 and abs(f-adf)<=1e-10 and abs(f-transformed_f)<=1e-10 and np.isfinite(transform_gradient_error) and transform_gradient_error<=1e-5 and float(np.abs(theta-recovered).max())<=1e-12
    passes=independent and PG<=.001 and ADPG<=.001
    endpoint={'candidate':candidate['id'],'objective':float(f),'PG':PG,'AD_PG':ADPG,'AD_objective':adf,'AD_objective_error':abs(f-adf),'AD_abs_error':float(np.abs(g-adg).max()),'AD_scaled_error':error,'finite':finite,'bounds_pass':bounds,'bound_hits':int((np.abs(theta)>=8).sum()),'transform_objective_error':abs(f-transformed_f),'transform_gradient_error':float(np.abs(S*g-S*transformed_g).max()),'coordinate_roundtrip_error':float(np.abs(theta-recovered).max()),'theta_sha256':digest(theta),'theta':theta.tolist(),'analytical_gradient':g.tolist(),'AD_gradient':adg.tolist(),'block_summary':blocks(theta,g,y.shape[-1],context.shape[-1],4),'tanh':saturation(theta,y,context,4),'historical_fixed_checker':historical,'historical_failures_unchanged':True,'independent_checks_pass':independent,'feasible':passes,'optimizer_success':result['solver_success'],'optimizer_status':result['solver_status'],'optimizer_message':result['solver_message'],'iterations_reported':result['solver_iterations'],'accepted_steps':result['accepted_count'],'warm_steps':result['warm_accepted'],'objective_gradient_calls':result['call_count'],'solver_nfev':result['solver_nfev'],'elapsed_seconds':time.perf_counter()-start,'validation_access':False,'final_access':False}
    save('endpoint.json',endpoint);save('gate_result.json',{'gate':'PASS','bounded_candidate_completed':True,'candidate':candidate['id'],'feasible':passes,'independent_checks_pass':independent,'PG':PG,'AD_PG':ADPG,'new_optimization_candidates':1,'objective_gradient_calls':result['call_count'],'call_cap':candidate['objective_gradient_call_cap'],'scientific_outcome':'OPTIMIZER_FEASIBILITY' if passes else 'OPTIMIZATION_INCONCLUSIVE','original_scientific_failure_unchanged':True,'validation_access':False,'final_access':False})

if __name__=='__main__':main()
