"""Strict artifact utilities; no signing, neural loader or entitlement creation."""
import hashlib
import json
import os
from pathlib import Path

if __package__:
    from paper12_controls1.release_control import read_json, safe, verify_approval, validate_state_manifest
else:
    from release_control import read_json, safe, verify_approval, validate_state_manifest

MISSION='P12-D-PRODUCTION-PATH-READINESS-1'
BASE='76b19508a5a0728e500ff2e5f9c959309fbf967e'
PRIMARY=('own','population','stimulus_time','combined')
MANDATORY=('primary','matched16','rate_matched','boundary20','boundary40')
DEV_SIGN={'own':1,'population':-1,'stimulus_time':-1,'combined':-1}
RELEVANT={'own':('T',),'population':('T',),'stimulus_time':('S','B'),'combined':('T','S','B')}

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(v):return hashlib.sha256(v).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def new(p,v):
    with Path(p).open('xb') as f:f.write(canonical(v)+b'\n');f.flush();os.fsync(f.fileno())
def check_hashes(root,expected):
    for name,value in expected.items():
        if sha(safe(root,Path(root)/name))!=value:raise PermissionError('ARTIFACT_HASH:'+name)
def array_sha(a):
    import numpy as np
    return digest(np.ascontiguousarray(a).tobytes())

def validate_partition(manifest,partition,animals=None,trials=None):
    mice=manifest['cohort']
    if len(mice)!=13 or len(set(mice))!=13 or partition['cohort']!=mice or set(partition['D_trial_ids'])!=set(mice):raise PermissionError('EXACT_THIRTEEN_PARTITION')
    sessions={c['mouse_id']:c['session_id'] for c in manifest['cases']}
    for mouse in mice:
        cases=[c for c in manifest['cases'] if c['mouse_id']==mouse];ids=partition['D_trial_ids'][mouse]
        if len(ids)!=len(set(ids)) or not ids or any(set(ids)&set(c['trial_ids']) for c in cases):raise PermissionError('D_TRIAL_DUPLICATE_OR_C_OVERLAP')
        rows=partition['sessions'][mouse]
        if rows['session_id']!=sessions[mouse] or rows['trial_ids']!=ids or len(rows['conditions'])!=len(ids) or len(rows['orders'])!=len(ids):raise PermissionError('D_CONTEXT_IDENTITY')
        if any(not isinstance(v,int) or not 0<=v<=7 for v in rows['conditions']) or any(not isinstance(v,int) or not 0<=v<=599 for v in rows['orders']):raise PermissionError('D_CONTEXT_RANGE')
        if any(rows['conditions'].count(i)<16 for i in range(8)):raise PermissionError('D_CONDITION_COVERAGE')
    if manifest['synthetic'] is False:
        if animals is None or trials is None:raise PermissionError('ORIGINAL_REAL_METADATA_REQUIRED')
        final=[a for a in animals if a['group']=='final']
        if len(animals)!=26 or [a['mouse_id'] for a in final]!=mice:raise PermissionError('ORIGINAL_REAL_COHORT')
        conditions=sorted({t['condition'] for t in trials})
        for a in final:
            rows=[t for t in trials if t['session_id']==a['session_id'] and t['metadata_admitted'] and t['partition']=='locked_evaluation'];saved=partition['sessions'][a['mouse_id']]
            if [t['trial_id'] for t in rows]!=saved['trial_ids'] or [conditions.index(t['condition']) for t in rows]!=saved['conditions'] or [t['provider_row_index'] for t in rows]!=saved['orders']:raise PermissionError('ORIGINAL_REAL_D_PARTITION')
    return True
