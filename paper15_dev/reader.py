"""Trusted local Development extractor. Only A is implemented/exportable at M2."""
import datetime
import hashlib
import json
from pathlib import Path
import numpy as np
from .source import P, R, BUCKET, dump, roster
from .physiology import unit_qc
from .source_integrity import conditional_download


def authorize(subject, role, row, metadata):
    if row['subject']!=subject or row['allocation']!='DEVELOPMENT':
        raise PermissionError('Final neural access is forbidden in this mission')
    if role!='A':
        raise PermissionError('B/E are not released by the M2 extractor')
    if not metadata['result']['prephysiology_possible']:
        raise PermissionError('Failed metadata/coverage admission')


def project_A(times, labels, start, stop, cluster_count, support, fs):
    """Decode full Development chunks internally; export no B/E summary."""
    if len(times)!=len(labels) or not np.issubdtype(labels.dtype,np.integer):
        raise ValueError('Source timestamp/label identity mismatch')
    ts=[];ls=[]
    for i in range(0,len(times),1000000):
        chunk=np.asarray(times[i:i+1000000])
        # NaN/Inf cannot be assigned a role: fail source, never silently drop.
        if not np.isfinite(chunk).all():
            raise ValueError('Unpartitionable nonfinite Development source timestamp')
        take=(chunk>=start)&(chunk<stop)
        ts.append(chunk[take]);ls.append(np.asarray(labels[i:i+1000000])[take])
    at=np.concatenate(ts).astype(np.float64);al=np.concatenate(ls)
    if len(at) and (not (np.diff(at)>=0).all() or al.min()<0 or al.max()>=cluster_count):
        raise ValueError('A-only timestamp ordering/cluster identity failure')
    if len(at) and (at[0]<support[0]-1/fs or at[-1]>support[1]+1/fs):
        raise ValueError('A-only spikes outside registered AP/sync support')
    return at,al


def neural_file(row, file, s3):
    if row['allocation']!='DEVELOPMENT' or file['role'] not in ('times','clusters'):
        raise PermissionError('No Final or non-frozen neural source')
    frozen=json.loads((P/'NEURAL_HEADER_FREEZE.json').read_text(encoding='utf8'))
    pin=next((x for x in frozen['files'] if x['key']==file['key']),None)
    assert pin is not None and all(pin[k]==file[k] for k in ('bytes','etag','last_modified'))
    prior=json.loads((R/'paper15_m0/results/FILE_RECEIPTS.json').read_text(encoding='utf8'))
    old=next((x for x in prior if x['key']==file['key'] and x['status']=='COMPLETE'),None)
    if old:
        path=R/'paper15_m0/work/native'/row['eid']/Path(file['key']).name
        expected=old['sha256']
    else:
        path=P/'work/neural'/row['eid']/Path(file['key']).name
        assert not path.exists(), 'No silent rerun/download overwrite'
        path.parent.mkdir(parents=True,exist_ok=True)
        head=s3.meta.client.head_object(Bucket=BUCKET,Key=file['key'])
        assert head['ContentLength']==file['bytes'] and head['ETag'].strip('"')==file['etag']
        assert head['LastModified'].isoformat()==file['last_modified']
        assert head.get('VersionId')==pin['version_id'] and ('VersionId' in head)==pin['version_id_header_present']
        conditional_download(s3.meta.client,BUCKET,file,pin,path)
        expected=None
    h=hashlib.sha256();md5=hashlib.md5()
    with path.open('rb') as handle:
        for block in iter(lambda:handle.read(8*1024*1024),b''):
            h.update(block);md5.update(block)
    assert path.stat().st_size==file['bytes']
    assert expected is None or h.hexdigest()==expected
    assert '-' in file['etag'] or md5.hexdigest()==file['etag']
    return path,dict(key=file['key'],dataset_uuid=file['dataset_uuid'],role=file['role'],
        sha256=h.hexdigest(),bytes=file['bytes'],reuse_M0=old is not None,
        version_id=None if old else head.get('VersionId'),
        version_id_header_present=None if old else 'VersionId' in head)


