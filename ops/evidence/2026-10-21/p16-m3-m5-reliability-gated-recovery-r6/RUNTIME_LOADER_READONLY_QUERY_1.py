"""Read-only identity query. No child creation, fixture or model imports."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
def identity(value):
    p=Path(value)
    with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    return {'path':str(p),'sha256':digest,'bytes':p.stat().st_size}
result={'mission':'P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6',
        'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sys_executable':identity(sys.executable),
        'sys_base_executable':identity(sys._base_executable),
        'version':sys.version,'prefix':sys.prefix,'base_prefix':sys.base_prefix,
        'stdlib_os':str(Path(__import__('os').__file__)),
        'child_created_by_query':False,'WinAPI_fixture_calls':0,
        'model_imports':0,'neural_state_reads':0}
with (E/'RUNTIME_LOADER_READONLY_RESULT_1.json').open('x',encoding='utf8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
