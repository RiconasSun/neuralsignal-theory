import ast
import shutil
import subprocess
import sys
import study as r
from prepare import security
from launch_phase import completed
from m4_driver import transformed


def main():
    r.verify();bindings=completed('full');a=security()
    runtime_hashes=r.load(r.HERE/'.private/training_issuer.json')['runtime_sha256']
    for name,digest in runtime_hashes.items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('VERIFIED_RUNTIME_CHANGED')
    full=r.load(r.HERE/'results/full/native/gate_result.json')
    if full['completed_fit_count']!=78 or full['converged_fit_count']!=78:raise RuntimeError('ALL78_OFFSET_SEEDS_REQUIRED')
    rows=r.HERE/'results/full/native/offset_records.json'
    if r.sha(rows)!=full['records_sha256']:raise RuntimeError('OFFSET_RECORD_HASH')
    receipt=r.load(r.HERE/'results/full_launch_receipt.json');state=r.HERE/receipt['output_directory']/'offset_states.npz'
    if r.sha(state)!=full['state_sha256']:raise RuntimeError('FROZEN_OFFSET_STATE_HASH')
    old=r.load(r.HARNESS/'execution_registration.json');code=r.HERE/'exports/M4_code';code.mkdir(exist_ok=False)
    for name,digest in old['native_code_sha256'].items():
        src=r.HARNESS/'exports/code'/name
        if r.sha(src)!=digest:raise RuntimeError('ARCHIVED_M4_NATIVE_CODE_CHANGED')
        if name=='model_worker.py':continue
        shutil.copy2(src,code/name)
    driver=transformed((r.PREVIOUS/'model_worker.py').read_text());ast.parse(driver)
    (code/'worker.py').write_text(driver,encoding='utf-8',newline='')
    for name in ('impossibility.py','frozen_offset.py','m4_control_tests.py'):shutil.copy2(r.HERE/name,code/name)
    shutil.copy2(state,code/'offset_states.npz');shutil.copy2(rows,code/'offset_records.json')
    r.save(code/'offset_bundle.json',dict(state_sha256=full['state_sha256'],records_sha256=full['records_sha256']),True);a.protect(code)
    data=r.HERE/'exports/M4_AB';shutil.copytree(r.HARNESS/'exports/development_AB',data);a.protect(data)
    if r.sha(data/'manifest.json')!=old['input_manifest_sha256']:raise RuntimeError('FROZEN_DEVELOPMENT_AB_CHANGED')
    manifest=r.load(data/'manifest.json')
    if len(manifest['sessions'])!=13 or manifest['compartments']!=['A','B']:raise RuntimeError('FROZEN_THIRTEEN_AB_REQUIRED')
    for session in manifest['sessions']:
        if r.sha(data/session['file'])!=session['sha256']:raise RuntimeError('FROZEN_AB_DATA_HASH')
    r.save(r.HERE/'M4_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_numerical_tests=True,before_model_fits=True,
        full_offset_bindings=bindings,full_offset_state_sha256=full['state_sha256'],full_offset_records_sha256=full['records_sha256'],
        code_sha256={p.name:r.sha(p) for p in code.iterdir() if p.is_file()},input_manifest_sha256=r.sha(data/'manifest.json'),
        runtime_sha256=runtime_hashes,
        source_sha256={n:r.sha(r.ROOT/n) for n in r.load(r.M3/'M4_registration.json')['source_sha256']},
        controller_sha256={n:r.sha(r.HERE/n) for n in ('prepare_m4.py','launch_m4.py','m4_driver.py','impossibility.py','frozen_offset.py','m4_control_tests.py')},
        early_stop='Exact convergence-only impossibility, all216 attempts per completed mouse; no score selection',
        model_optimizer_grids_thresholds_unchanged=True,M3_repeated=False,final_access=False),True)
    runner="import sys,unittest,json;sys.path.insert(0,sys.argv[1]);a=unittest.defaultTestLoader.discover(sys.argv[1],pattern='m4_numerical_tests.py');b=unittest.defaultTestLoader.discover(sys.argv[1],pattern='m4_control_tests.py');s=unittest.TestSuite([a,b]);r=unittest.TextTestRunner(verbosity=2).run(s);print(json.dumps(dict(count=r.testsRun,passed=r.wasSuccessful(),skipped=len(r.skipped))));sys.exit(0 if r.wasSuccessful() else 1)"
    result=subprocess.run([sys.executable,'-c',runner,str(code)],cwd=r.ROOT,capture_output=True,text=True)
    log=r.HERE/'results/M4/numerical_tests.log';log.parent.mkdir(parents=True,exist_ok=True);log.write_text(result.stdout+result.stderr,encoding='utf-8')
    report=r.json.loads(result.stdout);passed=result.returncode==0 and report['count']==8 and report['passed'] and report['skipped']==0
    r.save(r.HERE/'results/M4/numerical_gate.json',dict(gate='PASS' if passed else 'FAIL',tests_run=report['count'],exit_code=result.returncode,
        log_sha256=r.sha(log),registration_sha256=r.sha(r.HERE/'M4_registration.json'),synthetic_only=True),True)
    print(result.stdout+result.stderr)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
