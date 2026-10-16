"""Four registered fixed-coefficient controls, pure arrays and explicit RNG."""
import numpy as np
from fractions import Fraction
from .predictive import evaluate,baseline_eta
from .animal_stats import holm

LABELS=['B0','B1','B2','B3','B4','D','C','S','Bstar']
SUITES=['temporal','history','task_order','conditional_Bstar']
SEEDS=dict(zip(SUITES,[130101,130102,130103,130104]))


def temporal(y,rng):
    y=np.asarray(y)
    if y.ndim!=3 or y.shape[1:]!=(30,8):raise ValueError('Original30-bin8unit epochs required')
    out=y.copy()
    for epoch in range(len(y)):
        for unit in range(8):
            for start in range(0,30,5):out[epoch,start:start+5,unit]=rng.permutation(y[epoch,start:start+5,unit])
    return out


def donors(ordinals,rng):
    ordinals=np.asarray(ordinals)
    if ordinals.ndim!=1 or len(set(ordinals.tolist()))!=len(ordinals) or np.any((ordinals<1)|(ordinals>120)):
        raise ValueError('Unique original chronological epoch ordinals required')
    quartiles=(ordinals-1)//30;indices=np.arange(len(ordinals))
    out=np.empty(len(ordinals),dtype=np.int64)
    for quartile in np.unique(quartiles):
        group=indices[quartiles==quartile]
        if len(group)<2:raise ValueError('History control requires >=2epochs in every partition/order quartile; no pooling')
        while True:
            candidate=rng.permutation(group)
            if np.all(candidate!=group):break
        out[group]=candidate
    return out


def conditional_counts(q,bundle,rng):
    q=np.asarray(q)
    if q.ndim!=3 or q.shape[1:]!=(30,11) or not np.isfinite(q).all():raise ValueError('Full frozen30-bin nuisance trajectories required')
    generated=np.zeros((*q.shape[:2],8),dtype=np.int64)
    # Each mean uses only already generated bins. All warm-up bins are generated.
    for t in range(30):
        eta=baseline_eta(generated,q,bundle,bundle['Bstar'])[:,t]
        with np.errstate(over='raise',invalid='raise'):means=np.exp(eta)
        if not np.isfinite(means).all():raise ValueError('Conditional model null nonfinite mean; no clipping or rescue')
        generated[:,t]=rng.poisson(means)
    return generated


def replicate(suite,y,q,bundle,ordinals,rng):
    y=np.asarray(y);q=np.asarray(q)
    if len(ordinals)!=len(y):raise ValueError('Original partition ordinal identity mismatch')
    if suite=='temporal':return evaluate(temporal(y,rng),q,bundle)
    if suite=='history':
        donor=donors(ordinals,rng)
        return evaluate(y,q,bundle,history_driver=y[donor],filter_driver=y[donor])
    if suite=='task_order':return evaluate(y,q[rng.permutation(len(q))],bundle)
    if suite=='conditional_Bstar':return evaluate(conditional_counts(q,bundle,rng),q,bundle)
    raise ValueError('Unregistered control suite')


def effects(scores):
    a=np.asarray(scores)
    if a.shape[-1]!=len(LABELS) or not np.isfinite(a).all():raise ValueError('All9finite score labels required')
    b4,D,C,S,Bstar=[a[...,LABELS.index(k)] for k in ['B4','D','C','S','Bstar']]
    return np.stack([D-b4,C-b4,D-C,D-Bstar,C-Bstar,D-S],axis=-1)


def exact_total(values):
    ratios=[float(v).as_integer_ratio() for v in values]
    denominator=max(den for _,den in ratios)
    return Fraction(sum(num*(denominator//den) for num,den in ratios),denominator)


def linear_q95(values):
    ordered=sorted(values);rank=Fraction((len(ordered)-1)*95,100)
    lower=rank.numerator//rank.denominator;weight=rank-lower
    return (1-weight)*ordered[lower]+weight*ordered[min(lower+1,len(ordered)-1)]


def summarize(arrays,observed_scores,mouse_order):
    if set(arrays)!=set(SUITES) or len(mouse_order)<8 or len(mouse_order)!=len(set(mouse_order)):
        raise ValueError('All four999replicate paired-mouse controls required')
    n=len(mouse_order);obs_effects=effects(np.array([[observed_scores[m][k] for k in LABELS] for m in mouse_order]))
    observed_totals=[exact_total(obs_effects[:,j]) for j in range(6)]
    observed=np.array([float(value/n) for value in observed_totals])
    means={};totals={}
    for suite,array in arrays.items():
        a=np.asarray(array)
        if a.shape!=(999,len(mouse_order),len(LABELS)):raise ValueError('Exactly999replicates/all original mice required')
        difference=effects(a)
        totals[suite]=[[exact_total(difference[r,:,j]) for j in range(6)] for r in range(999)]
        means[suite]=np.array([[float(value/n) for value in row] for row in totals[suite]])
    exceed=[sum(row[j]>=observed_totals[j] for row in totals['conditional_Bstar']) for j in [3,4]]
    p=np.array([(1+count)/1000 for count in exceed])
    adjusted=holm(p);references={};quantiles={}
    for suite in SUITES[:3]:
        quantiles[suite]=[linear_q95([row[j] for row in totals[suite]]) for j in range(6)]
        quantile=np.array([float(value/n) for value in quantiles[suite]])
        references[suite]={'mean_effects':means[suite].mean(axis=0).tolist(),'q95_effects':quantile.tolist(),
            'observed_minus_reference_mean':(observed-means[suite].mean(axis=0)).tolist(),
            'reference_type':'Assumption-dependent stress comparison, not randomization-valid biological significance'}
    guards={}
    for j,name in enumerate(['D','C']):
        above=[observed_totals[3+j]>quantiles[suite][3+j] for suite in ['temporal','history']]
        guards[name]={'conditional_Bstar_p':float(p[j]),'conditional_Bstar_Holm2_p':float(adjusted[j]),
            'conditional_inclusive_exceedances':exceed[j],
            'above_temporal_q95':bool(above[0]),'above_history_q95':bool(above[1]),
            'numerical_reference_conditions_met':bool(adjusted[j]<=.05 and all(above)),
            'interpretation':'Necessary guard only; primary/Bstar statistics, sensitivities and defensible assumptions also required'}
    return {'replicates_per_suite':999,'seeds':SEEDS,'mouse_order':mouse_order,'observed_equal_mouse_effects':observed.tolist(),
        'stress_references':references,'beyond_baseline_null_guards':guards,
        'decision_arithmetic':'Exact dyadic totals of supplied per-mouse binary64 effects; inclusive conditional tails; strict reference comparisons against exact nominal95/100 linear interpolation. Display floats do not decide gates.',
        'task_order_stress_can_rescue_failed_claim':False,'D_minus_C_parametric_superiority_test_required':False},means
