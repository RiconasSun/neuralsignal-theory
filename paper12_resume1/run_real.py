"""Immutable scientific extractor; prospective scoped transport/storage adapter only."""
import sys
import types
import uuid
import study as r
import verified_atomic as a
from preflight import guard, verify_reuse
from transport import Source
import index2
import custodian as c


def extractor(namespace):
    old=index2.session_callable()
    replacements={'.private/real_index2':'.private/'+namespace,
                  'results/M2/index2/sessions':'results/M2/extracted',
                  'results/M2/index2/failures':'results/M2/failures'}
    found=[x for x in old.__code__.co_consts if isinstance(x,str) and x in replacements]
    if sorted(found)!=sorted(replacements):raise RuntimeError('EXTRACTOR_ADAPTER_SCOPE')
    code=old.__code__.replace(co_consts=tuple(replacements.get(x,x) if isinstance(x,str) else x for x in old.__code__.co_consts))
    namespace_globals=dict(old.__globals__)
    encrypted_globals=dict(c.encrypted_write.__globals__)
    # Context study remains original custody ID; downstream cipher compatibility unchanged.
    proxy=types.SimpleNamespace(**vars(r));proxy.ID='P12-M2-ISOLATED-CUSTODY-1'
    encrypted_globals.update(r=proxy,protect=a.protect)
    encrypted=types.FunctionType(c.encrypted_write.__code__,encrypted_globals)
    namespace_globals.update(r=proxy,Source=Source,protect=a.protect,
                             check_gate=guard,encrypted_write=encrypted)
    return types.FunctionType(code,namespace_globals)


def validate(receipt,animal):
    for key in ('session_id','mouse_id','group'):
        if receipt[key]!=animal[key]:raise RuntimeError('SESSION_IDENTITY_CHANGED')
    if receipt['source_etag']!=r.load(r.HERE/'registration.json')['sources'][animal['session_id']]['etag']:
        raise RuntimeError('SOURCE_CHANGED')
    expected={'A','B'} if animal['group']=='development' else {'C','D'}
    if set(receipt['ciphertext_receipts'])!=expected:raise RuntimeError('COMPARTMENTS_INVALID')
    if receipt['qc_partition']!=('train' if animal['group']=='development' else 'calibration'):
        raise RuntimeError('QC_PARTITION_INVALID')
    if any(receipt[k] is not False for k in ('final_values_exposed_to_analysis','final_holdout_evaluated','raw_vectors_exported')):
        raise RuntimeError('NEURAL_ACCESS_BOUNDARY_FAILED')
    ns=receipt['custody_artifact_namespace']
    if not ns.startswith('sessions/run_') or '/' in ns[len('sessions/run_'):]:raise RuntimeError('ARTIFACT_NAMESPACE_INVALID')
    root=r.HERE/'.private'/ns/animal['session_id']
    for part,value in receipt['ciphertext_receipts'].items():
        a.check_acl(root/(part+'.gcm'));a.check_acl(root/(part+'.key'))
        if r.sha(root/(part+'.gcm'))!=value['ciphertext_sha256'] or (root/(part+'.gcm')).stat().st_size!=value['ciphertext_bytes'] or (root/(part+'.key')).stat().st_size!=32:
            raise RuntimeError('ARTIFACT_INTEGRITY_FAILED')
    return root


def main():
    reg=guard();verify_reuse()
    if list((r.HERE/'results/M2/failures').glob('*.json')):raise RuntimeError('NEW_CRITICAL_FAILURE_STOP')
    frozen=r.ROOT/'paper12_curated_v1'
    animals=r.load(frozen/'locks/animals.json');units=r.load(frozen/'locks/units.json');trials=r.load(frozen/'locks/trials.json')
    items={x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    for animal in animals:
        sid=animal['session_id'];public=r.HERE/'results/M2/sessions'/(sid+'.json')
        if sid in reg['reuse']:
            receipt=r.load(r.OLD/'results/M2/index2/sessions'/(sid+'.json'))
            receipt.update(recovery_disposition='REUSED_UNCHANGED',prior_receipt_sha256=reg['reuse'][sid]['receipt_sha256'],
                           artifact_study='paper12_custody1')
            receipt['custody_artifact_namespace']=receipt.get('custody_artifact_namespace','real_index2')
        else:
            item=items[sid];expected=reg['sources'][sid]
            if dict(file_id=item['file_id'],etag=item['etag'],bytes=int(item['content_range'].split('/')[-1]))!={k:expected[k] for k in ('file_id','etag','bytes')}:
                raise RuntimeError('FROZEN_SOURCE_IDENTITY_CHANGED')
            raw=r.HERE/'results/M2/extracted'/(sid+'.json')
            plan=r.HERE/'.private/plans'/(sid+'.json')
            if not raw.exists():
                if plan.exists():raise RuntimeError('INTERRUPTED_EXTRACTION_REQUIRES_AUDIT')
                ns='sessions/run_'+uuid.uuid4().hex
                a.prepare(plan.parent);a.durable_record(plan,dict(namespace=ns,source=expected,session_id=sid))
                try:
                    extractor(ns)(animal,item,[u for u in units if u['session_id']==sid],[t for t in trials if t['session_id']==sid])
                except Exception as exc:
                    private=r.HERE/'.private/diagnostics'/(sid+'.json');a.prepare(private.parent)
                    a.durable_record(private,dict(error_type=type(exc).__name__,message=str(exc),events=getattr(exc,'events',[]),winerror=getattr(exc,'winerror',None)))
                    # Extractor's public message may contain a path. Preserve exact bytes privately.
                    failure=r.HERE/'results/M2/failures'/(sid+'.json')
                    if failure.exists():
                        copy=private.with_suffix('.original.json');a.durable_record(copy,r.load(failure))
                        value=r.load(failure);value['error_code']=str(exc) if isinstance(exc,RuntimeError) and len(str(exc))<100 and '/' not in str(exc) and '\\' not in str(exc) else 'SOURCE_OR_CHECKPOINT_FAILURE'
                        value['private_original_sha256']=r.sha(copy);r.save(failure,value)
                    raise RuntimeError('REAL_EXTRACTION_CRITICAL_STOP') from None
            receipt=r.load(raw);saved=r.load(plan)
            if saved['source']!=expected or saved['session_id']!=sid:raise RuntimeError('PLAN_CHANGED')
            receipt.update(custody_artifact_namespace=saved['namespace'],artifact_study='paper12_resume1',
                           recovery_disposition='NEW_FROZEN_EXTRACTION')
            root=validate(receipt,animal)
            issuer=r.HERE/'.private/issuers'/(sid+'.json')
            hashes={p.name:r.sha(p) for p in root.iterdir() if p.is_file()}
            value=dict(receipt=receipt,artifact_sha256=hashes)
            if issuer.exists():
                if r.load(issuer)!=value:raise RuntimeError('COMPLETE_ISSUER_CHANGED')
            else:a.prepare(issuer.parent);a.durable_record(issuer,value)
        receipt['registration_sha256']=r.sha(r.HERE/'registration.json')
        if public.exists():
            if r.load(public)!=receipt:raise RuntimeError('PUBLIC_RECEIPT_CHANGED')
        else:r.save(public,receipt,True)
    print('26_FROZEN_SESSIONS_COMPLETED; FINAL_EVALUATION_NOT_PERFORMED')


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(dict(stopped=True,error_type=type(exc).__name__,error_code=str(exc) if isinstance(exc,RuntimeError) else 'REAL_CONTINUATION_ABORT'),flush=True)
        sys.exit(1)
