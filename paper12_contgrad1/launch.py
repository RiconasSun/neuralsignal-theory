"""Custodian controller reusing the archived zero-capability native launcher."""
import ast
import importlib.util
import shutil
import sys
import study as r

def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('gradient_verified_atomic',r.PREVIOUS/'verified_atomic.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);a.verify_parity();a.require_custodian();return a

def verify():
    registration=r.load(r.HERE/'registration.json')
    for name,digest in registration['sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_PROTOCOL_CHANGED:'+name)
    implementation=r.load(r.HERE/'execution_sources_v3.json')
    for name,digest in implementation['sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('REGISTERED_SOURCE_CHANGED:'+name)
    for name,digest in r.load(r.HERE/'prior_manifest.json')['sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('BASE_BYTES_CHANGED:'+name)

def main():
    verify();a=security()
    issuer=r.load(r.DYNAMICS/'.private/training_issuer.json');source=r.DYNAMICS/'exports/training_A'
    oldreg=r.load(r.DYNAMICS/'smoke_execution_registration.json')
    if r.sha(source/'manifest.json')!=issuer['manifest_sha256'] or issuer['manifest_sha256']!=oldreg['A_manifest_sha256']:raise RuntimeError('SAME_A_MANIFEST_REQUIRED')
    manifest=r.load(source/'manifest.json')
    if manifest['group']!='development' or manifest['compartments']!=['A'] or len(manifest['sessions'])!=13 or manifest['sessions'][0]['session_id']!='766640955':raise PermissionError('EXACT_DEVELOPMENT_A')
    for session in manifest['sessions']:
        if r.sha(source/session['file'])!=session['sha256']:raise RuntimeError('FROZEN_A_BYTES')
    exports=r.HERE/'exports';exports.mkdir(exist_ok=False)
    data=exports/'training_A';shutil.copytree(source,data);a.protect(data)
    runtime=exports/'runtime';shutil.copytree(r.DYNAMICS/'exports/runtime',runtime);a.protect(runtime)
    if issuer['runtime_sha256']!=oldreg['runtime_sha256']:raise RuntimeError('SAME_RUNTIME_REQUIRED')
    for name,digest in issuer['runtime_sha256'].items():
        if r.sha(runtime/name)!=digest:raise RuntimeError('FROZEN_RUNTIME_BYTES:'+name)
    private=r.HERE/'.private';a.prepare(private)
    for name in ('source_canary.bin','key_canary.bin'):
        path=private/name;path.write_bytes(b'SYNTHETIC_ROLE_PROBE_ONLY_NO_NEURAL_CONTENT');a.protect(path)
    code=exports/'code_diagnostic';code.mkdir(exist_ok=False)
    archived=r.load(r.OFFSET/'M4_registration.json')['code_sha256']
    for name in ('model_math.py','predictive_models.py','predictive_models_code1.py','r2_models.py','baseline_features.py','frozen_offset.py','native_analysis_check.py'):
        original=r.OFFSET/'exports/M4_code'/name
        if r.sha(original)!=archived[name]:raise RuntimeError('ARCHIVED_MATH_CHANGED:'+name)
        shutil.copy2(original,code/name)
    for name in ('worker.py','independent_ad.py','diagnostics.py','test_diagnostics.py','protocol.json'):
        shutil.copy2(r.HERE/name,code/name)
    shutil.copy2(r.DYNAMICS/'oracle.py',code/'oracle_original.py');shutil.copy2(r.DYNAMICS/'oracle_cached.py',code/'oracle.py')
    shutil.copy2(r.DYNAMICS/'results/smoke/native/CA1_Continuous_4_0.001_11.json',code/'preserved_failure.json')
    gate=r.load(r.OFFSET/'results/full/native/gate_result.json');offset_receipt=r.load(r.OFFSET/'results/full_launch_receipt.json')
    if gate['gate']!='PASS' or gate['converged_fit_count']!=78 or offset_receipt['exit_code']!=0 or offset_receipt['timed_out']:raise RuntimeError('FROZEN_OFFSETS_NOT_COMPLETE')
    states=r.OFFSET/offset_receipt['output_directory']/'offset_states.npz';records=r.OFFSET/'results/full/native/offset_records.json'
    if r.sha(states)!=gate['state_sha256'] or r.sha(records)!=gate['records_sha256']:raise RuntimeError('FROZEN_OFFSET_ARTIFACT_CHANGED')
    shutil.copy2(states,code/'offset_states.npz');shutil.copy2(records,code/'offset_records.json')
    r.save(code/'offset_bundle.json',dict(state_sha256=gate['state_sha256'],records_sha256=gate['records_sha256']))
    a.protect(code)
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/'execution_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_real_fit=True,base=r.BASE,protocol_sha256=r.sha(r.HERE/'protocol.json'),source_registration_sha256=r.sha(r.HERE/'execution_sources_v3.json'),code_sha256=hashes,runtime_sha256=issuer['runtime_sha256'],A_manifest_sha256=issuer['manifest_sha256'],preserved_failure_sha256=r.sha(code/'preserved_failure.json'),real_fits_max=1,validation_access=False,final_access=False))
    spec=importlib.util.spec_from_file_location('gradient_archived_launcher',r.OFFSET/'launch_phase.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    tree=ast.parse((r.OFFSET/'launch_phase.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='native_run')
    class Scope(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='Training-only offset ':return ast.copy_location(ast.Constant('Registered A-only continuous gradient diagnostic '),n)
            return n
    fn=Scope().visit(fn);ns=dict(vars(old));ns['r']=r
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),ns)
    ns['native_run']('diagnostic',data,code,hashes,a)
    receipt=r.load(r.HERE/'results/diagnostic_launch_receipt.json')
    public=r.HERE/'results/diagnostic/native';protected=r.HERE/receipt['output_directory']
    for name in ('gradient_scan.csv',):
        if (protected/name).exists():shutil.copy2(protected/name,public/name)
    final=r.load(public/'gate_result.json')
    if final['CSV_sha256']!=r.sha(public/'gradient_scan.csv'):raise RuntimeError('PUBLIC_CSV_HASH')
    print('NATIVE_DIAGNOSTIC_COMPLETE',final['verdict'],'rows',final['coordinate_rows'])

if __name__=='__main__':main()
