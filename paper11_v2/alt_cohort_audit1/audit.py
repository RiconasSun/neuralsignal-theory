"""Bounded public repository-metadata acquisition; no data-file downloads."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from register import HERE, OUT, ROOT, read, save, sha, verify

API_HOSTS = {'api.osf.io', 'api.figshare.com'}
DOC_HOSTS = {'osf.io', 'www.nature.com', 'doi.org', 'figshare.com'}


def permitted(url, kind):
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.username or parts.password:
        return False
    if kind == 'api':
        return ((parts.hostname == 'api.osf.io' and parts.path.startswith('/v2/')) or
                (parts.hostname == 'api.figshare.com' and parts.path.startswith('/v2/articles/')))
    if kind == 'document':
        return parts.hostname in DOC_HOSTS and ('download' not in parts.path.lower())
    return False


def classify_file(name):
    # Names classify metadata availability only; they never authorize downloads.
    low = name.lower()
    if low.endswith(('.zip', '.tar', '.gz', '.7z')):
        return 'MIXED_ARCHIVE_NOT_OPENED'
    if low.endswith(('.ncs', '.ns1', '.ns2', '.ns3', '.ns4', '.ns5', '.ns6', '.nev', '.mat', '.h5', '.nwb')):
        return 'BINARY_DATA_NOT_OPENED'
    if any(k in low for k in ('spike', 'timestamp', 'waveform', 'behavior', 'response', 'outcome')):
        return 'POTENTIALLY_PROTECTED_VALUES_NOT_OPENED'
    if any(k in low for k in ('readme', 'license', 'dictionary', 'manifest', 'header', 'clock', 'gap')):
        return 'DOCUMENT_CANDIDATE_REQUIRES_ACCESS_PLAN'
    return 'INVENTORY_ONLY'


def verdict(qc):
    if qc.get('authoritative_incompatibility') is True:
        return 'FAIL'
    mandatory = ['complete_inventory', 'pinned_version', 'license_established',
                 'canonical_patient_mapping', 'independence_supported',
                 'native_recording_support', 'gaps_verified', 'clock_mapping_verified']
    if all(qc.get(k) is True for k in mandatory) and qc.get('documented_eligible_patients', 0) >= 8:
        return 'PASS'
    if (all(qc.get(k) is True for k in mandatory) and
            qc.get('cohort_eligibility_complete') is True and qc.get('documented_eligible_patients', 0) < 8):
        return 'FAIL'
    return 'INCONCLUSIVE'


def register_implementation():
    verify()
    save(OUT / 'implementation_registration.json', {
        'registered_utc': datetime.now(timezone.utc).isoformat(),
        'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in
                          [Path(__file__), HERE / 'test_audit.py']},
        'no_data_file_downloads': True})


def verify_implementation():
    verify()
    for name, digest in read(OUT / 'implementation_registration.json')['source_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('Registered implementation changed: ' + name)


class Collector:
    def __init__(self, name):
        import requests
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'P11-metadata-only-audit/1.0'
        self.folder = OUT / name
        self.folder.mkdir(exist_ok=False)
        self.policy = read(HERE / 'protocol.json')['source_policy']
        self.receipts = []
        self.total = 0

    def get(self, url, kind='api'):
        if not permitted(url, kind):
            raise ValueError('Forbidden acquisition endpoint')
        if len(self.receipts) >= self.policy['max_requests']:
            raise RuntimeError('Request budget exhausted')
        record = {'url': url, 'kind': kind, 'utc': datetime.now(timezone.utc).isoformat(),
                  'data_file_download': False}
        data = bytearray()
        try:
            with self.session.get(url, stream=True, timeout=self.policy['timeout_seconds'],
                                  allow_redirects=False) as response:
                record.update(status=response.status_code, headers={k: response.headers.get(k) for k in
                              ('Content-Type', 'ETag', 'Last-Modified', 'Location')})
                for chunk in response.iter_content(16384):
                    if len(data) + len(chunk) > self.policy['per_response_bytes'] or self.total + len(data) + len(chunk) > self.policy['total_bytes']:
                        raise RuntimeError('Metadata byte budget exhausted')
                    data.extend(chunk)
                if response.status_code != 200:
                    record['error'] = 'HTTP_NOT_200'
                elif kind == 'api' and 'json' not in response.headers.get('Content-Type', '').lower():
                    record['error'] = 'API_NOT_JSON'
        except Exception as error:
            record['error'] = type(error).__name__
            record['message'] = 'Bounded metadata request failed; no data download fallback'
        self.total += len(data)
        file = f'{len(self.receipts):03d}.receipt'
        (self.folder / file).write_bytes(data)
        record.update(local=file, bytes=len(data), sha256=sha(self.folder/file))
        self.receipts.append(record)
        if 'error' in record:
            return None
        if kind == 'api':
            try:
                return json.loads(data)
            except (ValueError, UnicodeError):
                record['error'] = 'INVALID_JSON'
                return None
        return bytes(data).decode('utf-8', errors='replace')

    def finish(self):
        save(self.folder / 'receipts.json', {'total_bytes': self.total,
             'completed_utc': datetime.now(timezone.utc).isoformat(), 'receipts': self.receipts})


def traverse_osf(collector, first):
    queue = [first]
    seen = set()
    items = []
    failures = []
    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        result = collector.get(url)
        if result is None:
            failures.append(url)
            continue
        rows = result.get('data', [])
        if isinstance(rows, dict):
            rows = [rows]
        for entry in rows:
            items.append(entry)
            rel = entry.get('relationships', {})
            for key in ('files', 'children'):
                related = rel.get(key, {}).get('links', {}).get('related', {})
                target = related.get('href') if isinstance(related, dict) else related
                if target:
                    queue.append(target)
        next_url = result.get('links', {}).get('next')
        if next_url:
            queue.append(next_url)
    return {'items': items, 'failure_urls': failures, 'visited': sorted(seen),
            'complete_inventory': not failures and bool(items)}


def primary():
    verify_implementation()
    c = Collector('osf')
    try:
        inventory = traverse_osf(c, 'https://api.osf.io/v2/nodes/vh5kq/')
        c.get('https://www.nature.com/articles/s41597-024-04265-1', 'document')
        if not inventory['complete_inventory']:
            c.get('https://osf.io/vh5kq/', 'document')
            c.get('https://doi.org/10.17605/OSF.IO/VH5KQ', 'document')
        save(c.folder / 'inventory.json', inventory)
    finally:
        c.finish()


def fallback():
    verify_implementation()
    if read(OUT / 'gate_result.json')['scientific_verdict'] == 'PASS':
        raise RuntimeError('Fallback not authorized after primary PASS')
    c = Collector('figshare')
    try:
        article = c.get('https://api.figshare.com/v2/articles/14905317')
        versions = c.get('https://api.figshare.com/v2/articles/14905317/versions')
        c.get('https://www.nature.com/articles/s41562-023-01706-6', 'document')
        save(c.folder / 'inventory.json', {'article': article, 'versions': versions,
             'files': article.get('files', []) if article else [], 'data_files_opened': 0})
    finally:
        c.finish()


def replay():
    verify_implementation()
    lock = read(OUT / 'artifact_lock.json')
    for name, digest in lock.items():
        assert sha(ROOT / name) == digest, name
    qc = read(OUT / 'QC.json')
    assert verdict(qc) == read(OUT / 'gate_result.json')['scientific_verdict']
    for name in ('osf', 'figshare'):
        p = OUT / name / 'receipts.json'
        if p.exists():
            for record in read(p)['receipts']:
                assert not record['data_file_download']
                assert permitted(record['url'], record['kind'])
                assert sha(p.parent / record['local']) == record['sha256']
    print('Saved metadata/hash/gate verification PASS; no network or neural access.')


if __name__ == '__main__':
    {'register': register_implementation, 'primary': primary, 'fallback': fallback,
     'replay': replay}[sys.argv[1]]()
