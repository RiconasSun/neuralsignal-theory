"""Reproduce only retained HDF5 metadata and synthetic regressions, offline."""
import contextlib
import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

import h5py
import numpy as np
import requests
import scipy

from .links import ALIAS, EXPECTED, Inspector, LinkProblem, no_dataset_values
from .saved_ranges import SavedRangeReader

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_linkdiag_r1'
E = R / 'ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextlib.contextmanager
def offline():
    def deny(*a, **kw):
        raise RuntimeError('Network forbidden in saved-only reproduction')
    with patch.object(socket.socket, 'connect', deny), patch.object(socket, 'create_connection', deny), patch.object(requests.Session, 'request', deny):
        yield


def replay():
    receipt = read(P/'results/SOURCE_INSPECTION_RECEIPT.json')
    reg = read(P/'ACCESS_REGISTRATION.json')
    rows = []
    reader = SavedRangeReader(R, receipt['source']['size'], receipt['ranges'])
    with offline(), no_dataset_values() as canary:
        with h5py.File(reader, 'r') as file:
            inspector = Inspector(file, lambda row: rows.append(copy.deepcopy(row)))
            try:
                result = inspector.run(reg['allowed_paths'])
            except LinkProblem as exc:
                result = {'status': 'SOURCE_SCHEMA_INCOMPATIBLE' if exc.kind in ['SCHEMA', 'MISSING'] else 'UNSAFE_OR_UNEXPECTED_LINK' if exc.kind in ['UNSAFE', 'CYCLE'] else 'INCONCLUSIVE_METADATA',
                          'problem_kind': exc.kind, 'problem_path': exc.path, 'error': exc.detail}
        assert canary['forbidden_value_calls'] == 0
    assert result['status'] == receipt['status'] == 'SOURCE_SCHEMA_INCOMPATIBLE'
    for field in ['problem_kind', 'problem_path', 'error']:
        assert result[field] == receipt[field]
    assert rows == inspector.rows == receipt['component_audit']
    journal = [json.loads(x) for x in (P/'results/COMPONENT_JOURNAL.jsonl').read_text().splitlines()]
    assert journal == rows
    objects = inspector.objects
    assert objects[ALIAS]['same_file_id'] and objects[EXPECTED]['same_file_id']
    assert objects[ALIAS]['object_address'] == objects[EXPECTED]['object_address'] == 19550656
    rot = objects['/processing/running/running_wheel_rotation/data']
    assert rot['dtype'] == '<f4' and rot['shape'] == [365911]
    assert objects[ALIAS]['dtype'] == '<f8'
    assert objects['/processing/running/running_speed_end_times/timestamps']['dtype'] == '<f8'
    soft = [x for x in rows if x['path'] == ALIAS and x['link_class'] == 'SoftLink']
    assert len(soft) == 2 and soft[0]['expected_object_match'] is None and soft[1]['expected_object_match'] is True
    assert all(x['literal_target'] == x['normalized_candidate'] == EXPECTED for x in soft)
    return {'diagnostic_status': result['status'], 'actual_failed_component': ALIAS, 'actual_link_class': 'SoftLink',
            'literal_target': EXPECTED, 'normalized_target': EXPECTED, 'expected_source_object_match': True,
            'rotation_storage_dtype': rot['dtype'], 'timestamp_storage_dtype': objects[ALIAS]['dtype'],
            'metadata_rows': 365911, 'component_events': len(rows), 'offline_hdf5_metadata_replay': True,
            'dataset_values_read': 0, 'new_network_requests': 0, 'same_row_numeric_timing_validated': False}


