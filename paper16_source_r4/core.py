"""R4 bookkeeping plus explicitly version-verified frozen R3 scientific utilities."""
from pathlib import Path
import hashlib
import json
import os

R = Path(__file__).resolve().parents[1]
P = R/'paper16_source_r4'
E = R/'ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4'
S = R/'paper16_dev_r3'


def load(path): return json.loads(Path(path).read_text(encoding='utf8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def registration(): return load(P/'ACCESS_REGISTRATION.json')


def verify_versions():
    for name, digest in registration()['reuse_modules'].items():
        if sha(R/name) != digest: raise RuntimeError('Frozen utility version changed: '+name)


verify_versions()
from paper16_dev_r3.core import (SourceStop, ResourceStop, CommonSupportStop, once, array_id,
    save_arrays, validate_item, finite_native, observation_mask, coverage, qc_a, extract_a, select_common)
from paper16_dev_r3.clock_bound import guard, make_stage, verify_stage_environment
from paper16_dev_r3.run_m2 import source_inputs, supervise_child
from paper16_dev_r3.windows_job import require_job


def verify_history():
    history = load(P/'R3_REUSE_MANIFEST.json')
    for row in history['public_files']+history['private_files']:
        path = R/row['path']
        if row['path'] == 'ops/daily-operations.md':
            snapshot = E/'R3_DAILY_FROZEN_SNAPSHOT.bin'
            if not snapshot.exists() or sha(snapshot) != row['sha256'] or not path.read_bytes().endswith(snapshot.read_bytes()):
                raise SourceStop('Original R3 daily bytes not preserved as exact suffix')
        elif path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise SourceStop('Historical R3 public/private evidence changed: '+row['path'])
    for name, expected in [('paper16_m1/M1_FREEZE_MANIFEST.json',334),
            ('paper16_dev/STOP_FREEZE_MANIFEST.json',58),
            ('paper16_linkdiag_r1/DIAGNOSTIC_FREEZE_MANIFEST.json',100),
            ('paper16_running_r2/RUNNING_FREEZE_MANIFEST.json',357)]:
        rows = load(R/name)['files']
        if len(rows) != expected: raise SourceStop('Historical manifest denominator changed')
        for row in rows:
            path = R/row['path']
            if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']: raise SourceStop('Frozen scientific source/evidence changed')
    verify_versions()


def verify_saved_A(item, expected_count=None):
    import numpy as np
    folder = S/'results/sources'/str(item['session_id'])
    raw = (folder/'UNIT_QC.jsonl').read_bytes()
    rows = [json.loads(s) for s in raw.decode('utf8').splitlines()]
    if expected_count is not None and len(rows) != expected_count: raise SourceStop('Historical A capture count')
    if [x['unit_id'] for x in rows] != item['candidate_unit_ids'][:len(rows)]: raise SourceStop('Historical candidate order/prefix mismatch')
    _, flashes, _, _ = source_inputs(item)
    for row in rows:
        capture = row['private_A_capture']; path = (R/capture['private_path']).resolve()
        path.relative_to((S/'work/private/A'/str(item['session_id'])).resolve())
        if sha(path) != capture['sha256']: raise SourceStop('Historical A file hash mismatch')
        with np.load(path, allow_pickle=False) as data: arrays = {k:data[k].copy() for k in data.files}
        if {k:array_id(v) for k,v in arrays.items()} != capture['arrays']: raise SourceStop('Historical A native array identity')
        if qc_a(arrays, flashes['start'], registration()) != row['A_physiology']: raise SourceStop('Historical A QC mismatch')
    return raw, rows


def private_file(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out:
        out.write(body); out.flush(); os.fsync(out.fileno())
