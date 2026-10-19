"""Version-bound legacy range/hard-link primitives,explicitly extracted;no legacy imports or workers."""
import io,hashlib
import requests,h5py

class RangeReader(io.RawIOBase):
    def __init__(self, url, size, max_bytes=2097152, etag=None):
        self.url, self.size, self.pos = url, size, 0
        self.used, self.maximum, self.ranges = 0, max_bytes, []
        self.http = requests.Session()
        self.cache = {}
        self.etag = etag
        self.reserved=0;self.calls=0
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        if self.pos < 0: raise ValueError('Negative offset')
        return self.pos
    def read(self, n=-1):
        if n < 0 or n > 131072: raise RuntimeError('Range size budget exceeded')
        if n == 0: return b''
        if self.pos >= self.size: return b''
        n = min(n, self.size - self.pos)
        key = (self.pos, n)
        if key not in self.cache:
            if self.reserved + n + 1 > self.maximum or self.calls>=256: raise RuntimeError('File metadata budget exceeded')
            self.reserved+=n+1;self.calls+=1
            end = self.pos + n - 1
            headers = {'Range': f'bytes={self.pos}-{end}'}
            if self.etag: headers['If-Match'] = self.etag
            with self.http.get(self.url, params={'p12_offset': self.pos, 'p12_length': n},
                               headers=headers, stream=True, timeout=20) as res:
                expected = f'bytes {self.pos}-{end}/{self.size}'
                if res.status_code != 206 or res.headers.get('Content-Range') != expected:
                    raise RuntimeError('Range not honored; no bulk response consumed')
                if self.etag and res.headers.get('ETag') != self.etag:
                    raise RuntimeError('Object version changed')
                payload = res.raw.read(n + 1)
                if len(payload) != n: raise RuntimeError('Range length mismatch')
            self.cache[key] = payload
            self.used += n
            self.ranges.append({'offset': self.pos, 'bytes': n, 'sha256': hashlib.sha256(payload).hexdigest()})
        self.pos += n
        return self.cache[key]
    def readinto(self, buf):
        value = self.read(len(buf))
        buf[:len(value)] = value
        return len(value)

def hard_object(file, path):
    group = file
    for part in path.strip('/').split('/'):
        if not isinstance(group, h5py.Group): raise RuntimeError('Expected group')
        if not isinstance(group.get(part, getlink=True), h5py.HardLink):
            raise RuntimeError('Soft/external link forbidden: ' + path)
        group = group[part]
    return group
