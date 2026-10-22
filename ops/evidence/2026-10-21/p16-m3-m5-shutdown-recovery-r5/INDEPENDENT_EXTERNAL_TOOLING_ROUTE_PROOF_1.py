"""Synthetic no-filesystem traps for the preserved external review-1 candidate."""
import ast,datetime,hashlib,importlib.util,json,tempfile
from pathlib import Path
from unittest.mock import patch
E=Path(__file__).resolve().parent
def H(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
sources={'reproduce_saved_external_review1_snapshot.py':'ecbaa256929c9c04b535d6b042acfcdfef2d105509497fe8744e36480bc8d18f','build_archive_external_review1_snapshot.py':'f81f6c1887ab3b972869d9398dc3c1b162cfd4e55a3516ce3f560813986e84b8'}
for name,digest in sources.items():assert H(E/name)==digest
m=module('independent_external_route_reproducer',E/'reproduce_saved_external_review1_snapshot.py');b=module('independent_external_route_builder',E/'build_archive_external_review1_snapshot.py')
proofs=[]
class UnguardedExists(RuntimeError):pass
parent=E.parents[3]/'_r5_independent_external_temp';parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='external_route_',dir=parent) as temporary:
    root=Path(temporary).resolve();assert root.parent==parent.resolve()
    for tool in [m,b]:tool.R=root;tool.P=root/'paper16_development_r5';tool.E=root/tool.EP
    m.P.mkdir();m.E.mkdir(parents=True)
    for label,tool,call in [('metadata_route',m,m.validate_terminal_metadata),('archive_builder_route',b,b.build)]:
        external=tool.E/'EXTERNAL_SCIENTIFIC_STOP.json';guarded=[];original=tool.local
        def tracked(name):guarded.append(name);return original(name)
        def trapped(path):
            if path==external:raise UnguardedExists('Synthetic exists trap; no actual target following')
            raise AssertionError('Unexpected filesystem exists probe')
        with patch.object(tool,'local',side_effect=tracked),patch.object(Path,'exists',trapped):
            try:call()
            except UnguardedExists:pass
            else:raise AssertionError('Expected preserved candidate to reach unguarded exists trap')
        assert external.relative_to(root).as_posix() not in guarded
        proofs.append({'entry':label,'observed':'External STOP exists reached before its local/no-follow guard','actual_target_access':False,'guarded_names_before_trap':guarded})
tree=ast.parse((E/'reproduce_saved_external_review1_snapshot.py').read_text(encoding='utf8'))
external=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='validate_external_terminal'][0]
unguarded=[node.lineno for node in ast.walk(external) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='exists' and isinstance(node.func.value,ast.BinOp)]
assert unguarded
proofs.append({'entry':'validate_external_terminal','observed':'Additional unguarded P/work/E exists call confirmed statically','source_lines':unguarded,'actual_target_access':False})
record={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','reviewer':'/root/r4_interruption_review','recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewed_preserved_source_sha256':sources,'finding':'P1_EXTERNAL_ROUTE_REPARSE_DENIAL_ORDER','proofs':proofs,'full_real_reproduction_or_archive_run':False,'real_saved_state_audits':0,'NPZ_decodes':0,'scientific_model_calls':0,'network_access':False,'source_modified':False}
target=E/'INDEPENDENT_EXTERNAL_TOOLING_ROUTE_PROOF_RESULT_1.json'
with target.open('x',encoding='utf8',newline='\n') as stream:json.dump(record,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps({'proofs':len(proofs),'result_sha256':H(target),'scientific_calls':0}))
