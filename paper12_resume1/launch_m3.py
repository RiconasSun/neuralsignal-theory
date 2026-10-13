"""Storage/gate adapter for the unchanged native progressive M3 launcher."""
import ast
import sys
import types
from pathlib import Path
import study as r
import verified_atomic as a
from preflight import guard
import launch_analysis as archived
from register_m3 import guard_adapter
from fingerprints import check as check_fingerprints

SCIENCE_FILES={'development_registration.json','M3_METHOD_DECISION1.json','method_registration1.json',
               'progressive_registration1.json'}


def mapped(path):
    path=Path(path)
    public={r.ROOT/'paper12_curated_v1/locks'/name for name in ('animals.json','units.json','trials.json')}
    if path in public:return path
    path=a.check_path(path)
    relative=path.relative_to(r.HERE).as_posix()
    if relative in SCIENCE_FILES:return r.OLD/relative
    if relative=='results/M2/aggregate4/gate_result.json':return r.HERE/'results/M2/gate_result.json'
    if relative.startswith('results/M2/index2/sessions/'):
        return r.HERE/'results/M2/sessions'/path.name
    policy=r.load(r.OLD/'development_registration.json')
    if relative in policy['implementation_sha256']:return r.OLD/relative
    return path


def load(path):return r.load(mapped(path))
def sha(path):return r.sha(mapped(path)) if str(path).startswith(str(r.HERE)) else r.sha(path)


def main():
    policy=guard_adapter();reg=guard()
    if r.load(r.HERE/'results/M2/gate_result.json')['gate']!='PASS':raise RuntimeError('NEW_M2_PASS_REQUIRED')
    for path in (r.HERE/'results/M2/sessions').glob('*.json'):
        receipt=r.load(path)
        if receipt['group']=='development':check_fingerprints(receipt,reg)
    proxy=types.SimpleNamespace(**vars(r));proxy.ID='P12-M2-ISOLATED-CUSTODY-1';proxy.load=load;proxy.sha=sha
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    runtimes=list((r.HERE/'exports').glob('replay_probe_*/runtime'))
    if len(runtimes)!=1:raise RuntimeError('PREFLIGHT_RUNTIME_AMBIGUOUS')
    runtime=runtimes[0]
    canary=r.load(r.HERE/'results/native_canary.json')
    source='.private/'+canary['synthetic_run_namespace']+'/main/trial_0/block.checkpoint'
    mapping={'results/M3/native1':'results/M3/progressive1','results/M3/native_launch_receipt.json':'results/M3/progressive_launch_receipt_code4.json',
        'exports/native_probe/runtime':runtime.relative_to(r.HERE).as_posix(),'.private/native_probe_source.bin':source}
    changed=[]
    class Adapt(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:changed.append(n.value);return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_BinOp(self,n):
            if isinstance(n.op,ast.Div) and isinstance(n.left,ast.Name) and n.left.id=='code' and isinstance(n.right,ast.Constant) and n.right.value=='analysis_worker.py':
                changed.append('entrypoint');return ast.copy_location(ast.BinOp(left=n.left,op=n.op,right=ast.Constant('analysis_worker_progress1.py')),n)
            if isinstance(n.op,ast.Div) and isinstance(n.left,ast.Attribute) and isinstance(n.left.value,ast.Name) and n.left.value.id=='r' and n.left.attr=='HERE' and isinstance(n.right,ast.Name) and n.right.id=='filename':
                changed.append('code_copy');n.left=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(r.OLD))],keywords=[])
            return self.generic_visit(n)
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter.elts.extend([ast.Constant('analysis_worker_progress1.py'),ast.Constant('stage_gate.py')]);changed.append('progressive_copy')
            return self.generic_visit(n)
    node=Adapt().visit(node)
    if sorted(changed)!=sorted(list(mapping)+['entrypoint','code_copy','progressive_copy']):raise RuntimeError('NATIVE_LAUNCH_ADAPTER_SCOPE')
    globals_copy=dict(vars(archived));globals_copy.update(r=proxy,custodian=types.SimpleNamespace(check_gate=guard))
    grant_globals=dict(archived.grant.__globals__);grant_globals['r']=proxy
    globals_copy['grant']=a.clone(archived.grant,grant_globals)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),__file__,'exec'),globals_copy)
    globals_copy['main']()


if __name__=='__main__':main()
