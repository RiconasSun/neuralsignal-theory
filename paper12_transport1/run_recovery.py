"""Same scientific extractor/index fix,only transport/storage changed prospectively."""
import sys
import types
import uuid
from collections import Counter
import common as r
import custodian as c
import index2
from range_transport import Source


def guard(require_isolation=True):
    registration=r.verify();c.check_gate()
    implementation=r.load(r.HERE/'implementation_registration.json')
    for name,digest in implementation['implementation_sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('RECOVERY_IMPLEMENTATION_CHANGED')
    if implementation['registration_sha256']!=r.sha(r.HERE/'registration.json'):
        raise RuntimeError('RECOVERY_POLICY_CHANGED')
    issuer=r.OLD/'.private/transport_recovery1/reuse_issuer.json'
    if r.sha(issuer)!=implementation['private_reuse_issuer_sha256']:raise RuntimeError('REUSE_ISSUER_CHANGED')
    for sid,artifact in r.load(issuer).items():
        for name,digest in artifact['fingerprints'].items():
            if r.sha(r.OLD/'.private'/artifact['namespace']/sid/name)!=digest:
                raise RuntimeError('PRIOR_PRIVATE_ARTIFACT_CHANGED')
    if require_isolation:
        proof=r.load(r.HERE/'results/isolation/native.json')
        if proof['mandatory_isolation_pass'] is not True:raise RuntimeError('ACCESS_ISOLATION_FAILED')
        tests=r.load(r.HERE/'results/preflight_tests.json')
        if tests['passed'] is not True:raise RuntimeError('SYNTHETIC_PREFLIGHT_FAILED')
        for name,digest in tests['test_code_sha256'].items():
            if r.sha(r.HERE/name)!=digest:raise RuntimeError('SYNTHETIC_PREFLIGHT_STALE')
        if tests['log_sha256']!=r.sha(r.HERE/'results/preflight_tests.log'):
            raise RuntimeError('SYNTHETIC_PREFLIGHT_LOG_CHANGED')
    return registration


def extractor(namespace='transport_recovery1/sessions'):
    old=index2.session_callable()
    storage={'.private/real_index2':'.private/'+namespace,
             'results/M2/index2/sessions':'../paper12_transport1/results/M2/extracted',
             'results/M2/index2/failures':'../paper12_transport1/results/M2/failures'}
    found=[x for x in old.__code__.co_consts if isinstance(x,str) and x in storage]
    if sorted(found)!=sorted(storage):raise RuntimeError('RECOVERY_STORAGE_PATCH_SCOPE')
    code=old.__code__.replace(co_consts=tuple(storage.get(x,x) if isinstance(x,str) else x for x in old.__code__.co_consts))
    namespace=dict(old.__globals__);namespace['Source']=Source
    return types.FunctionType(code,namespace)


def validate_completion(receipt,animal,source):
    for key in ('session_id','mouse_id','group'):
        if receipt[key]!=animal[key]:raise RuntimeError('COMPLETE_IDENTITY_INVALID')
    if receipt['source_etag']!=source['etag']:raise RuntimeError('COMPLETE_SOURCE_INVALID')
    expected=('A','B') if animal['group']=='development' else ('C','D')
    if set(receipt['ciphertext_receipts'])!=set(expected):raise RuntimeError('COMPLETE_COMPARTMENTS_INVALID')
    if receipt['qc_partition']!=('train' if animal['group']=='development' else 'calibration'):
        raise RuntimeError('COMPLETE_QC_ROLE_INVALID')
    for key in ('final_values_exposed_to_analysis','final_holdout_evaluated','raw_vectors_exported'):
        if receipt[key] is not False:raise RuntimeError('COMPLETE_ACCESS_INVALID')
    namespace=receipt['custody_artifact_namespace']
    if not namespace.startswith('transport_recovery1/sessions/run_') or '/' in namespace[len('transport_recovery1/sessions/run_'):]:
        raise RuntimeError('COMPLETE_NAMESPACE_INVALID')
    private=r.OLD/'.private'/namespace/receipt['session_id']
    for part,expected in receipt['ciphertext_receipts'].items():
        path=private/(part+'.gcm')
        if path.stat().st_size!=expected['ciphertext_bytes'] or r.sha(path)!=expected['ciphertext_sha256']:
            raise RuntimeError('COMPLETE_CIPHERTEXT_INVALID')
        if (private/(part+'.key')).stat().st_size!=32:raise RuntimeError('COMPLETE_KEY_INVALID')


def seal_session(receipt,animal,source):
    validate_completion(receipt,animal,source)
    sid=receipt['session_id'];private=r.OLD/'.private'/receipt['custody_artifact_namespace']/sid
    hashes={name:r.sha(private/name) for name in ['private_provenance.json']+
            [part+ext for part in receipt['ciphertext_receipts'] for ext in ('.gcm','.key')]}
    path=r.OLD/'.private/transport_recovery1/completed_issuers'/(sid+'.json')
    r.save(path,dict(receipt=receipt,artifact_sha256=hashes),True);c.protect(path.parent);c.protect(path)


def verify_completed(receipt):
    sid=receipt['session_id'];issuer=r.load(r.OLD/'.private/transport_recovery1/completed_issuers'/(sid+'.json'))
    if issuer['receipt']!=receipt:raise RuntimeError('CURRENT_COMPLETE_RECEIPT_CHANGED')
    for name,digest in issuer['artifact_sha256'].items():
        if r.sha(r.OLD/'.private'/receipt['custody_artifact_namespace']/sid/name)!=digest:
            raise RuntimeError('CURRENT_COMPLETE_ARTIFACT_CHANGED')


def main():
    registration=guard()
    if list((r.HERE/'results/M2/failures').glob('*.json')):
        raise RuntimeError('PRESERVED_RECOVERY_FAILURE_STOP')
    old=r.ROOT/'paper12_curated_v1'
    animals=r.load(old/'locks/animals.json');units=r.load(old/'locks/units.json');trials=r.load(old/'locks/trials.json')
    items={x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    manifest=[]
    for animal in animals:
        sid=animal['session_id'];item=items[sid];expected=registration['sources'][sid]
        if dict(file_id=item['file_id'],etag=item['etag'],bytes=int(item['content_range'].split('/')[-1]))!={k:expected[k] for k in ('file_id','etag','bytes')}:
            raise RuntimeError('FROZEN_SOURCE_IDENTITY_CHANGED')
        if r.sha(r.OLD/'results/index2/audit'/(sid+'.json'))!=expected['raw_index_audit_sha256']:
            raise RuntimeError('PRIOR_RAW_INDEX_AUDIT_CHANGED')
        bad=r.HERE/'results/M2/failures'/(sid+'.json')
        if bad.exists():raise RuntimeError('PRESERVED_RECOVERY_FAILURE_STOP')
        public=r.HERE/'results/M2/sessions'/(sid+'.json')
        if sid in registration['reuse']:
            previous=r.OLD/'results/M2/index2/sessions'/(sid+'.json')
            if r.sha(previous)!=registration['reuse'][sid]['receipt_sha256']:raise RuntimeError('PRIOR_RECEIPT_CHANGED')
            receipt=r.load(previous);receipt.update(recovery_disposition='REUSED_UNCHANGED_ARTIFACTS',prior_receipt_sha256=r.sha(previous))
            receipt['custody_artifact_namespace']=receipt.get('custody_artifact_namespace','real_index2')
        else:
            if public.exists():
                receipt=r.load(public);verify_completed(receipt)
            else:
                raw=r.HERE/'results/M2/extracted'/(sid+'.json')
                issuer=r.OLD/'.private/transport_recovery1/completed_issuers'/(sid+'.json')
                plan=r.OLD/'.private/transport_recovery1/plans'/(sid+'.json')
                if raw.exists():
                    receipt=r.load(raw)
                    saved_plan=r.load(plan)
                    if saved_plan['session_id']!=sid or saved_plan['source']!=expected:
                        raise RuntimeError('RECOVERY_PLAN_CHANGED')
                    namespace=saved_plan['namespace']
                else:
                    namespace='transport_recovery1/sessions/run_'+uuid.uuid4().hex
                    # Interrupted work is preserved; verified raw-byte cache is reused.
                    plan.parent.mkdir(parents=True,exist_ok=True);c.protect(plan.parent)
                    if plan.exists():
                        previous=plan.with_name(sid+'.prior_'+uuid.uuid4().hex+'.json');plan.rename(previous)
                    r.save(plan,dict(namespace=namespace,session_id=sid,source=expected),True);c.protect(plan)
                    execute=extractor(namespace)
                    execute(animal,item,[u for u in units if u['session_id']==sid],[t for t in trials if t['session_id']==sid])
                    receipt=r.load(raw)
                receipt.update(recovery_disposition='NEW_FROZEN_EXTRACTION',custody_artifact_namespace=namespace,
                               recovery_registration_sha256=r.sha(r.HERE/'registration.json'))
                validate_completion(receipt,animal,expected)
                if issuer.exists():verify_completed(receipt)
                else:seal_session(receipt,animal,expected)
        receipt['recovery_registration_sha256']=r.sha(r.HERE/'registration.json')
        if public.exists():
            if r.load(public)!=receipt:raise RuntimeError('RESUME_PUBLIC_RECEIPT_CHANGED')
        else:r.save(public,receipt,True)
        manifest.append(dict(session_id=sid,group=animal['group'],disposition=receipt['recovery_disposition'],receipt_sha256=r.sha(public)))
        r.save(r.HERE/'results/reuse_vs_new_current.json',dict(rows=manifest,frozen_denominator=26))
    groups=Counter(x['group'] for x in animals)
    print(dict(full_cohort_extraction_complete=True,groups=dict(groups),final_holdout_evaluated=False))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(dict(stopped=True,error_type=type(exc).__name__,error_code=str(exc) if isinstance(exc,RuntimeError) else 'RECOVERY_ABORT'),flush=True)
        sys.exit(1)
