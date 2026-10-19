"""Exact ranges, durable bounded timeout retries, immutable historical prefix."""
import io
import hashlib
import json
import os
import time
from pathlib import Path
import requests
import urllib3
from .core import R, P, S, SourceStop, ResourceStop, load, sha, once, guard, validate_item, private_file

TIMEOUTS = (requests.exceptions.Timeout, urllib3.exceptions.TimeoutError)


class Journal:
    def __init__(self, path, reg, append=False):
        self.path, self.reg = Path(path), reg
        self.by_source = {}; self.reserved = self.payload = self.recovery_slots = 0
        self.events = []
        if append:
            for line in self.path.read_text(encoding='utf8').splitlines(): self._account(json.loads(line))
        self.out = self.path.open('a' if append else 'x', encoding='utf8', newline='\n')
    def _account(self, row):
        sid = row['session_id']; state = self.by_source.setdefault(sid, {'requests':0, 'reserved':0, 'payload':0, 'recovery_slots':0})
        if row['event'] == 'RESERVED':
            if row['request'] != state['requests']+1: raise SourceStop('R4 journal request sequence changed')
            state['requests'] += 1; state['reserved'] += row['reserved_bytes']; self.reserved += row['reserved_bytes']
        elif row['event'] == 'PAYLOAD': state['payload'] += row['bytes']; self.payload += row['bytes']
        elif row['event'] == 'RETRY_SLOT_RESERVED': state['recovery_slots'] += 1; self.recovery_slots += 1
        self.events.append(row)
    def emit(self, event, session_id, **fields):
        row = {'event':event, 'session_id':session_id, 'monotonic':time.monotonic(), **fields}
        self.out.write(json.dumps(row, allow_nan=False)+'\n'); self.out.flush(); os.fsync(self.out.fileno()); self._account(row)
    def reserve(self, item, method, offset, length, attempt):
        sid = item['session_id']; state = self.by_source.get(sid, {'requests':0, 'reserved':0})
        cap = self.reg['resources']; amount = length+1
        if (not 0 <= length <= cap['per_request_bytes_max'] or self.reserved+amount > cap['aggregate_reserved_bytes_max']
            or state['reserved']+amount > cap['per_source_reserved_bytes_max'] or state['requests'] >= cap['per_source_requests_max']):
            raise ResourceStop('R4 request/byte cap denied BEFORE network')
        request = state['requests']+1
        self.emit('RESERVED',sid,request=request,method=method,offset=offset,expected_bytes=length,reserved_bytes=amount,attempt=attempt)
        return request
    def retry_slot(self, item, offset, length):
        sid = item['session_id']; count = self.by_source[sid]['recovery_slots']; policy = self.reg['recovery']
        if count >= policy['new_timeout_recovery_slots_per_source_max'] or self.recovery_slots >= policy['new_timeout_recovery_slots_global_max']:
            raise ResourceStop('R4 timeout recovery cap exhausted; no second request')
        self.emit('RETRY_SLOT_RESERVED',sid,offset=offset,length=length)
    def close(self): self.out.close()


