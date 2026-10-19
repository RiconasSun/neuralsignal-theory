"""One registered source-object metadata inspection with durable accounting."""
from pathlib import Path
import contextlib
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import h5py
import requests
from .links import Inspector, LinkProblem, ALLOWED, no_dataset_values

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_linkdiag_r1'
E = R / 'ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1'


class ResourceLimit(RuntimeError):
    pass


def guard(deadline):
    if time.monotonic() >= deadline:
        raise ResourceLimit('Registered 600-second source deadline exhausted')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write_once(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())


class Journal:
    def __init__(self, path):
        self.file = Path(path).open('x', encoding='utf8', newline='\n')
    def append(self, row):
        self.file.write(json.dumps(row, allow_nan=False)+'\n'); self.file.flush(); os.fsync(self.file.fileno())
    def close(self):
        self.file.close()


def review_gate():
    reg = read(P/'ACCESS_REGISTRATION.json')
    receipt = read(E/'PREACCESS_APPROVAL.json')
    required = {'paper16_linkdiag_r1/'+x for x in ['ACCESS_REGISTRATION.json','links.py','inspect_source.py','test_diagnostic.py','saved_ranges.py']}
    if receipt.get('decision') != 'ACCEPTED_SINGLE_OBJECT_METADATA_ONLY' or any(type(receipt.get(k)) is not int or receipt[k] != 0 for k in ['open_P0','open_P1']):
        raise ValueError('Independent metadata-only approval absent or failed')
    if not required <= receipt.get('reviewed_hashes', {}).keys():
        raise ValueError('Incomplete review source binding')
    for name, digest in receipt['reviewed_hashes'].items():
        path = (R/name).resolve()
        if not path.is_relative_to(R) or sha(path) != digest:
            raise ValueError('Reviewed source identity mismatch')
    if sha(E/'PREACCESS_REVIEW.md') != receipt['report_sha256']:
        raise ValueError('Independent report mismatch')
    for name, digest in reg['prior_source_pins'].items():
        if sha(R/name) != digest:
            raise ValueError('Historical source/stop modified')
    return reg


def validate_source(item, reg):
    if item != reg['source'] or item['session_id'] != 750749662 or item['mouse_id'] != '726162197' or item['role'] != 'Development':
        raise ValueError('Additional/Final/altered source denied before open')


class MetadataRangeReader(io.RawIOBase):
    def __init__(self, item, deadline, journal, body_dir=None):
        self.item, self.deadline, self.journal = item, deadline, journal
        self.pos = self.used = self.reserved = self.calls = 0
        self.cache = {}; self.ranges = []; self.headers = []
        self.http = requests.Session()
        self.body_dir = Path(body_dir) if body_dir is not None else None
        if self.body_dir is not None:
            self.body_dir.resolve().relative_to(P.resolve())
            self.body_dir.mkdir()
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos+offset if whence == 1 else self.item['size']+offset
        if self.pos < 0: raise ValueError('Negative seek')
        return self.pos
    def read(self, n=-1):
        guard(self.deadline)
        if n < 0 or n > 8388608: raise ResourceLimit('Oversized HDF5 metadata request')
        n = min(n, max(0, self.item['size']-self.pos)); output = bytearray()
        while n:
            guard(self.deadline); size = min(n, 131072); key = self.pos, size
            if key not in self.cache:
                if self.calls >= 128 or self.reserved+size+1 > 8388608:
                    raise ResourceLimit('Registered request/byte ceiling reached before request')
                self.calls += 1; self.reserved += size+1
                req = self.calls; first = self.pos; last = first+size-1
                self.journal.append({'event':'RESERVED','request':req,'offset':first,'expected_bytes':size,'reserved_bytes':size+1})
                url = 'https://api.brain-map.org/api/v2/well_known_file_download/'+str(self.item['file_id'])
                with self.http.get(url,params={'p16_linkdiag_offset':first,'p16_linkdiag_length':size},
                        headers={'Range':f'bytes={first}-{last}','If-Match':self.item['etag']},
                        stream=True,timeout=min(20,max(.001,self.deadline-time.monotonic()))) as response:
                    header={'request':req,'status':response.status_code,'content_range':response.headers.get('Content-Range'),'etag':response.headers.get('ETag')}
                    self.headers.append(header); self.journal.append({'event':'RESPONSE_HEADERS',**header})
                    if response.status_code != 206 or header['content_range'] != f'bytes {first}-{last}/{self.item["size"]}' or header['etag'] != self.item['etag']:
                        raise RuntimeError('Pinned metadata range identity failed; no bulk fallback')
                    payload=bytearray()
                    while len(payload) <= size:
                        guard(self.deadline)
                        chunk=response.raw.read(min(16384,size+1-len(payload)))
                        if not chunk: break
                        payload.extend(chunk); self.used += len(chunk)
                        self.journal.append({'event':'PAYLOAD','request':req,'bytes':len(chunk)})
                    guard(self.deadline)
                    if len(payload) != size: raise RuntimeError('Metadata range length mismatch')
                data=bytes(payload)
                row={'request':req,'offset':first,'bytes':size,'sha256':hashlib.sha256(data).hexdigest()}
                if self.body_dir is not None:
                    path=self.body_dir/f'META_RANGE_{req:04}.bin'
                    with path.open('xb') as out:
                        out.write(data);out.flush();os.fsync(out.fileno())
                    row['payload_path']=path.relative_to(R).as_posix()
                self.cache[key]=data
                self.ranges.append(row);self.journal.append({'event':'COMPLETE_RANGE',**row})
            output.extend(self.cache[key]);self.pos+=size;n-=size
        return bytes(output)
    def readinto(self, buffer):
        data=self.read(len(buffer));buffer[:len(data)]=data;return len(data)


