"""Explicitly authorized trusted full-record decoder, exporting C only."""
import datetime
import json
from pathlib import Path
import numpy as np
from .source import R,P,E,BUCKET,read,dump,sha,source_rows,frozen_definitions
from .source_integrity import conditional_download,verify_etag_bytes
from .physiology import unit_qc

READER_REQUIRED={'source.py','metadata_access.py','metadata_qc.py','reader.py','physiology.py',
                 'native_table.py','features.py','source_integrity.py','SOURCE_FILE_FREEZE.json',
                 'FINAL_SOURCE_HEADER_FREEZE.json','results/FINAL_METADATA_GATE.json'}


def check_reader_gate(gate):
    if not gate.get('approved_C_only') or not READER_REQUIRED<=set(gate.get('hashes',{})):
        raise PermissionError('Complete reviewed C-reader gate required')
    for rel,h in gate['hashes'].items():
        if sha(P/rel)!=h:raise PermissionError('C-reader frozen input mismatch: '+rel)
    item=gate['independent_review'];receipt=read(R/item['path'])
    if sha(R/item['path'])!=item['sha256']:raise PermissionError('Review identity mismatch')
    if (receipt['decision']!='ACCEPTED_C_ONLY_READER' or type(receipt['open_P0']) is not int
        or receipt['open_P0']!=0 or type(receipt['open_P1']) is not int or receipt['open_P1']!=0
        or receipt['approved_C_only'] is not True or receipt['hashes']!=gate['hashes']):
        raise PermissionError('Review does not approve this exact C-only state')
    if sha(R/receipt['report_path'])!=receipt['report_sha256']:raise PermissionError('Review report mismatch')
    frozen_definitions()


def authorize(subject,role,row,state):
    if role!='C' or row not in source_rows() or subject!=row['subject']:
        raise PermissionError('Trusted preparation exports original Final C only')
    if not state['result']['prephysiology_possible']:raise PermissionError('Metadata admission unavailable')


def project_C(times,labels,start,stop,cluster_count,support,fs):
    """Only classification touches full-record values; no D summaries/output."""
    if len(times)!=len(labels) or not np.issubdtype(labels.dtype,np.integer):
        raise ValueError('Source array identity mismatch')
    ts=[];ls=[]
    for lo in range(0,len(times),1000000):
        chunk=np.asarray(times[lo:lo+1000000])
        # A nonfinite timestamp cannot be assigned to C or non-C: generic source error.
        # No count, value, location, inferred role or D-finite statistic is exported.
        if not np.isfinite(chunk).all():raise ValueError('UNASSIGNABLE_SOURCE_TIMESTAMP')
        take=(chunk>=start)&(chunk<stop)
        ts.append(chunk[take]);ls.append(np.asarray(labels[lo:lo+1000000])[take])
    ct=np.concatenate(ts).astype(np.float64) if ts else np.empty(0,np.float64)
    cl=np.concatenate(ls) if ls else np.empty(0,labels.dtype)
    if len(ct) and (not (np.diff(ct)>=0).all() or cl.min()<0 or cl.max()>=cluster_count):
        raise ValueError('C_ONLY_SOURCE_ORDER_OR_CLUSTER_ERROR')
    if len(ct) and (ct[0]<support[0]-1/fs or ct[-1]>support[1]+1/fs):
        raise ValueError('C_ONLY_SOURCE_SUPPORT_ERROR')
    return ct,cl


def neural_file(client,row,file):
    assert row in source_rows() and file in row['files'] and file['role'] in ('times','clusters')
    pin=next(x for x in read(P/'FINAL_SOURCE_HEADER_FREEZE.json')['files'] if x['key']==file['key'])
    target=P/'work/neural'/row['eid']/Path(file['key']).name
    target.parent.mkdir(parents=True,exist_ok=True)
    conditional_download(client,BUCKET,file,pin,target)
    assert verify_etag_bytes(target.read_bytes(),pin['etag'])
    return target,dict(role=file['role'],key=file['key'],bytes=file['bytes'],sha256=sha(target),
        object_version_id=pin.get('version_id'),etag=pin['etag'],whole_recording_physical_body=True,
        receipt_scope='Raw source custody only; no D spike totals/statistics or neural analysis')


