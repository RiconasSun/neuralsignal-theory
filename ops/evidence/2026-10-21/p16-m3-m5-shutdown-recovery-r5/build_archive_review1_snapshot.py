"""Create-only local saved-state inventory after actual R5 termination.

No model imports, raw neural array decoding, optimization, or network calls.
The postarchive annex policy is deliberately finite to avoid a hash cycle.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path

R = Path(__file__).resolve().parents[4]
P = R / 'paper16_development_r5'
E = Path(__file__).resolve().parent
EP = E.relative_to(R).as_posix()
MISSION = 'P16-M3-M5-SHUTDOWN-RECOVERY-R5'
BASE = 'b7bb1227379462c2c7a1cef40ab0d0e99a6d020b'
ANNEXES = {
    'paper16_development_r5/LOCAL_ARCHIVE_MANIFEST.json': 'Create-only inventory self reference',
    'paper16_development_r5/PUBLICATION_MANIFEST.json': 'Separate prospective publication annex; no transmission authorized',
    **{EP + '/' + name: 'Postarchive saved-only closure annex; independently bound by final review'
       for name in ['SAVED_REPRODUCTION.log', 'SAVED_REPRODUCTION_RECEIPT.json',
                    'FINAL_REVIEW.md', 'FINAL_REVIEW_BINDING.json', 'verdict.md',
                    'REQUIREMENT_VERIFICATION.json', 'LOCAL_COMMIT_RECEIPT.json']},
}


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative(path):
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(R) or path.is_symlink():
        raise ValueError('Nonlocal or symbolic archive member')
    return resolved.relative_to(R).as_posix()


def build():
    if not (P / 'results/SUPERVISION.json').exists():
        raise RuntimeError('Actual native supervision terminal receipt required')
    supervision = load(P / 'results/SUPERVISION.json')
    supervisor = load(P / 'results/SUPERVISOR.json')
    if (type(supervision.get('returncode')) is not int
            or any(type(supervision.get(k)) is not bool for k in
                   ['killed_at_deadline', 'completed_before_deadline',
                    'native_job_tree_enforced', 'assigned_before_resume'])
            or supervision['native_job_tree_enforced'] is not True
            or supervision['assigned_before_resume'] is not True
            or supervision.get('job_name') != supervisor.get('job_name')
            or supervisor.get('stage_sha256') != sha(P / 'results/STAGE_CLAIM.json')
            or not supervisor['job_name'].startswith('Local\\P16_R5_' + str(supervisor['supervisor_pid']) + '_')):
        raise RuntimeError('Actual native Job/process/stage receipt binding failed')
    stop = P / 'results/SCIENTIFIC_STOP.json'
    complete = P / 'results/WORKER_COMPLETE.json'
    if stop.exists() == complete.exists():
        raise RuntimeError('Exactly one actual scientific terminal state required')
    if complete.exists() and not (E / 'M4_APPROVAL.json').exists():
        raise RuntimeError('Independent complete-M4 approval required')
    if complete.exists() and (supervision['returncode'] != 0
                             or supervision['killed_at_deadline']
                             or not supervision['completed_before_deadline']
                             or supervision.get('clock_failure') is not None):
        raise RuntimeError('Complete-M4 native termination must pass')
    roots = ['paper16_development_r5', EP]
    files = {}
    excluded = dict(ANNEXES)
    for root in roots:
        for path in (R / root).rglob('*'):
            if not path.is_file():
                continue
            name = relative(path)
            if '__pycache__' in path.parts or (E / 'LOCAL_ONLY') in path.parents:
                excluded[name] = 'Nonpublication cache or local Git closure receipt, excluded explicitly at freeze'
            elif name not in excluded:
                files[name] = path
    references = [P / 'INDEPENDENT_R5_PROTECTED_HASH_READBACK.json',
                  P / 'PREFIT_FREEZE_MANIFEST_V3.json']
    for index in references:
        for row in load(index)['files']:
            path = R / row['path']
            name = relative(path)
            if name in excluded:
                raise RuntimeError('Frozen scientific reference cannot be excluded: ' + name)
            if sha(path) != row['sha256']:
                raise RuntimeError('Original frozen identity changed: ' + name)
            files[name] = path
    rows = [{'path': name, 'sha256': sha(path), 'bytes': path.stat().st_size}
            for name, path in sorted(files.items())]
    output = {
        'schema': 'R5_LOCAL_ARCHIVE_V1', 'mission': MISSION, 'base': BASE,
        'created_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'inventory_roots': roots,
        'exclusions': [{'path': name, 'reason': reason} for name, reason in sorted(excluded.items())],
        'historical_reference_manifests': [relative(path) for path in references],
        'files': rows, 'file_count': len(rows),
        'public_manifest': None,
        'public_manifest_policy': 'Deferred separate final-review-bound annex; this archive does not authorize publication',
        'new_model_or_derivative_calls': 0,
        'E_access': False, 'Final_C_D_access': False,
    }
    target = P / 'LOCAL_ARCHIVE_MANIFEST.json'
    with target.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'manifest': relative(target), 'sha256': sha(target),
                      'files': len(rows), 'create_only': True}, indent=2))


if __name__ == '__main__':
    build()