class Transport:
    def __init__(self, item, reg, stage, journal):
        validate_item(item,reg); guard(stage)
        if item['session_id'] in [x['session_id'] for x in reg['objects'][:3]]:
            raise SourceStop('Successfully completed R3 source must not be reopened')
        self.item,self.reg,self.stage,self.journal = item,reg,stage,journal
        self.http = requests.Session(); self.http.mount('https://',requests.adapters.HTTPAdapter(max_retries=0))
        self.url = 'https://api.brain-map.org/api/v2/well_known_file_download/'+str(item['file_id'])
    def timeout(self):
        guard(self.stage)
        return min(30,max(.001,self.stage['deadline_monotonic']-time.monotonic()))
    def head(self):
        sid=self.item['session_id']; request=self.journal.reserve(self.item,'HEAD',None,0,1)
        guard(self.stage); self.journal.emit('HTTP_SENT',sid,request=request,method='HEAD',attempt=1)
        try:
            with self.http.head(self.url,headers={'If-Match':self.item['etag'],'Accept-Encoding':'identity'},
                                allow_redirects=False,timeout=self.timeout()) as response:
                result={'status':response.status_code,'etag':response.headers.get('ETag'),'size':response.headers.get('Content-Length')}
                self.journal.emit('HEADERS',sid,request=request,**result)
                if result != {'status':200,'etag':self.item['etag'],'size':str(self.item['size'])}:
                    raise SourceStop('Non-neural HEAD exact identity/size/ETag preflight failed')
                guard(self.stage); self.journal.emit('PREFLIGHT_PASS',sid,request=request,body_bytes=0)
                return result
        except BaseException as exc:
            self.journal.emit('REQUEST_FAILED',sid,request=request,error_type=type(exc).__name__,retry=False); raise
    def download(self, offset, length):
        if type(offset) is not int or type(length) is not int or not 0 <= offset < offset+length <= self.item['size']:
            raise SourceStop('Invalid exact source offsets')
        sid=self.item['session_id']; end=offset+length-1
        for attempt in [1,2]:
            guard(self.stage); request=self.journal.reserve(self.item,'GET',offset,length,attempt)
            path=P/'work/private/http_attempts'/str(sid)/(f'{request:05}.bin'); path.parent.mkdir(parents=True,exist_ok=True)
            try:
                guard(self.stage); self.journal.emit('HTTP_SENT',sid,request=request,method='GET',attempt=attempt,offset=offset,length=length)
                with self.http.get(self.url,params={'p16_r4_offset':offset,'p16_r4_length':length},
                    headers={'Range':f'bytes={offset}-{end}','If-Match':self.item['etag'],'Accept-Encoding':'identity'},
                    stream=True,allow_redirects=False,timeout=self.timeout()) as response:
                    headers={'status':response.status_code,'content_range':response.headers.get('Content-Range'),
                             'etag':response.headers.get('ETag'),'content_length':response.headers.get('Content-Length')}
                    self.journal.emit('HEADERS',sid,request=request,**headers)
                    if (headers['status'] != 206 or headers['etag'] != self.item['etag']
                        or headers['content_range'] != f'bytes {offset}-{end}/{self.item["size"]}'
                        or headers['content_length'] not in [None,str(length)]):
                        raise SourceStop('Exact206/range/ETag/length header mismatch; no body or retry')
                    data=bytearray()
                    with path.open('xb') as out:
                        while len(data) <= length:
                            guard(self.stage); chunk=response.raw.read(min(16384,length+1-len(data)))
                            if not chunk: break
                            self.journal.emit('PAYLOAD',sid,request=request,bytes=len(chunk))
                            out.write(chunk);out.flush();os.fsync(out.fileno());data.extend(chunk)
                        guard(self.stage)
                        if len(data) != length: raise SourceStop('Incomplete/oversized body; retained partial is never accepted')
                payload=bytes(data)
                self.journal.emit('COMPLETE_HTTP_BODY',sid,request=request,offset=offset,length=length,sha256=hashlib.sha256(payload).hexdigest(),attempt=attempt)
                if attempt == 2:self.journal.emit('RECOVERED_R4_TIMEOUT',sid,request=request,offset=offset,length=length)
                return payload,request
            except BaseException as exc:
                retry=isinstance(exc,TIMEOUTS) and attempt == 1
                self.journal.emit('REQUEST_FAILED',sid,request=request,error_type=type(exc).__name__,retry=retry,attempt=attempt)
                if not retry: raise
                self.journal.retry_slot(self.item,offset,length)
                delay=self.reg['recovery']['backoff_seconds']; guard(self.stage)
                if time.monotonic()+delay >= self.stage['deadline_monotonic']: raise ResourceStop('No wall budget for fixed recovery delay')
                time.sleep(delay);guard(self.stage)
        raise AssertionError('Two-request loop must terminate')
    def cache(self, offset, payload, origin, **fields):
        root=P/'work/private/ranges'/str(self.item['session_id']);root.mkdir(parents=True,exist_ok=True)
        path=root/(str(offset)+'.bin'); private_file(path,payload)
        receipt={'session_id':self.item['session_id'],'offset':offset,'bytes':len(payload),'source_size':self.item['size'],
            'etag':self.item['etag'],'sha256':hashlib.sha256(payload).hexdigest(),'origin':origin,**fields}
        once(path.with_suffix('.json'),receipt)
        return receipt
    def recover_historical(self):
        policy=self.reg['recovery']
        if self.item['session_id'] != policy['session_id']:raise SourceStop('Only exact fourth source may recover historical range')
        prefix_path=R/policy['prefix_path'];prefix=prefix_path.read_bytes()
        if len(prefix) != policy['prefix_length'] or hashlib.sha256(prefix).hexdigest()!=policy['prefix_sha256']:
            raise SourceStop('Saved original prefix corrupted; no request')
        if (policy['suffix_offset'] != policy['old_offset']+len(prefix)
            or len(prefix)+policy['suffix_length'] != policy['old_length']):raise SourceStop('Prefix/suffix overlap or gap')
        suffix,request=self.download(policy['suffix_offset'],policy['suffix_length'])
        if prefix_path.read_bytes()!=prefix:raise SourceStop('R3 prefix changed during recovery')
        payload=prefix+suffix
        if len(payload)!=policy['old_length']:raise SourceStop('Reconstructed range length mismatch')
        receipt=self.cache(policy['old_offset'],payload,'R3_PREFIX_PLUS_R4_EXACT_SUFFIX',
            prefix_sha256=policy['prefix_sha256'],prefix_bytes=len(prefix),suffix_offset=policy['suffix_offset'],
            suffix_bytes=len(suffix),suffix_sha256=hashlib.sha256(suffix).hexdigest(),request=request)
        self.journal.emit('RECOVERED_HISTORICAL_R3_RANGE',self.item['session_id'],**{k:v for k,v in receipt.items() if k!='session_id'})
        return receipt
    def close(self):self.http.close()


