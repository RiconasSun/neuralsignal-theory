"""Read only official digital clock files and labelled barcode edges."""
import ast
import io
import json
from datetime import datetime,timezone
import sys
from pathlib import Path
import h5py
import numpy as np
import requests
from register import HERE,ROOT,sha,verify
from clock import check_policy,decode,unwrap,probe_segments,affine
sys.path.insert(0,str(ROOT/'paper12'))
from header_metadata import hard_object

def old(name):return json.loads((ROOT/'paper12/metadata'/name).read_text())

def digital_object(key):
    return key.startswith('visual-coding-neuropixels/raw-data/') and key.rsplit('/',1)[-1] in ('sync.h5','event_timestamps.npy','channel_states.npy')

def acquire(item,name,budget,offline=False):
    if not digital_object(item['key']) or item['bytes']>budget:raise RuntimeError('Forbidden or oversized digital object')
    directory=HERE/'sync_cache' if name.endswith('_sync') else HERE/'metadata/digital'
    directory.mkdir(exist_ok=True,parents=True)
    path=directory/(name+'.receipt')
    old_path=HERE/'metadata/digital'/(name+'.receipt')
    url='https://allen-brain-observatory.s3.us-west-2.amazonaws.com/'+item['key']
    cached=old_path if old_path.exists() else path
    if cached.exists():
        receipt=json.loads((HERE/'metadata/digital'/(name+'.json')).read_text())
        if receipt['url']!=url or receipt['etag']!=item['etag_not_assumed_checksum'] or receipt['bytes']!=item['bytes']:
            raise RuntimeError('Cached digital provenance mismatch')
        if cached.stat().st_size!=item['bytes'] or sha(cached)!=receipt['sha256']:raise RuntimeError('Cached digital bytes changed')
        return cached
    if offline:raise RuntimeError('Frozen digital cache absent; offline audit never downloads')
    with requests.get(url,headers={'If-Match':item['etag_not_assumed_checksum']},stream=True,timeout=45) as response:
        response.raise_for_status()
        if response.headers.get('ETag')!=item['etag_not_assumed_checksum']:raise RuntimeError('Frozen digital object changed')
        chunks=[];size=0
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>budget:raise RuntimeError('Digital transport budget exceeded')
            chunks.append(chunk)
        if size!=item['bytes']:raise RuntimeError('Digital object length mismatch')
        payload=b''.join(chunks)
    path.write_bytes(payload)
    receipt_path=HERE/'metadata/digital'/(name+'.json')
    receipt_path.parent.mkdir(exist_ok=True,parents=True)
    receipt_path.write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),
                    'url':url,'bytes':size,'etag':item['etag_not_assumed_checksum'],'sha256':sha(path)},indent=2))
    return path

def read_sync(path):
    with h5py.File(path,'r') as file:
        meta_ds=hard_object(file,'/meta')
        if meta_ds.ndim!=0 or meta_ds.dtype.kind not in 'SO':raise RuntimeError('Undefined sync metadata schema')
        metadata=ast.literal_eval(meta_ds[()].decode())
        labels=metadata['line_labels'];bit=next((labels.index(x) for x in ('barcode','barcodes','barcode_ephys') if x in labels),None)
        if bit is None:raise RuntimeError('Undefined barcode line')
        data=hard_object(file,'/data')
        if data.ndim!=2 or data.shape[1]!=2 or data.dtype!=np.dtype('uint32') or data.size*4>25000000:
            raise RuntimeError('Undefined/oversized digital sync schema')
        counters=np.asarray(data[:,0]);barcode_bit=(np.asarray(data[:,1])&(1<<bit))!=0
        samples,wraps=unwrap(counters)
        ni=metadata['ni_daq']
        frequency=float(ni.get('sample_freq',ni.get('counter_output_freq')))
        if ni['counter_bits']!=32 or frequency<=0:raise RuntimeError('Undefined native sync clock')
        edges=np.r_[0,np.diff(barcode_bit.astype(int))]
        times,codes,mismatch=decode(samples[edges==1]/frequency,samples[edges==-1]/frequency)
        return {'barcode_times':times.tolist(),'barcode_codes':codes.astype(int).tolist(),
                'barcode_on_seconds':(samples[edges==1]/frequency).tolist(),
                'barcode_off_seconds':(samples[edges==-1]/frequency).tolist(),
                'sample_frequency_hz':frequency,'counter_wraps':wraps,'digital_event_rows':int(data.shape[0]),
                'first_digital_event_seconds':float(samples[0]/frequency),'last_digital_event_seconds':float(samples[-1]/frequency),
                'sync_metadata':{k:metadata.get(k) for k in ('start_time','stop_time','total_samples','sampling_type')},
                'counter_monotone':bool(np.all(np.diff(samples)>=0)), 'barcode_bit':bit,
                'parser_length_mismatch':mismatch,'other_digital_bits_interpreted':False,'analog_values_decoded':False}

