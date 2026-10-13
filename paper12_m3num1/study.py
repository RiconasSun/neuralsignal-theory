import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'paper12_custody1'
PREVIOUS = ROOT / 'paper12_resume1'
ID = 'P12-M3-NUMERICAL-RECOVERY-1'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value, exclusive=False):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False); f.write('\n')


def verify():
    p = load(HERE / 'registration.json')
    for name, digest in p['prior_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('HISTORICAL_BYTES_CHANGED:' + name)
    for name, digest in p['prospective_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('PROTOCOL_CHANGED:' + name)
    return p


def register():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if not head.startswith('98666f3'):
        raise RuntimeError('BASE_MISMATCH')
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    inputs = [HERE / n for n in ('protocol.json', 'mission.json', 'study.py', '.gitignore')]
    inputs.append(ROOT / 'ops/evidence/2026-10-12/p12-m3-numerical-recovery-1/goldenstandards.md')
    save(HERE / 'registration.json', dict(mission=ID, base=head, utc=datetime.now(timezone.utc).isoformat(),
        prior_sha256={n: sha(ROOT/n) for n in names if n},
        prospective_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
        source_requests=0, final_evaluation_access=False), True)
    verify(); print('PROSPECTIVE_DIAGNOSTIC_REGISTRATION_FROZEN')


if __name__ == '__main__':
    register()
