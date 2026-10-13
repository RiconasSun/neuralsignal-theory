import importlib.util
import shutil
import sys
import study as r


def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('offset_verified_atomic',r.PREVIOUS/'verified_atomic.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);a.verify_parity();a.require_custodian()
    return a


def main():
    r.verify();a=security()
    r.save(r.HERE/'implementation_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        source_sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in [r.M3/'numerical.py',r.M3/'test_numerical.py',r.PREVIOUS/'task_offset.py',
            r.OLD/'baseline_features.py',r.OLD/'baseline_fit.py',r.OLD/'native_analysis_check.py',r.OLD/'launch_analysis.py']},
        local_sha256={p.name:r.sha(p) for p in r.HERE.glob('*.py')},before_A_derivation=True),True)
    source=r.HARNESS/'exports/development_AB';manifest=r.load(source/'manifest.json')
    if r.sha(source/'manifest.json')!=r.load(r.HARNESS/'execution_registration.json')['input_manifest_sha256'] or manifest['group']!='development' or manifest['compartments']!=['A','B'] or len(manifest['sessions'])!=13:
        raise RuntimeError('FROZEN_PARENT_AB_REQUIRED')
    import numpy as np
    exports=r.HERE/'exports';exports.mkdir(exist_ok=False);data=exports/'training_A';data.mkdir();a.protect(data)
    derived=[]
    for session in manifest['sessions']:
        old=source/session['file']
        if r.sha(old)!=session['sha256']:raise RuntimeError('PARENT_AB_HASH')
        with np.load(old,allow_pickle=False) as z:
            values={k:z[k] for k in ('CA1_A','DG_A','conditions_A','orders_A','trial_ids_A','CA1_unit_ids','DG_unit_ids')}
        target=data/session['file'];np.savez(target,**values);a.protect(target)
        item=dict(session);item.update(sha256=r.sha(target),parent_AB_sha256=session['sha256'],trial_ids={'A':session['trial_ids']['A']});derived.append(item)
    r.save(data/'manifest.json',dict(group='development',compartments=['A'],sessions=derived,ridge_normalization='per_unit_exposure',parent_manifest_sha256=r.sha(source/'manifest.json')),True);a.protect(data/'manifest.json')
    runtime=exports/'runtime';shutil.copytree(r.HARNESS/'exports/runtime',runtime);a.protect(runtime)
    runtime_hashes=r.load(r.M3/'optimizer_amendment.json')['runtime_sha256']
    for name,digest in runtime_hashes.items():
        if r.sha(runtime/name)!=digest:raise RuntimeError('VERIFIED_RUNTIME_HASH')
    private=r.HERE/'.private';a.prepare(private)
    for name in ('source_canary.bin','key_canary.bin'):
        path=private/name
        with path.open('xb') as f:f.write(b'SYNTHETIC_NO_NEURAL_CONTENT')
        a.protect(path)
    r.save(private/'training_issuer.json',dict(manifest_sha256=r.sha(data/'manifest.json'),runtime_sha256=runtime_hashes),True);a.protect(private/'training_issuer.json')
    r.save(r.HERE/'results/training_derivation_receipt.json',dict(manifest_sha256=r.sha(data/'manifest.json'),parent_manifest_sha256=r.sha(source/'manifest.json'),
        session_count=13,compartments=['A'],B_neural_arrays_decoded=False,final_decoded=False,source_requests=0,M3_fits_repeated=0),True)
    print('THIRTEEN_A_ONLY_DERIVATIVES_READY; NO_NEW_SOURCE_OR_M3_FITS')


if __name__=='__main__':main()
