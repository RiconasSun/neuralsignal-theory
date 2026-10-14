"""Trusted custodian; original native zero-capability launcher retained."""
import ast
import importlib.util
import shutil
import sys
import study as r

def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('conditioning_atomic',r.PREVIOUS/'verified_atomic.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);a.verify_parity();a.require_custodian();return a
def native(phase,data,code,hashes,a):
    spec=importlib.util.spec_from_file_location('conditioning_launcher',r.OFFSET/'launch_phase.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    fn=next(n for n in ast.parse((r.OFFSET/'launch_phase.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='native_run')
    class Scope(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='Training-only offset ':return ast.copy_location(ast.Constant('Bounded Conditioning Optimizer '),n)
            return n
    fn=Scope().visit(fn);namespace=dict(vars(old));namespace['r']=r
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),__file__,'exec'),namespace)
    receipt,gate=namespace['native_run'](phase,data,code,hashes,a)
    source=r.HERE/receipt['output_directory'];public=r.HERE/f'results/{phase}/native'
    # Native core already copied JSON; protected npz arrays stay protected.
    for p in source.glob('*.json'):
        if r.sha(p)!=r.sha(public/p.name):raise RuntimeError('PUBLIC_OUTPUT_BYTES')
    return receipt,gate

def main():
    phase=sys.argv[1]
    if phase not in ('audit','A','B','C'):raise RuntimeError('NO_UNREGISTERED_CANDIDATE')
    registration=r.load(r.HERE/('audit_source_registration.json' if phase=='audit' else 'trial_registration.json'))
    for name,digest in registration['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('PREREGISTERED_SOURCE_CHANGED:'+name)
    if (r.HERE/f'{phase}_execution_registration.json').exists():raise RuntimeError('NO_PHASE_RETRY')
    a=security();old=r.load(r.GRAD/'execution_registration.json');exports=r.HERE/'exports'
    if phase=='audit':
        exports.mkdir(exist_ok=False);shutil.copytree(r.GRAD/'exports/training_A',exports/'training_A');a.protect(exports/'training_A');shutil.copytree(r.GRAD/'exports/runtime',exports/'runtime');a.protect(exports/'runtime');a.prepare(r.HERE/'.private')
        for name in ('source_canary.bin','key_canary.bin'):
            p=r.HERE/'.private'/name;p.write_bytes(b'SYNTHETIC_ROLE_PROBE_ONLY');a.protect(p)
    data=exports/'training_A'
    if r.sha(data/'manifest.json')!=old['A_manifest_sha256']:raise RuntimeError('FROZEN_A_HASH')
    for session in r.load(data/'manifest.json')['sessions']:
        if r.sha(data/session['file'])!=session['sha256']:raise RuntimeError('FROZEN_A_BYTES')
    for name,digest in old['runtime_sha256'].items():
        if r.sha(exports/'runtime'/name)!=digest:raise RuntimeError('FROZEN_RUNTIME')
    code=exports/('code_'+phase);code.mkdir(exist_ok=False)
    for name in ('model_math.py','predictive_models.py','predictive_models_code1.py','r2_models.py','baseline_features.py','frozen_offset.py','native_analysis_check.py','offset_bundle.json','offset_records.json','offset_states.npz','oracle.py','oracle_original.py','preserved_failure.json'):
        src=r.GRAD/'exports/code_diagnostic'/name
        if r.sha(src)!=old['code_sha256'][name]:raise RuntimeError('IMMUTABLE_MATH_OFFSET_CHECKER')
        shutil.copy2(src,code/name)
    for name in ('worker.py','conditioning.py','policies.py','independent_ad.py','test_conditioning.py','saved_vectors.json'):shutil.copy2(r.HERE/name,code/name)
    if phase=='audit':shutil.copy2(r.HERE/'audit_protocol.json',code/'policy.json')
    else:
        audit_receipt=r.load(r.HERE/'results/audit_launch_receipt.json');audit_gate=r.load(r.HERE/'results/audit/native/gate_result.json')
        if audit_receipt['exit_code']!=0 or audit_receipt['timed_out'] or audit_gate['gate']!='PASS' or audit_gate['new_optimization_fits']:raise RuntimeError('AUDIT_FIRST_GATE')
        for name,digest in registration['audit_sha256'].items():
            if r.sha(r.HERE/name)!=digest:raise RuntimeError('PREREGISTERED_AUDIT_CHANGED')
        protocol=r.load(r.HERE/'candidate_protocol.json');candidate=next(z for z in protocol['candidates'] if z['id']==phase)
        r.save(code/'policy.json',dict(phase='candidate',candidate=candidate,S_sha256=protocol['S_sha256'],initial_theta_sha256=protocol['initial_theta_sha256']))
        shutil.copy2(r.HERE/'results/audit/native/scale.json',code/'scale.json')
    a.protect(code);hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()}
    r.save(r.HERE/f'{phase}_execution_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_real_execution=True,phase=phase,base=r.BASE,code_sha256=hashes,A_manifest_sha256=old['A_manifest_sha256'],runtime_sha256=old['runtime_sha256'],source_registration_sha256=r.sha(r.HERE/('audit_source_registration.json' if phase=='audit' else 'trial_registration.json')),validation_access=False,final_access=False,offset_refits=0))
    receipt,gate=native(phase,data,code,hashes,a);print('PHASE_COMPLETE',phase,gate)

if __name__=='__main__':main()
