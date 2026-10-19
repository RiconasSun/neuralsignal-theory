"""Native A-only extraction and frozen source/QC rules. No network or fitting."""
from pathlib import Path
import hashlib
import json
import math
import os
import numpy as np

R = Path(__file__).resolve().parents[1]
P = R/'paper16_dev_r3'
E = R/'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3'


class SourceStop(ValueError): pass
class ResourceStop(RuntimeError): pass
class CommonSupportStop(SourceStop): pass


def load(path): return json.loads(Path(path).read_text(encoding='utf8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def once(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def array_id(a):
    a = np.asarray(a)
    return {'dtype': a.dtype.str, 'shape': list(a.shape), 'sha256': hashlib.sha256(a.tobytes(order='C')).hexdigest()}


def save_arrays(path, arrays):
    with Path(path).open('xb') as f:
        np.savez_compressed(f, **arrays); f.flush(); os.fsync(f.fileno())
    return {'sha256': sha(path), 'arrays': {k: array_id(v) for k, v in arrays.items()}}


def validate_item(item, reg):
    matches = [x for x in reg['objects'] if x['session_id'] == item.get('session_id')]
    if (item.get('session_id') in reg['denied_final_session_ids'] or len(matches) != 1
            or item != matches[0] or item.get('role') != 'Development'):
        raise SourceStop('Final/unregistered/altered source denied before opening')


def frozen_functions(reg):
    # Verify exact source versions BEFORE importing their mathematical functions.
    for name in ['paper16_dev/m2_core.py', 'paper16_m0/code/core.py']:
        if sha(R/name) != reg['old_pins'][name]: raise SourceStop('Frozen mathematical source changed')
    from paper16_dev.m2_core import physiological_summary, role_coverage
    from paper16_m0.code.core import intervals, observed
    return physiological_summary, role_coverage, intervals, observed


def finite_native(values):
    a = np.asarray(values)
    if a.dtype != np.dtype('float64') or a.ndim != 1 or not np.isfinite(a).all():
        raise SourceStop('Nonfinite/non-native binary64 spike timestamps; cannot partition')
    if np.any(a[1:] < a[:-1]): raise SourceStop('Decreasing selected-unit source timestamps')
    return a


def observation_mask(onsets, stops, source_valid, obs, reg):
    _, _, merge, observed = frozen_functions(reg)
    onsets, stops = np.asarray(onsets), np.asarray(stops)
    source_valid = np.asarray(source_valid)
    if (onsets.dtype != np.dtype('float64') or stops.dtype != np.dtype('float64')
            or onsets.shape != (150,) or stops.shape != (150,) or source_valid.shape != (150,)
            or source_valid.dtype != np.dtype('bool') or not np.isfinite(onsets).all()
            or not np.isfinite(stops).all() or np.any(np.diff(onsets) <= 0)
            or np.any(stops < onsets + 11*.02)):
        raise SourceStop('Original native flash/support identity')
    if obs is None:
        support = [[float(a), float(b)] for a, b in zip(onsets, stops)]
    else:
        raw = np.asarray(obs)
        if raw.dtype != np.dtype('float64') or raw.ndim != 2 or raw.shape[1] != 2:
            raise SourceStop('Native selected-unit observation metadata shape/dtype')
        support = merge(raw.tolist())
    return source_valid & np.array([observed(float(a), float(a+11*.02), support, [])
                                    for a in onsets], dtype=bool)


def coverage(mask, colors):
    mask, colors = np.asarray(mask), np.asarray(colors)
    if mask.shape != (150,) or mask.dtype != np.dtype('bool') or colors.shape != (150,) or not np.isin(colors, [-1, 1]).all():
        raise SourceStop('Original presentation mask/color identity')
    result = {}
    for role, lo, hi, floor in [('A', 0, 90, 30), ('B', 90, 120, 8), ('E', 120, 150, 8)]:
        for color in [-1, 1]:
            n = int(np.count_nonzero(mask[lo:hi] & (colors[lo:hi] == color)))
            result[f'{role}:{color}'] = {'presentations': n, 'minimum': floor, 'pass': n >= floor}
    return result


def extract_a(spikes, onsets, mask, role='A'):
    if role != 'A': raise SourceStop('M2 cannot export B/E/Final neural observations')
    spikes = finite_native(spikes)
    rows = np.flatnonzero(np.asarray(mask) & (np.arange(150) < 90))
    pieces, offsets = [], [0]
    for i in rows:
        a, b = onsets[i], onsets[i] + 11*.02
        values = spikes[np.searchsorted(spikes, a, side='left'):np.searchsorted(spikes, b, side='left')].copy()
        pieces.append(values); offsets.append(offsets[-1]+len(values))
    times = np.concatenate(pieces) if pieces else np.empty(0, dtype=np.float64)
    return {'timestamps': times, 'offsets': np.asarray(offsets, dtype=np.int64),
            'original_ordinals': rows.astype(np.int64)}


def qc_a(arrays, onsets, reg):
    physiology, _, _, _ = frozen_functions(reg)
    times = finite_native(arrays['timestamps'])
    rows, offsets = arrays['original_ordinals'], arrays['offsets']
    if (rows.dtype != np.dtype('int64') or offsets.dtype != np.dtype('int64')
            or np.any((rows < 0) | (rows >= 90)) or np.any(np.diff(rows) <= 0)
            or offsets.shape != (len(rows)+1,) or offsets[0] != 0 or offsets[-1] != len(times)
            or np.any(np.diff(offsets) < 0)):
        raise SourceStop('A-only original-row/offset integrity')
    for j, row in enumerate(rows):
        value = times[offsets[j]:offsets[j+1]]
        if np.any((value < onsets[row]) | (value >= onsets[row]+11*.02)):
            raise SourceStop('Non-A/cross-window values in A capture')
    windows = [(float(onsets[i]), float(onsets[i]+11*.02)) for i in rows]
    if not windows:
        return {'spikes': 0, 'occupied': 0, 'exposure': 0., 'rate': None, 'ISI_pairs': 0,
                'short_ISI_pairs': 0, 'short_ISI_fraction': None, 'pass': False, 'reason': 'NO_SUPPORTED_A_PRESENTATIONS'}
    return physiology(times, windows, 'A')


def select_common(records, colors, running_missing, reg):
    ids = [int(x['unit_id']) for x in records]
    if len(ids) != len(set(ids)): raise SourceStop('Duplicate candidate unit result')
    good = sorted((x for x in records if x['A_physiology']['pass'] and x['individual_source_coverage_pass']), key=lambda x: int(x['unit_id']))
    if len(good) < 8:
        return {'admitted': False, 'reason': 'FEWER_THAN_EIGHT_A_QUALIFIED_SUPPORTED_UNITS',
                'passing_units': len(good), 'selected_unit_ids': [], 'common_mask': None}
    selected = good[:8]
    common = np.logical_and.reduce([np.asarray(x['observation_mask'], dtype=bool) for x in selected])
    counts = coverage(common, colors)
    _, running_coverage, _, _ = frozen_functions(reg)
    rc = running_coverage(np.asarray(running_missing), np.asarray(colors), common)
    if not all(x['pass'] for x in counts.values()) or not all(v['pass'] for role in rc.values() for v in role.values()):
        raise CommonSupportStop('Lowest eight common support/role/color/running gate failed; no replacement')
    return {'admitted': True, 'reason': None, 'passing_units': len(good),
            'selected_unit_ids': [int(x['unit_id']) for x in selected], 'common_mask': common.tolist(),
            'coverage': counts, 'running_coverage': rc}
