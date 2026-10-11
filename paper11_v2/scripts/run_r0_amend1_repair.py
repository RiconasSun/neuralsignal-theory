"""Registered audit repair: complete decode ledger and strictly offline replay."""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import run_r0_amend1 as old

ORIGINAL_OUT = old.OUT
OUT = old.base.STUDY / 'results/R0_amendment1_code1'
ORIGINAL_PARTITION_ARRAYS = old.partition_arrays


def traced_partition_arrays(arrays, unit_rows, partitions, reader=None):
    ledger = []
    allowed = set(partitions['train']) | set(partitions['validation'])
    forbidden = set(partitions['test'])
    def guarded_read(group):
        name = group.attrs.get('name', group.name.rsplit('/', 1)[-1])
        name = name.decode() if isinstance(name, bytes) else str(name)
        match = re.fullmatch(r'Spike_Times_Unit_(\d+)_(u[A-Za-z]+)_(\d+)_Trial_(\d+)', name)
        if not match:
            raise ValueError('Unbound decode name')
        uid, tid = int(match.group(1)), int(match.group(4))
        if tid not in allowed or tid in forbidden or uid not in unit_rows:
            raise ValueError('Forbidden array dereference blocked')
        entry = {'unit': uid, 'trial': tid, 'partition': 'train' if tid in partitions['train'] else 'validation',
                 'source_array': name, 'decode_attempted': True, 'decode_completed': False}
        ledger.append(entry)
        value = reader(group) if reader else group['data'][...]
        entry['decode_completed'] = True
        return value
    selected, train, val, qc, _ = ORIGINAL_PARTITION_ARRAYS(arrays, unit_rows, partitions, guarded_read)
    return selected, train, val, qc, ledger


def preflight_saved(required_paths, artifact_hashes, exists=None, digest=None):
    exists = exists or (lambda p: Path(p).is_file())
    digest = digest or old.base.digest
    for path in required_paths:
        if not exists(path):
            raise ValueError(f'Saved-only replay missing artifact; no raw fallback: {path}')
    for path, sha in artifact_hashes.items():
        if not exists(path) or digest(path) != sha:
            raise ValueError(f'Saved-only replay corrupt artifact; no raw fallback: {path}')


def register():
    old.verify()
    target = OUT / 'registration.json'
    if target.exists():
        old.OUT = OUT
        old.verify()
        return
    obj = old.load(ORIGINAL_OUT / 'registration.json')
    sources = [Path(__file__), old.base.STUDY / 'tests/test_r0_amend1_repair.py',
               old.base.STUDY / 'scripts/reproduce-r0-amend1-code1.ps1']
    obj['input_sha256'].update({str(p.relative_to(old.base.ROOT)).replace('\\', '/'): old.base.digest(p) for p in sources})
    obj['prior_failure_sha256'].update({str(p.relative_to(old.base.ROOT)).replace('\\', '/'): old.base.digest(p) for p in ORIGINAL_OUT.rglob('*') if p.is_file()})
    obj.update({'registered_utc': datetime.now(timezone.utc).isoformat(), 'code_repair': 'R0-TRIAL-1-CODE-1',
                'reason': 'Independent review found omitted decode entries for rejected units and unsafe saved-only missing-file fallthrough. No oldtest/external read occurred in completed runs.',
                'original_QC_preserved': True, 'unit_or_trial_criteria_changed': False,
                'complete_ledger_policy': 'Record every allowed dereference before reading data, including units later excluded and unsuccessful reads.',
                'replay_policy': 'Verify complete session/feature roster and all original artifact hashes first, then prohibit all fresh session_QC calls.',
                'before_repaired_QC': True})
    old.base.save(target, obj, immutable=True)
    print('Registered R0-TRIAL-1-CODE-1; original unit masks and thresholds unchanged.')


def run(replay=False):
    old.OUT = OUT
    old.verify()
    mapping = old.nix_mapping.load()
    if replay:
        lock = old.load(OUT / 'artifact_lock.json')['sha256']
        paths = [OUT / 'sessions' / (o['session_key'].replace('/', '_') + '.json') for o in mapping['objects']]
        preflight_saved(paths, {old.base.ROOT / rel: sha for rel, sha in lock.items()})
        def no_fresh_QC(*args, **kwargs):
            raise RuntimeError('Saved-only replay attempted raw QC; prohibited')
        old.session_QC = no_fresh_QC
    old.partition_arrays = traced_partition_arrays
    result = old.run(replay=replay)
    if not replay:
        original = old.load(ORIGINAL_OUT / 'gate_result.json')
        new = old.load(OUT / 'gate_result.json')
        for key in ['qualified_subjects', 'qualified_sessions', 'session_local_units_sum', 'training_trials', 'validation_trials', 'training_spikes', 'validation_spikes']:
            if new[key] != original[key]:
                raise ValueError(f'Audit-only repair changed scientific admission: {key}')
        for obj in mapping['objects']:
            filename = obj['session_key'].replace('/', '_') + '.json'
            a, b = old.load(ORIGINAL_OUT / 'features' / filename), old.load(OUT / 'features' / filename)
            if a != b:
                raise ValueError('Audit-only repair changed unit mask/count data')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register', 'run', 'replay', 'verify'])
    action = parser.parse_args().action
    OUT.mkdir(parents=True, exist_ok=True)
    if action == 'register':
        register()
    elif action == 'verify':
        old.OUT = OUT
        old.verify()
        print('Preserved failures, repaired sources and immutable final split verified.')
    else:
        sys.exit(run(replay=action == 'replay'))
