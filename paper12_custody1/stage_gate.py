"""Progressive baseline numerical admission; failed fits are never erased."""
def assess(records, sessions):
    if len(set(sessions)) != len(sessions):
        raise ValueError('STAGE_SUBJECT_DUPLICATION')
    expected = len(sessions) * 126
    subset = [x for x in records if x['session_id'] in sessions]
    eligible = {}
    for region in ('CA1', 'DG'):
        eligible[region] = {}
        for kind in ('stationary', 'history', 'population', 'event', 'drift', 'combined'):
            ridges = [None] if kind == 'stationary' else [.001, .01, .1, 1.]
            options = []
            for ridge in ridges:
                fits = [x for x in subset if x['region'] == region and x['kind'] == kind and x['ridge'] == ridge]
                identities = {(x['session_id'], x['seed']) for x in fits}
                required = {(s, seed) for s in sessions for seed in (11, 23, 37)}
                if len(fits) == len(required) and identities == required and all(x['converged'] is True for x in fits):
                    options.append(ridge)
            eligible[region][kind] = options
    passed = len(subset) == expected and all(eligible[r][k] for r in eligible for k in eligible[r])
    return dict(gate='PASS' if passed else 'FAIL', expected_fit_count=expected,
                completed_fit_count=len(subset), eligible_ridges=eligible,
                sessions=sessions, mouse_count=len(sessions),
                scientific_verdict='BASELINE_NUMERICAL_ADMISSION' if passed else 'INCONCLUSIVE',
                final_values_exposed_to_analysis=False, final_holdout_evaluated=False,
                full_study_validated=False)
