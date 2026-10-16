"""Saved evidence only: validate the stopped E controls without generating draws."""
import json
from collections import Counter
import numpy as np
from .source import P, ROOT, sha
from . import baseline_A as b

E = ROOT / 'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution'


def audit():
    root = P / 'results/m6_controls_E'
    gate = b.read(P / 'results/M6_E_CONTROLS_GATE.json')
    expected = {'suite': 'conditional_Bstar', 'replicate': 0, 'mouse_id': '156130'}
    assert gate['M6_E_CONTROLS'] == 'FAIL' and gate['attempt'] == expected
    assert gate['error_type'] == 'FloatingPointError' and gate['error'] == 'overflow encountered in exp'
    assert gate['retry_or_new_random_draw_authorized'] is False
    assert gate['final_C_model_fits'] == 0 and gate['final_D_outcomes_accessed'] is False
    rows = [json.loads(line) for line in (root / 'actions.jsonl').read_text(encoding='utf8').splitlines()]
    assert rows[0]['event'] == 'CONTROL_EXECUTION_START'
    assert rows[-1]['event'] == 'CONTROL_EXECUTION_ERROR'
    assert len([r for r in rows if r['event'] == 'CONTROL_EXECUTION_START']) == 1
    assert len([r for r in rows if r['event'] == 'CONTROL_EXECUTION_ERROR']) == 1
    assert not any(r['event'] == 'CONTROL_EXECUTION_COMPLETE' for r in rows)
    mice = b.read(P / 'results/M5_EXPLORATORY_RESULTS.json')['mouse_order']
    assert mice == sorted(mice) and len(mice) == 10
    suites = ['temporal', 'history', 'task_order', 'conditional_Bstar']
    starts = Counter(r['suite'] for r in rows if r['event'] == 'REPLICATE_START')
    completed = Counter(r['suite'] for r in rows if r['event'] == 'REPLICATE_COMPLETE')
    mouse_complete = Counter(r['suite'] for r in rows if r['event'] == 'MOUSE_CONTROL_COMPLETE')
    evidence = {}
    for suite in suites:
        array = np.load(root / (suite + '.npy'), allow_pickle=False, mmap_mode='r')
        assert array.shape == (999, 10, 9) and array.dtype == np.float64
        successes = [r for r in rows if r['event'] == 'MOUSE_CONTROL_COMPLETE' and r['suite'] == suite]
        expected_pairs = [(rep, mouse) for rep in range(999) for mouse in mice] if suite != 'conditional_Bstar' else [(0, m) for m in mice[:3]]
        assert [(r['replicate'], r['mouse_id']) for r in successes] == expected_pairs
        valid = np.isfinite(array).all(axis=2)
        assert int(valid.sum()) == len(successes)
        for index, (rep, mouse) in enumerate(expected_pairs):
            assert valid[rep, mice.index(mouse)] and successes[index]['nominal_unit_bins'] == 6000
        assert np.isnan(array[~valid]).all()
        full = suite != 'conditional_Bstar'
        assert starts[suite] == (999 if full else 1)
        assert completed[suite] == (999 if full else 0)
        assert mouse_complete[suite] == (9990 if full else 3)
        markers = [r for r in rows if r['event'] == 'SUITE_COMPLETE' and r['suite'] == suite]
        assert len(markers) == int(full)
        digest = sha((root / (suite + '.npy')).read_bytes())
        if full:
            assert markers[0]['artifact_sha256'] == digest
        evidence[suite] = {'started_replicates': starts[suite], 'completed_replicates': completed[suite],
            'completed_mouse_replicates': mouse_complete[suite], 'sha256': digest,
            'partial_nan_rows_preserved': int((~valid).sum()), 'full_suite_complete': full}
    assert sum(mouse_complete.values()) == 29973
    assert sum(starts.values()) == 2998 and sum(completed.values()) == 2997
    assert not (root / 'equal_mouse_distributions.npz').exists()
    assert b.read(E / 'M6_E_native_exit.json')['exit_code'] == 1
    trace = (E / 'M6_E_native_execution.txt').read_text(encoding='utf8')
    assert 'conditional_counts' in trace and 'FloatingPointError: overflow encountered in exp' in trace
    freeze = P / 'M6_E_IMPLEMENTATION_FREEZE_r2.json'
    assert sha(freeze.read_bytes()) == gate['source_freeze']
    for name, digest in b.read(freeze)['hashes'].items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    for name in ['FINAL_C_APPROVAL.json', 'FINAL_D_APPROVAL.json', 'results/FINAL_C_GATE.json',
                 'results/FINAL_D_RESULTS.json', 'results/FINAL_C_FULL_STATE_MANIFEST.json']:
        assert not (P / name).exists(), name
    assert not (P / 'results/final_C').exists() and not (P / 'results/final_D').exists()
    original = b.read(ROOT / 'paper13_ki_pl_contract1/FREEZE_r2.json')
    for name, digest in original['hashes'].items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    return {'scope': 'SAVED_EVIDENCE_ONLY_NO_NEW_DRAWS_FITS_OR_SOURCE_IO', 'M6_E_CONTROLS': 'FAIL',
        'failure': gate, 'suites': evidence, 'started_replicates': 2998, 'completed_replicates': 2997,
        'completed_mouse_replicates': 29973, 'attempted_mouse_replicates': 29974,
        'planned_mouse_replicates': 39960, 'unattempted_mouse_replicates': 9986,
        'new_real_C_model_fits': 0, 'D_neural_outcomes_exported': False, 'D_assessment_executed': False,
        'original_hashes_verified': len(original['hashes']), 'control_freeze_hashes_verified': len(b.read(freeze)['hashes']),
        'scientific_null_p_values': 'NOT_COMPUTED_INCOMPLETE_REQUIRED_FOUR_SUITE_BUNDLE',
        'access_log_sha256': sha((P / 'results/source_access.jsonl').read_bytes()),
        'stop': 'Required numerical failure; coverage-only owner amendment cannot authorize continuation'}


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
