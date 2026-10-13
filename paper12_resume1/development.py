"""New gate/mixed storage bridge; immutable development selection and cipher context."""
import hashlib
import sys
from pathlib import Path
import numpy as np
import study as r
import verified_atomic as a
from preflight import guard,verify_reuse
from run_real import validate
from cipher_core import unseal
from manifest_validation import validate_manifest
from register_m3 import guard_adapter
from fingerprints import check as check_fingerprints


def main():
    guard_adapter();reg=guard();verify_reuse()
    gate=r.load(r.HERE/'results/M2/gate_result.json')
    if gate['gate']!='PASS':raise PermissionError('NEW_M2_PASS_REQUIRED')
    method=r.load(r.OLD/'M3_METHOD_DECISION1.json')
    policy=r.load(r.OLD/'development_registration.json')
    for name,digest in policy['implementation_sha256'].items():
        if r.sha(r.OLD/name)!=digest:raise RuntimeError('OLD_IMPLEMENTATION_CHANGED')
    if method['ridge_normalization']!='per_unit_exposure':raise RuntimeError('FROZEN_RIDGE_CHANGED')
    frozen=r.ROOT/'paper12_curated_v1'
    animals=r.load(frozen/'locks/animals.json');units=r.load(frozen/'locks/units.json');trials=r.load(frozen/'locks/trials.json')
    root=r.HERE/'exports/development1';root.mkdir(parents=True,exist_ok=False);a.protect(root)
    manifest=dict(group='development',compartments=['A','B'],sessions=[],
        M2_gate_sha256=r.sha(r.HERE/'results/M2/gate_result.json'),
        development_registration_sha256=r.sha(r.OLD/'development_registration.json'),
        method_decision_sha256=r.sha(r.OLD/'M3_METHOD_DECISION1.json'),ridge_normalization=method['ridge_normalization'])
    conditions=sorted({t['condition'] for t in trials})
    if len(conditions)!=8:raise RuntimeError('CONDITIONS_CHANGED')
    receipts={}
    for animal in animals:
        if animal['group']!='development':continue
        sid=animal['session_id'];p=r.HERE/'results/M2/sessions'/(sid+'.json');receipt=r.load(p);receipts[sid]=receipt
        if gate['receipt_sha256'][p.relative_to(r.HERE).as_posix()]!=r.sha(p):raise RuntimeError('NEW_GATE_RECEIPT_CHANGED')
        if not receipt['eligible_mouse']:continue
        private=check_fingerprints(receipt,reg)
        if receipt['artifact_study']=='paper12_resume1':validate(receipt,animal)
        localunits=[u for u in units if u['session_id']==sid];localtrials=[t for t in trials if t['session_id']==sid]
        qc={u['unit_id']:u for u in r.load(private/'private_provenance.json')['unit_QC']}
        fields={};selected={}
        for region in ('CA1','DG'):
            indices=[i for i,u in enumerate(localunits) if u['subfield']==region and qc[u['unit_id']]['eligible']]
            indices.sort(key=lambda i:hashlib.sha256(('P12-CURATED-EXPLORATORY-V1|unit|'+localunits[i]['unit_id']).encode()).hexdigest())
            selected[region]=indices[:32]
            if len(selected[region])<5:raise RuntimeError('UNIT_ADMISSION_MISMATCH')
            fields[region+'_unit_ids']=np.array([localunits[i]['unit_id'] for i in selected[region]])
        base=dict(study='P12-M2-ISOLATED-CUSTODY-1',mouse=animal['mouse_id'],source_etag=receipt['source_etag'],
                  trial_lock_sha256=r.sha(frozen/'locks/trials.json'),unit_lock_sha256=r.sha(frozen/'locks/units.json'))
        for compartment,partition in (('A','train'),('B','validation')):
            subset=[t for t in localtrials if t['partition']==partition and t['metadata_admitted']]
            shape=(len(subset),20,len(localunits));envelope=private/(compartment+'.gcm')
            if r.sha(envelope)!=receipt['ciphertext_receipts'][compartment]['ciphertext_sha256']:raise RuntimeError('COMPARTMENT_CHANGED')
            context=dict(**base,compartment=compartment,shape=list(shape),dtype='<u4')
            data=unseal((private/(compartment+'.key')).read_bytes(),envelope.read_bytes(),context)
            tensor=np.frombuffer(data,dtype='<u4').reshape(shape)
            for region in ('CA1','DG'):fields[region+'_'+compartment]=tensor[:,:,selected[region]]
            fields['conditions_'+compartment]=np.array([conditions.index(t['condition']) for t in subset])
            fields['orders_'+compartment]=np.array([t['provider_row_index'] for t in subset])
            fields['trial_ids_'+compartment]=np.array([t['trial_id'] for t in subset])
            del tensor,data
        path=root/(sid+'.npz');np.savez(path,**fields);a.protect(path)
        manifest['sessions'].append(dict(mouse_id=animal['mouse_id'],session_id=sid,file=path.name,sha256=r.sha(path),
            unit_ids={region:fields[region+'_unit_ids'].tolist() for region in ('CA1','DG')},
            trial_ids={part:fields['trial_ids_'+part].tolist() for part in ('A','B')}))
    validate_manifest(manifest,animals,receipts,r.sha(r.HERE/'results/M2/gate_result.json'),r.sha(r.OLD/'development_registration.json'))
    r.save(root/'manifest.json',manifest,True);a.protect(root/'manifest.json')
    issuer=r.HERE/'.private/development_export_issuer.json'
    a.prepare(issuer.parent)
    a.durable_record(issuer,dict(manifest_sha256=r.sha(root/'manifest.json'),M2_gate_sha256=manifest['M2_gate_sha256'],
        development_registration_sha256=manifest['development_registration_sha256'],method_decision_sha256=manifest['method_decision_sha256']))
    print('ONLY_DEVELOPMENT_AB_EXPORTED; NO_FINAL_CD_ACCESS')


if __name__=='__main__':main()
