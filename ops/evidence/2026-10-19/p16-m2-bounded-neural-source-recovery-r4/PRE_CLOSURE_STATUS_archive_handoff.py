"""Exact-file archive checks; no neural acquisition or model execution."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_source_r4'
E = R / 'ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4'
BASE = 'd60e913c528feecfaaab9397ba1a6157c511526d'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=R)


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(body):
    return hashlib.sha256(body).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf8', newline='\n') as out:
        json.dump(value, out, indent=2, allow_nan=False)
        out.write('\n')


def approval():
    value = load(E / 'FINAL_APPROVAL.json')
    assert value['decision'] == 'ACCEPTED_R4_M2_SOURCE_HANDOFF'
    assert value['open_P0'] == value['open_P1'] == 0
    assert sha((E / 'review.md').read_bytes()) == value['report_sha256']
    assert sha((P / 'FINAL_FREEZE_MANIFEST.json').read_bytes()) == value['manifest_sha256']
    for name, digest in value['reviewed_closure_hashes'].items():
        assert sha((R / name).read_bytes()) == digest, name
    for row in load(P / 'FINAL_FREEZE_MANIFEST.json')['files']:
        body = (R / row['path']).read_bytes()
        assert len(body) == row['bytes'] and sha(body) == row['sha256'], row['path']
    return value


def plan():
    value = approval()
    assert git('branch', '--show-current').strip() == b'test'
    assert git('rev-parse', 'HEAD').strip().decode() == BASE
    assert git('rev-parse', 'origin/test').strip().decode() == BASE
    assert not git('diff', '--cached', '--name-only').strip()
    assert git('diff', '--name-only').decode().splitlines() == ['ops/daily-operations.md']
    assert (R / 'ops/daily-operations.md').read_bytes().endswith(git('show', BASE + ':ops/daily-operations.md'))
    unknown = [s.decode() for s in git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if s]
    assert all(s.startswith(('paper16_source_r4/', E.relative_to(R).as_posix() + '/')) for s in unknown)
    names = sorted(unknown + ['ops/daily-operations.md'])
    covered = {row['path'] for row in load(P / 'FINAL_FREEZE_MANIFEST.json')['files']}
    covered.update(value['reviewed_closure_hashes'])
    covered.update(value['closure_files'])
    assert set(names) <= covered, sorted(set(names) - covered)
    assert not any('/work/' in s or s.endswith(('.npz', '.npy', '.h5', '.nwb')) for s in names)
    assert all(not s.endswith('.bin') or s == E.relative_to(R).as_posix() + '/R3_DAILY_FROZEN_SNAPSHOT.bin' for s in names)
    files = [{'path': name, 'bytes': (R / name).stat().st_size, 'sha256': sha((R / name).read_bytes())} for name in names]
    (P / 'work/stage-paths.nul').write_bytes(b'\0'.join(s.encode() for s in names) + b'\0')
    write(P / 'work/STAGING_PLAN.json', {'base': BASE, 'files': files, 'approval_sha256': sha((E / 'FINAL_APPROVAL.json').read_bytes())})
    print(json.dumps({'exact_stage_files': len(files), 'raw_neural_staged': False}))


def batch(ref, names):
    data = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=R,
                                   input=('\n'.join(ref + ':' + name for name in names) + '\n').encode())
    pos = 0
    result = []
    for name in names:
        end = data.index(b'\n', pos)
        header = data[pos:end].split()
        pos = end + 1
        assert len(header) == 3 and header[1] == b'blob', name
        size = int(header[2])
        body = data[pos:pos + size]
        pos += size
        assert data[pos:pos + 1] == b'\n'
        pos += 1
        result.append((header[0].decode(), body))
    assert pos == len(data)
    return result


def staged():
    approval()
    plan_value = load(P / 'work/STAGING_PLAN.json')
    names = [row['path'] for row in plan_value['files']]
    actual = [s.decode() for s in git('diff', '--cached', '--name-only', '-z').split(b'\0') if s]
    assert set(actual) == set(names) and len(actual) == len(names)
    assert not git('diff', '--name-only').strip()
    assert not git('ls-files', '--others', '--exclude-standard', '-z')
    assert not git('diff', '--cached', '--diff-filter=D', '--name-only')
    for row, (blob, body) in zip(plan_value['files'], batch('', names)):
        assert body == (R / row['path']).read_bytes()
        assert len(body) == row['bytes'] and sha(body) == row['sha256']
        row['staged_git_blob'] = blob
    write(P / 'work/STAGED_VERIFICATION.json', {'files': plan_value['files'], 'index_equals_reviewed_tree': True, 'unrelated_files': 0})
    print(json.dumps({'staged_byte_verified': len(names), 'unrelated_files': 0}))


def finish():
    value = approval()
    plan_value = load(P / 'work/STAGING_PLAN.json')
    staged_value = load(P / 'work/STAGED_VERIFICATION.json')
    commit = git('rev-parse', 'HEAD').strip().decode()
    assert git('rev-parse', commit + '^').strip().decode() == BASE
    assert git('rev-parse', 'origin/test').strip().decode() == commit
    remote = git('ls-remote', '--heads', 'origin', 'refs/heads/test').decode().strip()
    assert remote.split()[0] == commit
    assert not git('ls-remote', '--heads', 'origin', 'refs/heads/main').strip()
    names = [row['path'] for row in plan_value['files']]
    changed = [s.decode() for s in git('diff', '--name-only', '-z', BASE, commit).split(b'\0') if s]
    assert set(changed) == set(names) and len(changed) == len(names)
    assert not git('diff', '--diff-filter=D', '--name-only', BASE, commit)
    assert not git('status', '--porcelain=v1', '--untracked-files=all')
    rows = []
    for row, staged_row, (blob, body) in zip(plan_value['files'], staged_value['files'], batch('origin/test', names)):
        assert row['path'] == staged_row['path']
        assert body == (R / row['path']).read_bytes()
        assert len(body) == row['bytes'] and sha(body) == row['sha256']
        assert blob == staged_row['staged_git_blob']
        rows.append({**row, 'remote_git_blob': blob, 'remote_sha256': sha(body), 'byte_readback_match': True})
    fields = load(P / 'TERMINAL_FIELDS.json')
    fields.update({'GIT_COMMIT': commit, 'REMOTE_VERIFICATION': 'VERIFIED_ORIGIN_TEST_ALL_CHANGED_BLOBS_AND_CLEAN_TREE',
                   'INDEPENDENT_REVIEW': value['decision'], 'SAVED_REPRODUCTION': 'POSTFREEZE_NATIVE_POWERSHELL_SAVED_ONLY_PASS'})
    requirements = load(E / 'REQUIREMENT_RESULTS.json')
    for row in requirements['items']:
        if row['status'] == 'PENDING_ARCHIVE':
            row.update({'status': 'VERIFIED', 'actual_closure_proof': 'Reviewed exact normal commit/push, full remote blob readback and clean tree'})
    verified = sum(row['status'] == 'VERIFIED' for row in requirements['items'])
    if fields['FINAL_STATUS'] == 'PASS':
        assert verified == 120 and fields['BUG_COUNT'] == fields['WARN_COUNT'] == 0
        assert fields['M2_SCIENTIFIC_GATE'] == 'M2_SOURCE_AND_PHYSIOLOGY_PASS'
    receipt = {'mission': fields['MISSION_ID'], 'base': BASE, 'commit': commit, 'branch': 'test',
               'verified_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'origin_test': remote,
               'origin_main': 'ABSENT_VERIFIED_NOT_INVENTED', 'normal_push': True, 'force_push': False,
               'changed_file_count': len(rows), 'changed_file_manifest': rows,
               'final_manifest_sha256': value['manifest_sha256'], 'final_review_sha256': value['report_sha256'],
               'terminal_fields': fields, 'baseline_requirement_count': 120, 'verified_baseline_count': verified,
               'requirement_trace': requirements['items'], 'clean_before_receipt': True, 'clean_after_receipt': True,
               'model_fits': 0, 'B_E_neural_scientific_access': False, 'Final_C_access': False, 'Final_D_access': False,
               'next_mission_started': False}
    write(P / 'work/FINAL_HANDOFF_RECEIPT.json', receipt)
    assert not git('status', '--porcelain=v1', '--untracked-files=all')
    print(json.dumps({'commit': commit, 'remote_changed_blobs_verified': len(rows), 'clean': True,
                      'verified_baseline_count': verified, 'handoff_receipt_sha256': sha((P / 'work/FINAL_HANDOFF_RECEIPT.json').read_bytes())}))


if __name__ == '__main__':
    {'plan': plan, 'staged': staged, 'finish': finish}[sys.argv[1]]()
