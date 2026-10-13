"""Frozen same-source transport; opaque old blocks verified without neural decoding."""
import hashlib
import io
import os
from pathlib import Path
import sys
import time
import requests
from urllib3.exceptions import ReadTimeoutError, ProtocolError
import study as r
import verified_atomic as a
sys.path.append(str(r.ROOT / 'paper12_transport1'))
from bounded_core import byte_range, validate, validate_headers
from custodian import Source as OriginalSource

TRANSIENT = (requests.Timeout, requests.ConnectionError, requests.exceptions.ChunkedEncodingError,
             ReadTimeoutError, ProtocolError)
STATUSES = {408,429,500,502,503,504}


class Response:
    def __init__(self, body, headers):
        self.status_code=206; self.headers=headers; self.raw=io.BytesIO(body)
    def __enter__(self): return self
    def __exit__(self,*args): self.raw.close()


def prior_budget(old, identity):
    start = identity['start']
    ledger = old / ('attempts_%016x' % start)
    used = []
    for number in range(1,4):
        intent = ledger / (str(number)+'.intent.json')
        result = ledger / (str(number)+'.result.json')
        if intent.exists():
            if r.load(intent) != dict(source=identity,attempt=number):
                raise RuntimeError('OLD_ATTEMPT_SOURCE_CHANGED')
            if result.exists():
                value = r.load(result)
                if value.get('attempt') != number or value.get('status') not in ('TRANSIENT_FAILURE','VERIFIED_COMPLETE_BLOCK'):
                    raise RuntimeError('OLD_TERMINAL_TRANSPORT_FAILURE')
            used.append(number)
        elif result.exists():
            raise RuntimeError('OLD_RESULT_WITHOUT_INTENT')
    if used != list(range(1,len(used)+1)):
        raise RuntimeError('OLD_NONSEQUENTIAL_BUDGET')
    return len(used)


def prior_block(old, identity):
    expected = old / ('chunk_%016x' % identity['start'])
    candidates = [expected] if expected.exists() else []
    for pending in sorted(old.glob('pending_*')):
        marker = pending / 'marker.json'
        if marker.exists() and r.load(marker).get('source') == identity:
            candidates.append(pending)
    if len(candidates)>1:
        raise RuntimeError('OLD_DUPLICATE_BLOCK_CONFLICT')
    if not candidates:
        used=prior_budget(old,identity)
        for number in range(1,used+1):
            result=old/('attempts_%016x'%identity['start'])/(str(number)+'.result.json')
            if result.exists() and r.load(result).get('status')=='VERIFIED_COMPLETE_BLOCK':
                raise RuntimeError('OLD_VERIFIED_BLOCK_ARTIFACT_MISSING')
        return None
    path = candidates[0]; marker = r.load(path/'marker.json')
    length = identity['end']-identity['start']+1
    if marker.get('source') != identity or (path/'body.blob').stat().st_size != length:
        raise RuntimeError('OLD_BLOCK_IDENTITY_OR_LENGTH_FAILED')
    body = (path/'body.blob').read_bytes()
    if marker.get('sha256') != hashlib.sha256(body).hexdigest():
        raise RuntimeError('OLD_BLOCK_HASH_FAILED')
    number = prior_budget(old, identity)
    if not number or r.load(old/('attempts_%016x'%identity['start'])/(str(number)+'.result.json')).get('status')!='VERIFIED_COMPLETE_BLOCK':
        raise RuntimeError('OLD_BLOCK_RESPONSE_NOT_VERIFIED')
    return body, number, path.name.startswith('pending_')


