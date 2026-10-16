"""Trusted source adapter: bounded ranges, immutable assets, gated partition export.

NWB ragged unit times have no time-window index. The source adapter transiently
decodes one unit's timestamps then exports authorized windows only. It must not
summarize full-record or excluded-window neural outcomes. This is not a claim
that no final timestamp is ever decoded inside this trusted low-level adapter.
"""
import datetime
import hashlib
import io
import json
from pathlib import Path
import h5py
import numpy as np
import requests

P=Path(__file__).resolve().parent
ROOT=P.parent
CONFIG=json.loads((P/'ACTIVATION.json').read_text())
ALLOCATION=json.loads((P/'EPOCH_UNIT_ALLOCATION.json').read_text())['records']

def sha(data):return hashlib.sha256(data).hexdigest()
def append(path,row):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf8',newline='\n') as f:f.write(json.dumps(row,allow_nan=False)+'\n')

def require_access_approval():
    decision=P/'ACCESS_DECISION.json';approval=P/'PREACCESS_APPROVAL.json'
    if not decision.exists() or not approval.exists():raise PermissionError('Owner raw-source decision and independent preaccess approval required; no neural access')
    d=json.loads(decision.read_text());a=json.loads(approval.read_text())
    if not d.get('owner_explicitly_permits_fullrecord_decode') or not a.get('accepted'):raise PermissionError('Raw source access not authorized/approved')
    if sha((ROOT/d['owner_reply_path']).read_bytes())!=d['owner_reply_sha256']:raise PermissionError('Owner decision evidence mismatch')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:raise PermissionError('Preaccess review identity mismatch')
    for name,h in json.loads(freeze.read_text())['hashes'].items():
        if sha((ROOT/name).read_bytes())!=h:raise PermissionError('Unreviewed source change: '+name)
    return a

class SourceReader(io.RawIOBase):
    def __init__(self,record):
        require_access_approval() # before Session, source cache or network access
        self.record=record;self.a=record['asset'];self.size=self.a['size'];self.pos=0
        ids={r['asset']['asset_id'] for r in ALLOCATION}
        if self.a['asset_id'] not in ids:raise ValueError('Asset outside activated allocation')
        self.session=requests.Session();self.folder=P/'work/source_ranges'/self.a['asset_id'];self.folder.mkdir(parents=True,exist_ok=True)
        self.journal=P/'results/source_access.jsonl';self.used=0;self.memory={}
        prior=[json.loads(x) for x in self.journal.read_text().splitlines()] if self.journal.exists() else []
        self.total_calls=len(prior);self.total_bytes=sum(x.get('bytes',0) for x in prior)
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        p=n if whence==0 else self.pos+n if whence==1 else self.size+n
        if p<0 or p>self.size:raise ValueError('NWB seek bounds')
        self.pos=p;return p
    def block(self,start):
        end=min(self.size,start+1048576)-1
        if start in self.memory:return self.memory[start]
        path=self.folder/f'{start}.bin';receipt=path.with_suffix('.json')
        if path.exists():
            rec=json.loads(receipt.read_text());b=path.read_bytes()
            if rec['etag']!=self.record['etag'] or sha(b)!=rec['sha256'] or len(b)!=end-start+1:raise ValueError('Source cache identity/corruption')
        else:
            for attempt in range(2):
                if self.total_calls>=CONFIG['budgets']['requests_max'] or self.total_bytes>=CONFIG['budgets']['transport_bytes_max']:raise ValueError('Registered source budget exhausted')
                self.total_calls+=1
                rec={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'asset_id':self.a['asset_id'],'mouse_id':self.record['mouse_id'],'start':start,'stop':end,'attempt':attempt+1,'purpose':'opaqueNWBsource range; no neural outcome summary'};n=0
                try:
                    url=f"https://api.dandiarchive.org/api/assets/{self.a['asset_id']}/download/?p13exec_start={start}&n={end-start+1}"
                    with self.session.get(url,headers={'Range':f'bytes={start}-{end}','If-Match':self.record['etag']},stream=True,timeout=(20,60)) as r:
                        rec['status']=r.status_code
                        if r.status_code!=206:raise ValueError('Range refused; bulk body unread')
                        if r.headers.get('ETag')!=self.record['etag'] or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{self.size}':raise ValueError('Frozen NWB version/range mismatch')
                        parts=[]
                        for chunk in r.iter_content(65536):
                            n+=len(chunk)
                            if n>end-start+1 or self.total_bytes+n>CONFIG['budgets']['transport_bytes_max']:raise ValueError('Range/registered transport budget overflow')
                            parts.append(chunk)
                        b=b''.join(parts)
                        if len(b)!=end-start+1:raise ValueError('Range truncated')
                    self.total_bytes+=n;rec.update(bytes=n,etag=self.record['etag'],sha256=sha(b));append(self.journal,rec)
                    path.write_bytes(b);receipt.write_text(json.dumps(rec,indent=2)+'\n');break
                except Exception as exc:
                    self.total_bytes+=n;rec.update(bytes=n,error=repr(exc));append(self.journal,rec)
                    if attempt==1:raise
        self.used+=len(b);self.memory[start]=b
        return b
    def read(self,n=-1):
        if n<0 or n>134217728:raise ValueError('Unbounded source read forbidden')
        end=min(self.size,self.pos+n);parts=[]
        while self.pos<end:
            start=self.pos//1048576*1048576;b=self.block(start);take=min(end-self.pos,len(b)-(self.pos-start))
            parts.append(b[self.pos-start:self.pos-start+take]);self.pos+=take
        return b''.join(parts)
    def readinto(self,b):
        value=self.read(len(b));b[:len(value)]=value;return len(value)

