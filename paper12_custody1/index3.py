"""Trusted audit-completion attestation and strict-bound recovery ledger."""
import sys
from datetime import datetime,timezone
import register as r
import custodian as original
import index2
import source_safe4
from cache_binding3 import validate


def inputs():
    old=r.ROOT/'paper12_curated_v1'
    animals=r.load(old/'locks/animals.json')
    items={x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    return old,animals,items


def expected(a,item):
    return {k:a[k] for k in ('mouse_id','session_id','group')}|{
        'source':{'file_id':item['file_id'],'etag':item['etag'],'bytes':int(item['content_range'].split('/')[-1])},
        'index_registration_sha256':r.sha(r.HERE/'index_registration2.json')}


def attest():
    original.check_gate()
    registration=r.load(r.HERE/'index_registration2.json')
    for path,value in registration['sha256'].items():
        if r.sha(r.HERE/path)!=value:raise RuntimeError('INDEX_AUDIT_GENERATOR_CHANGED')
    old,animals,items=inputs();bindings={}
    for a in animals:
        sid=a['session_id'];path=r.HERE/'results/index2/audit'/(sid+'.json')
        audit=r.load(path);previous=r.HERE/'results/M2/transport1/sessions'/(sid+'.json')
        exp=expected(a,items[sid]);entry={**exp,'audit_sha256':r.sha(path),
            'previous_output_sha256':r.sha(previous) if previous.exists() else None}
        validate(audit,entry,exp,r.sha(path),r.load(previous) if previous.exists() else None,
                 r.sha(previous) if previous.exists() else None)
        bindings[sid]=entry
    record={'utc':datetime.now(timezone.utc).isoformat(),'issuer':'Trusted host/controller;generated after all26 live raw-index audits;not a claim of independent-human attestation',
            'prior_source_mapping_sha256':r.sha(r.ROOT/'paper12/metadata/allen_header_capability.json'),
            'animal_lock_sha256':r.sha(old/'locks/animals.json'),'bindings':bindings,
            'implementation_sha256':{p:r.sha(r.HERE/p) for p in ('index3.py','cache_binding3.py','test_cache_binding3.py','source_safe4.py','test_source_safe4.py')},
            'all_raw_audits_strict_true':True,'original_results_overwritten':False}
    # Public content is metadata and fingerprints only; store issuer copy protected.
    private=r.HERE/'.private/audit_completion_binding3.json'
    r.save(private,record,True);original.protect(private)
    r.save(r.HERE/'audit_completion_binding3.json',record,True)
    print('All26 source/identity/registration/audit/previous-output bindings attested')


def main():
    if '--attest' in sys.argv:attest();return
    original.check_gate()
    index_reg=r.load(r.HERE/'index_registration2.json')
    for path,value in index_reg['sha256'].items():
        if r.sha(r.HERE/path)!=value:raise RuntimeError('INDEX_IMPLEMENTATION_CHANGED_AFTER_AUDIT')
    record=r.load(r.HERE/'audit_completion_binding3.json')
    if r.sha(r.HERE/'audit_completion_binding3.json')!=r.sha(r.HERE/'.private/audit_completion_binding3.json'):
        raise RuntimeError('TRUSTED_AUDIT_ATTESTATION_CHANGED')
    for p,value in record['implementation_sha256'].items():
        if r.sha(r.HERE/p)!=value:raise RuntimeError('CACHE_BINDING_IMPLEMENTATION_CHANGED')
    old,animals,items=inputs();units=r.load(old/'locks/units.json');trials=r.load(old/'locks/trials.json')
    execute=index2.session_callable()
    execute.__globals__['Source']=source_safe4.Source
    for a in animals:
        sid=a['session_id'];auditpath=r.HERE/'results/index2/audit'/(sid+'.json')
        previous=r.HERE/'results/M2/transport1/sessions'/(sid+'.json')
        binding=record['bindings'][sid];exp=expected(a,items[sid])
        validate(r.load(auditpath),binding,exp,r.sha(auditpath),r.load(previous) if previous.exists() else None,
                 r.sha(previous) if previous.exists() else None)
        current=r.HERE/'results/M2/index2/sessions'/(sid+'.json');bad=r.HERE/'results/M2/index2/failures'/(sid+'.json')
        if bad.exists():raise RuntimeError('PRESERVED_INDEX2_FAILURE_STOP')
        if current.exists():
            existing=r.load(current)
            for field in ('mouse_id','session_id','group'):
                if existing.get(field)!=a[field]:raise RuntimeError('CURRENT_QC_IDENTITY_MISMATCH')
            if existing.get('source_etag')!=items[sid]['etag'] or existing.get('final_values_exposed_to_analysis') is not False or existing.get('final_holdout_evaluated') is not False:
                raise RuntimeError('CURRENT_QC_SOURCE_OR_ACCESS_MISMATCH')
            if previous.exists() and (existing.get('prior_output_sha256')!=r.sha(previous) or existing.get('audit_attestation_sha256')!=r.sha(r.HERE/'audit_completion_binding3.json')):
                raise RuntimeError('CURRENT_REUSED_QC_BINDING_MISMATCH')
            continue
        if previous.exists():
            value=r.load(previous);value.update(index_validation='Raw audit+bound source/identity/registration/hashes validated before reuse',
                prior_output_sha256=r.sha(previous),audit_attestation_sha256=r.sha(r.HERE/'audit_completion_binding3.json'),
                custody_artifact_namespace='real_transport1')
            r.save(current,value,True)
        else:
            execute(a,items[sid],[u for u in units if u['session_id']==sid],[t for t in trials if t['session_id']==sid])


if __name__=='__main__':
    try:main()
    except Exception:
        print('BOUND_INDEX3_STOP_CHECK_RECEIPTS',flush=True);sys.exit(1)
