"""D1 saved-code/scaler/input audit; no conditional simulation or RNG draws."""
import numpy as np
from .common import P, E, OLD, MICE, identities, load_mouse, manual_B2, save_new, sha
from paper13_ki_execution1.predictive import baseline_eta


def run():
    identities()
    output = {'phase': 'D1_STATIC_ONLY', 'conditional_simulations': 0,
        'log_float64_max': float(np.log(np.finfo(np.float64).max)),
        'source_checks': {
            'lag_groups': [[1], [2, 3], [4, 5]], 'strict_past': True, 'epoch_reset': True,
            'standardization': '(raw-A_mean)/A_population_sd; zero-SD coordinate0',
            'intercept': 'Amean0/SD1; log expected count per100ms, no exposure multiplier',
            'recursion': 'generate all30bins including warmup; calculate eta then exp then Poisson then assign current counts',
            'same_bin_or_other_unit_feedback_in_B2': False, 'coefficient_bounds_bound_simulated_count_support': False,
            'registered_model_match': 'No demonstrated mismatch: original own-history/scaling/log-link/strict-order definitions match'},
        'mice': {}}
    for mouse in MICE:
        y, q, bundle, ordinals, units = load_mouse(mouse)
        assert bundle['Bstar'] == 'B2'
        raw, terms, independent, beta, intercept = manual_B2(y, bundle)
        actual = baseline_eta(y, q, bundle, 'B2')
        error = float(np.max(np.abs(independent-actual)))
        assert np.allclose(independent, actual, rtol=2e-14, atol=2e-14)
        inverse = intercept[None, None, :] + np.sum(raw[..., 1:] * beta[None, None, :, 1:], axis=-1)
        assert np.allclose(inverse, actual, rtol=2e-14, atol=2e-14)
        scale = bundle['baseline_scalers']['B2']
        theta = np.asarray(bundle['baseline_thetas']['B2']).reshape(8, 4)
        assert np.all(np.isfinite(theta)) and np.max(np.abs(theta)) <= 8
        assert np.array_equal(np.asarray(scale['mean'])[:, 0], np.zeros(8))
        assert np.array_equal(np.asarray(scale['sd'])[:, 0], np.ones(8))
        output['mice'][mouse] = {'Bstar': bundle['Bstar'], 'unit_ids': units.tolist(), 'theta_standardized': theta.tolist(),
            'A_mean': scale['mean'], 'A_population_sd': scale['sd'], 'raw_history_slopes': beta[:, 1:].tolist(),
            'effective_raw_intercept': intercept.tolist(), 'own_history_group_maxima_observed_E': raw[..., 1:].max(axis=(0, 1)).tolist(),
            'observed_E_count_max': int(y.max()), 'observed_E_eta_min': float(actual.min()),
            'observed_E_eta_max': float(actual.max()), 'independent_formula_max_absolute_error': error,
            'static_limitation': 'Positive feedback or unconstrained count support alone does not identify the realized failed stochastic path'}
    output.update(static_can_establish_actual_failed_path=False,
        replay_needed=True, reason='Saved failure lacks bin/unit/generated prefix. Static equations match B2 but do not establish actual failure mechanism.',
        original_failure_remains='FAIL_UNAVAILABLE', new_real_fits=0, final_C_fits=0, final_D_access=False,
        source_access_log_sha256=sha(OLD / 'results/source_access.jsonl'))
    save_new(P / 'results/D1_STATIC.json', output)
    (E / 'D1_STATIC_REPORT.md').write_text('''# D1 static determination

Frozen B2 computes three strictly past own-unit count sums, resets each epoch, uses A-only mean/population-SD and unscaled intercept, then evaluates the Poisson log-link. Generator loops bins0..29, calculates eta from already assigned bins, exponentiates and only then samples/assigns current counts; all warm-up bins are simulated. No nuisance/current-count/cross-unit term enters B2. Raw-coordinate slopes theta/sd and effective intercept theta0-sum(theta*mean/sd) reproduce the saved-input log-rates; zero SD remains zero. No demonstrated implementation/protocol discrepancy.

Saved D1_STATIC.json contains original standardized coefficients, A scalers, inverse slopes, observed-E feature/rate ranges and independent scalar-loop formula checks for each of the four prefix mice. Coefficient bounds do not impose a hard upper bound on generated history counts or exponential means. log(float64max) is a numerical boundary, not a stability certificate.

Static source/parameter evidence cannot determine the actual failed bin, unit or generated history prefix, which the original failure did not serialize. A feedback sign alone cannot prove the realized mechanism. D1 therefore cannot establish the full root cause. The prospectively registered single exact failed-prefix replay is needed; no simulation or RNG draw has been performed in D1. Original numerical STOP and6/9coverage INCONCLUSIVE restrictions remain unchanged.
''', encoding='utf8')
    return output


if __name__ == '__main__':
    print(run()['reason'])
