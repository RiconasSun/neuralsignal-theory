"""Consumed-entitlement-only compartment producer. Keys never leave trusted custody."""
from pathlib import Path
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
if __package__:
    from .common import *
else:from common import *

def validate_catalog(binding,body):
    binding=Path(binding);c=read_json(binding/'C_state_manifest.json');p=read_json(binding/'partition_manifest.json');catalog=read_json(binding/'source_catalog.json')
    validate_partition(c,p,read_json(binding/'animals.json') if not c['synthetic'] else None,read_json(binding/'trials.json') if not c['synthetic'] else None)
    if catalog['realm']!=body['realm'] or catalog['cohort']!=c['cohort'] or set(catalog['sessions'])!=set(c['cohort']) or (body['realm']=='SYNTHETIC_D') is not c['synthetic']:raise PermissionError('SOURCE_CATALOG_REALM_COHORT')
    roots=read_json(binding/'source_roots.json')
    if roots['realm']!=body['realm'] or set(roots['sessions'])!=set(c['cohort']):raise PermissionError('EXACT_SOURCE_ROOT_ROSTER')
    for mouse in c['cohort']:
        item=catalog['sessions'][mouse];part=p['sessions'][mouse]
        if item['mouse_id']!=mouse or item['session_id']!=part['session_id'] or item['trial_ids_D']!=part['trial_ids'] or len(item['source_unit_ids'])!=len(set(item['source_unit_ids'])):raise PermissionError('SOURCE_CATALOG_IDENTITIES')
        if item['context']['compartment']!='D' or item['context']['dtype']!='<u4' or item['context']['shape']!=[len(part['trial_ids']),20,len(item['source_unit_ids'])] or item['context']['mouse']!=mouse:raise PermissionError('SOURCE_D_COMPARTMENT_SHAPE')
        source_units=read_json(binding/'source_units.json')
        if source_units[item['session_id']]!=item['source_unit_ids']:raise PermissionError('SOURCE_ORDERED_UNIT_LOCK')
        if c['synthetic']:
            if item['context']['unit_lock_sha256']!=sha(binding/'source_units.json') or item['context']['trial_lock_sha256']!=sha(binding/'partition_manifest.json'):raise PermissionError('SOURCE_ORDERED_UNIT_TRIAL_LOCK')
        else:
            original_units=read_json(binding/'units.json');receipt=read_json(binding/('source_receipt_'+item['session_id']+'.json'))
            expected=[u['unit_id'] for u in original_units if u['session_id']==item['session_id']]
            context={'study':'P12-M2-ISOLATED-CUSTODY-1','mouse':mouse,'source_etag':receipt['source_etag'],'trial_lock_sha256':sha(binding/'trials.json'),'unit_lock_sha256':sha(binding/'units.json'),'compartment':'D','shape':[len(part['trial_ids']),20,len(expected)],'dtype':'<u4'}
            if item['source_unit_ids']!=expected or item['context']!=context or item['ciphertext_sha256']!=receipt['ciphertext_receipts']['D']['ciphertext_sha256'] or receipt['session_id']!=item['session_id'] or receipt['mouse_id']!=mouse or receipt['group']!='final':raise PermissionError('ORIGINAL_CUSTODY_RECEIPT_CONTEXT')
            if item['cipher_file']!=item['session_id']+'/D.gcm' or item['key_file']!=item['session_id']+'/D.key':raise PermissionError('ORIGINAL_D_SOURCE_NAMES')
            location=roots['sessions'][mouse]
            if location['artifact_study']!=receipt['artifact_study'] or location['namespace']!=receipt['custody_artifact_namespace'] or Path(location['root']).as_posix()!=Path(roots['repository_root'],receipt['artifact_study'],'.private',receipt['custody_artifact_namespace']).as_posix():raise PermissionError('ORIGINAL_CUSTODY_ROOT_MAPPING')
        if any(Path(item[name]).is_absolute() or '..' in Path(item[name]).parts for name in ('cipher_file','key_file')):raise PermissionError('SOURCE_CATALOG_PATH')
        selected=[]
        for region in ('CA1','DG'):
            case=next(k for k in c['cases'] if k['mouse_id']==mouse and k['region']==region and k['view']=='primary');selected+=case['unit_ids']
        if not set(selected)<=set(item['source_unit_ids']):raise PermissionError('SOURCE_CATALOG_SELECTED_UNITS')
    return c,p,catalog

