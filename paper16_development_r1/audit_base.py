"""Saved-identity audit only; no neural decoding, source access or optimization."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_development_r1'
E = R / 'ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r1'
BASE = 'ed2b52f5ba7a21ed870911e135c194c253b473ab'


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def verify_rows(rows, allow_daily_snapshot=False):
    for row in rows:
        path = R / row['path']
        if row['path'] == 'ops/daily-operations.md' and allow_daily_snapshot:
            path = E / 'R4_BASE_DAILY_SNAPSHOT.bin'
            assert (R / row['path']).read_bytes().endswith(path.read_bytes())
        assert path.stat().st_size == row['bytes'], row['path']
        assert sha(path) == row['sha256'], row['path']
    return len(rows)


def verify():
    bootstrap = load(E / 'BOOTSTRAP.json')
    assert bootstrap['BASE'] == bootstrap['HEAD'] == bootstrap['origin_test'] == BASE
    assert bootstrap['initial_worktree_clean'] and bootstrap['fetch_verified']
    assert sha(E / 'OWNER_REQUEST.txt') == bootstrap['owner_request_sha256']
    assert len(bootstrap['normative_frozen_files']) == 13
    normative = verify_rows(bootstrap['normative_frozen_files'])
    m1 = load(R / 'paper16_m1/M1_FREEZE_MANIFEST.json')
    assert len(m1['files']) == m1['expected_payload_count'] == 334
    m1_count = verify_rows(m1['files'])
    receipt_path = R / 'paper16_source_r4/work/FINAL_HANDOFF_RECEIPT.json'
    assert sha(receipt_path) == '52cbf3eef9946661819491616ff800c149fd49c4e64e8d4c6f86578c1003aab4'
    receipt = load(receipt_path)
    assert receipt['final_status'] == 'PASS' and receipt['commit'] == BASE
    assert receipt['normal_push'] and not receipt['force_push']
    assert len(receipt['changed_file_manifest']) == receipt['changed_file_count'] == 2012
    changed = verify_rows(receipt['changed_file_manifest'], True)
    manifest_path = R / 'paper16_source_r4/FINAL_FREEZE_MANIFEST.json'
    assert sha(manifest_path) == '99159812e89b5322701546b5f2196e7d8cee02d8a6e66318955022bcd3f71e01'
    r4 = load(manifest_path)
    assert (r4['all_original_sources_complete'], r4['admitted_mice'], r4['BO'], r4['FC'],
            r4['retained_A_states']) == (28, 27, 5, 22, 1983)
    frozen = verify_rows(r4['files'], True)
    result = {
        'mission': 'P16-M3-M5-FROZEN-DEVELOPMENT-R1', 'BASE': BASE,
        'verified_at_UTC': datetime.now(timezone.utc).isoformat(),
        'normative_file_count': normative, 'M1_payloads_verified': m1_count,
        'R4_changed_file_identities_verified': changed, 'R4_manifest_entries_verified': frozen,
        'R4_postcommit_receipt_sha256': sha(receipt_path),
        'R4_final_archive_PASS_verified': True,
        'initial_worktree_clean': True, 'origin_main': bootstrap['origin_main'],
        'new_neural_decoding': False, 'new_source_requests': 0, 'new_model_fits': 0,
        'B_access': False, 'E_access': False, 'Final_C_access': False, 'Final_D_access': False,
        'R4_saved_only_reproduction': 'Separate native PowerShell receipt required',
        'complete': True,
    }
    return result


if __name__ == '__main__':
    output = P / 'BASE_AND_FREEZE_AUDIT.json'
    result = verify()
    with output.open('x', encoding='utf8', newline='\n') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result))
