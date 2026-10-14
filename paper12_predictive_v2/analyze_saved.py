"""Public saved-score statistics; cannot open neural counts or final artifacts."""
import study as r
def build():
    import numpy as np
    from mouse_statistics import PRIMARY,aggregate,holm
    rows=r.load(r.HERE/'results/science/native/scientific_scores.json')['rows'];stats=aggregate(rows)
    old=r.load(r.HERE/'results/reused_M3_records.json');baselines=[]
    for mouse in stats['primary']['mouse_ids']:
        for region in ('CA1','DG'):
            ref=[z for z in old if z['mouse_id']==mouse and z['region']==region and z['kind']=='stationary'];base=float(np.mean([z['validation_LL_nats_per_unit_bin'] for z in ref]))
            for model in ('stationary','history','population','event','drift','combined'):
                selected=[z for z in old if z['mouse_id']==mouse and z['region']==region and z['kind']==model and z['ridge']==(None if model=='stationary' else .1)]
                if len(selected)!=3:raise RuntimeError('ALL_SEEDS_FIXED_RIDGE')
                ll=float(np.mean([z['validation_LL_nats_per_unit_bin'] for z in selected]));baselines.append({'mouse_id':mouse,'region':region,'model':model,'LL':ll,'gain_over_stationary':ll-base})
    null_summary={};pooled_p=[];regional_p=[];keys=[]
    for suite in ('T','S','B','O'):
        ca=[];dg=[];oc=[];od=[]
        for mouse in stats['primary']['mouse_ids']:
            case=next(z['session_id'] for z in rows if z['mouse_id']==mouse)
            for region,values,observed in [('CA1',ca,oc),('DG',dg,od)]:
                z=r.load(r.HERE/f'results/nulls_complete/native/{case}_{region}_{suite}.json');values.append(z['gains']);observed.append(z['observed'])
        ca=np.array(ca);dg=np.array(dg);pool=(ca+dg).mean(axis=0)/2;difference=(ca-dg).mean(axis=0);obs_pool=(np.array(oc)+np.array(od)).mean(axis=0)/2;obs_difference=(np.array(oc)-np.array(od)).mean(axis=0);center=difference.mean(axis=0)
        for i,k in enumerate(PRIMARY):
            a=float((1+np.sum(pool[:,i]>=obs_pool[i]))/1000);b=float((1+np.sum(np.abs(difference[:,i]-center[i])>=abs(obs_difference[i]-center[i])))/1000)
            key=suite+'_'+k;keys.append(key);pooled_p.append(a);regional_p.append(b)
            null_summary[key]={'suite':suite,'contrast':k,'observed_pooled_gain':float(obs_pool[i]),'null_pooled_mean':float(pool[:,i].mean()),'null_pooled95':np.quantile(pool[:,i],[.025,.975]).tolist(),'pooled_exceedance_p':a,'observed_CA1_minus_DG':float(obs_difference[i]),'null_CA1_minus_DG_mean':float(center[i]),'null_CA1_minus_DG95':np.quantile(difference[:,i],[.025,.975]).tolist(),'regional_centered_exceedance_p':b,'replicates':999,'mice':13,'interpretation':'Exploratory fixed-predictor stress test, conditional on registered assumptions; not refit/M4 or model-free causal test'}
    for k,a,b in zip(keys,holm(pooled_p),holm(regional_p)):null_summary[k].update(pooled_holm_p=a,regional_holm_p=b)
    return {'mouse_statistics':stats,'fixed_ridge_baselines':baselines,'null_statistics':null_summary,'scope':'Exploratory Development B; A fitting; final unexposed','units':'nats per actual nominal curated-release unit-bin','final_access':False}
def main():
    value=build();r.save(r.HERE/'results/exploratory_statistics.json',value)
    print({k:{'effect':v['mean_CA1_minus_DG'],'CI95':v['CI95'],'holm_p':v['holm_p']} for k,v in value['mouse_statistics']['primary']['statistics'].items()})
if __name__=='__main__':main()
