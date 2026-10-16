"""Explicit bounded metadata-only Parquet range reader; no SDK fallbacks."""
import datetime
import hashlib
import io
import json
import re
from urllib.parse import urlparse
import requests
from .audit import P,read,write

PREFIX=read(P/'DR_SOURCE_REGISTRATION.json')['exact_prefix']
IBL='https://ibl-brain-wide-map-public.s3.amazonaws.com/aggregates/2024_Q2_IBL_et_al_BWM/trials.pqt'
URLS={PREFIX+n+'.parquet' for n in ['session','trials','units']}|{IBL}


def request(url,*,method='GET',headers=None,maximum=65536):
    if url not in URLS:raise PermissionError('Not an exact registered metadata object')
    if method not in ['GET','HEAD'] or method=='GET' and (not headers or not re.fullmatch(r'bytes=\d+-\d+',headers.get('Range',''))):
        raise PermissionError('Only bounded metadata ranges or HEAD allowed')
    root=P/'metadata';root.mkdir(exist_ok=True);log=root/'access.jsonl'
    prior=[json.loads(s) for s in log.read_text().splitlines()] if log.exists() else []
    limits=read(P/'REGISTRATION.json')['retrieval_bounds'];record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'method':method,'headers':headers,'kind':'METADATA_RANGE'}
    if len(prior)>=limits['new_http_attempts']:raise RuntimeError('Metadata request budget exhausted')
    used=sum(r.get('bytes',0) for r in prior);parts=[];n=0
    try:
        with requests.request(method,url,headers=headers,timeout=(15,40),stream=True) as response:
            record.update(status=response.status_code,ETag=response.headers.get('ETag'),content_range=response.headers.get('Content-Range'),length=response.headers.get('Content-Length'))
            response.raise_for_status()
            if method=='GET' and response.status_code!=206:raise RuntimeError('Range not honored; no bulk fallback')
            if method=='GET':
                for chunk in response.iter_content(65536):
                    n+=len(chunk)
                    if n>min(maximum,limits['single_response_bytes']) or used+n>limits['total_bytes']:raise RuntimeError('Metadata byte budget exceeded')
                    parts.append(chunk)
            data=b''.join(parts);record['sha256']=hashlib.sha256(data).hexdigest()
            return data,dict(response.headers)
    except Exception as exc:
        record['error_type']=type(exc).__name__;record['error']=str(exc);raise
    finally:
        record['bytes']=n
        with log.open('a',encoding='utf8') as f:f.write(json.dumps(record)+'\n')


class MetadataRanges(io.RawIOBase):
    def __init__(self,url):
        self.url=url;_,h=request(url,method='HEAD');self.size=int(h['Content-Length']);self.etag=h['ETag'];self.pos=0;self.cache={}
        self.root=P/'work/ranges'/hashlib.sha256((url+self.etag).encode()).hexdigest();self.root.mkdir(parents=True,exist_ok=True)
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        p=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        if p<0 or p>self.size:raise ValueError('Invalid metadata seek')
        self.pos=p;return p
    def read(self,n=-1):
        if n<0 or n>4000000:raise PermissionError('Unbounded/oversized range forbidden')
        n=min(n,self.size-self.pos)
        if n==0:return b''
        a=self.pos;b=a+n-1;key=(a,n);path=self.root/(str(a)+'_'+str(n)+'.bin')
        if key not in self.cache:
            if path.exists():
                raw=path.read_bytes();receipt=read(path.with_suffix('.json'))
                if len(raw)!=n or hashlib.sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('Saved metadata range changed')
            else:
                raw,h=request(self.url,headers={'Range':f'bytes={a}-{b}','If-Match':self.etag},maximum=n)
                if h.get('Content-Range')!=f'bytes {a}-{b}/{self.size}' or h.get('ETag')!=self.etag or len(raw)!=n:raise ValueError('Metadata object identity/range mismatch')
                path.write_bytes(raw);write(path.with_suffix('.json'),{'sha256':hashlib.sha256(raw).hexdigest()})
            self.cache[key]=raw
        self.pos+=n;return self.cache[key]
    def readinto(self,buf):
        data=self.read(len(buf));buf[:len(data)]=data;return len(data)


def schemas():
    import pyarrow.parquet as pq
    for name in ['session','trials','units']:
        path=P/'metadata'/('DR_'+name+'_schema.json')
        if path.exists():continue
        try:
            f=MetadataRanges(PREFIX+name+'.parquet');pf=pq.ParquetFile(f)
            write(path,{'source_url':f.url,'ETag':f.etag,'object_size':f.size,'columns':pf.schema_arrow.names,'schema':str(pf.schema_arrow),
                'rows':pf.metadata.num_rows,'row_groups':pf.metadata.num_row_groups,'stage':'FOOTER_ONLY_NO_COLUMN_VALUES'})
        except Exception as exc:
            write(path,{'source_url':PREFIX+name+'.parquet','status':'UNAVAILABLE_METADATA','error_type':type(exc).__name__,'error':str(exc)})
    print('Registered metadata footer attempts complete; no NWB or neural column values.')


if __name__=='__main__':schemas()