def run():
    from one.remote.aws import get_s3_public
    gate=json.loads((P/'READER_GATE.json').read_text(encoding='utf8'))
    assert gate['approved_for_A_only']
    for rel,sha in gate['hashes'].items():
        assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==sha
    freeze=json.loads((P/'SOURCE_FILE_FREEZE.json').read_text(encoding='utf8'))
    s3,bucket=get_s3_public();assert bucket==BUCKET
    rows={x['eid']:x for x in roster()};out=[]
    for entry in freeze['subjects']:
        row=rows[entry['eid']]
        if row['allocation']!='DEVELOPMENT':continue
        state=json.loads((P/'metadata'/(row['subject']+'_task.json')).read_text(encoding='utf8'))
        if not state['result']['prephysiology_possible']:
            out.append(dict(subject=row['subject'],lab=row['lab'],admitted=False,
                reason='REGISTERED_METADATA_TRIAL_OR_UNIT_COVERAGE',neural_access=False))
            continue
        authorize(row['subject'],'A',row,state)
        receipt=P/'results'/(row['subject']+'_A_QC.json')
        assert not receipt.exists(), 'A physiology is append-only, no silent rerun'
        journal=dict(subject=row['subject'],role='A',status='STARTED',files=[],
            started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),B_export=False,E_export=False,Final_access=False)
        dump(receipt,journal)
        try:
            files={}
            for file in entry['files']:
                if file['role'] in ('times','clusters'):
                    path,rec=neural_file(row,file,s3);files[file['role']]=path
                    journal['files'].append(rec);dump(receipt,journal)
            tr=state['trials'];a_stop=state['result']['partitions']['A'][1]
            at,al=project_A(np.load(files['times'],mmap_mode='r',allow_pickle=False),
                np.load(files['clusters'],mmap_mode='r',allow_pickle=False),
                tr[0]['intervals_0'],tr[a_stop-1]['intervals_1'],len(state['native_uuid_list']),
                state['result']['recording_sync_support'],state['result']['fs'])
            ids=np.flatnonzero(np.asarray(state['valid'])&(np.asarray(state['roles'])=='A'))
            epochs=np.array([[tr[i]['stimOn_times']-.5,tr[i]['stimOn_times']+.5] for i in ids])
            atlas={int(x['id']):x['acronym'] for x in json.loads((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']}
            import re
            units=[i for i,(a,label) in enumerate(zip(state['native_cluster_atlas'],state['native_provider_labels']))
                if label==1 and re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(a))))]
            metrics,ranked=unit_qc(at,al,units,[state['native_uuid_list'][i] for i in units],ids,epochs,a_stop)
            selected=ranked[:8] if len(ranked)>=8 else []
            export=P/'work/A_exports'/(row['subject']+'.npz');export.parent.mkdir(parents=True,exist_ok=True)
            assert not export.exists()
            np.savez_compressed(export,times=at,labels=al,trial_ids=ids,epochs=epochs)
            journal.update(status='COMPLETED',physiology=metrics,ranking=[x['cluster_id'] for x in ranked],
                selected_unit_ids=[x['cluster_id'] for x in selected],selected_unit_uuids=[x['uuid'] for x in selected],
                A_epochs=len(ids),A_export_sha256=hashlib.sha256(export.read_bytes()).hexdigest(),
                all_A_source_units_preserved=True,qualified_units=len(ranked),admitted=len(selected)==8,
                completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            dump(receipt,journal)
            out.append(dict(subject=row['subject'],lab=row['lab'],admitted=len(selected)==8,qualified_units=len(ranked),
                neural_access=True,reason=None if len(selected)==8 else 'FEWER_THAN_8_A_PHYSIOLOGY_UNITS'))
            print(row['subject'],'A qualified',len(ranked),'admitted',len(selected)==8,flush=True)
        except Exception as exc:
            journal.update(status='SOURCE_FAILURE',error=type(exc).__name__+': '+str(exc));dump(receipt,journal)
            raise
    admitted=[x for x in out if x['admitted']]
    dump(P/'results/M2_PHYSIOLOGY_GATE.json',dict(subjects=out,development_eligible_mice=len(admitted),
        development_labs=len({x['lab'] for x in admitted}),M2_SOURCE_QC_PASS=len(admitted)>=8 and len({x['lab'] for x in admitted})>=4,
        required_mice=8,required_labs=4,Final_neural_access=False,real_fits=0))


if __name__=='__main__':run()
