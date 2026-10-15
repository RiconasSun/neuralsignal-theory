"""Conditional trusted C custody and isolated calibration. No D decoder or grant."""
import hashlib
import importlib.util
import shutil
import sys
import types
import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import study as r
from native import security,prepare_job,launch
from run_synthetic_calibration import science_code
from release_control import canonical,digest,read_json
from state_manifest import create

def verify_engineering():
    r.verify();a=security();a.check_acl(r.HERE/'.private/C_authorization')
    root=r.HERE/'.private/C_authorization'
    for p in root.iterdir():a.check_acl(p)
    approved=r.load(root/'approval.json');body=approved['body'];anchor=r.load(root/'authority.json')
    if set(body)!= {'scope','mission','base','snapshot_file','snapshot_sha256','evidence_sha256','review_sha256'} or body['snapshot_file']!='implementation_snapshot_v2.json' or body['scope']!='C_ONLY_CALIBRATION' or body['mission']!=r.MISSION or body['base']!=r.BASE:raise PermissionError('C_APPROVAL_SCOPE')
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(anchor['public'])).verify(bytes.fromhex(approved['signature']),canonical(body))
    if r.sha(r.HERE/body['snapshot_file'])!=body['snapshot_sha256']:raise PermissionError('C_IMPLEMENTATION_SNAPSHOT')
    for name,h in r.load(r.HERE/body['snapshot_file'])['sha256'].items():
        if r.sha(r.ROOT/name)!=h:raise PermissionError('CODE_CHANGED_AFTER_REVIEW')
    for name,h in body['evidence_sha256'].items():
        if r.sha(r.HERE/name)!=h:raise PermissionError('E3_EVIDENCE_CHANGED')
    for name,h in body['review_sha256'].items():
        if r.sha(r.ROOT/name)!=h:raise PermissionError('INDEPENDENT_REVIEW_CHANGED')
    if set(body['review_sha256'])!= {'ops/evidence/2026-10-14/p12-final-prerelease-controls-1/engineering_review.md','ops/evidence/2026-10-14/p12-final-prerelease-controls-1/scientific_review.md'}:raise PermissionError('BOTH_FINAL_REVIEWS_REQUIRED')
    return body

def old_acl(a,base,path):
    # Query the original exact host/SYSTEM/deny-all-AppContainer ACL without modifying it.
    namespace=dict(a.check_path.__globals__);namespace['r']=types.SimpleNamespace(HERE=base)
    cp=a.clone(a.check_path,namespace)
    namespace=dict(a.check_acl.__globals__);namespace.update(r=types.SimpleNamespace(HERE=base),check_path=cp)
    a.clone(a.check_acl,namespace)(path)

def C_private(a,receipt,reg):
    sid=receipt['session_id']
    if receipt['artifact_study']=='paper12_resume1':
        base=r.PREVIOUS;root=base/'.private'/receipt['custody_artifact_namespace']/sid;issuer=base/'.private/issuers'/(sid+'.json')
        old_acl(a,base,issuer);record=r.load(issuer);expected=dict(receipt);expected.pop('registration_sha256')
        if record['receipt']!=expected:raise PermissionError('C_ISSUER_RECEIPT')
        hashes=record['artifact_sha256']
    elif receipt['artifact_study']=='paper12_custody1':
        base=r.OLD;issuer=base/'.private/transport_recovery1/reuse_issuer.json';old_acl(a,base,issuer);record=r.load(issuer)[sid]
        if sid not in reg['reuse'] or record['namespace']!=receipt['custody_artifact_namespace']:raise PermissionError('C_ORIGINAL_NAMESPACE')
        root=base/'.private'/record['namespace']/sid;hashes=record['fingerprints']
        prior=base/'results/M2/index2/sessions'/(sid+'.json')
        if r.sha(prior)!=reg['reuse'][sid]['receipt_sha256'] or receipt['prior_receipt_sha256']!=r.sha(prior):raise PermissionError('C_REUSE_SOURCE')
    else:raise PermissionError('UNKNOWN_C_CUSTODY')
    for name in ('C.gcm','C.key','private_provenance.json'):
        p=root/name;old_acl(a,base,p)
        if r.sha(p)!=hashes[name]:raise PermissionError('C_PRIVATE_ARTIFACT_INTEGRITY')
    # D access-control metadata only; never open/hash/decrypt a D payload/key.
    for name in ('D.gcm','D.key'):old_acl(a,base,root/name)
    return root

