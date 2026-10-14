"""All four registered 999-replicate fixed-predictor falsification suites."""
import hashlib
import json
from pathlib import Path
import sys
import time
def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    code=Path(__file__).parent;out=Path(output);data=Path(data)
    def save(name,v):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('NATIVE_ROLE')
    import unittest
    tests=unittest.TestResult();unittest.defaultTestLoader.discover(str(code),pattern='test_nulls.py').run(tests)
    save('oracle_tests.json',{'count':tests.testsRun,'passed':tests.wasSuccessful(),'skips':len(tests.skipped),'errors':str(tests.errors),'failures':str(tests.failures)})
    if not tests.wasSuccessful() or tests.testsRun!=5 or tests.skipped:raise RuntimeError('NULL_ORACLE_GATE')
    import numpy as np
    from nulls import NAMES,eta,get_gains,temporal,permute_labels,rng
    manifest=json.loads((data/'manifest.json').read_text());states=np.load(code/'primary_states.npz',allow_pickle=False);start=time.perf_counter();cases=0;invariants=0
    for s in manifest['sessions']:
        p=data/s['file']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('AB_HASH')
        with np.load(p,allow_pickle=False) as z:
            for region in ('CA1','DG'):
                case=s['session_id']+'_'+region;y=z[region+'_B'].astype(int);c=z['conditions_B'];o=z['orders_B'];ms=(states[case+'_mean'],states[case+'_scale']);w=np.stack([states[case+'_'+n] for n in NAMES]);original=eta(y,c,o,w,ms);observed=get_gains(y,original)
                save(case+'_reference.json',{'mouse_id':s['mouse_id'],'region':region,'gains':observed.tolist(),'B_trials':len(y),'B_unit_bins':int(y.size),'final_access':False})
                for suite in ('T','S','B','O'):
                    values=[]
                    for rep in range(999):
                        if time.perf_counter()-start>=43200:raise RuntimeError('NULL_WALL_LIMIT')
                        random=rng(s['session_id'],region,suite,rep)
                        if suite=='T':
                            changed=temporal(y,original[NAMES.index('N')],random);prediction=eta(changed,c,o,w,ms);invariants+=1
                        else:
                            changed=y;cc,oo,bb=permute_labels(c,o,suite,random);prediction=eta(y,cc,oo,w,ms,bb)
                        values.append(get_gains(changed,prediction).tolist())
                    cases+=1;save(case+'_'+suite+'.json',{'mouse_id':s['mouse_id'],'session_id':s['session_id'],'region':region,'suite':suite,'replicates':999,'gains':values,'observed':observed.tolist(),'fixed_predictors':True,'null_refits':0,'trial_assignment_changed':False,'final_access':False})
        save('progress_'+s['session_id']+'.json',{'completed_cases':cases,'elapsed_seconds':time.perf_counter()-start,'new_fits':0,'final_access':False})
    save('gate_result.json',{'gate':'PASS','suites':4,'cases':cases,'replicates_per_case':999,'null_evaluations':cases*999,'count_preservation_checks':invariants,'new_fits':0,'final_access':False,'elapsed_seconds':time.perf_counter()-start})
if __name__=='__main__':
    try:main()
    except Exception as e:
        import traceback
        with (Path(sys.argv[3])/'failure.json').open('x',encoding='utf-8') as f:json.dump({'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'scientific_stop':True,'final_access':False},f,indent=2)
        raise
