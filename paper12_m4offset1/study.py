import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/'paper12_custody1'
PREVIOUS=ROOT/'paper12_resume1'
M3=ROOT/'paper12_m3num1'
HARNESS=ROOT/'paper12_m4harness1'
ID='P12-M4-OFFSET-NUMERICAL-RECOVERY-1'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path,value,exclusive=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x' if exclusive else 'w',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')


def verify():
    record=load(HERE/'registration.json')
    for name,digest in record['prior_sha256'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('HISTORICAL_BYTES_CHANGED:'+name)
    for name,digest in record['implementation_sha256'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('REGISTERED_DIAGNOSTIC_CODE_CHANGED:'+name)
    return record