class RangeReader(io.RawIOBase):
    def __init__(self,transport,offline=False):
        self.t=transport;self.item=transport.item;self.reg=transport.reg;self.stage=transport.stage
        self.pos=0;self.memory={};self.offline=offline
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        if type(offset) is not int or whence not in [0,1,2]:raise SourceStop('Invalid seek')
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.item['size']+offset
        if self.pos<0:raise SourceStop('Negative source seek')
        return self.pos
    def block(self,offset):
        guard(self.stage)
        if offset in self.memory:return self.memory[offset]
        length=min(self.reg['resources']['per_request_bytes_max'],self.item['size']-offset)
        for origin,root in [('R4',P),('R3',S)]:
            path=root/'work/private/ranges'/str(self.item['session_id'])/(str(offset)+'.bin');receipt=path.with_suffix('.json')
            if origin=='R3' and path.exists() and not receipt.exists():continue
            if path.exists() or receipt.exists():
                if not path.exists() or not receipt.exists():raise SourceStop('Incomplete new cache publication; no fallback')
                meta=load(receipt);payload=path.read_bytes()
                if (meta['session_id']!=self.item['session_id'] or meta['offset']!=offset or meta['bytes']!=length
                    or meta['source_size']!=self.item['size'] or meta['etag']!=self.item['etag']
                    or len(payload)!=length or hashlib.sha256(payload).hexdigest()!=meta['sha256']):raise SourceStop('Cache source/hash identity mismatch')
                if origin=='R3':
                    pins={r['path']:r for r in load(P/'R3_REUSE_MANIFEST.json')['private_files']}
                    for f in [path,receipt]:
                        row=pins.get(f.relative_to(R).as_posix())
                        if row is None or sha(f)!=row['sha256']:raise SourceStop('Unverified historical cache denied')
                    self.t.journal.emit('R3_COMPLETE_CACHE_REUSED',self.item['session_id'],offset=offset,bytes=length,sha256=meta['sha256'])
                self.memory[offset]=payload;return payload
        policy=self.reg['recovery']
        if self.item['session_id']==policy['session_id'] and offset==policy['old_offset']:
            raise SourceStop('Historical incomplete range must be explicitly suffix-recovered first')
        if self.offline:raise SourceStop('Required complete cache absent; offline mode forbids acquisition')
        payload,request=self.t.download(offset,length);self.t.cache(offset,payload,'R4_EXACT_NEW_RANGE',request=request)
        self.memory[offset]=payload;return payload
    def read(self,n=-1):
        guard(self.stage)
        if type(n) is not int or n<0 or n>self.reg['resources']['logical_read_bytes_max']:raise ResourceStop('Unbounded/oversized source read denied')
        n=min(n,max(0,self.item['size']-self.pos));result=bytearray();step=self.reg['resources']['per_request_bytes_max']
        while n:
            first=self.pos//step*step;payload=self.block(first);start=self.pos-first;count=min(n,len(payload)-start)
            if count<=0:raise SourceStop('Cache cursor/length mismatch')
            result.extend(payload[start:start+count]);self.pos+=count;n-=count
        return bytes(result)
    def readinto(self,buffer):
        value=self.read(len(buffer));buffer[:len(value)]=value;return len(value)
