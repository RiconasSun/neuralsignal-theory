"""Authorized32trial R0 amendment; fresh NIX QC and strictly partitioned arrays."""
import argparse
import csv
import json
import math
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np
import h5py
import run_r0 as base
import run_r0_schema as schema

OLD = base.ROOT / 'paper11'
OUT = base.STUDY / 'results/R0_amendment1'
SCRIPTS = OLD / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import nix_mapping
import run_m1 as m1


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def csv_rows(path, delimiter=','):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def preserve_inventory():
    return {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p)
            for directory in [base.OUT, schema.OUT, base.STUDY / 'results/R0_final']
            for p in sorted(directory.rglob('*')) if p.is_file()}


def register():
    target = OUT / 'registration.json'
    if target.exists():
        verify()
        return
    schema.verify()
    inputs = [Path(__file__), base.STUDY / 'tests/test_r0_amend1.py',
              base.STUDY / 'scripts/reproduce-r0-amend1.ps1', base.STUDY / 'protocol/r0_amendment1.json',
              OLD / 'data_manifest/M1/trial_splits.json', OLD / 'data_manifest/M1/acquisition_receipts.json',
              OLD / 'data_manifest/M1/split_lock.json', OLD / 'data_manifest/M2/features.json',
              OLD / 'data_manifest/M2/nix_objects.json', OLD / 'results/M1/unit_qc.csv',
              OLD / 'results/M1/session_qc.csv']
    inputs += [OLD / r['feature_path'] for r in load(OLD / 'data_manifest/M2/features.json')['files']]
    base.save(target, {'study': 'P11-v2', 'amendment': 'R0-TRIAL-1',
                      'registered_utc': datetime.now(timezone.utc).isoformat(),
                      'before_new_QC_value_access': True,
                      'authorization': load(base.STUDY / 'protocol/r0_amendment1.json')['authority'],
                      'input_sha256': {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p) for p in inputs},
                      'prior_failure_sha256': preserve_inventory(),
                      'external_final_lock_sha256': base.digest(schema.OUT / 'final_validation_lock.json'),
                      'base_commit': base.git('rev-parse', 'HEAD')}, immutable=True)
    print('R0-TRIAL-1 registered before fresh source QC.', flush=True)


def verify():
    schema.verify()
    r = load(OUT / 'registration.json')
    for rel, sha in {**r['input_sha256'], **r['prior_failure_sha256']}.items():
        if base.digest(base.ROOT / rel) != sha:
            raise RuntimeError(f'Frozen input/failure changed: {rel}')
    if base.digest(schema.OUT / 'final_validation_lock.json') != r['external_final_lock_sha256']:
        raise RuntimeError('External60/40lock changed')
    return r


def count_array(times):
    times = np.asarray(times)
    if times.ndim != 1 or times.dtype.kind not in 'fiu':
        raise ValueError('Non-numeric/rank1 spike array')
    if not np.isfinite(times).all() or np.any(times < -6) or np.any(times > 2):
        raise ValueError('Nonfinite/out-of-window allowed timestamp')
    if np.any(np.diff(times) < 0):
        raise ValueError('Nonmonotonic allowed timestamps')
    bins = np.zeros(60, dtype=np.int64)
    for value in times:
        d = Decimal(str(float(value)))
        if d < 0:
            bins[int((d + Decimal(6)) / Decimal('.1'))] += 1
    return bins


def admissible_unit(row):
    label = row['anatomical_location']
    region, hemisphere = m1.anatomy(label)
    finite = all(math.isfinite(float(row['macro_contact_mni_' + x])) for x in 'xyz')
    return region == 'hippocampus' and hemisphere in {'left', 'right'} and finite