def derive_C(job,approval):
    a=security();data=job/'exports/C_only';data.mkdir();a.protect(data)
    frozen=r.ROOT/'paper12_curated_v1';animals=r.load(frozen/'locks/animals.json');units=r.load(frozen/'locks/units.json');trials=r.load(frozen/'locks/trials.json')
    gate=r.load(r.PREVIOUS/'results/M2/gate_result.json');reg=r.load(r.PREVIOUS/'registration.json')
    if gate['gate']!='PASS':raise PermissionError('ORIGINAL_C_QC_GATE')
    conditions=sorted({t['condition'] for t in trials});sessions=[];metadata=[];qc_audit=[];d_probes={}
    sys.path.append(str(r.OLD));spec=importlib.util.spec_from_file_location('C_only_cipher',r.OLD/'cipher_core.py');cipher=importlib.util.module_from_spec(spec);spec.loader.exec_module(cipher)
    for animal in animals:
        if animal['group']!='final':continue
        sid=animal['session_id'];relative='results/M2/sessions/'+sid+'.json';p=r.PREVIOUS/relative;receipt=r.load(p)
        if r.sha(p)!=gate['receipt_sha256'][relative] or receipt['group']!='final' or receipt['mouse_id']!=animal['mouse_id'] or receipt['qc_partition']!='calibration' or receipt['final_holdout_evaluated'] or receipt['final_values_exposed_to_analysis']:raise PermissionError('C_IDENTITY_BOUNDARY')
        private=C_private(a,receipt,reg);qc={u['unit_id']:u for u in r.load(private/'private_provenance.json')['unit_QC']}
        localunits=[u for u in units if u['session_id']==sid];localtrials=[t for t in trials if t['session_id']==sid];selectedtrials=[t for t in localtrials if t['partition']=='calibration' and t['metadata_admitted']]
        fields={};indices={};selected={}
        for region in ('CA1','DG'):
            eligible=[]
            for i,u in enumerate(localunits):
                if u['subfield']!=region:continue
                q=qc[u['unit_id']]
                if q['eligible']:
                    if u['metadata_quarantined'] or q['QC_trials']!=len(selectedtrials) or not (.1<=q['rate_Hz']<=100 and q['active_trial_fraction']>=.1 and q['ISI_under_1ms_fraction']<=.01 and not q['invalid_permitted_timestamps']):raise PermissionError('C_FROZEN_PHYSIOLOGY')
                    eligible.append(i)
            eligible.sort(key=lambda i:hashlib.sha256(('P12-CURATED-EXPLORATORY-V1|unit|'+localunits[i]['unit_id']).encode()).hexdigest());indices[region]=eligible[:32]
            if len(indices[region])!=32:raise RuntimeError('C_PRIMARY_MATCHED32_COVERAGE')
            selected[region]=[localunits[i]['unit_id'] for i in indices[region]];fields[region+'_unit_ids']=np.array(selected[region])
            metadata.extend(localunits[i] for i in indices[region])
        shape=[len(selectedtrials),20,len(localunits)]
        context={'study':'P12-M2-ISOLATED-CUSTODY-1','mouse':animal['mouse_id'],'source_etag':receipt['source_etag'],'trial_lock_sha256':r.sha(frozen/'locks/trials.json'),'unit_lock_sha256':r.sha(frozen/'locks/units.json'),'compartment':'C','shape':shape,'dtype':'<u4'}
        if r.sha(private/'C.gcm')!=receipt['ciphertext_receipts']['C']['ciphertext_sha256']:raise PermissionError('C_CIPHERTEXT_HASH')
        payload=cipher.unseal((private/'C.key').read_bytes(),(private/'C.gcm').read_bytes(),context);tensor=np.frombuffer(payload,dtype='<u4').reshape(shape)
        for region in ('CA1','DG'):
            y=tensor[:,:,indices[region]];fields[region+'_C']=y
            for j,uid in enumerate(selected[region]):
                q=qc[uid]
                if abs(float(y[:,:,j].sum())-q['rate_Hz']*2*len(selectedtrials))>1e-8 or abs(float(np.mean(y[:,:,j].sum(axis=1)>0))-q['active_trial_fraction'])>1e-12:raise RuntimeError('C_COUNTS_QC_PARITY')
            qc_audit.append({'mouse_id':animal['mouse_id'],'session_id':sid,'region':region,'selected_units':selected[region],'all_selected_C_QC_passed':True,'ISI_from_frozen_C_timestamp_QC':True,'C_QC_private_artifact_sha256':r.sha(private/'private_provenance.json'),'receipt_sha256':r.sha(p)})
        fields.update(conditions_C=np.array([conditions.index(t['condition']) for t in selectedtrials]),orders_C=np.array([t['provider_row_index'] for t in selectedtrials]),trial_ids_C=np.array([t['trial_id'] for t in selectedtrials]))
        target=data/(sid+'.npz');np.savez(target,**fields);a.protect(target)
        sessions.append({'session_id':sid,'mouse_id':animal['mouse_id'],'file':target.name,'sha256':r.sha(target),'unit_ids':selected,'trial_ids':{'C':fields['trial_ids_C'].tolist()}})
        d_probes[sid+'_D_key_open_denied']=str(private/'D.key');d_probes[sid+'_D_cipher_open_denied']=str(private/'D.gcm')
        del tensor,payload,fields
    if len(sessions)!=13:raise PermissionError('C_THIRTEEN_FINAL_MICE')
    r.save(data/'metadata.json',metadata);r.save(data/'C_QC_attestation.json',qc_audit)
    r.save(data/'manifest.json',{'group':'final','compartments':['C'],'synthetic':False,'sessions':sessions,
        'C_approval_sha256':digest(canonical(approval)),'QC_attestation_sha256':r.sha(data/'C_QC_attestation.json'),
        'denial_probes':{'C_approval_signing_key':str(r.HERE/'.private/C_authorization/issuer.key')},'accesscheck_only_paths':d_probes})
    r.save(r.HERE/'final_D_partition_manifest.json',{'scope':'METADATA_ONLY_NO_D_VALUES','animals_sha256':r.sha(frozen/'locks/animals.json'),
        'trials_sha256':r.sha(frozen/'locks/trials.json'),'cohort':[s['mouse_id'] for s in sessions],
        'D_trial_ids':{a['mouse_id']:[t['trial_id'] for t in trials if t['session_id']==a['session_id'] and t['partition']=='locked_evaluation' and t['metadata_admitted']] for a in animals if a['group']=='final'}})
    a.protect(data)
    return data

