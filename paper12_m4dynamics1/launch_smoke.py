"""Future registered adapter: identical oracle, cached factorial constants only."""
import ast
import sys
import study as r
import launch as original
from controls import completed,verify

def main():
    verify();bindings=completed('diagnosis')
    if r.load(r.HERE/'results/cache_equivalence2.json')['gate']!='PASS' or r.load(r.HERE/'results/cache_fallback.json')['gate']!='PASS':raise RuntimeError('CACHE_EQUIVALENCE_REQUIRED')
    cache=r.load(r.HERE/'cache_registration2.json')
    for name,digest in cache['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('CACHE_SOURCE_CHANGED')
    amendment=r.load(r.HERE/'optimizer_amendment.json')
    if amendment['diagnosis_bindings']!=bindings:raise RuntimeError('DIAGNOSIS_BINDINGS_CHANGED')
    tree=ast.parse((r.HERE/'launch.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    loops=[i for i,n in enumerate(fn.body) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and ast.unparse(n.iter)=='sources.items()']
    if len(loops)!=2:raise RuntimeError('REGISTERED_LAUNCHER_LAYOUT_REQUIRED')
    point=loops[-1]
    fn.body[point:point]=ast.parse("sources['oracle_original.py']=r.HERE/'oracle.py'\nsources['oracle.py']=r.HERE/'oracle_cached.py'").body
    transformed=ast.unparse(fn)
    r.save(r.HERE/'smoke_adapter_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_new_fits=True,
        adapter_sha256=r.sha(__file__),original_launcher_sha256=r.sha(r.HERE/'launch.py'),cache_registration_sha256=r.sha(r.HERE/'cache_registration2.json'),
        transformed_AST_sha256=r.hashlib.sha256(transformed.encode()).hexdigest(),optimizer_amendment_sha256=r.sha(r.HERE/'optimizer_amendment.json'),
        diagnostic_bindings=bindings,only_change='Independent factorial-term cache with original PMF fallback; optimization/objective/model unchanged',final_access=False))
    sys.argv=[sys.argv[0],'smoke'];ns=dict(vars(original));exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),ns);ns['main']()

if __name__=='__main__':main()
