"""Bounded official release/converter documentary snapshots; never execute source."""
import datetime,json
from urllib.parse import urlparse
import requests
from .source_metadata import P,read,write,append,sha,verify_history
COMMIT='54030ac4eb40a74978ac1f6ef6e966278b9d3f34'
FILES=['src/ibl_to_nwb/datainterfaces/_session_epochs_interface.py','documentation/conversion/trials_interface.md','documentation/ibl_science/wheel_data.md','src/ibl_to_nwb/utils/electrodes.py','src/ibl_to_nwb/utils/probe_naming.py','src/ibl_to_nwb/fixtures/load_fixtures.py','src/ibl_to_nwb/fixtures/bwm_qc.json']
def plan():
    records=[dict(name='converter_'+f.replace('/','__'),url=f'https://raw.githubusercontent.com/catalystneuro/IBL-to-nwb/{COMMIT}/{f}',role='Static converter/source semantics only; not verified historical writer') for f in FILES]
    records.extend(dict(name='asset_'+r['asset']['asset_id']+'.json',url=f"https://api.dandiarchive.org/api/dandisets/000409/versions/0.260309.1324/assets/{r['asset']['asset_id']}/",role='Fixed release official per-asset metadata') for r in read(P/'SOURCE_AUDIT_ROSTER.json')['records'])
    write(P/'DOCUMENTARY_PLAN.json',dict(records=records,max_requests=24,max_bytes=12000000,redirects=False,neural=False,registered_before_requests=True))
def fetch():
    verify_history();policy=read(P/'DOCUMENTARY_PLAN.json');folder=P/'sources';folder.mkdir(exist_ok=True)
    log=P/'results/DOCUMENTARY_ACCESS.jsonl';previous=[json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []
    used=sum(x.get('bytes',0) for x in previous)
    for item in policy['records']:
        dest=folder/item['name']
        if dest.exists():raise FileExistsError('Preserve previous documentary receipt; no overwrite')
        if len(previous)>=policy['max_requests']:raise RuntimeError('Documentary request bound')
        u=urlparse(item['url']);assert u.scheme=='https' and u.hostname in {'api.dandiarchive.org','raw.githubusercontent.com'}
        row=dict(**item,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bytes=0)
        try:
            with requests.get(item['url'],timeout=(15,40),allow_redirects=False,stream=True) as response:
                row['status']=response.status_code
                chunks=[]
                for chunk in response.iter_content(65536):
                    row['bytes']+=len(chunk)
                    if used+row['bytes']>policy['max_bytes']:raise RuntimeError('Documentary byte bound')
                    chunks.append(chunk)
                data=b''.join(chunks);row['sha256']=sha(data);dest.write_bytes(data)
                if response.status_code!=200:row['available']=False
                else:row['available']=True
            write(folder/(item['name']+'.receipt.json'),row)
        except Exception as exc:row['error_type']=type(exc).__name__;raise
        finally:append(log,row);previous.append(row);used+=row['bytes']
        print(item['name'],row['status'],row['bytes'],flush=True)
if __name__=='__main__':
    import sys
    {'plan':plan,'fetch':fetch}[sys.argv[1]]()