def run():
    from one.remote.aws import get_s3_public
    check_reader_gate(read(P/'C_READER_GATE.json'))
    assert not (P/'results/FINAL_C_QC_GATE.json').exists()
    s3,bucket=get_s3_public();assert bucket==BUCKET
    labs={r['subject']:r['lab'] for r in __import__('paper15_final1.source',fromlist=['roster']).roster()}
    out=[]
    metadata_gate=read(P/'results/FINAL_METADATA_GATE.json')
    assert metadata_gate['at_least_six_metadata_possible']
    for row in source_rows():
        subject=row['subject']
        if subject not in metadata_gate['possible_subjects']:
            out.append(dict(subject=subject,lab=labs[subject],admitted=False,reason='IMMUTABLE_FINAL_SOURCE_EXCLUSION',C_neural_access=False));continue
        state=read(P/'metadata'/(subject+'_task.json'))
        if not state['result']['prephysiology_possible']:
            out.append(dict(subject=subject,lab=labs[subject],admitted=False,reason='FROZEN_METADATA_COVERAGE_OR_UNITS',C_neural_access=False));continue
        authorize(subject,'C',row,state)
        path=P/'results'/(subject+'_C_QC.json');assert not path.exists(),'C preparation attempt already exists; no silent rerun'
        record=dict(subject=subject,role='C',status='STARTED',files=[],started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            reader_gate_sha256=sha(P/'C_READER_GATE.json'),D_scientific_projection=False)
        dump(path,record)
        try:
            files={}
            for file in row['files']:
                if file['role'] not in ('times','clusters'):continue
                source,receipt=neural_file(s3.meta.client,row,file)
                files[file['role']]=source;record['files'].append(receipt);dump(path,record)
            tr=state['trials'];start,stop=state['result']['partitions']['C']
            ct,cl=project_C(np.load(files['times'],mmap_mode='r',allow_pickle=False),np.load(files['clusters'],mmap_mode='r',allow_pickle=False),
                tr[start]['intervals_0'],tr[stop-1]['intervals_1'],len(state['native_uuid_list']),
                state['result']['recording_sync_support'],state['result']['fs'])
            ids=np.flatnonzero(np.asarray(state['valid'])&(np.asarray(state['roles'])=='C'))
            epochs=np.array([[tr[i]['stimOn_times']-.5,tr[i]['stimOn_times']+.5] for i in ids])
            from .anatomy import candidate_units
            units=candidate_units(state)
            metrics,ranked=unit_qc(ct,cl,units,[state['native_uuid_list'][u] for u in units],ids,epochs,stop)
            # Pure reused physiology uses historical A names internally; expose explicit C names.
            metrics=[{k.replace('original_A_','original_C_').replace('A_','C_'):v for k,v in m.items()} for m in metrics]
            selected=ranked[:8] if len(ranked)>=8 else []
            export=P/'work/C_exports'/(subject+'.npz');export.parent.mkdir(parents=True,exist_ok=True);assert not export.exists()
            np.savez_compressed(export,times=ct,labels=cl,trial_ids=ids,epochs=epochs)
            record.update(status='COMPLETE_C_ONLY',physiology=metrics,ranking=[x['cluster_id'] for x in ranked],
                selected_unit_ids=[x['cluster_id'] for x in selected],selected_unit_uuids=[x['uuid'] for x in selected],
                qualified_units=len(ranked),C_epochs=len(ids),C_export_sha256=sha(export),admitted=len(selected)==8,
                low_level_scope='Whole-record times/cluster arrays internally decoded only to classify and export C; no D scientific arrays/stats/streams',
                all_C_role_source_observations_retained=True,completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            dump(path,record)
            out.append(dict(subject=subject,lab=labs[subject],admitted=len(selected)==8,C_qualified_units=len(ranked),
                C_epochs=len(ids),D_metadata_epochs=state['result']['structural_eligible_epochs']['D'],
                C_neural_access=True,reason=None if selected else 'FEWER_THAN_8_C_QUALIFIED_UNITS'))
            print(subject,'C qualified',len(ranked),'admitted',bool(selected),flush=True)
        except Exception as exc:
            record.update(status='FAILED_C_SOURCE_IMMUTABLE',error=type(exc).__name__+': '+str(exc));dump(path,record);raise
    valid=[r for r in out if r['admitted']];counts={lab:sum(r['lab']==lab for r in valid) for lab in sorted({r['lab'] for r in valid})}
    dump(P/'results/FINAL_C_QC_GATE.json',dict(subjects=out,eligible_mice=len(valid),eligible_labs=len(counts),lab_counts=counts,
        primary_coverage=len(valid)==8 and len(counts)>=4 and max(counts.values(),default=0)<=len(valid)/2,
        descriptive_cohort_eligible=len(valid)>=6,C_QC_completed=True,real_fits=0,D_neural_scientific_access=False))


if __name__=='__main__':run()
