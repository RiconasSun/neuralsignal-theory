"""Metadata-only scoped archive closure. Never load neural arrays or run models."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
P = R / 'paper15_r1'
W = P / 'work'
BASE = 'b0b692bd9b7e42f767117a51d0119644327a97f0'
ER = E.relative_to(R).as_posix()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=R)


def blobs(queries):
    """Read a bounded batch of Git blobs without changing the index."""
    for start in range(0, len(queries), 16):
        part = queries[start:start + 16]
        payload = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=R,
                                          input=('\n'.join(part) + '\n').encode())
        offset = 0
        for query in part:
            end = payload.index(b'\n', offset)
            header = payload[offset:end].split()
            assert len(header) == 3 and header[1] == b'blob', query
            size = int(header[2])
            offset = end + 1
            value = payload[offset:offset + size]
            offset += size
            assert payload[offset:offset + 1] == b'\n'
            offset += 1
            yield value
        assert offset == len(payload)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def integrity():
    archive = read(P / 'ARCHIVE_FREEZE.json')
    for relative, expected in archive['hashes'].items():
        assert sha(P / relative) == expected, relative
    for relative, expected in archive['external_hashes'].items():
        assert sha(R / relative) == expected, relative
    original = git('show', BASE + ':ops/daily-operations.md')
    assert len(original) == 65054
    assert hashlib.sha256(original).hexdigest() == '7854ac3bdf3a6ac30676413ef125a0d1849bfcec7b5fb91f28a7fd51974101bf'
    assert (R / 'ops/daily-operations.md').read_bytes().endswith(original)
    assert git('branch', '--show-current').decode().strip() == 'test'
    return archive, original


def matrix_update(ids, proofs, final=False):
    matrix = read(E / 'PRESERVATION_MATRIX.json')
    baseline = read(E / 'baseline.json')
    assert len(matrix['rows']) == len(baseline['requirements']) == 196
    for row, frozen in zip(matrix['rows'], baseline['requirements']):
        assert row['requirement_id'] == frozen['id'] and row['requirement'] == frozen['requirement']
        if row['requirement_id'] in ids:
            row['status'] = 'VERIFIED'
            row.pop('remaining_gate', None)
            row['evidence'] += [{'path': ER + '/' + name, 'sha256': sha(E / name)} for name in proofs]
    matrix['verified_baseline_count'] = sum(row['status'] == 'VERIFIED' for row in matrix['rows'])
    matrix['scope'] = ('Complete Development handoff; H1 actual remote proof archived. H2 own push/readback/clean and final handoff are enforced before terminal return.'
                       if final else 'H1 reviewed archive candidate; four Git/return/stop closure obligations remain open.')
    dump(E / 'PRESERVATION_MATRIX.json', matrix)
    lines = ['# Requirement preservation matrix', '',
             'All 196 original IDs and requirement texts retained. Scientific mixed/unavailable findings follow the original reporting contract; no scientific failure is reclassified.', '',
             '|ID|Status|Verification|Primary evidence|', '|---|---|---|---|']
    lines += [f"|{row['requirement_id']}|{row['status']}|{row['verification_method']}|{row['implementation_location']}|" for row in matrix['rows']]
    (E / 'preservation-matrix.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def prepare_h1():
    _, original = integrity()
    reviews = ['FINAL_SCIENTIFIC_REVIEW_RECEIPT_1.json', 'FINAL_NUMERICAL_EVIDENCE_REVIEW_RECEIPT_1.json']
    for name in reviews:
        receipt = read(E / name)
        assert receipt['decision'] == 'ACCEPTED_ARCHIVE_CANDIDATE_H1'
        assert type(receipt['open_P0']) is int and receipt['open_P0'] == 0
        assert type(receipt['open_P1']) is int and receipt['open_P1'] == 0
        assert receipt['source_archive_sha256'] == sha(P / 'ARCHIVE_FREEZE.json')
    matrix_update({'REQ-194'}, reviews)
    (E / 'review.md').write_text(
        '# Independent review aggregate — H1 archive candidate\n\n'
        'Mission P15-DEV-EXACT-NATIVE-REPAIR-R1. REVIEW_MODE complete for the frozen scientific/source archive. '
        'Both final independent reviews accept ACCEPTED_ARCHIVE_CANDIDATE_H1; P0=0, P1=0, bug_count=0, warn_count=0. '
        'See FINAL_SCIENTIFIC_REVIEW_1.md and FINAL_NUMERICAL_EVIDENCE_REVIEW_1.md and their receipts. '
        'All failed intermediate reviews remain preserved; corrections were verified before the affected production stages.\n\n'
        'This accepts a scoped normal origin/test archive. MERGE_ALLOWED=false: no main promotion or scientific validation. '
        'N1 primary 7/10 fails the original 8/10 requirement, N4 aggregate is unavailable (5 mice), and all five secondary Holm tests are nonsignificant. '
        'All results exploratory. No Final C/D access, fit or evaluation. No next mission.\n\n'
        'Remaining closure: H1 normal commit/push, actual remote SHA/blob manifest and clean tree; then metadata-only H2 archiving that proof, independent closure review, H2 normal push/readback/clean and final owner handoff/stop. '
        'Current 192/196 verified; no terminal full-mission PASS asserted here.\n', encoding='utf-8')
    (E / 'verdict.md').write_text(
        '# Reviewed archive candidate; Git closure pending\n\n'
        'Mission P15-DEV-EXACT-NATIVE-REPAIR-R1. Internal CONTINUE_EXECUTION; 192/196 verified, four Git/return/stop obligations pending. '
        'bug_count=0; warn_count=0; all anti-shrink counters=0; no required item omitted. '
        'Both independent final reviews accept the frozen H1 archive candidate. Native saved-only PowerShell reproduction exit0, 126 tests.\n\n'
        'Native repair and authorized Development execution complete: 10 mice/8 labs, 610 new main +525 sensitivity fits, historical359 preserved, cumulative1494. '
        'One E batch, 34965 reference bundles. Primary N1 mixed (7/10<8); N4 aggregate unavailable (5); all five secondary Holm p>.05. '
        'No robust primary, dynamics, movement-independent, persistent-state, mechanistic or held-out validation claim. '
        'No Final C/D neural access or automatic Prompt4.\n\n'
        'Await actual scoped origin/test commit/push/readback/clean followed by truthful metadata closure.\n', encoding='utf-8')
    prefix = ('# Current mission: P15-DEV-EXACT-NATIVE-REPAIR-R1\n\n'
              'CLOSURE_MODE: reviewed Development archive candidate; Git closure pending. Exact-native/source/A gates PASS; '
              '10 Development mice/8 labs, new610main+525sensitivity fits; old359 preserved. B selection frozen; one E batch complete. '
              'Exploratory only: primary N1 7/10<8, N4 aggregate unavailable with5mice, all5secondary Holm tests nonsignificant. '
              '126 saved-only reproduction tests PASS; final independent reviews P0/P1=0. No Final C/D access or automatic Prompt4. '
              f'Evidence: {ER}. Original daily-operations bytes preserved below.\n\n---\n')
    (R / 'ops/daily-operations.md').write_bytes(prefix.encode() + original)
    integrity()


def stage_plan(label):
    integrity()
    assert not git('diff', '--cached', '--name-only', '-z'), 'Unexpected pre-existing staged files'
    names = set(git('ls-files', '--others', '--exclude-standard', '-z').decode().strip('\0').split('\0'))
    names.update(git('diff', '--name-only', '-z').decode().strip('\0').split('\0'))
    names.discard('')
    assert names
    for name in names:
        assert name == 'ops/daily-operations.md' or name.startswith('paper15_r1/') or name.startswith(ER + '/'), name
        assert '/work/' not in name and '__pycache__' not in name and not name.endswith('.pyc'), name
        if label == 'H2':
            assert not name.startswith('paper15_r1/'), 'H2 must be metadata-only'
    W.mkdir(exist_ok=True)
    (W / (label + '_pathspec.nul')).write_bytes(b''.join(n.encode() + b'\0' for n in sorted(names)))
    dump(W / (label + '_staging_manifest.json'), {'label': label, 'files': {n: sha(R/n) for n in sorted(names)}, 'count': len(names)})
    print(json.dumps({'label': label, 'stage_paths': len(names)}))


def stage_verify(label):
    expected = read(W / (label + '_staging_manifest.json'))
    names = git('diff', '--cached', '--name-only', '-z').decode().strip('\0').split('\0')
    assert sorted(names) == sorted(expected['files'])
    for name, blob in zip(names, blobs([':' + n for n in names]), strict=True):
        assert hashlib.sha256(blob).hexdigest() == expected['files'][name], name
        assert sha(R / name) == expected['files'][name], name
    integrity()
    print(json.dumps({'label': label, 'staged_files_verified': len(names), 'git_index_mutated': False}))


def readback(label):
    integrity()
    commit = git('rev-parse', 'HEAD').decode().strip()
    remote_lines = git('ls-remote', '--heads', 'origin', 'refs/heads/main', 'refs/heads/test').decode().splitlines()
    remote = {line.split()[1]: line.split()[0] for line in remote_lines}
    assert remote.get('refs/heads/test') == commit
    assert git('rev-parse', 'origin/test').decode().strip() == commit
    assert not git('status', '--porcelain'), 'Must capture actual clean tree before writing receipt'
    parent = git('rev-parse', 'HEAD^').decode().strip()
    names = git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', 'HEAD').decode().strip('\0').split('\0')
    expected = read(W / (label + '_staging_manifest.json'))
    assert sorted(names) == sorted(expected['files'])
    manifest = []
    for name, blob in zip(names, blobs([commit + ':' + n for n in names]), strict=True):
        digest = hashlib.sha256(blob).hexdigest()
        assert digest == sha(R / name) == expected['files'][name], name
        manifest.append({'path': name, 'bytes': len(blob), 'sha256': digest})
    receipt = {'mission': 'P15-DEV-EXACT-NATIVE-REPAIR-R1', 'label': label,
               'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'commit': commit, 'parent': parent,
               'origin_test': remote['refs/heads/test'], 'origin_main': remote.get('refs/heads/main'),
               'branch_classification': 'TEST_ONLY_REMOTE_NO_MAIN' if 'refs/heads/main' not in remote else 'CHECK_REMOTE_GRAPH',
               'remote_readback': True, 'fetched_origin_test_matches': True, 'working_tree_clean': True,
               'normal_nonforce_push': True, 'main_written': False, 'changed_files': manifest,
               'changed_file_count': len(manifest), 'source_archive_sha256': sha(P / 'ARCHIVE_FREEZE.json'),
               'Final_C_access': False, 'Final_D_access': False, 'new_fit_or_E_replay': False}
    # H1 proof is archived by H2. H2 own post-push proof stays ignored to avoid self-reference.
    target = E / 'H1_REMOTE_READBACK.json' if label == 'H1' else W / 'H2_REMOTE_READBACK.json'
    dump(target, receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'changed_files'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare-h1', 'stage-plan', 'stage-verify', 'readback', 'integrity'])
    parser.add_argument('--label', choices=['H1', 'H2'], default='H1')
    args = parser.parse_args()
    if args.action == 'prepare-h1': prepare_h1()
    elif args.action == 'stage-plan': stage_plan(args.label)
    elif args.action == 'stage-verify': stage_verify(args.label)
    elif args.action == 'readback': readback(args.label)
    else:
        archive, _ = integrity()
        print(json.dumps({'package_hashes_verified': len(archive['hashes']), 'external_hashes_verified': len(archive['external_hashes'])}))
