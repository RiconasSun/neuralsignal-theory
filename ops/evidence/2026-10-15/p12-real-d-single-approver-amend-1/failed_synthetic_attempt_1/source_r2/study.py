"""Frozen source verification, synthetic-only bundles and append-only execution records."""
from pathlib import Path
import shutil
from .common import *

ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'paper12_singleowner1'
EVIDENCE=ROOT/'ops/evidence/2026-10-15/p12-real-d-single-approver-amend-1'
SAVED=ROOT/'paper12_controls1/jobs/saved_v2_9546086888504515998/exports/saved'
RUNTIME=ROOT/'paper12_condition1/exports/runtime'

def source_hashes():return {p.name:sha(p) for p in sorted(HERE.glob('*.py'))}|{p.name:sha(p) for p in sorted(HERE.glob('*.ps1'))}

def verify():
    registration=read_json(EVIDENCE/'registration.json');check_hashes(ROOT,registration['source_sha256'])
    freeze=read_json(HERE/'source_freeze.json')
    if source_hashes()!=freeze['source_sha256']:raise PermissionError('PRODUCTION_SOURCE_FREEZE_DRIFT')
    return registration

def bundle(path,role):
    path.mkdir(parents=True)
    for p in HERE.glob('*.py'):shutil.copyfile(p,path/p.name)
    frozen={'release_control.py':ROOT/'paper12_controls1/release_control.py','test_controller.py':ROOT/'paper12_controls1/test_controller.py','access_check.py':ROOT/'paper12_controls1/access_check.py','selection.py':ROOT/'paper12_predictive_v2/selection.py','native_analysis_check.py':ROOT/'paper12_custody1/native_analysis_check.py'}
    for name in ('glm','nulls','null_cache','mouse_statistics'):frozen[name+'.py']=ROOT/('paper12_predictive_v2/'+name+'.py')
    for name,source in frozen.items():shutil.copyfile(source,path/name)
    shutil.copyfile(HERE/(role+'_worker.py'),path/'worker.py')
    new(path/'math_sources.json',{name:sha(source) for name,source in frozen.items() if name in ('glm.py','nulls.py','null_cache.py','mouse_statistics.py')})
    new(path/'bootstrap_manifest.json',{p.name:sha(p) for p in path.iterdir() if p.is_file()})
    return {p.name:sha(p) for p in path.iterdir() if p.is_file()}

def saved_binding(path):
    path.mkdir();m=read_json(SAVED/'C_state_manifest.json')
    if m['synthetic'] is not True or m['artifact_sha256']['complete_states.npz']!='abb9f7537ff1b03210487227d3b23e6b44200d19f4d2bf56d73bfe67b241135a':raise PermissionError('GENUINE_SAVED_SYNTHETIC_ONLY')
    for name in list(m['artifact_sha256'])+['C_state_manifest.json']:shutil.copyfile(SAVED/name,path/name)
    validate_state_manifest(m,path)
    for name,source in {'PROTOCOL.md':ROOT/'paper12_predictive_v2/PROTOCOL.md','FINAL_VALIDATION_PLAN.md':ROOT/'paper12_predictive_v2/FINAL_VALIDATION_PLAN.md'}.items():shutil.copyfile(source,path/name)
    for name in ('SECURITY_AMENDMENT.md','human_authorization.bin'):shutil.copyfile(EVIDENCE/name,path/name)
    new(path/'analysis_spec.json',{'one_assessment':True,'hypotheses':list(PRIMARY),'Holm':4,'bootstrap':10000,'controls':4,'replicates':999})
    for role in ('engineering','scientific'):
        source=EVIDENCE/(role+'_preexecution_review.md')
        if not source.is_file():raise PermissionError('ACTUAL_INDEPENDENT_PREEXECUTION_REVIEW_REQUIRED')
        shutil.copyfile(source,path/(role+'_review.md'))
    return m

def synthetic_sources(job,binding,m):
    import os
    import numpy as np
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from .native_host import protect
    root=job/'.private/synthetic_sources';root.mkdir();protect(root)
    rng=np.random.default_rng(20261015);units={};partition={'cohort':m['cohort'],'D_trial_ids':{},'sessions':{}}
    for mouse in m['cohort']:
        cases=[c for c in m['cases'] if c['mouse_id']==mouse and c['view']=='primary'];sid=cases[0]['session_id'];ids=[sid+':D:'+str(i) for i in range(240)]
        units[sid]=[u for region in ('CA1','DG') for c in cases if c['region']==region for u in c['unit_ids']]+[sid+'_unselected_canary_'+str(i) for i in range(3)]
        partition['D_trial_ids'][mouse]=ids;partition['sessions'][mouse]={'session_id':sid,'trial_ids':ids,'conditions':[i%8 for i in range(240)],'orders':list(range(240,480))}
    new(binding/'source_units.json',units);new(binding/'partition_manifest.json',partition)
    catalog={'realm':'SYNTHETIC_D','cohort':m['cohort'],'sessions':{}};roots={'realm':'SYNTHETIC_D','sessions':{}}
    for index,mouse in enumerate(m['cohort']):
        p=partition['sessions'][mouse];sid=p['session_id'];shape=[240,20,len(units[sid])];data=rng.poisson(.25,size=shape).astype('<u4');data[:,:,-3:]=777
        context={'study':'P12-M2-ISOLATED-CUSTODY-1','mouse':mouse,'source_etag':'SYNTHETIC_ONLY','trial_lock_sha256':sha(binding/'partition_manifest.json'),'unit_lock_sha256':sha(binding/'source_units.json'),'compartment':'D','shape':shape,'dtype':'<u4'}
        key=os.urandom(32);nonce=os.urandom(12);envelope=b'P12GCM1\0'+nonce+AESGCM(key).encrypt(nonce,data.tobytes(),canonical(context))
        local=root/('custody_'+str(index%3));local.mkdir(exist_ok=True);protect(local);roots['sessions'][mouse]={'root':str(local)}
        cipher=sid+'.gcm';keyfile=sid+'.key';(local/cipher).write_bytes(envelope);(local/keyfile).write_bytes(key);protect(local/cipher);protect(local/keyfile)
        catalog['sessions'][mouse]={'mouse_id':mouse,'session_id':sid,'trial_ids_D':p['trial_ids'],'source_unit_ids':units[sid],'context':context,'cipher_file':cipher,'key_file':keyfile,'ciphertext_sha256':digest(envelope)}
    new(binding/'source_catalog.json',catalog);new(binding/'source_roots.json',roots)
    return root

def runtime_copy(job):
    runtime=job/'exports/runtime';shutil.copytree(RUNTIME,runtime)
    expected=read_json(ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256'];check_hashes(runtime,expected)
    return runtime,{'runtime_sha256':expected}
