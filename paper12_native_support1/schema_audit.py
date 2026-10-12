"""Same-object schema verification for every previously decoded NWB value path."""
import json
import h5py
from native_headers import FIELDS,TABLES,permitted,validate_type,RangeReader,hard_object
from register import HERE,ROOT,verify
from storage import load

if __name__=='__main__':
    verify();directory=HERE/'metadata/schema_checks';directory.mkdir(exist_ok=True)
    items=json.loads((ROOT/'paper12/metadata/allen_header_capability.json').read_text())
    for item in sorted(items,key=lambda r:r['session_id']):
        target=directory/(item['session_id']+'.json')
        if target.exists():continue
        prior=load(HERE/'metadata/native_headers'/target.name)
        reader=RangeReader('https://api.brain-map.org/api/v2/well_known_file_download/'+item['file_id'],
                           int(item['content_range'].split('/')[-1]),max_bytes=4194304,etag=item['etag'])
        paths=[p for p in ('/session_start_time','/timestamps_reference_time') if p in prior]
        paths += ['/intervals/'+name+'/'+field for name,table in prior['tables'].items() for field in table]
        result={'session_id':item['session_id'],'decoded_values':False,'pass':False,'schema':{}}
        try:
            with h5py.File(reader,'r') as file:
                for path in paths:
                    if not permitted(path):raise RuntimeError('Forbidden saved path')
                    data=hard_object(file,path);validate_type(data,path)
                    result['schema'][path]={'dtype':str(data.dtype),'shape':list(data.shape)}
            result['pass']=True
        except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)[:250]
        result['ranges']=reader.ranges;result['transport_bytes']=reader.used;reader.http.close()
        target.write_text(json.dumps(result,indent=2,sort_keys=True))
        print(json.dumps({'session':item['session_id'],'pass':result['pass'],'error':result.get('error')}),flush=True)
