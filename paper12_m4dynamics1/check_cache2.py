import ast
import sys
import study as r

def main():
    r.save(r.HERE/'cache_registration2.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_testing=True,
        reason='Independent review P1: cache must not narrow original count domain; fallback original PMF above cache range',
        previous_registration_sha256=r.sha(r.HERE/'cache_registration.json'),
        sha256={n:r.sha(r.HERE/n) for n in ('oracle.py','oracle_cached.py','oracle_cached_v1.py.txt','check_cache.py','check_cache2.py')},active_replay_changed=False))
    tree=ast.parse((r.HERE/'check_cache.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    fn.body=fn.body[1:]
    class Output(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='results/cache_equivalence.json':return ast.copy_location(ast.Constant('results/cache_equivalence2.json'),n)
            return n
    fn=Output().visit(fn)
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('registered_cache_checks',r.HERE/'check_cache.py');module=module_from_spec(spec);spec.loader.exec_module(module)
    ns=dict(vars(module));exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),ns);ns['main']()
    import numpy as np
    import oracle_cached as fast
    import oracle_original as old
    y=np.array([1000001.,2000000.]);eta=np.array([-.3,5.])
    assert np.array_equal(fast.pmf(y,eta),old.pmf(y,eta))
    r.save(r.HERE/'results/cache_fallback.json',dict(gate='PASS',counts=[1000001,2000000],exact_original_fallback=True,synthetic_only=True))

if __name__=='__main__':main()
