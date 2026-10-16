"""Bounded public metadata acquisition. Never imports a spike/neural loader."""
import datetime
import hashlib
import io
import json
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
META = HERE / 'metadata'
POLICY = json.loads((HERE/'M0_REGISTRATION.json').read_text())
META.mkdir(exist_ok=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Transport:
    def __init__(self):
        journal = META/'access.jsonl'
        prior = [json.loads(line) for line in journal.read_text().splitlines()] if journal.exists() else []
        self.calls = len(prior)
        self.used = sum(row.get('bytes',0) for row in prior)
        self.session = requests.Session()

    def request(self, url, *, method='GET', headers=None, params=None, maximum=4000000):
        if not url.startswith(('https://api.github.com/repos/int-brain-lab/',
                               'https://raw.githubusercontent.com/int-brain-lab/',
                               'https://docs.internationalbrainlab.org/',
                               'https://ibl-brain-wide-map-public.s3.amazonaws.com/aggregates/')):
            raise ValueError('Outside registered metadata providers')
        if 'spikes' in url.lower():
            raise ValueError('Spike access forbidden')
        last = None
        for attempt in range(POLICY['bounds']['attempts_per_request']):
            self.calls += 1
            if self.calls > POLICY['bounds']['http_requests']:
                raise RuntimeError('Request budget exceeded')
            record = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      'url': url, 'method': method, 'params': params,
                      'headers': headers, 'attempt': attempt+1}
            count = 0
            try:
                with self.session.request(method, url, params=params, headers=headers,
                                          timeout=(15,45), stream=True) as res:
                    record.update(status=res.status_code,
                                  response_headers=dict(res.headers))
                    # A failed range request must never consume a bulk object.
                    if headers and 'Range' in headers and res.status_code != 206:
                        raise RuntimeError('Range request not honored')
                    res.raise_for_status()
                    chunks, count = [], 0
                    for chunk in res.iter_content(65536):
                        count += len(chunk)
                        self.used += len(chunk)
                        if count > maximum or self.used > POLICY['bounds']['transport_bytes']:
                            raise RuntimeError('Transport byte budget exceeded')
                        chunks.append(chunk)
                    payload = b''.join(chunks)
                    record.update(bytes=len(payload), sha256=sha(payload))
                    return payload, dict(res.headers), record
            except Exception as exc:
                last = exc
                record['error'] = repr(exc)
            finally:
                record.setdefault('bytes', count)
                with (META/'access.jsonl').open('a',encoding='utf8') as f:
                    f.write(json.dumps(record)+'\n')
        raise RuntimeError(f'Metadata access failed: {url}') from last

    def save(self, name, url):
        data, headers, receipt = self.request(url)
        with (META/name).open('xb') as f:
            f.write(data)
        with (META/(name+'.receipt.json')).open('x',encoding='utf8') as f:
            f.write(json.dumps(receipt,indent=2)+'\n')
        return data


class ParquetRanges(io.RawIOBase):
    def __init__(self, transport, url):
        self.transport, self.url, self.pos = transport, url, 0
        _, head, receipt = transport.request(url,method='HEAD')
        self.size = int(head['Content-Length'])
        self.etag = head['ETag']
        self.head = receipt
        self.cache = {}

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        target = offset if whence == 0 else self.pos+offset if whence == 1 else self.size+offset
        if target < 0 or target > self.size:
            raise ValueError('Invalid metadata range')
        self.pos = target
        return target

    def read(self, n=-1):
        if n < 0:
            raise ValueError('Unbounded parquet read forbidden')
        n = min(n, self.size-self.pos)
        if not n: return b''
        start, end = self.pos, self.pos+n-1
        key = (start,n)
        if key not in self.cache:
            data, headers, _ = self.transport.request(
                self.url, headers={'Range':f'bytes={start}-{end}', 'If-Match':self.etag},
                params={'p13_start':start,'p13_length':n},maximum=n)
            if headers.get('Content-Range') != f'bytes {start}-{end}/{self.size}' or headers.get('ETag') != self.etag or len(data)!=n:
                raise RuntimeError('Metadata object/range changed')
            self.cache[key] = data
        self.pos += n
        return self.cache[key]

    def readinto(self, buf):
        data = self.read(len(buf)); buf[:len(data)] = data
        return len(data)


def sources():
    t=Transport()
    commit = json.loads(t.save('provider_commit.json','https://api.github.com/repos/int-brain-lab/paper-brain-wide-map/commits/main'))['sha']
    base=f'https://raw.githubusercontent.com/int-brain-lab/paper-brain-wide-map/{commit}/'
    t.save('bwm_loading.py.source',base+'brainwidemap/bwm_loading.py')
    t.save('fixture.csv',base+'brainwidemap/fixtures/2023_12_bwm_release.csv')
    t.save('provider_README.md',base+'README.md')
    t.save('release_documentation.html','https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html')
    print(json.dumps({'source_commit':commit,'requests':t.calls,'bytes':t.used}))


if __name__=='__main__':
    sources()
