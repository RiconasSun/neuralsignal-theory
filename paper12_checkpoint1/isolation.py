"""Immutable native security harness adapted only to synthetic candidate paths."""
import ast
import sys
import shutil
import uuid
import re
from pathlib import Path
import study as r
from history_guard import verify as verify_history
from custody_security import protect,require_custodian,check_path
from atomic_checkpoint import read
import native_profile_probe as original


def main():
    verify_history();require_custodian()
    native_path=r.HERE/'results/native.json'
    output='results/isolation.json';root=r.HERE/'exports/native_probe'
    if '--native' in sys.argv:
        native_path=check_path(Path(sys.argv[sys.argv.index('--native')+1]))
        output=check_path(Path(sys.argv[sys.argv.index('--output')+1])).relative_to(r.HERE).as_posix()
        root=r.HERE/'exports'/('replay_probe_'+uuid.uuid4().hex)
    native=r.load(native_path)
    if native['synthetic_only'] is not True or not re.fullmatch(r'run_[0-9a-f]{32}',native['synthetic_run_namespace']):
        raise RuntimeError('SYNTHETIC_RECEIPT_IDENTITY_INVALID')
    checkpoint=r.HERE/'.private'/native['synthetic_run_namespace']/'main/trial_0/block.checkpoint'
    if not checkpoint.exists():raise RuntimeError('SYNTHETIC_CHECKPOINT_MISSING')
    runtime=root/'runtime';runtime.mkdir(parents=True,exist_ok=False)
    archived_runtime=r.ROOT/'paper12_custody1/exports/native_probe/runtime'
    for name in ('base','deps'):
        shutil.copytree(archived_runtime/name,runtime/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    tree=ast.parse((r.ROOT/'paper12_custody1/native_profile_probe.py').read_text())
    function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
    counts=[]
    class Adapt(ast.NodeTransformer):
        def visit_Assign(self,node):
            node=self.generic_visit(node)
            if len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
                name=node.targets[0].id
                if name=='root':node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(root))],keywords=[]);counts.append('exports_root')
                if name=='source':node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(checkpoint))],keywords=[]);counts.append('source')
            if len(node.targets)==1 and isinstance(node.targets[0],ast.Subscript) and isinstance(node.targets[0].value,ast.Name) and node.targets[0].value.id=='result' and isinstance(node.targets[0].slice,ast.Constant) and node.targets[0].slice.value=='host_positive_reads':
                node.value=ast.parse('checkpoint_positive(source) and len(key.read_bytes())==32',mode='eval').body;counts.append('host_positive_oracle')
            return node
        def visit_For(self,node):
            node=self.generic_visit(node)
            if isinstance(node.target,ast.Name) and node.target.id=='p' and isinstance(node.iter,ast.Tuple) and [getattr(x,'id',None) for x in node.iter.elts]==['source','key']:
                node.iter=ast.Tuple(elts=[ast.Name(id='key',ctx=ast.Load())],ctx=ast.Load());counts.append('no_source_overwrite')
            return node
        def visit_BinOp(self,node):
            node=self.generic_visit(node)
            if isinstance(node.op,ast.Div) and isinstance(node.right,ast.Constant) and node.right.value=='runtime_canary.py' and isinstance(node.left,ast.Attribute) and isinstance(node.left.value,ast.Name) and node.left.value.id=='r':
                node.left=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(r.ROOT/'paper12_custody1'))],keywords=[]);counts.append('original_canary_code')
            return node
    function=Adapt().visit(function)
    if sorted(counts)!=sorted(('exports_root','source','host_positive_oracle','no_source_overwrite','original_canary_code')):raise RuntimeError('ISOLATION_ADAPTER_SCOPE')
    first=native['noninjected_commits'][0]
    def checkpoint_positive(path):
        return len(read(path,dict(dataset='synthetic',version=1,block=0),first['receipt']['body_sha256']))==first['payload_bytes']
    namespace=dict(vars(original));namespace.update(r=r,protect=protect,checkpoint_positive=checkpoint_positive,output_name=lambda:output)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),str(r.HERE/'isolation.py'),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