def worker(deadline):
    reg=review_gate();validate_source(reg['source'],reg);guard(deadline)
    results=P/'results';results.mkdir(exist_ok=True)
    parent=read(results/'INSPECTION_ATTEMPT.json')
    if parent['deadline'] != deadline or parent['registration_sha256'] != sha(P/'ACCESS_REGISTRATION.json'):
        raise ValueError('Parent registered deadline/identity mismatch')
    write_once(results/'SOURCE_OPEN_ATTEMPT.json',{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'source':reg['source'],'inspection_sha256':sha(Path(__file__)),'deadline':deadline,'no_retry':True})
    transport=Journal(results/'RANGE_JOURNAL.jsonl'); components=Journal(results/'COMPONENT_JOURNAL.jsonl')
    reader=MetadataRangeReader(reg['source'],deadline,transport,results/'metadata_ranges');inspector=None;value_canary=None
    result={'status':'INCONCLUSIVE_METADATA','running_numeric_values_read':0,'neural_values_read':0,'additional_sources':0}
    try:
        with no_dataset_values() as canary:
            value_canary=canary
            with h5py.File(reader,'r') as file:
                inspector=Inspector(file,components.append,lambda:guard(deadline))
                result.update(inspector.run(reg['allowed_paths']))
            result['forbidden_dataset_value_calls']=canary['forbidden_value_calls']
        guard(deadline)
    except ResourceLimit as exc:
        result.update({'status':'INCONCLUSIVE_RESOURCE_LIMIT','error':str(exc)})
    except LinkProblem as exc:
        status='UNSAFE_OR_UNEXPECTED_LINK' if exc.kind in ['UNSAFE','CYCLE'] else 'SOURCE_SCHEMA_INCOMPATIBLE' if exc.kind in ['SCHEMA','MISSING'] else 'INCONCLUSIVE_METADATA'
        result.update({'status':status,'problem_kind':exc.kind,'problem_path':exc.path,'error':exc.detail})
    except Exception as exc:
        result.update({'status':'INCONCLUSIVE_METADATA','error':type(exc).__name__+': '+str(exc)})
    finally:
        result.update({'source':reg['source'],'registration_sha256':sha(P/'ACCESS_REGISTRATION.json'),
                       'new_range_requests':reader.calls,'new_payload_bytes':reader.used,'new_reserved_bytes':reader.reserved,
                       'ranges':reader.ranges,'response_headers':reader.headers,
                       'payload_accounting_complete': len(reader.ranges)==reader.calls,
                       'payload_upper_bound_if_incomplete': reader.reserved if len(reader.ranges)!=reader.calls else reader.used,
                       'forbidden_dataset_value_calls':value_canary['forbidden_value_calls'] if value_canary else 0,
                       'component_audit':inspector.rows if inspector else [],'worker_completed_monotonic':time.monotonic(),
                       'metadata_only':True,'production_reader_modified':False,'M2_restarted':False,'Final_C_D_access':False})
        write_once(results/'SOURCE_INSPECTION_RECEIPT.json',result)
        reader.http.close();transport.close();components.close()
    print(json.dumps({k:v for k,v in result.items() if k not in ['component_audit','objects','ranges','response_headers']}),flush=True)


def supervise(command, seconds, target, registration_sha256='synthetic'):
    started=time.monotonic();deadline=started+seconds
    write_once(Path(target).with_name('INSPECTION_ATTEMPT.json'),{'started':started,'deadline':deadline,'registration_sha256':registration_sha256})
    child=subprocess.Popen(command+['--deadline',repr(deadline)])
    try:
        code=child.wait(timeout=max(.001,deadline-time.monotonic()))
    except subprocess.TimeoutExpired:
        child.kill();child.wait()
        write_once(target,{'status':'INCONCLUSIVE_RESOURCE_LIMIT','child_killed':True,'valid_completed_inspection':False,
                   'started':started,'deadline':deadline,'completed':time.monotonic()})
        return 124
    completed=time.monotonic();valid=code==0 and completed<deadline
    write_once(target,{'status':'TIMELY_INSPECTION_COMPLETED' if valid else 'INCONCLUSIVE_RESOURCE_LIMIT' if completed>=deadline else 'INCONCLUSIVE_METADATA',
               'child_exit':code,'child_killed':False,'valid_completed_inspection':valid,
               'started':started,'deadline':deadline,'completed':completed})
    return code if code else (0 if valid else 124)


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker(float(sys.argv[sys.argv.index('--deadline')+1]))
    else:
        reg=review_gate();validate_source(reg['source'],reg)
        target=P/'results/SUPERVISION.json';target.parent.mkdir(exist_ok=True)
        raise SystemExit(supervise([sys.executable,'-m','paper16_linkdiag_r1.inspect_source','--worker'],600,target,sha(P/'ACCESS_REGISTRATION.json')))
