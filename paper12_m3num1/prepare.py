"""Trusted derivative creation: already authorized A export only, no extraction."""
import importlib.util
import shutil
import sys
from pathlib import Path
from datetime import datetime,timezone
import study as r


def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('num_scoped_atomic',r.PREVIOUS/'verified_atomic.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.verify_parity();module.require_custodian()
    return module


def guard():
    r.verify()
    policy=r.load(r.HERE/'implementation_registration.json')
    for name,digest in policy['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('NUMERICAL_CODE_CHANGED')
    if r.load(r.PREVIOUS/'results/M2/gate_result.json')['gate']!='PASS':raise RuntimeError('M2_PASS_REQUIRED')
    return policy


def main():
    r.verify();a=security()
    files=('prepare.py','launch.py','worker.py','numerical.py','test_numerical.py')
    r.save(r.HERE/'implementation_registration.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        sha256={n:r.sha(r.HERE/n) for n in files},source_requests=0),True)
    guard()
    import numpy as np
    src=r.PREVIOUS/'exports/development1'
    manifest=r.load(src/'manifest.json');issuer=r.load(r.PREVIOUS/'.private/development_export_issuer.json')
    if issuer['manifest_sha256']!=r.sha(src/'manifest.json'):raise RuntimeError('EXPORT_ISSUER_HASH')
    if manifest['compartments']!=['A','B']:raise RuntimeError('WRONG_PARENT_EXPORT')
    session=manifest['sessions'][0]
    if session['mouse_id']!='744912849' or session['session_id']!='766640955':raise RuntimeError('FROZEN_FIRST_MOUSE')
    path=src/session['file']
    if r.sha(path)!=session['sha256']:raise RuntimeError('PARENT_COUNT_HASH')
    target=r.HERE/'exports/training_only';target.mkdir(parents=True,exist_ok=False);a.protect(target)
    fields={}
    with np.load(path,allow_pickle=False) as z:
        for name in ('CA1_A','DG_A','conditions_A','orders_A','trial_ids_A','CA1_unit_ids','DG_unit_ids'):
            fields[name]=z[name]
    out=target/session['file'];np.savez(out,**fields);a.protect(out)
    derived=dict(session);derived['sha256']=r.sha(out);derived['trial_ids']={'A':session['trial_ids']['A']}
    r.save(target/'manifest.json',dict(group='development',compartments=['A'],sessions=[derived],
        ridge_normalization='per_unit_exposure',parent_manifest_sha256=r.sha(src/'manifest.json')),True)
    a.protect(target/'manifest.json')
    private=r.HERE/'.private';a.prepare(private)
    for name in ('source_canary.bin','key_canary.bin'):
        p=private/name
        with p.open('xb') as f:f.write(b'SYNTHETIC_NO_NEURAL_CONTENT')
        a.protect(p)
    oldruntime=list((r.PREVIOUS/'exports').glob('replay_probe_*/runtime'))
    if len(oldruntime)!=1:raise RuntimeError('RUNTIME_AMBIGUOUS')
    shutil.copytree(oldruntime[0],r.HERE/'exports/runtime')
    r.save(private/'training_issuer.json',dict(manifest_sha256=r.sha(target/'manifest.json'),
        count_sha256=r.sha(out),parent_manifest_sha256=r.sha(src/'manifest.json')),True)
    a.protect(private/'training_issuer.json')
    r.save(r.HERE/'results/training_export_receipt.json',dict(training_only=True,mouse_id=session['mouse_id'],
        session_id=session['session_id'],parent_manifest_sha256=r.sha(src/'manifest.json'),
        derivative_manifest_sha256=r.sha(target/'manifest.json'),derivative_count_sha256=r.sha(out),
        B_decoded=False,final_decoded=False,source_requests=0),True)
    print('A_ONLY_DERIVATIVE_READY; NO_B_CD_DECODE')


if __name__=='__main__':main()
