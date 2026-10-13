"""Reuse archived zero-capability launcher body with bounded audited AST adaptation."""
import ast
import types
import sys
from pathlib import Path
import study as r
from prepare import guard,security


def main():
    guard();a=security()
    sys.path.append(str(r.OLD))
    import launch_analysis as archived
    issuer=r.load(r.HERE/'.private/training_issuer.json');data=r.HERE/'exports/training_only'
    if issuer['manifest_sha256']!=r.sha(data/'manifest.json'):raise RuntimeError('INPUT_MANIFEST_CHANGED')
    session=r.load(data/'manifest.json')['sessions'][0]
    if issuer['count_sha256']!=r.sha(data/session['file']):raise RuntimeError('INPUT_COUNT_CHANGED')
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text())
    body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    index=next(i for i,n in enumerate(body.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user' for t in n.targets))
    body.body=ast.parse("security_only=False\ndata=r.HERE/'exports/training_only'").body+body.body[index:]
    mapping={'analysis_worker.py':'worker.py','exports/native_probe/runtime':'exports/runtime',
        '.private/native_probe_source.bin':'.private/source_canary.bin','.private/native_probe_key.bin':'.private/key_canary.bin',
        'results/M3/native1':'results/diagnosis','results/M3/native_launch_receipt.json':'results/diagnosis_launch_receipt.json'}
    copies=('worker.py','numerical.py','test_numerical.py','baseline_features.py','baseline_fit.py','native_analysis_check.py')
    class Adapter(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter=ast.Tuple(elts=[ast.Constant(x) for x in copies],ctx=ast.Load())
                return n
            return self.generic_visit(n)
    body=Adapter().visit(body)
    # Copy loop chooses immutable originals for archived primitives, new code otherwise.
    loop=next(n for n in ast.walk(body) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='filename')
    loop.body=ast.parse("shutil.copy2((r.OLD if filename in ('baseline_features.py','baseline_fit.py','native_analysis_check.py') else r.HERE)/filename,code/filename)").body
    ns=dict(vars(archived));ns['r']=r
    grants=dict(archived.grant.__globals__);grants['r']=r;ns['grant']=a.clone(archived.grant,grants)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),__file__,'exec'),ns)
    ns['main']()
    receipt=r.load(r.HERE/'results/diagnosis_launch_receipt.json')
    if receipt['exit_code']!=0 or not receipt['role_proof_pass']:raise RuntimeError('DIAGNOSIS_NATIVE_GATE_FAILED')


if __name__=='__main__':main()
