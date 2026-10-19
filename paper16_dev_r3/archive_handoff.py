"""Exact-file Git evidence helper for the reviewed NEED_ENV source-stop archive."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

R = Path(__file__).resolve().parents[1]
P = R/'paper16_dev_r3'
E = R/'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3'
BASE = '8801b945004cda0dd7ecd9ddde1daaa507414a96'


def git(*args): return subprocess.check_output(['git', *args], cwd=R)
def read(path): return json.loads(path.read_text(encoding='utf8'))
def digest(body): return hashlib.sha256(body).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf8', newline='\n') as out:
        json.dump(value, out, indent=2, allow_nan=False); out.write('\n'); out.flush(); os.fsync(out.fileno())


def approval():
    value = read(E/'FINAL_APPROVAL.json')
    assert value['decision'] == 'ACCEPTED_R3_SOURCE_STOP_ARCHIVE_ONLY'
    assert value['open_P0'] == value['open_P1'] == 0
    assert value['report_sha256'] == digest((E/'review.md').read_bytes())
    assert value['manifest_sha256'] == digest((P/'STOP_FREEZE_MANIFEST.json').read_bytes())
    for name, sha in value['reviewed_closure_hashes'].items(): assert digest((R/name).read_bytes()) == sha, name
    for row in read(P/'STOP_FREEZE_MANIFEST.json')['files']:
        body = (R/row['path']).read_bytes()
        assert len(body) == row['bytes'] and digest(body) == row['sha256'], row['path']
    return value


def plan():
    value = approval()
    assert git('branch', '--show-current').strip() == b'test'
    assert git('rev-parse', 'HEAD').strip().decode() == git('rev-parse', 'origin/test').strip().decode() == BASE
    assert not git('diff', '--cached', '--name-only').strip()
    assert git('diff', '--name-only').decode().splitlines() == ['ops/daily-operations.md']
    assert (R/'ops/daily-operations.md').read_bytes().endswith(git('show', BASE+':ops/daily-operations.md'))
    unknown = [x.decode() for x in git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if x]
    assert all(x.startswith(('paper16_dev_r3/', 'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/')) for x in unknown)
    names = sorted(unknown+['ops/daily-operations.md'])
    covered = {r['path'] for r in read(P/'STOP_FREEZE_MANIFEST.json')['files']}
    covered.update(value['reviewed_closure_hashes'])
    covered.update(['paper16_dev_r3/STOP_FREEZE_MANIFEST.json',
        'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/review.md',
        'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/FINAL_REVIEW_1.md',
        'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/FINAL_APPROVAL.json'])
    assert set(names) <= covered, 'Unreviewed file appeared after final freeze/review'
    assert not any('/work/' in x or x.endswith(('.npz', '.npy', '.h5', '.nwb')) for x in names)
    assert {x for x in names if x.endswith('.bin')} <= {
        'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/PRECHANGE_GIT_TREE.bin',
        'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/DAILY_PRESTOP_SNAPSHOT.bin'}
    files = [{'path': n, 'bytes': (R/n).stat().st_size, 'sha256': digest((R/n).read_bytes())} for n in names]
    (P/'work/stage-paths.nul').write_bytes(b'\0'.join(n.encode() for n in names)+b'\0')
    write(P/'work/STAGING_PLAN.json', {'base': BASE, 'files': files, 'approval_sha256': digest((E/'FINAL_APPROVAL.json').read_bytes()),
          'manifest_sha256': value['manifest_sha256']})
    print(json.dumps({'exact_stage_files': len(files), 'raw_neural_staged': False}))


def batch(ref, names):
    data = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=R,
        input=('\n'.join(ref+':'+n for n in names)+'\n').encode())
    pos = 0; output = []
    for name in names:
        end = data.index(b'\n', pos); header = data[pos:end].split(); pos = end+1
        assert len(header) == 3 and header[1] == b'blob', name
        size = int(header[2]); body = data[pos:pos+size]; pos += size
        assert data[pos:pos+1] == b'\n'; pos += 1; output.append((header[0].decode(), body))
    assert pos == len(data)
    return output


def staged():
    approval(); value = read(P/'work/STAGING_PLAN.json'); names = [x['path'] for x in value['files']]
    actual = [x.decode() for x in git('diff', '--cached', '--name-only', '-z').split(b'\0') if x]
    assert set(actual) == set(names) and len(actual) == len(names)
    assert not git('diff', '--name-only').strip() and not git('ls-files', '--others', '--exclude-standard', '-z')
    assert not git('diff', '--cached', '--diff-filter=D', '--name-only')
    for row, (blob, body) in zip(value['files'], batch('', names)):
        assert body == (R/row['path']).read_bytes() and len(body) == row['bytes'] and digest(body) == row['sha256']
        row['staged_git_blob'] = blob
    write(P/'work/STAGED_VERIFICATION.json', {'files': value['files'], 'index_equals_reviewed_working_tree': True, 'unrelated_files': 0})
    print(json.dumps({'staged_byte_verified': len(names), 'unrelated_files': 0}))


def finish():
    value = approval(); plan = read(P/'work/STAGING_PLAN.json'); stage = read(P/'work/STAGED_VERIFICATION.json')
    assert plan['files'] == [{k: v for k, v in r.items() if k != 'staged_git_blob'} for r in stage['files']]
    commit = git('rev-parse', 'HEAD').strip().decode()
    assert git('rev-parse', commit+'^').strip().decode() == BASE
    assert git('rev-parse', 'origin/test').strip().decode() == commit
    remote = git('ls-remote', '--heads', 'origin', 'refs/heads/test').decode().strip()
    assert remote.split()[0] == commit
    assert not git('ls-remote', '--heads', 'origin', 'refs/heads/main').strip()
    names = [r['path'] for r in plan['files']]
    changed = [x.decode() for x in git('diff', '--name-only', '-z', BASE, commit).split(b'\0') if x]
    assert set(changed) == set(names) and len(changed) == len(names)
    assert not git('diff', '--diff-filter=D', '--name-only', BASE, commit)
    assert not git('status', '--porcelain=v1', '--untracked-files=all')
    rows = []
    for original, staged_row, (blob, body) in zip(plan['files'], stage['files'], batch('origin/test', names)):
        assert body == (R/original['path']).read_bytes() and digest(body) == original['sha256'] and len(body) == original['bytes']
        assert blob == staged_row['staged_git_blob']
        rows.append({**original, 'remote_git_blob': blob, 'remote_sha256': digest(body), 'byte_readback_match': True})
    fields = read(P/'TERMINAL_FIELDS.json')
    assert fields['FINAL_STATUS'] == 'NEED_ENV' and fields['WARN_COUNT'] == 1
    fields['GIT_COMMIT'] = commit; fields['REMOTE_VERIFICATION'] = 'VERIFIED_ORIGIN_TEST_ALL_CHANGED_BLOBS_AND_CLEAN_TREE'
    requirements = read(E/'REQUIREMENT_RESULTS.json'); semantic = read(P/'SEMANTIC_RESULTS.json')
    for group in [requirements['items'], semantic['items']]:
        for row in group:
            if row['status'] == 'PENDING_ARCHIVE':
                row['status'] = 'VERIFIED'
                row['actual_closure_proof'] = 'Independent accepted source-stop archive plus exact normal commit/push/remote changed blobs/clean; no scientific failure reclassified.'
    assert any(r['status'] == 'BLOCKED_NEED_ENV' for r in requirements['items'])
    receipt = {'mission': fields['MISSION_ID'], 'final_status': 'NEED_ENV', 'scientific_verdict': fields['SCIENTIFIC_VERDICT'],
        'archive_verified': True, 'not_scientific_PASS': True, 'base': BASE, 'commit': commit, 'branch': 'test',
        'origin_test': remote, 'origin_main': 'ABSENT_VERIFIED_NOT_INVENTED', 'verified_at_UTC': datetime.now(timezone.utc).isoformat(),
        'normal_push': True, 'force_push': False, 'changed_file_count': len(rows), 'changed_file_manifest': rows,
        'final_manifest_sha256': value['manifest_sha256'], 'final_review_sha256': value['report_sha256'],
        'terminal_fields': fields, 'requirement_trace': requirements['items'], 'semantic_trace': semantic['items'],
        'baseline_requirement_count': 333, 'verified_baseline_count': sum(r['status'] == 'VERIFIED' for r in requirements['items']),
        'bug_count': 0, 'warn_count': 1, 'clean_before_receipt': True, 'clean_after_receipt': True,
        'new_source_or_fit_after_stop': False, 'next_mission_started': False}
    write(P/'work/FINAL_HANDOFF_RECEIPT.json', receipt)
    assert not git('status', '--porcelain=v1', '--untracked-files=all')
    print(json.dumps({'final_status': 'NEED_ENV', 'scientific_verdict': fields['SCIENTIFIC_VERDICT'], 'commit': commit,
          'remote_changed_blobs_verified': len(rows), 'clean': True,
          'handoff_receipt_sha256': digest((P/'work/FINAL_HANDOFF_RECEIPT.json').read_bytes())}, indent=2))


if __name__ == '__main__': {'plan': plan, 'staged': staged, 'finish': finish}[sys.argv[1]]()
