"""Trusted host adapter: actual native zero-capability processes, immutable code."""
import ast
import importlib.util
import shutil
import sys
import types
import study as r

def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('controls_atomic',r.PREVIOUS/'verified_atomic.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);a.verify_parity();a.require_custodian();return a

def launch(phase,job,data,code,hook=lambda package,pid,work,grant,user:None):
    a=security();job.mkdir(parents=True,exist_ok=True)
    proxy=types.SimpleNamespace(**vars(r));proxy.HERE=job
    spec=importlib.util.spec_from_file_location('controls_archived',r.OLD/'launch_analysis.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    tree=ast.parse((r.OLD/'launch_analysis.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    index=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='user' for t in n.targets))
    fn.body=ast.parse('security_only=False\ndata=selected_data').body+fn.body[index:]
    mapping={'analysis_worker.py':'worker.py','exports/native_probe/runtime':'exports/runtime',
        '.private/native_probe_source.bin':'.private/source_canary.bin','.private/native_probe_key.bin':'.private/key_canary.bin',
        'results/M3/native1':f'results/{phase}/native','results/M3/native_launch_receipt.json':f'results/{phase}_launch_receipt.json',
        'Development M3 baselines only':'Prerelease engineering '+phase,'M3_gate':phase+'_gate'}
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    class Adapt(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in mapping:return ast.copy_location(ast.Constant(mapping[n.value]),n)
            return n
        def visit_For(self,n):
            if isinstance(n.target,ast.Name) and n.target.id=='filename':
                n.iter=ast.Tuple(elts=[ast.Constant(x) for x in hashes],ctx=ast.Load());n.body=ast.parse('shutil.copy2(selected_code/filename,code/filename)').body;return n
            if isinstance(n.target,ast.Name) and n.target.id=='path' and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Attribute) and n.iter.func.attr=='glob':
                # Every individual attempt stays immutable in the native output and lossless archive.
                # Model summaries retain all endpoint records; avoid duplicating tens of thousands
                # of small files into the public summary directory before sealing them.
                n.body=ast.parse("if '_unit' in path.stem or path.stem.startswith('private_'): continue").body+n.body
            return self.generic_visit(n)
        def visit_Expr(self,n):
            if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='ResumeThread':
                return ast.parse('prelaunch(package,pi.pid,job,grant,user)\nk.ResumeThread(pi.thread)').body
            return self.generic_visit(n)
    fn=Adapt().visit(fn);namespace=dict(vars(old));namespace.update(r=proxy,selected_data=data,selected_code=code,prelaunch=hook)
    for index,node in enumerate(fn.body):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='receipt' for t in node.targets):
            fn.body[index+1:index+1]=ast.parse('receipt.update(mission='+repr(r.MISSION)+', phase='+repr(phase)+', synthetic_only='+repr(phase!='real_C')+', C_access_authorized='+repr(phase=='real_C')+', D_RELEASE_CONSUMED=False, D_EVALUATION_EXECUTED=False)').body
            break
    gs=dict(old.grant.__globals__);gs['r']=proxy;namespace['grant']=a.clone(old.grant,gs)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),namespace)
    namespace['main']()
    receipt=r.load(job/f'results/{phase}_launch_receipt.json')
    gatepath=job/f'results/{phase}/native/gate_result.json'
    return receipt,r.load(gatepath) if gatepath.exists() else None

def prepare_job(name):
    a=security();job=r.HERE/'jobs'/name;exports=job/'exports';exports.mkdir(parents=True,exist_ok=False)
    shutil.copytree(r.ROOT/'paper12_condition1/exports/runtime',exports/'runtime');a.protect(exports/'runtime')
    expected=r.load(r.ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256']
    for n,h in expected.items():
        if r.sha(exports/'runtime'/n)!=h:raise RuntimeError('FROZEN_RUNTIME_DRIFT')
    a.prepare(job/'.private')
    for name in ('source_canary.bin','key_canary.bin'):
        p=job/'.private'/name;p.write_bytes(b'SYNTHETIC_ENGINEERING_CANARY');a.protect(p)
    return job
