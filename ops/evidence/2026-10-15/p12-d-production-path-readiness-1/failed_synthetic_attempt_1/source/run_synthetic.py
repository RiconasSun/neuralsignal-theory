"""Trusted host full production rehearsal. Only generated SYNTHETIC_D entitlements."""
import concurrent.futures
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat,PrivateFormat,NoEncryption
from .common import *
from . import study as r
from .native_host import NativeProcess,protect,grant,hold_process,require_custodian
from .production_broker import RegisteredDeployment,preflight,deliver
from .activation import activate_registered

NAMES=['success','duplicate','concurrent','replay','missing_signature','missing_review','wrong_signature','changed_artifact','wrong_principal','wrong_realm','missing_ledger','tampered_ledger','malformed_ledger','partial_ledger','missing_genesis','unknown_field','fence_rollback','restored_log','missing_tombstone','missing_intent']+['crash_'+x for x in ('before_intent','after_intent','after_intent_append','after_consumed_append','after_consumed')]
EXTRA=['delivery_duplicate','delivery_concurrent','cipher_tamper','key_tamper']+['delivery_crash_'+x for x in ('after_delivery_fence','after_private_export','after_complete_staging','after_acl_grant')]

def wait_file(path,process,timeout=300):
    end=time.monotonic()+timeout
    while not path.exists():
        if process.poll() is not None:raise RuntimeError('NATIVE_PROCESS_EXIT_BEFORE_READY:'+str(process.output))
        if time.monotonic()>end:raise TimeoutError('NATIVE_READY_LIMIT')
        time.sleep(.2)

def fixture(data,name,artifacts,manifest,principal,controller_sid,pub,key):
    folder=data/name;folder.mkdir();ledger=folder/'ledger';ledger.mkdir();fence=data/('fence_'+name);fence.mkdir()
    (ledger/'writer.lock').write_bytes(b'PREINITIALIZED_NATIVE_LOCK');ident=uuid.uuid4().hex()
    genesis={'version':1,'realm':'SYNTHETIC_D','authorization_id':ident,'binding_root_sha256':digest(canonical(artifacts))};new(ledger/'genesis.json',genesis);gh=digest(canonical(genesis));event={'sequence':0,'previous':gh,'state':'GENESIS','authorization_id':ident,'binding':gh};(ledger/'events.jsonl').write_bytes(canonical(event)+b'\n')
    anchor={'realm':'SYNTHETIC_D','mission':MISSION,'base':BASE,'authority_public':pub,'authorization_id':ident,'genesis_sha256':gh,'controller_sid':controller_sid,'principal':principal,'cohort':manifest['cohort'],'protocol_sha256':artifacts['PROTOCOL.md'],'partition_sha256':artifacts['partition_manifest.json'],'C_manifest_sha256':digest(canonical(manifest)),'C_manifest_file':'C_state_manifest.json','analysis_spec_sha256':artifacts['analysis_spec.json'],'artifacts':dict(artifacts),'reviews':{k:artifacts[k+'_review.md'] for k in ('engineering','scientific')},'fence_root':str(fence)}
    body={k:anchor[k] for k in ('realm','mission','base','authorization_id','cohort','protocol_sha256','partition_sha256','C_manifest_sha256','analysis_spec_sha256','principal','artifacts','reviews')};body['version']=1
    if name=='changed_artifact':anchor['artifacts']=dict(artifacts,**{'PROTOCOL.md':'0'*64});body['artifacts']=anchor['artifacts']
    if name=='wrong_principal':body['principal']=dict(principal,pid=principal['pid']+1)
    if name=='missing_review':anchor['reviews']={};body['reviews']={}
    if name=='wrong_realm':anchor['realm']='REAL_D';anchor['authority_public']='00'*32
    if body['realm']!='SYNTHETIC_D':raise PermissionError('SYNTHETIC_ISSUER_ONLY')
    new(folder/'approval.json',{'body':body,'signature':key.sign(canonical(body)).hex()});new(folder/'anchor.json',anchor)
    if name=='missing_ledger':(ledger/'events.jsonl').unlink()
    if name=='missing_genesis':(ledger/'genesis.json').unlink()
    if name=='tampered_ledger':(ledger/'events.jsonl').write_bytes(canonical(dict(event,previous='0'*64))+b'\n')
    if name=='partial_ledger':(ledger/'events.jsonl').write_bytes(canonical(event))
    if name=='malformed_ledger':(ledger/'events.jsonl').write_bytes(b'{malformed}\n')
    if name=='restored_log':new(fence/(ident+'.json'),{'authorization_id':ident,'previously_consumed_synthetic_fixture':True})
    if name in ('missing_tombstone','missing_intent'):
        previous=digest(canonical(event));events=[event]
        for state in ('INTENT','CONSUMED'):
            e={'sequence':len(events),'previous':previous,'state':state,'authorization_id':ident,'binding':digest(canonical(body))};events.append(e);previous=digest(canonical(e))
        (ledger/'events.jsonl').write_bytes(b''.join(canonical(e)+b'\n' for e in events));new(fence/(ident+'.json'),{'authorization_id':ident,'binding':digest(canonical(body))})
        new(ledger/('intent.json' if name=='missing_tombstone' else 'consumed.json'),{'authorization_id':ident,'ledger_tail':previous})

