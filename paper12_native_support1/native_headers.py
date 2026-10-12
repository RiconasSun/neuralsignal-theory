"""NWB stimulus, exclusion and probe metadata only; no units/analog values."""
import json
import re
import sys
from pathlib import Path
import h5py
import numpy as np
from register import HERE,ROOT,verify,sha
from clock import check_policy
sys.path.insert(0,str(ROOT/'paper12'))
from header_metadata import RangeReader,hard_object

FIELDS=('start_time','stop_time','stimulus_block','stimulus_index','frame','orientation','temporal_frequency','contrast')
TABLES=('drifting_gratings_75_repeats_presentations','natural_movie_one_more_repeats_presentations',
        'drifting_gratings_presentations','natural_movie_one_presentations','invalid_times')

def permitted(path):
    if path in ('/session_start_time','/timestamps_reference_time'):return True
    parts=path.strip('/').split('/')
    if len(parts)==3 and parts[0]=='intervals' and parts[1] in TABLES:
        return parts[2] in FIELDS or (parts[1]=='invalid_times' and parts[2] in ('tags','tags_index'))
    return bool(re.fullmatch(r'/general/(extracellular_ephys|devices)/probe[^/]+/(description|location|sampling_rate|lfp_sampling_rate|has_lfp_data)',path))

def read(file,path):
    if not permitted(path):raise RuntimeError('Forbidden metadata value path')
    data=hard_object(file,path)
    validate_type(data,path)
    if data.ndim>1 or data.size>150000:raise RuntimeError('Metadata shape budget')
    if data.ndim==0:value=data[()]
    else:
        step=max(1,65536//data.dtype.itemsize)
        value=np.concatenate([data[i:i+step] for i in range(0,data.size,step)]) if data.size else np.array([],dtype=data.dtype)
    if isinstance(value,bytes):return value.decode()
    if isinstance(value,np.ndarray):return [x.decode() if isinstance(x,bytes) else x.item() if isinstance(x,np.generic) else x for x in value]
    return value.item() if isinstance(value,np.generic) else value

def validate_type(data,path):
    if not isinstance(data,h5py.Dataset):raise RuntimeError('Expected metadata dataset')
    field=path.rsplit('/',1)[-1]
    text=field in ('session_start_time','timestamps_reference_time','tags','location','description')
    if text:
        if h5py.check_string_dtype(data.dtype) is None:raise RuntimeError('Expected verified HDF string metadata')
    elif data.dtype.kind not in 'fiu' or data.dtype.hasobject:
        raise RuntimeError('Expected numeric timing/stimulus/index metadata')

def inspect(item):
    reader=RangeReader('https://api.brain-map.org/api/v2/well_known_file_download/'+item['file_id'],
                       int(item['content_range'].split('/')[-1]),max_bytes=4194304,etag=item['etag'])
    result={'session_id':item['session_id'],'tables':{},'probe_metadata':{},'decoded_neural_values':False}
    try:
        with h5py.File(reader,'r') as file:
            result['root_attributes']={k:str(v) for k,v in file.attrs.items()}
            for path in ('/session_start_time','/timestamps_reference_time'):
                if path in file:result[path]=read(file,path)
            for root in ('/general/extracellular_ephys','/general/devices'):
                if root in file:
                    group=hard_object(file,root)
                    result[root+'_names']=list(group.keys())
                    for name in group.keys():
                        if not name.startswith('probe'):continue
                        sub=hard_object(file,root+'/'+name)
                        result['probe_metadata'][root+'/'+name]={'attributes':{k:str(v) for k,v in sub.attrs.items()},'fields':{}}
                        for field in ('description','location','sampling_rate','lfp_sampling_rate','has_lfp_data'):
                            path=root+'/'+name+'/'+field
                            if path in file:result['probe_metadata'][root+'/'+name]['fields'][field]=read(file,path)
            if '/intervals' in file:
                result['all_interval_names']=list(hard_object(file,'/intervals').keys())
            for name in TABLES:
                root='/intervals/'+name
                if root not in file:continue
                group=hard_object(file,root);record={}
                fields=FIELDS+('tags','tags_index') if name=='invalid_times' else FIELDS
                for field in fields:
                    path=root+'/'+field
                    if path in file:record[field]=read(file,path)
                result['tables'][name]=record
    except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)[:250]
    result['transport_bytes']=reader.used;result['ranges']=reader.ranges
    reader.http.close()
    return result

def main(smoke=False):
    verify();check_policy()
    items=json.loads((ROOT/'paper12/metadata/allen_header_capability.json').read_text())
    session=json.loads((ROOT/'paper12/metadata/allen_sessions.receipt').read_text())['msg']
    priority={r['id']:r['stimulus_name']=='functional_connectivity' for r in session}
    items=sorted(items,key=lambda r:(not priority[r['session_id']],r['session_id']))
    if smoke:items=items[:1]
    directory=HERE/'metadata/native_headers';directory.mkdir(exist_ok=True,parents=True)
    for item in items:
        path=directory/(item['session_id']+'.json')
        if path.exists() or Path(str(path)+'.gz').exists():continue
        result=inspect(item);path.write_text(json.dumps(result,indent=2,sort_keys=True))
        print(json.dumps({'session':item['session_id'],'tables':list(result['tables']),
                          'bytes':result['transport_bytes'],'error':result.get('error')}),flush=True)

if __name__=='__main__':main('--smoke' in sys.argv)
