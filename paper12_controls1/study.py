"""New controls track only; no mutable scientific policy."""
from pathlib import Path
from datetime import datetime,timezone
from register import sha,load,save,BASE,MISSION
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/'paper12_custody1'
PREVIOUS=ROOT/'paper12_resume1'
OFFSET=ROOT/'paper12_m4offset1'
def verify():
    reg=load(HERE/'prospective_registration.json')
    if sha(HERE/'SECURITY_ARCHITECTURE.md')!=reg['architecture_sha256'] or sha(HERE/'mission.json')!=reg['mission_sha256']:raise RuntimeError('E0_CHANGED')
    for name,digest in reg['source_sha256'].items():
        if sha(ROOT/name)!=digest:raise RuntimeError('FROZEN_SOURCE_CHANGED:'+name)
    return reg
