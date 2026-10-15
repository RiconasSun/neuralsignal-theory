"""Mouse-level exploratory inference from public scalar scores only."""
import itertools
import numpy as np
PRIMARY=['own','population','stimulus_time','combined']
def holm(values):
    values=np.asarray(values,dtype=float);order=np.argsort(values,kind='stable');answer=np.empty(len(values));last=0.
    for rank,i in enumerate(order):last=max(last,min(1.,(len(values)-rank)*values[i]));answer[i]=last
    return answer.tolist()
def paired(values,seed=120214):
    x=np.asarray(values,dtype=float);n=len(x)
    if n<8:raise ValueError('MINIMUM_EIGHT_PAIRED_MICE')
    signs=np.array(list(itertools.product((-1.,1.),repeat=n)))
    p=float(np.mean(np.abs(signs@x/n)>=abs(float(x.mean()))-1e-15))
    random=np.random.default_rng(seed);resamples=x[random.integers(0,n,size=(10000,n))].mean(axis=1)
    return {'mice':n,'mean_CA1_minus_DG':float(x.mean()),'CI95':np.quantile(resamples,[.025,.975]).tolist(),'paired_signflip_p':p,'bootstrap_replicates':10000,'signflip_assignments':2**n,'mouse_differences':x.tolist(),'leave_one_mouse_out_means':[(float(x.sum()-v)/(n-1)) for v in x]}
def aggregate(rows):
    views=sorted({r['view'] for r in rows});result={}
    for view in views:
        local=[r for r in rows if r['view']==view];mice=sorted({r['mouse_id'] for r in local});paired_rows=[]
        for mouse in mice:
            regions={r['region']:r for r in local if r['mouse_id']==mouse}
            if set(regions)=={'CA1','DG'}:paired_rows.append((mouse,regions))
        if len(paired_rows)<8:
            result[view]={'mice':len(paired_rows),'status':'INSUFFICIENT_COVERAGE_NO_GROUP_INFERENCE','mouse_ids':[m for m,r in paired_rows]};continue
        statistics={k:paired([r['CA1']['gains'][k]-r['DG']['gains'][k] for m,r in paired_rows]) for k in PRIMARY}
        for k in PRIMARY:
            statistics[k]['mean_CA1_gain']=float(np.mean([r['CA1']['gains'][k] for m,r in paired_rows]));statistics[k]['mean_DG_gain']=float(np.mean([r['DG']['gains'][k] for m,r in paired_rows]))
        if view=='primary':
            adjusted=holm([statistics[k]['paired_signflip_p'] for k in PRIMARY])
            for k,p in zip(PRIMARY,adjusted):statistics[k]['holm_p']=p
        else:
            for k in PRIMARY:statistics[k].pop('paired_signflip_p')
        result[view]={'mice':len(paired_rows),'mouse_ids':[m for m,r in paired_rows],'statistics':statistics,'status':'EXPLORATORY_PRIMARY' if view=='primary' else 'DESCRIPTIVE_SENSITIVITY_NO_SELECTION'}
    return result
