"""Fresh-process code/runtime attestation for the actual production roles."""
import hashlib
import json
from pathlib import Path
import sys

def bootstrap(deps,code):
    if any(n in sys.modules for n in ('glm','nulls','null_cache','mouse_statistics','selection')):raise PermissionError('EMPTY_SCIENTIFIC_MODULE_CACHE_REQUIRED')
    code=Path(code);expected=json.loads((code/'bootstrap_manifest.json').read_text())
    if {p.name for p in code.iterdir() if p.is_file()}!=set(expected)|{'bootstrap_manifest.json'}:raise PermissionError('EXACT_NATIVE_CODE_ROSTER')
    for name,h in expected.items():
        if hashlib.sha256((code/name).read_bytes()).hexdigest()!=h:raise PermissionError('NATIVE_CODE_HASH:'+name)
    sys.path[:0]=[str(code),str(deps)]
    return {'fresh_process':True,'scientific_cache_empty':True,'code_files':len(expected)}

def runtime_check(data,deps):
    expected=json.loads((Path(data)/'runtime_identity.json').read_text())['runtime_sha256'];root=Path(deps).parent
    for name,h in expected.items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=h:raise PermissionError('NATIVE_RUNTIME_HASH:'+name)
    return {'files':len(expected),'verified':True}
