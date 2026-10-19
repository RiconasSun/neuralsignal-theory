"""Source-preserving precision adapter to unchanged frozen running mathematics."""
import hashlib
import numpy as np
from paper16_dev.m2_core import running_features, role_coverage, admission_possible


def array_identity(array):
    return {'dtype': array.dtype.str, 'shape': list(array.shape),
            'raw_bytes_sha256': hashlib.sha256(array.tobytes(order='C')).hexdigest()}


def native_arrays(start, end, rotation, first=False):
    if any(not isinstance(x, np.ndarray) or x.ndim != 1 for x in [start, end, rotation]):
        raise ValueError('Native vectors required')
    if start.dtype.str != '<f8' or end.dtype.str != '<f8':
        raise ValueError('Native binary64 source timestamps required without conversion')
    if rotation.dtype.str not in ['<f4', '<f8'] or (first and rotation.dtype.str != '<f4'):
        raise ValueError('Unsupported source rotation storage')
    if not 0 < len(start) == len(end) == len(rotation) <= 2000000:
        raise ValueError('Native source row correspondence/capacity')
    if any(not np.isfinite(x).all() for x in [start, end, rotation]):
        raise ValueError('Nonfinite native running source')
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        start_diff, end_diff, duration = np.diff(start), np.diff(end), end-start
    if not np.isfinite(duration).all() or np.any(start_diff < 0) or np.any(end_diff < 0):
        raise ValueError('Native source row order')
    if np.any(end <= start):
        raise ValueError('Nonpositive source interval')
    promoted = rotation.astype(np.float64, copy=True)
    if promoted.astype(rotation.dtype).tobytes() != rotation.tobytes():
        raise ValueError('Exact native rotation roundtrip failed')
    if promoted.dtype.str != '<f8' or not np.isfinite(promoted).all():
        raise ValueError('Finite float64 arithmetic inputs required')
    report = {'start': array_identity(start), 'end': array_identity(end),
              'native_rotation': array_identity(rotation), 'promoted_rotation': array_identity(promoted),
              'float32_source_preserved': rotation.dtype.str == '<f4',
              'float64_promotion_exact': True, 'timestamps_preserved': True,
              'stored_zero_rows_retained': int(np.count_nonzero(rotation == 0)),
              'duplicate_start_differences': int(np.count_nonzero(start_diff == 0)),
              'duplicate_end_differences': int(np.count_nonzero(end_diff == 0)),
              'duration_over_point1_excluded_later': int(np.count_nonzero(duration > .1)),
              'extra_sensor_precision_claimed': False}
    return promoted, report


def derive(start, end, rotation, onsets, colors, source_valid, invalid, first=False):
    before = [array_identity(x) for x in [start, end, rotation]]
    promoted, report = native_arrays(start, end, rotation, first)
    if onsets.dtype.str != '<f8' or onsets.shape != (150,) or colors.shape != (150,) or source_valid.shape != (150,):
        raise ValueError('Frozen original flash/role metadata required')
    if not np.isfinite(onsets).all() or np.any(np.diff(onsets) <= 0) or set(colors.tolist()) != {-1., 1.}:
        raise ValueError('Frozen flash identity/order/color')
    targets = onsets[:, None] + np.arange(5, 11, dtype=np.float64)[None, :] * .02
    # Exactly the original M2 source-window subset, not a new selection rule.
    keep = (end >= onsets[0]-.2) & (start <= onsets[-1]+.22)
    original_rows = np.flatnonzero(keep)
    a, b, q = start[keep], end[keep], promoted[keep]
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        values, missing, parent = running_features(a, b, q, targets, invalid)
    parent_original = np.full(parent.shape, -1, dtype=np.int64)
    parent_original[~missing] = original_rows[parent[~missing]]
    if np.any(b[parent[~missing]] >= targets[~missing]):
        raise ValueError('Strict past invariant failed')
    coverage = role_coverage(missing, colors, source_valid)
    after = [array_identity(x) for x in [start, end, rotation]]
    if before != after:
        raise ValueError('Native source bits mutated during arithmetic')
    arrays = {'start': a, 'end': b, 'net_rotation_promoted': q, 'source_row_index': original_rows,
              'targets': targets, 'running': values, 'running_squared': np.square(values),
              'color_running': colors[:, None]*values, 'missing': missing, 'parent': parent,
              'parent_original_row': parent_original, 'color': colors, 'source_valid': source_valid,
              'invalid': np.asarray(invalid, dtype=np.float64).reshape(-1, 2)}
    if any(x.dtype.kind == 'f' and (x.dtype.str != '<f8' or not np.isfinite(x).all()) for x in arrays.values()):
        raise ValueError('Derived finite float64 policy')
    report.update({'coverage': coverage,
                   'direct_running_coverage_pass': all(x['pass'] for role in coverage.values() for x in role.values()),
                   'potential_running_coverage_pass': all(x['possible_after_observation_support'] for role in coverage.values() for x in role.values()),
                   'native_arrays_unchanged_after_features': True, 'rows_retained_for_features': len(a),
                   'strict_past_verified': True, 'no_imputed_zero_rows': True,
                   'native_retained_rows': len(start)})
    return arrays, report
