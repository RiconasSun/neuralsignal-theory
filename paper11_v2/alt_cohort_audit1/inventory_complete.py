"""Registered efficient metadata pagination after preserved 250-request stop."""
import sys
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from audit import Collector, verify_implementation
from register import OUT, ROOT, read, save, sha


def paged(url):
    p = urlsplit(url)
    query = dict(parse_qsl(p.query))
    query['page[size]'] = '100'
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), p.fragment))


def register():
    verify_implementation()
    initial = read(OUT / 'osf/receipts.json')
    assert len(initial['receipts']) == 250
    save(OUT / 'inventory_completion_registration.json', {
        'registered_utc': datetime.now(timezone.utc).isoformat(),
        'source_sha256': sha(__file__), 'initial_receipts_sha256': sha(OUT / 'osf/receipts.json'),
        'reason': 'Default ten-item pagination exhausted registered acquisition budget; preserve initial stop and re-inventory uniformly with100items/page',
        'additional_max_requests': 250, 'additional_max_bytes': 33554432,
        'all_scientific_and_access_thresholds_unchanged': True,
        'no_data_files': True, 'no_patient_selection': True,
        'observed_initial_attempt': '250 metadata requests; RuntimeError Request budget exhausted, exit1; no gate PASS',
        'Nature_document_retry': 'Public cookies_not_supported document URL; no login or access-control bypass'})


def acquire():
    verify_implementation()
    reg = read(OUT / 'inventory_completion_registration.json')
    assert sha(__file__) == reg['source_sha256']
    c = Collector('osf_complete')
    queue = ['https://api.osf.io/v2/nodes/vh5kq/']
    seen = set()
    items = {}
    failures = []
    try:
        while queue:
            url = paged(queue.pop(0))
            if url in seen:
                continue
            seen.add(url)
            data = c.get(url)
            if data is None:
                failures.append(url)
                continue
            rows = data.get('data', [])
            if isinstance(rows, dict):
                rows = [rows]
            for row in rows:
                items[(row['type'], row['id'])] = row
                for key in ('files', 'children'):
                    rel = row.get('relationships', {}).get(key, {}).get('links', {}).get('related', {})
                    target = rel.get('href') if isinstance(rel, dict) else rel
                    if target:
                        queue.append(target)
            if data.get('links', {}).get('next'):
                queue.append(data['links']['next'])
        for suffix in ['', '/tables/1', '/tables/2']:
            c.get('https://www.nature.com/articles/s41597-024-04265-1' + suffix + '?error=cookies_not_supported', 'document')
    except Exception as error:
        failures.append('EXECUTION:' + type(error).__name__)
        raise
    finally:
        save(c.folder / 'inventory.json', {'items': list(items.values()), 'failure_urls': failures,
             'remaining_queue': queue, 'visited': sorted(seen),
             'complete_inventory': not failures and not queue and bool(items),
             'uniform_all_folders_and_pages': True, 'data_files_opened': 0})
        c.finish()


if __name__ == '__main__':
    {'register': register, 'acquire': acquire}[sys.argv[1]]()