def partition_arrays(arrays, unit_rows, partitions, reader=None):
    train, val, forbidden = map(set, (partitions['train'], partitions['validation'], partitions['test']))
    if train & val or forbidden & (train | val):
        raise ValueError('Train/development/forbidden overlap')
    allowed = train | val
    pattern = re.compile(r'Spike_Times_Unit_(\d+)_(u[A-Za-z]+)_(\d+)_Trial_(\d+)$')
    indexed = {}
    for group_key in arrays:
        group = arrays[group_key]
        name = group.attrs.get('name', group_key)
        name = name.decode() if isinstance(name, bytes) else str(name)
        match = pattern.fullmatch(name)
        if not match:
            continue
        uid, tid = int(match.group(1)), int(match.group(4))
        if tid not in allowed or uid not in unit_rows:
            continue  # Never dereference forbidden/other-region dataset values, length, rank or dtype.
        if match.group(2) + match.group(3) != unit_rows[uid]['microwire']:
            raise ValueError('Unit-microwire identity mismatch')
        key = (uid, tid)
        if key in indexed:
            raise ValueError('Duplicate allowed unit/trial array')
        unit = group.attrs.get('unit', '')
        if isinstance(unit, bytes):
            unit = unit.decode()
        if unit != 's':
            raise ValueError('Allowed spike timestamp clock is not seconds')
        indexed[key] = group
    read = reader or (lambda g: g['data'][...])
    train_counts, unit_qc, ledger = {}, [], []
    for uid in sorted(unit_rows):
        try:
            if any((uid, tid) not in indexed for tid in partitions['train']):
                raise ValueError('Missing training observation arrays, not zero firing')
            values = [count_array(read(indexed[uid, tid])) for tid in partitions['train']]
            ledger.extend({'unit': uid, 'trial': tid, 'partition': 'train'} for tid in partitions['train'])
            count = np.stack(values)
            total = int(count.sum())
            okay, reason = total >= 20, None if total >= 20 else 'training_spikes_below20'
            train_counts[uid] = count
        except ValueError as exc:
            total, okay, reason = None, False, str(exc)
        unit_qc.append({'unit_id': uid, 'anatomical_label': unit_rows[uid]['anatomical_location'],
                        'hemisphere': m1.anatomy(unit_rows[uid]['anatomical_location'])[1],
                        'training_spikes': total, 'admitted': okay, 'reason': reason,
                        'unit_type': 'SU_MU_NOT_DISTINGUISHED', 'observation_arrays_verified': True})
    selected = [q['unit_id'] for q in unit_qc if q['admitted']]
    train_values = np.stack([train_counts[u] for u in selected], axis=2) if selected else np.zeros((len(train), 60, 0), dtype=np.int64)
    validation_values = np.zeros((len(val), 60, len(selected)), dtype=np.int64)
    for j, uid in enumerate(selected):
        for i, tid in enumerate(partitions['validation']):
            if (uid, tid) not in indexed:
                raise ValueError('Missing frozen selected-unit development observation array')
            validation_values[i, :, j] = count_array(read(indexed[uid, tid]))
            ledger.append({'unit': uid, 'trial': tid, 'partition': 'validation'})
    return selected, train_values, validation_values, unit_qc, ledger


