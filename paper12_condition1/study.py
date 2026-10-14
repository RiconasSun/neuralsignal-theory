"""Append-only artifacts for the bounded optimization study."""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/'paper12_custody1'
PREVIOUS=ROOT/'paper12_resume1'
OFFSET=ROOT/'paper12_m4offset1'
GRAD=ROOT/'paper12_contgrad1'
BASE='36a4099d0d7473fd21e592f3f2f321a493c46e44'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v,exclusive=True):
    if exclusive is not True:raise ValueError('APPEND_ONLY')
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
