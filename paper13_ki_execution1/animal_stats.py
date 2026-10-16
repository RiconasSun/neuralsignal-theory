"""Frozen mouse-level contrasts, exact sign enumeration and whole-mouse CI."""
import hashlib
import itertools
import numpy as np

CONTRASTS=['D_minus_B4','C_minus_B4','D_minus_C','D_minus_Bstar','C_minus_Bstar','D_minus_S']


def holm(pvalues):
    p=np.asarray(pvalues,dtype=float)
    if p.ndim!=1 or not len(p) or not np.isfinite(p).all() or np.any((p<0)|(p>1)):raise ValueError('Valid pvalues required')
    order=np.argsort(p,kind='stable');adjusted=np.empty_like(p);running=0.
    for rank,index in enumerate(order):
        running=max(running,(len(p)-rank)*p[index]);adjusted[index]=min(1.,running)
    return adjusted


def exact_signflip(values):
    v=np.asarray(values,dtype=float)
    if v.ndim!=1 or not 8<=len(v)<=10 or not np.isfinite(v).all():raise ValueError('8to10finite paired mouse effects required')
    # Every finite binary64 is an exact rational with a power-of-two denominator.
    # Compare arbitrary-precision integer sums, so cancellation cannot lose ties.
    ratios=[float(value).as_integer_ratio() for value in v]
    denominator=max(d for _,d in ratios)
    integers=[num*(denominator//den) for num,den in ratios]
    observed=abs(sum(integers));assignments=2**len(v)
    exceed=sum(abs(sum(sign*value for sign,value in zip(signs,integers)))>=observed
               for signs in itertools.product([-1,1],repeat=len(v)))
    return {'p':exceed/assignments,'exceedances_including_ties':exceed,'assignments':assignments,
        'observed_abs_mean':abs(float(v.mean())),
        'exact_tail_arithmetic':'Common-power-of-two integer sums of exact supplied binary64 values; inclusive ties; no epsilon/rounding',
        'null_assumption':'Fair conditional signs / joint sign symmetry; not arbitrary mean-zero validity'}


def contrast_matrix(scores,mouse_order):
    if len(mouse_order)!=len(set(mouse_order)) or not 8<=len(mouse_order)<=10:raise ValueError('Unique paired mouse identities required')
    if set(scores)!=set(mouse_order):raise ValueError('All and only the registered mouse scores required')
    rows=[]
    for mouse in mouse_order:
        s=scores[mouse]
        if set(s)!={'B4','D','C','Bstar','S'}:raise ValueError('All primary and guard scores required')
        if not np.isfinite(list(s.values())).all():raise ValueError('Nonfinite paired score; do not silently drop mouse')
        rows.append([s['D']-s['B4'],s['C']-s['B4'],s['D']-s['C'],s['D']-s['Bstar'],s['C']-s['Bstar'],s['D']-s['S']])
    return np.asarray(rows,dtype=float)


def whole_mouse_bootstrap(matrix):
    x=np.asarray(matrix,dtype=float)
    if x.ndim!=2 or x.shape[1]!=6 or not 8<=len(x)<=10 or not np.isfinite(x).all():raise ValueError('Finite paired six-contrast mouse matrix required')
    indices=np.random.default_rng(130041).integers(0,len(x),size=(10000,len(x)),dtype=np.int64)
    means=x[indices].mean(axis=1)
    interval=np.quantile(means,[.025,.975],axis=0,method='linear')
    return interval,indices,means


def summarize(scores,mouse_order):
    x=contrast_matrix(scores,mouse_order);interval,indices,bootstrap=whole_mouse_bootstrap(x)
    tests=[exact_signflip(x[:,j]) for j in range(6)]
    adjusted=np.r_[holm([t['p'] for t in tests[:3]]),holm([t['p'] for t in tests[3:]])]
    rows={}
    for j,name in enumerate(CONTRASTS):
        v=x[:,j];mean=float(v.mean());lomo=np.array([np.delete(v,k).mean() for k in range(len(v))])
        lower,upper=interval[:,j];positive=int(np.count_nonzero(v>0));negative=int(np.count_nonzero(v<0))
        positive_conditions=bool(adjusted[j]<=.05 and lower>0 and positive>=.75*len(v) and np.all(lomo>0))
        negative_conditions=bool(adjusted[j]<=.05 and upper<0 and negative>=.75*len(v) and np.all(lomo<0))
        rows[name]={'mean_nats_per_nominal_unit_bin':mean,'mouse_effects':v.tolist(),
            'CI95_percentile':[float(lower),float(upper)],'signflip':tests[j],'Holm_adjusted_p':float(adjusted[j]),
            'multiplicity_family':'three_primaries' if j<3 else 'three_interpretation_guards',
            'positive_mice':positive,'negative_mice':negative,'zero_mice':int(np.count_nonzero(v==0)),
            'leave_one_mouse_out_means':lomo.tolist(),'positive_statistical_conditions_met':positive_conditions,
            'negative_statistical_conditions_met':negative_conditions if name=='D_minus_C' else None,
            'final_claim_status':'NOT_CLASSIFIED; applicable null/sensitivity/coverage/temporal gates still required'}
    result={'mouse_order':mouse_order,'mouse_is_independent_unit':True,'equal_mouse_aggregation':True,'contrasts':rows,
        'bootstrap_replicates':10000,'bootstrap_seed':130041,'CI_method':'percentile .025/.975; quantile linear',
        'joint_mouse_bootstrap_indices_sha256':hashlib.sha256(indices.tobytes()).hexdigest(),
        'final_claims_evaluated':False,'non_significance_is_not_equivalence':True,
        'sampling_limit':'Single-lab selected mouse cohort; sign symmetry and bootstrap mouse-sampling assumptions are not established by model fit.'}
    return result,{'mouse_contrast_matrix':x,'bootstrap_mouse_indices':indices,'bootstrap_contrast_means':bootstrap}
