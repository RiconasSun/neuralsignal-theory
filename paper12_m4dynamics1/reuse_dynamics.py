"""Reuse completed A-only first-mouse fits; score B only in gated competition."""
import hashlib
import json
from pathlib import Path
import numpy as np

_bundle=None

class ReuseIntegrityError(RuntimeError):pass

def fit_or_reuse(math,session,region,family,size,raw_y,model,validation,ridge,seed):
    if session['session_id']!='766640955':return math.fit(model,validation,ridge,seed)
    try:theta,metrics=_reuse(math,session,region,family,size,raw_y,model,validation,ridge,seed)
    except ReuseIntegrityError:raise
    except Exception as exc:raise ReuseIntegrityError('REUSE_ARTIFACT_DECODE_OR_COMPUTATION_FAILURE') from exc
    training=model.score(theta)/model.y.size;valid=validation.score(theta)/validation.y.size
    metrics.update(converged=bool(metrics['converged'] and np.isfinite(training) and np.isfinite(valid)),
        training_LL_nats_per_unit_bin=float(training),validation_LL_nats_per_unit_bin=float(valid))
    return theta,metrics

def _reuse(math,session,region,family,size,raw_y,model,validation,ridge,seed):
    global _bundle
    root=Path(__file__).parent
    if _bundle is None:
        bundle=json.loads((root/'reuse_bundle.json').read_text())
        if set(bundle['sha256'])!={'reuse_states.npz','reuse_summary.json','reuse_gate.json'}:raise ReuseIntegrityError('EXACT_REUSE_HASH_SET_REQUIRED')
        for name,digest in bundle['sha256'].items():
            if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ReuseIntegrityError('REUSED_FIT_ARTIFACT_CHANGED')
        bindings=bundle['completed_smoke_bindings']
        if set(bindings)!={'gate','receipt','proof','oracles','summary'} or bundle['sha256']['reuse_summary.json']!=bindings['summary'] or bundle['sha256']['reuse_gate.json']!=bindings['gate']:raise ReuseIntegrityError('COMPLETED_SMOKE_BINDINGS_REQUIRED')
        gate=json.loads((root/'reuse_gate.json').read_text())
        if gate['gate']!='PASS' or gate['completed_fit_count']!=216 or gate['fitted_states_sha256']!=bundle['sha256']['reuse_states.npz']:raise ReuseIntegrityError('EXACT_COMPLETED_SMOKE_GATE_REQUIRED')
        summary=json.loads((root/'reuse_summary.json').read_text())
        if summary.get('validation_access') is not False or summary.get('final_access') is not False or any(z.get('validation_access') is not False or z.get('final_access') is not False for z in summary['rows']):raise ReuseIntegrityError('EXPLICIT_A_ONLY_REUSE_REQUIRED')
        from roster import validate
        try:validate([{k:v for k,v in z.items() if k!='validation_access'} for z in summary['rows']])
        except RuntimeError as exc:raise ReuseIntegrityError('REUSE_ROSTER_INVALID') from exc
        with np.load(root/'reuse_states.npz',allow_pickle=False) as z:states={k:z[k] for k in z.files}
        expected={f"{z['region']}_{z['family']}_{z['size']}_{z['ridge']}_{z['seed']}" for z in summary['rows']}
        if len(states)!=216 or set(states)!=expected:raise ReuseIntegrityError('EXACT_REUSE_STATE_ROSTER_REQUIRED')
        _bundle=(summary,states)
    summary,states=_bundle
    identity=(region,family,size,ridge,seed)
    old=next(z for z in summary['rows'] if (z['region'],z['family'],z['size'],z['ridge'],z['seed'])==identity)
    condition=next(z for z in summary['conditioning'] if z['region']==region)
    if hashlib.sha256(np.ascontiguousarray(raw_y).tobytes()).hexdigest()!=condition['training_array_sha256']:raise ReuseIntegrityError('REUSED_TRAINING_COUNTS_CHANGED')
    theta=states[f'{region}_{family}_{size}_{ridge}_{seed}']
    loss,g=math.objective(theta,model,ridge);pg=math.projected_gradient(theta,g)
    if loss!=old['penalized_training_objective'] or pg!=old['projected_gradient'] or len(theta)!=model.n_parameters:raise ReuseIntegrityError('REUSED_FIT_DEFINITION_CHANGED')
    keys=('optimizer_success','optimizer_message','iterations','objective_calls','projected_gradient','penalized_training_objective','bound_hits','elapsed_seconds')
    metrics={k:old[k] for k in keys}
    metrics.update(converged=bool(old['converged']),model_specific_parameters=model.n_parameters,
        training_unit_bins=int(model.y.size),validation_unit_bins=int(validation.y.size),ridge_normalization='per_unit_exposure',reused_training_fit=True)
    return theta,metrics
