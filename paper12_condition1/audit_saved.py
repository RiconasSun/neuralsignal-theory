"""Independently reconstruct trial gates from public saved endpoint vectors."""
import hashlib
import array
import math

def sha_vector(values):return hashlib.sha256(array.array('d',values).tobytes()).hexdigest()
def pg(theta,gradient):return max(abs(g) if not (t<=-8 and g>0 or t>=8 and g<0) else 0 for t,g in zip(theta,gradient))
def check_endpoint(endpoint,history,policy,scale):
    t=endpoint['theta'];g=endpoint['analytical_gradient'];a=endpoint['AD_gradient']
    if not len(t)==len(g)==len(a)==384:raise RuntimeError('384_COORDINATES_REQUIRED')
    if sha_vector(t)!=endpoint['theta_sha256']:raise RuntimeError('VECTOR_CHANGED')
    finite=all(math.isfinite(x) for v in (t,g,a) for x in v) and math.isfinite(endpoint['objective'])
    bounds=all(-8<=x<=8 for x in t);analytic_pg=pg(t,g);ad_pg=pg(t,a)
    abs_error=max(abs(x-y) for x,y in zip(g,a));scaled=max(abs(x-y)/max(1,abs(x),abs(y)) for x,y in zip(g,a))
    for name,value in (('PG',analytic_pg),('AD_PG',ad_pg),('AD_abs_error',abs_error),('AD_scaled_error',scaled)):
        if not math.isclose(value,endpoint[name],rel_tol=1e-12,abs_tol=1e-12):raise RuntimeError('DERIVATIVE_METRIC_CHANGED:'+name)
    if bounds!=endpoint['bounds_pass'] or finite!=endpoint['finite']:raise RuntimeError('DOMAIN_FINITE_CHANGED')
    if not math.isclose(abs(endpoint['objective']-endpoint['AD_objective']),endpoint['AD_objective_error'],rel_tol=1e-12,abs_tol=1e-12):raise RuntimeError('INDEPENDENT_OBJECTIVE_ARITHMETIC')
    independent=finite and bounds and scaled<=1e-5 and endpoint['AD_objective_error']<=1e-10 and endpoint['transform_objective_error']<=1e-10 and math.isfinite(endpoint['transform_gradient_error']) and endpoint['transform_gradient_error']<=1e-5 and endpoint['coordinate_roundtrip_error']<=1e-12
    feasible=independent and analytic_pg<=.001 and ad_pg<=.001
    if independent!=endpoint['independent_checks_pass'] or feasible!=endpoint['feasible']:raise RuntimeError('SCIENTIFIC_GATE_CHANGED')
    calls=history['calls'];accepted=history['accepted']
    if len(calls)!=history['call_count'] or len(calls)!=endpoint['objective_gradient_calls'] or len(calls)>policy['objective_gradient_call_cap'] or [z['call'] for z in calls]!=list(range(1,len(calls)+1)):raise RuntimeError('CALL_LEDGER')
    if len(accepted)!=history['accepted_count'] or len(accepted)!=endpoint['accepted_steps'] or [z['accepted'] for z in accepted]!=list(range(1,len(accepted)+1)):raise RuntimeError('ITERATION_LEDGER')
    if policy['kind']=='adam_lbfgsb' and history['warm_accepted']!=300:raise RuntimeError('FIXED_WARM_SCHEDULE')
    if any(z['call_count']>len(calls) for z in accepted):raise RuntimeError('ACCEPTED_CALL_REFERENCE')
    if feasible and any(not z['finite'] for z in calls):raise RuntimeError('FEASIBILITY_REQUIRES_FINITE_TRIAL_HISTORY')
    if accepted and (not math.isclose(accepted[-1]['objective'],endpoint['objective'],rel_tol=1e-12,abs_tol=1e-12) or not math.isclose(accepted[-1]['PG'],endpoint['PG'],rel_tol=1e-10,abs_tol=1e-10)):raise RuntimeError('FINAL_RECORDED_STATE_IDENTITY')
    return feasible