def produce(context,verify_target,protect,hook=lambda point:None):
    # Revalidate immutable signed artifacts and durable proof even for a direct call.
    if __package__:
        from .production_broker import revalidate_context
    else:from production_broker import revalidate_context
    body=revalidate_context(context,verify_target,require_delivery_fence=True)
    binding=Path(context['binding_root']);source=Path(context['source_root']);destination=Path(context['delivery_root'])
    c,p,catalog=validate_catalog(binding,body)
    roots=read_json(binding/'source_roots.json')
    if body['realm']=='SYNTHETIC_D':
        job=Path(context['job_root']).resolve()
        if any(not Path(v['root']).resolve().is_relative_to(job/'.private/synthetic_sources') for v in roots['sessions'].values()):raise PermissionError('SYNTHETIC_SOURCE_NAMESPACE')
    if sha(__file__)!=read_json(binding/'code_identity.json')['source_sha256']['custodian_producer.py']:raise PermissionError('PRODUCER_VERSION')
    destination.mkdir(exist_ok=False);protect(destination)
    sessions={};source_receipts={}
    for mouse in c['cohort']:
        verify_target(body['principal']);s=catalog['sessions'][mouse];part=p['sessions'][mouse]
        root=Path(roots['sessions'][mouse]['root']);cipherpath=safe(root,root/s['cipher_file']);keypath=safe(root,root/s['key_file'])
        envelope=cipherpath.read_bytes()
        if digest(envelope)!=s['ciphertext_sha256'] or envelope[:8]!=b'P12GCM1\0' or len(envelope)<36:raise PermissionError('D_ENVELOPE_INTEGRITY')
        key=keypath.read_bytes()
        if len(key)!=32:raise PermissionError('D_KEY_LENGTH')
        raw=AESGCM(key).decrypt(envelope[8:20],envelope[20:],canonical(s['context']))
        if len(raw)!=int(np.prod(s['context']['shape']))*4:raise PermissionError('D_PAYLOAD_LENGTH')
        tensor=np.frombuffer(raw,dtype='<u4').reshape(s['context']['shape']);fields={};selected={}
        for region in ('CA1','DG'):
            case=next(k for k in c['cases'] if k['mouse_id']==mouse and k['region']==region and k['view']=='primary');ids=case['unit_ids'];indices=[s['source_unit_ids'].index(i) for i in ids]
            fields[region+'_D']=tensor[:,:,indices].copy();fields[region+'_unit_ids']=np.array(ids);selected[region]=ids
        fields.update(trial_ids_D=np.array(part['trial_ids']),conditions_D=np.array(part['conditions']),orders_D=np.array(part['orders']))
        file=s['session_id']+'.npz'
        if Path(file).name!=file:raise PermissionError('OUTPUT_SESSION_PATH')
        path=destination/file
        with path.open('xb') as handle:np.savez(handle,**fields);handle.flush();__import__('os').fsync(handle.fileno())
        protect(path)
        sessions[mouse]={'file':file,'sha256':sha(path),'unit_ids':selected,'trial_ids':part['trial_ids'],'trial_mask_sha256':digest(canonical(part['trial_ids'])),'source_ciphertext_sha256':s['ciphertext_sha256']}
        source_receipts[mouse]={'source_ciphertext_sha256':s['ciphertext_sha256'],'authenticated_context_sha256':digest(canonical(s['context'])),'output_sha256':sessions[mouse]['sha256'],'selected_units':selected,'exact_D_trial_mask_sha256':sessions[mouse]['trial_mask_sha256']}
        del tensor,raw,key,fields
        hook('after_private_export')
    delivered={k:context[k] for k in ('realm','authorization_id','binding','principal','C_manifest_sha256','partition_sha256','code_sha256')}
    delivered.update(complete=True,cohort=c['cohort'],sessions=sessions,source_integrity_receipts=source_receipts,keys_exported=False,unrestricted_vectors_exported=False,producer_sha256=sha(__file__))
    new(destination/'delivery_manifest.json',delivered);protect(destination/'delivery_manifest.json')
    for item in sessions.values():
        if sha(safe(destination,destination/item['file']))!=item['sha256']:raise PermissionError('OUTPUT_ROUNDTRIP_INTEGRITY')
    if {x.name for x in destination.iterdir()}!={v['file'] for v in sessions.values()}|{'delivery_manifest.json'}:raise PermissionError('EXACT_DELIVERY_OUTPUT_ROSTER')
    hook('after_complete_staging');return delivered
