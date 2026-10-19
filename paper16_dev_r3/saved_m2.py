"""Saved M2 evidence replay only. Never acquires sources or fits/scorers models."""
import json
from unittest.mock import patch
import numpy as np
from .core import R, P, E, load, sha, array_id, qc_a, coverage, select_common
from .run_m2 import verify_preaccess, source_inputs


def verify():
    reg = verify_preaccess()
    freeze = load(P/'PREACCESS_FREEZE_3.json')
    for row in freeze['files']:
        path = R/row['path']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
    root = P/'results/sources'
    expected = {str(x['session_id']) for x in reg['objects']}
    assert all(x.is_dir() and x.name in expected for x in root.iterdir())
    complete, failures, captures = [], [], 0
    for item in reg['objects']:
        folder = root/str(item['session_id'])
        if not folder.exists(): continue
        assert load(folder/'ATTEMPT.json')['source'] == item
        _, flashes, running, _ = source_inputs(item)
        records = [json.loads(s) for s in (folder/'UNIT_QC.jsonl').read_text(encoding='utf8').splitlines()]
        assert [r['unit_id'] for r in records] == item['candidate_unit_ids'][:len(records)]
        for row in records:
            receipt = row['private_A_capture']; path = (R/receipt['private_path']).resolve()
            path.relative_to((P/'work/private/A'/str(item['session_id'])).resolve())
            assert sha(path) == receipt['sha256']
            with np.load(path, allow_pickle=False) as saved:
                arrays = {k: saved[k].copy() for k in saved.files}
            assert {k: array_id(a) for k, a in arrays.items()} == receipt['arrays']
            assert qc_a(arrays, flashes['start'], reg) == row['A_physiology']
            counts = coverage(np.asarray(row['observation_mask'], dtype=bool), flashes['color'])
            assert counts == row['source_coverage']
            assert all(v['pass'] for v in counts.values()) == row['individual_source_coverage_pass']
            captures += 1
        if (folder/'FAILURE.json').exists():
            assert not (folder/'RESULT.json').exists()
            failure = load(folder/'FAILURE.json')
            assert failure['no_retry'] and failure['no_later_source_or_fit_authorized']
            assert failure['completed_private_A_captures'] == len(list(folder.glob('A_CAPTURE_*.json')))
            failures.append(item['session_id'])
        else:
            result = load(folder/'RESULT.json')
            assert result['source_pass'] and result['A_QC_complete']
            assert len(records) == len(item['candidate_unit_ids']) == result['private_A_capture_count']
            assert sha(folder/'UNIT_QC.jsonl') == result['UNIT_QC_sha256']
            assert select_common(records, flashes['color'], running['missing'], reg) == result['selection']
            assert result['optimizer_attempts'] == result['running_acquisition_calls'] == 0
            assert result['A_only_export'] and not result['B_E_arrays_exported']
            assert not result['Final_C_access'] and not result['Final_D_access']
            complete.append(result)
    journal = [json.loads(s) for s in (P/'results/NEURAL_BUDGET.jsonl').read_text().splitlines()]
    by_source = {}; payload = 0
    for row in journal:
        if row['event'] == 'RESERVED':
            state = by_source.setdefault(row['session_id'], {'reserved': 0, 'requests': 0})
            assert row['request'] == state['requests']+1
            assert row['reserved_bytes'] == row['expected_bytes']+1
            state['requests'] += 1; state['reserved'] += row['reserved_bytes']
        elif row['event'] == 'PAYLOAD': payload += row['bytes']
    assert sum(v['reserved'] for v in by_source.values()) <= reg['resources']['aggregate_reserved_bytes_max']
    assert all(v['reserved'] <= reg['resources']['per_source_reserved_bytes_max'] for v in by_source.values())
    assert (P/'results/NEURAL_BUDGET.jsonl').read_bytes().startswith((P/'results/BUDGET_FIRST.jsonl').read_bytes())
    admitted = [x for x in complete if x['selection']['admitted']]
    bo = sum(x['source']['protocol'] == 'brain_observatory_1.1' for x in admitted)
    return {'saved_prefix_integrity_and_A_replay': True, 'complete_sources': len(complete), 'failed_sources': failures,
            'A_candidate_states_replayed': captures, 'admitted_mice_in_completed_prefix': len(admitted),
            'admitted_BO_in_prefix': bo, 'admitted_FC_in_prefix': len(admitted)-bo,
            'source_payload_bytes': payload, 'source_reserved_bytes': sum(v['reserved'] for v in by_source.values()),
            'original_sources': len(reg['objects']), 'whole_M2_pass_not_implied': True,
            'new_source_requests': 0, 'new_model_fits': 0, 'B_E_neural_access': False, 'Final_C_D_access': False}


if __name__ == '__main__':
    with patch('socket.socket.connect', side_effect=RuntimeError('Saved-only reproduction: network forbidden')):
        print(json.dumps(verify(), sort_keys=True, allow_nan=False))
