"""Aggregate the three completed bounded candidates without rerunning fits."""
import math
import csv
import study as r
from audit_saved import check_endpoint
def main():
    protocol=r.load(r.HERE/'candidate_protocol.json');scale=r.load(r.HERE/'results/audit/native/scale.json');endpoints=[];calls=0
    for name in ('A','B','C'):
        endpoint=r.load(r.HERE/f'results/{name}/native/endpoint.json');history=r.load(r.HERE/f'results/{name}/native/termination_history.json');policy=next(p for p in protocol['candidates'] if p['id']==name)
        check_endpoint(endpoint,history,policy,scale['S']);endpoints.append(endpoint);calls+=history['call_count']
    if calls>24500:raise RuntimeError('NO_BUDGET_EXPANSION')
    outcome='OPTIMIZER_FEASIBILITY' if any(z['feasible'] for z in endpoints) else 'OPTIMIZATION_INCONCLUSIVE'
    proposed=next((z['candidate'] for z in endpoints if z['feasible']),None)
    r.save(r.HERE/'results/study_outcome.json',{'mission':'P12-M4-CONDITIONING-OPTIMIZER-1','base':r.BASE,'scientific_outcome':outcome,'candidate_count':3,'feasible_candidates':[z['candidate'] for z in endpoints if z['feasible']],'proposal_candidate_in_original_registered_order':proposed,'objective_gradient_calls':calls,'total_call_cap':24500,'no_replacements_or_retries':True,'original_scientific_failures_immutable':True,'full_M4_pass':False,'M5':False,'M6':False,'M7':False,'validation_access':False,'final_access':False,'stop_after_bounded_study':True})
    with (r.HERE/'candidate_outcomes.csv').open('x',encoding='utf-8',newline='') as f:
        keys=['candidate','objective','PG','AD_PG','AD_scaled_error','AD_objective_error','transform_gradient_error','finite','bounds_pass','optimizer_success','optimizer_status','iterations_reported','accepted_steps','warm_steps','objective_gradient_calls','solver_nfev','feasible','elapsed_seconds'];writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for z in endpoints:writer.writerow({k:z[k] for k in keys})
    print('STUDY_COMPLETED',outcome,'candidates3','calls',calls,'proposal',proposed)
if __name__=='__main__':main()
