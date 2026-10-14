"""Independent saved-CSV aggregation and decision reconstruction; stdlib only."""
import math
import hashlib
import array

def reconstruct(rows,stages,decision):
    scales=(1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8)
    bystage={}
    for name in ('initial','intermediate','endpoint'):
        selected=[r for r in rows if r['stage']==name]
        meta=next(s for s in stages if s['stage']==name)
        if {r['theta_sha256'] for r in selected}!={meta['theta_sha256']}:raise RuntimeError('STAGE_VECTOR_HASH')
        for i in range(384):
            values=[r for r in selected if int(r['coordinate'])==i]
            if len(values)!=7 or any(len({r[k] for r in values})!=1 for k in ('theta','analytical','AD','block','likelihood_AD','ridge_AD')):raise RuntimeError('SAME_VECTOR_COORDINATE_REQUIRED')
        first={int(r['coordinate']):float(r['theta']) for r in selected}
        vector=array.array('d',[first[i] for i in range(384)])
        if hashlib.sha256(vector.tobytes()).hexdigest()!=meta['theta_sha256']:raise RuntimeError('PUBLIC_COORDINATE_VECTOR_DIGEST')
        rebuilt={}
        for scale in scales:
            group=[r for r in selected if float(r['scale'])==scale]
            if len(group)!=384:raise RuntimeError('SCALE_COORDINATE_COUNT')
            rebuilt[str(scale)]={method:max(float(r[method+'_scaled_error']) for r in group) for method in ('central','fourth','richardson')}
            finite=sum(r['finite']=='True' for r in group)
            stable=0
            for r in group:
                expected=r['finite']=='True' and float(r['roundoff_indicator'])<=1e-5 and abs(float(r['richardson'])-float(r['central']))<=1e-5*max(1.,abs(float(r['richardson'])))
                if expected!=(r['extrapolation_stable']=='True'):raise RuntimeError('EXTRAPOLATION_STABILITY_CHANGED')
                stable+=expected
            rebuilt[str(scale)].update(coordinate_count=384,finite_count=finite,stable_count=stable)
            for k,v in rebuilt[str(scale)].items():
                if not math.isclose(v,meta['scan'][str(scale)][k],rel_tol=1e-12,abs_tol=1e-12):raise RuntimeError('STAGE_SCAN_MAX_CHANGED')
        admax=max(float(r['AD_scaled_error']) for r in selected)
        if not math.isclose(admax,meta['AD_gradient_scaled_error_max'],rel_tol=1e-12,abs_tol=1e-12):raise RuntimeError('AD_MAX_CHANGED')
        bystage[name]=rebuilt
    valid=all(s['objective_abs_error']<=1e-10 and s['AD_gradient_scaled_error_max']<=1e-5 for s in stages)
    objective_valid=all(s['objective_abs_error']<=1e-10 for s in stages)
    defect=objective_valid and any(s['AD_gradient_scaled_error_max']>1e-5 for s in stages)
    scan=bystage['endpoint'];frozen=scan[str(1e-5)]['central'];stable=[]
    for scale in scales[-3:]:
        s=scan[str(scale)];stable.append(all(s[k]<=1e-5 for k in ('central','fourth','richardson')) and s['central']<frozen and s['finite_count']==s['stable_count']==s['coordinate_count'])
    instability=objective_valid and not decision['original_gradient_gate_passed'] and frozen>1e-5 and any(stable[i] and stable[i+1] for i in range(2))
    if defect and instability:verdict='BOTH_DEFECTS'
    elif defect:verdict='ANALYTICAL_GRADIENT_DEFECT'
    elif valid and instability:verdict='FINITE_DIFFERENCE_INSTABILITY'
    elif valid and decision['original_gradient_gate_passed'] and decision['original_fit_nonconvergent']:verdict='GRADIENT_VALID_BUT_OPTIMIZER_NONCONVERGENT'
    else:verdict='INCONCLUSIVE'
    if verdict!=decision['verdict'] or valid!=decision['analytical_gradient_validated'] or stable!=decision['higher_order_stable_scales']:raise RuntimeError('D4_RECONSTRUCTION_CHANGED')
    return verdict
