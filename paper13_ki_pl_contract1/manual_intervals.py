"""Only the one registered target's manual bad-interval member, via byte ranges."""
import io
import json
import zipfile
import h5py
from sources import P,M,Transport,sha

URL='https://zenodo.org/api/records/14205018/files/preprocessing.zip/content'
SIZE=1928203597

class ArchiveReader(io.RawIOBase):
    def __init__(self,t): self.t=t;self.pos=0;self.cache={};self.used=0;self.ranges=[]
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        p=n if whence==0 else self.pos+n if whence==1 else SIZE+n
        if p<0 or p>SIZE:raise ValueError('Seek outside fixed archive')
        self.pos=p;return p
    def read(self,n=-1):
        if n<0:
            n=SIZE-self.pos
            if n>65558:raise ValueError('Unbounded read denied')
        if n>12582912:raise ValueError('Range budget')
        end=min(SIZE,self.pos+n);parts=[]
        while self.pos<end:
            start=self.pos//65536*65536;stop=min(SIZE,start+65536)-1
            if start not in self.cache:
                data,h,_=self.t.request(URL,headers={'Range':f'bytes={start}-{stop}'},maximum=stop-start+1)
                if h.get('Content-Range')!=f'bytes {start}-{stop}/{SIZE}' or len(data)!=stop-start+1:raise ValueError('Range identity mismatch')
                self.used+=len(data)
                if self.used>12582912:raise ValueError('Archive transport budget')
                self.cache[start]=data;self.ranges.append({'start':start,'bytes':len(data),'sha256':sha(data)})
            take=min(end,stop+1)-self.pos
            parts.append(self.cache[start][self.pos-start:self.pos-start+take]);self.pos+=take
        return b''.join(parts)
    def readinto(self,b):
        d=self.read(len(b));b[:len(d)]=d;return len(d)

def decode(data):
    with h5py.File(io.BytesIO(data),'r') as h:
        if set(h.keys())!={'badtints'} or not isinstance(h.get('badtints',getlink=True),h5py.HardLink):raise ValueError('Unexpected interval member')
        d=h['badtints']
        if d.external or d.ndim!=2 or d.shape[1]!=2 or d.shape[0]>10000:raise ValueError('Not bounded interval metadata')
        rows=d[()].tolist()
        from audit import validate_intervals
        validate_intervals(rows)
        return {'dataset':'badtints','intervals':rows,'attrs':{k:str(v) for k,v in d.attrs.items()}}

def main():
    # Freeze implementation identity before the first new interval extraction.
    freeze=M/'interval_acquisition_source_freeze.json'
    if not freeze.exists():
        with freeze.open('x') as f:json.dump({x.name:sha(x.read_bytes()) for x in [P/'REGISTRATION.json',P/'sources.py',Path(__file__)]},f,indent=2)
    expected='preprocessing/bad_times_manual/147463_20191113_probe0__badtimes.h5'
    if (M/'manual_bad_intervals.json').exists():raise FileExistsError('Immutable acquisition already exists')
    reader=ArchiveReader(Transport())
    with zipfile.ZipFile(reader) as z:
        names=[n for n in z.namelist() if '/bad_times_manual/' in n and n.endswith('.h5')]
        if expected not in names:raise ValueError('Registered member missing')
        item=z.getinfo(expected)
        if item.file_size>65536:raise ValueError('Unexpected interval size')
        b=z.read(item)
        (M/'147463_20191113_probe0__badtimes.h5').write_bytes(b)
        result=decode(b)
    result.update(member=expected,member_sha256=sha(b),all_manual_members=names,source_url=URL,
                  declared_archive_md5='4bbf126e997dea2cf88f7eb92bc27b07',full_archive_checksum_verified=False,
                  ranges=reader.ranges,range_bytes=reader.used,
                  identity_limit='Fixed published record/size/declared checksum and individual ranges; no ETag or independently verified full archive hash')
    (M/'manual_bad_intervals.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))

if __name__=='__main__':
    from pathlib import Path
    main()
