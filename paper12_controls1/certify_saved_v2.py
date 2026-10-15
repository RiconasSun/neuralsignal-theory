"""Fresh native v2 sealing/oracles for saved successful synthetic fits; zero new fits."""
import ast
import shutil
import sys
import study as r
from native import security,prepare_job,launch
from run_synthetic_calibration import science_code
from state_manifest import create
from release_control import digest,canonical

def main():
    attempt=sys.argv[1];prior_path=sys.argv[2]
    if not attempt.isdecimal():raise ValueError('ATTEMPT_ID')
    r.verify();prior=r.load(r.HERE/prior_path);original=r.HERE/prior['state_output_directory'];oldjob=r.HERE/prior['job']
    if prior['receipt']['exit_code']!=0 or prior['receipt']['profile_cleanup_hresult']!='0x00000000' or prior['gate']['gate']!='PASS':raise ValueError('SUCCESSFUL_SAVED_NATIVE_FITS_REQUIRED')
    def functions(path):return {n.name:n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
    old=functions(oldjob/'exports/code/calibration.py');new=functions(r.HERE/'calibration.py');parity={}
    for name in ('certificate','fit_n','validate_arrays','array_hash','fit_all'):
        node=new[name]
        if name=='fit_all':
            for call in ast.walk(node):
                if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='coverage':call.args=call.args[:3]
        before=ast.dump(old[name],include_attributes=False);after=ast.dump(node,include_attributes=False)
        if before!=after:raise PermissionError('SAVED_FIT_MATH_CHANGED:'+name)
        parity[name]=digest(after.encode())
    a=security();job=prepare_job('saved_v2_'+attempt);data=job/'exports/saved';manifest=create(original,data)
    r.save(data/'prior_execution.json',{'original_gate':prior['gate'],'original_oracles':r.load(original/'oracle_tests.json'),
        'original_role':r.load(original/'role_proof.json'),'original_launch':prior['receipt'],'math_AST_parity':parity})
    code=job/'exports/code';science_code(code)
    shutil.copy2(r.HERE/'saved_v2_worker.py',code/'worker.py');shutil.copy2(r.HERE/'release_control.py',code/'release_control.py')
    a.protect(data);a.protect(code)
    r.save(r.HERE/('saved_v2_execution_registration_'+attempt+'.json'),{'before_execution':True,'utc':r.datetime.now(r.timezone.utc).isoformat(),
        'prior_result':prior_path,'prior_result_sha256':r.sha(r.HERE/prior_path),'source_sha256':{p.name:r.sha(p) for p in r.HERE.glob('*.py')},
        'code_sha256':{p.name:r.sha(p) for p in code.iterdir()},'C_manifest_sha256':digest(canonical(manifest)),
        'registration':'RETROSPECTIVE_SAVED_SYNTHETIC','unchanged_fitting_AST_sha256':parity,'saved_cohort_refits':0,'synthetic_oracle_model_fits':6,'real_C_D_access':False})
    receipt,gate=launch('certificate',job,data,code)
    r.save(r.HERE/('results/saved_v2_'+attempt+'.json'),{'gate':prior['gate'],'state_output_directory':prior['state_output_directory'],
        'certificate_receipt':receipt,'certificate_gate':gate,'certificate_job':str(job.relative_to(r.HERE)),
        'C_manifest_sha256':digest(canonical(manifest)),'full_state_sha256':manifest['artifact_sha256']['complete_states.npz'],
        'prior_result':prior_path,'saved_cohort_refits':0,'synthetic_oracle_model_fits':6,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
    if receipt['exit_code']!=0 or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000' or not gate or gate['gate']!='PASS':raise RuntimeError('NATIVE_SAVED_V2_GATE')
    print({'saved_v2_certificate':'PASS','saved_cohort_refits':0,'synthetic_oracle_model_fits':6,'prospective_roster_oracles':True})
if __name__=='__main__':main()
