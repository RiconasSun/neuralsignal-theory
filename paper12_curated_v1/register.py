"""Metadata-only prospective registration; no neural reader is imported."""
import csv
import gzip
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'paper12_native_support1'
MISSION = 'P12-CURATED-EXPLORATORY-V1'
CHECKPOINT = '104a6afea72a6eb66620200d6fc261bca774400e'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1048576), b''):
            h.update(data)
    return h.hexdigest()


def digest(text):
    return hashlib.sha256(text.encode('ascii')).hexdigest()


def load(path):
    path = Path(path)
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    with gzip.open(str(path) + '.gz', 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def rows(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def save(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def allocate(mice):
    if len(mice) != 26 or len(set(mice)) != 26:
        raise ValueError('Exactly26independent metadata identities required')
    ordered = sorted(mice, key=lambda x: digest(MISSION + '|animal|' + x))
    return {m: 'development' if i < 13 else 'final' for i, m in enumerate(ordered)}


def partition(session, trials, group):
    if len(trials) != 600 or len({r['trial_index'] for r in trials}) != 600:
        raise ValueError('All600unique grating presentations must remain inventoried')
    by_condition = defaultdict(list)
    for row in trials:
        by_condition[row['condition']].append(row)
    if len(by_condition) != 8 or any(len(v) != 75 for v in by_condition.values()):
        raise ValueError('Expected8conditions x75genuine repetitions')
    result = {}
    for values in by_condition.values():
        ordered = sorted(values, key=lambda r: digest(MISSION + '|trial|' + session + '|' + r['trial_index']))
        for i, row in enumerate(ordered):
            result[row['trial_index']] = ('train' if group == 'development' else 'calibration') if i < 45 else (
                'validation' if group == 'development' else 'locked_evaluation')
    return result


def affected(tags, probe, registry):
    if 'EcephysProbe' in tags:
        tokens = [x for x in tags if x != 'EcephysProbe']
        matches = {p for p, name in registry.items() if p in tokens or name in tokens}
        if len(matches) != 1 or any(x not in set(registry) | set(registry.values()) for x in tokens):
            return None
        return probe in matches
    return True if any(x in tags for x in ('EcephysSession', 'Stimulus', 'stimulus', 'all_probes')) else None


def support(probe, start, end, invalid, registry):
    for interval in invalid:
        match = affected(interval['tags'], probe['probe_id'], registry)
        if match is None:
            return False
        if match and start < interval['stop'] and end > interval['start']:
            return False
    return any(x['pass'] and start >= x['master_anchor_min_seconds'] and
               end <= x['master_anchor_max_seconds'] for x in probe.get('segments', []))


def build():
    sessions = [r for r in rows(OLD / 'results/session_evidence_matrix.csv') if r['protocol'] == 'functional_connectivity']
    if len(sessions) != 26 or len({r['session_id'] for r in sessions}) != 26:
        raise ValueError('FC full denominator mismatch')
    groups = allocate([r['mouse_id'] for r in sessions])
    trial_groups = defaultdict(list)
    for r in rows(OLD / 'results/functional_connectivity_trial_inventory.csv'):
        if r['kind'] == 'grating':
            trial_groups[r['session_id']].append(r)
    anatomy = rows(OLD / 'results/unit_anatomy_uncertainty.csv')
    units_by_probe = defaultdict(list)
    for u in anatomy:
        if u['subfield'] in ('CA1', 'DG'):
            units_by_probe[u['probe_id']].append(u)
    inventory, trial_lock, unit_lock = [], [], []
    for session in sorted(sessions, key=lambda r: r['session_id']):
        sid = session['session_id']
        group = groups[session['mouse_id']]
        digital = load(OLD / 'results/digital_code2' / (sid + '.json'))
        probes = digital['probes']
        registry = {p['probe_id']: p['name'] for p in probes}
        inv = []
        for interval in rows(OLD / 'results/known_invalid_intervals.csv'):
            if interval['session_id'] == sid:
                inv.append({'start': float(interval['start']), 'stop': float(interval['stop']), 'tags': json.loads(interval['tags'])})
        admitted = []
        for p in probes:
            rate = p.get('api_sampling_rate_hz')
            rate_ok = isinstance(rate, (int, float)) and rate > 0 and rate < float('inf')
            quarantine = p['probe_id'] == '846401834' or not rate_ok
            target = units_by_probe[p['probe_id']]
            if target and not quarantine:
                admitted.append(p)
            for u in target:
                unit_lock.append({**u, 'session_id': sid, 'mouse_id': session['mouse_id'], 'group': group,
                                  'metadata_quarantined': quarantine, 'physiological_QC': 'NOT_ASSESSED'})
        part = partition(sid, trial_groups[sid], group)
        counts = defaultdict(int)
        conditions = defaultdict(lambda: defaultdict(int))
        for t in sorted(trial_groups[sid], key=lambda r: int(r['trial_index'])):
            start, stop = float(t['start']), float(t['stop'])
            supported = [p['probe_id'] for p in admitted if support(p, start, start + 2., inv, registry)]
            reasons = []
            if stop < start + 2.:
                reasons.append('ACTUAL_DURATION_BELOW_2S')
            if len(supported) != len(admitted) or not admitted:
                reasons.append('COMMON_PROBE_CLOCK_OR_INVALID_MASK')
            if session['grating_physical_frame_clock_pass'] != 'True':
                reasons.append('GRATING_FRAME_DIAGNOSTIC_FAIL')
            ok = not reasons
            split = part[t['trial_index']]
            if ok:
                counts[split] += 1
                conditions[t['condition']][split] += 1
            trial_lock.append({'trial_id': sid + ':grating:' + t['trial_index'], 'provider_row_index': int(t['trial_index']),
                               'session_id': sid, 'mouse_id': session['mouse_id'], 'group': group, 'partition': split,
                               'condition': t['condition'], 'start': start, 'provider_stop': stop, 'analysis_stop': start + 2.,
                               'nominal_bin_edges': [start + i / 10. for i in range(21)],
                               'metadata_admitted': ok, 'exclusions': reasons, 'supported_probe_ids': supported})
        inventory.append({'mouse_id': session['mouse_id'], 'session_id': sid, 'group': group,
                          'all_trials': 600, 'partition_counts_after_metadata_mask': dict(counts),
                          'condition_counts_after_metadata_mask': dict(conditions), 'primary_candidate_probe_ids': [p['probe_id'] for p in admitted],
                          'anatomical_potential_units': {s: sum(u['subfield'] == s and not u['metadata_quarantined'] for u in unit_lock if u['session_id'] == sid) for s in ('CA1', 'DG')},
                          'actually_eligible': None, 'physiological_QC': 'NOT_ASSESSED'})
    return inventory, trial_lock, unit_lock


def verify():
    reg = load(HERE / 'registration.json')
    for category in ('prior_sha256', 'frozen_sha256'):
        for name, value in reg[category].items():
            if sha(ROOT / name) != value:
                raise RuntimeError('Frozen evidence changed: ' + name)
    if reg['old_ops'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('Prior operations history modified')
    return reg


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        r = verify()
        print(json.dumps({'verified': True, 'prior_files': len(r['prior_sha256']), 'frozen_files': len(r['frozen_sha256'])}))
        return
    if (HERE / 'registration.json').exists():
        raise RuntimeError('Prospective registration is append-once')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != CHECKPOINT:
        raise RuntimeError('Wrong starting checkpoint')
    inventory, trials, units = build()
    save(HERE / 'locks/animals.json', inventory, True)
    save(HERE / 'locks/trials.json', trials, True)
    save(HERE / 'locks/units.json', units, True)
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    frozen = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'registration.json']
    frozen.append(ROOT / 'ops/evidence/2026-10-11/p12-curated-exploratory-v1/goldenstandards.md')
    reg = {'mission': MISSION, 'registered_utc': datetime.now(timezone.utc).isoformat(), 'prechange_HEAD': head,
           'neural_values_read_at_registration': 0,
           'prior_sha256': {p: sha(ROOT / p) for p in files if p and p != 'ops/daily-operations.md'},
           'frozen_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in frozen},
           'old_ops': (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8')}
    save(HERE / 'registration.json', reg, True)
    verify()
    summary = {'gate': 'PASS', 'milestone': 'M1', 'scope': 'Prospective registration only; no actual eligibility or scientific validation',
               'registered_utc': reg['registered_utc'], 'registration_sha256': sha(HERE / 'registration.json'),
               'candidate_mice': len(inventory), 'development_candidates': 13, 'final_candidates': 13,
               'all_locked_trials': len(trials), 'all_locked_target_unit_identities': len(units),
               'metadata_admitted_trials': sum(t['metadata_admitted'] for t in trials),
               'known_quarantined_unit_identities': sum(u['metadata_quarantined'] for u in units),
               'actually_eligible_mice': None, 'neural_values_decoded': 0, 'final_holdout_decoded': False,
               'original_M0_reclassified': False, 'prior_files_preserved': len(reg['prior_sha256'])}
    save(HERE / 'results/M1/gate_result.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
