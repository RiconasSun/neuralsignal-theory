"""Uniform saved inventory QC, without reading event/neural data contents."""
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

from audit import classify_file, verdict, verify_implementation
from register import HERE, OUT, ROOT, read, save, sha


def file_rows(items):
    return [dict(id=x['id'], **x['attributes']) for x in items
            if x.get('type') == 'files' and x.get('attributes', {}).get('kind') == 'file']


def metadata_sessions(files):
    sessions = defaultdict(list)
    for row in files:
        path = row['materialized_path']
        if path.startswith('/Events Files/') and row['name'].lower().endswith(('.mat', '.txt')):
            stem = row['name'].rsplit('.', 1)[0]
            sessions[stem].append(row['id'])
    result = []
    for label, ids in sorted(sessions.items()):
        match = re.match(r'^(BJH\d+|UIC\d+|p\d+WV)_', label, re.I)
        result.append({'session_file_label': label, 'patient_file_label': match.group(1) if match else 'UNKNOWN',
                       'event_file_ids': ids, 'valid_trials': None, 'hippocampal_units': None,
                       'native_boundaries': 'UNKNOWN', 'gap_coverage': 'UNKNOWN',
                       'event_neural_map': 'UNKNOWN', 'eligible': 'UNKNOWN',
                       'filename_is_not_private_patient_identity': True})
    return result


def primary():
    verify_implementation()
    inventory = read(OUT / 'osf_complete/inventory.json')
    files = file_rows(inventory['items'])
    sessions = metadata_sessions(files)
    patients = defaultdict(list)
    for row in sessions:
        patients[row['patient_file_label']].append(row['session_file_label'])
    qc = {'mission': 'P11-ALT-COHORT-AUDIT-1', 'candidate': 'OSF:vh5kq',
          'complete_inventory': inventory['complete_inventory'],
          'pinned_version': all(x.get('current_version') is not None and
                                x.get('extra', {}).get('hashes', {}).get('sha256') for x in files),
          'pin_scope': 'Provider per-file version/checksum inventory snapshot, not an immutable project release or full-byte verification',
          'license_established': read(OUT / 'documents/000.receipt')['data']['attributes']['name'] == 'CC0 1.0 Universal',
          'canonical_patient_mapping': False, 'independence_supported': True,
          'independence_scope': 'Published source-site cohort distinct from primary Zurich; no private cross-cohort identity audit',
          'native_recording_support': False, 'gaps_verified': False, 'clock_mapping_verified': False,
          'authoritative_incompatibility': False, 'cohort_eligibility_complete': False,
          'documented_eligible_patients': 0, 'zero_is_certified_count_not_actual_ineligible_count': True,
          'published_patient_potential': 16, 'observed_patient_file_labels': sorted(patients),
          'observed_session_file_labels': len(sessions), 'files': len(files),
          'files_with_provider_sha256': sum(bool(x.get('extra', {}).get('hashes', {}).get('sha256')) for x in files),
          'file_extension_counts': dict(Counter(x['name'].rsplit('.', 1)[-1].lower() for x in files)),
          'native_raw_file_candidates': [x['materialized_path'] for x in files if x['name'].lower().endswith(('.ncs', '.nev', '.ns1', '.ns2', '.ns3', '.ns4', '.ns5', '.ns6'))],
          'metadata_document_candidates': [x['materialized_path'] for x in files if classify_file(x['name']) == 'DOCUMENT_CANDIDATE_REQUIRES_ACCESS_PLAN'],
          'candidate_spike_values_accessed': False, 'candidate_outcome_values_accessed': False,
          'models_fitted': 0, 'original_holdouts_unchanged': True,
          'missing_evidence': ['session-to-patient author mapping and published/inventory denominator reconciliation',
             'per-session hippocampus-only simultaneous unit dictionary', 'actual valid trial coverage without outcome filtering',
             'raw acquisition headers/start/end/gap/valid-sample manifests', 'event-to-neural clock mapping and synchronization evidence',
             'training spike adequacy deliberately not examined']}
    save(OUT / 'QC.json', qc)
    save(OUT / 'patient_QC.json', [{'patient_file_label': p, 'session_labels': labels,
        'session_count': len(labels), 'hippocampal_units': None, 'valid_trials': None,
        'eligible': 'UNKNOWN', 'excluded': False} for p, labels in sorted(patients.items())])
    save(OUT / 'session_QC.json', sessions)
    with (OUT / 'file_inventory.csv').open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['id', 'path', 'bytes', 'current_version', 'modified', 'provider_sha256', 'access'])
        writer.writeheader()
        for row in sorted(files, key=lambda r: r['materialized_path']):
            writer.writerow(dict(id=row['id'], path=row['materialized_path'], bytes=row['size'],
                current_version=row['current_version'], modified=row['date_modified'],
                provider_sha256=row.get('extra', {}).get('hashes', {}).get('sha256'), access=classify_file(row['name'])))
    save(OUT / 'gate_result.json', {'mission': qc['mission'], 'scientific_verdict': verdict(qc),
        'evaluated_utc': datetime.now(timezone.utc).isoformat(), 'QC_sha256': sha(OUT / 'QC.json'),
        'original_R2_verdict': 'FAIL', 'new_validation_arm_admitted': False,
        'eligible_patient_count_established': False,
        'stop': True, 'next_allowed': 'Figshare documentation/inventory assessment only; no fitting or final validation'})
    print('Primary gate:', verdict(qc), 'files:', len(files), 'sessions:', len(sessions), 'patient labels:', len(patients))


if __name__ == '__main__':
    primary()
