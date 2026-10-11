"""Audit local checksum-bound NIX array names/schema, never signal values."""
from collections import Counter
from pathlib import Path
import re

import run_m1 as m1
import nix_mapping

RAW = m1.PAPER / 'raw' / 'NIX'


class CoverageUnavailable(RuntimeError):
    pass


def validate_inventory(records, unit_ids, trial_ids, microwires):
    expected = {(unit, trial) for unit in unit_ids for trial in trial_ids}
    counts = Counter((record['unit'], record['trial']) for record in records)
    if set(counts) != expected or any(value != 1 for value in counts.values()):
        raise ValueError('NIX coverage has missing, duplicate or extraneous arrays')
    for record in records:
        if record['microwire'] != microwires[record['unit']] or record['rank'] != 1:
            raise ValueError('NIX coverage identity or schema mismatch')
        if record['dtype_kind'] not in 'fiu' or record['time_unit'] != 's':
            raise ValueError('NIX timestamps must have numeric seconds schema')


def audit_session(key, unit_ids, trial_ids):
    import h5py
    subject, session = key.split('/')
    directory = m1.DATA / 'nm000363' / subject
    session_row = next(row for row in m1.rows(directory / f'{subject}_sessions.tsv') if row['session_id'] == session)
    path = RAW / session_row['nix_source_file']
    if not path.exists():
        raise CoverageUnavailable(f'Missing checksum-bound original NIX coverage source: {path.name}')
    mapping_path = m1.PAPER / 'data_manifest/M2/nix_objects.json'
    mapping = nix_mapping.load() if mapping_path.exists() else {'objects': []}
    source_object = next((obj for obj in mapping['objects'] if obj['session_key'] == key), None)
    expected_sha = source_object['sha256'] if source_object else session_row['nix_source_sha256']
    if source_object and source_object['original_sha256'] != session_row['nix_source_sha256']:
        raise ValueError('Original NIX source identity disagrees with primary masked-object mapping')
    if m1.digest(path) != expected_sha:
        raise ValueError('NIX checksum mismatch; no unbound source substitution')
    unit_path = directory / session / 'ieeg' / f'{subject}_{session}_task-verbalWM_units.tsv'
    microwires = {int(row['unit_id']): row['microwire'] for row in m1.rows(unit_path)}
    records = []
    pattern = re.compile(r'Spike_Times_Unit_(\d+)_(u[A-Za-z]+)_(\d+)_Trial_(\d+)$')
    with h5py.File(path, 'r') as handle:
        arrays = handle['data'][path.stem]['data_arrays']
        for group_key in arrays:
            group = arrays[group_key]
            name = group.attrs.get('name', group_key)
            name = name.decode() if isinstance(name, bytes) else str(name)
            match = pattern.fullmatch(name)
            if not match or int(match.group(1)) not in unit_ids:
                continue
            data = group['data']
            unit = group.attrs.get('unit', '')
            unit = unit.decode() if isinstance(unit, bytes) else str(unit)
            records.append({'unit': int(match.group(1)), 'trial': int(match.group(4)),
                            'microwire': match.group(2) + match.group(3),
                            'rank': data.ndim, 'dtype_kind': data.dtype.kind, 'time_unit': unit})
            # Never call data[()], inspect array lengths, or load any spike value.
    validate_inventory(records, unit_ids, trial_ids, microwires)
    return {'session': key, 'nix_sha256': expected_sha, 'inventory': records,
            'original_nix_sha256': session_row['nix_source_sha256'], 'masked_source': source_object is not None,
            'timestamp_values_read': False, 'array_lengths_exported': False,
            'exposure_basis': 'published eight-second trial convention; no independent dropout masks'}


def audit_all(selected, splits):
    records = []
    missing = []
    for key, units in sorted(selected.items()):
        try:
            records.append(audit_session(key, [int(row['unit_id']) for row in units],
                                         sorted(splits[key]['valid_trials'] + [row['trial'] for row in splits[key]['excluded_trials']])))
        except CoverageUnavailable as error:
            missing.append(str(error))
    report = {'gate': 'NEED_ENV' if missing else 'PASS', 'sessions_verified': len(records),
              'sessions_required': len(selected), 'missing': missing, 'records': records,
              'heldout_timestamp_values_read': False}
    m1.write_json(m1.PAPER / 'results' / 'M2' / 'coverage_audit.json', report)
    if missing:
        raise CoverageUnavailable(f'{len(missing)} required NIX coverage inventories unavailable; no scientific M2 PASS')
    return report
