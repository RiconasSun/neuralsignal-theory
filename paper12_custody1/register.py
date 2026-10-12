"""Append-once prospective access amendment, never mutates original evidence."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ID = 'P12-M2-ISOLATED-CUSTODY-1'
BASE = 'a00ed81e8112d5c076a04f6768b4e9b1fed0c3dd'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data, exclusive=False):
    path = Path(path)
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def verify():
    reg = load(HERE / 'registration.json')
    for category in ('prior_sha256', 'amendment_sha256'):
        for name, value in reg[category].items():
            if sha(ROOT / name) != value:
                raise RuntimeError('FROZEN_EVIDENCE_CHANGED:' + name)
    if reg['old_ops'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('OLD_OPS_HISTORY_CHANGED')
    return reg


def main():
    if '--verify' in sys.argv:
        reg = verify()
        print(json.dumps({'verified': True, 'prior_files': len(reg['prior_sha256'])}))
        return
    if (HERE / 'registration.json').exists():
        raise RuntimeError('APPEND_ONLY_REGISTRATION_EXISTS')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != BASE:
        raise RuntimeError('CHECKPOINT_CHANGED')
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    baseline = ROOT / 'ops/evidence/2026-10-12/p12-m2-isolated-custody-1/goldenstandards.md'
    inputs = [HERE / p for p in ('mission.json', 'amendment.json', 'register.py', '.gitignore')] + [baseline]
    reg = {'mission': ID, 'registered_utc': datetime.now(timezone.utc).isoformat(), 'checkpoint': head,
           'neural_values_read': 0, 'prior_sha256': {p: sha(ROOT / p) for p in files if p and p != 'ops/daily-operations.md'},
           'amendment_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
           'old_ops': (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8')}
    save(HERE / 'registration.json', reg, True)
    verify()
    result = {'milestone': 'ACCESS_AMENDMENT_REGISTRATION', 'gate': 'PASS', 'registered_utc': reg['registered_utc'],
              'registration_sha256': sha(HERE / 'registration.json'), 'prior_files_preserved': len(reg['prior_sha256']),
              'original_M1_gate': 'PASS', 'original_M2_gate': 'FAIL', 'original_M2_reclassified': False,
              'source_full_session_decoded_by_custodian': False, 'final_values_exposed_to_analysis': False, 'final_holdout_evaluated': False}
    save(HERE / 'results/registration_gate.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
