"""Exact-roster native metadata inventory. This module never reads neural payloads."""
import concurrent.futures
import csv
import datetime
import hashlib
import json
import re
import math
import struct
from pathlib import Path, PurePosixPath

R = Path(__file__).resolve().parents[1]
P = R / 'paper15_r1'
BUCKET = 'ibl-brain-wide-map-public'


def json_safe(value):
    if isinstance(value,float) and not math.isfinite(value):
        return {'__p15_binary64__':struct.pack('>d',value).hex()}
    if isinstance(value,dict):return {k:json_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [json_safe(v) for v in value]
    return value

def load_json(text,**kwargs):
    def hook(value):
        if set(value)=={'__p15_binary64__'}:
            number=struct.unpack('>d',bytes.fromhex(value['__p15_binary64__']))[0]
            assert not math.isfinite(number)
            return number
        return value
    return json.loads(text,object_hook=hook,**kwargs)

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(value), indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8')


def roster():
    with (R/'paper15_m1/COHORT.csv').open(encoding='utf8') as handle:
        return list(csv.DictReader(handle))


def rules(probe):
    sort = f'alf/{probe}/pykilosort/#2024-05-06#/'
    raw = f'raw_ephys_data/{probe}/'
    stem = '_spikeglx_ephysData_g0_t0.imec'
    return dict(times=(sort, 'spikes.times.', '.npy'), clusters=(sort, 'spikes.clusters.', '.npy'),
        cluster_channels=(sort, 'clusters.channels.', '.npy'), metrics=(sort, 'clusters.metrics.', '.pqt'),
        uuids=(sort, 'clusters.uuids.', '.csv'), atlas=(sort, 'channels.brainLocationIds_ccf_2017.', '.npy'),
        trials=('alf/#2025-03-03#/', '_ibl_trials.table.', '.pqt'),
        wheel_times=('alf/', '_ibl_wheel.timestamps.', '.npy'), wheel_position=('alf/', '_ibl_wheel.position.', '.npy'),
        saturation=(raw, '_iblqc_ephysSaturationAP.samples.', '.pqt'),
        recording_meta=(raw, stem, '.meta'), sync=(raw, stem, '.npy'))


def resolve(row, inv):
    root = f"data/{row['lab']}/Subjects/{row['subject']}/{row['date']}/{int(row['session_number']):03}/"
    assert inv['prefix'] == root and inv['bucket'] == BUCKET
    files, issues = [], []
    for role, (collection, stem, suffix) in rules(row['probe_name']).items():
        hits = [x for x in inv['objects'] if str(PurePosixPath(x['key']).parent)+'/' == root+collection
                and PurePosixPath(x['key']).name.startswith(stem) and x['key'].endswith(suffix)]
        if role in ('recording_meta', 'sync'):
            token = r'\.ap\.' if role == 'recording_meta' else r'\.sync\.'
            hits = [x for x in hits if re.match(re.escape(stem)+r'\d*'+token, PurePosixPath(x['key']).name)]
        if len(hits) != 1:
            issues.append(dict(role=role, reason='ESSENTIAL_MATCH_NOT_UNIQUE', matches=len(hits)))
            continue
        x = hits[0]
        match = re.search(r'\.([0-9a-f-]{36})\.[^.]+$', x['key'])
        if not match:
            issues.append(dict(role=role, reason='MISSING_UUID')); continue
        files.append(dict(**x, role=role, dataset_uuid=match.group(1), subject=row['subject'],
            eid=row['eid'], pid=row['pid'], probe=row['probe_name'], allocation=row['allocation'], bucket=BUCKET))
    # Full selected-probe and session catalog retained for subsequent annotation clock audit.
    annotations = [x for x in inv['objects'] if any(t in x['key'].lower()
        for t in ('saturation', 'invalid', 'artifact', 'badinterval', 'bad_interval'))]
    return dict(subject=row['subject'], eid=row['eid'], pid=row['pid'], allocation=row['allocation'],
        files=files, issues=issues, additional_annotation_catalog=annotations,
        source_inventory_pass=not issues, neural_payload_access=False)


def inventory():
    from one.remote.aws import get_s3_public
    s3, bucket = get_s3_public()
    assert bucket == BUCKET
    rows = roster()
    assert len(rows) == 20 and sum(x['allocation'] == 'DEVELOPMENT' for x in rows) == 12
    pilots = json.loads((R/'paper15_m0/PILOT_FILE_FREEZE.json').read_text(encoding='utf8'))['files']
    pilot_ids = {x['eid'] for x in pilots}
    def one(row):
        dest = P/'source'/(row['eid']+'_s3.json')
        if row['eid'] in pilot_ids:
            assert row['allocation'] == 'DEVELOPMENT'
            inv = json.loads((R/'paper15_m0/source'/(row['eid']+'_s3.json')).read_text(encoding='utf8'))
        elif dest.exists():
            inv = json.loads(dest.read_text(encoding='utf8'))
        else:
            prefix = f"data/{row['lab']}/Subjects/{row['subject']}/{row['date']}/{int(row['session_number']):03}/"
            reply = s3.meta.client.list_objects_v2(Bucket=BUCKET, Prefix=prefix, MaxKeys=1000)
            assert not reply.get('IsTruncated'), 'Essential bounded inventory exceeded; preserve and stop'
            inv = dict(bucket=BUCKET, prefix=prefix, listed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                objects=[dict(key=x['Key'], bytes=x['Size'], etag=x['ETag'].strip('"'),
                    last_modified=x['LastModified'].isoformat()) for x in reply.get('Contents', [])])
            dump(dest, inv)
        resolved = resolve(row, inv)
        if row['eid'] in pilot_ids:
            original = {x['role']: x for x in pilots if x['eid'] == row['eid']}
            for f in resolved['files']:
                assert all(f[k] == original[f['role']][k] for k in ('key', 'bytes', 'etag', 'dataset_uuid'))
        print(row['subject'], row['allocation'], len(inv['objects']), len(resolved['issues']), flush=True)
        return resolved
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, rows))
    target = P/'SOURCE_FILE_FREEZE.json'
    assert not target.exists(), 'Append-only original source freeze cannot be overwritten'
    dump(target, dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        roster_sha256=hashlib.sha256((R/'paper15_m1/COHORT.csv').read_bytes()).hexdigest(),
        all_inventory_pass=all(x['source_inventory_pass'] for x in results), subjects=results,
        neural_payload_access=False, final_neural_access=False,
        meaning='Exact object inventory only; annotation, clock, task and physiology are not thereby certified'))


if __name__ == '__main__':
    inventory()
