"""Selective HDF5 metadata decoding over checked, bounded HTTP ranges."""
import hashlib
import io
import json
import re
from pathlib import Path
import h5py
import numpy as np
import requests
from acquire import HERE
from register import sha, verify

class RangeReader(io.RawIOBase):
    def __init__(self, url, size, max_bytes=2097152, etag=None):
        self.url, self.size, self.pos = url, size, 0
        self.used, self.maximum, self.ranges = 0, max_bytes, []
        self.http = requests.Session()
        self.cache = {}
        self.etag = etag
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
            if self.used + n > self.maximum: raise RuntimeError('File metadata budget exceeded')
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

def permitted(path):
    return path in ('/session_start_time', '/timestamps_reference_time') or bool(
        re.fullmatch(r'/intervals/[^/]+/(start_time|stop_time|stimulus_name)', path)) or path == '/intervals/invalid_times/tags'

def hard_object(file, path):
    group = file
    for part in path.strip('/').split('/'):
        if not isinstance(group, h5py.Group): raise RuntimeError('Expected group')
        if not isinstance(group.get(part, getlink=True), h5py.HardLink):
            raise RuntimeError('Soft/external link forbidden: ' + path)
        group = group[part]
    return group

def validate_dataset(file, path):
    if not permitted(path): raise RuntimeError('Forbidden HDF5 value path: ' + path)
    data = hard_object(file, path)
    if not isinstance(data, h5py.Dataset): raise RuntimeError('Expected metadata dataset')
    if path.endswith(('/start_time', '/stop_time')):
        if data.ndim != 1 or data.dtype.kind != 'f': raise RuntimeError('Expected float timestamp vector')
    elif path in ('/session_start_time', '/timestamps_reference_time'):
        if data.ndim != 0 or data.dtype.kind not in 'SO': raise RuntimeError('Expected scalar string origin')
    return data

def read_metadata(file, path):
    if not permitted(path): raise RuntimeError('Forbidden HDF5 value path: ' + path)
    data = validate_dataset(file, path)
    if data.size * data.dtype.itemsize > 131072:
        if data.ndim != 1 or data.dtype.kind not in 'fiu':
            raise RuntimeError('Non-numeric metadata array budget exceeded')
        step = 65536 // data.dtype.itemsize
        return np.concatenate([data[start:start + step] for start in range(0, data.size, step)])
    return data[()]

def inspect(item):
    out = {'session_id': item['session_id'], 'recording_support': 'UNKNOWN',
           'decoded_neural_values': False, 'intervals': {}}
    if not item.get('hdf5_signature'):
        out['error'] = 'No verified HDF5 range access'
        return out
    reader = RangeReader('https://api.brain-map.org/api/v2/well_known_file_download/' + item['file_id'],
                         int(item['content_range'].split('/')[-1]), etag=item.get('etag'))
    try:
        with h5py.File(reader, 'r') as file:
            out['root_names'] = list(file.keys())
            for path in ('/session_start_time', '/timestamps_reference_time'):
                if path in file:
                    value = read_metadata(file, path)
                    out[path] = value.decode() if isinstance(value, bytes) else str(value)
            if '/acquisition' in file:
                out['acquisition_names_only'] = list(hard_object(file, '/acquisition').keys())
            if '/intervals' in file:
                for name in hard_object(file, '/intervals').keys():
                    group = hard_object(file, '/intervals/' + name)
                    interval = {'columns': list(group.keys())}
                    for field in ('start_time', 'stop_time'):
                        path = '/intervals/' + name + '/' + field
                        if path in file:
                            values = np.asarray(read_metadata(file, path), dtype=float)
                            interval[field] = {'n': values.size, 'finite': int(np.isfinite(values).sum()),
                                               'min': float(np.nanmin(values)) if values.size else None,
                                               'max': float(np.nanmax(values)) if values.size else None,
                                               'array_sha256': hashlib.sha256(values.tobytes()).hexdigest()}
                    out['intervals'][name] = interval
            out['limitation'] = 'Stimulus interval envelopes are not native continuous neural recording support; no acquisition sample values decoded'
    except Exception as exc:
        out['error'] = type(exc).__name__ + ': ' + str(exc)[:250]
    finally:
        out['transport_bytes'] = reader.used
        out['ranges'] = reader.ranges
        reader.http.close()
    return out

def main():
    verify()
    policy = json.loads((HERE / 'header_registration.json').read_text())
    if policy['policy_sha256'] != sha(HERE / 'HEADER_POLICY.json'): raise RuntimeError('Changed policy')
    directory = HERE / 'metadata/headers_code1'
    directory.mkdir(exist_ok=True)
    items = json.loads((HERE / 'metadata/allen_header_capability.json').read_text())
    for item in sorted(items, key=lambda r: r['session_id']):
        path = directory / (item['session_id'] + '.json')
        if path.exists(): continue
        result = inspect(item)
        path.write_text(json.dumps(result, indent=2, sort_keys=True))
        print(json.dumps({'session': item['session_id'], 'bytes': result.get('transport_bytes'),
                          'interval_tables': len(result['intervals']), 'error': result.get('error')}), flush=True)

if __name__ == '__main__': main()
