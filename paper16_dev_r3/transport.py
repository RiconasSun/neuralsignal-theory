"""Bounded append-only R3 neural range transport, private cache, no retries."""
import io
import hashlib
import json
import os
from pathlib import Path
import time
import requests
from .core import P, SourceStop, ResourceStop, once, load, sha, validate_item
from .clock_bound import guard


class BudgetJournal:
    def __init__(self, path, reg, append=False):
        self.reg = reg; self.path = Path(path); self.reserved = 0; self.by_source = {}; self.payload = 0
        if append:
            for line in self.path.read_text(encoding='utf8').splitlines():
                row = json.loads(line)
                if row['event'] == 'RESERVED':
                    sid = row['session_id']; state = self.by_source.setdefault(sid, {'reserved': 0, 'requests': 0})
                    if row['request'] != state['requests']+1: raise SourceStop('Journal request identity/order corruption')
                    self.reserved += row['reserved_bytes']; state['reserved'] += row['reserved_bytes']; state['requests'] += 1
                elif row['event'] == 'PAYLOAD': self.payload += row['bytes']
        self.file = self.path.open('a' if append else 'x', encoding='utf8', newline='\n')
    def emit(self, event, **fields):
        self.file.write(json.dumps({'event': event, 'monotonic': time.monotonic(), **fields}, allow_nan=False)+'\n')
        self.file.flush(); os.fsync(self.file.fileno())
    def reserve(self, item, offset, size):
        cap = self.reg['resources']; sid = item['session_id']
        state = self.by_source.setdefault(sid, {'reserved': 0, 'requests': 0})
        amount = size+1
        if (self.reserved+amount > cap['aggregate_reserved_bytes_max']
                or state['reserved']+amount > cap['per_source_reserved_bytes_max']
                or state['requests'] >= cap['per_source_requests_max']):
            raise ResourceStop('Neural range budget denied BEFORE network; no fallback')
        state['requests'] += 1; state['reserved'] += amount; self.reserved += amount
        self.emit('RESERVED', session_id=sid, request=state['requests'], offset=offset, expected_bytes=size, reserved_bytes=amount)
        return state['requests']
    def close(self): self.file.close()


class RangeReader(io.RawIOBase):
    def __init__(self, item, reg, stage, journal, private_root, offline=False):
        validate_item(item, reg); guard(stage)
        self.item, self.reg, self.stage, self.journal = item, reg, stage, journal
        self.pos = self.used = self.calls = 0; self.ranges = []; self.cache = {}
        root = Path(private_root).resolve()
        if not root.is_relative_to((P/'work/private').resolve()): raise SourceStop('Raw source cache must remain private/ignored')
        self.private = root/str(item['session_id']); self.private.mkdir(parents=True, exist_ok=True)
        self.offline = offline; self.http = requests.Session()
        self.http.mount('https://', requests.adapters.HTTPAdapter(max_retries=0))
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        if type(offset) is not int or whence not in [0, 1, 2]: raise ResourceStop('Invalid source seek')
        self.pos = offset if whence == 0 else self.pos+offset if whence == 1 else self.item['size']+offset
        if self.pos < 0: raise SourceStop('Negative source offset')
        return self.pos
    def _block(self, offset):
        guard(self.stage)
        length = min(self.reg['resources']['per_request_bytes_max'], self.item['size']-offset)
        key = str(offset); path = self.private/(key+'.bin'); receipt = self.private/(key+'.json')
        if offset in self.cache: return self.cache[offset]
        if path.exists() or receipt.exists():
            if not path.exists() or not receipt.exists(): raise SourceStop('Incomplete private source cache; no retry')
            meta = load(receipt); payload = path.read_bytes()
            if (meta['session_id'] != self.item['session_id'] or meta['offset'] != offset or meta['bytes'] != length
                    or meta['etag'] != self.item['etag'] or meta['source_size'] != self.item['size']
                    or len(payload) != length or hashlib.sha256(payload).hexdigest() != meta['sha256']):
                raise SourceStop('Private source-cache identity/hash mismatch')
            self.cache[offset] = payload; return payload
        if self.offline: raise SourceStop('Required cached native range absent; no acquisition fallback')
        request = self.journal.reserve(self.item, offset, length); self.calls += 1
        end = offset+length-1; sid = self.item['session_id']
        url = 'https://api.brain-map.org/api/v2/well_known_file_download/'+str(self.item['file_id'])
        try:
            with self.http.get(url, params={'p16_r3_offset': offset, 'p16_r3_length': length},
                 headers={'Range': f'bytes={offset}-{end}', 'If-Match': self.item['etag']},
                 stream=True, allow_redirects=False, timeout=min(30, max(.001, self.stage['deadline_monotonic']-time.monotonic()))) as response:
                header = {'status': response.status_code, 'content_range': response.headers.get('Content-Range'), 'etag': response.headers.get('ETag')}
                self.journal.emit('HEADERS', session_id=sid, request=request, **header)
                if (header['status'] != 206 or header['content_range'] != f'bytes {offset}-{end}/{self.item["size"]}'
                        or header['etag'] != self.item['etag']):
                    raise SourceStop('Pinned exact206/range/ETag failed; no bulk body, redirect or retry')
                data = bytearray()
                # Persist every delivered partial byte before another source read can fail.
                with path.open('xb') as out:
                    while len(data) <= length:
                        guard(self.stage)
                        chunk = response.raw.read(min(16384, length+1-len(data)))
                        if not chunk: break
                        self.used += len(chunk); self.journal.payload += len(chunk)
                        self.journal.emit('PAYLOAD', session_id=sid, request=request, bytes=len(chunk))
                        out.write(chunk); out.flush(); os.fsync(out.fileno())
                        data.extend(chunk)
                    guard(self.stage)
                    if len(data) != length: raise SourceStop('Exact response-length failure; retain partial evidence')
            payload = bytes(data)
            meta = {'session_id': sid, 'offset': offset, 'bytes': length, 'etag': self.item['etag'],
                    'source_size': self.item['size'], 'request': request, 'sha256': hashlib.sha256(payload).hexdigest()}
            once(receipt, meta); self.journal.emit('COMPLETE_RANGE', **meta)
            self.ranges.append(meta); self.cache[offset] = payload; return payload
        except BaseException as exc:
            self.journal.emit('RANGE_FAILED', session_id=sid, request=request, error_type=type(exc).__name__, retry=False)
            raise
    def read(self, n=-1):
        guard(self.stage)
        if type(n) is not int or n < 0 or n > self.reg['resources']['logical_read_bytes_max']:
            raise ResourceStop('Unbounded/oversized source read denied before network')
        n = min(n, max(0, self.item['size']-self.pos)); result = bytearray()
        block = self.reg['resources']['per_request_bytes_max']
        while n:
            guard(self.stage); first = self.pos//block*block; payload = self._block(first)
            left = self.pos-first; count = min(n, len(payload)-left)
            if count <= 0: raise SourceStop('Native range/cache cursor mismatch')
            result.extend(payload[left:left+count]); self.pos += count; n -= count
        return bytes(result)
    def readinto(self, buffer):
        value = self.read(len(buffer)); buffer[:len(value)] = value; return len(value)
    def close(self):
        if getattr(self, 'http', None) is not None: self.http.close()
        super().close()