def read_edges(path):
    with path.open('rb') as stream:
        version=np.lib.format.read_magic(stream)
        if version==(1,0):shape,fortran,dtype=np.lib.format.read_array_header_1_0(stream)
        elif version==(2,0):shape,fortran,dtype=np.lib.format.read_array_header_2_0(stream)
        else:raise RuntimeError('Unsupported digital NPY version')
        if len(shape)!=1 or dtype.kind not in 'iu' or dtype.hasobject:raise RuntimeError('Undefined native edge schema')
        if stream.tell()+np.prod(shape)*dtype.itemsize!=path.stat().st_size:raise RuntimeError('NPY payload length mismatch')
    return np.load(path,allow_pickle=False)

def main(smoke=False,output=None,offline=False):
    verify();check_policy()
    inventory=old('allen_raw_inventory.json');probes=old('allen_probes.receipt')['msg']
    sessions=old('allen_sessions.receipt')['msg']
    sid_order=sorted(r['id'] for r in sessions if r['stimulus_name']=='functional_connectivity')+sorted(r['id'] for r in sessions if r['stimulus_name']!='functional_connectivity')
    if smoke:sid_order=sid_order[:1]
    directory=Path(output) if output else HERE/'results/digital_code2';directory.mkdir(exist_ok=True,parents=True)
    for sid in sid_order:
        output=directory/(sid+'.json')
        if output.exists():continue
        objects=next(r['objects'] for r in inventory if r['session_id']==sid)
        result={'session_id':sid,'probes':[],'native_continuity_certified':False}
        try:
            sync=next(o for o in objects if o['key'].endswith('/sync.h5'))
            result['master']=read_sync(acquire(sync,sid+'_sync',25000000,offline=offline))
        except Exception as exc:
            result['master_error']=type(exc).__name__+': '+str(exc)[:250]
        for probe in (p for p in probes if p['ecephys_session_id']==sid):
            p={'probe_id':probe['id'],'name':probe['name'],'api_sampling_rate_hz':float(probe['sampling_rate']),
               'native_continuity_certified':False,'clock_pass':False}
            try:
                prefix='visual-coding-neuropixels/raw-data/'+sid+'/'+probe['id']+'/'
                ts=next(o for o in objects if o['key']==prefix+'event_timestamps.npy')
                cs=next(o for o in objects if o['key']==prefix+'channel_states.npy')
                times=read_edges(acquire(ts,sid+'_'+probe['id']+'_timestamps',5000000,offline=offline))
                states=read_edges(acquire(cs,sid+'_'+probe['id']+'_states',5000000,offline=offline))
                bt,bc,splits,diagnostics=probe_segments(times,states)
                p.update(diagnostics);p['split_times_seconds']=splits;p['barcode_count']=len(bt)
                p['segments']=[]
                if 'master' not in result:raise RuntimeError('No master clock')
                for i,start in enumerate(splits):
                    end=splits[i+1] if i+1<len(splits) else float('inf')
                    mask=(bt>start)&(bt<end)
                    d=affine(result['master']['barcode_times'],result['master']['barcode_codes'],bt[mask],bc[mask])
                    d['segment_start_native_seconds']=start;d['segment_stop_native_seconds']=end if np.isfinite(end) else None
                    p['segments'].append(d)
                p['clock_pass']=bool(p['segments'] and all(s['pass'] for s in p['segments']))
                band=next((o for o in objects if o['key']==prefix+'spike_band.dat'),None)
                if band:
                    p['raw_band_bytes']=band['bytes'];p['conditional_int16_384_samples']=band['bytes']//768
                    p['bytes_divisible_by_768']=band['bytes']%768==0
                    p['conditional_serialized_duration_seconds']=band['bytes']/768/30000
                    p['native_start_index_verified']=False
                p['native_observation_envelope_certified']=False
            except Exception as exc:p['error']=type(exc).__name__+': '+str(exc)[:250]
            result['probes'].append(p)
        output.write_text(json.dumps(result,indent=2,sort_keys=True))
        print(json.dumps({'session':sid,'probes':len(result['probes']),'clock_pass':sum(p['clock_pass'] for p in result['probes']),
                          'master_error':result.get('master_error')}),flush=True)

if __name__=='__main__':main('--smoke' in sys.argv)
