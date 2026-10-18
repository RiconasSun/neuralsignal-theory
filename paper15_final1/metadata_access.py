"""Final metadata/wheel body access and header pinning. No neural decode."""
import datetime
from pathlib import Path
from .source import R,P,BUCKET,read,dump,sha,frozen_definitions,source_rows
from .source_integrity import conditional_download,verify_etag_bytes
from paper15_r1.metadata_access import local_path as original_metadata_path

METADATA=frozenset(('cluster_channels','metrics','uuids','atlas','trials','saturation','recording_meta','sync'))
WHEEL=frozenset(('wheel_times','wheel_position'))


def permit(row,file,neural=False):
    actual=next((r for r in source_rows() if r['subject']==row['subject']),None)
    if actual!=row or file not in row['files']:raise PermissionError('Not exact original Final source identity')
    if file['role'] not in METADATA|WHEEL|({'times','clusters'} if neural else set()):raise PermissionError('Payload not authorized in metadata worker')


def local_path(row,file):
    permit(row,file)
    if file['role'] in METADATA:return original_metadata_path(row,file)
    path=P/'work/metadata'/row['eid']/Path(file['key']).name
    receipt=read(P/'source'/(row['subject']+'_wheel_receipt.json'))
    rec=next(x for x in receipt['files'] if x['key']==file['key'])
    assert rec['status']=='COMPLETE' and path.stat().st_size==file['bytes'] and sha(path)==rec['sha256']
    return path


def verified_head(client,file):
    head=client.head_object(Bucket=BUCKET,Key=file['key'])
    assert head['ContentLength']==file['bytes'] and head['ETag'].strip('"')==file['etag']
    assert head['LastModified'].isoformat()==file['last_modified']
    return dict(file,version_id=head.get('VersionId'),version_id_header_present='VersionId' in head)


def run():
    from one.remote.aws import get_s3_public
    frozen_definitions()
    s3,bucket=get_s3_public();assert bucket==BUCKET
    target=P/'FINAL_SOURCE_HEADER_FREEZE.json';assert not target.exists(),'Preserve prior Final pinning attempt'
    rows=source_rows();headers=[]
    for row in rows:
        for file in row['files']:
            if file['role'] in WHEEL|{'times','clusters'}:headers.append(verified_head(s3.meta.client,file))
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        original_source_sha256=sha(R/'paper15_r1/SOURCE_FILE_FREEZE.json'),subjects=[r['subject'] for r in rows],
        files=headers,neural_payload_decoded=False,Final_D_scientific_access=False))
    for row in rows:
        dest=P/'source'/(row['subject']+'_wheel_receipt.json');assert not dest.exists()
        receipt=dict(subject=row['subject'],status='STARTED',files=[],neural_payload_access=False)
        dump(dest,receipt)
        try:
            for file in row['files']:
                if file['role'] in METADATA:
                    path=local_path(row,file)
                    receipt['files'].append(dict(role=file['role'],key=file['key'],bytes=file['bytes'],
                        sha256=sha(path),status='COMPLETE',reused_original_metadata_cache=True))
                    continue
                if file['role'] not in WHEEL:continue
                permit(row,file)
                pin=next(x for x in headers if x['key']==file['key'])
                path=P/'work/metadata'/row['eid']/Path(file['key']).name;path.parent.mkdir(parents=True,exist_ok=True)
                rec=dict(role=file['role'],key=file['key'],bytes=file['bytes'],status='STARTED')
                receipt['files'].append(rec);dump(dest,receipt)
                conditional_download(s3.meta.client,BUCKET,file,pin,path)
                assert verify_etag_bytes(path.read_bytes(),pin['etag'])
                rec.update(status='COMPLETE',sha256=sha(path));dump(dest,receipt)
            receipt.update(status='COMPLETE',completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            dump(dest,receipt);print(row['subject'],'exact native metadata+wheel verified; no neural decode',flush=True)
        except Exception as exc:
            receipt.update(status='FAILED_IMMUTABLE',error=type(exc).__name__+': '+str(exc));dump(dest,receipt);raise


if __name__=='__main__':run()
