"""Local gradient-difference Hessian, block scales and recurrence saturation."""
import hashlib
import numpy as np
from independent_ad import layout

def digest(theta):return hashlib.sha256(np.ascontiguousarray(theta,dtype=np.float64).tobytes()).hexdigest()
def blocks(theta,gradient,units,context,dimension,diagonal=None):
    result={}
    for name,i,j,shape in layout(units,context,dimension):
        g=gradient[i:j];t=theta[i:j];pg=g.copy();pg[(t<=-8)&(g>0)]=0;pg[(t>=8)&(g<0)]=0
        row={'coordinates':j-i,'gradient_inf':float(np.abs(g).max()),'gradient_l2':float(np.linalg.norm(g)),'gradient_rms':float(np.sqrt(np.mean(g*g))),'physical_PG':float(np.abs(pg).max()),'PG_coordinate':int(i+np.abs(pg).argmax())}
        if diagonal is not None:row['curvature_diagonal_abs']={'min':float(np.abs(diagonal[i:j]).min()),'max':float(np.abs(diagonal[i:j]).max()),'median':float(np.median(np.abs(diagonal[i:j])))}
        result[name]=row
    return result
def hessian(theta,fun,scale):
    result=np.empty((len(theta),len(theta)));cross=0
    for i in range(len(theta)):
        h=scale*max(1.,abs(theta[i]));plus=theta.copy();minus=theta.copy();plus[i]+=h;minus[i]-=h
        cross+=bool(plus[i]>8 or minus[i]<-8)
        result[:,i]=(fun(plus)[1]-fun(minus)[1])/(2*h)
    if not np.isfinite(result).all():raise FloatingPointError('NONFINITE_LOCAL_HESSIAN')
    return result,cross
def spectrum(matrix):
    symmetric=(matrix+matrix.T)/2;values=np.linalg.eigvalsh(symmetric);cut=max(1.,float(np.abs(values).max()))*1e-8
    absolute=np.abs(values);resolved=absolute[absolute>cut]
    return {'eigenvalues':values.tolist(),'minimum':float(values.min()),'maximum':float(values.max()),'negative_count':int((values < -cut).sum()),'near_zero_count':int((absolute<=cut).sum()),'resolution_cutoff':cut,'resolved_abs_condition_estimate':float(resolved.max()/resolved.min()) if len(resolved) else None,'asymmetry_inf_relative':float(np.linalg.norm(matrix-matrix.T,np.inf)/max(1.,np.linalg.norm(matrix,np.inf))),'finite_precision_local_estimate':True}
def scale_from_diagonal(diagonal):return np.clip(1/np.sqrt(np.maximum(np.abs(diagonal),1e-6)),1e-4,1e4)
def saturation(theta,y,x,dimension):
    parts=[theta[i:j].reshape(shape) for _,i,j,shape in layout(y.shape[-1],x.shape[-1],dimension)];a,b,d,c=parts;h=np.zeros((len(y),dimension));all_h=[]
    for t in range(y.shape[1]):
        past=np.zeros((len(y),y.shape[-1])) if t==0 else np.log1p(y[:,t-1])
        h=np.tanh(h@a.T+past@b.T+x[:,t]@d.T);all_h.append(h.copy())
    states=np.asarray(all_h);derivative=1-states*states
    return {'hidden_values':int(states.size),'abs_hidden_max':float(np.abs(states).max()),'fraction_abs_gt_0.95':float(np.mean(np.abs(states)>.95)),'fraction_abs_gt_0.99':float(np.mean(np.abs(states)>.99)),'tanh_derivative_min':float(derivative.min()),'tanh_derivative_mean':float(derivative.mean()),'finite':bool(np.isfinite(states).all())}
