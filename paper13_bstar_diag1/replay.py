"""One consumed diagnostic prefix; original function, observational tracing only."""
import inspect
import json
import os
import socket
import sys
import platform
import numpy as np
import scipy
from unittest.mock import patch
from .common import P, E, OLD, ROOT, MICE, read, sha, identities, load_mouse, manual_B2, save_new
from paper13_ki_execution1 import control_core as core


class Observer:
    def __init__(self):
        self.code = core.conditional_counts.__code__
        lines, first = inspect.getsourcelines(core.conditional_counts)
        candidates = [first+i for i, line in enumerate(lines) if 'means=np.exp(eta)' in line]
        if len(candidates) != 1:
            raise RuntimeError('Original exponential observation line identity is ambiguous')
        self.line = candidates[0]
        self.records = []
        self.etas = []
        self.last_generated = None
        self.exception = None

    def trace(self, frame, event, arg):
        if frame.f_code is self.code:
            if event == 'line' and frame.f_lineno == self.line:
                eta = frame.f_locals['eta']
                generated = frame.f_locals['generated']
                t = int(frame.f_locals['t'])
                if not np.isfinite(eta).all():
                    raise RuntimeError('Unexpected pre-exponential nonfinite eta; diagnostic identity STOP')
                self.records.append({'bin_zero_based': t, 'bin_one_based': t+1,
                    'eta_min': float(eta.min()), 'eta_max': float(eta.max()),
                    'previous_generated_count_max': int(generated[:, :t].max(initial=0)),
                    'positions_above_log_float64_max': np.argwhere(eta > np.log(np.finfo(np.float64).max)).tolist()})
                self.etas.append(eta.copy())
                self.last_generated = generated.copy()
            elif event == 'exception':
                kind, exc, _ = arg
                self.exception = {'type': kind.__name__, 'message': str(exc), 'line': frame.f_lineno}
            return self.trace
        return None


def observed_call(function):
    if sys.gettrace() is not None:
        raise RuntimeError('Existing tracer would invalidate original-function observation')
    observer = Observer()
    sys.settrace(observer.trace)
    try:
        result = function()
        return result, observer
    finally:
        sys.settrace(None)


def consume(path, registration):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write((json.dumps(registration, sort_keys=True, allow_nan=False)+'\n').encode('utf8'))
        stream.flush()
        os.fsync(stream.fileno())


