"""Repeat immutable native synthetic probe in distinct receipts/canary namespace."""
import ast
import common as r
import native_profile_probe as old_probe


def main():
    r.verify()
    tree=ast.parse((r.OLD/'native_profile_probe.py').read_text())
    function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
    mapping={'.private/native_probe_source.bin':'.private/transport_recovery1/canary_source.bin',
             '.private/native_probe_key.bin':'.private/transport_recovery1/canary_key.bin'}
    changed=[]
    class Rewrite(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str) and node.value in mapping:
                changed.append(node.value);return ast.copy_location(ast.Constant(mapping[node.value]),node)
            return node
    function=Rewrite().visit(function)
    if sorted(changed)!=sorted(mapping):raise RuntimeError('SYNTHETIC_PROBE_PATCH_SCOPE')
    import custodian
    private=r.OLD/'.private/transport_recovery1';private.mkdir(exist_ok=True);custodian.protect(private)
    namespace=dict(vars(old_probe));namespace['output_name']=lambda:'../paper12_transport1/results/isolation/native.json'
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),str(r.OLD/'native_profile_probe.py'),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
