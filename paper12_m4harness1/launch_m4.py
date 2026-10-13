"""Reuse native isolated launcher; only paths/test-copy change, science unchanged."""
import ast
import importlib.util
import sys
import study as r
from prepare_execution import security,numerical


def main():
    r.verify();numerical();a=security();policy=r.load(r.HERE/'execution_registration.json')
    for name,digest in policy['implementation_sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('LAUNCH_CODE_CHANGED')
    if policy['numerical_gate_sha256']!=r.sha(r.HERE/'results/numerical_gate.json') or policy['independent_review_sha256']!=r.sha(r.HERE/'review_clearance.json'):
        raise RuntimeError('ADMISSION_PROOF_CHANGED')
    if policy['M3_gate_sha256']!=r.sha(r.M3/'results/full/gate_result.json'):raise RuntimeError('M3_GATE_CHANGED')
    for name,digest in policy['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_SOURCE_CHANGED')
    code_root=r.HERE/'exports/code'
    for name,digest in policy['native_code_sha256'].items():
        if r.sha(code_root/name)!=digest:raise RuntimeError('NATIVE_CODE_CHANGED')
    for name,digest in policy['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('RUNTIME_CHANGED')
    data=r.HERE/'exports/development_AB';manifest=r.load(data/'manifest.json')
    if r.sha(data/'manifest.json')!=policy['input_manifest_sha256'] or manifest['compartments']!=['A','B'] or len(manifest['sessions'])!=13:
        raise RuntimeError('FROZEN_DEVELOPMENT_ONLY_INPUT_REQUIRED')
    for session in manifest['sessions']:
        if r.sha(data/session['file'])!=session['sha256']:raise RuntimeError('INPUT_CHANGED')
    sys.path.append(str(r.OLD))
    spec=importlib.util.spec_from_file_location('harness_archived_launcher',r.OLD/'launch_analysis.py')
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    i=next(i for i,n in enumerate(body.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user' for t in n.targets))
    body.body=ast.parse("security_only=False\ndata=r.HERE/'exports/development_AB'").body+body.body[i:]
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
    if receipt['exit_code']!=0 or receipt['timed_out'] or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000':
        raise RuntimeError('MANDATORY_M4_GATE_FAILED_STOP')
    if r.load(r.HERE/'results/M4/native/gate_result.json')['gate']!='PASS':raise RuntimeError('MANDATORY_M4_SCIENTIFIC_GATE_FAILED_STOP')


if __name__=='__main__':main()