def session_QC(key, obj, receipts, splits):
    subject, session = key.split('/')
    stem = f'{subject}/{session}/ieeg/{subject}_{session}_task-verbalWM_'
    metadata_paths = [stem + x for x in ['units.tsv', 'trials.tsv', 'trialevents.tsv']]
    hashes = {}
    for rel in metadata_paths:
        path = OLD / 'raw/M1/nm000363' / rel
        expected = receipts['nm000363', rel]['sha256']
        if base.digest(path) != expected:
            raise ValueError('Primary metadata checksum mismatch')
        hashes[rel] = expected
    rows = csv_rows(OLD / 'raw/M1/nm000363' / (stem + 'units.tsv'), '\t')
    units = {int(r['unit_id']): r for r in rows if admissible_unit(r)}
    if len({int(r['unit_id']) for r in rows}) != len(rows):
        raise ValueError('Duplicate unit identity')
    # Companion mapping and trial/event identity are checksum-bound to the original metadata lock.
    original_qc = {int(r['unit_id']): r for r in csv_rows(OLD / 'results/M1/unit_qc.csv') if r['subject'] == subject and r['session'] == session}
    for uid, row in units.items():
        q = original_qc[uid]
        if q['region'] != 'hippocampus' or q['anatomical_label'] != row['anatomical_location'] or q['companion_electrode_mapping'] not in {'VERIFIED', 'UNPAIRED'}:
            raise ValueError('Anatomy/contact provenance mismatch')
    path = OLD / 'raw/NIX' / obj['filename']
    if base.digest(path) != obj['sha256'] or path.stat().st_size != obj['size']:
        raise ValueError('NIX source integrity mismatch')
    with h5py.File(path, 'r') as f:
        selected, train, val, unit_qc, ledger = partition_arrays(f['data'][path.stem]['data_arrays'], units, splits[key]['partitions'])
    record = next(x for x in load(OLD / 'data_manifest/M2/features.json')['files'] if x['session_key'] == key)
    old = load(OLD / record['feature_path'])
    if base.digest(OLD / record['feature_path']) != record['sha256']:
        raise ValueError('Archived train features corrupted')
    if old['trial_ids'] != splits[key]['partitions']['train']:
        raise ValueError('Archived train trial identity mismatch')
    common = sorted(set(selected) & set(old['unit_ids']))
    if not common or not np.array_equal(train[:, :, [selected.index(u) for u in common]], np.asarray(old['counts'])[:, :, [old['unit_ids'].index(u) for u in common]]):
        raise ValueError('Fresh common-unit NIX train reconstruction differs from pinned M2 counts')
    p = splits[key]['partitions']
    okay = len(p['train']) >= 24 and len(p['validation']) >= 8 and len(p['train']) + len(p['validation']) >= 32 and len(selected) >= 5
    meta = csv_rows(OLD / 'raw/M1/nm000363' / (stem + 'trials.tsv'), '\t')
    ids = [int(x['trial']) for x in meta]
    if ids != list(range(1, len(ids) + 1)) or not set(p['train'] + p['validation']) <= set(ids):
        raise ValueError('Incomplete/duplicate trial roster')
    causal = [{'trial': int(x['trial']), 'set_size': int(x['set_size'])} for x in meta if int(x['trial']) in set(p['train'] + p['validation'])]
    feature = {'session': key, 'subject': subject, 'unit_ids': selected, 'train_trial_ids': p['train'],
               'validation_trial_ids': p['validation'], 'training_counts': train.tolist(), 'validation_counts': val.tolist(),
               'causal_trial_metadata': causal, 'unit_QC': unit_qc,
               'old_test_values_accessed': False, 'external_values_accessed': False}
    featurepath = OUT / 'features' / (key.replace('/', '_') + '.json')
    base.save(featurepath, feature, immutable=True)
    result = {'session': key, 'subject': subject, 'admitted': okay, 'simultaneous_hippocampal_units': len(selected),
              'train_trials': len(p['train']), 'validation_trials': len(p['validation']),
              'usable_trials': len(p['train']) + len(p['validation']), 'training_spikes': int(train.sum()),
              'validation_spikes': int(val.sum()), 'train_unit_bins': int(train.size), 'validation_unit_bins': int(val.size),
              'training_min_spikes_per_unit': min(q['training_spikes'] for q in unit_qc if q['admitted']) if selected else 0,
              'feature_sha256': base.digest(featurepath), 'feature_path': str(featurepath.relative_to(base.STUDY)).replace('\\', '/'),
              'metadata_sha256': hashes, 'source_sha256': obj['sha256'], 'decoded_array_ledger': ledger,
              'nonhippocampal_units_excluded': len(rows) - len(units), 'unit_QC': unit_qc,
              'legacy_unit_mask_changed': selected != old['unit_ids'], 'common_legacy_units_verified': common,
              'alignment': splits[key]['alignment'], 'old_test_values_accessed': False,
              'observation_basis': 'Fresh allowed unit/trial array inventory; published8s window. No independent per-bin dropout masks.'}
    base.save(OUT / 'sessions' / (key.replace('/', '_') + '.json'), result, immutable=True)
    print(f"QC {key} units={len(selected)} train={len(train)} validation={len(val)} admitted={okay}", flush=True)
    return result


def sensitivity(records):
    return [{'usable_trial_minimum': t, 'simultaneous_unit_minimum': u,
             'subjects': len({r['subject'] for r in records if r.get('admitted') and r['usable_trials'] >= t and r['simultaneous_hippocampal_units'] >= u}),
             'sessions': sum(r.get('admitted', False) and r['usable_trials'] >= t and r['simultaneous_hippocampal_units'] >= u for r in records)}
            for t in [32, 36, 40] for u in [5, 10, 20]]


