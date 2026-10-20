"""Synthetic witnesses of protocol interpretation differences; no fits or neural inputs.

These are not production numerical certification or proposed scientific operators.
They test whether unresolved definitions can affect units or fixed-model predictions.
"""
import json
import math


def witnesses():
    ids = list(range(1, 9))
    # Ten synthetic complete presentations. Both intervals have integer counts;
    # warmup counts are nonnegative. No fixture is a real mouse or admission QC.
    full_counts = [44, 55, 66, 77, 88, 99, 110, 121]
    score_counts = [36, 12, 42, 18, 40, 24, 38, 30]
    full_rates = [x / 2.2 for x in full_counts]
    score_rates = [x / 1.2 for x in score_counts]
    assert all(0 <= s <= f for s, f in zip(score_counts, full_counts))
    ranked = lambda rates: sorted(ids, key=lambda u: (rates[u - 1], u))[2:6]
    a, b = ranked(full_rates), ranked(score_rates)
    assert set(a) != set(b)
    # Two interpretations of colorflip with an already-fitted B1 coefficient:
    # flip only color x peri-onset PSTH indices, versus also the current-color
    # dependent color*running term. All other features and targets stay fixed.
    running, beta_color_running = .2, .7
    common_psth_eta = 1.0
    eta_psth_only = common_psth_eta + beta_color_running * running
    eta_current_color = common_psth_eta - beta_color_running * running
    assert eta_psth_only != eta_current_color
    ll = lambda eta: (math.log(.02) + eta) - .02 * math.exp(eta)
    return {
        'scope': 'SYNTHETIC_CONTRACT_DIFFERENCE_WITNESSES_ONLY',
        'real_data': False, 'optimization_attempts': 0,
        'S07': {
            'unit_ids': ids, 'full_window_counts': full_counts,
            'scored_window_counts': score_counts,
            'full_window_exposure': 2.2, 'scored_window_exposure': 1.2,
            'full_window_middle_four': a, 'scored_window_middle_four': b,
            'selected_sets_differ': True,
            'not_an_authorized_choice': True,
        },
        'N4': {
            'fixed_beta_color_running': beta_color_running, 'running': running,
            'common_wrong_PSTH_eta': common_psth_eta,
            'PSTH_only_flip_eta': eta_psth_only,
            'current_color_covariate_flip_eta': eta_current_color,
            'PSTH_only_fixed_target_logscore': ll(eta_psth_only),
            'current_color_flip_fixed_target_logscore': ll(eta_current_color),
            'predictions_differ': True, 'not_an_authorized_choice': True,
        },
    }


if __name__ == '__main__':
    print(json.dumps(witnesses(), indent=2))
