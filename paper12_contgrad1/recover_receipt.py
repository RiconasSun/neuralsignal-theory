"""Certify completed original outputs without rerunning the optimizer."""
import ast
import importlib.util
import shutil
import study as r
from launch import security

def main():
    registration=r.load(r.HERE/'recovery_registration2.json')
    for name,digest in registration['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('RECOVERY_SOURCE_CHANGED:'+name)
    a=security();primary=r.HERE/'results/diagnostic/native';old=r.load(r.HERE/'execution_registration.json');data=r.HERE/'exports/training_A'
    for name,key in (('execution_registration.json','original_execution_registration_sha256'),('results/diagnostic/native/gate_result.json','primary_gate_sha256'),('results/diagnostic/native/gradient_scan.csv','primary_CSV_sha256')):
        if r.sha(r.HERE/name)!=registration[key]:raise RuntimeError('PREREGISTERED_PRIMARY_BINDING:'+key)
    for name,digest in registration['primary_JSON_sha256'].items():
        if r.sha(primary/name)!=digest:raise RuntimeError('PREREGISTERED_PRIMARY_JSON:'+name)
    for name,digest in old['code_sha256'].items():
        if r.sha(r.HERE/'exports/code_diagnostic'/name)!=digest:raise RuntimeError('ORIGINAL_NUMERICAL_CODE_CHANGED:'+name)
    if r.sha(data/'manifest.json')!=old['A_manifest_sha256']:raise RuntimeError('ORIGINAL_A_HASH')
    for name,digest in old['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('UNCHANGED_RUNTIME')
    code=r.HERE/'exports/code_receipt_recovery';code.mkdir(exist_ok=False)
    for name,source in {'worker.py':r.HERE/'certify_saved_worker.py','native_analysis_check.py':r.OFFSET/'exports/M4_code/native_analysis_check.py','reproduce_saved.py':r.HERE/'reproduce_saved.py','audit_statistics.py':r.HERE/'audit_statistics.py','study.py':r.HERE/'study.py','primary_gate.json':primary/'gate_result.json','primary_reproduction.json':primary/'reproduction.json','primary_decision.json':primary/'decision.json','primary_tests.json':primary/'synthetic_tests.json','gradient_scan.csv':primary/'gradient_scan.csv'}.items():shutil.copy2(source,code/name)
    bindings={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(code/'recovery_binding.json',dict(sha256=bindings,A_manifest_sha256=old['A_manifest_sha256'],original_execution_registration_sha256=r.sha(r.HERE/'execution_registration.json'),original_fit_count=1,no_refit=True))
    a.protect(code);hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/'recovery_execution_registration.json',dict(before_execution=True,code_sha256=hashes,registration_sha256=r.sha(r.HERE/'recovery_registration2.json'),scope='Saved-only certificate; no new fits/gradient evaluations',original_controller_receipt_missing=True))
    spec=importlib.util.spec_from_file_location('saved_cert_archived_launcher',r.OFFSET/'launch_phase.py');oldmodule=importlib.util.module_from_spec(spec);spec.loader.exec_module(oldmodule)
    fn=next(n for n in ast.parse((r.OFFSET/'launch_phase.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='native_run')
    class Scope(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='Training-only offset ':return ast.copy_location(ast.Constant('Saved-only continuous diagnostic certification '),n)
            return n
    fn=Scope().visit(fn);namespace=dict(vars(oldmodule));namespace['r']=r
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),namespace)
    namespace['native_run']('receipt_recovery',data,code,hashes,a)
    print('FRESH_NATIVE_SAVED_CERTIFICATION_PASS NO_REFIT')

if __name__=='__main__':main()
