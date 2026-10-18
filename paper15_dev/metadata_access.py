"""Allowlisted source/task/curation metadata only; Final neural objects are denied."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
from .source import P, R, BUCKET, dump

METADATA = frozenset(('cluster_channels', 'metrics', 'uuids', 'atlas', 'trials', 'saturation', 'recording_meta', 'sync'))


def permit_metadata(row, role):
    allowed = METADATA | ({'wheel_times', 'wheel_position'} if row['allocation'] == 'DEVELOPMENT' else set())
    if role not in allowed:
        raise PermissionError('Not authorized by metadata access stage: '+role)


def local_path(row, file):
    permit_metadata(row, file['role'])
    pilots = json.loads((R/'paper15_m0/PILOT_FILE_FREEZE.json').read_text(encoding='utf8'))['files']
    if any(x['key'] == file['key'] for x in pilots):
        return R/'paper15_m0/work/native'/row['eid']/Path(file['key']).name
    return P/'work/metadata'/row['eid']/Path(file['key']).name


def fetch(source_only=False):
    from one.remote.aws import get_s3_public, s3_download_file
    freeze = json.loads((P/'SOURCE_FILE_FREEZE.json').read_text(encoding='utf8'))
    assert freeze['all_inventory_pass']
    s3, bucket = get_s3_public(); assert bucket == BUCKET
    original = json.loads((R/'paper15_m0/results/FILE_RECEIPTS.json').read_text(encoding='utf8'))
    def one(row):
        receipt_path = P/'source'/(row['eid']+('_source_recovery_receipt.json' if source_only else '_metadata_receipt.json'))
        assert not receipt_path.exists(), 'No silent overwrite/retry of metadata receipts'
        receipts = []
        try:
            for file in row['files']:
                role = file['role']
                if source_only and role in ('wheel_times', 'wheel_position'):
                    continue
                try:
                    permit_metadata(row, role)
                except PermissionError:
                    continue
                target = local_path(row, file)
                old = next((x for x in original if x['key'] == file['key'] and x['status'] == 'COMPLETE'), None)
                rec = dict(role=role, key=file['key'], status='STARTED', bytes=file['bytes'],
                    neural_payload=False, allocation=row['allocation'])
                receipts.append(rec)
                assert file['bytes'] <= 15000000
                previous_path = P/'source'/(row['eid']+'_metadata_receipt.json')
                previous = json.loads(previous_path.read_text(encoding='utf8')) if previous_path.exists() else {}
                cached = next((x for x in previous.get('files',[]) if x['key']==file['key'] and x.get('sha256')),None)
                if old:
                    assert target.exists() and target.stat().st_size == file['bytes']
                    rec['source'] = 'REUSED_M0_IMMUTABLE'
                    b = target.read_bytes()
                    assert hashlib.sha256(b).hexdigest() == old['sha256']
                elif cached:
                    assert target.exists() and target.stat().st_size==file['bytes']
                    b=target.read_bytes(); assert hashlib.sha256(b).hexdigest()==cached['sha256']
                    rec.update(source='REUSED_VERIFIED_ATTEMPT_1', version_id=cached.get('version_id'),
                        version_id_header_present=cached.get('version_id_header_present'),etag=file['etag'],last_modified=file['last_modified'])
                else:
                    head = s3.meta.client.head_object(Bucket=BUCKET, Key=file['key'])
                    assert head['ContentLength'] == file['bytes'] and head['ETag'].strip('"') == file['etag']
                    assert head['LastModified'].isoformat() == file['last_modified']
                    rec.update(version_id=head.get('VersionId'), version_id_header_present='VersionId' in head,
                        last_modified=head['LastModified'].isoformat(), etag=file['etag'])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    assert not target.exists(), 'Unexpected existing payload has no verified receipt'
                    s3_download_file(file['key'], target, s3=s3, bucket_name=BUCKET, overwrite=False)
                    assert target.stat().st_size == file['bytes']
                    b = target.read_bytes()
                if '-' not in file['etag']:
                    assert hashlib.md5(b).hexdigest() == file['etag']
                rec.update(status='COMPLETE', sha256=hashlib.sha256(b).hexdigest())
            dump(receipt_path, dict(subject=row['subject'], eid=row['eid'], files=receipts,
                completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                neural_arrays_accessed=False, final_wheel_values_accessed=False))
            print(row['subject'], len(receipts), 'metadata verified', flush=True)
        except Exception as exc:
            if receipts:
                receipts[-1].update(status='FAILED', error=type(exc).__name__+': '+str(exc))
            dump(receipt_path, dict(subject=row['subject'], files=receipts, failure=type(exc).__name__+': '+str(exc)))
            raise
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(one, freeze['subjects']))


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-only',action='store_true')
    fetch(ap.parse_args().source_only)
