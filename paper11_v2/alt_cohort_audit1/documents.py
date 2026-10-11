"""Prospectively locked standalone README/license/descriptor acquisition."""
import json
import sys
from datetime import datetime, timezone
from urllib.parse import urlsplit

from audit import Collector, verify_implementation
from register import HERE, OUT, ROOT, read, save, sha


def candidates():
    entries = {}
    for file in sorted((OUT / 'osf').glob('*.receipt')):
        try:
            data = read(file).get('data', [])
        except (ValueError, UnicodeError):
            continue
        if isinstance(data, dict):
            data = [data]
        for item in data:
            attrs = item.get('attributes', {})
            if attrs.get('kind') == 'file' and attrs.get('name', '').lower() == 'readme.rtf':
                entries[item['id']] = item
    return list(entries.values())


def register_documents():
    verify_implementation()
    docs = candidates()
    if len(docs) != 3 or any(x['attributes']['size'] > 4096 for x in docs):
        raise RuntimeError('Unexpected standalone README scope')
    save(OUT / 'document_access_plan.json', {
        'registered_utc': datetime.now(timezone.utc).isoformat(),
        'source_sha256': {__file__.replace('\\', '/').split('/neuralsignal institute/')[-1]: sha(__file__)},
        'readmes': docs, 'exact_names': ['readMe.rtf'], 'max_document_bytes': 4096,
        'allowed_redirect_hosts': ['osf.io', 'files.osf.io', 'storage.googleapis.com'],
        'never_log_signed_redirect_queries': True,
        'additional_metadata': ['OSF license', 'Nature patient/session and anatomy tables'],
        'raw_data_or_archives': 'FORBIDDEN; standalone README only, not event/unit values',
        'scientific_rules_unchanged': True})


def acquire():
    import requests
    verify_implementation()
    plan = read(OUT / 'document_access_plan.json')
    assert sha(__file__) == next(iter(plan['source_sha256'].values()))
    c = Collector('documents')
    doc_receipts = []
    try:
        c.get('https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96c/')
        c.get('https://www.nature.com/articles/s41597-024-04265-1/tables/1', 'document')
        c.get('https://www.nature.com/articles/s41597-024-04265-1/tables/2', 'document')
        for i, item in enumerate(plan['readmes']):
            attrs = item['attributes']
            target = f"https://files.osf.io/v1/resources/vh5kq/providers/osfstorage/{item['id']}?action=download&version={attrs['current_version']}"
            receipt = {'id': item['id'], 'path': attrs['materialized_path'],
                       'version': attrs['current_version'], 'started_utc': datetime.now(timezone.utc).isoformat(),
                       'provider_sha256': attrs['extra']['hashes']['sha256'],
                       'standalone_document': True, 'neural_or_outcome_values': False, 'redirect_hosts': []}
            try:
                for _ in range(5):
                    parts = urlsplit(target)
                    if parts.scheme != 'https' or parts.hostname not in plan['allowed_redirect_hosts']:
                        raise RuntimeError('Nonallowlisted document redirect')
                    receipt['redirect_hosts'].append(parts.hostname)
                    with requests.get(target, stream=True, timeout=45, allow_redirects=False) as r:
                        receipt['status'] = r.status_code
                        if r.status_code in (301, 302, 303, 307, 308):
                            target = r.headers['Location']
                            continue
                        r.raise_for_status()
                        payload = bytearray()
                        for chunk in r.iter_content(1024):
                            if len(payload) + len(chunk) > plan['max_document_bytes']:
                                raise RuntimeError('Standalone document size exceeded')
                            payload.extend(chunk)
                        if len(payload) != attrs['size'] or not bytes(payload).startswith(b'{\\rtf'):
                            raise RuntimeError('README not expected RTF bytes')
                        local = f'readme_{i}.rtf'
                        (c.folder / local).write_bytes(payload)
                        receipt.update(local=local, bytes=len(payload), sha256=sha(c.folder/local))
                        if receipt['sha256'] != receipt['provider_sha256']:
                            raise RuntimeError('Provider document checksum mismatch')
                        receipt['verified'] = True
                        break
                else:
                    raise RuntimeError('Redirect limit exceeded')
            except Exception as e:
                receipt.update(error=type(e).__name__, verified=False)
            doc_receipts.append(receipt)
    finally:
        save(c.folder / 'standalone_document_receipts.json', doc_receipts)
        c.finish()


if __name__ == '__main__':
    {'register': register_documents, 'acquire': acquire}[sys.argv[1]]()
