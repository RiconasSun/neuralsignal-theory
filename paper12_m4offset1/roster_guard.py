import hashlib
import numpy as np

OPTIONS=dict(ftol=1e-10,gtol=1e-5,maxiter=2000,maxfun=80000)


def validate_roster(rows,meta,states,sessions):
    animals={s['session_id']:s['mouse_id'] for s in sessions}
    expected={(s,roi,seed) for s in animals for roi in ('CA1','DG') for seed in (11,23,37)}
    actual={(r['session_id'],r['region'],r['seed']) for r in rows}
    if actual!=expected or len(rows)!=len(expected):raise RuntimeError('EXACT_OFFSET_ROSTER_REQUIRED')
    cases={s+'_'+roi for s in animals for roi in ('CA1','DG')}
    keys={s+'_'+roi+'_'+str(seed) for s,roi,seed in expected}
    if set(meta)!=cases or set(states)!=keys:raise RuntimeError('EXACT_CASE_AND_STATE_KEYS_REQUIRED')
    for row in rows:
        case=row['session_id']+'_'+row['region'];m=meta[case];weight=states[case+'_'+str(row['seed'])]
        if row['mouse_id']!=animals[row['session_id']] or m['mouse_id']!=row['mouse_id'] or row['ridge']!=.1 or row.get('training_only') is not True or row['optimizer_policy']!=OPTIONS:
            raise RuntimeError('FROZEN_OFFSET_DEFINITION_REQUIRED')
        if row['training_array_sha256']!=m['training_array_sha256'] or weight.shape!=(m['unit_count'],29) or not np.all(np.isfinite(weight)) or np.any(np.abs(weight)>8):
            raise RuntimeError('TRAINING_STATE_BINDING_OR_BOUNDS_FAILED')
        if not row['converged'] or not row['optimizer_success'] or not np.isfinite(row['projected_gradient']) or row['projected_gradient']>.001:
            raise RuntimeError('ALL_SEEDS_OFFSET_CONVERGENCE_REQUIRED')
        for name in ('initial_gradient_check','terminal_gradient_check'):
            check=row[name]
            if not check['passed'] or not all(np.isfinite(x) and x<=1e-5 for x in check['max_relative_errors']):
                raise RuntimeError('RETAINED_GRADIENT_ORACLE_FAILED')
    return True


def validate_case(case,y,session,rows,meta):
    m=meta[case];digest=hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()
    if m['training_array_sha256']!=digest or m['parent_AB_sha256']!=session['parent_AB_sha256'] or m['unit_count']!=y.shape[-1] or m['mouse_id']!=session['mouse_id']:
        raise RuntimeError('REUSED_TRAINING_CASE_CHANGED')
    for row in rows:
        if row['session_id']+'_'+row['region']==case and row['training_unit_bins']!=y.size:
            raise RuntimeError('REUSED_EXPOSURE_CHANGED')
