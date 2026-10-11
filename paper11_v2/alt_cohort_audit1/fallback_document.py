"""Versioned next-candidate metadata confirmation, no archive access."""
import sys
from datetime import datetime, timezone
from audit import Collector, verify_implementation
from register import OUT, read, save, sha


def register():
    assert read(OUT / 'gate_result.json')['scientific_verdict'] == 'INCONCLUSIVE'
    save(OUT / 'fallback_document_plan.json', {
        'utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': sha(__file__),
        'candidate_version': '14905317.v1', 'no_archive_access': True,
        'requests': ['https://api.figshare.com/v2/articles/14905317/versions/1',
                     'https://www.nature.com/articles/s41562-023-01706-6?error=cookies_not_supported']})


def acquire():
    verify_implementation()
    plan = read(OUT / 'fallback_document_plan.json')
    assert sha(__file__) == plan['source_sha256']
    c = Collector('figshare_document')
    try:
        c.get(plan['requests'][0])
        c.get(plan['requests'][1], 'document')
    finally:
        c.finish()


if __name__ == '__main__':
    {'register': register, 'acquire': acquire}[sys.argv[1]]()
