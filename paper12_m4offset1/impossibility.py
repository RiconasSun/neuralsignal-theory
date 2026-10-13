"""Convergence-only necessary condition for the unchanged full-cohort selection."""
import itertools

FAMILIES=('Discrete','Continuous','Hybrid')


def complete(rows,sessions,definition):
    selected=[r for r in rows if all(r.get(k)==v for k,v in definition.items())]
    expected=set(itertools.product(sessions,('CA1','DG'),(11,23,37)))
    return len(selected)==len(expected) and {(r['session_id'],r['region'],r['seed']) for r in selected}==expected and all(r['converged'] is True for r in selected)


def early_failure(rows,sessions):
    definitions=[dict(family=f,size=size,ridge=ridge) for f in FAMILIES for size in ((1,2,4) if f=='Continuous' else (2,3,4)) for ridge in (.001,.01,.1,1.)]
    expected={(s,roi,seed,d['family'],d['size'],d['ridge']) for s in sessions for roi in ('CA1','DG') for seed in (11,23,37) for d in definitions}
    dynamic=[r for r in rows if r['family'] in FAMILIES]
    if len(dynamic)!=len(expected) or {(r['session_id'],r['region'],r['seed'],r['family'],r['size'],r['ridge']) for r in dynamic}!=expected:
        raise RuntimeError('COMPLETE_PREFIX_GRID_REQUIRED_BEFORE_IMPOSSIBILITY_STOP')
    possible={f:sum(complete(dynamic,sessions,d) for d in definitions if d['family']==f) for f in FAMILIES}
    failed=next((f for f in FAMILIES if possible[f]==0),None)
    return ('FAMILY_HAS_NO_POSSIBLE_COHORT_ELIGIBLE_CONFIGURATION:'+failed if failed else None),possible
