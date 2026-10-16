"""Same three registered stress procedures; failed conditional reference unavailable."""
import numpy as np
from paper13_ki_execution1 import control_core as original

LABELS=original.LABELS
SUITES=original.SUITES[:3]
SEEDS={name:original.SEEDS[name] for name in SUITES}


def replicate(suite,*args,**kwargs):
    if suite not in SUITES:raise PermissionError('Conditional Bstar null FAILED_UNAVAILABLE; never rerun or replace')
    return original.replicate(suite,*args,**kwargs)


def summarize(arrays,observed_scores,mouse_order):
    if set(arrays)!=set(SUITES) or len(mouse_order)<8 or len(mouse_order)!=len(set(mouse_order)):
        raise ValueError('All three original999 paired-mouse suites required; failed fourth retained unavailable')
    n=len(mouse_order);obs=original.effects(np.array([[observed_scores[m][k] for k in LABELS] for m in mouse_order]))
    observed_totals=[original.exact_total(obs[:,j]) for j in range(6)]
    observed=np.array([float(value/n) for value in observed_totals]);means={};references={};quantiles={}
    for suite in SUITES:
        a=np.asarray(arrays[suite])
        if a.shape!=(999,n,len(LABELS)):raise ValueError('Original999replicate/fullmouse denominator required')
        difference=original.effects(a)
        totals=[[original.exact_total(difference[r,:,j]) for j in range(6)] for r in range(999)]
        means[suite]=np.array([[float(value/n) for value in row] for row in totals])
        quantiles[suite]=[original.linear_q95([row[j] for row in totals]) for j in range(6)]
        references[suite]={'mean_effects':means[suite].mean(axis=0).tolist(),
            'q95_effects':[float(value/n) for value in quantiles[suite]],
            'observed_minus_reference_mean':(observed-means[suite].mean(axis=0)).tolist(),
            'reference_type':'Assumption-dependent stress comparison, not randomization-valid biological significance'}
    guards={}
    for j,name in enumerate(['D','C']):
        guards[name]={'conditional_Bstar_p':None,'conditional_Bstar_Holm2_p':None,
            'conditional_inclusive_exceedances':None,'conditional_Bstar_status':'FAILED_UNAVAILABLE',
            'above_temporal_q95':bool(observed_totals[3+j]>quantiles['temporal'][3+j]),
            'above_history_q95':bool(observed_totals[3+j]>quantiles['history'][3+j]),
            'numerical_reference_conditions_met':False,'interpretation':'Required conditional reference unavailable; no broad confirmation'}
    return {'replicates_per_suite':999,'seeds':SEEDS,'mouse_order':mouse_order,'observed_equal_mouse_effects':observed.tolist(),
        'stress_references':references,'beyond_baseline_null_guards':guards,'conditional_Bstar_status':'FAILED_UNAVAILABLE',
        'original_four_null_completion_gate':'FAIL_RETAINED_NOT_RECLASSIFIED',
        'decision_arithmetic':'Original exact dyadic totals/nominal95percent linear quantile; no changed operator or threshold',
        'task_order_stress_can_rescue_failed_claim':False,'D_minus_C_parametric_superiority_test_required':False},means
