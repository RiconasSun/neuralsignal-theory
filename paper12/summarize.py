"""Generate fail-closed M0 QC and primary admission before the alternative audit."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from audit import HERE, main as audit_allen, table, write_csv
from register import verify, sha

def summarize(output=None):
    verify()
    output = Path(output) if output else HERE / 'results'
    coverage = audit_allen(output)
    records = [json.loads(p.read_text()) for p in sorted((HERE / 'metadata/headers_code1').glob('*.json'))]
    expected = {r['id'] for r in table('sessions')}
    if {r['session_id'] for r in records} != expected:
        raise RuntimeError('Do not gate an incomplete header denominator')
    errors = {r['session_id']: r['error'] for r in records if 'error' in r}
    summary = {'session_headers': len(records), 'errors': errors,
               'recording_support_verified_sessions': 0,
               'timestamp_origins_available': sum('/session_start_time' in r for r in records),
               'interval_tables': dict(Counter(name for r in records for name in r['intervals'])),
               'metadata_transport_bytes': sum(r.get('transport_bytes', 0) for r in records),
               'native_neural_acquisition_names_present': sum(any('electrical' in name.lower() for name in r.get('acquisition_names_only', [])) for r in records),
               'invalid_times_tables_available': sum('invalid_times' in r['intervals'] for r in records),
               'decoded_neural_values': False}
    trial_rows = []
    for r in records:
        for stimulus, interval in r['intervals'].items():
            if 'start_time' in interval and 'stop_time' in interval:
                a, b = interval['start_time'], interval['stop_time']
                trial_rows.append({'session_id': r['session_id'], 'interval_table': stimulus,
                                   'starts': a['n'], 'stops': b['n'], 'finite_starts': a['finite'],
                                   'finite_stops': b['finite'], 'first_start_seconds': a['min'],
                                   'last_stop_seconds': b['max'],
                                   'repeat_identity': 'NOT_DECODED', 'native_recording_support': 'UNKNOWN'})
    if trial_rows: write_csv(output / 'allen_stimulus_intervals.csv', trial_rows)
    raw = json.loads((HERE / 'metadata/allen_raw_inventory.json').read_text())
    if {r['session_id'] for r in raw} != expected: raise RuntimeError('Incomplete raw object inventory')
    summary['raw_object_count'] = sum(len(r['objects']) for r in raw)
    summary['standalone_recording_parameter_sidecars'] = sum(
        o['key'].endswith(('.meta', '.oebin', 'params.json', 'settings.xml')) for r in raw for o in r['objects'])
    summary['digital_sync_files_available'] = sum(any(o['key'].endswith('/sync.h5') for o in r['objects']) for r in raw)
    summary['continuous_signal_objects_opened'] = 0
    (output / 'allen_support_qc.json').write_text(json.dumps(summary, indent=2, sort_keys=True))
    reason = ['Native probe-specific recording origin/end/gap support has not been independently established.',
              'Stimulus timestamps and documented common-clock alignment are not proof of complete raw neural support.',
              'Anatomical labels are atlas registrations; per-probe independent localization was not inspected.',
              'Repeat identities and per-session behavioral missingness remain unverified.',
              'Mutable API metadata and NWB last-modified IDs are not a full immutable physiological manifest.']
    original_gate_path = HERE / 'results/allen_gate_result.json'
    if original_gate_path.exists():
        names = json.loads(original_gate_path.read_text())['input_sha256']
        inputs = {name: sha(HERE/name) for name in names}
    else:
        inputs = {p.relative_to(HERE).as_posix(): sha(p) for p in sorted((HERE / 'metadata').rglob('*')) if p.is_file()}
    gate = {'phase': 'M0 Allen', 'verdict': 'INCONCLUSIVE', 'pass': False,
            'potential_paired_mice': coverage['potential_paired_mice'], 'admitted_mice': 0,
            'minimum_required_mice': 16, 'thresholds_changed': False,
            'blockers': reason, 'next': 'One registered metadata-only IBL assessment; no M1',
            'input_sha256': inputs}
    encoded = json.dumps(gate, indent=2, sort_keys=True)
    target = output / 'allen_gate_result.json'
    if target.exists() and target.read_text() != encoded:
        raise RuntimeError('Do not overwrite an original gate')
    if not target.exists(): target.write_text(encoded)
    print(json.dumps(summary, indent=2))
    return gate

if __name__ == '__main__': summarize()