def main(attempt):
    r.verify();require_custodian()
    if not attempt.isdecimal():raise ValueError('APPEND_ONLY_ATTEMPT_ID')
    job=r.HERE/'jobs'/('synthetic_'+attempt);job.mkdir(parents=True,exist_ok=False);(job/'exports').mkdir();private=job/'.private';private.mkdir();protect(private)
    for name in ('source_canary.bin','key_canary.bin'):(private/name).write_bytes(b'SYNTHETIC_PRIVATE_CANARY');protect(private/name)
    runtime,runtime_identity=r.runtime_copy(job);data=job/'exports/security';data.mkdir();td=job/'exports/target';td.mkdir();binding=data/'binding';manifest=r.saved_binding(binding);source=r.synthetic_sources(job,binding,manifest)
    tc=job/'exports/target_code';cc=job/'exports/controller_code';target_code=r.bundle(tc,'target');controller_code=r.bundle(cc,'controller')
    new(binding/'code_identity.json',{'source_sha256':r.source_hashes(),'target_code_sha256':target_code,'controller_code_sha256':controller_code,'new_source_freeze_sha256':sha(r.HERE/'source_freeze.json')});new(binding/'runtime_identity.json',runtime_identity)
    new(td/'runtime_identity.json',runtime_identity);new(data/'runtime_identity.json',runtime_identity)
    authority=private/'synthetic_authority';authority.mkdir();protect(authority);key=Ed25519PrivateKey.generate();pub=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex();kp=authority/'synthetic_only.key';kp.write_bytes(key.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption()));protect(kp)
    new(authority/'synthetic_authority.json',{'realm':'SYNTHETIC_D','mission':MISSION,'base':BASE,'public_key_hex':pub});protect(authority/'synthetic_authority.json')
    new(td/'target_config.json',{'protected_probes':{'issuer':str(kp),'source':str(source/'custody_0'/(manifest['cases'][0]['session_id']+'.gcm')),'key':str(source/'custody_0'/(manifest['cases'][0]['session_id']+'.key')),'ledger':str(data/'success/ledger/events.jsonl')},'approval_path':str(data/'success/approval.json'),'anchor_path':str(data/'success/anchor.json'),'binding_root':str(binding),'delivery_root':str(td/'payload')})
    new(data/'controller_probes.json',{'issuer':str(kp),'source':str(source/'custody_0'/(manifest['cases'][0]['session_id']+'.gcm')),'key':str(source/'custody_0'/(manifest['cases'][0]['session_id']+'.key'))});new(data/'extra_consumptions.json',EXTRA)
    new(data/'synthetic_oracles.json',{'realm':'SYNTHETIC_D'})
    new(data/'production_plan.json',{'ledger':str(data/'success/ledger'),'anchor_path':str(data/'success/anchor.json'),'binding_root':str(binding),'approval_path':str(data/'success/approval.json')})
    target=None;controller=None
    try:
        pending=private/'real_authority_pending';pending.mkdir();protect(pending);new(pending/'deployment.json',{'realm':'REAL_D','authority_root':str(pending/'UNPROVISIONED'),'authority_receipt_sha256':None,'owner_designation_sha256':'3bf5ec38e3aa7938183452421f93134fa6763f4262400af8c551581ff32603ba'});protect(pending/'deployment.json')
        try:preflight(RegisteredDeployment(pending/'deployment.json',sha(pending/'deployment.json')),lambda x:(_ for _ in ()).throw(AssertionError('NO_REAL_ROLE_RESOLUTION')))
        except PermissionError as exc:
            if str(exc)!='AUTHORITY_PENDING':raise
        else:raise RuntimeError('REAL_PENDING_ENTRY_NOT_DENIED')
        new(job/'real_pending_denial.json',{'status':'AUTHORITY_PENDING','D_source_resolved':False,'controller_resumed':False,'entitlement_created':False})
        target=NativeProcess(job,'target',td,tc,runtime)
        with hold_process(target.pi.pid) as (principal,verify_target):
            controller=NativeProcess(job,'controller',data,cc,runtime)
            artifacts={p.name:sha(p) for p in binding.iterdir() if p.is_file()}
            for name in NAMES+EXTRA:fixture(data,name,artifacts,manifest,principal,controller.package,pub,key)
            # Readonly artifacts for both roles. Only controller receives each ledger/fence RW.
            grant(data,controller.package);grant(binding,controller.package,shared=True);grant(binding,target.package,shared=True)
            for name in NAMES+EXTRA:grant(data/name/'ledger',controller.package,True);grant(data/('fence_'+name),controller.package,True)
            for file in ('approval.json','anchor.json'):
                grant(data/'success'/file,controller.package,shared=True);grant(data/'success'/file,target.package,shared=True)
            links=data/'link_tests';links.mkdir();(links/'ordinary_dir').mkdir();(links/'ordinary.bin').write_bytes(b'SYNTHETIC_LINK');os.link(links/'ordinary.bin',links/'hardlinked.bin')
            junction=subprocess.run(['cmd','/d','/c','mklink','/J',str(links/'junction'),str(links/'ordinary_dir')],capture_output=True,text=True)
            if junction.returncode:raise RuntimeError('SYNTHETIC_JUNCTION_CREATION')
            deployments={}
            for name in ['success']+EXTRA:
                root=private/('deployment_'+name);root.mkdir();protect(root);path=root/'deployment.json'
                value={'realm':'SYNTHETIC_D','synthetic':True,'mission':MISSION,'base':BASE,'job_root':str(job),'authority_root':str(authority),'authority_receipt_sha256':sha(authority/'synthetic_authority.json'),'anchor_path':str(data/name/'anchor.json'),'anchor_sha256':sha(data/name/'anchor.json'),'approval_path':str(data/name/'approval.json'),'ledger':str(data/name/'ledger'),'binding_root':str(binding),'target_code_root':str(tc),'runtime_root':str(runtime),'source_root':str(source),'delivery_root':str(td/'payload' if name=='success' else job/'exports'/('failed_'+name)),'target_data_root':str(td if name=='success' else job/'exports'/('signal_'+name))}
                if name!='success':Path(value['target_data_root']).mkdir();protect(value['target_data_root'])
                value['controller_code_root']=str(cc)
                new(path,value);protect(path);deployments[name]=RegisteredDeployment(path,sha(path))
            preflight(deployments['success'],verify_target)
            denied_host=False;denied_substitution=False
            try:
                with hold_process(os.getpid()):pass
            except PermissionError:denied_host=True
            try:verify_target(dict(principal,pid=principal['pid']+1))
            except PermissionError:denied_substitution=True
            if not denied_host or not denied_substitution:raise PermissionError('HELD_PROCESS_DENIAL_TESTS')
            new(job/'execution_registration.json',{'before_role_execution':True,'source_sha256':r.source_hashes(),'target_code':target_code,'controller_code':controller_code,'held_principal':principal,'controller_sid':controller.package,'binding_sha256':artifacts,'deployment_sha256':{k:v.file_sha256 for k,v in deployments.items()},'synthetic_only':True,'real_operations':False})
            target.realm='SYNTHETIC_D';controller.realm='SYNTHETIC_D';target.resume();wait_file(target.output/'ready.json',target);controller.resume()
            wait_file(controller.output/'oracles_done.json',controller,1800)
            failures=delivery_negatives(job,deployments,controller.output,verify_target,source,manifest)
            completion,gate=activate_registered(deployments['success'].path,deployments['success'].file_sha256,target,controller,verify_target,protect,grant)
            cg=read_json(controller.output/'gate_result.json');receipt=read_json(controller.output/'consumed_success.json')
            try:deliver(deployments['success'],receipt,verify_target,protect,grant)
            except (FileExistsError,PermissionError):pass
            else:raise RuntimeError('SUCCESS_DUPLICATE_DELIVERY_NOT_DENIED')
            if gate['gate']!='PASS' or gate['synthetic'] is not True or gate['null_cases']!=104 or gate['null_evaluations']!=103896:raise RuntimeError('FULL_PRODUCTION_SYNTHETIC_GATE')
            new(job/'result.json',{'gate':'PASS','synthetic_only':True,'production_completion':completion,'controller_gate':cg,'evaluator_gate':gate,'delivery_negative_tests':failures,'host_principal_denied':denied_host,'substituted_principal_denied':denied_substitution,'REAL_D_AUTHORITY_PROVISIONED':False,'REAL_D_SIGNATURE_ISSUED':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'SCIENTIFIC_VALIDATION_PASS':False,'source_sha256':r.source_hashes(),'target_output':str(target.output),'controller_output':str(controller.output)})
    except BaseException as exc:
        new(job/'attempt_failure.json',{'error_type':type(exc).__name__,'message':str(exc),'traceback':__import__('traceback').format_exc(),'real_D_operations':False});raise
    finally:
        if controller:controller.close()
        if target:target.close()
    # Public engineering evidence excludes all keys, plaintext D arrays, and deployment secrets.
    out=r.HERE/'results'/('synthetic_'+attempt);out.mkdir(parents=True)
    for p in (job/'result.json',job/'execution_registration.json',job/'native_target_receipt.json',job/'native_controller_receipt.json'):shutil.copyfile(p,out/p.name)
    for role,process in (('target',target),('controller',controller)):
        dest=out/role;dest.mkdir()
        for p in process.output.iterdir():
            if p.is_file() and p.suffix in ('.json','.md'):shutil.copyfile(p,dest/p.name)
    new(out/'evidence_inventory.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print({'synthetic_engineering':'PASS','evidence':str(out),'real_D_operations':False},flush=True)

def delivery_negatives(job,deployments,output,verify_target,source,manifest):
    results={}
    class Injected(Exception):pass
    def inject(point):
        def hook(found):
            if found==point:raise Injected(point)
        return hook
    for name in EXTRA:
        d=deployments[name];receipt=read_json(output/('consumed_'+name+'.json'))
        if name in ('delivery_duplicate','delivery_concurrent'):
            # A stopped delivery wins the exclusive durable fence; every other delivery loses.
            def attempt(_):
                try:deliver(d,receipt,verify_target,protect,grant,inject('after_delivery_fence'));return 'unexpected'
                except Injected:return 'winner_poisoned'
                except FileExistsError:return 'denied'
            if name=='delivery_concurrent':
                with concurrent.futures.ThreadPoolExecutor(2) as pool:values=list(pool.map(attempt,range(2)))
            else:values=[attempt(0),attempt(1)]
            if sorted(values)!=['denied','winner_poisoned']:raise RuntimeError('EXCLUSIVE_DELIVERY_TEST')
        else:
            path=None;original=None
            try:
                if name in ('cipher_tamper','key_tamper'):
                    sid=manifest['cases'][0]['session_id'];path=source/'custody_0'/(sid+('.gcm' if name=='cipher_tamper' else '.key'));original=path.read_bytes();path.write_bytes(bytes([original[0]^1])+original[1:])
                    try:deliver(d,receipt,verify_target,protect,grant)
                    except (PermissionError,__import__('cryptography.exceptions',fromlist=['InvalidTag']).InvalidTag):pass
                    else:raise RuntimeError('SOURCE_TAMPER_NOT_DENIED')
                else:
                    try:deliver(d,receipt,verify_target,protect,grant,inject(name.removeprefix('delivery_crash_')))
                    except Injected:pass
                    else:raise RuntimeError('DELIVERY_INTERRUPT_NOT_REACHED')
            finally:
                if path is not None:path.write_bytes(original)
            try:deliver(d,receipt,verify_target,protect,grant)
            except FileExistsError:pass
            else:raise RuntimeError('POISONED_DELIVERY_RESTART')
        if (Path(d['target_data_root'])/'start_evaluation.json').exists():raise RuntimeError('FAILED_DELIVERY_SIGNALED_EVALUATOR')
        results[name]={'fail_closed':True,'valid_release':False,'retry_denied':True,'start_signal_absent':True,'synthetic_capability_granted':name=='delivery_crash_after_acl_grant','injection':'host exception interruption' if name.startswith('delivery_crash') else 'tamper/duplicate/concurrent','REAL_D_capability_granted':False}
    new(job/'delivery_failures.json',results);return results

if __name__=='__main__':main(__import__('sys').argv[1])
