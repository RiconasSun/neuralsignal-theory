"""Saved-document inputs and immutable source verification."""
from pathlib import Path
import csv,hashlib,json,socket,sys,importlib.abc

P=Path(__file__).resolve().parent
R=P.parent
E=R/'ops/evidence/2026-10-18/p15-m7-full-manuscript-and-publication-package'
ORDER=['B4-B1','B4-B3','B4-B2','D-B4','C-B4','D-S']
LABELS=['Combined history','Own history','Other-unit history','Discrete beyond B4','Continuous beyond B4','Discrete vs static']
COHORTS={'Development':'paper15_r1','Final':'paper15_final1'}

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_rows(p,data,fields=None):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(dict.fromkeys(k for r in data for k in r)));w.writeheader();w.writerows(data)
def verify_sources():
    frozen=read(P/'SOURCE_HASHES.json')
    for n,h in frozen['hashes'].items():
        path=(R/n).resolve();assert path.is_relative_to(R) and 'work' not in path.relative_to(R).parts
        assert path.suffix.lower() not in {'.npy','.npz','.nwb','.h5'}
        assert sha(path)==h,n
    return len(frozen['hashes'])
class NoWorkers(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.startswith(('paper15_m0','paper15_m1','paper15_dev','paper15_r1','paper15_final1')):
            raise PermissionError('Manuscript process cannot import scientific workers: '+fullname)
def lock_process():
    import numpy as np
    def denied(*args,**kwargs):raise PermissionError('Results-locked manuscript: no arrays or network')
    np.load=denied;socket.socket.connect=denied;socket.create_connection=denied
    if not any(isinstance(x,NoWorkers) for x in sys.meta_path):sys.meta_path.insert(0,NoWorkers())
def stats(cohort):return read(R/COHORTS[cohort]/'results'/('E_STATISTICS.json' if cohort=='Development' else 'D_STATISTICS.json'))
def fmt(v,n=8):return f'{float(v):.{n}g}'
