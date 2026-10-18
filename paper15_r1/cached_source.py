"""Verified read-only reuse of already pinned Development source cache."""
from .source import load_json
import hashlib,json
from pathlib import Path
from .source import R,P

def cached_neural(row,file,s3=None):
    if row['allocation']!='DEVELOPMENT' or file['role'] not in ('times','clusters'):
        raise PermissionError('Only original Development neural sources are authorized')
    old=load_json((R/'paper15_dev/results'/(row['subject']+'_A_QC.json')).read_text())
    receipt=next(x for x in old['files'] if x['key']==file['key'])
    path=(R/'paper15_m0/work/native' if receipt['reuse_M0'] else R/'paper15_dev/work/neural')/row['eid']/Path(file['key']).name
    assert path.stat().st_size==file['bytes']==receipt['bytes']
    h=hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda:handle.read(8*1024*1024),b''):h.update(block)
    assert h.hexdigest()==receipt['sha256']
    return path,dict(receipt,reused_readonly_original_cache=True,original_path=str(path.relative_to(R)),new_fitting_coefficients_reused=False)
