"""Public exact-artifact preparation only. No REAL issuer, source/key or ledger API."""
import argparse
import shutil
import uuid
from pathlib import Path
from .common import *
from . import study as r
from .owner_protocol import POLICY,AMENDMENT,DESIGNATION
from .real_metadata import materialize

def build(output):
    r.verify()
    pointer=r.HERE/'latest_saved_result.json'
    if not pointer.is_file():raise RuntimeError('ENGINEERING_GATE_PENDING')
    result=read_json(r.HERE/read_json(pointer)['path']/'result.json')
    if result['gate']!='PASS' or result['synthetic_only'] is not True or result['evaluator_gate']['null_evaluations']!=103896:raise RuntimeError('FULL_SYNTHETIC_ENGINEERING_GATE_REQUIRED')
    if not (r.EVIDENCE/'saved_reproduction_final.log').is_file():raise RuntimeError('SAVED_REPRODUCTION_REQUIRED')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    metadata=output/'public_metadata';receipt=materialize(metadata)
    for name,source in {'PROTOCOL.md':r.ROOT/'paper12_predictive_v2/PROTOCOL.md','FINAL_VALIDATION_PLAN.md':r.ROOT/'paper12_predictive_v2/FINAL_VALIDATION_PLAN.md','SECURITY_AMENDMENT.md':r.EVIDENCE/'SECURITY_AMENDMENT.md','human_authorization.bin':r.EVIDENCE/'human_authorization.bin','PUBLIC_KEY_VALIDITY_AMENDMENT.md':r.EVIDENCE/'PUBLIC_KEY_VALIDITY_AMENDMENT.md','human_fix_authorization.txt':r.EVIDENCE/'human_fix_authorization.txt','source_freeze.json':r.HERE/'source_freeze.json','complete_C_sealing_receipt.json':r.ROOT/'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1/complete_C_sealing_receipt.json','complete_seal_inventory.json':r.ROOT/'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1/complete_seal_inventory.json'}.items():shutil.copyfile(source,output/name)
    new(output/'runtime_identity.json',{'runtime_sha256':read_json(r.ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256']})
    identity={'source_sha256':r.source_hashes(),'new_source_freeze_sha256':sha(r.HERE/'source_freeze.json'),'target_code_sha256':r.bundle(output/'expected_target_code','target'),'controller_code_sha256':r.bundle(output/'expected_controller_code','controller')}
    new(output/'expected_code_identity.json',identity)
    spec={'one_assessment':True,'hypotheses':list(PRIMARY),'contrasts':{'own':['F','NP'],'population':['F','NH'],'stimulus_time':['F','OHP'],'combined':['F','O']},'Holm':4,'bootstrap':10000,'bootstrap_seed':120214,'controls':4,'replicates':999,'pooled_and_regional_Holm_families':16,'mandatory_sensitivities':list(MANDATORY),'minimum_paired_mice':8,'scientific_rules':'Exact original FINAL_VALIDATION_PLAN.md; no changes','no_refitting':True}
    new(output/'analysis_specification.json',spec)
    roster={p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    preparation_id=uuid.uuid4().hex
    pending={'version':1,'mission':MISSION,'base':BASE,'realm':'REAL_D_PREPARATION_ONLY','authorization_id':preparation_id,'policy':POLICY,'security_amendment_sha256':AMENDMENT,'owner_designation_sha256':DESIGNATION,'artifact_sha256':roster,'artifact_roster_sha256':digest(canonical(roster)),'cohort':read_json(metadata/'C_state_manifest.json')['cohort'],'metadata_receipt':receipt,'principal':None,'required_live_principal_fields':['package_sid','pid','creation_identity'],'controller_sid':None,'owner_authority_receipt_sha256':None,'canonical_REAL_D_approval_body':None,'status':'NOT_SIGNABLE_AUTHORITY_AND_LIVE_PRINCIPAL_PENDING','approval_scope':'One assessment only under unchanged original final plan; this dossier is not a release approval','missing_requirements':['Genuine owner-controlled isolated-key ceremony and protected public trust root','Fresh held live restricted target/controller identity and complete reviewed staged bindings'],'entitlement_created':False,'REAL_D_SIGNATURE_ISSUED':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'SCIENTIFIC_VALIDATION_PASS':False,'irreversible_boundary':'Only a separately authorized owner offline REAL_D signature may precede exactly-once consumption. Consumption is durable before decryption; interruption never restores entitlement.'}
    new(output/'PENDING_REQUEST.json',pending)
    return {'status':pending['status'],'authorization_id':preparation_id,'artifact_roster_sha256':pending['artifact_roster_sha256'],'dossier_sha256':sha(output/'PENDING_REQUEST.json'),'signable':False,'REAL_D_SIGNATURE_ISSUED':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();print(__import__('json').dumps(build(args.output),sort_keys=True))

if __name__=='__main__':main()
