"""All historical scalar trajectories and saved coordinate gradient scales."""
import csv
import math
import study as r

def main():
    source=r.ROOT/'paper12_m4dynamics1/results/smoke/native/CA1_Continuous_4_0.001_11.json'
    old=r.load(source);history=old['objective_history'];accepted=old['accepted_iteration_history']
    if len(history)!=2230 or len(accepted)!=2000:raise RuntimeError('ORIGINAL_COMPLETE_TRAJECTORIES')
    target=r.HERE/'saved_trajectories.csv'
    with target.open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['kind','index','objective','PG','gradient_inf','bound_hits']);writer.writeheader()
        for kind,rows in (('objective_call',history),('accepted_iterate',accepted)):
            for i,row in enumerate(rows):writer.writerow(dict(kind=kind,index=i+1,**row))
    summary={}
    for kind,rows in (('objective_call',history),('accepted_iterate',accepted)):
        summary[kind]={'count':len(rows),'objective_first':rows[0]['objective'],'objective_last':rows[-1]['objective'],'objective_min':min(z['objective'] for z in rows),'PG_min':min(z['PG'] for z in rows),'PG_max':max(z['PG'] for z in rows),'PG_last':rows[-1]['PG'],'PG_le_0.001_count':sum(z['PG']<=.001 for z in rows),'finite':all(math.isfinite(z['objective']) and math.isfinite(z['PG']) for z in rows),'objective_increases':sum(rows[i]['objective']>rows[i-1]['objective']+1e-12 for i in range(1,len(rows)))}
    r.save(r.HERE/'saved_trajectory_audit.json',{'source_sha256':r.sha(source),'CSV_sha256':r.sha(target),'summary':summary,'full_coordinate_gradients_available_only_at':['initial','intermediate','endpoint'],'real_optimization_calls':0,'validation_access':False,'final_access':False})
    print('SAVED_TRAJECTORY_AUDIT',summary)
if __name__=='__main__':main()
