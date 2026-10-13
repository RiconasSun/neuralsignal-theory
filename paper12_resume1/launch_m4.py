"""Same native no-capability execution boundary, frozen M4 worker instead of M3."""
import ast
import json
import sys
import types
from pathlib import Path
import study as r
import verified_atomic as a
from preflight import guard
from register_m3 import guard_adapter
from launch_m3 import load,sha
import launch_analysis as archived


def implementation_path(name):
    if name in ('predictive_models.py','predictive_models_code1.py','r2_models.py'):
        return r.ROOT/'paper11_v2/scripts'/name
    if name in ('model_worker.py','model_math.py','task_offset.py','competition.py','baseline_metrics.json'):
        return r.HERE/name
    allowed={'baseline_features.py','baseline_fit.py','native_analysis_check.py','test_baseline_features.py','test_baseline_fit.py'}
    if name not in allowed:raise RuntimeError('M4_CODE_COPY_SCOPE')
    return r.OLD/name


def main():
    guard_adapter();guard()
    reg=r.load(r.HERE/'M4_implementation_registration.json')
    for relative,digest in reg['sha256'].items():
        if r.sha(r.ROOT/relative)!=digest:raise RuntimeError('M4_IMPLEMENTATION_CHANGED')
    gate=r.HERE/'results/M3/progressive1/gate_result.json'
    if r.sha(gate)!=reg['M3_gate_sha256'] or r.load(gate)['gate']!='PASS':raise RuntimeError('M3_PASS_REQUIRED')
    numerical=r.load(r.HERE/'results/M4/numerical_gate.json')
    if numerical['gate']!='PASS' or numerical['exit_code']!=0 or numerical['fixture_scope_only'] is not True:
        raise RuntimeError('M4_NUMERICAL_PASS_REQUIRED')
    if numerical['registered_sources_sha256']!=r.sha(r.HERE/'M4_implementation_registration.json') or numerical['log_sha256']!=r.sha(r.HERE/'results/M4/numerical_tests.log'):
        raise RuntimeError('M4_NUMERICAL_EVIDENCE_CHANGED')
    proxy=types.SimpleNamespace(**vars(r));proxy.ID='P12-M2-ISOLATED-CUSTODY-1';proxy.load=load;proxy.sha=sha
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    runtime=list((r.HERE/'exports').glob('replay_probe_*/runtime'))
    if len(runtime)!=1:raise RuntimeError('PREFLIGHT_RUNTIME_AMBIGUOUS')
    canary=r.load(r.HERE/'results/native_canary.json')
    mapping={'results/M3/native1':'results/M4/native1','results/M3/native_launch_receipt.json':'results/M4/native_launch_receipt.json',
        'exports/native_probe/runtime':runtime[0].relative_to(r.HERE).as_posix(),
        '.private/native_probe_source.bin':'.private/'+canary['synthetic_run_namespace']+'/main/trial_0/block.checkpoint',
        'analysis_worker.py':'model_worker.py','M3_gate':'M4_gate'}
    changed=[]
    class Adapt(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:changed.append(n.value);return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_BinOp(self,n):
            if isinstance(n.op,ast.Div) and isinstance(n.left,ast.Attribute) and isinstance(n.left.value,ast.Name) and n.left.value.id=='r' and n.left.attr=='HERE' and isinstance(n.right,ast.Name) and n.right.id=='filename':
                changed.append('code_copy');return ast.copy_location(ast.Call(func=ast.Name(id='implementation_path',ctx=ast.Load()),args=[n.right],keywords=[]),n)
            return self.generic_visit(n)
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter.elts.extend(ast.Constant(x) for x in ('model_math.py','task_offset.py','competition.py','predictive_models.py','predictive_models_code1.py','r2_models.py','baseline_metrics.json'));changed.append('M4_import_copy')
            return self.generic_visit(n)
    node=Adapt().visit(node)
    expected=list(mapping)+['analysis_worker.py','code_copy','M4_import_copy']
    if sorted(changed)!=sorted(expected):raise RuntimeError('M4_NATIVE_ADAPTER_SCOPE')
    namespace=dict(vars(archived));namespace.update(r=proxy,custodian=types.SimpleNamespace(check_gate=guard),implementation_path=implementation_path)
    globals_copy=dict(archived.grant.__globals__);globals_copy['r']=proxy
    namespace['grant']=a.clone(archived.grant,globals_copy)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),__file__,'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
