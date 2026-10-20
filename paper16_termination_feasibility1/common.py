"""Mission identities/guards; no neural reader, scoring or fit at import."""
import hashlib,json,os,platform,time
import importlib.metadata as metadata
from pathlib import Path
import numpy as np
from paper16_dev_r3.clock_bound import guard as old_guard,make_stage,verify_stage_environment
from paper16_dev_r3.windows_job import require_job
from paper16_m1.code import spec

R=Path(__file__).resolve().parents[1];P=R/'paper16_termination_feasibility1'
E=R/'ops/evidence/2026-10-20/p16-numerical-termination-policy-feasibility-1'
BASE='682b0ac37fc6a0bc211acc388134058ec3c071aa'
MISSION='P16-NUMERICAL-TERMINATION-POLICY-FEASIBILITY-1'
class ImplementationStop(RuntimeError):pass
class NumericalStop(RuntimeError):pass
class BudgetStop(RuntimeError):pass
class AccessStop(RuntimeError):pass
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,message):
    if not ok:raise ImplementationStop(message)
def once(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def event(p,**row):
    with Path(p).open('a',encoding='utf8',newline='\n') as f:
        f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def array_id(a):
    a=np.asarray(a);return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def arrays(p,**values):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:np.savez_compressed(f,**values);f.flush();os.fsync(f.fileno())
    return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'arrays':{k:array_id(v) for k,v in values.items()}}
def guard(stage):
    old_guard(stage)
    if stage['deadline_monotonic']-stage['start_monotonic']>7200:raise BudgetStop('Mission wall cap7200s')
NUMERIC=load(P/'CANDIDATE_NUMERICAL_POLICY.json')
def verify_policy():
    old=load(R/'paper16_m1/NUMERICAL_POLICY.json');expected=load(R/'paper16_m1/NUMERICAL_POLICY.json');expected['options']['ftol']=0.0
    require(NUMERIC==expected and old['options']['ftol']==1e-12,'Only registered ftol0 change permitted')
def verify_history(protected=False):
    pins=load(P/'SOURCE_PINS.json');require(pins['BASE']==BASE,'BASE identity')
    for name,digest in pins['files'].items():require(sha(R/name)==digest,'Historical file changed: '+name)
    if protected:
        rows=load(R/'paper16_development_r3/PROTECTED_STATE_MANIFEST.json')['files']
        for row in rows:require(sha(R/row['path'])==row['sha256'] and (R/row['path']).stat().st_size==row['bytes'],'Protected hash: '+row['path'])
    return len(pins['files'])
def verify_runtime():
    identity=load(P/'RUNTIME_IDENTITY.json')
    actual={'Python':platform.python_version(),**{k:metadata.version(k) for k in ['numpy','scipy','h5py','requests']}}
    require(actual==identity['versions']==NUMERIC['software'],'Pinned runtime version')
    for name,digest in identity['files'].items():require(sha(R/name)==digest,'Runtime file identity')
    require(sha(R/identity['runtime_executable'])==identity['python_launcher_sha256'],'Python launcher identity')
    return actual
def verify_code():
    manifest=load(P/'CODE_FREEZE.json')
    for row in manifest['files']:require(sha(R/row['path'])==row['sha256'],'Reviewed candidate changed: '+row['path'])
    verify_policy();verify_runtime();return manifest
def verify_prefit():
    verify_history();verify_code()
    approval=load(E/'PREFIT_APPROVAL.json')
    require(approval['decision']=='ACCEPTED_SINGLE_A_DIAGNOSTIC' and approval['open_P0']==approval['open_P1']==0,'Independent prefit acceptance required')
    require(approval['manifest_sha256']==sha(P/'PREFIT_MANIFEST.json'),'Prefit exact manifest identity')
    review=R/approval['review_path'];require(review.resolve().is_relative_to(E.resolve()) and sha(review)==approval['review_sha256'],'Independent review identity')
    for row in load(P/'PREFIT_MANIFEST.json')['files']:require(sha(R/row['path'])==row['sha256'],'Prefit artifact changed')
    cert=load(P/'SYNTHETIC_CERTIFICATION.json');require(cert['mandatory_tests_pass'] and cert['real_A_attempts']==0,'Native synthetic certification required')
    return approval
def claim(path,value):
    once(path,value)  # exclusive create and fsync; never overwrite/recover entitlement

