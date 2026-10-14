def validate(rows):
    expected={(roi,f,k,ridge,seed) for roi in ('CA1','DG') for f in ('Discrete','Continuous','Hybrid') for k in ((1,2,4) if f=='Continuous' else (2,3,4)) for ridge in (.001,.01,.1,1.) for seed in (11,23,37)}
    actual={(z['region'],z['family'],z['size'],z['ridge'],z['seed']) for z in rows}
    if len(rows)!=216 or actual!=expected or any(z['session_id']!='766640955' or z['mouse_id']!='744912849' or any('validation' in k for k in z) for z in rows):
        raise RuntimeError('EXACT_FIRST_MOUSE_TRAINING_REFERENCE_ROSTER_REQUIRED')
    return True
