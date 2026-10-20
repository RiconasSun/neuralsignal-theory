"""Verify finite forensic archive payload; no scientific imports/computation."""
import json
from .audit import R, P, load, sha, require


def verify():
    archive = load(P/'ARCHIVE_MANIFEST.json')
    names = [r['path'] for r in archive['files']]
    require(len(names) == len(set(names)), 'Unique archive paths')
    for row in archive['files']:
        path = R/row['path']
        require(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'Forensic archive payload identity: '+row['path'])
    print(json.dumps({'archive_payload_integrity': 'PASS', 'files': len(names), 'self_referential_commit_claim': False}))


if __name__ == '__main__':verify()
