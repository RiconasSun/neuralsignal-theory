"""R2 identities, append-only evidence and explicitly pinned scientific reuse."""
import hashlib,json,os
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[1];P=R/'paper16_development_r2'
E=R/'ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2'
BASE='4aef2810885b6167ef909eb8ccc9e8c5c967871a'
MISSION='P16-M3-M5-FROZEN-DEVELOPMENT-R2'

class ImplementationStop(RuntimeError):pass
class NumericalStop(RuntimeError):pass
class BudgetStop(RuntimeError):pass
class AccessStop(RuntimeError):pass

def load(path):return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def once(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def event(path,**row):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf8',newline='\n') as f:
        f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def array_id(a):
    a=np.asarray(a);return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def arrays(path,**values):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:np.savez_compressed(f,**values);f.flush();os.fsync(f.fileno())
    return {'path':path.relative_to(R).as_posix(),'sha256':sha(path),'arrays':{k:array_id(v) for k,v in values.items()}}
def verify_pins():
    for name,digest in load(P/'SOURCE_PINS.json')['files'].items():
        if sha(R/name)!=digest:raise ImplementationStop('Frozen reuse identity changed: '+name)

verify_pins()
from paper16_m1.code import spec,dynamics,analysis_oracles
from paper16_dev_r3.clock_bound import guard,make_stage,verify_stage_environment
from paper16_dev_r3.windows_job import require_job

MODELS=['B0','B1','B2','B3','B4','C','D','S']
CONTRASTS=[('B4','B1'),('B4','B2'),('B4','B3'),('D','B4'),('C','B4'),('D','S')]
REFIT_PANELS=['S01','S02','S05','S06','S07','S09','S10','S11']
SEEDS=[11,23,37];GRID=[.01,.1,1.]
NUMERIC=load(R/'paper16_m1/NUMERICAL_POLICY.json')
