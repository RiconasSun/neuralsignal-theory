"""AST-extracted tests; only frozen public metadata is read, never private states."""
import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
P=R/'paper16_development_r6'
source=E/'PRIMARY_REUSE_AUDIT_R6.py'
entry=P/'audit_entry.py'
J=lambda path:json.loads(path.read_bytes())
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
registration=J(E/'PURE_REUSE_REPAIR_TEST_REGISTRATION_1.json')
for row in registration['sources']:
    assert H(R/row['path'])==row['sha256']
assert H(Path(__file__))==registration['test_sha256']
names={'require','local_file','load','sha','canonical_B0_targets'}
tree=ast.parse(source.read_bytes())
ns={'R':R,'E':E,'P':P,'O':R/'paper16_development_r3',
    'BASE':'e1aab9622a7e63b99335a529d8ad0107f611dc8c',
    'Path':Path,'PRIVATE_ALLOWED':False,'json':json,'hashlib':hashlib,'subprocess':subprocess}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(source),'exec'),ns)
tests=[]
def record(name,action,denied=False):
    try:action()
    except (RuntimeError,KeyError):
        if not denied:raise
    else:
        if denied:raise AssertionError('Expected denial: '+name)
    tests.append({'name':name,'status':'PASS'})
for origin in ['r3','r4','r5']:
    for fn in ['load','sha']:
        record('preapproval_'+fn+'_'+origin,lambda fn=fn,origin=origin:ns[fn](R/('paper16_development_'+origin)/'work/fits/must_not_open/RESULT.json'),True)
record('preapproval_array_outside_work',lambda:ns['load'](P/'never_open.npz'),True)
record('preapproval_fit_journal',lambda:ns['sha'](R/'paper16_development_r5/results/FIT_JOURNAL.jsonl'),True)
record('preapproval_public_source_allowed',lambda:ns['sha'](source))
coverage=ns['canonical_B0_targets']()
assert coverage['expected_mouse_unit_pairs']==coverage['unique_actual_pairs']==coverage['canonical_path_hashes']==216
record('canonical216_public_only',lambda:None)
original_load=ns['load'];targets=original_load(P/'REUSE_CANDIDATES.json')
for mutation in ['duplicate','missing','wrong_unit','wrong_path','wrong_hash','bool_unit']:
    altered=copy.deepcopy(targets)
    b=altered['B0_targets']
    if mutation=='duplicate':b[:]=[copy.deepcopy(b[0]) for _ in range(216)]
    if mutation=='missing':b.pop()
    if mutation=='wrong_unit':b[0]['unit_id']=-1
    if mutation=='wrong_path':b[0]['result_path']='paper16_development_r3/work/B0/other/RESULT.json'
    if mutation=='wrong_hash':b[0]['result_sha256']='0'*64
    if mutation=='bool_unit':b[0]['unit_id']=True
    ns['load']=lambda path,altered=altered:altered if path==P/'REUSE_CANDIDATES.json' else original_load(path)
    record('canonical216_reject_'+mutation,lambda:ns['canonical_B0_targets'](),True)
ns['load']=original_load
etree=ast.parse(entry.read_bytes());en={'hashlib':hashlib}
exec(compile(ast.Module(body=[n for n in etree.body if isinstance(n,ast.FunctionDef) and n.name=='exact_source'],type_ignores=[]),str(entry),'exec'),en)
raw=b'PUBLIC_SYNTHETIC_SENTINEL=1\n';ref={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
record('selected_source_exact_bytes',lambda:en['exact_source'](ref,raw))
record('selected_source_mutation_denied',lambda:en['exact_source'](ref,raw+b'#altered'),True)
record('selected_source_wrong_hash_denied',lambda:en['exact_source']({**ref,'sha256':'0'*64},raw),True)
record('selected_source_bool_size_denied',lambda:en['exact_source']({**ref,'bytes':True},raw),True)
main=next(n for n in etree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
text=ast.unparse(main)
assert text.index("approval['decision']")<text.index('target.read_bytes()')<text.index('exec(compile(verified')
record('entry_approval_and_verified_bytes_precede_execution',lambda:None)
result={'mission':registration['mission'],'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'test_sha256':H(Path(__file__)),'sources':registration['sources'],'test_count':len(tests),'tests':tests,
        'failures':0,'public_canonical_B0_coverage':coverage,'private_state_reads':0,
        'actual_auditors_imported_or_executed':False,'model_calls':0,'native_lifecycle_calls':0}
with (E/'PURE_REUSE_REPAIR_TEST_RESULT_1.json').open('x',encoding='utf8',newline='\n') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'tests':len(tests),'failures':0,'private_reads':0,'result_sha256':H(E/'PURE_REUSE_REPAIR_TEST_RESULT_1.json')}))
