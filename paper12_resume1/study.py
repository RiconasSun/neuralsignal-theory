import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'paper12_custody1'
ID = 'P12-M2-REAL-RESUME-1'
BASE = '376ca01cb97659d1acda84366b06963d30aa9405'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def verify():
    record = load(HERE / 'registration.json')
    for name, digest in record['prior_sha256'].items():
        if name == 'ops/daily-operations.md':
            original = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
            if hashlib.sha256(original).hexdigest() != digest or not (ROOT / name).read_bytes().endswith(original):
                raise RuntimeError('PRIOR_OPERATIONS_BYTES_CHANGED')
        elif sha(ROOT / name) != digest:
            raise RuntimeError('PRIOR_EVIDENCE_CHANGED:' + name)
    for name, digest in record['prospective_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('PROSPECTIVE_PROTOCOL_CHANGED')
    return record


def register():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != BASE:
        raise RuntimeError('WRONG_BASE')
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    inputs = [HERE / x for x in ('.gitignore', 'mission.json', 'protocol.json', 'study.py')]
    inputs.append(ROOT / 'ops/evidence/2026-10-12/p12-m2-real-resume-1/goldenstandards.md')
    prior = load(ROOT / 'paper12_transport1/registration.json')
    save(HERE / 'registration.json', dict(mission=ID, base=BASE,
        registered_utc=datetime.now(timezone.utc).isoformat(), real_source_requests=0,
        sources=prior['sources'], reuse=prior['reuse'],
        prior_sha256={x: sha(ROOT / x) for x in names if x},
        prospective_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in inputs}), True)
    verify()
    print('PROSPECTIVE_REGISTRATION_COMPLETE; NO SOURCE REQUESTS')


if __name__ == '__main__':
    register()
