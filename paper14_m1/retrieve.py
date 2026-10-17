"""Bounded official rights/provenance metadata retrieval; no data-array reader."""
import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

P=Path(__file__).resolve().parent
ROOT=P.parent
DOC_HOSTS={'alleninstitute.org','www.allenneuraldynamics.org','docs.allenneuraldynamics.org','allenneuraldynamics.github.io'}
REPOS={'AllenNeuralDynamics/aind-data-access-api','AllenNeuralDynamics/aind-data-schema','AllenInstitute/npc_sessions','AllenInstitute/npc_lims','AllenNeuralDynamics/dr-datacube','AllenNeuralDynamics/conect-dev-capsule'}
S3='aind-scratch-data.s3.us-west-2.amazonaws.com'


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def digest(raw):return hashlib.sha256(raw).hexdigest()
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')


def validate(url,method,params=None):
    u=urlparse(url)
    if u.scheme!='https' or u.username or u.password:raise PermissionError('HTTPS official metadata only')
    if method not in {'GET','HEAD'}:raise PermissionError('Read-only requests only')
    if u.hostname in DOC_HOSTS:
        if not any(u.path.endswith(s) for s in ['.nwb','.h5','.hdf5','.parquet','.zip','.gz','.bin','.npy','.tif','.mp4']):return
    if u.hostname in {'api.github.com','raw.githubusercontent.com'}:
        parts=u.path.strip('/').split('/')
        repo='/'.join(parts[1:3]) if u.hostname=='api.github.com' else '/'.join(parts[:2])
        if repo not in REPOS:raise PermissionError('Unregistered processing/documentation source')
        if u.hostname=='api.github.com' and ('git/trees' in u.path or '/commits/' in u.path or u.path.endswith(repo) or u.path.endswith('/license')):return
        if u.hostname=='raw.githubusercontent.com' and (u.path.endswith(('.py','.md','.json','.toml','.yaml','.yml','.txt')) or u.path.endswith('/LICENSE')):return
    if u.hostname=='api.allenneuraldynamics.org':
        if u.path in {'/openapi.json','/docs'} or u.path.startswith('/v2/metadata_index/data_assets'):return
    if u.hostname==S3:
        q=params or parse_qs(u.query)
        if u.path=='/' and str(q.get('list-type'))=='2' and str(q.get('prefix','')).startswith('dynamic-routing/cache/') and int(q.get('max-keys',0))<=1000:return
        # Only explicit sidecar descriptors/rights text, never NWB or data chunks.
        if u.path.startswith('/dynamic-routing/cache/') and u.path.rsplit('/',1)[-1] in {'LICENSE','LICENSE.txt','README.md','data_description.json','processing.json','nwb_contents.json'}:return
    if u.hostname=='aind-open-data.s3.us-west-2.amazonaws.com':
        prefixes=read(P/'CANONICAL_MAPPING_ACCESS.json')['canonical_prefixes']
        q=params or {}
        if u.path=='/' and q.get('list-type')=='2' and q.get('prefix') in prefixes and int(q.get('max-keys',0))<=1000:return
        if any(u.path.lstrip('/').startswith(prefix) for prefix in prefixes):
            if method=='HEAD' or u.path.rsplit('/',1)[-1] in {'data_description.json','processing.json','nwb_contents.json'}:return
            if u.path.endswith('.nwb.zarr/.zmetadata') and (P/'CANONICAL_DESCRIPTOR_ADDENDUM.json').exists():return
    raise PermissionError('Not a registered rights/source metadata URL')


def get(url,name,*,method='GET',params=None):
    validate(url,method,params)
    directory=P/'sources';directory.mkdir(exist_ok=True)
    target=directory/name
    if target.exists():
        receipt=read(target.with_suffix(target.suffix+'.receipt.json'))
        if digest(target.read_bytes())!=receipt['sha256']:raise ValueError('Saved source changed')
        return target.read_bytes()
    log=directory/'access.jsonl';limits=read(P/'REGISTRATION.json')['new_http_limits']
    rows=[json.loads(x) for x in log.read_text(encoding='utf8').splitlines()] if log.exists() else []
    if len(rows)>=limits['attempts']:raise RuntimeError('Request budget exhausted')
    used=sum(x['bytes'] for x in rows);r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'method':method,'params':params,'purpose':'RIGHTS_PROVENANCE_OR_DESCRIPTOR_METADATA_ONLY'};n=0
    try:
        with requests.request(method,url,params=params,timeout=(15,35),stream=True,allow_redirects=False) as response:
            r.update(status=response.status_code,headers={k:v for k,v in response.headers.items() if k.lower() in {'etag','content-length','content-type','location','last-modified','x-amz-version-id'}})
            # Do not follow a new target or download an error/redirect payload as evidence of content.
            if response.is_redirect:raise RuntimeError('Redirect recorded; register exact destination explicitly')
            response.raise_for_status();parts=[]
            if method=='GET':
                for chunk in response.iter_content(65536):
                    n+=len(chunk)
                    if n>limits['single_response_bytes'] or used+n>limits['total_bytes']:raise RuntimeError('Source metadata byte budget exceeded')
                    parts.append(chunk)
            raw=b''.join(parts);r['sha256']=digest(raw);r['saved_as']=str(target.relative_to(P));target.write_bytes(raw);write(target.with_suffix(target.suffix+'.receipt.json'),r);return raw
    except Exception as exc:
        r['error_type']=type(exc).__name__;r['error']=str(exc);raise
    finally:
        r['bytes']=n
        with log.open('a',encoding='utf8') as f:f.write(json.dumps(r,sort_keys=True)+'\n')


def attempt(url,name,**kw):
    try:return get(url,name,**kw)
    except (requests.RequestException,RuntimeError) as exc:
        print(name,type(exc).__name__);return None


def initial():
    for url,name in [
        ('https://alleninstitute.org/legal/terms-of-use','institute_terms.html'),
        ('https://alleninstitute.org/legal/citation-policy','institute_citation.html'),
        ('https://docs.allenneuraldynamics.org/en/latest/policies_practices/publication_standards.html','publication_standards.html'),
        ('https://docs.allenneuraldynamics.org/en/latest/explore_analyze/outreach.html','outreach.html'),
        ('https://api.allenneuraldynamics.org/openapi.json','api_openapi.json'),
        ('https://api.github.com/repos/AllenNeuralDynamics/aind-data-access-api/commits/main','access_api_commit.json'),
        ('https://api.github.com/repos/AllenInstitute/npc_lims/commits/main','npc_lims_commit.json'),
        ('https://api.github.com/repos/AllenInstitute/npc_sessions/commits/main','npc_sessions_commit.json')]:attempt(url,name)


if __name__=='__main__':initial()
