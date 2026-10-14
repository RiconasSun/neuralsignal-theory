"""All preregistered nested GLM cases; one attempt and stop on critical failure."""
import hashlib
import json
from pathlib import Path
import sys
import time
def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    out=Path(output);code=Path(__file__).parent;data=Path(data)
    def load(p):return json.loads(Path(p).read_text())
    def save(name,v):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('NATIVE_ROLE')
    import unittest
    tests=unittest.TestResult();unittest.defaultTestLoader.discover(str(code),pattern='test_*.py').run(tests)
    save('oracle_tests.json',{'count':tests.testsRun,'passed':tests.wasSuccessful(),'skips':len(tests.skipped),'errors':str(tests.errors),'failures':str(tests.failures)})
    if not tests.wasSuccessful() or tests.testsRun!=17 or tests.skipped:raise RuntimeError('ORACLE_GATE')
    import numpy as np
    from scipy.special import gammaln
    from glm import raw,scale,transform,MODELS,obj,fit,pg,score,gains,independent_ad
    from selection import views
    manifest=load(data/'manifest.json');meta=load(code/'development_metadata.json');offsets=np.load(code/'offset_states.npz',allow_pickle=False)
    rows=[];arrays={};attempts=0;case_count=0;start=time.perf_counter()
    for s in manifest['sessions']:
        p=data/s['file']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('DATA_HASH')
        with np.load(p,allow_pickle=False) as z:
            md={k:[next(m for m in meta if m['unit_id']==str(uid)) for uid in z[k+'_unit_ids']] for k in ('CA1','DG')}
            rates={k:z[k+'_A'].mean(axis=(0,1))/.1 for k in md};vvs=views(rates['CA1'],rates['DG'],md)
            primary={}
            for view,selection in vvs.items():
                if min(map(len,selection.values()))<5:continue
                for region in ('CA1','DG'):
                    ids=selection[region];y=z[region+'_A'][:,:,ids].astype(float);v=z[region+'_B'][:,:,ids].astype(float)
                    xa=raw(y,z['conditions_A'],z['orders_A']);ms=scale(xa);xa=transform(xa,ms);xb=transform(raw(v,z['conditions_B'],z['orders_B']),ms)
                    weights={};scores={};references={};case=s['session_id']+'_'+region+'_'+view
                    for name,indices in MODELS.items():
                        if name=='N':
                            mean=np.mean([offsets[s['session_id']+'_'+region+'_'+str(seed)] for seed in (11,23,37)],axis=0)[ids]
                            w=np.zeros((len(ids),39));w[:,:29]=mean;references[name]='Frozen mean of all three converged offset states'
                            maxpg=0.;maxad=0.
                            for u in range(len(ids)):
                                x=xa[:,:,u,:29].reshape(-1,29);yy=y[:,:,u].ravel();f,g=obj(mean[u],x,yy);af,ag=independent_ad(mean[u],x,yy)
                                maxpg=max(maxpg,pg(mean[u],g));maxad=max(maxad,float(np.max(np.abs(g-ag)/np.maximum(1,np.maximum(np.abs(g),np.abs(ag))))))
                                if maxpg>.001 or maxad>1e-5 or abs(f-af)>1e-10:raise RuntimeError('REUSED_OFFSET_OBJECTIVE_NUMERICAL_GATE')
                            save(case+'_N_reuse.json',{'case':case,'model':name,'reused':True,'original_seed_fits':3,'PG':maxpg,'AD_scaled_error':maxad,'passed':True,'final_access':False})
                        elif view!='primary' and name in ('O','NH'):
                            w=primary[region][name][ids].copy();references[name]='Exact selected primary coefficient rows; unchanged covariates and scaler'
                        else:
                            w=np.zeros((len(ids),39));records=[]
                            for u in range(len(ids)):
                                if time.perf_counter()-start>=43200:raise RuntimeError('REGISTERED_PHASE_WALL_LIMIT')
                                attempts+=1;theta,record=fit(xa[:,:,u,indices].reshape(-1,len(indices)),y[:,:,u].ravel());record.update(unit_id=str(z[region+'_unit_ids'][ids[u]]),attempt=attempts)
                                records.append(record);w[u,indices]=theta
                                if not record['passed']:
                                    save(case+'_'+name+'_FAIL.json',{'case':case,'model':name,'records':records,'failed_unit':u,'new_unit_fit_attempts':attempts,'new_completed_model_cases':case_count,'scientific_stop':True,'final_access':False});raise RuntimeError('REGISTERED_NEW_GLM_NUMERICAL_GATE')
                            case_count+=1;save(case+'_'+name+'_fit.json',{'case':case,'model':name,'new_fit':True,'records':records,'coefficient_sha256':hashlib.sha256(np.ascontiguousarray(w).tobytes()).hexdigest(),'passed':True,'final_access':False})
                        weights[name]=w;scores[name]=score(v,xb,w)
                    eta=np.log(y.mean(axis=(0,1)));scores['stationary']=float(np.sum(v*eta-np.exp(eta)-gammaln(v+1))/v.size)
                    gg=gains(scores);gg['total']=scores['F']-scores['stationary']
                    row={'mouse_id':s['mouse_id'],'session_id':s['session_id'],'region':region,'view':view,'units':len(ids),'A_trials':len(y),'B_trials':len(v),'B_unit_bins':int(v.size),'scores':scores,'gains':gg,'reuse':references,'unit_ids':[str(z[region+'_unit_ids'][i]) for i in ids]};rows.append(row)
                    save(case+'_scores.json',row)
                    if view=='primary':
                        primary[region]=weights
                        arrays[s['session_id']+'_'+region+'_mean']=ms[0];arrays[s['session_id']+'_'+region+'_scale']=ms[1]
                        for name,w in weights.items():arrays[s['session_id']+'_'+region+'_'+name]=w
            save('progress_'+s['session_id']+'.json',{'completed_mice':len({r['mouse_id'] for r in rows}),'new_model_cases':case_count,'new_unit_fit_attempts':attempts,'elapsed_seconds':time.perf_counter()-start,'final_access':False})
    np.savez(out/'primary_states.npz',**arrays)
    save('scientific_scores.json',{'rows':rows,'new_model_cases':case_count,'new_unit_fit_attempts':attempts,'final_access':False})
    save('gate_result.json',{'gate':'PASS','completed_mice':13,'new_model_cases':case_count,'new_unit_fit_attempts':attempts,'all_new_fits_passed':True,'primary_states_sha256':hashlib.sha256((out/'primary_states.npz').read_bytes()).hexdigest(),'elapsed_seconds':time.perf_counter()-start,'final_access':False})
if __name__=='__main__':
    try:main()
    except Exception as e:
        import traceback
        with (Path(sys.argv[3])/'failure.json').open('x',encoding='utf-8') as f:json.dump({'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'scientific_stop':True,'final_access':False},f,indent=2)
        raise
