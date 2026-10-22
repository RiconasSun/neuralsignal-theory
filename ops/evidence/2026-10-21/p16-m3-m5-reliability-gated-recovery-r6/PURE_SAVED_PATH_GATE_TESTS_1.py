"""AST-only saved-verifier regression with fake stat/open traps; no data reads."""
import ast
import hashlib
import io
import json
from pathlib import Path
import stat
from types import SimpleNamespace
from unittest.mock import patch

R=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
source=R/'paper16_development_r6/reproduce_saved.py'
reg=json.loads((E/'PURE_SAVED_PATH_GATE_REGISTRATION_1.json').read_bytes())
assert hashlib.sha256(source.read_bytes()).hexdigest()==reg['source_sha256']
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==reg['test_sha256']
tree=ast.parse(source.read_bytes())
ns={'R':R,'stat':stat,'hashlib':hashlib,'json':json}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['C','public','H','J']],type_ignores=[]),str(source),'exec'),ns)
tests=[]
cases=[('traversal',R/'..'/'outside.txt',None),('outside',R.parent/'outside.txt',None),
       ('symlink_text',R/'link.txt','link.txt'),('junction_parent',R/'linkdir'/'public.txt','linkdir'),
       ('root_reparse',R/'public.txt',R.name),('array',R/'private.npz',None),
       ('private_work',R/'paper16_development_r5'/'work'/'private.json',None),
       ('case_insensitive_work',R/'paper16_development_r5'/'WORK'/'private.json',None),
       ('local_only',R/'ops'/'LOCAL_ONLY'/'private.txt',None)]
for name,path,redirect in cases:
    def fake_stat(p,redirect=redirect):
        islink=p.name==redirect
        return SimpleNamespace(st_mode=stat.S_IFLNK if islink and redirect=='link.txt' else stat.S_IFREG,
                               st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT if islink else 0)
    with patch.object(Path,'lstat',fake_stat),patch.object(Path,'open',side_effect=AssertionError('FORBIDDEN_DATA_OPEN')) as opened:
        try:ns['H'](path)
        except AssertionError as exc:assert 'FORBIDDEN_DATA_OPEN' not in str(exc)
        else:raise AssertionError('Path unexpectedly accepted: '+name)
        assert opened.call_count==0
    tests.append({'name':name,'status':'PASS','actual_data_opens':0})
for kind,raw in [('H',b'public synthetic text'),('J',b'{"public":true}')]:
    with patch.object(Path,'lstat',return_value=SimpleNamespace(st_mode=stat.S_IFREG,st_file_attributes=0)),patch.object(Path,'open',return_value=io.BytesIO(raw)):
        value=ns[kind](R/'public.txt')
        assert value==(hashlib.sha256(raw).hexdigest() if kind=='H' else {'public':True})
    tests.append({'name':'safe_public_'+kind,'status':'PASS','actual_data_opens':0})
result={'mission':reg['mission'],'scope':'AST extraction and fake stat/open only',
        'source_sha256':reg['source_sha256'],'test_sha256':reg['test_sha256'],
        'tests':tests,'test_count':len(tests),'failures':0,'actual_array_or_journal_opens':0,
        'actual_verifier_main_executed':False,'native_auditors_models_executed':False}
with (E/'PURE_SAVED_PATH_GATE_RESULT_1.json').open('x',encoding='utf8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'tests':len(tests),'failures':0,'scope':result['scope']}))
