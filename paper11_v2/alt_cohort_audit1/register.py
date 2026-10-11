"""Freeze protocol and all previous tracked evidence before acquisition."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'results'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(obj, handle, indent=2, sort_keys=True, allow_nan=False)


def verify():
    reg = read(OUT / 'registration.json')
    for field in ('preserved_tracked_sha256', 'registered_source_sha256'):
        for name, digest in reg[field].items():
            if sha(ROOT / name) != digest:
                raise RuntimeError('Frozen file changed: ' + name)
    if reg['original_ops_text'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('Original operations text not preserved')
    return reg


def register():
    policy = read(HERE / 'protocol.json')
    checks = {'paper11_v2/results/R2/gate_result.json': 'original_R2_gate_sha256',
              'paper11_v2/results/R0_schema1/final_validation_lock.json': 'original_split_sha256',
              'paper11_v2/boundary_audit1/results/gate_result.json': 'prior_audit_gate_sha256'}
    for path, field in checks.items():
        assert sha(ROOT / path) == policy[field]
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    source = [HERE / 'protocol.json', Path(__file__), ROOT / 'paper11_v2/mission-alt-cohort-audit1.json']
    save(OUT / 'registration.json', {
        'registered_utc': datetime.now(timezone.utc).isoformat(),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'mission': policy['mission'], 'before_new_acquisition': True,
        'preserved_tracked_sha256': {p: sha(ROOT / p) for p in files if p and p != 'ops/daily-operations.md'},
        'original_ops_text': (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'),
        'registered_source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in source}})
    verify()


if __name__ == '__main__':
    {'register': register, 'verify': verify}[sys.argv[1]]()
    print('Registration/preservation verified; no neural access.')
