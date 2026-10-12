"""Check actual decoded paths against their original object versions; no values."""
import json
import h5py
from acquire import HERE
from header_metadata import RangeReader, validate_dataset, hard_object
from register import verify

def main():
    verify()
    directory = HERE / 'metadata/link_audit'
    directory.mkdir(exist_ok=True)
    items = json.loads((HERE/'metadata/allen_header_capability.json').read_text())
    for item in sorted(items, key=lambda r:r['session_id']):
        path = directory / (item['session_id'] + '.json')
        if path.exists(): continue
        original = json.loads((HERE/'metadata/headers_code1'/path.name).read_text())
        paths = [p for p in ('/session_start_time','/timestamps_reference_time') if p in original]
        paths += ['/intervals/'+ name+'/'+ field for name, table in original['intervals'].items()
                  for field in ('start_time','stop_time') if field in table]
        reader = RangeReader('https://api.brain-map.org/api/v2/well_known_file_download/'+item['file_id'],
                             int(item['content_range'].split('/')[-1]), etag=item['etag'])
        result = {'session_id':item['session_id'], 'paths':paths, 'decoded_values':False, 'pass':False}
        try:
            with h5py.File(reader,'r') as file:
                for p in paths: validate_dataset(file,p)
                for p in ('/acquisition','/intervals'): hard_object(file,p)
            result['pass'] = True
        except Exception as exc:
            result['error'] = type(exc).__name__ + ': ' + str(exc)[:250]
        result['ranges'] = reader.ranges
        result['bytes'] = reader.used
        reader.http.close()
        path.write_text(json.dumps(result,indent=2))
        print(json.dumps({'session':item['session_id'],'pass':result['pass'],'bytes':reader.used}),flush=True)

if __name__=='__main__': main()
