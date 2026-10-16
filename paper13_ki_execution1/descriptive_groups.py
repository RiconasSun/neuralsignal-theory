"""Predeclared descriptive group/leave-group-out summaries, no new tests."""
import numpy as np
from .control_core import LABELS,effects


def summarize(scores,descriptors,mice):
    if set(scores)!=set(mice) or set(descriptors)!=set(mice):raise ValueError('Original paired mouse descriptor/score roster required')
    matrix=effects(np.array([[scores[mouse][name] for name in LABELS] for mouse in mice]))
    catalog={'condition':{},'genotype':{},'raw_provider_DV_median':{},'individual_probe':{},'laboratory':{}}
    for mouse in mice:
        d=descriptors[mouse];conditions=d['documented_conditions']
        catalog['condition'][mouse]=' | '.join(conditions) if conditions else 'NOT_DOCUMENTED_IN_SAVED_TABLE'
        catalog['genotype'][mouse]=str(d['genotype'])
        dv=d['provider_coordinates'].get('DV')
        catalog['raw_provider_DV_median'][mouse]=repr(float(np.median(dv))) if dv is not None and np.isfinite(np.asarray(dv,dtype=float)).all() else 'NOT_AVAILABLE'
        catalog['individual_probe'][mouse]=mouse+'|'+str(d['probe_id'])
        catalog['laboratory'][mouse]='SOURCE_STUDY_SINGLE_LABORATORY'
    result={}
    for variable,assignments in catalog.items():
        rows={}
        for value in sorted(set(assignments.values())):
            inside=[j for j,m in enumerate(mice) if assignments[m]==value];outside=[j for j,m in enumerate(mice) if assignments[m]!=value]
            rows[value]={'mice':[mice[j] for j in inside],'n':len(inside),'equal_mouse_effect_means':matrix[inside].mean(axis=0).tolist(),
                'leave_group_out_mice':[mice[j] for j in outside],
                'leave_group_out_means':matrix[outside].mean(axis=0).tolist() if outside else None,
                'leave_group_out_status':'COMPUTED_DESCRIPTIVE' if outside else 'UNAVAILABLE_EMPTY_REMAINDER',
                'documented_measured_value':not any(s in value for s in ['NOT_DECODED','NOT_DOCUMENTED','NOT_AVAILABLE'])}
        result[variable]={'assignments':assignments,'groups':rows,'new_hypothesis_test':False,
            'physical_units_verified':False if variable=='raw_provider_DV_median' else None,
            'interpretation':'Raw coordinate exact-value grouping, not verified tissue depth' if variable=='raw_provider_DV_median' else 'Descriptive dependence only; no independent replication or missing-covariate adjustment claim'}
    return {'groups':result,'individual_probe_leaveout_equals_mouse_leaveout':True,'laboratories':1,
        'genotype_value_missingness_means_not_decoded_not_provider_absence':True,'optional_group_results_can_rescue':False}
