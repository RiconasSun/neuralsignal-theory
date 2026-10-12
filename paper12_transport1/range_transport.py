"""Bounded retries and atomically committed private opaque byte checkpoints."""
import hashlib
import io
import json
import os
from pathlib import Path
import time
import uuid
import requests
from urllib3.exceptions import ReadTimeoutError, ProtocolError
from bounded_core import byte_range, validate, validate_headers
import common as r
import custodian as old_custodian

TRANSIENT = (requests.Timeout, requests.ConnectionError, requests.exceptions.ChunkedEncodingError, ReadTimeoutError, ProtocolError)
STATUSES = {408,429,500,502,503,504}


class CachedResponse:
    def __init__(self, body, headers):
        self.status_code=206;self.headers=headers;self.raw=io.BytesIO(body)
    def __enter__(self):return self
    def __exit__(self,*args):self.raw.close()


class RetryHTTP:
    def __init__(self, owner, root, protect, session=None, sleep=time.sleep):
        self.owner=owner;self.root=Path(root);self.protect=protect;self.sleep=sleep
        self.root.mkdir(parents=True,exist_ok=True);protect(self.root)
        self.session=session or requests.Session();self.session.headers['Accept-Encoding']='identity'
        self.stats=dict(requests=0,cache_hits=0,transient_failures=0,accepted_network_bytes=0)
    def get(self,url,**kwargs):
        stop=self.root/'STOP.json'
        if stop.exists():raise RuntimeError(r.load(stop)['error_code'])
        try:return self._get(url,**kwargs)
        except Exception as exc:
            code=str(exc) if isinstance(exc,RuntimeError) else 'TRANSPORT_STATE_INVALID'
            r.save(stop,dict(error_code=code,error_type=type(exc).__name__),True);self.protect(stop)
            raise
    def _get(self,url,**kwargs):
        start,end=byte_range(kwargs['headers']['Range'],self.owner.size)
        identity=dict(file_id=self.owner.file_id,etag=self.owner.etag,size=self.owner.size,start=start,end=end)
        chunk=self.root/('chunk_%016x'%start)
        if chunk.exists():
            marker=r.load(chunk/'marker.json');body=(chunk/'body.blob').read_bytes()
            if marker.get('source')!=identity or marker.get('sha256')!=hashlib.sha256(body).hexdigest() or len(body)!=end-start+1:
                raise RuntimeError('CACHE_INTEGRITY_FAILED')
            self.stats['cache_hits']+=1
        else:
            ledger=self.root/('attempts_%016x'%start);ledger.mkdir(exist_ok=True);self.protect(ledger)
            used=[]
            for number in range(1,4):
                intent=ledger/(str(number)+'.intent.json')
                if intent.exists():
                    if r.load(intent)['source']!=identity:raise RuntimeError('ATTEMPT_SOURCE_IDENTITY_CHANGED')
                    result_path=ledger/(str(number)+'.result.json')
                    if result_path.exists():
                        previous=r.load(result_path)
                        if previous.get('attempt')!=number or previous.get('status') not in ('FATAL','TRANSIENT_FAILURE','VERIFIED_COMPLETE_BLOCK'):
                            raise RuntimeError('ATTEMPT_JOURNAL_INVALID')
                        if previous['status']=='FATAL':raise RuntimeError('PRESERVED_FATAL_TRANSPORT_FAILURE')
                    used.append(number)
            if used!=list(range(1,len(used)+1)):raise RuntimeError('ATTEMPT_JOURNAL_INVALID')
            body=None
            for number in range(len(used)+1,4):
                intent=ledger/(str(number)+'.intent.json')
                with intent.open('x',encoding='utf-8',newline='\n') as f:
                    json.dump(dict(source=identity,attempt=number),f,sort_keys=True)
                    f.flush();os.fsync(f.fileno())
                self.protect(intent);self.stats['requests']+=1
                try:
                    headers=dict(kwargs['headers']);headers['Accept-Encoding']='identity'
                    with self.session.get(url,params=kwargs.get('params'),headers=headers,stream=True,timeout=(20,120),allow_redirects=False) as response:
                        if response.status_code in STATUSES:
                            raise requests.ConnectionError('RETRYABLE_HTTP_STATUS')
                        validate_headers(response.status_code,response.headers,start,end,self.owner.size,self.owner.etag)
                        body=response.raw.read(end-start+2)
                        validate(response.status_code,response.headers,body,start,end,self.owner.size,self.owner.etag)
                    self.stats['accepted_network_bytes']+=len(body)
                    result=dict(attempt=number,status='VERIFIED_COMPLETE_BLOCK')
                except TRANSIENT as exc:
                    body=None;self.stats['transient_failures']+=1
                    result=dict(attempt=number,status='TRANSIENT_FAILURE',error_type=type(exc).__name__)
                except Exception as exc:
                    r.save(ledger/(str(number)+'.result.json'),dict(attempt=number,status='FATAL',error_type=type(exc).__name__),True)
                    self.protect(ledger/(str(number)+'.result.json'));raise
                r.save(ledger/(str(number)+'.result.json'),result,True);self.protect(ledger/(str(number)+'.result.json'))
                if body is not None:break
                if number<3:self.sleep(2**number)
            if body is None:raise RuntimeError('TRANSPORT_UNRECOVERABLE')
            pending=self.root/('pending_'+uuid.uuid4().hex);pending.mkdir();self.protect(pending)
            target=pending/'body.blob'
            with target.open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
            self.protect(target)
            marker=pending/'marker.json'
            with marker.open('x',encoding='utf-8',newline='\n') as f:
                json.dump(dict(source=identity,sha256=hashlib.sha256(body).hexdigest()),f,sort_keys=True)
                f.flush();os.fsync(f.fileno())
            self.protect(marker);pending.rename(chunk)
        return CachedResponse(body,{'ETag':self.owner.etag,'Content-Range':f'bytes {start}-{end}/{self.owner.size}'})
    def close(self):self.session.close()


class Source(old_custodian.Source):
    def __init__(self,item):
        old_custodian.require_custodian();super().__init__(item);self.http.close()
        self.file_id=item['file_id'];self.session_id=item['session_id']
        self.http=RetryHTTP(self,r.OLD/'.private/transport_recovery1/cache'/self.session_id,old_custodian.protect)
        self.closed_audit=False
    @property
    def bytes(self):
        return self.http.stats['accepted_network_bytes'] if hasattr(getattr(self,'http',None),'stats') else 0
    @bytes.setter
    def bytes(self,value):pass
    def close(self):
        if not getattr(self,'closed_audit',True):
            r.save(r.HERE/'results/transport'/(self.session_id+'.json'),dict(
                session_id=self.session_id,**self.http.stats,
                byte_count_scope='Fully accepted HTTPbytes only;not partial/wire traffic;cache hits separate',
                checkpoint_verification_policy='Every reused completed block source/hash/length checked;fatal failures persist',raw_ranges_or_hashes_published=False))
            self.closed_audit=True
        super().close()
