"""Reproduce archived stop evidence, never resume the stopped experiment."""
import json
import socket
import unittest
import zipfile
import copy
from collections import Counter
from unittest.mock import patch
from .source import P, ROOT, sha
from . import baseline_A as b
from . import development_bundle as bundles
from . import restore_saved_states as restore
from . import controls_E
from .audit_M6_stop import audit


def check_matrix(matrix, baseline):
    fields = ('id', 'phase', 'requirement')
    rows = matrix['requirements']
    assert [tuple(r[k] for k in fields) for r in rows] == [tuple(r[k] for k in fields) for r in baseline['requirements']]
    assert len(rows) == len({r['id'] for r in rows}) == matrix['count'] == matrix['original_count'] == 86
    counts = Counter(r['status'] for r in rows)
    assert set(counts) <= {'VERIFIED', 'BLOCKED_HUMAN_INPUT'}
    assert matrix['verified_baseline_count'] == counts['VERIFIED']
    assert matrix['blocked_human_input_count'] == counts['BLOCKED_HUMAN_INPUT']
    assert sum(counts.values()) == 86 and matrix['full_mission_PASS'] is False


def main():
    freeze = b.read(P / 'NUMERICAL_STOP_FREEZE.json')
    for name, digest in freeze['hashes'].items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    original = b.read(ROOT / 'paper13_ki_pl_contract1/FREEZE_r2.json')
    for manifest in [b.read(P / 'M6_E_IMPLEMENTATION_FREEZE_r2.json'), original]:
        for name, digest in manifest['hashes'].items():
            assert sha((ROOT / name).read_bytes()) == digest, name
    evidence = ROOT / 'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution'
    matrix = b.read(evidence / 'preservation_matrix_stop.json')
    baseline = b.read(evidence / 'baseline.json')
    check_matrix(matrix, baseline)
    for key in ['verified_baseline_count', 'blocked_human_input_count']:
        corrupted = copy.deepcopy(matrix)
        corrupted[key] += 1
        try:
            check_matrix(corrupted, baseline)
        except AssertionError:
            pass
        else:
            raise AssertionError('Corrupted matrix aggregate was accepted: ' + key)
    historical = {}
    for name in ['M6_E_r1_failed_code_package.zip', 'NUMERICAL_STOP_HISTORICAL_BYTES.zip']:
        with zipfile.ZipFile(evidence / name) as archive:
            for member in archive.namelist():
                historical[(member, sha(archive.read(member)))] = archive.read(member)
    for path in [P / 'SAVED_PROGRESS_FREEZE.json', evidence / 'CHECKPOINT_CANDIDATE_r2.json', P / 'M6_E_IMPLEMENTATION_FREEZE.json']:
        for name, digest in b.read(path)['hashes'].items():
            if sha((ROOT / name).read_bytes()) != digest:
                assert (name, digest) in historical, name
                if name == 'ops/daily-operations.md':
                    assert (ROOT / name).read_bytes().endswith(historical[(name, digest)])
    names = ['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A','test_development_B',
        'test_families','test_animal_stats','test_predictive','test_development_bundle','test_exploratory_E',
        'test_control_core','test_sensitivity_plan','test_restore_saved','test_controls_E','test_final_C','test_sensitivity_scores']
    before = sha((P / 'results/source_access.jsonl').read_bytes())
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Saved-only stop reproduction denies network')):
        restored = restore.restore(ROOT, b.read(evidence / 'SAVED_DERIVED_STATES_MANIFEST.json'))
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.' + name for name in names]))
        assert result.wasSuccessful() and result.testsRun == 127
        _, _, baselines, _, families, _ = bundles.gates()
        _, data = controls_E.inputs()
        assert len(baselines) == 390 and len(families) == 540 and len(data) == 10
        report = audit()
    assert before == sha((P / 'results/source_access.jsonl').read_bytes()) == report['access_log_sha256']
    assert report == json.loads((ROOT / 'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution/M6_STOP_SAVED_AUDIT.json').read_text(encoding='utf-8-sig'))
    print(json.dumps({'saved_stop_audit': 'MATCH', 'unique_synthetic_tests': result.testsRun,
        'saved_fit_certificates_verified': len(baselines) + len(families),
        'original_saved_states': restored['verified_original_saved_states'],
        'matrix_verified_rows': matrix['verified_baseline_count'], 'matrix_blocked_rows': matrix['blocked_human_input_count'],
        'matrix_corrupted_aggregate_denial_checks': 2,
        'stop_freeze_hashes': len(freeze['hashes']), 'scientific_status': 'STOP_NUMERICAL_NOT_FINAL_VALIDATION',
        'new_draws': 0, 'new_real_fits': 0, 'new_source_requests': 0, 'D_assessment': False}))


if __name__ == '__main__':
    main()
