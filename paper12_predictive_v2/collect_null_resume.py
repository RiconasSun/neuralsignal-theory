"""Merge exact saved checkpoints and complete isolated-role results, no new scores."""
import shutil
import study as r
def main():
    reg=r.load(r.HERE/'null_resume_registration.json');target=r.HERE/'results/nulls_complete/native';target.mkdir(parents=True,exist_ok=False);cases={};proofs=[];invariants=6*999
    for name,digest in reg['completed_case_sha256'].items():
        p=r.HERE/'results/nulls/native'/name
        if r.sha(p)!=digest:raise RuntimeError('CHECKPOINT_CHANGED')
        shutil.copy2(p,target/name);cases[name]=digest
    for job in reg['jobs']:
        here=r.HERE/'jobs'/job['job'];receipt=r.load(here/'results/nulls_launch_receipt.json');gate=r.load(here/'results/nulls/native/gate_result.json');proof=r.load(here/'results/nulls/native/role_proof.json')
        if receipt['exit_code']!=0 or receipt['timed_out'] or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000' or gate['gate']!='PASS' or not proof['pass'] or proof['capability_count']!=0:raise RuntimeError('JOB_NATIVE_GATE')
        if gate['cases']!=len(job['sessions'])*8 or gate['new_fits']!=0:raise RuntimeError('EXACT_JOB_CASES')
        invariants+=gate['count_preservation_checks'];proofs.append({'job':job['job'],'receipt_sha256':r.sha(here/'results/nulls_launch_receipt.json'),'proof_sha256':r.sha(here/'results/nulls/native/role_proof.json'),'gate_sha256':r.sha(here/'results/nulls/native/gate_result.json')})
        for p in (here/'results/nulls/native').glob('*.json'):
            if p.stem[-2:] not in ('_T','_S','_B','_O'):continue
            if p.name in cases:raise RuntimeError('NO_DUPLICATE_COMPLETED_NULLS')
            shutil.copy2(p,target/p.name);cases[p.name]=r.sha(p)
    if len(cases)!=104 or invariants!=26*999:raise RuntimeError('ALL_REGISTERED_NULLS_REQUIRED')
    r.save(target/'gate_result.json',{'gate':'PASS','type':'Exact checkpoint plus three native job aggregate, not a synthetic native receipt','cases':104,'replicates_per_case':999,'null_evaluations':104*999,'count_preservation_checks':invariants,'new_fits':0,'final_access':False,'case_sha256':cases,'native_jobs':proofs,'initial_failed_native_receipt_sha256':reg['failed_native_receipt_sha256']})
    print('ALL_REGISTERED_NULLS_COMPLETE',len(cases))
if __name__=='__main__':main()