def node(file,path):
    obj=file
    for part in path.strip('/').split('/'):
        if not isinstance(obj,h5py.Group) or not isinstance(obj.get(part,getlink=True),h5py.HardLink):raise ValueError('External/soft source link denied')
        obj=obj[part]
    if not isinstance(obj,h5py.Dataset) or obj.external or obj.is_virtual:raise ValueError('Not internal nonvirtual source dataset')
    return obj

def partition_windows(record,partition):
    allowed={'A'} if record['role']=='development' else {'C'}
    if partition not in allowed:raise PermissionError('Pre-fit source export permits A/C only')
    return [e for e in record['epochs'] if e['partition']==partition]

def cut_windows(times,windows):
    times=np.asarray(times,dtype=np.float64)
    if times.ndim!=1 or not np.isfinite(times).all():
        # A nonfinite timestamp cannot be assigned to any temporal partition.
        # Halt source extraction, do not silently discard it or mark one unit
        # physiologically bad using an unassignable full-record sample.
        raise ValueError('SOURCE_INTEGRITY_STOP: nonfinite/unassignable source timestamp')
    # No global ordering/rate/physiological-QC statistic may use excluded samples.
    # Structural nonfinite/unassignable source errors stop extraction, not unit QC.
    return [np.asarray(times[(times>=e['start'])&(times<e['stop'])]-e['start'],dtype=np.float64) for e in windows]

def load_unit(file,row):
    ix=node(file,'/units/spike_times_index')
    if ix.ndim!=1 or row<0 or row>=ix.shape[0]:raise ValueError('Invalid unit row')
    lo=int(ix[row-1]) if row else 0;hi=int(ix[row])
    times=node(file,'/units/spike_times')
    if times.ndim!=1 or not 0<=lo<=hi<=times.shape[0]:raise ValueError('Ragged storage index corrupt')
    # Full-record values stay private to the trusted source adapter; caller gets
    # only temporal windows. Storage lengths must not be used as physiological QC.
    return np.asarray(times[lo:hi],dtype=np.float64)

def unit_window_export(file,row,record,partition):
    windows=partition_windows(record,partition) # deny before any source value read
    result=cut_windows(load_unit(file,row),windows)
    return result
