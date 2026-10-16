"""Pre-D mathematical state completeness checks, no fitting or neural IO."""
import numpy as np
from . import models as m
from .sensitivity_plan import unit_panels

PARAMETERS={'B0':8,'B1':96,'B2':32,'B3':176,'B4':288}


def vector(value,n,label,bounded=False):
    a=np.asarray(value,dtype=float)
    if a.shape!=(n,) or not np.isfinite(a).all() or (bounded and np.any((a< -8)|(a>8))):raise ValueError('Incomplete/nonfinite/out-of-bounds '+label)
    return a


def validate(bundle):
    if bundle['training_partition']!='C':raise PermissionError('Final scoring requires calibrated C states')
    units=bundle['units'];ids=[u['unit_id'] for u in units]
    if len(ids)!=8 or len(set(ids))!=8 or ids!=sorted(ids):raise ValueError('Original8ordered C units required')
    for unit in units:
        qc=bundle['unit_QC'][str(unit['unit_id'])]
        if qc['partition']!='C' or not qc['pass'] or not np.isfinite([qc['rate_hz'],qc['refractory_fraction']]).all():raise ValueError('Original C-only selected-unit QC required')
    if set(bundle['source_fit_requests'])!={'B0','B1','B2','B3','B4','D','C','S'} or len(bundle['all_C_fit_requests'])!=22:
        raise ValueError('All selected/original22Cfit identities required')
    if bundle['Bstar'] not in PARAMETERS:raise ValueError('Frozen strongest baseline identity required')
    for name,n in PARAMETERS.items():
        vector(bundle['baseline_thetas'][name],n,name+' coefficients',True);state=bundle['baseline_scalers'][name];K=n//8
        mean=np.asarray(state['mean'],dtype=float);sd=np.asarray(state['sd'],dtype=float)
        if mean.shape!=(8,K) or sd.shape!=(8,K) or not np.isfinite(mean).all() or not np.isfinite(sd).all() or np.any(sd<0):raise ValueError('Incomplete '+name+' C scaler')
        if np.any(mean[:,0]!=0) or np.any(sd[:,0]!=1):raise ValueError('Original unstandardized intercept convention required')
        _,sources=m.raw_features(np.zeros((1,6,8)),np.zeros((1,6,11)),name)
        if not np.array_equal(state['source_units'],sources):raise ValueError('Original neural-source coordinate ordering required')
        if 'zero_sd' in state and not np.array_equal(state['zero_sd'],sd==0):raise ValueError('Zero-variance scaler metadata mismatch')
    for name in ['D','S']:
        vector(bundle[name]['theta'],16,name+' emission coefficients',True)
        if bundle[name]['p'] not in [.5,.9,.98] or (name=='S' and bundle[name]['p']!=.5):raise ValueError('Frozen transition/static convention required')
    configuration=bundle['C'];vector(configuration['theta'],16,'C readout',True)
    if tuple(configuration['tau']) not in [(.1,.3),(.3,1.),(.1,1.)] or configuration['seed'] not in [11,23,37]:raise ValueError('Original fixed leaky timescale/seed policy required')
    state=configuration['state'];Q=np.asarray(state['Q'],dtype=float)
    if Q.shape!=(8,2) or not np.isfinite(Q).all() or not np.allclose(Q,m.projection(configuration['seed']),rtol=0,atol=1e-14):raise ValueError('Frozen original8unit QR projection required; no renormalization')
    for key,n in [('count_mean',8),('count_sd',8),('h_mean',2),('h_sd',2)]:
        a=vector(state[key],n,'C '+key)
        if key.endswith('_sd') and np.any(a<0):raise ValueError('Nonnegative frozen C scaling required')
    if bundle['sensitivity_unit_masks']!=unit_panels(bundle):raise ValueError('Original C-only sensitivity unit masks required')
    return {'complete':True,'baseline_parameter_counts':PARAMETERS,'dynamic_added_parameters':16,'original_units':8}
