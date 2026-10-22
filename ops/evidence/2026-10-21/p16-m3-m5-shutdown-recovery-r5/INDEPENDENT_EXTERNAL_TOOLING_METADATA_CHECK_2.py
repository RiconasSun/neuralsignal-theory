"""Exact closure source/test receipt joins and normal-path AST preservation."""
import ast,datetime,hashlib,json,os
from pathlib import Path
R=Path.cwd().resolve();E=R/'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5'
def J(p):return json.loads(p.read_bytes())
def H(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def C(v,message):
    if not v:raise AssertionError(message)
def ref(row):
    p=R/row['path'];C(p.resolve().is_relative_to(R),'Repository-local receipt');C(H(p)==row['sha256'] and p.stat().st_size==row['bytes'],'Current exact receipt/source '+row['path']);return p
def functions(path):return {n.name:n for n in ast.parse(path.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef)}
def dump(nodes):return ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False)
expected={'reproduce_saved.py':'b0f5723264693184cf800309feeba89031fb13a5003567e698579cc2867fc476','build_archive.py':'a673f2664424e30f82f451c0db35830e79b9882d3b92e513fea4fe5bf899960e','test_external_closure.py':'a0c60c58c1bc9328712377e00d571c021e3098f6debe14fb38db70c41f0c6c81'}
for name,digest in expected.items():C(H(E/name)==digest,'Exact independently reviewed external repair candidate')
handoff_path=E/'EXTERNAL_TOOLING_HANDOFF_2.json';handoff=J(handoff_path)
for key in ['sources','preserved_candidate_sources']:
    for row in handoff[key]:ref(row)
ref(handoff['runtime'])
checks=[]
for check in handoff['checks']:
    C(type(check['actual_native_exit_code']) is int and check['actual_native_exit_code']==0,'Actual retained native synthetic exit')
    result=J(ref(check['result']));ref(check['native_output'])
    checks.append({'tests':check['synthetic_test_count'],'native_exit':0,'result_sha256':check['result']['sha256'],'native_log_sha256':check['native_output']['sha256']})
independent_path=E/'EXTERNAL_TOOLING_SYNTHETIC_TEST_RESULT_1041.json';independent=J(independent_path)
C(independent['test_count']==len(independent['tests'])==69 and independent['failed']==0 and all(row['PASS'] is True for row in independent['tests']),'Independent actual69 focused synthetic checks')
C(independent['source_sha256']==expected and independent['real_saved_bundle_reads']==independent['real_archive_or_reproduction_runs']==independent['new_fits_derivatives_scores']==independent['NPZ_decodes']==0,'Same exact sources; synthetic-only independent execution')
old=functions(E/'reproduce_saved_preexternal_snapshot.py');new=functions(E/'reproduce_saved.py')
unchanged=[];changed=[]
for name,node in old.items():
    if name in ['stage_and_native','validate_terminal_metadata','run']:continue
    C(name in new and ast.dump(node,include_attributes=False)==ast.dump(new[name],include_attributes=False),'Preserved native parser/numerical helper '+name);unchanged.append(name)
terminal_body=[node for node in new['validate_terminal_metadata'].body if not (isinstance(node,ast.If) and any(isinstance(child,ast.Return) and isinstance(child.value,ast.Call) and isinstance(child.value.func,ast.Name) and child.value.func.id=='validate_external_terminal' for child in node.body))]
C(dump(old['validate_terminal_metadata'].body)==dump(terminal_body),'Native terminal validator unchanged after guarded external dispatch')
run_body=[node for node in new['run'].body if not (isinstance(node,ast.If) and isinstance(node.test,ast.Call) and isinstance(node.test.func,ast.Attribute) and node.test.func.attr=='get' and isinstance(node.test.func.value,ast.Name) and node.test.func.value.id=='terminal_meta')]
C(dump(old['run'].body)==dump(run_body),'Normal native run unchanged after metadata-only external early return')
bo=functions(E/'build_archive_preexternal_snapshot.py')['build'];bn=functions(E/'build_archive.py')['build']
root_index=lambda body:next(i for i,node in enumerate(body) if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='roots' for t in node.targets))
oi,ni=root_index(bo.body),root_index(bn.body)
branch=next(node for node in bn.body if isinstance(node,ast.If) and isinstance(node.test,ast.Name) and node.test.id=='external_present')
C(dump(branch.orelse)==dump(bo.body[2:oi]),'Original builder native precondition branch retained exactly')
C(dump(bn.body[ni:])==dump(bo.body[oi:]),'Original full inventory/reference/exclusion/create-only builder body retained exactly')
C(not (R/'paper16_development_r5/LOCAL_ARCHIVE_MANIFEST.json').exists(),'No real archive executed before tooling acceptance')
result={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','reviewer':'/root/r4_interruption_review','recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':expected,'handoff_sha256':H(handoff_path),'primary_fresh_checks_not_summed':checks,'independent_synthetic_tests':69,'independent_synthetic_result_sha256':H(independent_path),'unchanged_native_helper_functions':unchanged,'normal_native_terminal_run_and_builder_retained_by_AST':True,'scientific_model_imports_or_calls':0,'NPZ_decodes':0,'real_saved_state_audits_repeated':0,'real_archive_or_reproduction_executed':False,'decision':'PASS_EXACT_EXTERNAL_TOOLING_METADATA_AND_AST_BINDINGS_ONLY'}
target=E/'INDEPENDENT_EXTERNAL_TOOLING_METADATA_CHECK_RESULT_2.json'
with target.open('x',encoding='utf8',newline='\n') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(result,indent=2))
