"""Journaled anonymous official metadata retrieval. Never load NWB or signal arrays."""
import datetime
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse
import requests

P=Path(__file__).resolve().parent
S=P/'sources'
REPOS={'awslabs/open-data-registry','AllenInstitute/npc_sessions','AllenInstitute/npc_lims','AllenNeuralDynamics/aind-data-access-api','AllenNeuralDynamics/aind-data-schema'}

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')

def validate(url,params=None):
    u=urlparse(url)
    if u.scheme!='https' or u.username or u.password:raise PermissionError('Official anonymous HTTPS only')
    if u.hostname in {'registry.opendata.aws','creativecommons.org','allenneuraldynamics.github.io','docs.allenneuraldynamics.org','www.internationalbrainlab.com','docs.internationalbrainlab.org'}:
        if not re.search(r'\.(nwb|h5|bin|npy|parquet|mp4|zip)$',u.path):return
    if u.hostname=='api.allenneuraldynamics.org' and u.path=='/v2/metadata_index/data_assets':return
    if u.hostname in {'api.github.com','raw.githubusercontent.com'}:
        parts=u.path.strip('/').split('/');repo='/'.join(parts[1:3] if u.hostname=='api.github.com' else parts[:2])
        if repo in REPOS:
            if u.hostname=='api.github.com' and any(x in u.path for x in ['/commits/','/git/trees/']):return
            if u.hostname=='raw.githubusercontent.com' and (u.path.endswith(('.md','.py','.json','.yaml','.yml','.toml','.txt')) or u.path.endswith('/LICENSE')):return
    if u.hostname=='aind-open-data.s3.us-west-2.amazonaws.com':
        q=params or {}
        registered=read(P/'CANONICAL_ACCESS.json')['prefixes'] if (P/'CANONICAL_ACCESS.json').exists() else []
        if (P/'SORTED_METADATA_ACCESS.json').exists():registered+=read(P/'SORTED_METADATA_ACCESS.json')['prefixes']
        if u.path=='/' and q.get('list-type')=='2' and q.get('prefix','').rstrip('/') in registered and int(q.get('max-keys',0))<=1000:return
        path=u.path.lstrip('/')
        if any(path.startswith(prefix+'/') for prefix in registered):
            if path.rsplit('/',1)[-1] in {'data_description.json','processing.json','acquisition.json','session.json','quality_control.json','subject.json','.zmetadata','.zattrs','.zgroup'}:return
            allow=read(P/'COLUMN_ACCESS.json')['exact_keys'] if (P/'COLUMN_ACCESS.json').exists() else []
            if path in allow:return
    raise PermissionError('Not a registered metadata-only URL')

def get(url,name,params=None):
    validate(url,params)
    if Path(name).name!=name:raise ValueError('Basename only')
    S.mkdir(exist_ok=True);p=S/name;receipt=S/(name+'.receipt.json')
    if p.exists():
        assert sha(p.read_bytes())==read(receipt)['sha256'];return p.read_bytes()
    log=S/'access.jsonl';rows=[json.loads(t) for t in log.read_text().splitlines()] if log.exists() else []
    limits=read(P/'REGISTRATION.json')['budget'];used=sum(x['bytes'] for x in rows)
    if len(rows)>=limits['attempts']:raise RuntimeError('Registered HTTP attempt budget exhausted')
    if sum(x.get('saved_as')==name for x in rows)>=limits['attempts_per_request']:raise RuntimeError('Registered per-request budget exhausted')
    row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),url=url,params=params,method='GET',saved_as=name,bytes=0,purpose='LICENSE_SOURCE_OR_REGISTERED_METADATA_ONLY')
    try:
        with requests.get(url,params=params,stream=True,timeout=(15,45),allow_redirects=False) as r:
            row['status']=r.status_code;row['headers']={k:v for k,v in r.headers.items() if k.lower() in {'etag','content-length','content-type','last-modified','location','x-amz-version-id'}}
            if r.is_redirect:raise RuntimeError('Redirect destination requires registration')
            r.raise_for_status();parts=[]
            for chunk in r.iter_content(65536):
                row['bytes']+=len(chunk)
                if row['bytes']>limits['single_response_bytes'] or used+row['bytes']>limits['total_bytes']:raise RuntimeError('Registered byte limit exceeded')
                parts.append(chunk)
            raw=b''.join(parts);row['sha256']=sha(raw);p.write_bytes(raw);write(receipt,row);return raw
    except Exception as exc:
        row.update(error_type=type(exc).__name__,error=str(exc));raise
    finally:
        with log.open('a',encoding='utf8') as f:f.write(json.dumps(row,sort_keys=True)+'\n')

def initial():
    urls=[('registry.html','https://registry.opendata.aws/allen-nd-open-data/'),
          ('aind_data_documentation.html','https://allenneuraldynamics.github.io/data.html'),
          ('cc_by_4_legalcode.html','https://creativecommons.org/licenses/by/4.0/legalcode.en'),
          ('registry_commit.json','https://api.github.com/repos/awslabs/open-data-registry/commits/main')]
    for name,url in urls:
        try:get(url,name)
        except (requests.RequestException,RuntimeError) as exc:print(name,type(exc).__name__)
    query={'data_description.project_name':'Dynamic Routing','name':{'$regex':'_nwb_'}}
    projection={'_id':1,'name':1,'location':1,'data_description':1,'processing.data_processes.process_type':1,'processing.data_processes.code':1}
    get('https://api.allenneuraldynamics.org/v2/metadata_index/data_assets','dynamic_routing_nwb_catalog.json',dict(filter=json.dumps(query),projection=json.dumps(projection),limit='500'))
    print('Official release documentation and canonical NWB metadata catalog saved; eligibility not calculated.')

if __name__=='__main__':initial()
