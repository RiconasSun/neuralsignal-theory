"""Trusted controller; scientific A/B reads occur only in the native role."""
import ast
import importlib.util
import shutil
import sys
import study as r
def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('predictive_atomic',r.PREVIOUS/'verified_atomic.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);a.verify_parity();a.require_custodian();return a
def native(phase,data,code,hashes,a):
    spec=importlib.util.spec_from_file_location('predictive_native',r.OFFSET/'launch_phase.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    fn=next(n for n in ast.parse((r.OFFSET/'launch_phase.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='native_run')
    namespace=dict(vars(old));namespace['r']=r
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),namespace)
    return namespace['native_run'](phase,data,code,hashes,a)
def main():
    phase=sys.argv[1]
    if phase!='preflight':raise RuntimeError('NO_UNREGISTERED_PHASE')
    reg=r.load(r.HERE/'protocol_registration.json')
    if reg['protocol_sha256']!=r.sha(r.HERE/'PROTOCOL.md'):raise RuntimeError('FROZEN_PROTOCOL')
    if (r.HERE/f'{phase}_execution_registration.json').exists():raise RuntimeError('NO_PHASE_RETRY')
    a=security();exports=r.HERE/'exports';exports.mkdir(exist_ok=False)
    data=exports/'development_AB';source=r.OFFSET/'exports/M4_AB'
    if r.sha(source/'manifest.json')!='f5b3c745cd22459bf48e287a3f20b75b2c85151c896e5cb81df5182a8b0bcdb8':raise RuntimeError('FROZEN_AB_MANIFEST')
    shutil.copytree(source,data);a.protect(data)
    old=r.load(r.ROOT/'paper12_contgrad1/execution_registration.json')
    shutil.copytree(r.ROOT/'paper12_condition1/exports/runtime',exports/'runtime');a.protect(exports/'runtime')
    for name,digest in old['runtime_sha256'].items():
        if r.sha(exports/'runtime'/name)!=digest:raise RuntimeError('RUNTIME_HASH')
    a.prepare(r.HERE/'.private')
    for name in ('source_canary.bin','key_canary.bin'):
        p=r.HERE/'.private'/name;p.write_bytes(b'SYNTHETIC_ROLE_PROBE_ONLY');a.protect(p)
    code=exports/('code_'+phase);code.mkdir()
    for name in ('worker.py','selection.py','test_selection.py'):shutil.copy2(r.HERE/name,code/name)
    shutil.copy2(r.OLD/'native_analysis_check.py',code/'native_analysis_check.py')
    manifest=r.load(data/'manifest.json');sessions={s['session_id'] for s in manifest['sessions']}
    metadata=[u for u in r.load(r.ROOT/'paper12_curated_v1/locks/units.json') if u['session_id'] in sessions]
    r.save(code/'development_metadata.json',metadata)
    historical=r.load(r.ROOT/'paper12_m3num1/final_manifest.json')['sha256']
    rows=[];hashes={}
    keep=('seed','ridge','converged','optimizer_success','projected_gradient','training_LL_nats_per_unit_bin','validation_LL_nats_per_unit_bin','training_unit_bins','validation_unit_bins','mouse_id','session_id','region','kind','data_sha256','ridge_normalization')
    for p in sorted((r.ROOT/'paper12_m3num1/results/full').glob('*.json')):
        z=r.load(p)
        if z.get('family')!='baseline':continue
        digest=r.sha(p)
        if digest!=historical['results/full/'+p.name]:raise RuntimeError('M3_FROZEN_HASH')
        rows.append({k:z[k] for k in keep});hashes[p.name]=digest
    r.save(code/'baseline_records.json',rows)
    for name in ('offset_states.npz','offset_records.json','offset_bundle.json'):shutil.copy2(r.OFFSET/'exports/M4_code'/name,code/name)
    r.save(code/'policy.json',{'phase':phase,'mission':r.MISSION,'protocol_sha256':reg['protocol_sha256'],'expected_mice':13,'expected_m3':1638,'expected_offsets':78,'min_pairs':5,'min_mice':8})
    a.protect(code);code_hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/f'{phase}_execution_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_scientific_analysis':True,'base':r.BASE,'phase':phase,'code_sha256':code_hashes,'source_sha256':{name:r.sha(r.HERE/name) for name in ('worker.py','selection.py','test_selection.py','launch.py')},'M3_fit_sha256':hashes,'AB_manifest_sha256':r.sha(data/'manifest.json'),'runtime_sha256':old['runtime_sha256'],'offset_states_sha256':r.sha(code/'offset_states.npz'),'offset_records_sha256':r.sha(code/'offset_records.json'),'unit_metadata_source_sha256':r.sha(r.ROOT/'paper12_curated_v1/locks/units.json'),'protocol_registration_sha256':r.sha(r.HERE/'protocol_registration.json'),'new_fits':0,'final_access':False})
    receipt,gate=native(phase,data,code,code_hashes,a);print('PREFLIGHT',gate)
if __name__=='__main__':main()
