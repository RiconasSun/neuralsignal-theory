"""Trusted orchestration of synthetic signed-ledger and actual Windows role proofs."""
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import uuid
import sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat,PrivateFormat,NoEncryption
import study as r
from native import security,prepare_job,launch
from broker import hold_process,synthetic_capability
from release_control import canonical,digest,durable_new,read_json
from state_manifest import create

NAMES=['success','duplicate','concurrent','replay','missing_signature','missing_review','wrong_signature','changed_artifact','wrong_principal',
       'wrong_realm','missing_ledger','tampered_ledger','malformed_ledger','partial_ledger','missing_genesis','unknown_field','fence_rollback','restored_log','missing_tombstone','missing_intent']
NAMES += ['crash_'+p for p in ('before_intent','after_intent','after_intent_append','after_consumed_append','after_consumed')]

def main():
    run_id=sys.argv[1] if len(sys.argv)>1 else '1'
    if not run_id.isdecimal():raise ValueError('ENGINEERING_ATTEMPT_ID')
    state_record=sys.argv[2] if len(sys.argv)>2 else 'results/synthetic_C.json'
    r.verify();a=security();old=r.load(r.HERE/state_record)
    if old['gate']['gate']!='PASS' or old['gate'].get('synthetic') is not True:raise RuntimeError('SYNTHETIC_C_BEFORE_SECURITY')
    job=prepare_job('controller_'+run_id);target=prepare_job('final_principal_'+run_id)
    data=job/'exports/security';data.mkdir();td=target/'exports/target';td.mkdir()
    code=job/'exports/code';code.mkdir();tc=target/'exports/code';tc.mkdir()
    for name in ('release_control.py','test_controller.py','access_check.py'):shutil.copy2(r.HERE/name,code/name)
    shutil.copy2(r.ROOT/'paper12_predictive_v2/selection.py',code/'selection.py')
    shutil.copy2(r.HERE/'controller_worker.py',code/'worker.py');shutil.copy2(r.OLD/'native_analysis_check.py',code/'native_analysis_check.py')
    for name,source in {'worker.py':r.HERE/'target_worker.py','release_control.py':r.HERE/'release_control.py','native_analysis_check.py':r.OLD/'native_analysis_check.py'}.items():shutil.copy2(source,tc/name)
    output=r.HERE/old['state_output_directory'];manifest=create(output,data/'binding')
    for name,source in {'PROTOCOL.md':r.ROOT/'paper12_predictive_v2/PROTOCOL.md','FINAL_VALIDATION_PLAN.md':r.ROOT/'paper12_predictive_v2/FINAL_VALIDATION_PLAN.md','animals.json':r.ROOT/'paper12_curated_v1/locks/animals.json'}.items():shutil.copy2(source,data/'binding'/name)
    spec={'one_assessment':True,'hypotheses':['own','population','stimulus_time','combined'],'Holm':4,'bootstrap':10000,'controls':4,'replicates':999,'synthetic_only':True,'no_real_D_authorization':True}
    r.save(data/'binding/analysis_spec.json',spec)
    r.save(data/'binding/partition_manifest.json',{'realm':'SYNTHETIC_D','cohort':manifest['cohort'],'D_trial_ids':{m:[m+':synthetic_D:'+str(i) for i in range(240)] for m in manifest['cohort']}})
    # Formal E0 independent review statements; final engineering approval is a separate later gate.
    for role,text in {'engineering':'Independent E0 security review: architecture acceptable for implementation only; no real C/D approval.',
                      'scientific':'Independent E0 scientific review: frozen policy consistent; no real C/D approval.'}.items():
        (data/'binding'/(role+'_review.txt')).write_text(text)
    r.save(data/'binding/runtime_identity.json',{'runtime_sha256':r.load(r.ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256'],
        'controller_code_sha256':{p.name:r.sha(p) for p in code.iterdir()},'target_code_sha256':{p.name:r.sha(p) for p in tc.iterdir()}})
    for name in NAMES:
        fixture=data/name;fixture.mkdir();(fixture/'ledger').mkdir();(data/('fence_'+name)).mkdir()
        (fixture/'ledger/writer.lock').write_bytes(b'PREINITIALIZED_NATIVE_LOCK')
        (fixture/'ledger/events.jsonl').write_bytes(b'UNINITIALIZED_SYNTHETIC_LEDGER')
    links=data/'link_tests';links.mkdir();(links/'ordinary_dir').mkdir();(links/'ordinary.bin').write_bytes(b'SYNTHETIC_LINK_FIXTURE')
    os.link(links/'ordinary.bin',links/'hardlinked.bin')
    # Only a synthetic signing authority is provisioned. Nothing here opens original custody keys.
    private=r.HERE/('.private/synthetic_approval_issuer_'+run_id);a.prepare(private)
    key=Ed25519PrivateKey.generate();kp=private/'synthetic_ed25519.key'
    kp.write_bytes(key.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption()));a.protect(kp)
    pub=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
    r.save(td/'protected_probes.json',{'issuer_key':str(kp),'controller_ledger':str(data/'success/ledger/events.jsonl')})
    r.save(data/'probes.json',{'issuer_key':str(kp),'target_private_source':str(target/'.private/source_canary.bin'),'target_private_key':str(target/'.private/key_canary.bin')})
    a.protect(data);a.protect(td);a.protect(code);a.protect(tc)
    started=threading.Event();info={}
    def target_hook(package,pid,work,grant,user):info.update(package=package,pid=pid);started.set()
    pool=concurrent.futures.ThreadPoolExecutor(1);future=pool.submit(launch,'target',target,td,tc,target_hook)
    if not started.wait(30):raise RuntimeError('TARGET_START_TIMEOUT')
    try:
        with hold_process(info['pid']) as (principal,verify_target):
            if principal['package_sid']!=info['package']:raise RuntimeError('TARGET_PACKAGE_SUBSTITUTION')
            denied_host=False;denied_changed=False
            try:
                with hold_process(os.getpid()):pass
            except PermissionError:denied_host=True
            try:verify_target(dict(principal,pid=principal['pid']+1))
            except PermissionError:denied_changed=True
            if not denied_host or not denied_changed:raise RuntimeError('ACTUAL_PRINCIPAL_DENIAL')
            def controller_hook(package,pid,work,grant,user):
                artifacts={p.name:r.sha(p) for p in (data/'binding').iterdir() if p.is_file()}
                for name in NAMES:
                    fixture=data/name;ident=uuid.uuid4().hex
                    genesis={'version':1,'realm':'SYNTHETIC_D','authorization_id':ident,'binding_root_sha256':digest(canonical(artifacts))}
                    durable_new(fixture/'ledger/genesis.json',genesis);gh=digest(canonical(genesis))
                    event={'sequence':0,'previous':gh,'state':'GENESIS','authorization_id':ident,'binding':gh}
                    (fixture/'ledger/events.jsonl').write_bytes(canonical(event)+b'\n')
                    anchor={'realm':'SYNTHETIC_D','mission':r.MISSION,'base':r.BASE,'authority_public':pub,'authorization_id':ident,'genesis_sha256':gh,
                        'controller_sid':package,'principal':principal,'cohort':manifest['cohort'],'protocol_sha256':artifacts['PROTOCOL.md'],
                        'partition_sha256':artifacts['partition_manifest.json'],'C_manifest_sha256':digest(canonical(manifest)),'C_manifest_file':'C_state_manifest.json',
                        'analysis_spec_sha256':artifacts['analysis_spec.json'],'artifacts':dict(artifacts),
                        'reviews':{k:artifacts[k+'_review.txt'] for k in ('engineering','scientific')},'fence_root':str(data/('fence_'+name))}
                    body={k:anchor[k] for k in ('realm','mission','base','authorization_id','cohort','protocol_sha256','partition_sha256','C_manifest_sha256','analysis_spec_sha256','principal','artifacts','reviews')};body['version']=1
                    if name=='changed_artifact':
                        anchor['artifacts']=dict(artifacts,**{'PROTOCOL.md':'0'*64});body['artifacts']=anchor['artifacts']
                    if name=='wrong_principal':body['principal']=dict(principal,pid=principal['pid']+1)
                    if name=='missing_review':anchor['reviews']={};body['reviews']={}
                    if name=='wrong_realm':anchor['realm']='REAL_D';anchor['authority_public']=Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
                    # No REAL_D approval issuer exists in this mission.
                    if body['realm']!='SYNTHETIC_D':raise PermissionError('SYNTHETIC_ISSUER_ONLY')
                    r.save(fixture/'approval.json',{'body':body,'signature':key.sign(canonical(body)).hex()});r.save(fixture/'anchor.json',anchor)
                    if name=='missing_ledger':(fixture/'ledger/events.jsonl').unlink()
                    if name=='missing_genesis':(fixture/'ledger/genesis.json').unlink()
                    if name=='tampered_ledger':(fixture/'ledger/events.jsonl').write_bytes(canonical(dict(event,previous='0'*64))+b'\n')
                    if name=='partial_ledger':(fixture/'ledger/events.jsonl').write_bytes(canonical(event))
                    if name=='malformed_ledger':(fixture/'ledger/events.jsonl').write_bytes(b'{malformed}\n')
                    if name=='restored_log':durable_new(data/('fence_'+name)/(ident+'.json'),{'authorization_id':ident,'previously_consumed_synthetic_fixture':True})
                    if name in ('missing_tombstone','missing_intent'):
                        previous=digest(canonical(event));all_events=[event]
                        for state in ('INTENT','CONSUMED'):
                            e={'sequence':len(all_events),'previous':previous,'state':state,'authorization_id':ident,'binding':digest(canonical(body))};all_events.append(e);previous=digest(canonical(e))
                        (fixture/'ledger/events.jsonl').write_bytes(b''.join(canonical(e)+b'\n' for e in all_events))
                        durable_new(data/('fence_'+name)/(ident+'.json'),{'authorization_id':ident,'binding':digest(canonical(body))})
                        if name=='missing_tombstone':durable_new(fixture/'ledger/intent.json',{'authorization_id':ident})
                        else:durable_new(fixture/'ledger/consumed.json',{'authorization_id':ident,'ledger_tail':previous})
                    # Signatures/anchors remain read-only; only this ledger and its separate fence are writable.
                    grant(fixture/'ledger',user,package,True);grant(data/('fence_'+name),user,package,True)
                a.protect(kp)
                junction=subprocess.run(['cmd','/d','/c','mklink','/J',str(links/'junction'),str(links/'ordinary_dir')],capture_output=True,text=True)
                if junction.returncode:raise RuntimeError('SYNTHETIC_JUNCTION_FIXTURE_FAILED:'+junction.stderr[:300])
                r.save(r.HERE/('security_execution_registration_'+run_id+'.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_execution':True,
                    'synthetic_only':True,'controller_sid':package,'controller_pid':pid,'held_target_identity':principal,
                    'code_sha256':{p.name:r.sha(p) for p in code.iterdir()},'source_sha256':{p.name:r.sha(p) for p in r.HERE.glob('*.py')},'binding_sha256':artifacts,'issuer_private_granted':False,
                    'actual_host_principal_denied':denied_host,'actual_target_substitution_denied':denied_changed,'real_D_approval_issued':False})
            receipt,gate=launch('security',job,data,code,controller_hook)
            if receipt['exit_code']!=0 or not gate or gate['gate']!='PASS' or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000':raise RuntimeError('ACTUAL_CONTROLLER_GATE_FAILED')
            public=job/'results/security/native';consumed=read_json(public/'consumed_synthetic_receipt.json');anchor=read_json(data/'success/anchor.json');approval=read_json(data/'success/approval.json')
            h=synthetic_capability(consumed,approval,anchor,data/'binding',data/'success/ledger',verify_target,td)
            duplicate_denied=False
            try:synthetic_capability(consumed,approval,anchor,data/'binding',data/'success/ledger',verify_target,td)
            except FileExistsError:duplicate_denied=True
            if not duplicate_denied:raise RuntimeError('DUPLICATE_BROKER_CAPABILITY')
            r.save(td/'stop.json',{'synthetic_stop':True})
            tr,tg=future.result(timeout=30)
            if tr['exit_code']!=0 or not tg or tg['gate']!='PASS' or tg['synthetic_capability_sha256']!=h or tr['profile_cleanup_hresult']!='0x00000000':raise RuntimeError('TARGET_CAPABILITY_PROOF')
            r.save(r.HERE/('results/security_'+run_id+'.json'),{'gate':'PASS','controller_receipt':receipt,'controller_gate':gate,'target_receipt':tr,'target_gate':tg,
                'duplicate_broker_denied':True,'actual_host_principal_denied':True,'actual_target_substitution_denied':True,'real_D_approval_issued':False,
                'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'synthetic_capabilities_granted':1,'injected_failures_counted_valid_releases':0,
                'controller_job':str(job.relative_to(r.HERE)),'target_job':str(target.relative_to(r.HERE)),
                'C_manifest_sha256':digest(canonical(manifest)),'full_state_sha256':manifest['artifact_sha256']['complete_states.npz']})
    finally:
        if not (td/'stop.json').exists():r.save(td/'stop.json',{'synthetic_stop_after_failure':True})
        pool.shutdown(wait=True)
    print({'engineering_security':'PASS','real_D_consumed':False,'real_D_evaluated':False})
if __name__=='__main__':main()
