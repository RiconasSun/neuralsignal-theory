"""Prospective checkpoint recovery with isolated native role resources."""
import shutil
import launch
import study as r
def main():
    if (r.HERE/'null_resume_registration.json').exists():raise RuntimeError('NO_RESUME_REPLACEMENT')
    a=launch.security();original=r.load(r.HERE/'nulls_execution_registration.json');old=r.load(r.HERE/'results/nulls_launch_receipt.json');failure=r.load(r.HERE/'results/nulls/native/failure.json')
    if old['exit_code']!=1 or failure['type']!='PermissionError':raise RuntimeError('EXPECTED_ENV_FAILURE_ONLY')
    completed={p.name:r.sha(p) for p in (r.HERE/'results/nulls/native').glob('*.json') if p.stem[-2:] in ('_T','_S','_B','_O')}
    if len(completed)!=24:raise RuntimeError('EXACT_CHECKPOINT_24')
    manifest=r.load(r.HERE/'exports/development_AB/manifest.json');remaining=[s['session_id'] for s in manifest['sessions'] if not all(f"{s['session_id']}_{reg}_{suite}.json" in completed for reg in ('CA1','DG') for suite in ('T','S','B','O'))]
    assignments=[remaining[i::3] for i in range(3)]
    jobs=[]
    for i,assigned in enumerate(assignments):
        here=r.HERE/'jobs'/('job'+str(i));exports=here/'exports';exports.mkdir(parents=True)
        shutil.copytree(r.HERE/'exports/development_AB',exports/'development_AB');a.protect(exports/'development_AB')
        shutil.copytree(r.HERE/'exports/runtime',exports/'runtime');a.protect(exports/'runtime');a.prepare(here/'.private')
        for name in ('source_canary.bin','key_canary.bin'):
            p=here/'.private'/name;p.write_bytes(b'SYNTHETIC_ROLE_PROBE_ONLY');a.protect(p)
        code=exports/'code';shutil.copytree(r.HERE/'exports/code_nulls',code)
        for name in ('null_cache.py','test_null_cache.py'):shutil.copy2(r.HERE/name,code/name)
        text=(r.HERE/'null_worker.py').read_text()
        text=text.replace("pattern='test_nulls.py'","pattern='test_null*.py'").replace('tests.testsRun!=5','tests.testsRun!=7')
        text=text.replace('from nulls import NAMES,eta,get_gains,temporal,permute_labels,rng','from nulls import NAMES,eta,get_gains,temporal,permute_labels,rng\n    from null_cache import Cache')
        text=text.replace("start=time.perf_counter();cases=0;invariants=0", "start=time.perf_counter();cases=0;invariants=0\n    assigned=json.loads((code/'assigned_sessions.json').read_text())\n    manifest['sessions']=[s for s in manifest['sessions'] if s['session_id'] in assigned]\n    if [s['session_id'] for s in manifest['sessions']]!=assigned:raise RuntimeError('EXACT_ASSIGNED_SESSIONS')")
        text=text.replace('observed=get_gains(y,original)','observed=get_gains(y,original);cache=Cache(y,c,o,w,ms)')
        text=text.replace('prediction=eta(y,cc,oo,w,ms,bb)','prediction=cache.predict(cc,oo,bb,suite)')
        (code/'worker.py').unlink();(code/'worker.py').write_text(text,encoding='utf-8');r.save(code/'assigned_sessions.json',assigned);a.protect(code)
        for n,d in original['runtime_sha256'].items():
            if r.sha(exports/'runtime'/n)!=d:raise RuntimeError('EXACT_RUNTIME')
        hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
        r.save(here/'execution_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_remaining_nulls':True,'assigned_sessions':assigned,'code_sha256':hashes,'AB_manifest_sha256':original['AB_manifest_sha256'],'runtime_sha256':original['runtime_sha256'],'primary_states_sha256':original['primary_states_sha256'],'replicates':999,'new_fits':0,'final_access':False,'isolated_runtime_and_data':True})
        jobs.append({'job':'job'+str(i),'sessions':assigned,'execution_registration_sha256':r.sha(here/'execution_registration.json')})
    r.save(r.HERE/'null_resume_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_remaining_nulls':True,'base':r.BASE,'failed_native_receipt_sha256':r.sha(r.HERE/'results/nulls_launch_receipt.json'),'failure_sha256':r.sha(r.HERE/'results/nulls/native/failure.json'),'completed_case_sha256':completed,'remaining_sessions':remaining,'jobs':jobs,'concurrency':3,'isolated_native_data_and_runtime':True,'replicates_per_case':999,'total_original_and_remaining_cases':104,'no_repeated_completed_cases':True,'method_settings_seed_trial_assignments_unchanged':True,'cache_equivalence':'S/B/O fixed-outcome histories reused; direct-kernel prediction/score parity<=1e-12 on full synthetic fixtures before resume','classification':'LOCAL_ENV_BROKEN: concurrent native cleanup revoked the shared data ACE, without data corruption or final exposure. Fix resource isolation, preserve failed receipt and completed cases.','source_sha256':{n:r.sha(r.HERE/n) for n in ('prepare_null_resume.py','null_cache.py','test_null_cache.py','null_job.py','collect_null_resume.py')},'new_fits':0,'final_access':False})
    print('CHECKPOINT_RESUME_REGISTERED',jobs)
if __name__=='__main__':main()
