from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'paper12_custody1'
sys.path.insert(0, str(OLD))
import register as old
sha, load, save = old.sha, old.load, old.save


def verify():
    old.verify()
    registration = load(HERE / 'registration.json')
    for name, digest in registration['prior_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('PRIOR_EVIDENCE_CHANGED:' + name)
    for name, digest in registration['amendment_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('TRANSPORT_AMENDMENT_CHANGED:' + name)
    if registration['old_ops'] not in (ROOT / 'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('PRIOR_OPERATIONS_HISTORY_CHANGED')
    return registration
