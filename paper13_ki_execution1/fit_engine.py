"""Append-only bounded fitting and coordinate diagnostics, synthetic until gates pass."""
import datetime
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from . import models as m
from . import independent_ad as ad

class ScientificStop(RuntimeError):pass

def digest_arrays(*arrays):
    h=hashlib.sha256()
    for a in arrays:
        x=np.asarray(a);h.update(str((x.shape,x.dtype.str)).encode());h.update(x.tobytes())
    return h.hexdigest()

def derivatives(kind,w,data,ridge,*,p=None,offset=None,spend=lambda:None):
    y=data['y']
    if kind=='HMM':
        def objective(z):spend();return m.hmm_eval(z,y,offset,p,ridge,gradient=False)
        spend()
        value,analytic=m.hmm_eval(w,y,offset,p,ridge)
        spend();spend()
        av,automatic=ad.hmm(w,y,offset,p,ridge)
    else:
        x=data['x'];penalize=kind=='C'
        def objective(z):spend();return m.glm_eval(z,x,y,ridge,offset=offset,penalize_intercept=penalize,gradient=False)
        spend()
        value,analytic=m.glm_eval(w,x,y,ridge,offset=offset,penalize_intercept=penalize)
        spend();spend()
        av,automatic=ad.glm(w,x,y,ridge,offset=offset,penalize_intercept=penalize)
    fixed=m.finite_difference(objective,w,1e-4)
    ae=m.gradient_errors(analytic,automatic);fe=m.gradient_errors(analytic,fixed)
    scan={};coords=sorted(set([0,len(w)//2,len(w)-1]))
    # All coordinates at gate step1e-4; other diagnostic steps use the same three
    # prospectively fixed coordinate probes, never a favorable selected step.
    for step in [1e-2,1e-3,1e-4,1e-5,1e-6]:
        errs=[]
        for j in coords:
            def f(a):
                z=w.copy();z[j]=a[0];return objective(z)
            numerical=m.finite_difference(f,np.array([w[j]]),step)[0]
            errs.append(float(abs(numerical-analytic[j])/max(1,abs(numerical),abs(analytic[j]))))
        scan[str(step)]={'coordinates':coords,'relative_errors':errs}
    passed=all(np.isfinite(a).all() for a in [value,av,analytic,automatic,fixed]) and abs(value-av)<=1e-10*max(1,abs(value)) and ae['max_relative']<=1e-5 and fe['max_relative']<=1e-5
    return {'pass':bool(passed),'objective':float(value),'independent_AD_objective':float(av),'theta':w.tolist(),'analytical_gradient':analytic.tolist(),'independent_AD_gradient':automatic.tolist(),'fixed_FD_gradient':fixed.tolist(),'AD_error':ae,'fixed_FD_error':fe,'diagnostic_scan':scan,'numerical_gate_step':1e-4}

def fit(path,kind,data,ridge,initial,*,p=None,offset=None,identity=None,source_hash=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    identity=identity or {}
    if kind not in {'GLM','HMM','C'}:raise ScientificStop('Unknown scientific model family')
    if not isinstance(identity,dict):raise ScientificStop('Scientific identity must be a canonical mapping')
    if identity.get('real_data') and (not source_hash or any(k not in identity for k in ['mouse_id','partition','configuration','unit_ids_sha256','epochs_sha256','scaler_sha256','protocol_sha256'])):
        raise ScientificStop('Real scientific fit identity incomplete; no attempt or cached lookup allowed')
    try:
        y=data['y'];w=np.asarray(initial,dtype=float)
        data_hash=digest_arrays(y,data.get('x',np.array([])),offset if offset is not None else np.array([]))
        request={'kind':kind,'ridge':float(ridge),'p':None if p is None else float(p),'source_hash':source_hash,'identity':identity,
                 'data_sha256':data_hash,'initial_sha256':digest_arrays(w),'offset_present':offset is not None}
        request_hash=hashlib.sha256(json.dumps(request,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    except (KeyError,ValueError,TypeError) as exc:raise ScientificStop('Incomplete/noncanonical fit request; cached PASS cannot be trusted') from exc
    if path.exists():
        old=json.loads(path.read_text())
        if old['status']!='PASS':raise ScientificStop('Preserved required fit failure; retry forbidden')
        if old.get('full_request_sha256')!=request_hash or old.get('full_request')!=request:raise ScientificStop('Saved fit request mismatch; no cached result substitution or implicit refitting')
        return old
    record={'identity':identity,'kind':kind,'ridge':ridge,'p':p,'source_hash':source_hash,'data_sha256':data_hash,'full_request':request,'full_request_sha256':request_hash,
            'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'STARTED','trajectory':[],'calls':0,'initial':w.tolist(),'real_data':identity.get('real_data',False)}
    # An attempt is durably visible before any optimization. Existing failure or
    # interruption is never silently replaced by another scientific fit.
    with path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(record,indent=2)+'\n')
    def safe(v):
        if isinstance(v,float) and not np.isfinite(v):return str(v)
        if isinstance(v,dict):return {k:safe(x) for k,x in v.items()}
        if isinstance(v,list):return [safe(x) for x in v]
        return v
    def persist():path.write_text(json.dumps(safe(record),indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    def spend():
        if record['calls']>=100000:raise ScientificStop('Registered maxfun budget exhausted')
        record['calls']+=1
    def objective(z):
        spend()
        result=m.hmm_eval(z,y,offset,p,ridge) if kind=='HMM' else m.glm_eval(z,data['x'],y,ridge,offset=offset,penalize_intercept=kind=='C')
        if not np.isfinite(result[0]) or not np.isfinite(result[1]).all():raise ScientificStop('Nonfinite trial objective/gradient')
        return result
    first_iterate=[]
    def callback(z):
        value,g=objective(z)
        if not first_iterate:first_iterate.append(z.copy())
        record['trajectory'].append({'iteration':len(record['trajectory'])+1,'objective':float(value),'PG':m.pg(z,g),'calls':record['calls']})
        with path.with_suffix('.trajectory.jsonl').open('a',encoding='utf8',newline='\n') as f:f.write(json.dumps(record['trajectory'][-1])+'\n')
    try:
        d0=derivatives(kind,w,data,ridge,p=p,offset=offset,spend=spend);record['derivatives']={'initial':d0};persist()
        if not d0['pass']:raise ScientificStop('Initial independent-gradient gate failed')
        r=minimize(objective,w,jac=True,method='L-BFGS-B',bounds=[(-8.,8.)]*len(w),callback=callback,
                   options={'maxiter':2000,'maxfun':100000,'maxls':40,'maxcor':10,'ftol':1e-12,'gtol':1e-5})
        mid=first_iterate[0] if first_iterate else w.copy()
        dm=derivatives(kind,mid,data,ridge,p=p,offset=offset,spend=spend);de=derivatives(kind,r.x,data,ridge,p=p,offset=offset,spend=spend)
        endpoint_pg=m.pg(r.x,r.jac)
        record.update(derivatives={'initial':d0,'intermediate_first_callback':dm,'endpoint':de},theta=r.x.tolist(),objective=float(r.fun),PG=endpoint_pg,iterations=int(r.nit),optimizer_calls=int(r.nfev),optimizer_success=bool(r.success),optimizer_status=int(r.status),termination=str(r.message))
        if not dm['pass'] or not de['pass'] or endpoint_pg>.001 or not np.isfinite(r.fun):raise ScientificStop('Required endpoint/intermediate numerical gate failed')
        record['status']='PASS';record['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();persist();return record
    except Exception as exc:
        record.update(status='FAILED_REQUIRED_GATE',failure=repr(exc),stopped_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());persist()
        raise ScientificStop(str(exc)) from exc
