import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):digest.update(block)
    return digest.hexdigest()


def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path,value,exclusive=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x' if exclusive else 'w',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')


def verify():
    record=load(HERE/'registration.json')
    for name,digest in record['prior_sha256'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('PRIOR_EVIDENCE_CHANGED:'+name)
    for name,digest in record['prospective_sha256'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('PROTOCOL_CHANGED:'+name)
    if record['old_operations'] not in (ROOT/'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('PRIOR_OPERATIONS_HISTORY_CHANGED')
    return record
