import hashlib
import numpy as np
from independent_ad import layout,constants,value_gradient,vector_losses

SCALES=(1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8)
def scaled_error(a,b):return np.abs(a-b)/np.maximum(1.,np.maximum(np.abs(a),np.abs(b)))
def formulas(fm2,fm,fmh,fph,fp,fp2,h):
    central=(fp-fm)/(2*h);half=(fph-fmh)/h
    fourth=(fm2-8*fm+8*fp-fp2)/(12*h)
    richardson=(4*half-central)/3
    return central,fourth,richardson

def inspect_vector(theta,model,ridge,stage,scales=SCALES,batch=16,progress=None):
    from model_math import objective,projected_gradient
    value,gradient=objective(theta,model,ridge)
    independent,ad,parts=value_gradient(theta,model.y,model.x,model.offset,model.dimension,ridge)
    scalar=vector_losses(theta[None],model.y,model.x,model.offset,model.dimension,ridge)[0]
    shape=layout(model.y.shape[-1],model.x.shape[-1],model.dimension)
    blocks={i:name for name,start,end,_ in shape for i in range(start,end)}
    digest=hashlib.sha256(np.ascontiguousarray(theta,dtype=np.float64).tobytes()).hexdigest()
    base=dict(stage=stage,theta_sha256=digest,objective=float(value),independent_AD_objective=independent,independent_forward_objective=float(scalar),objective_abs_error=max(abs(value-independent),abs(value-scalar)),AD_gradient_scaled_error_max=float(scaled_error(gradient,ad).max()),AD_gradient_abs_error_max=float(np.abs(gradient-ad).max()),PG=projected_gradient(theta,gradient),AD_PG=projected_gradient(theta,ad),bound_hits=int((np.abs(theta)>=8).sum()),float64_mantissa_bits=int(np.finfo(np.float64).nmant),longdouble_mantissa_bits=int(np.finfo(np.longdouble).nmant),normalization_exposure=int(len(model.y)*model.y.shape[1]),ridge_gradient_max_error=float(np.abs(parts['ridge_gradient']-ridge*theta).max()),parameter_blocks={name:[start,end] for name,start,end,_ in shape})
    rows=[];factorial=constants(model.y)
    for scale in scales:
        for start in range(0,len(theta),batch):
            coordinates=np.arange(start,min(start+batch,len(theta)));h=scale*np.maximum(1.,np.abs(theta[coordinates]));vectors=[]
            for i,step in zip(coordinates,h):
                for multiple in (-2.,-1.,-.5,.5,1.,2.):
                    vector=theta.copy();vector[i]+=multiple*step;vectors.append(vector)
            values=vector_losses(np.asarray(vectors),model.y,model.x,model.offset,model.dimension,ridge,factorial).reshape(-1,6)
            for i,step,v in zip(coordinates,h,values):
                central,fourth,richardson=formulas(*v,step);finite=bool(np.isfinite(v).all())
                rounding=float(np.finfo(float).eps*(abs(v[1])+abs(v[4]))/(2*step))
                row=dict(stage=stage,theta_sha256=digest,coordinate=int(i),block=blocks[int(i)],theta=float(theta[i]),scale=scale,h=float(step),analytical=float(gradient[i]),AD=float(ad[i]),AD_abs_error=float(abs(gradient[i]-ad[i])),AD_scaled_error=float(scaled_error(gradient[i],ad[i])),likelihood_AD=float(parts['normalized_likelihood_gradient'][i]),ridge_AD=float(parts['ridge_gradient'][i]),central=float(central),fourth_order=float(fourth),richardson=float(richardson),central_abs_error=float(abs(central-ad[i])),central_scaled_error=float(scaled_error(central,ad[i])),fourth_abs_error=float(abs(fourth-ad[i])),fourth_scaled_error=float(scaled_error(fourth,ad[i])),richardson_abs_error=float(abs(richardson-ad[i])),richardson_scaled_error=float(scaled_error(richardson,ad[i])),roundoff_indicator=rounding,extrapolation_change=float(abs(richardson-central)),symmetric_probe_crosses_bound=bool(theta[i]-2*step < -8 or theta[i]+2*step > 8),finite=finite,extrapolation_stable=bool(finite and rounding<=1e-5 and abs(richardson-central)<=1e-5*max(1.,abs(richardson))))
                row.update({name:float(value) for name,value in zip(('f_minus2','f_minus1','f_minus_half','f_plus_half','f_plus1','f_plus2'),v)})
                rows.append(row)
        if progress is not None:progress(stage,scale,len(rows))
    base['scan']={}
    for scale in scales:
        group=[row for row in rows if row['scale']==scale]
        base['scan'][str(scale)]={method:float(max(row[method+'_scaled_error'] for row in group)) for method in ('central','fourth','richardson')}
        base['scan'][str(scale)].update(coordinate_count=len(group),finite_count=sum(row['finite'] for row in group),stable_count=sum(row['extrapolation_stable'] for row in group))
    base['FD_forward_evaluations']=len(rows)*6
    return base,rows

def decide(stages,original_check,optimizer,synthetic_pass):
    valid=synthetic_pass and all(s['objective_abs_error']<=1e-10 and s['AD_gradient_scaled_error_max']<=1e-5 for s in stages)
    objective_valid=synthetic_pass and all(s['objective_abs_error']<=1e-10 for s in stages)
    analytic_defect=objective_valid and any(s['AD_gradient_scaled_error_max']>1e-5 for s in stages)
    endpoint=stages[-1]
    small=[endpoint['scan'][str(scale)]['central'] for scale in SCALES[-3:]]
    frozen_FD_error=endpoint['scan'][str(1e-5)]['central']
    stable_scales=[]
    for scale in SCALES[-3:]:
        check=endpoint['scan'][str(scale)]
        stable_scales.append(all(check[method]<=1e-5 for method in ('central','fourth','richardson')) and check['central']<frozen_FD_error and check['finite_count']==check['stable_count']==check['coordinate_count'])
    stable_pair=any(stable_scales[i] and stable_scales[i+1] for i in range(2))
    fd_instability=objective_valid and original_check['scaled_gradient_error']>1e-5 and frozen_FD_error>1e-5 and stable_pair
    original_fit_nonconvergent=not optimizer['optimizer_success'] or optimizer['projected_gradient']>.001
    nonconvergent=original_fit_nonconvergent if valid else None
    if analytic_defect and fd_instability:verdict='BOTH_DEFECTS'
    elif analytic_defect:verdict='ANALYTICAL_GRADIENT_DEFECT'
    elif valid and fd_instability:verdict='FINITE_DIFFERENCE_INSTABILITY'
    elif valid and original_check['passed'] and nonconvergent:verdict='GRADIENT_VALID_BUT_OPTIMIZER_NONCONVERGENT'
    else:verdict='INCONCLUSIVE'
    return dict(verdict=verdict,analytical_gradient_validated=valid,analytical_gradient_defect=analytic_defect,finite_difference_instability=fd_instability,predefined_small_scale_errors=small,higher_order_stable_scales=stable_scales,original_fit_nonconvergent=original_fit_nonconvergent,optimizer_nonconvergent_with_validated_gradient=nonconvergent,optimizer_correct_gradient_assessment='NONCONVERGENT_AT_AUDITED_VECTORS' if nonconvergent else ('CONVERGED' if valid else 'INCONCLUSIVE'),original_gradient_gate_passed=original_check['passed'],original_PG_gate_passed=optimizer['projected_gradient']<=.001,original_scientific_failure_unchanged=True)
