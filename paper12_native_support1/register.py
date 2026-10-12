"""Prospective registration protects every prior tracked scientific artifact."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify():
    r = json.loads((HERE/'registration.json').read_text())
    for key in ('protocol_hashes','prior_hashes'):
        for path,digest in r[key].items():
            if sha(ROOT/path)!=digest: raise RuntimeError('Frozen prior evidence changed: '+path)
    if r['old_ops'] not in (ROOT/'ops/daily-operations.md').read_text(encoding='utf-8'):
        raise RuntimeError('Old operations history changed')
    return r
if __name__=='__main__':
    if sys.argv[1]=='register':
        files = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
        record={'utc':datetime.now(timezone.utc).isoformat(),
                'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
                'protocol_hashes':{'paper12_native_support1/'+p:sha(HERE/p) for p in ('mission.json','protocol.json','register.py')},
                'prior_hashes':{p:sha(ROOT/p) for p in files if p and p!='ops/daily-operations.md'},
                'old_ops':(ROOT/'ops/daily-operations.md').read_text(encoding='utf-8')}
        if record['head']!='91c92abcda3549196cce1d6253ef0fa76c8d0886': raise RuntimeError('Checkpoint drift')
        with (HERE/'registration.json').open('x') as out: json.dump(record,out,indent=2,sort_keys=True)
    print(json.dumps({'verified':True,'utc':verify()['utc']}))
