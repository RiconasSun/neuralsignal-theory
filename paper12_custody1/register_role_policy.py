"""Freeze verified native role and extractor source before any real neural read."""
import subprocess
import sys
from datetime import datetime,timezone
import register as r


def main():
    r.verify()
    if (r.HERE/'role_registration.json').exists():raise RuntimeError('ROLE_REGISTRATION_ALREADY_EXISTS')
    cmd=[sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p','test_custody.py','-v']
    run=subprocess.run(cmd,capture_output=True,text=True)
    r.save(r.HERE/'results/functional_gate.json',{'pass':run.returncode==0,'synthetic_only':True,'command':cmd,
        'output':run.stdout+run.stderr,'source_full_session_decoded_by_custodian':False,'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False})
    if run.returncode:raise RuntimeError('FUNCTIONAL_CUSTODY_FAILED')
    proof=r.load(r.HERE/'results/isolation/native_profile_runtime2.json')
    if not proof['mandatory_isolation_pass']:raise RuntimeError('NATIVE_ROLE_NOT_VERIFIED')
    names=['ROLE_POLICY1.json','custodian.py','security.py','native_profile_probe.py','runtime_canary.py','cipher_core.py',
           'custody_core.py','test_custody.py','register_role_policy.py','results/functional_gate.json','results/isolation/native_profile_runtime2.json']
    record={'utc':datetime.now(timezone.utc).isoformat(),'scope':'Prospective native-role implementation binding;no scientific lock or oldfailure amendment',
            'sha256':{name:r.sha(r.HERE/name) for name in names},'source_full_session_decoded_by_custodian':False,
            'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False}
    r.save(r.HERE/'role_registration.json',record,True)
    r.save(r.HERE/'results/access_gate.json',{'gate':'PASS','scope':'Verified synthetic/native custody prerequisite only,not physiological gate',
        'role_registration_sha256':r.sha(r.HERE/'role_registration.json'),'neural_values_read_before_gate':0,'original_M2_reclassified':False})
    print({'gate':'PASS','neural_values_read_before_gate':0,'role_registration_sha256':r.sha(r.HERE/'role_registration.json')})


if __name__=='__main__':main()
