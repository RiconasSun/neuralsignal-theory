"""Bounded public source/metadata documents, never NWB or neural arrays."""
import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import requests
from .audit import P,read,write

META=P/'metadata'
REPOS={'allenneuraldynamics/dr-datacube','allenneuraldynamics/conect-dev-capsule','nsteinme/steinmetz-et-al-2019'}


def allowed(url):
    u=urlparse(url);path=u.path.lower()
    if u.scheme!='https':return False
    if u.netloc=='api.figshare.com':return path=='/v2/articles/9598406' or path.startswith('/v2/articles/9598406/versions')
    if u.netloc=='api.github.com':return any(path.startswith('/repos/'+r+'/') for r in REPOS)
    if u.netloc=='raw.githubusercontent.com':return any(path.startswith('/'+r+'/') for r in REPOS) and path.endswith(('.md','.py','.json','.csv','.toml','.txt','/license'))
    return False


def get(name,url):
    if not allowed(url) or Path(name).name!=name:raise PermissionError('Outside metadata-only source whitelist')
    META.mkdir(exist_ok=True);path=META/name;receipt=META/(name+'.receipt.json')
    if path.exists():
        if read(receipt)['sha256']!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError('Saved source hash changed')
        return path.read_bytes()
    log=META/'access.jsonl';prior=[json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []
    limits=read(P/'REGISTRATION.json')['retrieval_bounds']
    used=sum(x.get('bytes',0) for x in prior)
    for attempt in range(2):
        if len(prior)>=limits['new_http_attempts']:raise RuntimeError('Source request budget exhausted')
        record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'kind':'SOURCE_OR_METADATA_ONLY','attempt':attempt+1};payload=b''
        try:
            with requests.get(url,timeout=(15,40),stream=True) as response:
                record.update(status=response.status_code,ETag=response.headers.get('ETag'),declared_length=response.headers.get('Content-Length'))
                response.raise_for_status();parts=[]
                for block in response.iter_content(65536):
                    used+=len(block);record['bytes']=record.get('bytes',0)+len(block)
                    if record['bytes']>limits['single_response_bytes'] or used>limits['total_bytes']:raise RuntimeError('Metadata byte budget exhausted')
                    parts.append(block)
                payload=b''.join(parts)
            record['sha256']=hashlib.sha256(payload).hexdigest()
            path.write_bytes(payload);write(receipt,record)
            return payload
        except Exception as exc:
            record['error_type']=type(exc).__name__;record['error']=str(exc)
            if attempt==1:raise
        finally:
            prior.append(record)
            with log.open('a',encoding='utf8') as f:f.write(json.dumps(record)+'\n')


def initial():
    pins={}
    for alias,repo in [('dr','AllenNeuralDynamics/dr-datacube'),('capsule','AllenNeuralDynamics/conect-dev-capsule'),('steinmetz','nsteinme/steinmetz-et-al-2019')]:
        commit=json.loads(get(alias+'_commit.json','https://api.github.com/repos/'+repo+'/commits/HEAD'))['sha'];pins[alias]=commit
        get(alias+'_README.md','https://raw.githubusercontent.com/'+repo+'/'+commit+'/README.md')
        get(alias+'_tree.json','https://api.github.com/repos/'+repo+'/git/trees/'+commit+'?recursive=1')
        if alias=='dr':get('dr_pyproject.toml','https://raw.githubusercontent.com/'+repo+'/'+commit+'/pyproject.toml')
    get('steinmetz_figshare.json','https://api.figshare.com/v2/articles/9598406')
    write(P/'metadata/SOURCE_PINS.json',pins)
    print(json.dumps(pins))


if __name__=='__main__':initial()
