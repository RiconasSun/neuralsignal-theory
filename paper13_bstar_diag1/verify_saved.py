"""Final hash-bound saved evidence and bounded synthetic regression reproduction."""
import json
import socket
import unittest
from unittest.mock import patch
from .common import P, ROOT, E, read, sha, identities
from .audit_saved import audit


def main():
    freeze = read(P / 'FINAL_FREEZE.json')
    for name, digest in freeze['hashes'].items():
        assert sha(ROOT / name) == digest, name
    baseline = read(E / 'baseline.json')
    matrix = read(E / 'preservation_matrix.json')
    fields = ['id', 'phase', 'requirement']
    assert [[r[k] for k in fields] for r in baseline['requirements']] == [[r[k] for k in fields] for r in matrix['requirements']]
    assert len(matrix['requirements']) == len({r['id'] for r in matrix['requirements']}) == 39
    count = sum(r['status'] == 'VERIFIED' for r in matrix['requirements'])
    assert count == matrix['verified_pre_git_count']
    before = identities()
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Saved/synthetic reproduction forbids network')):
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('paper13_bstar_diag1.test_diagnostics'))
        if not result.wasSuccessful(): raise RuntimeError('Diagnostic synthetic regression failure')
        saved = audit()
    assert identities() == before
    assert saved == read(P / 'results/SAVED_AUDIT.json')
    print(json.dumps({'diagnosis': saved['diagnosis'], 'synthetic_tests': result.testsRun,
        'frozen_files': len(freeze['hashes']), 'verified_pre_git_requirements': count, 'baseline_requirement_count': 39,
        'new_diagnostic_replays': 0, 'new_real_fits': 0, 'final_C_fits': 0, 'final_D_access': False,
        'original_M6': 'FAIL_UNAVAILABLE', 'engineering_diagnostic_success_is_not_scientific_M6_PASS': True}))


if __name__ == '__main__': main()
