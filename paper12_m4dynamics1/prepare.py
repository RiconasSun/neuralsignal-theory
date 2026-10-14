import importlib.util
import shutil
import sys
import study as r
from controls import verify

def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('dynamics_verified_atomic',r.PREVIOUS/'verified_atomic.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);a.verify_parity();a.require_custodian();return a

def main():
    verify();a=security()
    r.save(r.HERE/'implementation_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_data_access=True,
        sha256={p.name:r.sha(p) for p in r.HERE.glob('*.py')}))
    exports=r.HERE/'exports';exports.mkdir(exist_ok=False)
    source=r.OFFSET/'exports/training_A';issuer=r.load(r.OFFSET/'.private/training_issuer.json')
    manifest=r.load(source/'manifest.json')
    if r.sha(source/'manifest.json')!=issuer['manifest_sha256'] or issuer['manifest_sha256']!=r.load(r.OFFSET/'results/training_derivation_receipt.json')['manifest_sha256'] or manifest['compartments']!=['A'] or len(manifest['sessions'])!=13:
        raise RuntimeError('FROZEN_A_MANIFEST_REQUIRED')
    for s in manifest['sessions']:
        if r.sha(source/s['file'])!=s['sha256']:raise RuntimeError('FROZEN_A_INPUT_CHANGED')
    data=exports/'training_A';shutil.copytree(source,data);a.protect(data)
    runtime=exports/'runtime';shutil.copytree(r.OFFSET/'exports/runtime',runtime);a.protect(runtime)
    for name,digest in issuer['runtime_sha256'].items():
        if r.sha(runtime/name)!=digest:raise RuntimeError('RUNTIME_CHANGED')
    private=r.HERE/'.private';a.prepare(private)
    for name in ('source_canary.bin','key_canary.bin'):
        path=private/name;path.write_bytes(b'SYNTHETIC_NO_NEURAL_CONTENT');a.protect(path)
    keys=('mouse_id','session_id','region','family','size','ridge','seed','converged','optimizer_success','optimizer_message','iterations','objective_calls','projected_gradient','penalized_training_objective','training_LL_nats_per_unit_bin','model_specific_parameters','training_unit_bins','bound_hits','ridge_normalization')
    # Custodian filters saved records; validation values never exported to diagnosis.
    oldrows=r.load(r.OFFSET/'results/M4/native/comparison_rows.json')['rows']
    rows=[{k:v[k] for k in keys} for v in oldrows if v['family'] in ('Discrete','Continuous','Hybrid')]
    if len(rows)!=216 or any('validation' in k for row in rows for k in row):raise RuntimeError('EXACT_TRAINING_ONLY_ORIGINAL_ROSTER')
    r.save(r.HERE/'original_training_diagnostics.json',dict(rows=rows,source_sha256=r.sha(r.OFFSET/'results/M4/native/comparison_rows.json'),validation_fields_exported=False))
    r.save(private/'training_issuer.json',issuer);a.protect(private/'training_issuer.json')
    r.save(r.HERE/'results/preparation_receipt.json',dict(A_manifest_sha256=issuer['manifest_sha256'],runtime_sha256=issuer['runtime_sha256'],session_count=13,
        reused_only=True,source_requests=0,new_extraction=0,M3_fits=0,offset_fits=0,validation_values_exported=False,final_access=False))

if __name__=='__main__':main()