def main():
    approval=verify_engineering();a=security();job=prepare_job('real_C_1');data=derive_C(job,approval);code=job/'exports/code';science_code(code);a.protect(code)
    r.save(r.HERE/'real_C_execution_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_real_C_fit':True,'approval_sha256':digest(canonical(approval)),
        'job':str(job.relative_to(r.HERE)),'C_manifest_sha256':r.sha(data/'manifest.json'),'code_sha256':{p.name:r.sha(p) for p in code.iterdir()},'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
    receipt,gate=launch('real_C',job,data,code)
    result={'receipt':receipt,'gate':gate,'job':str(job.relative_to(r.HERE)),'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}
    r.save(r.HERE/'results/real_C.json',result)
    if receipt['exit_code']!=0 or receipt['timed_out'] or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000' or not gate or gate['gate']!='PASS':raise RuntimeError('REAL_C_REQUIRED_GATE_FAILED_STOP_NO_RETRY')
    manifest=create(job/receipt['output_directory'],r.HERE/'.private/sealed_C_state');a.protect(r.HERE/'.private/sealed_C_state')
    for p in (r.HERE/'.private/sealed_C_state').rglob('*'):
        if p.is_file():a.protect(p)
    r.save(r.HERE/'results/C_sealing_receipt.json',{'complete':True,'mice':13,'cases':len(manifest['cases']),'seed_certificates':len(manifest['seed_certificates']),
        'canonical_manifest_sha256':digest(canonical(manifest)),'artifact_sha256':manifest['artifact_sha256'],'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
    print({'REAL_C_CALIBRATION_PASS':True,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
if __name__=='__main__':main()
