"""Native M4 with unchanged frozen code, conditional on complete M3/numerical gates."""
import ast
import sys
import study as r
from prepare import security
from transitions import completed


def main():
    r.verify();a=security();policy=r.load(r.HERE/'M4_registration.json')
    if completed(r,'full',1638)!=policy['preceding_M3_sha256']:raise RuntimeError('M3_BOUNDARY_CHANGED')
    if r.sha(r.HERE/'launch_m4.py')!=policy['launcher_sha256']:raise RuntimeError('M4_LAUNCHER_CHANGED')
    for name,digest in policy['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_M4_SOURCE_CHANGED')
    code_root=r.HERE/'exports/m4code'
    for name,digest in policy['native_code_sha256'].items():
        if r.sha(code_root/name)!=digest:raise RuntimeError('M4_CODE_CHANGED')
    numerical=r.load(r.HERE/'results/M4/numerical_gate.json')
    if numerical['gate']!='PASS' or numerical.get('exit_code')!=0 or numerical.get('synthetic_only') is not True or numerical.get('tests_run')!=5 or numerical['registration_sha256']!=r.sha(r.HERE/'M4_registration.json'):
        raise RuntimeError('M4_NUMERICAL_GATE_REQUIRED')
    if numerical['log_sha256']!=r.sha(r.HERE/'results/M4/numerical_tests.log'):raise RuntimeError('M4_TEST_PROOF_CHANGED')
    if r.sha(r.HERE/'exports/full_AB/manifest.json')!=policy['input_manifest_sha256'] or r.sha(r.HERE/'results/full_preflight.json')!=policy['full_preflight_sha256']:
        raise RuntimeError('M4_M3_INPUT_BINDING_CHANGED')
    if r.sha(r.HERE/'results/runtime_provenance.json')!=policy['runtime_provenance_sha256']:raise RuntimeError('M4_RUNTIME_PROVENANCE_CHANGED')
    for name,digest in policy['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('M4_RUNTIME_CHANGED')
    sys.path.append(str(r.OLD));import launch_analysis as original
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    i=next(i for i,n in enumerate(body.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user' for t in n.targets))
    body.body=ast.parse("security_only=False\ndata=r.HERE/'exports/full_AB'").body+body.body[i:]
    manifest=r.load(r.HERE/'exports/full_AB/manifest.json')
    if len(manifest['sessions'])!=13 or manifest['compartments']!=['A','B']:raise RuntimeError('M4_FROZEN_DATA_REQUIRED')
    for s in manifest['sessions']:
        if r.sha(r.HERE/'exports/full_AB'/s['file'])!=s['sha256']:raise RuntimeError('M4_INPUT_HASH')
    mapping={'analysis_worker.py':'model_worker.py','exports/native_probe/runtime':'exports/runtime',
        '.private/native_probe_source.bin':'.private/source_canary.bin','.private/native_probe_key.bin':'.private/key_canary.bin',
        'results/M3/native1':'results/M4/native','results/M3/native_launch_receipt.json':'results/M4_launch_receipt.json',
        'Development M3 baselines only':'Development M4 competition only','M3_gate':'M4_gate'}
    class Adapt(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter=ast.Tuple(elts=[ast.Constant(x) for x in policy['native_code_sha256']],ctx=ast.Load());return n
            return self.generic_visit(n)
    body=Adapt().visit(body)
    loop=next(n for n in ast.walk(body) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='filename')
    loop.body=ast.parse('shutil.copy2(selected_code/filename,code/filename)').body
    ns=dict(vars(original));ns.update(r=r,selected_code=code_root)
    gs=dict(original.grant.__globals__);gs['r']=r;ns['grant']=a.clone(original.grant,gs)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),__file__,'exec'),ns);ns['main']()
    receipt=r.load(r.HERE/'results/M4_launch_receipt.json')
    if receipt['exit_code']!=0 or not receipt['role_proof_pass']:raise RuntimeError('M4_GATE_FAILED_STOP')


if __name__=='__main__':main()
