"""Registered training-only phases using unchanged zero-capability native core."""
import ast
import importlib.util
import shutil
import sys
import study as r
from prepare import security


def native_run(phase,data,code_root,code_hashes,a):
    sys.path.append(str(r.OLD))
    spec=importlib.util.spec_from_file_location('offset_archived_native',r.OLD/'launch_analysis.py')
    archived=importlib.util.module_from_spec(spec);spec.loader.exec_module(archived)
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    index=next(i for i,n in enumerate(body.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user' for t in n.targets))
    body.body=ast.parse('security_only=False\ndata=selected_data').body+body.body[index:]
    mapping={'analysis_worker.py':'worker.py','exports/native_probe/runtime':'exports/runtime',
        '.private/native_probe_source.bin':'.private/source_canary.bin','.private/native_probe_key.bin':'.private/key_canary.bin',
        'results/M3/native1':f'results/{phase}/native','results/M3/native_launch_receipt.json':f'results/{phase}_launch_receipt.json',
        'Development M3 baselines only':'Training-only offset '+phase,'M3_gate':phase+'_gate'}
    class Adapt(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter=ast.Tuple(elts=[ast.Constant(x) for x in code_hashes],ctx=ast.Load());return n
            return self.generic_visit(n)
    body=Adapt().visit(body)
    loop=next(n for n in ast.walk(body) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='filename')
    loop.body=ast.parse('shutil.copy2(selected_code/filename,code/filename)').body
    ns=dict(vars(archived));ns.update(r=r,selected_code=code_root,selected_data=data)
    gs=dict(archived.grant.__globals__);gs['r']=r;ns['grant']=a.clone(archived.grant,gs)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),__file__,'exec'),ns);ns['main']()
    receipt=r.load(r.HERE/f'results/{phase}_launch_receipt.json');gate=r.load(r.HERE/f'results/{phase}/native/gate_result.json')
    if receipt['exit_code']!=0 or receipt['timed_out'] or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000' or gate['gate']!='PASS':
        raise RuntimeError('MANDATORY_NATIVE_GATE_FAILED_STOP:'+phase)
    return receipt,gate


def completed(phase):
    gate=r.load(r.HERE/f'results/{phase}/native/gate_result.json');receipt=r.load(r.HERE/f'results/{phase}_launch_receipt.json')
    proof=r.load(r.HERE/f'results/{phase}/native/role_proof.json');oracles=r.load(r.HERE/f'results/{phase}/native/oracle_tests.json')
    if gate['gate']!='PASS' or receipt['exit_code']!=0 or receipt['timed_out'] or receipt['profile_cleanup_hresult']!='0x00000000' or not receipt['role_proof_pass'] or proof['pass'] is not True or proof['capability_count']!=0 or oracles['count']!=12 or not oracles['passed']:
        raise RuntimeError('COMPLETE_NATIVE_PRECEDING_GATE_REQUIRED:'+phase)
    return {n:r.sha(r.HERE/p) for n,p in dict(gate=f'results/{phase}/native/gate_result.json',receipt=f'results/{phase}_launch_receipt.json',proof=f'results/{phase}/native/role_proof.json',oracles=f'results/{phase}/native/oracle_tests.json').items()}


def main():
    phase=sys.argv[1]
    if phase not in ('diagnosis','smoke','small','full'):raise RuntimeError('UNREGISTERED_PHASE')
    r.verify();a=security();implementation=r.load(r.HERE/'implementation_registration.json')
    for name,digest in implementation['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_PRIMITIVE_CHANGED')
    for name,digest in implementation['local_sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('DIAGNOSTIC_IMPLEMENTATION_CHANGED')
    issuer=r.load(r.HERE/'.private/training_issuer.json');data=r.HERE/'exports/training_A'
    if r.sha(data/'manifest.json')!=issuer['manifest_sha256']:raise RuntimeError('TRAINING_MANIFEST_CHANGED')
    for name,digest in issuer['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('RUNTIME_CHANGED')
    previous={'smoke':'diagnosis','small':'smoke','full':'small'}.get(phase)
    bindings=completed(previous) if previous else None
    amendment=r.load(r.HERE/'optimizer_amendment.json') if phase!='diagnosis' else None
    if amendment and amendment['diagnostic_sha256']!=completed('diagnosis'):raise RuntimeError('DIAGNOSIS_BINDINGS_CHANGED')
    code=r.HERE/'exports'/('code_'+phase);code.mkdir(exist_ok=False)
    sources={n:r.OLD/n for n in ('baseline_fit.py','baseline_features.py','native_analysis_check.py')}
    sources.update({n:r.M3/n for n in ('numerical.py','test_numerical.py')})
    sources.update({n:r.HERE/n for n in ('worker.py','offset_math.py','test_offset.py','original_offset_diagnostics.json')})
    sources['task_offset.py']=r.PREVIOUS/'task_offset.py' if phase=='diagnosis' else r.HERE/'patched/task_offset.py'
    for name,path in sources.items():shutil.copy2(path,code/name)
    policy=dict(phase=phase)
    if phase in ('small','full'):
        old=r.load(r.HERE/f'results/{previous}_launch_receipt.json');source=r.HERE/old['output_directory']/'offset_states.npz'
        old_gate=r.load(r.HERE/f'results/{previous}/native/gate_result.json')
        if r.sha(source)!=old_gate['state_sha256']:raise RuntimeError('PROTECTED_STATE_CHANGED')
        shutil.copy2(source,code/'reuse_states.npz');shutil.copy2(r.HERE/f'results/{previous}/native/offset_records.json',code/'reuse_records.json')
        policy['reuse_states_sha256']=r.sha(source)
    r.save(code/'worker_policy.json',policy,True);a.protect(code)
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/f'{phase}_execution_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_real_fits=True,
        code_sha256=hashes,preceding_native_sha256=bindings,amendment_sha256=r.sha(r.HERE/'optimizer_amendment.json') if amendment else None,
        A_manifest_sha256=issuer['manifest_sha256'],runtime_sha256=issuer['runtime_sha256'],validation_access=False,final_access=False),True)
    native_run(phase,data,code,hashes,a)


if __name__=='__main__':main()
