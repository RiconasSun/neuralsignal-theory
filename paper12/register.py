"""Register the metadata protocol before any public metadata acquisition."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify():
    record = json.loads((HERE / 'registration.json').read_text())
    for key in ('protocol_hashes', 'prior_hashes'):
        for path, digest in record[key].items():
            if sha(ROOT / path) != digest:
                raise RuntimeError('Immutable evidence changed: ' + path)
    if record['old_ops'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('Original operations history changed')
    return record

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'register':
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        record = {'utc': datetime.now(timezone.utc).isoformat(),
                  'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                  'protocol_hashes': {f'paper12/{p}': sha(HERE / p) for p in ('protocol_M0.json', 'mission.json', 'register.py')},
                  'prior_hashes': {p: sha(ROOT / p) for p in tracked if p and p != 'ops/daily-operations.md'},
                  'old_ops': (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8')}
        with (HERE / 'registration.json').open('x') as out:
            json.dump(record, out, indent=2, sort_keys=True)
    print(json.dumps({'verified': True, 'registered_utc': verify()['utc']}))
