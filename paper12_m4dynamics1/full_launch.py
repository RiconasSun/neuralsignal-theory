"""Conditional unchanged competition: no data preparation until smoke PASS."""
import ast
import difflib
import importlib.util
import shutil
import subprocess
import sys
import study as r
from controls import completed,verify
from prepare import security
from full_transform import transformed

def main():
    verify();diagnosis=completed('diagnosis');smoke=completed('smoke');a=security()
    if r.load(r.HERE/'optimizer_amendment.json')['diagnosis_bindings']!=diagnosis:raise RuntimeError('AMENDMENT_BINDING_REQUIRED')
    gate=r.load(r.HERE/'results/smoke/native/gate_result.json')
    if gate['completed_fit_count']!=216 or any(v<1 for v in gate['possible_configuration_counts'].values()):raise RuntimeError('FULL_FAMILY_SMOKE_REQUIRED')
    archived=r.load(r.OFFSET/'M4_registration.json')
    oldmath=r.OFFSET/'exports/M4_code/model_math.py'
    if r.sha(oldmath)!=archived['code_sha256']['model_math.py']:raise RuntimeError('FROZEN_MATH_SOURCE_REQUIRED')
    old=oldmath.read_bytes();needle=b'options=dict(maxiter=500,maxfun=20000,ftol=1e-5,gtol=1e-5))'
    replacement=b'options=dict(maxiter=2000,maxfun=80000,ftol=1e-10,gtol=1e-5))'
    if old.count(needle)!=1:raise RuntimeError('OPTIONS_ONLY_PATCH_LOCATION_REQUIRED')
    new=old.replace(needle,replacement,1)
    r.save(r.HERE/'full_method_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_AB_access=True,before_code_patch=True,
        diagnosis_bindings=diagnosis,smoke_bindings=smoke,optimizer_amendment_sha256=r.sha(r.HERE/'optimizer_amendment.json'),
        controller_sha256={n:r.sha(r.HERE/n) for n in ('full_launch.py','full_transform.py','reuse_dynamics.py')},
        original_model_math_sha256=r.sha(oldmath),amended_model_math_sha256=r.hashlib.sha256(new).hexdigest(),
        change='Exactly one solver-options replacement; same policy as all216 amended smoke fits',M3_refits=0,offset_refits=0,final_access=False))
    code=r.HERE/'exports/code_M4';code.mkdir(exist_ok=False)
    for name,digest in archived['code_sha256'].items():
        if name in ('worker.py','offset_states.npz','offset_records.json','offset_bundle.json'):continue
        source=r.OFFSET/'exports/M4_code'/name
        if r.sha(source)!=digest:raise RuntimeError('ARCHIVED_CODE_CHANGED:'+name)
        shutil.copy2(source,code/name)
    (code/'model_math.py').write_bytes(new)
    (r.HERE/'model_optimizer.diff').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='frozen/model_math.py',tofile='amended/model_math.py')),encoding='utf-8')
    driver=(r.OFFSET/'exports/M4_code/worker.py').read_text()
    if r.sha(r.OFFSET/'exports/M4_code/worker.py')!=archived['code_sha256']['worker.py']:raise RuntimeError('FROZEN_DRIVER_SOURCE_REQUIRED')
    driver=transformed(driver)
    point="    import numpy as np\n"
    block="""    import unittest
    suites=[unittest.TestLoader().discover(str(Path(__file__).parent),pattern=p) for p in ('test_*.py','m4_numerical_tests.py','m4_control_tests.py')]
    test=unittest.TestResult();unittest.TestSuite(suites).run(test)
    save('oracle_tests.json',dict(count=test.testsRun,passed=test.wasSuccessful(),failures=[str(x) for x in test.failures],errors=[str(x) for x in test.errors]))
    if test.testsRun!=14 or not test.wasSuccessful():raise RuntimeError('FOURTEEN_FROZEN_AND_INDEPENDENT_NUMERICAL_CHECKS_REQUIRED')
"""
    if driver.count(point)!=1:raise RuntimeError('NUMERICAL_CHECK_INSERTION_REQUIRED')
    driver=driver.replace(point,block+point,1);ast.parse(driver)
    (code/'worker.py').write_text(driver,encoding='utf-8',newline='')
    for name in ('reuse_dynamics.py','roster.py','oracle.py','test_oracle.py','test_hybrid_history.py'):shutil.copy2(r.HERE/name,code/name)
    receipt=r.load(r.HERE/'results/smoke_launch_receipt.json');state=r.HERE/receipt['output_directory']/'fitted_states.npz'
    if r.sha(state)!=gate['fitted_states_sha256']:raise RuntimeError('SMOKE_STATE_HASH_REQUIRED')
    shutil.copy2(state,code/'reuse_states.npz')
    shutil.copy2(r.HERE/'results/smoke/native/summary.json',code/'reuse_summary.json')
    shutil.copy2(r.HERE/'results/smoke/native/gate_result.json',code/'reuse_gate.json')
    r.save(code/'reuse_bundle.json',dict(sha256={n:r.sha(code/n) for n in ('reuse_states.npz','reuse_summary.json','reuse_gate.json')},completed_smoke_bindings=smoke))
    full=r.load(r.OFFSET/'results/full/native/gate_result.json');oldreceipt=r.load(r.OFFSET/'results/full_launch_receipt.json')
    oldproof=r.load(r.OFFSET/'results/full/native/role_proof.json')
    if full['gate']!='PASS' or full['converged_fit_count']!=78 or oldreceipt['exit_code']!=0 or oldreceipt['timed_out'] or not oldreceipt['role_proof_pass'] or oldreceipt['profile_cleanup_hresult']!='0x00000000' or not oldproof['pass'] or oldproof['capability_count']!=0:raise RuntimeError('COMPLETE_FROZEN_OFFSET_GATE_REQUIRED')
    for name,source,digest in (
        ('offset_states.npz',r.OFFSET/oldreceipt['output_directory']/'offset_states.npz',full['state_sha256']),
        ('offset_records.json',r.OFFSET/'results/full/native/offset_records.json',full['records_sha256'])):
        if r.sha(source)!=digest:raise RuntimeError('FROZEN_OFFSET_HASH_REQUIRED')
        shutil.copy2(source,code/name)
    r.save(code/'offset_bundle.json',dict(state_sha256=full['state_sha256'],records_sha256=full['records_sha256']))
    source=r.OFFSET/'exports/M4_AB'
    if r.sha(source/'manifest.json')!=archived['input_manifest_sha256']:raise RuntimeError('FROZEN_AB_MANIFEST_REQUIRED')
    manifest=r.load(source/'manifest.json')
    if manifest['group']!='development' or manifest['compartments']!=['A','B'] or len(manifest['sessions'])!=13:raise PermissionError('THIRTEEN_DEVELOPMENT_AB_ONLY')
    for s in manifest['sessions']:
        if r.sha(source/s['file'])!=s['sha256']:raise RuntimeError('FROZEN_AB_INPUT_HASH')
    data=r.HERE/'exports/M4_AB';shutil.copytree(source,data);a.protect(data);a.protect(code)
    for name,digest in archived['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('RUNTIME_CHANGED')
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/'M4_execution_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_real_fits=True,
        code_sha256=hashes,input_manifest_sha256=r.sha(data/'manifest.json'),runtime_sha256=archived['runtime_sha256'],
        method_registration_sha256=r.sha(r.HERE/'full_method_registration.json'),baseline_refits=0,offset_refits=0,first_mouse_refits=0,
        source='Same frozen13 development mice, all57 configurations, allseeds, bothregions; unchanged eligibility/one-SE',final_access=False))
    spec=importlib.util.spec_from_file_location('full_native_adapter',r.OFFSET/'launch_phase.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    tree=ast.parse((r.OFFSET/'launch_phase.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='native_run')
    class Scope(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='Training-only offset ':return ast.copy_location(ast.Constant('Frozen development A/B dynamical competition '),n)
            return n
    fn=Scope().visit(fn);ns=dict(vars(module));ns['r']=r
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),ns)
    ns['native_run']('M4',data,code,hashes,a)

if __name__=='__main__':main()
