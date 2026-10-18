"""Frozen Final mouse-level inference and explicit per-contrast claim conjunctions."""
import numpy as np
from .statistics import CONTRASTS,PRIMARY,SECONDARY,summarize,holm

MANDATORY_CASES=['S01','S04','S05','S06','S07','S08','S09','S10','S11']


def analyze_final(mouse_rows,specification):
    subjects=[r['subject'] for r in mouse_rows];expected=specification['primary_subjects']
    assert len(subjects)==len(set(subjects))==len(expected) and set(subjects)==set(expected)
    by={r['subject']:r for r in mouse_rows}
    for row in mouse_rows:
        assert {'B0','B1','B2','B3','B4'}<=set(row['models'])
        assert set(row['models'])=={f for f,cohort in specification['family_subjects'].items() if row['subject'] in cohort}
        assert all(m['unit_bins']>0 and np.isfinite(m['LL']) for m in row['models'].values())
    results={}
    for contrast,(left,right) in CONTRASTS.items():
        cohort=specification['contrast_subjects'][contrast]
        assert cohort==[s for s in expected if s in specification['family_subjects'][left] and s in specification['family_subjects'][right]]
        effects=[];rows=[]
        for subject in cohort:
            row=by[subject];a,b=row['models'][left],row['models'][right];assert a['unit_bins']==b['unit_bins']
            value=(a['LL']-b['LL'])/a['unit_bins'];effects.append(value)
            rows.append(dict(subject=subject,lab=row['lab'],effect=value,left_LL=a['LL'],right_LL=b['LL'],unit_bins=a['unit_bins']))
        if len(cohort)<6:
            panel=dict(contrast=contrast,status='UNAVAILABLE_PRE_D_C_VALID_COHORT_LT6',n_mice=len(cohort),
                paired_sign_flip_p=1.,mouse_effects=rows,mean_descriptive_unavailable_inference=float(np.mean(effects)) if effects else None,
                CI95=None,validated=False,heldout_animal_confirmation=False)
        else:
            panel=summarize(effects,[by[s]['lab'] for s in cohort],contrast)
            panel.update(status='REGISTERED_FINAL_DESCRIPTIVE_COMPARISON',mouse_effects=rows,
                exploratory=False,heldout_animal_assessment=True,heldout_animal_confirmation=False,validated=False,
                prespecified_cohort_from_C=True,conditional_assumption_test=True)
        results[contrast]=panel
    adjusted=holm([results[k]['paired_sign_flip_p'] for k in SECONDARY])
    for key,p in zip(SECONDARY,adjusted):results[key]['Holm5_adjusted_p']=float(p)
    return results


def claim_verdicts(statistics,sensitivities,controls,specification):
    out={}
    for contrast,result in statistics.items():
        n=result['n_mice'];rows=result['mouse_effects'];labs={r['lab'] for r in rows}
        lab_counts={lab:sum(r['lab']==lab for r in rows) for lab in labs}
        available=n>=6 and result.get('CI95') is not None
        primary=contrast==PRIMARY
        tests=dict(
            cohort_at_least8=n>=8,at_least4labs=len(labs)>=4,
            no_lab_over50percent=max(lab_counts.values(),default=0)<=n/2,
            source_and_main_numerical_valid=specification['source_main_numerical_valid'],
            independence_and_symmetry_defensible=specification['confirmatory_assumptions_defensible'],
            mean_at_least0p001=available and result['equal_mouse_mean']>=.001,
            positive_CI_lower=available and result['CI95'][0]>0,
            CI_width_at_most0p01=available and result['CI_width']<=.01,
            registered_p_at_most0p05=available and result['paired_sign_flip_p' if primary else 'Holm5_adjusted_p']<=.05,
            at_least75percent_positive=available and result['positive_mice']>=int(np.ceil(.75*n)),
            all_leave_one_mouse_means_positive=available and all(v>0 for v in result['leave_one_mouse_out_means']),
            all_leave_one_lab_means_positive=available and bool(result['leave_one_lab_out_means']) and all(v>0 for v in result['leave_one_lab_out_means'].values()))
        case_details={}
        if contrast in ('B4-B1','B4-B3','B4-B2'):
            for case in MANDATORY_CASES:
                panel=sensitivities[case][contrast]
                case_details[case]=dict(n_mice=panel['n_mice'],minimum6=panel['minimum6_coverage'],
                    positive_mean=panel.get('equal_mouse_mean',-np.inf)>0)
                tests['mandatory_'+case]=panel['minimum6_coverage'] and panel.get('equal_mouse_mean',-np.inf)>0
        else:
            tests['no_unregistered_sensitivity_credit']=True
        required_suites=['N1','N2']+(['N4'] if contrast in ('D-B4','D-S') else [])
        for suite in required_suites:
            panel=controls[contrast][suite]
            tests['reference_'+suite]=(panel.get('n_mice',0)>=6 and panel.get('descriptive_disruption_gate',False))
        if contrast=='D-S':tests['prescribed_static_capacity_pair_valid']=specification['static_capacity_pair_valid']
        supported=all(bool(v) for v in tests.values())
        if not available:verdict='INCONCLUSIVE REQUIRED GATE'
        elif n<8:verdict='DESCRIPTIVE ONLY'
        elif not tests['independence_and_symmetry_defensible']:verdict='INCONCLUSIVE REQUIRED GATE'
        elif supported:verdict='SUPPORTED UNDER REGISTERED PREDICTIVE CRITERIA'
        else:verdict='NOT SUPPORTED / MIXED'
        # Actual prospective six-mouse fallback cannot be promoted by favorable D values.
        if specification['mandatory_descriptive_only'] and available:
            assert n<8;verdict='DESCRIPTIVE ONLY';supported=False
        out[contrast]=dict(verdict=verdict,supported_under_complete_registered_conjunction=supported,
            criteria={k:bool(v) for k,v in tests.items()},failed_criteria=[k for k,v in tests.items() if not v],
            mandatory_case_details=case_details,required_reference_suites=required_suites,
            completed_predictive_assessment=available,causal_mechanism=False,all_movement_independence=False,
            biological_discrete_states=False,independent_lab_replication=False,NAP_CWP_validation=False)
    return out
