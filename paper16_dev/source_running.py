"""Pinned Development-only source behavior read. Never opens neural datasets."""
from pathlib import Path
import datetime
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import h5py
import numpy as np
import requests
from .m2_core import running_features, role_coverage, admission_possible
from paper16_m1.code.roster_metadata import invalid_rows

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_dev'
E = R / 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development'
M1E = R / 'ops/evidence/2026-10-18/p16-m1-visual-dynamics-protocol-freeze'
ALLOW = {'/identifier', '/session_start_time', '/timestamps_reference_time',
         '/processing/running/running_wheel_rotation/data',
         '/processing/running/running_wheel_rotation/timestamps',
         '/processing/running/running_speed/timestamps',
         '/processing/running/running_speed_end_times/timestamps'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def guard(deadline):
    if time.monotonic() >= deadline:
        raise RuntimeError('Registered source-stage wall budget exhausted')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def validate_development(item, reg):
    sid = item['session_id']
    matches = [x for x in reg['objects'] if x['session_id'] == sid]
    if sid in reg['denied_final_session_ids'] or len(matches) != 1 or item != matches[0]:
        raise ValueError('Unregistered or Final source denied before open')
    if item['role'] != 'Development':
        raise ValueError('Final source denied')


def review_gate():
    required = ['paper16_dev/M2_ACCESS_REGISTRATION.json', 'paper16_dev/m2_core.py',
                'paper16_dev/source_running.py', 'paper16_dev/test_m2.py',
                'paper16_dev/M2_ACCESS_REPAIR_1.json',
                'paper16_m1/M1_FREEZE_MANIFEST.json', 'paper16_m1/code/roster_metadata.py']
    approval = read_json(E / 'M2_RUNNING_ACCESS_APPROVAL.json')
    if (approval.get('decision') != 'ACCEPTED_M2_RUNNING_ONLY' or
            any(type(approval.get(k)) is not int or approval[k] != 0 for k in ['open_P0', 'open_P1'])):
        raise ValueError('Independent running-only access approval absent or failed')
    hashes = approval.get('reviewed_hashes', {})
    if not set(required) <= set(hashes):
        raise ValueError('Incomplete access review source binding')
    for name, digest in hashes.items():
        path = (R / name).resolve()
        if not path.is_relative_to(R) or sha(path) != digest:
            raise ValueError('Reviewed source identity mismatch ' + name)
    if sha(E / 'M2_RUNNING_ACCESS_REVIEW.md') != approval.get('report_sha256'):
        raise ValueError('Review evidence identity mismatch')
    for row in read_json(R / 'paper16_m1/M1_FREEZE_MANIFEST.json')['files']:
        if sha(R / row['path']) != row['sha256']:
            raise ValueError('Upstream M1 source freeze mismatch')
    return approval


def hard_object(file, path):
    if path not in ALLOW:
        raise ValueError('Neural/nonallowlisted path denied before lookup')
    group = file
    for part in path.strip('/').split('/'):
        if not isinstance(group, h5py.Group) or not isinstance(group.get(part, getlink=True), h5py.HardLink):
            raise ValueError('External/soft/noncanonical source link denied')
        group = group[part]
    return group


def decode_scalar(value):
    value = np.asarray(value).item()
    return value.decode('utf8') if isinstance(value, bytes) else str(value)


def native_running(file, sid, header, audit):
    if str(file.attrs.get('nwb_version')) != '2.2.2':
        raise ValueError('Frozen NWB generation changed')
    for name, expected in [('/identifier', str(sid)),
                           ('/session_start_time', header['/session_start_time']),
                           ('/timestamps_reference_time', header['/timestamps_reference_time'])]:
        dataset = hard_object(file, name)
        if not isinstance(dataset, h5py.Dataset) or dataset.size != 1:
            raise ValueError('Scalar identity schema')
        audit.append(name)
        if decode_scalar(dataset[()]) != expected:
            raise ValueError('Native source identity or clock mismatch')
    rot = hard_object(file, '/processing/running/running_wheel_rotation/data')
    parent = rot.parent
    unit = rot.attrs.get('unit')
    if isinstance(unit, bytes):
        unit = unit.decode('utf8')
    # TimeSeries.unit is a data-dataset attribute under standard NWB2.
    if unit != 'radians':
        raise ValueError('Native net_rotation angular units unverified')
    parent_unit = parent.attrs.get('unit', unit)
    if isinstance(parent_unit, bytes):
        parent_unit = parent_unit.decode('utf8')
    if parent_unit != unit:
        raise ValueError('Conflicting angular unit metadata')
    for name, expected in [('conversion', 1.), ('offset', 0.)]:
        if float(rot.attrs.get(name, expected)) != expected:
            raise ValueError('Unregistered native rotation scaling')
    ts = hard_object(file, '/processing/running/running_wheel_rotation/timestamps')
    ts_source = hard_object(file, '/processing/running/running_speed/timestamps')
    end = hard_object(file, '/processing/running/running_speed_end_times/timestamps')
    if h5py.h5o.get_info(ts.id).addr != h5py.h5o.get_info(ts_source.id).addr:
        raise ValueError('Native same-row timestamp link differs from writer')
    if any(not isinstance(x, h5py.Dataset) or x.ndim != 1 or x.dtype != np.dtype('float64') for x in [rot, ts, end]):
        raise ValueError('Native behavior precision/schema')
    if not 0 < len(rot) == len(ts) == len(end) <= 2000000:
        raise ValueError('Native behavior row correspondence or bound')
    names = ['/processing/running/running_wheel_rotation/data',
             '/processing/running/running_wheel_rotation/timestamps',
             '/processing/running/running_speed/timestamps',
             '/processing/running/running_speed_end_times/timestamps']
    audit.extend(names)
    a, b, q = np.asarray(ts[:]), np.asarray(end[:]), np.asarray(rot[:])
    # This call checks every decoded native row without inspecting neural data.
    running_features(a, b, q, np.empty(0, dtype=float), unit=unit)
    return a, b, q


class RangeReader(io.RawIOBase):
    def __init__(self, item, deadline):
        self.item = item
        self.deadline = deadline
        self.pos = self.used = self.reserved = self.calls = 0
        self.maximum = 134217728
        self.cache = {}
        self.ranges = []
        self.http = requests.Session()

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.item['size'] + offset
        if self.pos < 0:
            raise ValueError('Negative source seek')
        return self.pos

    def read(self, n=-1):
        guard(self.deadline)
        if n < 0 or n > 33554432:
            raise RuntimeError('Oversized source read denied')
        n = min(n, max(0, self.item['size'] - self.pos))
        out = bytearray()
        while n:
            guard(self.deadline)
            step = min(n, 1048576)
            key = (self.pos, step)
            if key not in self.cache:
                if time.monotonic() >= self.deadline or self.reserved + step + 1 > self.maximum or self.calls >= 4096:
                    raise RuntimeError('Registered source budget exhausted before request')
                self.reserved += step + 1
                self.calls += 1
                last = self.pos + step - 1
                url = 'https://api.brain-map.org/api/v2/well_known_file_download/' + str(self.item['file_id'])
                headers = {'Range': f'bytes={self.pos}-{last}', 'If-Match': self.item['etag']}
                with self.http.get(url, params={'p16_offset': self.pos, 'p16_length': step}, headers=headers,
                                   stream=True, timeout=min(30, max(.001, self.deadline-time.monotonic()))) as response:
                    if (response.status_code != 206 or response.headers.get('Content-Range') != f'bytes {self.pos}-{last}/{self.item["size"]}' or
                            response.headers.get('ETag') != self.item['etag']):
                        raise RuntimeError('Native range/object identity mismatch; no bulk fallback')
                    data = response.raw.read(step + 1)
                    guard(self.deadline)
                    if len(data) != step:
                        raise RuntimeError('Native range length mismatch')
                self.cache[key] = data
                self.used += step
                self.ranges.append({'offset': self.pos, 'bytes': step, 'sha256': hashlib.sha256(data).hexdigest()})
            out.extend(self.cache[key])
            self.pos += step
            n -= step
        return bytes(out)

    def readinto(self, buf):
        data = self.read(len(buf))
        buf[:len(data)] = data
        return len(data)


def main(deadline):
    review_gate()
    guard(deadline)
    reg = read_json(P / 'M2_ACCESS_REGISTRATION.json')
    source_receipts = read_json(M1E / 'ROSTER_METADATA_FINAL.json')
    lookup = {x['session_id']: R / x['path'] for x in source_receipts['sessions']}
    probes = read_json(R / 'paper16_m0/metadata/probes.body')['msg']
    result_dir = P / 'results/running'
    result_dir.mkdir(parents=True, exist_ok=True)
    stage_claim = P / 'results/M2_RUNNING_ATTEMPT.json'
    write_once(stage_claim, {'status': 'STARTED', 'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                             'registration_sha256': sha(P / 'M2_ACCESS_REGISTRATION.json'),
                             'reader_sha256': sha(Path(__file__)), 'no_retry': True})
    records = []
    for item in sorted(reg['objects'], key=lambda x: int(x['mouse_id'])):
        guard(deadline)
        validate_development(item, reg)
        sid = item['session_id']
        claim = result_dir / f'{sid}.attempt.json'
        write_once(claim, {'status': 'STARTED', 'session_id': sid, 'time': datetime.datetime.now(datetime.timezone.utc).isoformat()})
        reader = None
        audit = []
        try:
            header = json.loads(gzip.decompress((R / 'paper12_native_support1/metadata/native_headers' / f'{sid}.json.gz').read_bytes()))
            meta_path = lookup[sid]
            meta = read_json(meta_path)
            with np.load(meta_path.with_suffix('.npz'), allow_pickle=False) as npz:
                starts, stops, color, source_valid = (npz[x].copy() for x in ['start', 'stop', 'color', 'main_valid'])
            inv = header['tables'].get('invalid_times', {})
            scope = [x for x in probes if int(x['ecephys_session_id']) == sid]
            bad = invalid_rows(inv.get('start_time', []), inv.get('stop_time', []), inv.get('tags', []), inv.get('tags_index', []), item, scope)
            targets = starts[:, None] + np.arange(5, 11, dtype=float)[None, :] * .02
            # Reuse only original two complete local pilot objects, hash verified.
            local = R / 'paper16_m0/work' / f'session_{sid}.nwb'
            guard(deadline)
            if sid in [760345702, 829720705] and local.exists():
                receipt = read_json(R / 'paper16_m0/results' / f'TRANSFER_{sid}.json')
                digest = hashlib.sha256()
                with local.open('rb') as f:
                    for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
                        guard(deadline)
                        digest.update(block)
                if receipt['status'] != 'COMPLETE' or digest.hexdigest() != receipt['sha256']:
                    raise ValueError('Existing local Development object corrupted')
                guard(deadline)
                with h5py.File(local, 'r') as f:
                    a, b, q = native_running(f, sid, header, audit)
                origin = 'M0 complete hash-verified local object,behavior only'
            else:
                reader = RangeReader(item, deadline)
                with h5py.File(reader, 'r') as f:
                    a, b, q = native_running(f, sid, header, audit)
                origin = 'New pinned Development running-only ranged source'
            guard(deadline)
            keep = (b >= starts[0] - .2) & (a <= starts[-1] + .22)
            a, b, q = a[keep], b[keep], q[keep]
            values, missing, parent = running_features(a, b, q, targets, bad)
            coverage = role_coverage(missing, color, source_valid)
            guard(deadline)
            out = result_dir / f'{sid}.npz'
            if out.exists():
                raise FileExistsError('No running result overwrite/retry')
            np.savez_compressed(out, start=a, end=b, net_rotation=q, targets=targets,
                                running=values, missing=missing, parent=parent,
                                color=color, source_valid=source_valid, invalid=np.asarray(bad, dtype=float).reshape(-1, 2))
            guard(deadline)
            result = {'session_id': sid, 'mouse_id': item['mouse_id'], 'protocol': item['protocol'],
                      'probe_id': item['probe_id'], 'status': 'COMPLETE', 'source_origin': origin,
                      'native_unit': 'radians', 'row_time_correspondence_verified': True,
                      'coverage': coverage, 'running_coverage_pass': all(x['pass'] for role in coverage.values() for x in role.values()),
                      'potential_running_coverage_pass': all(x['possible_after_observation_support'] for role in coverage.values() for x in role.values()),
                      'rows_saved': len(a), 'saved_binary64_sha256': sha(out),
                      'source_stimulus_receipt_sha256': sha(meta_path), 'dataset_paths_read': audit,
                      'neural_datasets_read': 0, 'Final_C_access': False, 'Final_D_access': False,
                      'transport_bytes': reader.used if reader else 0, 'reserved_bytes': reader.reserved if reader else 0,
                      'ranges': reader.ranges if reader else []}
            guard(deadline)
            write_once(result_dir / f'{sid}.json', result)
            records.append(result)
            print(json.dumps({'session_id': sid, 'mouse_id': item['mouse_id'], 'running_coverage_pass': result['running_coverage_pass'],
                              'minimum_fraction': min(x['fraction'] for role in coverage.values() for x in role.values()),
                              'bytes': result['transport_bytes']}), flush=True)
        except Exception as exc:
            write_once(result_dir / f'{sid}.failure.json', {'status': 'FAILED_SOURCE_STOP', 'error': type(exc).__name__ + ': ' + str(exc),
                         'dataset_paths_read': audit, 'transport_bytes': reader.used if reader else 0,
                         'reserved_bytes': reader.reserved if reader else 0, 'ranges': reader.ranges if reader else [],
                         'neural_datasets_read': 0, 'no_retry': True})
            raise
        finally:
            if reader:
                reader.http.close()
    guard(deadline)
    summary = admission_possible(records)
    summary.update({'status': 'RUNNING_COHORT_VIABLE_FOR_A_QC' if summary['possible_A_physiological_admission'] else 'STOP_SOURCE_OR_QC',
                    'original_Development_mice': 28, 'records_complete': len(records),
                    'neural_datasets_read': 0, 'real_model_fits': 0, 'Final_C_access': False, 'Final_D_access': False,
                    'transport_bytes': sum(x['transport_bytes'] for x in records),
                    'reserved_bytes': sum(x['reserved_bytes'] for x in records)})
    guard(deadline)
    write_once(P / 'results/M2_RUNNING_GATE.json', summary)
    print(json.dumps(summary), flush=True)


def supervise(command, seconds, receipt_path):
    """Separate parent denies admission without a timely child completion receipt."""
    start = time.monotonic()
    deadline = start + seconds
    child = subprocess.Popen(command + ['--deadline', repr(deadline)])
    try:
        code = child.wait(timeout=max(.001, deadline-time.monotonic()))
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()
        write_once(receipt_path, {'status': 'STOP_BUDGET', 'child_killed': True,
                                  'deadline': deadline, 'completed': time.monotonic(), 'valid_source_stage': False})
        return 124
    completed = time.monotonic()
    valid = code == 0 and completed < deadline
    write_once(receipt_path, {'status': 'CHILD_COMPLETED_IN_BUDGET' if valid else 'CHILD_FAILED_OR_EXPIRED',
                              'child_exit': code, 'child_killed': False, 'started': start,
                              'deadline': deadline, 'completed': completed, 'valid_source_stage': valid})
    return code if code else (0 if valid else 124)


if __name__ == '__main__':
    if '--worker' in sys.argv:
        main(float(sys.argv[sys.argv.index('--deadline') + 1]))
    else:
        review_gate()
        target = P / 'results/M2_RUNNING_SUPERVISION.json'
        if target.exists() or (P / 'results/M2_RUNNING_ATTEMPT.json').exists():
            raise FileExistsError('Existing source attempt; no retry')
        raise SystemExit(supervise([sys.executable, '-m', 'paper16_dev.source_running', '--worker'], 14400, target))
