"""Saved-only independent reconstruction of the consumed diagnostic evidence."""
import json
import socket
from unittest.mock import patch
import numpy as np
from .common import P, E, OLD, MICE, read, identities, load_mouse, manual_B2, sha
from . import replay


def audit():
    identities()
    root = P / 'results/replay'
    if (root / 'IDENTITY_STOP.json').exists():
        return {'diagnosis': 'ROOT_CAUSE_UNDETERMINED', 'identity_stop': read(root / 'IDENTITY_STOP.json'),
            'original_M6': 'FAIL_UNAVAILABLE', 'further_replay_authorized': False}
    attempt, result = read(root / 'ATTEMPT.json'), read(root / 'RESULT.json')
    assert attempt['purpose'] == 'ONE_DIAGNOSTIC_PREFIX_NOT_SCIENTIFIC_NULL'
    assert attempt['seed'] == 130104 and attempt['mice'] == MICE and attempt['replicate'] == 0
    assert attempt['input_freeze_sha256'] == sha(P / 'INPUT_FREEZE.json')
    assert attempt['observer_freeze_sha256'] == sha(P / 'REPLAY_FREEZE.json')
    assert result['failure_identity_matched'] is True and result['stopped_at_original_failure'] is True
    assert result['mouse_order'] == MICE and result['failure'] == {'mouse_id': '156130', 'index': 3, 'replicate': 0}
    assert result['new_real_fits'] == result['final_C_fits'] == 0 and result['final_D_access'] is False
    assert result['runtime'] == read(P / 'REPLAY_FREEZE.json')['runtime']
    assert result['original_error'] == {'type': 'FloatingPointError', 'message': 'overflow encountered in exp', 'line': replay.Observer().line}
    assert read(E / 'D2_NATIVE_EXIT.json')['exit_code'] == 0
    replay.approval()
    expected = np.load(OLD / 'results/m6_controls_E/conditional_Bstar.npy', allow_pickle=False, mmap_mode='r')
    assert len(result['matched_rows']) == 3
    for index, mouse in enumerate(MICE[:3]):
        row = result['matched_rows'][index]
        assert row['mouse_id'] == mouse and row['scores_byte_exact'] is True
        replay.require_row_match(row['scores'], expected[0, index])
        assert read(root / (mouse+'_RNG_after.json')) == read(root / (MICE[index+1]+'_RNG_before.json'))
        trace = read(root / (mouse+'_TRACE.json'))
        assert trace['exception'] is None
        assert [r['bin_zero_based'] for r in trace['bins']] == list(range(30))
    assert result['failure_prefix_sha256'] == sha(root / 'failure_prefix.npz')
    with np.load(root / 'failure_prefix.npz', allow_pickle=False) as arrays:
        generated, etas, independent_saved, units = [arrays[k].copy() for k in ['generated', 'eta_history', 'independent_eta_at_failure', 'unit_ids']]
    trace = result['bin_trace']; t = trace[-1]['bin_zero_based']
    assert [r['bin_zero_based'] for r in trace] == list(range(t+1))
    assert generated.shape == (30, 30, 8) and etas.shape == (t+1, 30, 8)
    assert np.issubdtype(generated.dtype, np.integer) and np.all(generated >= 0) and not generated[:, t:].any()
    assert np.isfinite(etas).all() and len(result['overflow_cells']) > 0
    limit = np.log(np.finfo(np.float64).max)
    assert result['log_float64_max'] == float(limit)
    assert np.all(etas[:-1] <= limit) and np.any(etas[-1] > limit)
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Saved audit forbids network')), patch.object(replay.core, 'conditional_counts', side_effect=AssertionError('Saved audit forbids simulation')), patch.object(replay.core, 'replicate', side_effect=AssertionError('Saved audit forbids new scores')):
        _, _, bundle, ordinals, expected_units = load_mouse('156130')
        raw, terms, independent, beta, intercept = manual_B2(generated, bundle)
    np.testing.assert_array_equal(units, expected_units)
    np.testing.assert_array_equal(independent_saved, independent[:, t])
    np.testing.assert_allclose(independent[:, t], etas[-1], rtol=2e-14, atol=2e-14)
    cells = []
    for cell in result['overflow_cells']:
        epoch, unit = cell['epoch_index_zero_based'], cell['unit_index_zero_based']
        assert cell['unit_id'] == int(units[unit]) and cell['original_epoch_ordinal'] == ordinals[epoch]
        assert cell['eta_original'] == float(etas[-1, epoch, unit]) > limit
        assert cell['history_group_counts'] == raw[epoch, t, unit, 1:].tolist()
        assert cell['raw_history_slopes'] == beta[unit, 1:].tolist()
        assert cell['generated_unit_prefix'] == generated[epoch, :t, unit].tolist()
        np.testing.assert_allclose(sum(cell['standardized_terms']), cell['eta_original'], rtol=2e-14, atol=2e-14)
        np.testing.assert_allclose(cell['raw_intercept'] + sum(cell['raw_history_contributions']), cell['eta_original'], rtol=2e-14, atol=2e-14)
        cells.append(cell)
    assert len(cells) == len(np.argwhere(etas[-1] > limit))
    assert sha(OLD / 'results/source_access.jsonl') == read(P / 'results/D1_STATIC.json')['source_access_log_sha256']
    return {'diagnosis': 'DOCUMENTED_GENERATOR_INSTABILITY', 'scope': 'Realized frozen finite-horizon simulation path; no global instability theorem',
        'matched_prefix_rows': 3, 'failed_mouse': '156130', 'failed_bin_zero_based': t,
        'failed_bin_one_based': t+1, 'log_float64_max': float(limit),
        'eta_max_at_failure': float(etas[-1].max()), 'max_finite_generated_count': int(generated.max()),
        'overflow_cells': cells, 'diagnostic_replays_consumed': 1, 'scientific_null_replacements': 0,
        'original_M6': 'FAIL_UNAVAILABLE', 'new_real_fits': 0, 'final_C_fits': 0, 'final_D_access': False}


if __name__ == '__main__':
    print(json.dumps(audit(), allow_nan=False, sort_keys=True))
