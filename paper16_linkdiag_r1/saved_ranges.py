"""Offline opaque metadata-range replay; missing bytes never trigger acquisition."""
from pathlib import Path
import hashlib
import io


class MissingSavedRange(RuntimeError):
    pass


class SavedRangeReader(io.RawIOBase):
    def __init__(self, root, size, ranges):
        self.root=Path(root).resolve();self.size=size;self.pos=0;self.parts=[]
        for row in ranges:
            name=Path(row['payload_path'])
            if name.is_absolute() or '..' in name.parts or name.suffix!='.bin':
                raise ValueError('Unsafe saved metadata payload path')
            path=(self.root/name).resolve();path.relative_to(self.root)
            body=path.read_bytes()
            if len(body)!=row['bytes'] or hashlib.sha256(body).hexdigest()!=row['sha256']:
                raise ValueError('Saved metadata range corrupted')
            start=row['offset'];stop=start+len(body)
            if not 0<=start<stop<=size:
                raise ValueError('Saved source range bounds')
            for old_start,old_stop,old_body in self.parts:
                a,b=max(start,old_start),min(stop,old_stop)
                if a<b and body[a-start:b-start]!=old_body[a-old_start:b-old_start]:
                    raise ValueError('Contradictory overlapping saved source bytes')
            self.parts.append((start,stop,body))
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        if self.pos<0:raise ValueError('Negative saved seek')
        return self.pos
    def read(self,n=-1):
        if n<0 or n>8388608:raise MissingSavedRange('Oversized or unbounded saved metadata read')
        n=min(n,max(0,self.size-self.pos));out=bytearray()
        while n:
            candidates=[x for x in self.parts if x[0]<=self.pos<x[1]]
            if not candidates:raise MissingSavedRange(f'No saved metadata bytes at {self.pos}; network fallback forbidden')
            a,b,body=max(candidates,key=lambda x:x[1]);take=min(n,b-self.pos)
            out.extend(body[self.pos-a:self.pos-a+take]);self.pos+=take;n-=take
        return bytes(out)
    def readinto(self,buffer):
        body=self.read(len(buffer));buffer[:len(body)]=body;return len(body)
