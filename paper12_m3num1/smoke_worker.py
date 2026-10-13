"""Strict complete-roster baseline evaluation under one registered policy."""
import hashlib
import json
from pathlib import Path
import sys


def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:]
    sys.path[:0]=[deps,str(Path(__file__).resolve().parent)]
    output=Path(output)
    def save(name,value):
        with (output/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('NATIVE_ISOLATION_FAIL')
    import unittest
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test_numerical.py')
    test=unittest.TestResult();suite.run(test)
    save('oracle_tests.json',dict(count=test.testsRun,passed=test.wasSuccessful(),failures=test.failures,errors=test.errors))
    if not test.wasSuccessful():raise RuntimeError('NUMERICAL_ORACLE_FAIL')
    import numpy as np
    from baseline_features import design,training_scaler,transform,likelihood_gradient
    from baseline_fit import stationary
    from numerical import run_fit,REPAIRED
    manifest=json.loads((Path(data)/'manifest.json').read_text())
    if manifest['compartments']!=['A','B'] or manifest['group']!='development':raise PermissionError('DEV_AB_ONLY')
    results=[]
    for session in manifest['sessions']:
        path=Path(data)/session['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('INPUT_HASH_CHANGED')
        with np.load(path,allow_pickle=False) as z:
            for region in ('CA1','DG'):
                y=z[region+'_A'];valid=z[region+'_B']
                for kind in ('stationary','history','population','event','drift','combined'):
                    raw=design(y,z['conditions_A'],z['orders_A'],kind);scaler=training_scaler(raw)
                    x=transform(raw,scaler);del raw
                    vx=transform(design(valid,z['conditions_B'],z['orders_B'],kind),scaler)
                    for ridge in ([None] if kind=='stationary' else [.001,.01,.1,1.]):
                        for seed in (11,23,37):
                            if kind=='stationary':record=stationary(y,valid,seed)
                            else:
                                theta,record=run_fit(y,x,ridge,seed,REPAIRED,verify_gradient=False)
                                score=likelihood_gradient(theta,valid,vx)[0]/valid.size
                                record.update(validation_LL_nats_per_unit_bin=score,validation_unit_bins=int(valid.size),
                                    converged=bool(record['converged'] and np.isfinite(score)))
                            record.update(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,
                                kind=kind,ridge=ridge,seed=seed,data_sha256=session['sha256'],family='baseline',
                                ridge_normalization='per_unit_exposure')
                            save(f"{session['session_id']}_{region}_{kind}_{ridge}_{seed}.json",record)
                            results.append(record)
                    del x,vx
        count=len(results);passed=all(r['converged'] for r in results)
        stage=dict(gate='PASS' if passed else 'FAIL',completed_fit_count=count,expected_fit_count=126*len(manifest['sessions']),
            converged_fit_count=sum(r['converged'] for r in results),mouse_count=count//126,
            scientific_verdict='BASELINES_EXECUTED' if passed else 'NUMERICAL_INCONCLUSIVE',
            final_evaluation_access=False,preferred_regime_claim=False)
        save(f"stage_{count//126}.json",stage)
        if not passed:
            save('gate_result.json',stage);sys.exit(2)
    save('gate_result.json',stage)


if __name__=='__main__':main()
