"""Executable public-only audit reproduction, never a C fit or second D evaluation."""
import json
import unittest
from audit import build
from register_audit import HERE, ROOT, load, sha


def main():
    reg = load(HERE / 'registration.json')
    if sha(HERE / 'preservation_manifest.json') != reg['preservation_manifest_sha256']:
        raise RuntimeError('PRESERVATION_MANIFEST_CHANGED')
    preserved = load(HERE / 'preservation_manifest.json')['tracked_working_bytes_sha256']
    archive = HERE / 'historical_daily_operations.bin'
    for name, digest in preserved.items():
        if name == 'ops/daily-operations.md':
            if sha(archive) != digest or not (ROOT / name).read_bytes().endswith(archive.read_bytes()):
                raise RuntimeError('DAILY_HISTORY_CHANGED')
        elif sha(ROOT / name) != digest:
            raise RuntimeError('HISTORICAL_BYTES_CHANGED:' + name)
    seal = HERE / 'seal.json'
    if not seal.exists():
        raise RuntimeError('FINAL_AUDIT_SEAL_REQUIRED')
    for name, digest in load(seal)['sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('AUDIT_FILE_CHANGED:' + name)
    result = build()
    if result != load(HERE / 'pre_release_audit.json'):
        raise RuntimeError('AUDIT_REBUILD_MISMATCH')
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_audit.py')
    tests = unittest.TestResult()
    suite.run(tests)
    if tests.testsRun != 7 or not tests.wasSuccessful() or tests.skipped:
        raise RuntimeError(str({'tests': tests.testsRun, 'failures': tests.failures, 'errors': tests.errors}))
    print(json.dumps({'saved_integrity': 'PASS', 'executable_public_audit': 'PASS', 'tests': tests.testsRun,
                      'preserved_files': len(preserved), 'scientific_validation': 'NOT_EXECUTED',
                      'C_fits': 0, 'D_assessments': 0, 'protected_payload_reads': 0,
                      'release_allowed': result['release_allowed']}))


if __name__ == '__main__':
    main()