class HTTP:
    def __init__(self, owner, root=None, old=None, session=None, sleep=time.sleep):
        self.owner=owner
        self.root=a.prepare(root or r.HERE/'.private/cache'/owner.session_id)
        self.old=Path(old) if old else r.OLD/'.private/transport_recovery1/cache'/owner.session_id
        self.session=session or requests.Session()
        self.session.headers['Accept-Encoding']='identity'
        self.sleep=sleep
        self.stats=dict(requests=0,cache_hits=0,old_verified_blocks=0,old_pending_recovered=0,
                        transient_failures=0,accepted_network_bytes=0)

    def get(self,url,**kwargs):
        if (self.root/'STOP.json').exists():
            raise RuntimeError('PRESERVED_NEW_TRANSPORT_STOP')
        try:
            return self._get(url,**kwargs)
        except Exception as exc:
            code = str(exc) if isinstance(exc,RuntimeError) else 'TRANSPORT_OR_CHECKPOINT_ABORT'
            a.durable_record(self.root/'STOP.json',dict(error_code=code,error_type=type(exc).__name__,
                winerror=getattr(exc,'winerror',None),events=getattr(exc,'events',[])))
            raise

    def _get(self,url,**kwargs):
        start,end=byte_range(kwargs['headers']['Range'],self.owner.size)
        identity=dict(file_id=self.owner.file_id,etag=self.owner.etag,size=self.owner.size,start=start,end=end)
        name='b_%016x'%start
        target=self.root/(name+'.checkpoint')
        descriptor=self.root/(name+'.json')
        if target.exists():
            if not descriptor.exists(): raise RuntimeError('CHECKPOINT_WITHOUT_RECEIPT')
            saved=r.load(descriptor)
            if saved['source']!=identity or saved['artifact_sha256']!=r.sha(target):
                raise RuntimeError('CHECKPOINT_DESCRIPTOR_CHANGED')
            body=a.read(target,identity,saved['body_sha256'])
            self.stats['cache_hits']+=1
        else:
            ledger=a.prepare(self.root/(name+'_http'))
            origin=ledger/'origin.json'
            if origin.exists():
                value=r.load(origin)
                if value['source']!=identity or value['used']!=prior_budget(self.old,identity):
                    raise RuntimeError('CARRIED_BUDGET_CHANGED')
                carried=value['used']
            else:
                carried=prior_budget(self.old,identity)
                a.durable_record(origin,dict(source=identity,used=carried))
            saved=prior_block(self.old,identity)
            if saved:
                body,consumed,pending=saved
                if consumed!=carried:raise RuntimeError('OLD_BUDGET_BLOCK_MISMATCH')
                self.stats['old_verified_blocks']+=1
                self.stats['old_pending_recovered']+=int(pending)
            else:
                used=[]
                for number in range(carried+1,4):
                    intent=ledger/(str(number)+'.intent.json')
                    result=ledger/(str(number)+'.result.json')
                    if intent.exists():
                        if r.load(intent)!=dict(source=identity,attempt=number):raise RuntimeError('HTTP_INTENT_CHANGED')
                        if result.exists() and r.load(result).get('status')!='TRANSIENT_FAILURE':
                            raise RuntimeError('PRESERVED_HTTP_TERMINAL_RESULT')
                        used.append(number)
                    elif result.exists():raise RuntimeError('HTTP_RESULT_WITHOUT_INTENT')
                if used!=list(range(carried+1,carried+len(used)+1)):raise RuntimeError('HTTP_BUDGET_NONSEQUENTIAL')
                body=None
                for number in range(carried+len(used)+1,4):
                    a.durable_record(ledger/(str(number)+'.intent.json'),dict(source=identity,attempt=number))
                    self.stats['requests']+=1
                    try:
                        headers=dict(kwargs['headers']);headers['Accept-Encoding']='identity'
                        with self.session.get(url,params=kwargs.get('params'),headers=headers,stream=True,
                                              timeout=(20,120),allow_redirects=False) as res:
                            if res.status_code in STATUSES:raise requests.ConnectionError('RETRYABLE_STATUS')
                            validate_headers(res.status_code,res.headers,start,end,self.owner.size,self.owner.etag)
                            body=res.raw.read(end-start+2)
                            validate(res.status_code,res.headers,body,start,end,self.owner.size,self.owner.etag)
                        result=dict(attempt=number,status='VERIFIED_COMPLETE_BLOCK')
                        self.stats['accepted_network_bytes']+=len(body)
                    except TRANSIENT as exc:
                        body=None; self.stats['transient_failures']+=1
                        result=dict(attempt=number,status='TRANSIENT_FAILURE',error_type=type(exc).__name__)
                    except Exception as exc:
                        a.durable_record(ledger/(str(number)+'.result.json'),dict(attempt=number,status='FATAL',error_type=type(exc).__name__))
                        raise
                    a.durable_record(ledger/(str(number)+'.result.json'),result)
                    if body is not None:break
                    if number<3:self.sleep(2**number)
                if body is None:raise RuntimeError('TRANSPORT_UNRECOVERABLE')
            receipt=a.commit(self.root,name,body,identity)
            a.durable_record(descriptor,dict(source=identity,body_sha256=hashlib.sha256(body).hexdigest(),
                artifact_sha256=r.sha(target),publication=receipt))
        validate(206,{'Content-Range':f'bytes {start}-{end}/{self.owner.size}','ETag':self.owner.etag},
                 body,start,end,self.owner.size,self.owner.etag)
        return Response(body,{'Content-Range':f'bytes {start}-{end}/{self.owner.size}','ETag':self.owner.etag})

    def close(self):self.session.close()


class Source(OriginalSource):
    def __init__(self,item):
        a.require_custodian();super().__init__(item);self.http.close()
        self.file_id=item['file_id'];self.session_id=item['session_id']
        self.http=HTTP(self);self.audit_closed=False
    @property
    def bytes(self):return self.http.stats['accepted_network_bytes'] if hasattr(getattr(self,'http',None),'stats') else 0
    @bytes.setter
    def bytes(self,value):pass
    def close(self):
        if not getattr(self,'audit_closed',True):
            r.save(r.HERE/'results/transport'/(self.session_id+'.json'),dict(session_id=self.session_id,
                **self.http.stats,range_hash_details_private=True,whole_file_sha_available=False))
            self.audit_closed=True
        super().close()
