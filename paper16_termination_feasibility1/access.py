"""Exact saved-A loader and ordinary-process access checks, not hostile-admin security."""
import os,socket,sys
from pathlib import Path
import numpy as np
from .common import *

def allowed_protected(path):
    identity=load(P/'INPUT_IDENTITY.json');old=identity['original_failed_task']['folder']+'/initial.npz'
    return Path(path).resolve() in {(R/identity['A_state']['path']).resolve(),(R/old).resolve()}

def check_open(path):
    if not isinstance(path,(str,bytes,os.PathLike)):return
    value=Path(os.fsdecode(path)).resolve()
    # All historical work caches denied except exact original A state/initializer and pinned runtime.
    for parent in value.parents:
        if parent.name=='work' and parent.parent.name.startswith('paper16_'):
            if parent.parent==P or value.is_relative_to(R/'paper16_m1/work/runtime'):return
            if allowed_protected(value):return
            raise AccessStop('Unregistered protected input denied: '+str(value))

def install_guard():
    def hook(name,args):
        if name=='open':check_open(args[0])
        if name in ['socket.connect','socket.getaddrinfo']:raise AccessStop('No source network')
    sys.addaudithook(hook)

def load_A(folder,stage):
    verify_prefit();guard(stage)
    identity=load(P/'INPUT_IDENTITY.json');meta=identity['A_state']
    require(meta['role']=='A' and meta['key']=='733457989/S02' and meta['panel']=='S02','Exact A-only identity')
    path=R/meta['path'];require(allowed_protected(path) and sha(path)==meta['sha256'],'A state file identity')
    event(folder/'ACCESS.jsonl',event='A_STATE_DECODE_RESERVED',path=meta['path'],sha256=meta['sha256'],role='A')
    with np.load(path,allow_pickle=False) as state:
        values={k:state[k].copy() for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask','mean','scale','active']}
    for k,v in values.items():require(array_id(v)==meta['arrays'][k],'A feature/scaler/member identity: '+k)
    require(np.array_equal(values['ordinals'],np.arange(90)) and np.isfinite(values['raw']).all() and np.isfinite(values['y']).all(),'Original A rows/finiteness')
    require(values['score_mask'].all() and values['y'].shape==(90,6,8) and values['raw'].shape==(90,6,8,38),'Exact S02 target/mask/dimensions')
    event(folder/'ACCESS.jsonl',event='A_STATE_DECODE_COMPLETED',role='A',members=list(values),no_B_E_Final=True)
    from paper16_development_r3.features import Batch,Scaling
    from paper16_development_r3.models import Objective
    b=Batch(values['raw'],values['y'],values['ordinals'],values['unit_ids'],values['colors'],meta['dt'],meta['psth'],meta['b1'],'A','S02',values['running_missing'],values['score_mask'])
    s=Scaling(values['mean'],values['scale'],values['active'],meta['psth'])
    unit=np.flatnonzero(b.unit_ids==951800892);require(len(unit)==1,'Unit identity')
    objective=Objective(b,s,'C',1.0,unit=int(unit[0]))
    init=R/identity['original_failed_task']['folder']/'initial.npz'
    original=next(row for row in identity['original_failed_task']['files'] if row['path'].endswith('/initial.npz'))
    require(sha(init)==original['sha256'],'Original initializer hash')
    with np.load(init,allow_pickle=False) as z:
        require(all(np.array_equal(getattr(objective,k),z[k]) for k in ['x0','lo','hi']),'Exact original initialization/bounds')
    require(len(objective.x0)==37,'Exactly37 free coefficients')
    once(folder/'INPUT_RECEIPT.json',{'A_state_sha256':meta['sha256'],'members':{k:array_id(v) for k,v in values.items()},
        'initial':array_id(objective.x0),'lo':array_id(objective.lo),'hi':array_id(objective.hi),'original_initial_sha256':sha(init),
        'free':objective.free.tolist(),'unit_index':int(unit[0]),'model':'C','lambda':1.0,'new_model_selection':False})
    return objective
