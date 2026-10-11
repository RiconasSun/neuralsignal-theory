"""M2 training-only count extraction; validation/test timestamps stay opaque."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

import run_m1 as m1
import audit_nix_coverage as coverage

PAPER = m1.PAPER
RESULTS = PAPER / 'results' / 'M2'
MANIFEST = PAPER / 'data_manifest' / 'M2'
FEATURES = RESULTS / 'features'
M1_OUTPUTS = {'results/M1/unit_qc.csv', 'results/M1/session_qc.csv', 'results/M1/qc_report.json',
              'results/M1/gate_result.json', 'data_manifest/M1/split_lock.json',
              'data_manifest/M1/repository_trees/nm000363.json', 'data_manifest/M1/repository_trees/ds004752.json',
              'data_manifest/M1/acquisition_receipts.json'}


def require_hash(path, expected):
    if m1.digest(path) != expected:
        raise ValueError(f'Input identity mismatch: {path.relative_to(PAPER)}')


def verify_accepted_output(name, expected, commit):
    authoritative = subprocess.check_output(['git', 'show', commit + ':paper11/' + name], cwd=m1.ROOT)
    if m1.blob_sha(authoritative) != m1.blob_sha((PAPER / name).read_bytes()):
        raise ValueError('M1 output differs from accepted commit')
    require_hash(PAPER / name, expected)


def prerequisite():
    m1.prerequisite()
    gate = m1.m0.load(m1.RESULTS / 'gate_result.json')
    if gate['gate'] != 'PASS' or gate['tests_exit_code'] != 0:
        raise ValueError('M1 must pass before M2')
    for name, expected in gate['source_sha256'].items():
        require_hash(PAPER / name, expected)
    require_hash(m1.SPLIT, gate['split_sha256'])
    lock = m1.m0.load(m1.SPLIT_LOCK)
    require_hash(m1.SPLIT, lock['split_sha256'])
    for name, expected in lock['metadata_sha256'].items():
        require_hash(PAPER / name, expected)
    for receipt in m1.m0.load(m1.RECEIPTS)['files']:
        require_hash(m1.DATA / receipt['dataset'] / receipt['path'], receipt['sha256'])
    accepted = m1.m0.load(MANIFEST / 'accepted_m1_outputs.json')
    if accepted['accepted_m1_commit'] != '9145c407cf383226f111752d6299c4b5c0a98303':
        raise ValueError('Unrecognized accepted M1 commit')
    if set(accepted['sha256']) != M1_OUTPUTS:
        raise ValueError('Accepted M1 manifest missing required output entries')
    for name, expected in accepted['sha256'].items():
        verify_accepted_output(name, expected, accepted['accepted_m1_commit'])
    return gate


def bin_index(text):
    try:
        time = Decimal(text)
    except InvalidOperation as error:
        raise ValueError('Invalid training timestamp') from error
    if not time.is_finite() or not Decimal('-6') <= time <= Decimal('2'):
        raise ValueError('Invalid training timestamp/window')
    if time >= 0:
        return None
    return int((time + Decimal('6')) / Decimal('0.1'))


def extract(path, trial_ids, unit_ids):
    trial_lookup = {tid: index for index, tid in enumerate(trial_ids)}
    unit_lookup = {uid: index for index, uid in enumerate(unit_ids)}
    counts = [[[0 for _ in unit_ids] for _ in range(60)] for _ in trial_ids]
    with path.open(encoding='utf-8-sig', newline=None) as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        if reader.fieldnames != ['unit_id', 'trial', 'spike_time']:
            raise ValueError('Unexpected spike schema')
        for row in reader:
            tid = m1.integer(row['trial'])
            if tid not in trial_lookup:
                continue  # Do not decode heldout unit identity or timestamp.
            uid = m1.integer(row['unit_id'])
            if uid not in unit_lookup:
                continue
            index = bin_index(row['spike_time'])
            if index is not None:
                counts[trial_lookup[tid]][index][unit_lookup[uid]] += 1
    return counts


def causal_metadata(tid, set_size):
    # The stimulus reveals memory load at encoding, not during fixation.
    return {'trial': tid, 'bins': [
        {'bin': b, 'onset_seconds': str(Decimal('-6') + Decimal(b) / 10),
         'exposure_seconds': '0.1', 'phase': 'fixation' if b < 10 else 'encoding' if b < 30 else 'maintenance',
         'known_set_size': 0 if b < 10 else set_size, 'history_reset': b == 0}
        for b in range(60)]}


def check_roster(trial_rows):
    ids = sorted(m1.integer(row['trial']) for row in trial_rows)
    if ids != list(range(1, len(ids) + 1)):
        raise ValueError('Missing, duplicate or invalid trial identity')


def selection():
    units = m1.rows(m1.RESULTS / 'unit_qc.csv')
    sessions = m1.rows(m1.RESULTS / 'session_qc.csv')
    selected = {}
    for session in sessions:
        if session['eligible'] != 'True':
            continue
        key = session['subject'] + '/' + session['session']
        selected[key] = sorted((row for row in units if row['subject'] + '/' + row['session'] == key
                               and row['primary_analysis_eligible'] == 'True'), key=lambda row: int(row['unit_id']))
        if len(selected[key]) != int(session['eligible_hippocampal_units']):
            raise ValueError('Primary selection differs from M1')
    return selected


def source_audit():
    tree = m1.m0.load(m1.MANIFEST / 'repository_trees' / 'nm000363.json')['response']['tree']
    blobs = {item['path']: item['sha'] for item in tree}
    source = MANIFEST / 'source_audit' / 'laneA_convert_ieeg016.py'
    if not source.exists() or m1.blob_sha(source.read_bytes()) != blobs['code/' + source.name]:
        raise ValueError('Pinned coverage converter audit source absent or mismatched')
    # This source records array existence before iterating its spike content.
    text = source.read_text(encoding='utf-8')
    marker = "d.setdefault('trials_present', set()).add(tr)"
    if marker not in text or text.index(marker) >= text.index("v = da[k]['data'][()]"):
        raise ValueError('Empty-array observation provenance not established')
    return {'source_sha256': m1.digest(source), 'git_blob_sha1': blobs['code/' + source.name],
            'evidence': 'distinct trial-array existence recorded before spike iteration; empty arrays included',
            'limitation': 'derivative reports count of trial arrays, not per-bin acquisition dropout masks; conditional on published complete trial coverage',
            'independent_nix_array_roster_verified': False}


def session_features(key, units, split):
    subject, session = key.split('/')
    stem = m1.DATA / 'nm000363' / subject / session / 'ieeg' / f'{subject}_{session}_task-verbalWM_'
    trial_rows = m1.rows(Path(str(stem) + 'trials.tsv'))
    check_roster(trial_rows)
    trial_lookup = {int(row['trial']): row for row in trial_rows}
    ids = split['partitions']['train']
    unit_ids = [int(unit['unit_id']) for unit in units]
    if not ids or any(unit['full_observation_array_coverage'] != 'True' for unit in units):
        raise ValueError('Training observation coverage unresolved')
    counts = extract(Path(str(stem) + 'spikes.tsv'), ids, unit_ids)
    totals = [sum(bin_counts[u] for trial in counts for bin_counts in trial) for u in range(len(units))]
    expected = [int(unit['training_preprobe_spikes']) for unit in units]
    if totals != expected:
        raise ValueError('Binned counts do not conserve M1 training spikes')
    result = {'dataset': 'nm000363', 'subject': subject, 'session': session, 'partition': 'train',
              'unit_ids': unit_ids, 'trial_ids': ids, 'count_shape': [len(ids), 60, len(units)],
              'counts': counts, 'exposure_seconds': '0.1', 'observed_mask': 'all bins conditional on published full array coverage',
              'units': [{field: unit[field] for field in ('unit_id', 'hemisphere', 'macro_contact', 'unit_type')} for unit in units],
              'causal_metadata': [causal_metadata(tid, int(trial_lookup[tid]['set_size'])) for tid in ids],
              'validation_test_timestamps_parsed': False}
    file = FEATURES / f'{subject}_{session}_train.json'
    m1.write_json(file, result)
    flat = [value for trial in counts for bin_counts in trial for value in bin_counts]
    return {'session_key': key, 'trials': len(ids), 'units': len(units), 'observed_unit_bins': len(flat),
            'spikes': sum(flat), 'zero_bins': flat.count(0), 'max_count': max(flat),
            'feature_path': file.relative_to(PAPER).as_posix(), 'sha256': m1.digest(file)}


def pipeline():
    prerequisite()
    audit = source_audit()
    selected = selection()
    splits = m1.m0.load(m1.SPLIT)['sessions']
    for path in (m1.DATA / 'nm000363').rglob('*_trials.tsv'):
        check_roster(m1.rows(path))
    keys = sorted(selected)
    cohort = keys[:1]
    groups = [('smoke', cohort), ('small_cohort', [key for key in keys if key.split('/')[0] in ('sub-01', 'sub-02')]), ('full_cohort', keys)]
    stages, records = [], {}
    for stage, stage_keys in groups:
        for key in stage_keys:
            records[key] = session_features(key, selected[key], splits[key])
        stages.append({'stage': stage, 'sessions': len(stage_keys), 'subjects': len({key.split('/')[0] for key in stage_keys}),
                       'spikes': sum(records[key]['spikes'] for key in stage_keys)})
        print(json.dumps(stages[-1]), flush=True)
    prerequisite()
    records = [records[key] for key in keys]
    bins = sum(row['observed_unit_bins'] for row in records)
    qc = {'subjects': len({key.split('/')[0] for key in keys}), 'sessions': len(keys),
          'session_local_units': sum(row['units'] for row in records), 'training_trials': sum(row['trials'] for row in records),
          'observed_unit_bins': bins, 'training_spikes': sum(row['spikes'] for row in records),
          'zero_bin_fraction': sum(row['zero_bins'] for row in records) / bins,
          'primary_bin_ms': 100, 'bin_width_decision': 'RETAIN_FROZEN_100MS',
          'feasibility': 'count extraction/conservation passed; exposure conditional on array coverage; convergence NOT_ASSESSED_M4',
          'validation_test_timestamps_parsed': False, 'progressive_stages': stages, 'coverage_provenance': audit}
    m1.write_json(RESULTS / 'qc_report.json', qc)
    inputs = [m1.SPLIT, m1.SPLIT_LOCK, m1.RECEIPTS, m1.RESULTS / 'unit_qc.csv', m1.RESULTS / 'session_qc.csv']
    m1.write_json(MANIFEST / 'features.json', {'partition': 'train', 'files': records, 'inputs_sha256': {p.relative_to(PAPER).as_posix(): m1.digest(p) for p in inputs}})
    coverage_report = coverage.audit_all(selected, splits)
    qc['coverage_verified_sessions'] = coverage_report['sessions_verified']
    qc['coverage_provenance']['exact_pinned_nix_array_roster_verified'] = True
    qc['coverage_provenance']['independent_original_vs_masked_array_values_compared'] = False
    m1.write_json(RESULTS / 'qc_report.json', qc)
    return qc


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    started, errors, qc, missing_coverage = m1.now(), [], {}, False
    try:
        qc = pipeline()
    except coverage.CoverageUnavailable as error:
        errors.append(str(error))
        missing_coverage = True
        qc = m1.m0.load(RESULTS / 'qc_report.json')
    except (ValueError, OSError, KeyError) as error:
        errors.append(str(error))
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(PAPER / 'tests'), '-p', 'test_m2.py', '-v'], capture_output=True, text=True)
    (RESULTS / 'tests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    if tests.returncode:
        errors.append('Automated tests failed')
    gate = {'milestone': 'M2', 'gate': 'FAIL' if errors else 'PASS', 'errors': errors, 'tests_exit_code': tests.returncode,
            'preceding_gates': {'M0': 'PASS', 'M1': 'PASS'}, 'started_at_utc': started, 'finished_at_utc': m1.now(),
            'candidate_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=m1.ROOT, capture_output=True, text=True).stdout.strip(),
            'source_sha256': {name: m1.digest(PAPER / name) for name in ('scripts/run_m2.py', 'tests/test_m2.py', 'scripts/reproduce-m2.ps1', 'REPRODUCE_M2.md')},
            'split_sha256': m1.digest(m1.SPLIT), 'm0_freeze_sha256': m1.digest(m1.m0.LOCK),
            'scientific_verdict': 'NOT_EVALUATED', 'holdout_count_access': False, 'next_milestone_executed': False}
    gate['execution_status'] = 'NEED_ENV' if missing_coverage and not tests.returncode else gate['gate']
    gate['failure_class'] = 'OBSERVATION_COVERAGE_UNVERIFIED' if missing_coverage else None
    gate['source_sha256']['scripts/audit_nix_coverage.py'] = m1.digest(PAPER / 'scripts' / 'audit_nix_coverage.py')
    gate['source_sha256']['scripts/plot_m2_qc.py'] = m1.digest(PAPER / 'scripts' / 'plot_m2_qc.py')
    for name in ('scripts/nix_mapping.py', 'scripts/acquire_nix_coverage.py', 'scripts/probe_coverage_access.py'):
        gate['source_sha256'][name] = m1.digest(PAPER / name)
    gate['input_manifest_sha256'] = {name: m1.digest(MANIFEST / name) for name in ('features.json', 'accepted_m1_outputs.json', 'nix_objects.json') if (MANIFEST / name).exists()}
    m1.write_json(RESULTS / 'gate_result.json', gate)
    m1.write_json(RESULTS / 'claim_audit.json', {'supported': ['Training-only spike counts generated with conserved counts'] if not errors else [],
                 'unsupported': ['Preferred dynamical regime', 'NAP validated', 'CWP validated', 'model convergence', 'verified per-unit trial coverage', 'independent per-bin acquisition coverage'],
                 'scientific_verdict': 'NOT_EVALUATED', 'errors': errors})
    (RESULTS / 'DERIVED_DATA_LICENSE.txt').write_bytes((m1.RESULTS / 'DERIVED_DATA_LICENSE.txt').read_bytes())
    print(json.dumps({'gate': gate['gate'], 'qc': qc, 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
