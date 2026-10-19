"""Frozen M2 array-only running and A-physiology checks; no IO or fitting."""
import math
import numpy as np


def native_times(values):
    a = np.asarray(values)
    if a.dtype != np.dtype('float64') or a.ndim != 1 or not np.isfinite(a).all():
        raise ValueError('Finite native binary64 vector required')
    if np.any(np.diff(a) < 0):
        raise ValueError('Source time order')
    return a


def invalid_intervals(values):
    a = np.asarray(values, dtype=float).reshape(-1, 2)
    if not np.isfinite(a).all() or np.any(a[:, 1] <= a[:, 0]):
        raise ValueError('Source invalid intervals')
    return a


def overlaps(a, b, invalid):
    return bool(np.any((invalid[:, 0] < b) & (a < invalid[:, 1])))


def running_features(start, end, rotation, targets, invalid=(), unit='radians'):
    start, end = native_times(start), native_times(end)
    rotation = np.asarray(rotation)
    targets = np.asarray(targets)
    if (unit != 'radians' or rotation.dtype != np.dtype('float64') or
            rotation.ndim != 1 or len(start) != len(end) or len(start) != len(rotation) or
            not np.isfinite(rotation).all() or np.any(end <= start)):
        raise ValueError('Running units/row correspondence/integrity')
    if targets.dtype != np.dtype('float64') or not np.isfinite(targets).all():
        raise ValueError('Target native time integrity')
    bad = invalid_intervals(invalid)
    valid = (end - start > 0) & (end - start <= .1)
    for i in np.flatnonzero(valid):
        if overlaps(start[i], end[i], bad):
            valid[i] = False
    selected = np.flatnonzero(valid)
    out = np.zeros(targets.shape, dtype=float)
    missing = np.ones(targets.shape, dtype=bool)
    parent = np.full(targets.shape, -1, dtype=np.int64)
    # Latest valid parent, strictly ending before the prediction time. A gap
    # between that parent and prediction is also prohibited from crossing invalidity.
    for idx in np.ndindex(targets.shape):
        t = targets[idx]
        j = np.searchsorted(end[selected], t, side='left') - 1
        if j < 0:
            continue
        p = selected[j]
        age = t - end[p]
        if not 0 < age <= .1 or overlaps(start[p], t, bad):
            continue
        out[idx] = math.tanh(float(rotation[p] / (end[p] - start[p])) / 10.)
        missing[idx] = False
        parent[idx] = p
    return out, missing, parent


def role_coverage(missing, color, source_valid):
    if missing.shape != (150, 6) or color.shape != (150,) or source_valid.shape != (150,):
        raise ValueError('Original150/six score bins required')
    result = {}
    for role, (lo, hi, floor) in {'A': (0, 90, 30), 'B': (90, 120, 8), 'E': (120, 150, 8)}.items():
        result[role] = {}
        for c in [-1., 1.]:
            rows = np.flatnonzero((color == c) & source_valid & (np.arange(150) >= lo) & (np.arange(150) < hi))
            total = int(len(rows) * 6)
            available = int((~missing[rows]).sum())
            maximum_available = int(np.sort((~missing[rows]).sum(axis=1))[-floor:].sum()) if len(rows) >= floor else 0
            result[role][str(c)] = {'presentations': len(rows), 'score_bins': total,
                                     'available': available,
                                     'fraction': available / total if total else None,
                                     'pass': bool(len(rows) >= floor and total and available >= total / 2),
                                     'optimistic_fraction_upper_bound': maximum_available / (6 * floor),
                                     'possible_after_observation_support': bool(len(rows) >= floor and maximum_available >= 3 * floor)}
    return result


def physiological_summary(spikes, windows, role):
    if role != 'A':
        raise ValueError('This mission authorizes A physiology only')
    spikes = native_times(spikes)
    count = occupied = pairs = short = 0
    exposure = 0.
    prior_end = -math.inf
    for a, b in windows:
        if not (math.isfinite(a) and math.isfinite(b) and prior_end <= a < b):
            raise ValueError('Observation windows must be valid and disjoint')
        prior_end = b
        x = spikes[np.searchsorted(spikes, a, side='left'):np.searchsorted(spikes, b, side='left')]
        count += len(x)
        occupied += bool(len(x))
        exposure += b - a
        d = np.diff(x)
        pairs += len(d)
        short += int((d < .0015).sum())
    if exposure <= 0:
        raise ValueError('No supported A exposure')
    rate = count / exposure
    passed = count >= 30 and occupied >= 20 and .5 <= rate <= 150 and pairs >= 20 and short / pairs <= .02
    return {'spikes': count, 'occupied': occupied, 'exposure': exposure, 'rate': rate,
            'ISI_pairs': pairs, 'short_ISI_pairs': short,
            'short_ISI_fraction': short / pairs if pairs else None, 'pass': bool(passed)}


def admission_possible(records):
    if len({x['mouse_id'] for x in records}) != len(records):
        raise ValueError('Duplicate source mouse')
    if any(x['protocol'] not in ['brain_observatory_1.1', 'functional_connectivity'] for x in records):
        raise ValueError('Unknown source protocol')
    admitted = [x for x in records if x['potential_running_coverage_pass']]
    bo = sum(x['protocol'] == 'brain_observatory_1.1' for x in admitted)
    fc = sum(x['protocol'] == 'functional_connectivity' for x in admitted)
    return {'eligible_running': len(admitted), 'BO': bo, 'FC': fc,
            'possible_A_physiological_admission': len(admitted) >= 14 and bo >= 3 and fc >= 10}
