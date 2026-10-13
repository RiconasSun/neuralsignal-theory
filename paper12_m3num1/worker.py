"""Native diagnosis worker; A-only identity and archive-bound scalar diagnostics."""
import hashlib
import json
from pathlib import Path
import sys


def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:]
    sys.path[:0]=[deps,str(Path(__file__).resolve().parent)]
    from native_analysis_check import check
    output=Path(output)
    def save(name,value):
        with (output/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('ISOLATION_FAILED')
    import unittest
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test_numerical.py')
    test=unittest.TestResult();suite.run(test)
    save('oracle_tests.json',dict(count=test.testsRun,failures=test.failures,errors=test.errors,passed=test.wasSuccessful()))
    if not test.wasSuccessful():raise RuntimeError('ORACLE_FAIL')
    import numpy as np
    from baseline_features import design,training_scaler,transform
    from numerical import run_fit,ORIGINAL
    manifest=json.loads((Path(data)/'manifest.json').read_text())
    if manifest['compartments']!=['A'] or len(manifest['sessions'])!=1:raise PermissionError('DIAGNOSTIC_A_ONLY_REQUIRED')
    session=manifest['sessions'][0];path=Path(data)/session['file']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('INPUT_HASH')
    summary=[]
    with np.load(path,allow_pickle=False) as arrays:
        if any(k.endswith('_B') or k.endswith('_C') or k.endswith('_D') for k in arrays.files):raise PermissionError('FORBIDDEN_COMPARTMENT')
        for region in ('CA1','DG'):
            y=arrays[region+'_A']
            for kind in ('history','population','event','drift','combined'):
                raw=design(y,arrays['conditions_A'],arrays['orders_A'],kind)
                x=transform(raw,training_scaler(raw));del raw
                for ridge in (.001,.01,.1,1.):
                    for seed in (11,23,37):
                        _,record=run_fit(y,x,ridge,seed,ORIGINAL)
                        record.update(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,kind=kind,
                                      trace_origin='prospective_training_only_replay')
                        name=f'{region}_{kind}_{ridge}_{seed}.json';save(name,record)
                        summary.append({k:v for k,v in record.items() if k not in ('objective_history','accepted_iteration_history','conditioning')})
                del x
    valid=len(summary)==120 and all(x['initial_gradient_check']['passed'] and x['terminal_gradient_check']['passed'] for x in summary)
    premature=valid and all('RELATIVE REDUCTION' in x['optimizer_message'] and x['iterations']<500 and x['objective_calls']<20000 and x['projected_gradient']>.001 for x in summary)
    save('diagnosis_summary.json',dict(fits=summary,fit_count=len(summary),oracles_pass=valid,premature_relative_stopping_confirmed=premature,
        original_trajectories_available=False,final_evaluation_access=False,validation_scores_inspected=False))
    save('gate_result.json',dict(gate='PASS' if valid and premature else 'FAIL',phase='training_only_diagnosis',
        scientific_verdict='OPTIMIZER_AMENDMENT_ELIGIBLE' if valid and premature else 'NUMERICAL_INCONCLUSIVE'))
    if not(valid and premature):sys.exit(2)


if __name__=='__main__':main()
