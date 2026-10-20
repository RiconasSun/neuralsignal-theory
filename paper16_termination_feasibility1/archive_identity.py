"""Saved identity checks only; no scientific module or raw neural array import."""
import hashlib,json,platform
import importlib.metadata as metadata
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'paper16_termination_feasibility1';E=R/'ops/evidence/2026-10-20/p16-numerical-termination-policy-feasibility-1'
def load(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check_rows(rows):
    for row in rows:
        path=R/row['path']
        if sha(path)!=row['sha256'] or path.stat().st_size!=row['bytes']:raise RuntimeError('Frozen artifact identity: '+row['path'])
def verify():
    runtime=load(P/'RUNTIME_IDENTITY.json');versions={'Python':platform.python_version(),**{k:metadata.version(k) for k in ['numpy','scipy','h5py','requests']}}
    if versions!=runtime['versions']:raise RuntimeError('Pinned runtime versions')
    for name,digest in runtime['files'].items():
        if sha(R/name)!=digest:raise RuntimeError('Runtime source/binary hash: '+name)
    if sha(R/runtime['runtime_executable'])!=runtime['python_launcher_sha256']:raise RuntimeError('Runtime executable')
    check_rows(load(P/'CODE_FREEZE.json')['files']);check_rows(load(P/'PREFIT_MANIFEST.json')['files'])
    approval=load(E/'PREFIT_APPROVAL.json')
    if approval['manifest_sha256']!=sha(P/'PREFIT_MANIFEST.json') or approval['review_sha256']!=sha(R/approval['review_path']):raise RuntimeError('Exact independent prefit approval')
    if approval['decision']!='ACCEPTED_SINGLE_A_DIAGNOSTIC' or approval['open_P0'] or approval['open_P1']:raise RuntimeError('Prefit decision')
    claim=load(P/'REAL_CLAIM.json')
    if claim['prefit_approval_sha256']!=sha(E/'PREFIT_APPROVAL.json') or claim['code_freeze_sha256']!=sha(P/'CODE_FREEZE.json'):raise RuntimeError('Consumed authority binding')
    check_rows(load(P/'ARCHIVE_MANIFEST.json')['files'])
    print(json.dumps({'saved_identity':'PASS','runtime':versions,'worker_and_prefit_identity_unchanged':True,'new_math_evaluations':0}))
if __name__=='__main__':verify()
