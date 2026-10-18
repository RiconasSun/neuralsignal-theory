"""Small M0 source, interval and native-time oracles; no predictive models."""
import bisect
import hashlib
import json
import math
import os
import struct
from collections import Counter, defaultdict
from pathlib import Path

MISSION = 'P16-VISUAL-CORTEX-DATA-FIRST-M0'
REGIONS = {'VISp', 'VISp1', 'VISp2/3', 'VISp4', 'VISp5', 'VISp6a', 'VISp6b'}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dump_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf8')
    temp = path.with_name(path.name + '.tmp')
    with temp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def native_time(value):
    value = float(value)
    return {'binary64_le': struct.pack('<d', value).hex(),
            'finite': math.isfinite(value),
            'hex': value.hex() if math.isfinite(value) else None}


def restore_time(record):
    value, = struct.unpack('<d', bytes.fromhex(record['binary64_le']))
    if record['finite'] != math.isfinite(value):
        raise ValueError('Finite/missing flag mismatch')
    if math.isfinite(value) and value.hex() != record['hex']:
        raise ValueError('Binary64 identity mismatch')
    return value


def ordered_finite(values):
    if any(not math.isfinite(float(x)) for x in values):
        raise ValueError('Nonfinite timestamp')
    if any(a > b for a, b in zip(values[:-1], values[1:])):
        raise ValueError('Unordered timestamps')


def strict_past_index(times, start):
    ordered_finite(times)
    if not math.isfinite(start):
        raise ValueError('Nonfinite prediction time')
    return bisect.bisect_left(times, start) - 1


def intervals(values):
    result = sorted((float(a), float(b)) for a, b in values)
    if any(not (math.isfinite(a) and math.isfinite(b) and a < b) for a, b in result):
        raise ValueError('Invalid observation interval')
    merged = []
    for a, b in result:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(b, merged[-1][1])
        else:
            merged.append([a, b])
    return merged


def observed(a, b, support, invalid):
    return (any(left <= a and b <= right for left, right in support)
            and not any(left < b and a < right for left, right in invalid))


def count_bins(spikes, edges, support, invalid=()):
    ordered_finite(spikes)
    ordered_finite(edges)
    if len(edges) < 2 or any(a >= b for a, b in zip(edges[:-1], edges[1:])):
        raise ValueError('Bin edges must increase')
    support, invalid = intervals(support), intervals(invalid)
    return [bisect.bisect_left(spikes, b) - bisect.bisect_left(spikes, a)
            if observed(a, b, support, invalid) else None
            for a, b in zip(edges[:-1], edges[1:])]


def presentation_records(ids, starts, stops):
    if len(ids) != len(starts) or len(ids) != len(stops) or len(set(ids)) != len(ids):
        raise ValueError('Presentation identity mismatch')
    return [{'original_ordinal': i, 'presentation_id': str(key),
             'start': native_time(a), 'stop': native_time(b)}
            for i, (key, a, b) in enumerate(zip(ids, starts, stops))]


def source_qualified(row):
    try:
        a, p, v = (float(row[k]) for k in ('amplitude_cutoff', 'presence_ratio', 'isi_violations'))
    except (ValueError, TypeError, KeyError):
        return False
    return (row.get('quality') == 'good' and all(math.isfinite(x) for x in (a, p, v))
            and 0 <= a <= .1 and .95 <= p <= 1 and 0 <= v <= .5)


