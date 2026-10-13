"""Sealed policy and development-only derivative, scoped archived native launcher."""
import ast
import os
import sys
import shutil
from pathlib import Path
import study as r
from prepare import security,guard
from transitions import completed,verify_bindings


def main():
    guard();a=security();amendment=r.load(r.HERE/'optimizer_amendment.json')
    for name,digest in amendment['code_sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('AMENDED_IMPLEMENTATION_CHANGED')
    verify_bindings(amendment,dict(
        diagnostic_summary_sha256=r.sha(r.HERE/'results/diagnosis/diagnosis_summary.json'),
        diagnostic_gate_sha256=r.sha(r.HERE/'results/diagnosis/gate_result.json'),
        training_input_receipt_sha256=r.sha(r.HERE/'results/training_export_receipt.json'),
        diagnosis_implementation_sha256=r.sha(r.HERE/'implementation_registration.json'),
        runtime_provenance_sha256=r.sha(r.HERE/'results/runtime_provenance.json')))
    for name,digest in amendment['runtime_sha256'].items():
        if r.sha(r.HERE/'exports/runtime'/name)!=digest:raise RuntimeError('REGISTERED_RUNTIME_CHANGED')
    full='--full' in sys.argv;phase='full' if full else 'smoke'
    native_diagnosis=completed(r,'diagnosis',120)
    if native_diagnosis!=amendment['native_diagnosis_sha256']:raise RuntimeError('DIAGNOSIS_BINDING_CHANGED')
    smoke_bindings=completed(r,'smoke',126) if full else None
    src=r.PREVIOUS/'exports/development1';manifest=r.load(src/'manifest.json')
    issuer=r.load(r.PREVIOUS/'.private/development_export_issuer.json')
    if issuer['manifest_sha256']!=r.sha(src/'manifest.json'):raise RuntimeError('ORIGINAL_EXPORT_ISSUER_CHANGED')
    sessions=manifest['sessions'] if full else manifest['sessions'][:1]
    if len(sessions)!=(13 if full else 1):raise RuntimeError('FROZEN_ROSTER_DENOMINATOR')
    data=r.HERE/('exports/'+phase+'_AB');data.mkdir(exist_ok=False);a.protect(data)
    for session in sessions:
        p=src/session['file']
        if r.sha(p)!=session['sha256']:raise RuntimeError('ORIGINAL_EXPORT_HASH_CHANGED')
        shutil.copy2(p,data/session['file']);a.protect(data/session['file'])
    manifest=dict(manifest);manifest['sessions']=sessions
    r.save(data/'manifest.json',manifest,True);a.protect(data/'manifest.json')
    r.save(r.HERE/('results/'+phase+'_preflight.json'),dict(manifest_sha256=r.sha(data/'manifest.json'),
        amendment_sha256=r.sha(r.HERE/'optimizer_amendment.json'),session_count=len(sessions),
        preceding_smoke_sha256=smoke_bindings,
        source_requests=0,final_access=False),True)
    sys.path.append(str(r.OLD));import launch_analysis as original
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    i=next(i for i,n in enumerate(body.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user' for t in n.targets))
    body.body=ast.parse('security_only=False\ndata=selected_data').body+body.body[i:]
    mapping={'analysis_worker.py':'smoke_worker.py','exports/native_probe/runtime':'exports/runtime',
        '.private/native_probe_source.bin':'.private/source_canary.bin','.private/native_probe_key.bin':'.private/key_canary.bin',
        'results/M3/native1':'results/'+phase,'results/M3/native_launch_receipt.json':'results/'+phase+'_launch_receipt.json'}
    class Adapt(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter=ast.Tuple(elts=[ast.Constant(x) for x in ('smoke_worker.py','numerical.py','test_numerical.py','baseline_features.py','baseline_fit.py','native_analysis_check.py')],ctx=ast.Load());return n
            return self.generic_visit(n)
    body=Adapt().visit(body)
    loop=next(n for n in ast.walk(body) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='filename')
    loop.body=ast.parse("shutil.copy2((r.OLD if filename in ('baseline_features.py','baseline_fit.py','native_analysis_check.py') else r.HERE)/filename,code/filename)").body
    ns=dict(vars(original));ns.update(r=r,selected_data=data)
    gs=dict(original.grant.__globals__);gs['r']=r;ns['grant']=a.clone(original.grant,gs)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),__file__,'exec'),ns);ns['main']()
    receipt=r.load(r.HERE/('results/'+phase+'_launch_receipt.json'))
    if receipt['exit_code']!=0 or not receipt['role_proof_pass']:raise RuntimeError('REPAIRED_NATIVE_GATE_FAILED')


if __name__=='__main__':main()
