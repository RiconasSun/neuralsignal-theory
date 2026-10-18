"""Unchanged M1 eleven cases and metadata masks; C-only preparation below."""
import copy
import numpy as np

CASES=[dict(id='S01',units=5),dict(id='S02',units=12),dict(id='S03',units=20),
    dict(id='S04',units=8,delta=.1),dict(id='S05',units=8,warmup=.25,history=.25),
    dict(id='S06',units=8,strict=True),dict(id='S07',units=8,thin=True),
    dict(id='S08',units=8,dilation=.01),dict(id='S09',units=8,dilation=.05),
    dict(id='S10',units=8,rich=True),dict(id='S11',units=5,boundary=True)]


def metadata_case(state,case):
    out=copy.deepcopy(state);tr=out['trials'];n=len(tr);warm=case.get('warmup',.5)
    s=np.array([np.nan if t['stimOn_times'] is None else t['stimOn_times'] for t in tr])
    a=np.array([np.nan if t['intervals_0'] is None else t['intervals_0'] for t in tr])
    z=np.array([np.nan if t['intervals_1'] is None else t['intervals_1'] for t in tr])
    checks={k:np.asarray(v,bool) for k,v in state['check_masks'].items()}
    lo=s-warm;hi=s+.5;support=state['result']['recording_sync_support']
    checks['neural_epoch_inside_trial']=(lo>=a)&(hi<=z)
    checks['recording_sync_support']=(lo>=support[0])&(hi<=support[1])
    nonoverlap=np.ones(n,bool);finite=np.flatnonzero(np.isfinite(s))
    for before,after in zip(finite[:-1],finite[1:]):
        if lo[after]<hi[before]:nonoverlap[[before,after]]=False
    checks['no_overlapping_epoch']=nonoverlap
    sat=np.asarray(state['selected_probe_saturation_session_seconds']).reshape(-1,2).copy()
    dilation=case.get('dilation',0.)
    if len(sat):sat[:,0]-=dilation;sat[:,1]+=dilation
    bad=np.zeros(n,bool)
    for b,e in sat:bad|=(s-1<e)&(hi>b)
    checks['no_known_saturation']=~bad
    out['valid']=np.logical_and.reduce(list(checks.values())).tolist()
    out['check_masks']={k:v.tolist() for k,v in checks.items()}
    out['selected_probe_saturation_session_seconds']=sat.tolist()
    return out

