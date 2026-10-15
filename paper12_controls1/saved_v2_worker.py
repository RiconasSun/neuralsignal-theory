"""Native full-provenance certificate and executable prospective-roster regressions."""
import json
from pathlib import Path
import sys

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    from native_analysis_check import check
    from release_control import read_json,validate_state_manifest,check_numerical_rows
    data=Path(data);out=Path(output)
    def save(name,value):
        with (out/(name+'.json')).open('x') as f:json.dump(value,f,indent=2,allow_nan=False)
    proof=check(source,key,pid,sddl);save('role_proof',proof)
    if not proof['pass']:raise PermissionError('FRESH_NATIVE_ROLE')
    manifest=read_json(data/'C_state_manifest.json');validate_state_manifest(manifest,data)
    prior=read_json(data/'prior_execution.json')
    if prior['original_gate']['gate']!='PASS' or not prior['original_oracles']['passed'] or prior['original_oracles']['tests']!=27 or not prior['original_role']['pass'] or prior['original_launch']['exit_code']!=0:raise RuntimeError('SAVED_NATIVE_SCIENCE_REQUIRED')
    import unittest
    suite=unittest.TestSuite()
    for pattern in ('test_glm.py','test_selection.py','test_calibration.py'):suite.addTests(unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern=pattern))
    result=unittest.TestResult();suite.run(result)
    save('oracle_tests',{'tests':result.testsRun,'passed':result.wasSuccessful(),'skipped':len(result.skipped),'errors':[str(e) for e in result.errors],'failures':[str(e) for e in result.failures]})
    if not result.wasSuccessful() or result.skipped:raise RuntimeError('PROSPECTIVE_ROSTER_AND_MATH_ORACLES')
    case=manifest['cases'][0]
    try:check_numerical_rows({'passed':True,'records':[]},case,'O')
    except PermissionError:pass
    else:raise RuntimeError('EMPTY_CERTIFICATE_ACCEPTED')
    save('gate_result',{'gate':'PASS','scope':'Saved synthetic fits; v2 complete-provenance validation and fresh prospective-roster tests',
        'saved_cohort_refits':0,'synthetic_oracle_model_fits':6,'real_C_D_access':False,'saved_neural_input_partitions_opened':0,'generated_synthetic_oracle_fixtures':True,
        'oracle_tests':result.testsRun,'cases':len(manifest['cases']),'seed_certificates':len(manifest['seed_certificates']),
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
if __name__=='__main__':main()