def metadata_populations(sessions, probes, channels, units):
    """Preserve all probe rows and select at most one same-probe population/mouse."""
    def keyed(rows):
        out = {int(r['id']): r for r in rows}
        if len(out) != len(rows):
            raise ValueError('Duplicate source IDs')
        return out
    sm, pm, cm = keyed(sessions), keyed(probes), keyed(channels)
    if len({int(u['id']) for u in units}) != len(units):
        raise ValueError('Duplicate unit IDs')
    by_probe = defaultdict(list)
    excluded = Counter()
    for u in units:
        channel = cm.get(int(u['ecephys_channel_id']))
        if channel is None:
            raise ValueError('Unit missing source channel')
        pid = int(channel['ecephys_probe_id'])
        if pid not in pm:
            raise ValueError('Channel missing probe')
        region = channel.get('structure_acronym', channel.get('ecephys_structure_acronym'))
        if region in REGIONS:
            by_probe[pid].append(u)
        else:
            excluded['outside_VISp_or_unmapped'] += 1
    populations = []
    for pid, p in sorted(pm.items()):
        sid = int(p['ecephys_session_id'])
        if sid not in sm:
            raise ValueError('Probe missing source session')
        s = sm[sid]
        qualified = sorted(int(u['id']) for u in by_probe[pid] if source_qualified(u))
        try:
            rate = float(p['sampling_rate'])
            source_probe_valid = math.isfinite(rate) and rate > 0
        except (ValueError, TypeError, KeyError):
            source_probe_valid = False
        populations.append({'mouse_id': str(s['specimen_id']), 'session_id': sid,
                            'probe_id': pid, 'probe_name': p.get('name'),
                            'session_type': s.get('stimulus_name', s.get('session_type')),
                            'date_of_acquisition': s.get('date_of_acquisition', ''),
                            'fail_eye_tracking': s.get('fail_eye_tracking'),
                            'anatomical_units': len(by_probe[pid]),
                            'qualified_units': len(qualified), 'qualified_unit_ids': qualified,
                            'source_probe_valid': source_probe_valid,
                            **{f'tier_{n}': source_probe_valid and len(qualified) >= n for n in (5, 8, 12, 20)}})
    candidates = defaultdict(list)
    for row in populations:
        if row['tier_8']:
            candidates[row['mouse_id']].append(row)
    selected = []
    for mouse, rows in sorted(candidates.items()):
        date_sid = min((r['date_of_acquisition'], r['session_id']) for r in rows)
        same_session = [r for r in rows if (r['date_of_acquisition'], r['session_id']) == date_sid]
        selected.append(dict(min(same_session, key=lambda r: (-r['qualified_units'], r['probe_id']))))
    return {'all_populations': populations, 'selected': selected,
            'excluded_unit_reasons': dict(excluded),
            'source_units': len(units), 'source_sessions': len(sm),
            'source_mice': len({str(s['specimen_id']) for s in sessions})}


def allocate_roles(selected, historical_mouse_ids, historical_final_mouse_ids):
    if len({r['mouse_id'] for r in selected}) != len(selected):
        raise ValueError('Repeated mouse cannot become independent')
    history = set(map(str, historical_mouse_ids)) | set(map(str, historical_final_mouse_ids))
    fresh = [r for r in selected if str(r['mouse_id']) not in history]
    order = lambda r: hashlib.sha256((MISSION + r['mouse_id']).encode()).hexdigest()
    final_ids = set()
    if len(selected) >= 16 and len(fresh) >= 8:
        final_ids = {r['mouse_id'] for r in sorted(fresh, key=order)[:min(len(selected) // 2, len(fresh))]}
    return [{**r, 'group': 'Final_candidate' if r['mouse_id'] in final_ids else 'Development',
             'historical_source_overlap': str(r['mouse_id']) in history}
            for r in selected]


def choose_pilots(roles, object_sizes, historical_final_mouse_ids):
    blocked = set(map(str, historical_final_mouse_ids))
    pool = [r for r in roles if r['group'] == 'Development'
            and str(r['mouse_id']) not in blocked and r['session_id'] in object_sizes]
    rank = lambda r: (object_sizes[r['session_id']], r['session_id'])
    selected = []
    for kind in ('brain_observatory_1.1', 'functional_connectivity'):
        items = [r for r in pool if r['session_type'] == kind]
        if items:
            selected.append(min(items, key=rank))
    for r in sorted(pool, key=rank):
        if len(selected) == 2:
            break
        if r not in selected:
            selected.append(r)
    if len(selected) > 2 or sum(object_sizes[r['session_id']] for r in selected) > 5_980_000_000:
        raise ValueError('Registered pilot pair exceeds transfer ceiling')
    return selected


class TransferBudget:
    """Single downloader, durable consumed-payload ledger; interruption never resets it."""
    def __init__(self, path, ceiling=6_000_000_000):
        self.path, self.ceiling = Path(path), ceiling

    def charge(self, size, label):
        if type(size) is not int or size < 0:
            raise ValueError('Invalid byte charge')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock = self.path.with_suffix('.lock')
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            d = read_json(self.path) if self.path.exists() else {'bytes': 0, 'events': []}
            if d['bytes'] + size > self.ceiling:
                raise ValueError('Pilot transfer ceiling exceeded')
            d['bytes'] += size
            d['events'].append({'bytes': size, 'label': label})
            dump_json(self.path, d)
            return d['bytes']
        finally:
            os.close(fd)
            lock.unlink()
