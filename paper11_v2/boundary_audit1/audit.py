"""Sealed metadata-only boundary audit. No model or physiological accessor."""
import csv
import math
import re
import subprocess
import sys
from datetime import datetime, timezone

import h5py
import numpy as np
import register_sources as prov

ROOT, HERE, OUT = prov.ROOT, prov.HERE, prov.OUT
sys.path.insert(0, str(ROOT/'paper11_v2/scripts'))
from run_r0 import RangeReader

ROOT_TEXT = {'session_description','session_start_time','timestamps_reference_time'}
EVENT_TEXT = {'acquisition/events/description','acquisition/events/comments'}


def scalar(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    if isinstance(value, np.generic):
        return scalar(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Nonfinite scalar metadata')
    if isinstance(value, (str,int,float,bool)):
        return value
    raise ValueError('Unknown scalar representation')


def native(file, path):
    node = file
    for part in path.split('/'):
        if not isinstance(node.get(part, getlink=True), h5py.HardLink):
            raise ValueError('Missing/soft/external link denied')
        node = node[part]
    return node


def decode(file, path, index, ledger, raw_paths=()):
    if path.startswith(('units/','intervals/','stimulus/','processing/')):
        raise ValueError('Protected physiological/outcome path')
    allowed = (path in ROOT_TEXT or path in EVENT_TEXT) and index == 'scalar'
    allowed |= path == 'acquisition/events/data' and type(index) is int and index == 0
    allowed |= path == 'acquisition/events/timestamps' and type(index) is int and index in (0,-1)
    raw = path in raw_paths and len(path.split('/'))==3 and path.split('/')[0]=='acquisition' and path.split('/')[-1] in ('description','comments','starting_time','timestamps')
    if raw:
        group = native(file,'/'.join(path.split('/')[:2]))
        raw = scalar(group.attrs.get('neurodata_type',''))=='ElectricalSeries'
    allowed |= raw and (index == 'scalar' or type(index) is int and index in (0,-1))
    if not allowed:
        raise ValueError('Forbidden decode before HDF access')
    node = native(file,path)
    if not isinstance(node,h5py.Dataset):
        raise ValueError('Dataset required')
    if index == 'scalar':
        if node.shape != () or node.size != 1:
            raise ValueError('Bounded scalar required')
        value = node[()]
    else:
        if node.ndim != 1 or node.size < 2:
            raise ValueError('Endpoint vector required')
        value = node[index]
    value = scalar(value)
    if isinstance(value,str) and len(value.encode()) > 16384:
        raise ValueError('Metadata text budget exceeded')
    ledger.append({'path':path,'index':index,'value':value})
    return value


def label(value):
    text = str(value)
    m = re.fullmatch(r'\s*(\d+)(?:\.0)?\s*',text)
    return int(m.group(1)) if m else None


def contain(start,stop,trials):
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in [start,stop]) or stop <= start:
        raise ValueError('Invalid boundary')
    if not trials:
        raise ValueError('Empty target')
    for t in trials:
        x = t['start']
        if type(x) not in (int,float) or not math.isfinite(x):
            raise ValueError('Invalid epoch')
        if x < start or x+1 > stop:
            return False
    return True


def time_attrs(node):
    return {k:scalar(node.attrs[k]) for k in ['unit','conversion','offset','rate'] if k in node.attrs}


def seconds(attrs):
    return attrs.get('unit') in ('s','seconds') and attrs.get('conversion',1)==1 and attrs.get('offset',0)==0


def assess(meta,old,trials):
    if not seconds(meta['event_timestamp_attributes']):
        return {'verdict':'INCONCLUSIVE','reason':'Unknown native event time unit/scale/offset'}
    start,stop = meta['event_first_time'],meta['event_last_time']
    inside = contain(start,stop,trials)
    if (old.get('status')=='DOCUMENTED_CONTINUOUS_SUPPORT'
            and label(meta['first_TTL'])==55
            and start==old.get('experiment_start') and stop==old.get('experiment_end')):
        return {'verdict':'PASS' if inside else 'FAIL',
                'reason':'Source-backed original55/66experiment envelope; no raw dropout certificate',
                'documented_support_only':True,'all_scored_epochs_contained':inside}
    # Native raw metadata is inventoried but cannot establish a gap-free clock
    # mapping from endpoints alone. No source-specific raw witness was supplied.
    return {'verdict':'INCONCLUSIVE','reason':'No independent complete raw-recording boundary/common-clock/continuity witness; event1/99is not recordingstart',
            'event_span_contains_scored_epochs':inside,'raw_streams_present':bool(meta['raw_streams'])}


def inspect(file):
    ledger, metadata = [], {'root':{},'event_text':{},'raw_streams':[], 'decode_ledger':[]}
    metadata['nwb_version'] = scalar(file.attrs['nwb_version']) if 'nwb_version' in file.attrs else None
    for path in sorted(ROOT_TEXT):
        if path in file:
            metadata['root'][path] = decode(file,path,'scalar',ledger)
    for path in sorted(EVENT_TEXT):
        if path in file:
            metadata['event_text'][path] = decode(file,path,'scalar',ledger)
    events = native(file,'acquisition/events')
    for field in ('description','comments'):
        if field in events.attrs:
            metadata['event_text']['attribute:'+field] = scalar(events.attrs[field])
    metadata['first_TTL'] = decode(file,'acquisition/events/data',0,ledger)
    ts = native(file,'acquisition/events/timestamps')
    metadata['event_timestamp_attributes'] = time_attrs(ts)
    metadata['event_timestamp_shape'] = list(ts.shape)
    metadata['event_first_time'] = decode(file,'acquisition/events/timestamps',0,ledger)
    metadata['event_last_time'] = decode(file,'acquisition/events/timestamps',-1,ledger)
    acquisition = native(file,'acquisition')
    metadata['acquisition_groups'] = []
    for name in sorted(acquisition):
        link = acquisition.get(name,getlink=True)
        if not isinstance(link,h5py.HardLink):
            metadata['acquisition_groups'].append({'name':name,'link':'DENIED'}); continue
        group = acquisition[name]
        dtype = scalar(group.attrs['neurodata_type']) if 'neurodata_type' in group.attrs else None
        metadata['acquisition_groups'].append({'name':name,'neurodata_type':dtype})
        if dtype != 'ElectricalSeries':
            continue
        base = 'acquisition/'+name
        stream = {'name':name,'neurodata_type':dtype,'continuity_certified':False,'clock_mapping_certified':False}
        if 'data' in group:
            data = native(file,base+'/data')
            stream['signal_shape'] = list(data.shape)  # No signal values.
        for field in ['description','comments','starting_time','timestamps']:
            if field not in group:
                continue
            path = base+'/'+field
            node = native(file,path)
            indices = (0,-1) if field=='timestamps' else ('scalar',)
            stream[field] = [decode(file,path,i,ledger,raw_paths=(path,)) for i in indices]
            if field in ('timestamps','starting_time'):
                stream[field+'_attributes'] = time_attrs(node)
        metadata['raw_streams'].append(stream)
    if len(ledger)>128:
        raise ValueError('Endpoint budget exceeded')
    metadata['decode_ledger'] = ledger
    return metadata


def register():
    prov.verify()
    target = OUT/'implementation_registration.json'
    if target.exists():
        verify(); return
    files = [HERE/'audit.py',HERE/'test_boundary.py',HERE/'SOURCE_AUDIT.md',HERE/'reproduce.ps1']
    files += list((OUT/'sources').iterdir())
    prov.save(target, {'registered_utc':datetime.now(timezone.utc).isoformat(),
        'before_tests_and_new_NWB_access':True,'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):prov.sha(p) for p in files if p.is_file()},
        'protocol_registration_sha256':prov.sha(OUT/'protocol_registration.json'),
        'rule':'Exact frozen protocol; source-backed original55/66envelope or independently documented raw support; no newraw witness found;99unknown',
        'external_spikes_authorized':False,'R2_remains_FAIL':True})
    verify()


def verify():
    prov.verify()
    reg = prov.load(OUT/'implementation_registration.json')
    for p,digest in reg['source_sha256'].items():
        if prov.sha(ROOT/p)!=digest:
            raise RuntimeError('Frozen implementation/source changed:'+p)
    if reg['protocol_registration_sha256']!=prov.sha(OUT/'protocol_registration.json'):
        raise RuntimeError('Protocol registration changed')


def tests():
    result = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_boundary.py','-v'],capture_output=True,text=True)
    print(result.stdout+result.stderr)
    return result


def execute():
    import requests
    verify()
    marker = OUT/'execution_started.json'
    if marker.exists():
        raise RuntimeError('Audit already attempted; no overwrite')
    prov.save(marker,{'started_utc':datetime.now(timezone.utc).isoformat(),'metadata_only':True})
    test = tests()
    (OUT/'tests.log').write_text(test.stdout+test.stderr,encoding='utf-8')
    if test.returncode:
        raise RuntimeError('Controlled tests failed; no NWB access')
    lock = prov.load(ROOT/'paper11_v2/results/R0_schema1/final_validation_lock.json')
    prior = prov.load(ROOT/'paper11_v2/results/R2_external_support_code2/support_audit.json')
    old = {s['asset_id']:s for s in prior['sessions']}
    sessions = lock['eligible_sessions']
    if len(sessions)!=52 or len(old)!=52 or set(old)!={s['asset_id'] for s in sessions}:
        raise RuntimeError('Exact pinned52roster required')
    class TimedSession:
        def __init__(self): self.session=requests.Session()
        def get(self,*args,**kwargs):
            kwargs['timeout']=60
            return self.session.get(*args,**kwargs)
    transport = TimedSession()
    rows=[]
    for s in sorted(sessions,key=lambda x:x['asset_id']):
        reader=RangeReader('https://api.dandiarchive.org/api/assets/'+s['asset_id']+'/download/',s['size'],transport)
        row={k:s[k] for k in ['asset_id','path','patient','size','published_sha256']}
        try:
            with h5py.File(reader,'r') as f:
                meta=inspect(f)
            row.update(metadata=meta,**assess(meta,old[s['asset_id']],s['valid_recognition_trials']))
        except Exception as e:
            row.update(verdict='INCONCLUSIVE',reason='Metadata audit could not complete',error_class=type(e).__name__)
        row['range_receipts']=reader.receipts
        row['fetched_bytes']=reader.fetched
        rows.append(row)
        prov.save(OUT/'sessions'/(s['asset_id']+'.json'),row)
        print(s['asset_id'],row['verdict'],row['reason'],flush=True)
    verdict='FAIL' if any(r['verdict']=='FAIL' for r in rows) else 'PASS' if all(r['verdict']=='PASS' for r in rows) else 'INCONCLUSIVE'
    gate={'mission':'P11-v2-R2-BOUNDARY-AUDIT-1','audit_verdict':verdict,
          'sessions':52,'supported':sum(r['verdict']=='PASS' for r in rows),
          'inconclusive':sum(r['verdict']=='INCONCLUSIVE' for r in rows),'contradictions':sum(r['verdict']=='FAIL' for r in rows),
          'R2_original_gate':'FAIL','external_spikes_accessed':False,'final_physiological_holdout_accessed':False,
          'new_final_trial_or_response_values_read':False,'R2_resumed':False,'R3_executed':False,'tests_exit_code':test.returncode,
          'split_sha256':prov.load(HERE/'protocol.json')['split_sha256'],'source_hashes_unchanged':True,
          'scope':'Documented observation support only; not physiological eligibility/dropout/clock-error measurement'}
    verify()
    prov.save(OUT/'gate_result.json',gate)
    with (OUT/'session_summary.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['asset_id','path','patient','verdict','reason','fetched_bytes'])
        writer.writeheader();writer.writerows({k:r.get(k) for k in writer.fieldnames} for r in rows)
    prov.save(OUT/'QC.json',{'gate':gate,'range_bytes':sum(r['fetched_bytes'] for r in rows),'exact52identity':True,
             'no_full_file_checksums_claimed':True,'opaque_adjacent_bytes':'Buffered but never decoded; not zero transport claim',
             'raw_acquisition_stream_counts':[len(r.get('metadata',{}).get('raw_streams',[])) for r in rows]})
    prov.save(OUT/'artifact_lock.json',{'sha256':{str(p.relative_to(ROOT)).replace('\\','/'):prov.sha(p) for p in OUT.rglob('*') if p.is_file()}})
    print(gate)


def replay():
    verify()
    for p,digest in prov.load(OUT/'artifact_lock.json')['sha256'].items():
        if prov.sha(ROOT/p)!=digest:raise RuntimeError('Saved output changed:'+p)
    lock=prov.load(ROOT/'paper11_v2/results/R0_schema1/final_validation_lock.json')
    old={s['asset_id']:s for s in prov.load(ROOT/'paper11_v2/results/R2_external_support_code2/support_audit.json')['sessions']}
    for s in lock['eligible_sessions']:
        row=prov.load(OUT/'sessions'/(s['asset_id']+'.json'))
        if 'metadata' in row:
            check=assess(row['metadata'],old[s['asset_id']],s['valid_recognition_trials'])
            if any(row[k]!=v for k,v in check.items()):raise RuntimeError('Verdict replay mismatch')
    test=tests()
    prov.save(OUT/'replay_receipt.json',{'exit_code':test.returncode,'saved_sessions_verified':52,
              'original_R2_gate':'FAIL','no_network_or_neural_access':True,'audit_verdict':prov.load(OUT/'gate_result.json')['audit_verdict']})
    return test.returncode


if __name__=='__main__':
    action=sys.argv[1]
    sys.exit({'register':register,'execute':execute,'replay':replay,'verify':verify}[action]() or 0)
