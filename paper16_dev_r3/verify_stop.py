"""Read-only scientific-stop audit; cannot authorize another source or optimizer."""
import json
import platform
from importlib.metadata import version
from unittest.mock import patch
from .core import R, P, E, load, sha
from .saved_m2 import verify


def verify_stop(require_freeze=True):
    policy = load(R/'paper16_m1/NUMERICAL_POLICY.json')['software']
    runtime = {'Python': platform.python_version(), **{n: version(n) for n in ['numpy', 'scipy', 'h5py', 'requests']}}
    assert runtime == policy, 'Use original pinned scientific runtime; no silent dependency substitution'
    replay = verify()
    account = load(P/'SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')
    resources = load(P/'RESOURCE_LEDGER.json')
    fields = load(P/'TERMINAL_FIELDS.json')
    assert replay['complete_sources'] == account['complete_sources'] == 3
    assert replay['failed_sources'] == [763673393]
    assert account['attempted_sources'] == 4 and account['unattempted_sources'] == 24
    assert replay['A_candidate_states_replayed'] == account['completed_A_candidate_states'] == 228
    assert not account['global_admission_pass']
    assert [x['session_id'] for x in account['complete_prefix_admitted']] == [750749662, 757216464, 760345702]
    assert replay['source_payload_bytes'] == resources['source_payload_bytes'] == 236470272
    assert replay['source_reserved_bytes'] == resources['source_reserved_bytes'] == 236978402
    assert resources['source_requests'] == 226 and resources['events']['RANGE_FAILED'] == 1
    assert resources['fit_attempts'] == resources['running_acquisition_calls'] == resources['network_retries'] == 0
    assert not resources['wall_budget_exhausted'] and not resources['source_budget_exhausted']
    assert not (P/'results/WORKER_remaining.json').exists()
    assert not (P/'results/M2_COHORT.json').exists()
    supervision = load(P/'results/SUPERVISION_remaining.json')
    assert supervision['returncode'] == 1 and not supervision['valid_completed_worker']
    assert supervision['native_job_tree_enforced'] and supervision['assigned_before_resume']
    assert not supervision['killed_at_deadline'] and supervision['clock_failure'] is None
    failure = load(P/'results/sources/763673393/FAILURE.json')
    assert failure['error_type'] == 'ReadTimeoutError' and failure['source_requests_new'] == 28
    assert failure['completed_private_A_captures'] == 19 and failure['no_retry']
    inventory = load(P/'PRIVATE_STOP_INVENTORY.json')
    assert inventory['file_count'] == len(inventory['files']) == 679
    names = set(); range_bytes = 0; incomplete = []
    for row in inventory['files']:
        path = (R/row['path']).resolve()
        assert any(path.is_relative_to((P/'work/private'/n).resolve()) for n in ['A', 'ranges'])
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
        assert row['path'] not in names; names.add(row['path'])
        if path.suffix == '.bin':
            range_bytes += row['bytes']
            if not row['complete_cache_receipt_present']: incomplete.append(row)
    actual = {x.relative_to(R).as_posix() for n in ['A', 'ranges'] for x in (P/'work/private'/n).rglob('*') if x.is_file()}
    assert actual == names and range_bytes == resources['source_payload_bytes']
    assert len(incomplete) == 1 and incomplete[0]['bytes'] == 540672
    assert incomplete[0]['sha256'] == 'eeff268eac3c0857dc2e96e5fd8bade7cd65e1b7cf1f2a56a77a5abeabd536c6'
    assert fields['FINAL_STATUS'] == 'NEED_ENV' and fields['SCIENTIFIC_VERDICT'] == 'STOP_SOURCE / DEVELOPMENT_NOT_EVALUATED'
    assert fields['DEVELOPMENT_ATTEMPTS_USED'] == fields['DEVELOPMENT_ATTEMPTS_AUTHORIZED'] == 0
    assert fields['FROZEN_LAMBDA'] is None and fields['PRIMARY_DEVELOPMENT_EFFECT'] is None
    for name in ['M2_NEURAL_SOURCE_PASS', 'M2_PHYSIOLOGICAL_QC_PASS', 'M3_PRODUCTION_NUMERICAL_PASS',
                 'M4_B1_SELECTION_COMPLETE', 'M4_MODEL_FITTING_COMPLETE', 'M5_E_ASSESSMENT_COMPLETE',
                 'FINAL_C_ACCESS', 'FINAL_D_ACCESS', 'PROMPT_4_READY']:
        assert fields[name] is False, name
    optimizer = load(P/'OPTIMIZER_LEDGER.json')
    assert optimizer['attempts'] == [] and optimizer['attempts_used'] == 0
    stages = load(P/'UNEXECUTED_SCIENTIFIC_STAGES.json')
    assert len(stages['sensitivities']) == 12 and len(stages['controls']) == 4
    assert set(stages['sensitivities'].values()) == set(stages['controls'].values()) == {'NOT_EXECUTED_SOURCE_STOP'}
    assert not stages['M3']['certified'] and stages['M4']['A_fits'] == stages['M4']['B_score_access'] == stages['M5']['E_assessments'] == 0
    manifest = P/'STOP_FREEZE_MANIFEST.json'
    if require_freeze and not manifest.exists(): raise FileNotFoundError('Final stop manifest required; no archive verification')
    count = 0
    if manifest.exists():
        rows = load(manifest)['files']
        for row in rows:
            path = (R/row['path']).resolve(); path.relative_to(R)
            assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
        count = len(rows)
    return {**replay, 'full_private_stop_inventory_verified': 679, 'source_stop_account_verified': True,
            'verified_runtime': runtime,
            'frozen_stop_payloads_verified': count, 'saved_stop_freeze_verified': count > 0,
            'FINAL_STATUS': 'NEED_ENV', 'SCIENTIFIC_VERDICT': fields['SCIENTIFIC_VERDICT'],
            'M2_complete': False, 'M3_M5_executed': False, 'Final_C_D_access': False}


if __name__ == '__main__':
    with patch('socket.socket.connect', side_effect=RuntimeError('Saved-only audit: network forbidden')):
        print(json.dumps(verify_stop(), sort_keys=True, allow_nan=False))