def checks():
    assert sys.version.split()[0] == '3.11.15'
    assert (h5py.__version__, np.__version__, requests.__version__) == ('3.16.0', '2.4.6', '2.32.5')
    assert scipy.__version__ == '1.16.3'
    base = 'a0065c66aaa84ad39a985903fcd77bdc1e1e711c'
    daily = (R/'ops/daily-operations.md').read_bytes()
    old_daily = subprocess.check_output(['git','show',base+':ops/daily-operations.md'],cwd=R)
    assert daily.endswith(old_daily) and daily != old_daily
    changed = subprocess.check_output(['git','diff','--name-only',base,'--'],cwd=R).decode().splitlines()
    assert all(x == 'ops/daily-operations.md' or x.startswith(('paper16_linkdiag_r1/','ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1/')) for x in changed)
    baseline = read(E/'baseline.json')
    trace = read(P/'REQUIREMENT_TRACE.json')
    assert trace['baseline_sha256'] == sha(E/'baseline.json')
    assert baseline['requirement_count'] == len(trace['items']) == trace['baseline_requirement_count'] == 247
    for old, new in zip(baseline['requirements'], trace['items']):
        assert all(old[k] == new[k] for k in ['id','source_line','requirement'])
        assert new['evidence'] and new['verification_method']
    assert trace['content_verified_count'] == sum(x['status']=='VERIFIED' for x in trace['items']) == 234
    acceptance = read(P/'SEMANTIC_ACCEPTANCE.json')
    assert acceptance['count'] == len(acceptance['items']) == 60
    assert len({x['id'] for x in acceptance['items']}) == 60
    for manifest, count in [('paper16_m1/M1_FREEZE_MANIFEST.json', 334), ('paper16_dev/STOP_FREEZE_MANIFEST.json', 58)]:
        rows = read(R/manifest)['files']
        assert len(rows) == count
        for row in rows:
            path = R/row['path']
            assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes'], row['path']
    from .inspect_source import review_gate
    reg = review_gate()
    receipt = read(P/'results/SOURCE_INSPECTION_RECEIPT.json')
    parent = read(P/'results/INSPECTION_ATTEMPT.json')
    worker = read(P/'results/SOURCE_OPEN_ATTEMPT.json')
    supervision = read(P/'results/SUPERVISION.json')
    assert reg['source'] == receipt['source'] == worker['source']
    assert sha(P/'ACCESS_REGISTRATION.json') == receipt['registration_sha256'] == parent['registration_sha256']
    assert worker['inspection_sha256'] == sha(P/'inspect_source.py')
    assert supervision['valid_completed_inspection'] is True and supervision['child_exit'] == 0 and not supervision['child_killed']
    assert supervision['deadline'] == parent['deadline'] == worker['deadline']
    assert abs(parent['deadline']-parent['started']-600) < 1e-8
    assert parent['started'] <= receipt['worker_completed_monotonic'] <= supervision['completed'] < parent['deadline']
    assert 5 < supervision['completed']-parent['started'] < 6
    assert receipt['payload_accounting_complete'] is True
    assert receipt['new_range_requests'] == len(receipt['ranges']) == len(receipt['response_headers']) == 44
    assert sum(x['bytes'] for x in receipt['ranges']) == receipt['new_payload_bytes'] == 85712
    assert sum(x['bytes']+1 for x in receipt['ranges']) == receipt['new_reserved_bytes'] == 85756
    assert receipt['new_reserved_bytes'] <= 8388608 and receipt['new_range_requests'] <= 128
    journal = [json.loads(x) for x in (P/'results/RANGE_JOURNAL.jsonl').read_text().splitlines()]
    assert [x['request'] for x in journal if x['event'] == 'RESERVED'] == list(range(1,45))
    assert sum(x['bytes'] for x in journal if x['event'] == 'PAYLOAD') == 85712
    assert sum(x['reserved_bytes'] for x in journal if x['event'] == 'RESERVED') == 85756
    assert [{k:v for k,v in x.items() if k != 'event'} for x in journal if x['event'] == 'COMPLETE_RANGE'] == receipt['ranges']
    assert [{k:v for k,v in x.items() if k != 'event'} for x in journal if x['event'] == 'RESPONSE_HEADERS'] == receipt['response_headers']
    for row, header in zip(receipt['ranges'], receipt['response_headers']):
        assert 0 < row['bytes'] <= 131072
        assert header == {'request':row['request'], 'status':206, 'content_range':f"bytes {row['offset']}-{row['offset']+row['bytes']-1}/{reg['source']['size']}", 'etag':reg['source']['etag']}
    assert len(list((P/'results/metadata_ranges').glob('*.bin'))) == 44
    assert all(receipt[k] == 0 for k in ['running_numeric_values_read','neural_values_read','additional_sources','forbidden_dataset_value_calls'])
    assert not any(receipt[k] for k in ['production_reader_modified','M2_restarted','Final_C_D_access'])
    result = replay()
    result.update({'upstream_M1_payloads':334,'upstream_M2_payloads':58,'range_requests':44,'payload_bytes':85712,
                   'reserved_bytes':85756,'elapsed_seconds':round(supervision['completed']-parent['started'],3),
                   'owner_trace_rows':247,'content_verified_rows_before_closure':234,'semantic_acceptance_items':60})
    freeze = P/'DIAGNOSTIC_FREEZE_MANIFEST.json'
    if freeze.exists():
        from .payload_contract import EXPECTED_PAYLOAD
        files = read(freeze)['files']
        assert len(files) == len(EXPECTED_PAYLOAD) and {x['path'] for x in files} == set(EXPECTED_PAYLOAD)
        assert len({x['path'] for x in files}) == len(files)
        for row in files:
            path = R/row['path']
            assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes'], row['path']
        result['frozen_payloads'] = len(files)
    return result


def main():
    with offline():
        result = checks()
        suite = unittest.defaultTestLoader.loadTestsFromNames(['paper16_linkdiag_r1.test_diagnostic', 'paper16_linkdiag_r1.test_saved_evidence'])
        run = unittest.TextTestRunner(verbosity=2).run(suite)
        assert run.wasSuccessful() and run.testsRun == 15
        result['synthetic_tests_passed'] = run.testsRun
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