def run(replay=False):
    r = verify()
    mapping = nix_mapping.load()
    splits = load(OLD / 'data_manifest/M1/trial_splits.json')['sessions']
    receipts = {(x['dataset'], x['path']): x for x in load(OLD / 'data_manifest/M1/acquisition_receipts.json')['files']}
    lock = load(OLD / 'data_manifest/M1/split_lock.json')
    for name, expected in lock['metadata_sha256'].items():
        if base.digest(OLD / name) != expected:
            raise ValueError(f'Frozen metadata lock mismatch: {name}')
    records, failures = [], []
    for obj in mapping['objects']:
        key = obj['session_key']
        saved = OUT / 'sessions' / (key.replace('/', '_') + '.json')
        if replay and saved.exists():
            data = load(saved)
            if data.get('admitted') and base.digest(base.STUDY / data['feature_path']) != data['feature_sha256']:
                raise ValueError('Saved QC feature checksum mismatch')
            records.append(data)
            continue
        try:
            records.append(session_QC(key, obj, receipts, splits))
        except (ValueError, KeyError, OSError) as exc:
            failure = {'session': key, 'subject': key.split('/')[0], 'admitted': False, 'reason': str(exc)}
            records.append(failure)
            failures.append(failure)
            base.save(OUT / 'sessions' / (key.replace('/', '_') + '.json'), failure, immutable=True)
    passed = [x for x in records if x.get('admitted')]
    subjects = sorted({x['subject'] for x in passed})
    summary = [{'subject': s, 'sessions': [x['session'] for x in passed if x['subject'] == s],
                'sessions_n': sum(x['subject'] == s for x in passed),
                'simultaneous_units_by_session': {x['session']: x['simultaneous_hippocampal_units'] for x in passed if x['subject'] == s},
                'session_local_units_sum_not_unique_neurons': sum(x['simultaneous_hippocampal_units'] for x in passed if x['subject'] == s),
                'training_trials': sum(x['train_trials'] for x in passed if x['subject'] == s),
                'validation_trials': sum(x['validation_trials'] for x in passed if x['subject'] == s)} for s in subjects]
    base.save(OUT / 'cohort.json', {'subjects': summary, 'sessions': records, 'failures': failures,
              'sensitivity': sensitivity(records), 'leave_one_out_subject_count': max(len(subjects) - 1, 0),
              'sign_flip_minimum_two_sided_p': {str(n): 2 / 2**n for n in [6, 7, 8, 9]},
              'predictive_effects_or_power': 'NOT_EVALUATED'}, immutable=True)
    for name, rows in [('subject_table.csv', summary), ('session_table.csv', [{k: x.get(k) for k in ['session', 'subject', 'admitted', 'simultaneous_hippocampal_units', 'train_trials', 'validation_trials', 'usable_trials', 'training_spikes', 'validation_spikes', 'train_unit_bins', 'validation_unit_bins', 'reason']} for x in records])]:
        with (OUT / name).open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(base.STUDY / 'tests'), '-p', 'test_r0_amend1.py', '-v'], capture_output=True, text=True)
    (OUT / 'tests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    ext = load(schema.OUT / 'gate_result.json')
    enough = len(subjects) >= 8
    okay = enough and tests.returncode == 0 and not failures and ext['gate_verdict'] == 'PASS'
    result = {'study': 'P11-v2', 'milestone': 'R0', 'amendment': 'R0-TRIAL-1', 'gate_verdict': 'PASS' if okay else 'FAIL',
              'scientific_verdict': 'NOT_EVALUATED' if enough else 'DATA_INSUFFICIENT',
              'qualified_subjects': len(subjects), 'subject_ids': subjects, 'qualified_sessions': len(passed),
              'session_local_units_sum': sum(x['simultaneous_hippocampal_units'] for x in passed),
              'training_trials': sum(x['train_trials'] for x in passed), 'validation_trials': sum(x['validation_trials'] for x in passed),
              'training_spikes': sum(x['training_spikes'] for x in passed), 'validation_spikes': sum(x['validation_spikes'] for x in passed),
              'failures': failures, 'tests_exit_code': tests.returncode, 'old_test_values_accessed': False,
              'external_final_values_accessed': False, 'external_final_lock_unchanged': True,
              'original40_failure_unchanged': True, 'v1_failures_unchanged': True,
              'replay_saved_outputs_only': replay, 'registered_source_sha256': r['input_sha256'],
              'R1_authorized': okay, 'further_lowering_authorized': False, 'model_regime_preference': 'NOT_EVALUATED'}
    verify()
    target = 'replay_gate_result.json' if replay else 'gate_result.json'
    base.save(OUT / target, result, immutable=not replay)
    base.save(OUT / ('replay_QC.json' if replay else 'QC.json'), result, immutable=not replay)
    artifactpath = OUT / 'artifact_lock.json'
    if not replay:
        base.save(artifactpath, {'sha256': {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p) for p in OUT.rglob('*') if p.is_file() and p.name not in {'artifact_lock.json', 'tests.txt'}}}, immutable=True)
    else:
        for name, sha in load(artifactpath)['sha256'].items():
            if base.digest(base.ROOT / name) != sha:
                raise ValueError('Original amended QC artifact changed')
    print(json.dumps(result, indent=2), flush=True)
    return 0 if okay else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register', 'run', 'replay', 'verify'])
    a = parser.parse_args().action
    OUT.mkdir(parents=True, exist_ok=True)
    if a == 'register':
        register()
    elif a == 'verify':
        verify()
        print('All original failures, sources and60/40split remain unchanged.')
    else:
        sys.exit(run(replay=a == 'replay'))
