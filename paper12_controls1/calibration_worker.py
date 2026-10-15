"""Native scientific principal: admitted C counts only, no evaluation orchestration."""
import hashlib
import json
from pathlib import Path
import sys

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    data=Path(data);out=Path(output);code=Path(__file__).parent
    def save(name,value):
        with (out/(name+'.json')).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof',proof)
    if not proof['pass']:raise PermissionError('ACTUAL_NATIVE_ROLE_REQUIRED')
    import numpy as np
    from calibration import FIELDS,fit_all,array_hash
    manifest=json.loads((data/'manifest.json').read_text());meta=json.loads((data/'metadata.json').read_text())
    if manifest['group']!='final' or manifest['compartments']!=['C'] or len(manifest['sessions'])!=13:raise PermissionError('THIRTEEN_C_ONLY_INPUT')
    extra={}
    for label,path in manifest.get('denial_probes',{}).items():
        try:
            with open(path,'rb') as f:f.read(1)
            extra[label]=False
        except PermissionError:extra[label]=True
    save('extra_role_denials',extra)
    if not all(extra.values()):raise PermissionError('WORKER_PROTECTED_OBJECT_ACCESS')
    from access_check import denied_open
    checked={name:denied_open(path) for name,path in manifest.get('accesscheck_only_paths',{}).items()}
    save('protected_open_checks_without_reading',checked)
    if not all(checked.values()):raise PermissionError('PROTECTED_D_OPEN_ACCESS_CHECK_FAILED_NO_BYTES_READ')
    if manifest['synthetic']:
        import unittest
        suite=unittest.TestSuite()
        for pattern in ('test_glm.py','test_selection.py','test_calibration.py'):
            suite.addTests(unittest.defaultTestLoader.discover(str(code),pattern=pattern))
        result=unittest.TestResult();suite.run(result)
        save('oracle_tests',{'tests':result.testsRun,'passed':result.wasSuccessful(),'skipped':len(result.skipped),'errors':[str(e) for e in result.errors],'failures':[str(e) for e in result.failures]})
        if not result.wasSuccessful() or result.skipped:raise RuntimeError('SYNTHETIC_ORACLE_GATE')
    def read(s):
        path=data/s['file']
        if Path(s['file']).name!=s['file'] or hashlib.sha256(path.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('C_INPUT_HASH')
        with np.load(path,allow_pickle=False) as z:
            if set(z.files)!=FIELDS:raise PermissionError('C_ONLY_EXACT_SCHEMA_REQUIRED')
            return {k:z[k] for k in FIELDS}
    metadata={(z['session_id'],z['unit_id']):z for z in meta};done={}
    def checkpoint(arrays):
        for name,value in arrays.items():
            h=array_hash(value)
            if done.get(name)==h:continue
            # Bounded filename avoids legacy Windows MAX_PATH for long native job roots.
            target=out/('ck_'+hashlib.sha256((name+'|'+h).encode()).hexdigest()[:32]+'.npy')
            if not target.exists():
                with target.open('xb') as f:np.save(f,value,allow_pickle=False)
            done[name]=h
    try:
        arrays,report=fit_all(manifest['sessions'],read,metadata,save,checkpoint)
    except Exception as exc:
        save('calibration_failure',{'type':type(exc).__name__,'message':str(exc),'preserved_array_checkpoints':len(done),'C_only':True,'D_loaded':False})
        save('gate_result',{'gate':'FAIL','C_only':True,'D_loaded':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
        raise
    with (out/'complete_states.npz').open('xb') as f:np.savez(f,**arrays)
    report.update(state_file='complete_states.npz',state_sha256=hashlib.sha256((out/'complete_states.npz').read_bytes()).hexdigest(),
        input_manifest_sha256=hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest(),synthetic=manifest['synthetic'],
        metadata_sha256=hashlib.sha256((data/'metadata.json').read_bytes()).hexdigest())
    save('calibration_states',report)
    # Roundtrip all states without an additional fit.
    with np.load(out/'complete_states.npz',allow_pickle=False) as loaded:
        if set(loaded.files)!=set(arrays) or any(not np.array_equal(loaded[k],v) for k,v in arrays.items()):raise RuntimeError('FULL_STATE_ROUNDTRIP')
    save('gate_result',{'gate':'PASS','mice':13,'cases':len(report['cases']),'paired_counts':report['paired_counts'],
        'new_GLM_unit_attempts':report['new_GLM_unit_attempts'],'full_state_sha256':report['state_sha256'],'C_only':True,'D_loaded':False,
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'synthetic':manifest['synthetic']})
if __name__=='__main__':main()
