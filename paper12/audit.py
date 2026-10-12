"""Full-denominator anatomy audit; unknown recording support never passes."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from register import verify, sha

HERE = Path(__file__).resolve().parent

def table(name):
    path = HERE / 'metadata' / ('allen_' + name + '.receipt')
    receipt = json.loads(path.with_suffix('.json').read_text())
    if sha(path) != receipt['sha256']:
        raise RuntimeError('Snapshot checksum mismatch')
    data = json.loads(path.read_text())
    if not data['success'] or len(data['msg']) != data['total_rows']:
        raise RuntimeError('Incomplete snapshot')
    return data['msg']

def classify(label):
    if label in ('CA1', 'CA3', 'DG'):
        return label
    if label in ('DG-mo', 'DG-po', 'DG-sg'):
        return 'DG'
    return None

def potential(counts):
    return counts['CA1'] >= 5 and counts['DG'] >= 5

def evaluate(sessions, probes, channels, units):
    s = {r['id']: r for r in sessions}
    p = {r['id']: r for r in probes}
    c = {r['id']: r for r in channels}
    if any(len(rows) != len({r['id'] for r in rows}) for rows in (sessions, probes, channels, units)):
        raise RuntimeError('Duplicate table identity')
    counts = defaultdict(Counter)
    probe_counts = defaultdict(Counter)
    label_counts = Counter()
    orphan = Counter()
    for unit in units:
        channel = c.get(unit['ecephys_channel_id'])
        if channel is None:
            orphan['unit_channel'] += 1
            continue
        probe = p.get(channel['ecephys_probe_id'])
        if probe is None:
            orphan['channel_probe'] += 1
            continue
        if probe['ecephys_session_id'] not in s:
            orphan['probe_session'] += 1
            continue
        label = channel['structure_acronym']
        label_counts[str(label)] += 1
        region = classify(label)
        if region:
            counts[probe['ecephys_session_id']][region] += 1
            probe_counts[probe['id']][region] += 1
    for probe in probes:
        if probe['ecephys_session_id'] not in s:
            orphan['probe_session_metadata'] += 1
    by_mouse = defaultdict(list)
    coverage = []
    for session in sessions:
        sid = session['id']
        row = dict(session)
        row.update({region + '_candidate_units': counts[sid][region] for region in ('CA1', 'CA3', 'DG')})
        row['potential_paired_CA1_DG'] = potential(counts[sid])
        row['recording_support'] = 'UNKNOWN'
        row['simultaneous_support_verified'] = False
        row['trial_intervals_verified'] = False
        coverage.append(row)
        by_mouse[session['specimen_id']].append(row)
    mouse_rows = [{'mouse_id': mid, 'sessions': len(rows),
                   'potential_paired_sessions': sum(r['potential_paired_CA1_DG'] for r in rows),
                   'admitted_sessions': 0} for mid, rows in sorted(by_mouse.items())]
    probe_rows = [dict(r, **{region + '_candidate_units': probe_counts[r['id']][region]
                            for region in ('CA1', 'CA3', 'DG')}) for r in probes]
    return {'denominator': {'sessions': len(sessions), 'mice': len(by_mouse),
                            'probes': len(probes), 'channels': len(channels), 'units': len(units)},
            'potential_paired_sessions': sum(r['potential_paired_CA1_DG'] for r in coverage),
            'potential_paired_mice': sum(r['potential_paired_sessions'] > 0 for r in mouse_rows),
            'admitted_mice': 0, 'orphans': dict(orphan), 'raw_unit_labels': dict(sorted(label_counts.items())),
            'sessions': coverage, 'mice': mouse_rows, 'probes': probe_rows}

def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main(output=None):
    verify()
    result = evaluate(*(table(n) for n in ('sessions', 'probes', 'channels', 'units')))
    output = Path(output) if output else HERE / 'results'
    output.mkdir(exist_ok=True, parents=True)
    for key in ('sessions', 'mice', 'probes'):
        write_csv(output / ('allen_' + key + '.csv'), result.pop(key))
    (output / 'allen_coverage.json').write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2))
    return result

if __name__ == '__main__':
    main()
