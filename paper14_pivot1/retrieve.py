"""Bounded official release/source metadata GET only. No DANDI asset download."""
import datetime,hashlib,json
from pathlib import Path
from urllib.parse import urlparse
import requests
P=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(x):return hashlib.sha256(x).hexdigest()
def write(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def validate(url):
    u=urlparse(url)
    if u.scheme!='https' or u.username or u.password:raise PermissionError('Anonymous official HTTPS metadata only')
    if u.hostname=='api.dandiarchive.org' and u.path in {'/api/dandisets/000409/','/api/dandisets/000409/versions/0.260309.1324/','/api/dandisets/000409/versions/0.260309.1324/assets/'}:return
    if u.hostname in {'docs.internationalbrainlab.org','www.internationalbrainlab.com','registry.opendata.aws','creativecommons.org'} and not u.path.endswith(('.nwb','.zip','.npy','.pqt','.parquet')):return
    if u.hostname in {'raw.githubusercontent.com','api.github.com'}:
        parts=u.path.strip('/').split('/');repo='/'.join(parts[1:3] if u.hostname=='api.github.com' else parts[:2])
        if repo.lower() in {'int-brain-lab/ibl-to-nwb','catalystneuro/ibl-to-nwb','int-brain-lab/paper-brain-wide-map'}:
            if u.hostname=='api.github.com' and any(t in u.path for t in ['/commits/','/git/trees/']):return
            if u.hostname=='raw.githubusercontent.com' and u.path.endswith(('.md','.py','.json','.yaml','.toml','.txt')):return
    raise PermissionError('Outside registered source metadata; no content/blob/NWB endpoints')
def get(url,name,params=None):
    validate(url)
    if Path(name).name!=name:raise ValueError('Basename only')
    s=P/'sources';s.mkdir(exist_ok=True);p=s/name
    if p.exists():assert sha(p.read_bytes())==read(s/(name+'.receipt.json'))['sha256'];return p.read_bytes()
    log=s/'access.jsonl';rows=[json.loads(l) for l in log.read_text().splitlines()] if log.exists() else [];lim=read(P/'REGISTRATION.json')['access']
    if len(rows)>=lim['http_attempts'] or sum(r['saved_as']==name for r in rows)>=lim['attempts_per_request']:raise RuntimeError('Registered request budget exhausted')
    row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='GET',url=url,params=params,saved_as=name,bytes=0,purpose='RELEASE_LICENSE_SOURCE_OR_IDENTITY_METADATA_ONLY')
    try:
        with requests.get(url,params=params,stream=True,allow_redirects=False,timeout=(15,45)) as r:
            row.update(status=r.status_code,headers={k:v for k,v in r.headers.items() if k.lower() in {'etag','content-type','content-length','last-modified','location'}})
            if r.is_redirect:raise RuntimeError('Register exact redirect destination; no automatic follow')
            r.raise_for_status();parts=[]
            for chunk in r.iter_content(65536):
                row['bytes']+=len(chunk)
                if row['bytes']>lim['single_response_bytes'] or row['bytes']+sum(v['bytes'] for v in rows)>lim['total_bytes']:raise RuntimeError('Registered byte budget exceeded')
                parts.append(chunk)
            raw=b''.join(parts);row['sha256']=sha(raw);p.write_bytes(raw);write(s/(name+'.receipt.json'),row);return raw
    except Exception as exc:row.update(error_type=type(exc).__name__,error=str(exc));raise
    finally:
        with log.open('a',encoding='utf8') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
def initial():
    urls=[('dandiset.json','https://api.dandiarchive.org/api/dandisets/000409/'),('release.json','https://api.dandiarchive.org/api/dandisets/000409/versions/0.260309.1324/'),('ibl_registry.html','https://registry.opendata.aws/ibl-brain-wide-map/'),('ibl_release_docs.html','https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html'),('ibl_task.html','https://www.internationalbrainlab.com/brainwide-map')]
    for n,u in urls:
        try:get(u,n);print(n,'saved')
        except (requests.RequestException,RuntimeError) as exc:print(n,type(exc).__name__)
    get('https://api.dandiarchive.org/api/dandisets/000409/versions/0.260309.1324/assets/','assets_page1.json',dict(page_size='1000',metadata='false'))
    print('Release and asset identity metadata only saved.')
if __name__=='__main__':initial()
