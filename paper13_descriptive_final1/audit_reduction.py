"""Post-D saved-output audit; preserves the frozen original scientific scorer.

Joint-bin archives cannot recover unseen per-unit floats. Their reassociation
check is conditional compatibility, distinct from exact archival/statistic checks.
"""
import json
from fractions import Fraction
import numpy as np
from .common import P,ROOT
from .audit_saved import audit_C
from paper13_ki_execution1 import baseline_A as b
from paper13_ki_execution1.animal_stats import summarize

UROUND=Fraction(1,2**53)


def gamma(k):
    return k*UROUND/(1-k*UROUND)


def compare_score(sequence,original,model):
    sequence=np.asarray(sequence)
    if sequence.dtype!=np.float64 or sequence.shape!=(60,30) or not np.isfinite(sequence).all() or not np.isfinite(original):
        raise RuntimeError('Saved score shape/nonfinite mismatch')
    scored=sequence[:,5:]
    if np.any(scored>0):raise RuntimeError('Nonpositive joint log-score premise violated')
    grouped=float(scored.sum()/12000)
    residual=abs(Fraction.from_float(float(original))-Fraction.from_float(grouped))
    if model in ['D','S']:
        if grouped!=original:raise RuntimeError('Same-order D/S score must remain bitwise exact')
        return {'mode':'SAME_ORDER_EXACT','absolute_difference':0.0}
    B=sum((Fraction.from_float(float(v)) for v in scored.ravel()),Fraction(0))
    bound=abs(B)/12000*((gamma(12001)+gamma(8))/(1-gamma(8))+gamma(1501))
    if residual>bound:raise RuntimeError('Saved aggregate outside fixed forward-error compatibility bound')
    return {'mode':'CONDITIONAL_REASSOCIATION_COMPATIBILITY','absolute_difference':float(residual),
        'bound_exact_numerator':bound.numerator,'bound_exact_denominator':bound.denominator,
        'bound_display':float(bound),
        'premise':'Unseen computed unit log terms same-sign/nonpositive; not established from joint bins',
        'lossless_per_unit_reconstruction':False}


def check_copies(primary,final,state_identity,completed):
    if len(completed)!=1 or completed[0]['scores']!=final['scores'] or primary['result']!=final:
        raise RuntimeError('Original score copies/journal do not match exactly')
    if primary['state_identity']!=state_identity:raise RuntimeError('Original state identity copy differs')


def check_alias(arrays,scores):
    if not np.array_equal(arrays['Bstar'],arrays['B2']) or scores['Bstar']!=scores['B2']:
        raise RuntimeError('Original Bstar/B2 exact alias changed')


def audit_D():
    result=b.read(P/'results/FINAL_D_RESULTS.json')
    if result['FINAL_D_EXECUTION']!='VALIDLY_COMPLETED_ONCE_DESCRIPTIVE':raise RuntimeError('No complete descriptive D')
    mice=result['mouse_order'];scores={};compatibility={}
    if len(mice)!=9:raise RuntimeError('Original nine mice required')
    rows=[json.loads(line) for line in (P/'results/final_D/actions.jsonl').read_text(encoding='utf8').splitlines()]
    for mouse in mice:
        primary=b.read(P/'results/final_D/primary_mouse'/(mouse+'.json'))
        completed=[r for r in rows if r['event']=='D_MOUSE_PRIMARY_SENSITIVITY_COMPLETE' and r['mouse_id']==mouse]
        check_copies(primary,result['per_mouse'][mouse],result['state_identities'][mouse],completed)
        path=P/'results/final_D'/(mouse+'_bin_scores.npz')
        if b.sha(path.read_bytes())!=result['state_identities'][mouse]['bin_scores_sha256']:raise RuntimeError('Saved D bin-score hash mismatch')
        compatibility[mouse]={}
        with np.load(path,allow_pickle=False) as arrays:
            for name in ['B0','B1','B2','B3','B4','D','C','S','Bstar']:
                compatibility[mouse][name]=compare_score(arrays[name],result['per_mouse'][mouse]['scores'][name],name)
            check_alias(arrays,result['per_mouse'][mouse]['scores'])
        scores[mouse]={k:result['per_mouse'][mouse]['scores'][k] for k in ['B4','D','C','Bstar','S']}
    stats,_=summarize(scores,mice)
    for name,c in stats['contrasts'].items():
        for key,value in c.items():
            if key!='final_claim_status' and value!=result['statistics']['contrasts'][name][key]:raise RuntimeError('Saved statistic mismatch: '+name+'/'+key)
    if sum(r['event']=='FINAL_D_EXECUTION_START' for r in rows)!=1 or sum(r['event']=='FINAL_D_EXECUTION_COMPLETE' for r in rows)!=1:
        raise RuntimeError('One complete D assessment required')
    if any(r['event'] in ['D_CONTROL_ERROR','FINAL_D_EXECUTION_ERROR'] for r in rows):raise RuntimeError('Required D error retained; not valid full bundle')
    for suite,artifact in result['null_controls']['artifacts'].items():
        path=ROOT/artifact['path']
        if b.sha(path.read_bytes())!=artifact['sha256']:raise RuntimeError('D control artifact changed')
        a=np.load(path,allow_pickle=False,mmap_mode='r')
        if a.shape!=(999,9,9) or not np.isfinite(a).all():raise RuntimeError('Complete D three-suite reference shape/finite failure')
        if sum(r['event']=='D_MOUSE_CONTROL_COMPLETE' and r['suite']==suite for r in rows)!=8991:raise RuntimeError('D control attempt denominator mismatch')
    if set(result['null_controls']['artifacts'])!={'temporal','history','task_order'} or result['null_controls']['conditional_Bstar_status']!='FAILED_UNAVAILABLE':
        raise RuntimeError('Original conditional failure cannot be replaced')
    return {'FINAL_D_ASSESSMENT_EXECUTED':True,'FINAL_MICE_EVALUATED':9,'D_assessment_count':1,
        'D_mouse_control_replicates':26973,'conditional_Bstar':'FAILED_UNAVAILABLE','confirmatory_claims_withheld':True,
        'original_score_copies_journal_hashes_and_statistics_exact':True,'D_S_saved_bin_aggregates_exact':True,
        'other_models_saved_aggregate_compatibility':'CONDITIONAL_FORWARD_ERROR_BOUND; not lossless per-unit reconstruction',
        'compatibility':compatibility,'new_D_scores_or_control_draws_in_audit':0}
