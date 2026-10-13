import ast
import sys
import study as r
import launch_phase
from launch_phase import completed
from prepare import security


def main():
    r.verify();a=security();policy=r.load(r.HERE/'M4_registration.json');gate=r.load(r.HERE/'results/M4/numerical_gate.json')
    if completed('full')!=policy['full_offset_bindings']:raise RuntimeError('FULL_OFFSET_NATIVE_PROOF_CHANGED')
    if gate['gate']!='PASS' or gate['tests_run']!=8 or gate['exit_code']!=0 or gate['registration_sha256']!=r.sha(r.HERE/'M4_registration.json') or gate['log_sha256']!=r.sha(r.HERE/'results/M4/numerical_tests.log'):
        raise RuntimeError('ALL_EIGHT_M4_NUMERICAL_AND_CONTROL_TESTS_REQUIRED')
    for name,digest in policy['controller_sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('M4_CONTROL_CHANGED')
    for name,digest in policy['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_MODEL_MATHEMATICS_CHANGED')
    for name,digest in policy['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('VERIFIED_MODEL_RUNTIME_CHANGED')
    code=r.HERE/'exports/M4_code'
    for name,digest in policy['code_sha256'].items():
        if r.sha(code/name)!=digest:raise RuntimeError('M4_NATIVE_CODE_OR_TRAINING_STATE_CHANGED')
    data=r.HERE/'exports/M4_AB';manifest=r.load(data/'manifest.json')
    if r.sha(data/'manifest.json')!=policy['input_manifest_sha256']:raise RuntimeError('FROZEN_M4_AB_MANIFEST_CHANGED')
    for session in manifest['sessions']:
        if r.sha(data/session['file'])!=session['sha256']:raise RuntimeError('FROZEN_MODEL_INPUT_CHANGED')
    tree=ast.parse((r.HERE/'launch_phase.py').read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='native_run')
    class Scope(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='Training-only offset ':return ast.copy_location(ast.Constant('Frozen development A/B model competition '),n)
            return n
    body=Scope().visit(body);ns=dict(vars(launch_phase))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),__file__,'exec'),ns)
    ns['native_run']('M4',data,code,policy['code_sha256'],a)


if __name__=='__main__':main()
