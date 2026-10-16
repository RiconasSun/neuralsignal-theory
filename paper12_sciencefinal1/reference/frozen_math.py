"""Resolve exact verified original math bytes, without altering global module caches."""
import builtins
import hashlib
from pathlib import Path
import types

def load():
    here=Path(__file__).resolve().parent
    if (here/'math_sources.json').is_file():
        import json
        expected=json.loads((here/'math_sources.json').read_text());directory=here
    else:
        import json
        reg=json.loads((here.parent/'ops/evidence/2026-10-15/p12-d-production-path-readiness-1/registration.json').read_text())
        directory=here.parent/'paper12_predictive_v2'
        expected={Path(k).name:v for k,v in reg['source_sha256'].items() if Path(k).name in ('glm.py','nulls.py','null_cache.py','mouse_statistics.py')}
    modules={};original_import=builtins.__import__
    def verified_import(name,globals=None,locals=None,fromlist=(),level=0):
        if level==0 and name in expected:
            if name not in modules:raise ImportError('FROZEN_DEPENDENCY_ORDER')
            return modules[name]
        return original_import(name,globals,locals,fromlist,level)
    # Imports use module names, while the manifest uses filenames.
    module_names={Path(n).stem for n in expected}
    def route(name,globals=None,locals=None,fromlist=(),level=0):
        if level==0 and name in module_names:
            if name not in modules:raise ImportError('FROZEN_DEPENDENCY_ORDER')
            return modules[name]
        return original_import(name,globals,locals,fromlist,level)
    for name in ('glm','nulls','null_cache','mouse_statistics'):
        path=directory/(name+'.py');raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected[name+'.py']:raise PermissionError('FROZEN_MATH_HASH:'+name)
        module=types.ModuleType('p12_frozen_'+name);module.__file__=str(path)
        module.__dict__['__builtins__']=dict(vars(builtins),__import__=route)
        exec(compile(raw,str(path),'exec'),module.__dict__);modules[name]=module
    return modules