def require_row_match(scores, expected):
    actual = np.asarray(scores, dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    if actual.shape != (9,) or expected.shape != (9,) or not np.isfinite(actual).all() or actual.tobytes() != expected.tobytes():
        raise RuntimeError('Completed prefix score row differs byte-for-byte; identity STOP')


def approval():
    a = read(P / 'REPLAY_APPROVAL.json')
    if not a.get('accepted'):
        raise PermissionError('Independent frozen observer review required')
    freeze = P / a['freeze_file']
    if sha(freeze) != a['freeze_sha256'] or sha(ROOT / a['review_path']) != a['review_sha256']:
        raise PermissionError('Observer review or source identity changed')
    for name, digest in read(freeze)['hashes'].items():
        if sha(ROOT / name) != digest:
            raise PermissionError('Unreviewed diagnostic source/input: '+name)


def run():
    identities()
    approval()
    if read(P / 'results/D1_STATIC.json').get('replay_needed') is not True:
        raise PermissionError('D1 did not establish necessity for replay')
    if core.SUITES[-1] != 'conditional_Bstar' or core.SEEDS['conditional_Bstar'] != 130104:
        raise PermissionError('Original conditional suite RNG identity mismatch')
    root = P / 'results/replay'
    consume(root / 'ATTEMPT.json', {'purpose': 'ONE_DIAGNOSTIC_PREFIX_NOT_SCIENTIFIC_NULL',
        'seed': 130104, 'mice': MICE, 'replicate': 0,
        'input_freeze_sha256': sha(P / 'INPUT_FREEZE.json'),
        'observer_freeze_sha256': sha(P / 'REPLAY_FREEZE.json')})
    rng = np.random.default_rng(130104)
    expected = np.load(OLD / 'results/m6_controls_E/conditional_Bstar.npy', allow_pickle=False, mmap_mode='r')
    record = {'purpose': 'DIAGNOSTIC_ONLY_EXCLUDED_FROM_ALL_M6_STATISTICS', 'matched_rows': [],
        'seed': 130104, 'bit_generator': type(rng.bit_generator).__name__, 'mouse_order': MICE,
        'runtime': {'Python': platform.python_version(), 'NumPy': np.__version__, 'SciPy': scipy.__version__},
        'new_real_fits': 0, 'final_C_fits': 0, 'final_D_access': False}
    active = {}
    try:
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('No source/network during diagnostic prefix')):
            for index, mouse in enumerate(MICE):
                active = {'mouse_id': mouse, 'index': index, 'replicate': 0}
                y, q, bundle, ordinals, units = load_mouse(mouse)
                save_new(root / (mouse+'_RNG_before.json'), rng.bit_generator.state)
                observer = Observer()
                if sys.gettrace() is not None:
                    raise RuntimeError('Unexpected tracer before real prefix')
                try:
                    sys.settrace(observer.trace)
                    with np.errstate(over='raise', invalid='raise', divide='raise'):
                        result = core.replicate('conditional_Bstar', y, q, bundle, ordinals, rng)
                except FloatingPointError as exc:
                    if index != 3 or str(exc) != 'overflow encountered in exp' or observer.exception is None:
                        raise RuntimeError('Failure identity differs from original') from exc
                    if len(record['matched_rows']) != 3 or observer.exception['message'] != str(exc):
                        raise RuntimeError('Original prefix or error location did not match') from exc
                    # No further stochastic draw or score is produced after original failure.
                    sys.settrace(None)
                    t = observer.records[-1]['bin_zero_based']
                    generated = observer.last_generated
                    raw, terms, independent, beta, intercept = manual_B2(generated, bundle)
                    actual = observer.etas[-1]
                    if not np.allclose(independent[:, t], actual, rtol=2e-14, atol=2e-14):
                        raise RuntimeError('Independent contribution reconstruction differs')
                    positions = observer.records[-1]['positions_above_log_float64_max']
                    if not positions:
                        raise RuntimeError('No observed exponential boundary crossing')
                    cells = []
                    for epoch, unit in positions:
                        cells.append({'epoch_index_zero_based': epoch, 'original_epoch_ordinal': ordinals[epoch],
                            'unit_index_zero_based': unit, 'unit_id': int(units[unit]),
                            'eta_original': float(actual[epoch, unit]), 'raw_intercept': float(intercept[unit]),
                            'history_group_counts': raw[epoch, t, unit, 1:].tolist(),
                            'raw_history_slopes': beta[unit, 1:].tolist(),
                            'raw_history_contributions': (raw[epoch, t, unit, 1:]*beta[unit, 1:]).tolist(),
                            'standardized_terms': terms[epoch, t, unit].tolist(),
                            'generated_unit_prefix': generated[epoch, :t, unit].tolist()})
                    with (root / 'failure_prefix.npz').open('xb') as stream:
                        np.savez_compressed(stream, generated=generated, eta_history=np.stack(observer.etas),
                            independent_eta_at_failure=independent[:, t], unit_ids=units)
                    record.update(failure_identity_matched=True, stopped_at_original_failure=True,
                        failure=active, original_error=observer.exception, bin_trace=observer.records,
                        overflow_cells=cells, log_float64_max=float(np.log(np.finfo(np.float64).max)),
                        max_finite_generated_count=int(generated.max()),
                        RNG_after_failure=rng.bit_generator.state, failure_prefix_sha256=sha(root / 'failure_prefix.npz'))
                    save_new(root / 'RESULT.json', record)
                    return record
                finally:
                    sys.settrace(None)
                    save_new(root / (mouse+'_TRACE.json'), {'bins': observer.records, 'exception': observer.exception})
                if index == 3:
                    raise RuntimeError('Fourth simulation succeeded instead of original overflow; identity STOP')
                scores = np.asarray([result['scores'][name] for name in core.LABELS], dtype=np.float64)
                require_row_match(scores, expected[0, index])
                record['matched_rows'].append({'mouse_id': mouse, 'scores_byte_exact': True,
                    'scores': scores.tolist(), 'nominal_unit_bins': result['nominal_unit_bins']})
                save_new(root / (mouse+'_RNG_after.json'), rng.bit_generator.state)
                save_new(root / (mouse+'_MATCH.json'), record['matched_rows'][-1])
    except Exception as exc:
        save_new(root / 'IDENTITY_STOP.json', {'active': active, 'error_type': type(exc).__name__,
            'error': str(exc), 'attempt_consumed': True, 'retry_authorized': False,
            'diagnosis': 'ROOT_CAUSE_UNDETERMINED', 'matched_rows': record['matched_rows']})
        raise


if __name__ == '__main__':
    result = run()
    print(json.dumps({'failure_identity_matched': result['failure_identity_matched'],
        'matched_rows': len(result['matched_rows']), 'overflow_cells': len(result['overflow_cells']),
        'stopped_at_original_failure': True}))
