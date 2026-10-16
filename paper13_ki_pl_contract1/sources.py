"""Bounded public source acquisition. No NWB/neural download capability."""
import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import requests

P=Path(__file__).resolve().parent
M=P/'metadata'
POLICY=json.loads((P/'REGISTRATION.json').read_text())

def sha(b): return hashlib.sha256(b).hexdigest()

class Transport:
    def __init__(self):
        M.mkdir(exist_ok=True)
        self.journal=M/'access.jsonl'
        self.prior=[json.loads(x) for x in self.journal.read_text().splitlines()] if self.journal.exists() else []
        self.calls=len(self.prior);self.used=sum(x.get('bytes',0) for x in self.prior)
        self.session=requests.Session()
    def request(self,url,*,headers=None,maximum=12582912):
        if urlparse(url).hostname not in {'api.github.com','raw.githubusercontent.com','www.nature.com','zenodo.org'}:
            raise ValueError('Source provider denied')
        if urlparse(url).hostname=='zenodo.org' and url!='https://zenodo.org/api/records/14205018/files/preprocessing.zip/content':
            raise ValueError('Unregistered archive denied')
        if urlparse(url).hostname=='zenodo.org' and not (headers and headers.get('Range')):
            raise ValueError('Archive requires bounded range')
        for attempt in range(2):
            self.calls+=1
            if self.calls>POLICY['bounds']['new_http_requests']: raise RuntimeError('Request budget')
            rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'request_headers':headers,'attempt':attempt+1};count=0
            try:
                with self.session.get(url,headers=headers,stream=True,timeout=(20,45)) as r:
                    rec.update(status=r.status_code,response_headers={k:v for k,v in r.headers.items() if k.lower() not in {'set-cookie','authorization'}})
                    if headers and headers.get('Range') and r.status_code!=206: raise ValueError('Range refused; body unread')
                    r.raise_for_status();parts=[]
                    for b in r.iter_content(65536):
                        count+=len(b);self.used+=len(b)
                        if count>maximum or self.used>POLICY['bounds']['new_transport_bytes']: raise ValueError('Transport byte budget')
                        parts.append(b)
                    data=b''.join(parts);rec.update(bytes=count,sha256=sha(data))
                    return data,requests.structures.CaseInsensitiveDict(r.headers),rec
            except Exception as exc: rec['error']=repr(exc);last=exc
            finally:
                rec.setdefault('bytes',count)
                with self.journal.open('a',encoding='utf8',newline='\n') as f:f.write(json.dumps(rec)+'\n')
        raise RuntimeError('Public source request failed') from last
    def save(self,name,url):
        path=M/name
        if path.exists(): return path.read_bytes()
        data,_,rec=self.request(url)
        with path.open('xb') as f:f.write(data)
        path.with_name(path.name+'.receipt.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
        return data

def discover():
    t=Transport()
    repo='PierreLeMerre/Esr1_NPX_code'
    commit=json.loads(t.save('Esr1_commit.json',f'https://api.github.com/repos/{repo}/commits/HEAD'))['sha']
    tree=json.loads(t.save('Esr1_tree.json',f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
    print('PIN',commit)
    for x in tree['tree']:
        if x['type']=='blob': print(x['path'],x.get('size'))

if __name__=='__main__': discover()
