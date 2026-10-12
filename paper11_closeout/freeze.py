"""Freeze existing evidence; never inspect physiological holdouts."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def register():
    paths = load(HERE / 'inputs.json')
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    record = {'registered_utc': datetime.now(timezone.utc).isoformat(),
              'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'input_sha256': {p: sha(ROOT / p) for p in paths},
              'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in
                                [HERE / 'protocol.json', HERE / 'inputs.json', HERE / 'mission.json', Path(__file__)]},
              'previous_tracked_sha256': {p: sha(ROOT / p) for p in files if p and p != 'ops/daily-operations.md'},
              'original_ops': (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'),
              'raw_values_decoded': False, 'scientific_gate_amendment': False}
    with (HERE / 'evidence_freeze.json').open('x', encoding='utf-8') as f:
        json.dump(record, f, indent=2, sort_keys=True)
    verify()


def verify():
    record = load(HERE / 'evidence_freeze.json')
    for key in ('input_sha256', 'source_sha256', 'previous_tracked_sha256'):
        for name, digest in record[key].items():
            if sha(ROOT / name) != digest:
                raise RuntimeError('Frozen evidence changed: ' + name)
    if record['original_ops'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('Historical operations text changed')
    return record


if __name__ == '__main__':
    {'register': register, 'verify': verify}[sys.argv[1]]()
    print('Existing evidence frozen/verified; no new scientific execution.')
