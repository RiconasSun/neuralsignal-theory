"""C-only frozen fitting. No final-evaluation loader, scoring or release API."""
import hashlib
import time
import numpy as np
from scipy.optimize import minimize
from glm import raw,scale,transform,MODELS,obj,independent_ad
from accepted_fit import accepted_fit,original_pg
from baseline_fit import objective
from offset_math import features
from selection import views

SEEDS=(11,23,37)
OPTIONS=dict(maxiter=2000,maxfun=80000,ftol=1e-10,gtol=1e-5)
MANDATORY=('primary','matched16','rate_matched','boundary20','boundary40')
FIELDS={'CA1_C','DG_C','CA1_unit_ids','DG_unit_ids','conditions_C','orders_C','trial_ids_C'}

def array_hash(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

def validate_arrays(z,session):
    if set(z)!=FIELDS:raise PermissionError('C_ONLY_EXACT_SCHEMA_REQUIRED')
    c=np.asarray(z['conditions_C']);o=np.asarray(z['orders_C']);ids=np.asarray(z['trial_ids_C'])
    if c.ndim!=1 or o.shape!=c.shape or ids.shape!=c.shape or c.dtype.kind not in 'iu' or o.dtype.kind not in 'iu':raise ValueError('C_CONTEXT')
    if np.any((c<0)|(c>7)) or np.any((o<0)|(o>599)) or len(set(ids.tolist()))!=len(ids):raise ValueError('C_CONTEXT')
    if ids.tolist()!=session['trial_ids']['C'] or min(np.bincount(c,minlength=8))<24:raise ValueError('C_FROZEN_TRIAL_MASK')
    for region in ('CA1','DG'):
        y=np.asarray(z[region+'_C']);u=np.asarray(z[region+'_unit_ids']).tolist()
        if u!=session['unit_ids'][region] or len(u)!=32 or len(set(u))!=32:raise ValueError('C_PRIMARY_MATCHED32_REQUIRED')
        if y.shape!=(len(c),20,32) or not np.isfinite(y).all() or np.any(y<0) or np.any(y!=np.floor(y)):raise ValueError('C_COUNTS')
    return True

def coverage(sessions,read,metadata,emit=lambda name,value:None):
    result={};counts={v:0 for v in MANDATORY};roster=[]
    if len(sessions)!=13 or len({s['mouse_id'] for s in sessions})!=13:raise ValueError('THIRTEEN_FINAL_MICE')
    for s in sessions:
        z=read(s);validate_arrays(z,s)
        md={k:[metadata[(s['session_id'],uid)] for uid in s['unit_ids'][k]] for k in ('CA1','DG')}
        rates={k:(z[k+'_C'].mean(axis=(0,1))/.1).tolist() for k in ('CA1','DG')}
        vv=views(rates['CA1'],rates['DG'],md)
        unavailable={name:'FEWER_THAN_FIVE_PAIRED_UNITS' for name,v in vv.items() if min(map(len,v.values()))<5}
        probes=sorted({str(m['probe_id']) for rows in md.values() for m in rows},key=int)
        for p in probes:
            for name in ('leave_probe_'+p,'shared_probe_'+p):
                if name not in vv:unavailable[name]='FROZEN_PROBE_SELECTION_NOT_ELIGIBLE'
        vv={name:v for name,v in vv.items() if min(map(len,v.values()))>=5}
        for name in MANDATORY:
            if name in vv:
                if len(vv[name]['CA1'])!=len(vv[name]['DG']):raise ValueError('UNMATCHED_VIEW')
                if name=='primary' and len(vv[name]['CA1'])!=32:raise ValueError('C_PRIMARY_MATCHED32_REQUIRED')
                if name=='matched16' and len(vv[name]['CA1'])!=16:raise ValueError('MATCHED16_REQUIRED')
                counts[name]+=1
        result[s['session_id']]=vv
        roster.append({'session_id':s['session_id'],'mouse_id':s['mouse_id'],'unit_ids':s['unit_ids'],
            'trial_ids_C':s['trial_ids']['C'],'rates_C_Hz':rates,'metadata':md,'views':vv,'unavailable_views':unavailable})
    emit('private_prefit_roster',{'registration':'PROSPECTIVE_BEFORE_ANY_OPTIMIZER','sessions':roster,'paired_counts':counts})
    if any(v<8 for v in counts.values()):raise ValueError('MANDATORY_VIEW_MINIMUM_EIGHT:'+str(counts))
    return result,counts

def certificate(w,x,y):
    # Exact original flattened, summed per-unit objective; independent derivative primitives.
    f,g=objective(w.ravel(),y,x,.1,'per_unit_exposure')
    ff=0.;gg=[]
    for u in range(y.shape[-1]):
        af,ag=independent_ad(w[u],x[:,:,u,:].reshape(-1,x.shape[-1]),y[:,:,u].ravel());ff+=af;gg.append(ag)
    ag=np.asarray(gg).ravel();err=float(np.max(np.abs(g-ag)/np.maximum(1,np.maximum(np.abs(g),np.abs(ag)))))
    value={'objective':f,'AD_objective_error':abs(f-ff),'AD_scaled_error':err,'original_PG':original_pg(w.ravel(),g),
           'AD_original_PG':original_pg(w.ravel(),ag),'bounds':bool(np.all(np.abs(w)<=8)),
           'finite':bool(np.isfinite(w).all() and np.isfinite([f,ff]).all())}
    value['passed']=bool(value['finite'] and value['bounds'] and value['original_PG']<=.001 and value['AD_original_PG']<=.001 and err<=1e-5 and abs(f-ff)<=1e-10)
    return value

def fit_n(y,c,o,case,sink,arrays,deadline,checkpoint=lambda arrays:None):
    x=features(y,c,o);weights=[]
    for seed in SEEDS:
        key=case+'_N_seed'+str(seed);initial=np.random.default_rng(seed).normal(0,.05,y.shape[-1]*29)
        history=[];arrays[key+'_initial']=initial.copy()
        sink(key+'_started',{'seed':seed,'initial_sha256':array_hash(initial),'options':OPTIONS,'shape':list(y.shape),'normalization':'per_unit_exposure'})
        checkpoint({key+'_initial':initial})
        def loss(theta,*args):
            if time.monotonic()>deadline:raise RuntimeError('REGISTERED_WALL_LIMIT')
            f,g=objective(theta,*args);history.append({'objective':f,'original_PG':original_pg(theta,g)})
            return f,g
        try:
            result=minimize(loss,initial,args=(y,x,.1,'per_unit_exposure'),jac=True,method='L-BFGS-B',bounds=[(-8.,8.)]*initial.size,options=OPTIONS)
            w=result.x.reshape(y.shape[-1],29);arrays[key]=w.copy();cert=certificate(w,x,y)
            cert.update(seed=seed,optimizer_success=bool(result.success),optimizer_message=str(result.message),iterations=int(result.nit),objective_calls=int(result.nfev),history=history)
            cert['passed']=bool(cert['passed'] and result.success and result.nit<=2000 and result.nfev<=80000)
            sink(key,cert)
            checkpoint({key:w})
        except Exception as exc:
            sink(key+'_exception',{'error_type':type(exc).__name__,'message':str(exc),'history':history,'initial_sha256':array_hash(initial)})
            raise
        if not cert['passed']:raise RuntimeError('N_SEED_NUMERICAL_FAILURE:'+key)
        weights.append(w)
    mean=np.mean(weights,axis=0);cert=certificate(mean,x,y);sink(case+'_N_mean',cert)
    if not cert['passed']:raise RuntimeError('N_MEAN_NUMERICAL_FAILURE:'+case)
    return mean

def fit_all(sessions,read,metadata,sink,checkpoint,deadline=None):
    deadline=time.monotonic()+43200 if deadline is None else deadline
    selections,counts=coverage(sessions,read,metadata,sink) # durable roster before any optimizer call
    sink('coverage',{'paired_counts':counts,'sessions':list(selections),'view_sizes':{s:{v:{k:len(ids) for k,ids in z.items()} for v,z in vv.items()} for s,vv in selections.items()}})
    arrays={};cases=[];attempts=0
    for session in sessions:
        z=read(session);sid=session['session_id'];primary={}
        for region in ('CA1','DG'):
            yy=z[region+'_C'].astype(float);c=z['conditions_C'];o=z['orders_C'];case=sid+'_'+region
            mean=fit_n(yy,c,o,case,sink,arrays,deadline,checkpoint);checkpoint(arrays)
            primary[region]={'N':mean}
        for view,selection in selections[sid].items():
            for region in ('CA1','DG'):
                if time.monotonic()>deadline:raise RuntimeError('REGISTERED_WALL_LIMIT')
                ids=selection[region];y=z[region+'_C'][:,:,ids].astype(float);x0=raw(y,z['conditions_C'],z['orders_C']);ms=scale(x0);x=transform(x0,ms)
                case=sid+'_'+region+'_'+view;reuse={}
                arrays[case+'_mean']=ms[0];arrays[case+'_scale']=ms[1]
                if view!='primary':
                    parent=sid+'_'+region+'_primary'
                    for a,b in ((ms[0][:,:34],arrays[parent+'_mean'][ids,:34]),(ms[1][:,:34],arrays[parent+'_scale'][ids,:34])):
                        if not np.array_equal(a,b):raise RuntimeError('REUSE_SCALER_DRIFT')
                for name,columns in MODELS.items():
                    key=case+'_'+name
                    if name=='N' or (view!='primary' and name in ('O','NH')):
                        w=np.zeros((len(ids),39)) if name=='N' else primary[region][name][ids].copy()
                        if name=='N':w[:,:29]=primary[region]['N'][ids]
                        certs=[]
                        for u in range(len(ids)):
                            f,g=obj(w[u,columns],x[:,:,u,columns].reshape(-1,len(columns)),y[:,:,u].ravel());af,ag=independent_ad(w[u,columns],x[:,:,u,columns].reshape(-1,len(columns)),y[:,:,u].ravel())
                            err=float(np.max(np.abs(g-ag)/np.maximum(1,np.maximum(np.abs(g),np.abs(ag)))))
                            ok=original_pg(w[u,columns],g)<=.001 and original_pg(w[u,columns],ag)<=.001 and err<=1e-5 and abs(f-af)<=1e-10 and np.isfinite(w).all() and np.all(np.abs(w)<=8)
                            certs.append({'unit':u,'original_PG':original_pg(w[u,columns],g),'AD_original_PG':original_pg(w[u,columns],ag),'AD_scaled_error':err,'AD_objective_error':abs(f-af),'passed':bool(ok)})
                        sink(key,{'reused':True,'passed':all(q['passed'] for q in certs),'certificates':certs})
                        if not all(q['passed'] for q in certs):raise RuntimeError('REUSED_STATE_CERTIFICATE')
                        reuse[name]='N all3seed coefficient mean' if name=='N' else 'Exact primary rows with identical target/features/scaler columns'
                    else:
                        w=np.zeros((len(ids),39));records=[]
                        for u in range(len(ids)):
                            attempts+=1;tag=key+'_unit'+str(u)
                            sink(tag+'_started',{'attempt':attempts,'unit_id':session['unit_ids'][region][ids[u]],'columns':columns})
                            try:
                                theta,record=accepted_fit(x[:,:,u,columns].reshape(-1,len(columns)),y[:,:,u].ravel());w[u,columns]=theta
                                record.update(attempt=attempts,unit_id=session['unit_ids'][region][ids[u]])
                                sink(tag,record);checkpoint({tag:theta})
                            except Exception as exc:
                                sink(tag+'_exception',{'error_type':type(exc).__name__,'message':str(exc),'attempt':attempts});checkpoint(arrays);raise
                            records.append(record)
                            if not record['passed']:raise RuntimeError('GLM_NUMERICAL_FAILURE:'+tag)
                        sink(key,{'passed':True,'records':records,'coefficient_sha256':array_hash(w)})
                        arrays.pop(key+'_partial',None)
                    arrays[key]=w.copy()
                    if view=='primary' and name!='N':primary[region][name]=w.copy()
                record={'case':case,'mouse_id':session['mouse_id'],'session_id':sid,'region':region,'view':view,
                    'unit_ids':[session['unit_ids'][region][i] for i in ids],'selection':ids,'C_trial_ids':session['trial_ids']['C'],
                    'models':list(MODELS),'shape':[len(y),20,len(ids)],'reuse':reuse,
                    'arrays':{name:{'key':case+'_'+name,'shape':list(arrays[case+'_'+name].shape),'sha256':array_hash(arrays[case+'_'+name])} for name in (*MODELS,'mean','scale')}}
                cases.append(record);sink(case+'_state',record);checkpoint(arrays)
    return arrays,{'cases':cases,'paired_counts':counts,'new_GLM_unit_attempts':attempts,'complete':True,'C_only':True,'D_loaded':False}
