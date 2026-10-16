"""Saved-only scientific accounting; no fit, raw decoder or D likelihood rerun."""
import json
import numpy as np
from .common import P,OLD,ROOT,identities
from paper13_ki_execution1 import baseline_A as b
from paper13_ki_execution1.animal_stats import summarize


def audit_C():
    identities()
    gate=b.read(P/'results/FINAL_C_GATE.json')
    folder=P/'results/final_C';fits=[]
    for path in sorted((folder/'fits').glob('*/*.json')):
        r=b.read(path)
        if 'full_request_sha256' in r:fits.append((path,r))
    counts={status:sum(r['status']==status for _,r in fits) for status in sorted({r['status'] for _,r in fits})}
    if len({r['full_request_sha256'] for _,r in fits})!=len(fits):raise RuntimeError('Duplicate actual C request')
    rows=[json.loads(line) for line in (folder/'actions.jsonl').read_text(encoding='utf8').splitlines()]
    if sum(r['event']=='FINAL_C_START' for r in rows)!=1:raise RuntimeError('Repeated C execution')
    return {'FINAL_C_PASS':gate['FINAL_C_NUMERICS']=='PASS','FINAL_C_FITS_ATTEMPTED':len(fits),
        'C_fit_status_counts':counts,'C_fits_completed':sum(r['status']=='PASS' for _,r in fits),
        'C_fit_starts':sum(r['event']=='C_FIT_START' for r in rows),'C_fit_completions':sum(r['event']=='C_FIT_COMPLETE' for r in rows),
        'C_error':gate if gate['FINAL_C_NUMERICS']!='PASS' else None,
        'C_request_sha256s':[r['full_request_sha256'] for _,r in fits],'new_fits_in_audit':0}


def audit_D():
    result=b.read(P/'results/FINAL_D_RESULTS.json')
    if result['FINAL_D_EXECUTION']!='VALIDLY_COMPLETED_ONCE_DESCRIPTIVE':raise RuntimeError('No complete descriptive D')
    mice=result['mouse_order'];scores={}
    if len(mice)!=9:raise RuntimeError('Original nine mice required')
    for mouse in mice:
        path=P/'results/final_D'/(mouse+'_bin_scores.npz')
        if b.sha(path.read_bytes())!=result['state_identities'][mouse]['bin_scores_sha256']:raise RuntimeError('Saved D bin-score hash mismatch')
        with np.load(path,allow_pickle=False) as arrays:
            for name in ['B0','B1','B2','B3','B4','D','C','S','Bstar']:
                if arrays[name].shape!=(60,30) or not np.isfinite(arrays[name]).all():raise RuntimeError('Saved D log-score shape/finite mismatch')
                mean=float(arrays[name][:,5:].sum()/12000)
                if mean!=result['per_mouse'][mouse]['scores'][name]:raise RuntimeError('Saved D mean differs from original serialized log scores')
        scores[mouse]={k:result['per_mouse'][mouse]['scores'][k] for k in ['B4','D','C','Bstar','S']}
    stats,_=summarize(scores,mice)
    for name,c in stats['contrasts'].items():
        for key,value in c.items():
            if key!='final_claim_status' and value!=result['statistics']['contrasts'][name][key]:raise RuntimeError('Saved statistic mismatch: '+name+'/'+key)
    rows=[json.loads(line) for line in (P/'results/final_D/actions.jsonl').read_text(encoding='utf8').splitlines()]
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
        'saved_bin_score_and_statistics_match':True,'new_D_scores_or_control_draws_in_audit':0}


if __name__=='__main__':print(json.dumps(audit_C(),sort_keys=True))
