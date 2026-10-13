"""Close the new gate only after complete source, issuer, trial and QC evidence."""
from collections import Counter
import types
import study as r
import verified_atomic as a
from preflight import guard,verify_reuse
from fingerprints import check as check_fingerprints
import summarize
import qc
from transport import byte_range,prior_budget


def audit_transport(reg):
    rows=[]
    for sid,source in reg['sources'].items():
        if sid in reg['reuse']:continue
        root=r.HERE/'.private/cache'/sid
        complete=r.HERE/'results/M2/sessions'/(sid+'.json')
        if not root.exists():
            if complete.exists():raise RuntimeError('COMPLETED_SESSION_CACHE_MISSING')
            continue
        blocks=0;attempts=0;carried=0
        for descriptor in sorted(root.glob('b_*.json')):
            saved=r.load(descriptor);identity=saved['source']
            if {k:identity[k] for k in ('file_id','etag','size')}!=dict(file_id=source['file_id'],etag=source['etag'],size=source['bytes']):
                raise RuntimeError('CHECKPOINT_SOURCE_IDENTITY_CHANGED')
            start,end=byte_range('bytes=%s-%s'%(identity['start'],identity['end']),identity['size'])
            name='b_%016x'%start
            if descriptor.name!=name+'.json':raise RuntimeError('CHECKPOINT_NAME_RANGE_CHANGED')
            target=root/(name+'.checkpoint')
            if r.sha(target)!=saved['artifact_sha256'] or len(a.read(target,identity,saved['body_sha256']))!=end-start+1:
                raise RuntimeError('CHECKPOINT_POST_EXTRACTION_INTEGRITY_FAILED')
            ledger=root/(name+'_http');origin=r.load(ledger/'origin.json')
            if origin['source']!=identity or origin['used']!=prior_budget(r.OLD/'.private/transport_recovery1/cache'/sid,identity):
                raise RuntimeError('POST_EXTRACTION_BUDGET_CHANGED')
            consumed=origin['used'];carried+=consumed
            new=[n for n in range(consumed+1,4) if (ledger/(str(n)+'.intent.json')).exists()]
            if new!=list(range(consumed+1,consumed+len(new)+1)) or consumed+len(new)>3:
                raise RuntimeError('TRANSPORT_ATTEMPT_BOUND_VIOLATION')
            for n in new:
                if r.load(ledger/(str(n)+'.intent.json'))!=dict(source=identity,attempt=n):raise RuntimeError('HTTP_INTENT_CHANGED')
                result=r.load(ledger/(str(n)+'.result.json'))
                if result.get('attempt')!=n or result.get('status') not in ('VERIFIED_COMPLETE_BLOCK','TRANSIENT_FAILURE'):
                    raise RuntimeError('TRANSPORT_TERMINAL_RESULT')
            attempts+=len(new);blocks+=1
        if complete.exists() and not blocks:raise RuntimeError('COMPLETED_SESSION_NO_VERIFIED_BLOCKS')
        targets={p.stem for p in root.glob('b_*.checkpoint')}
        descriptors={p.stem for p in root.glob('b_*.json')}
        if targets!=descriptors:raise RuntimeError('CHECKPOINT_DESCRIPTOR_DENOMINATOR_MISMATCH')
        if (root/'STOP.json').exists() and complete.exists():raise RuntimeError('COMPLETION_WITH_TRANSPORT_STOP')
        rows.append(dict(session_id=sid,verified_checkpoint_blocks=blocks,new_HTTP_attempts=attempts,
                         prior_consumed_HTTP_attempts=carried,all_full_hashes_and_ranges_verified=True,
                         final_contents_decoded_by_audit=False,raw_ranges_published=False))
    expected={sid for sid in reg['sources'] if sid not in reg['reuse'] and (r.HERE/'results/M2/sessions'/(sid+'.json')).exists()}
    if {x['session_id'] for x in rows if x['verified_checkpoint_blocks']}>expected:raise RuntimeError('SOURCE_AUDIT_UNEXPECTED_COMPLETION')
    if {x['session_id'] for x in rows if x['verified_checkpoint_blocks']}!=expected:raise RuntimeError('SOURCE_AUDIT_COMPLETION_DENOMINATOR_MISMATCH')
    r.save(r.HERE/'results/M2/source_checkpoint_integrity.json',dict(rows=rows,
        expected_completed_new_sessions=len(expected),verified_completed_new_sessions=len(expected),
        audit_implementation_sha256=r.sha(r.HERE/'finalize_m2.py'),
        scope='Trusted opaque byte verification only; not independent whole-file provider checksum'))


def main():
    reg=guard();verify_reuse()
    animals=r.load(r.ROOT/'paper12_curated_v1/locks/animals.json')
    trials=r.load(r.ROOT/'paper12_curated_v1/locks/trials.json')
    verified=[]
    for animal in animals:
        p=r.HERE/'results/M2/sessions'/(animal['session_id']+'.json')
        if not p.exists():continue
        receipt=r.load(p);check_fingerprints(receipt,reg);verified.append(animal['session_id'])
        local=[t for t in trials if t['session_id']==animal['session_id'] and t['metadata_admitted']]
        partitions=('train','validation') if animal['group']=='development' else ('calibration','locked_evaluation')
        for condition in {t['condition'] for t in local}:
            for part,minimum in zip(partitions,(24,16)):
                if sum(t['condition']==condition and t['partition']==part for t in local)<minimum:
                    raise RuntimeError('FROZEN_TRIAL_ADMISSION_FAILED')
        if len({t['condition'] for t in local})!=8:raise RuntimeError('TRIAL_CONDITION_MISSING')
    qc.main();audit_transport(reg)
    namespace=dict(summarize.main.__globals__);proxy=types.SimpleNamespace(**vars(r))
    def save_candidate(path,value,exclusive=False):
        if path==r.HERE/'results/M2/gate_result.json':path=r.HERE/'replay/M2_gate_candidate.json'
        r.save(path,value,exclusive)
    proxy.save=save_candidate;namespace['r']=proxy
    types.FunctionType(summarize.main.__code__,namespace)()
    gate=r.load(r.HERE/'replay/M2_gate_candidate.json')
    reason_rows=r.load(r.HERE/'results/M2/aggregate_QC_reasons.json')['rows']
    if set(verified)!={x['session_id'] for x in reason_rows}:raise RuntimeError('QC_DENOMINATOR_MISMATCH')
    gate.update(completion_issuer_verified_count=len(verified),QC_reports=len(reason_rows),
                full_source_checkpoint_audit=True,final_values_exposed_to_analysis=False,
                final_holdout_evaluated=False,original_M2_reclassified=False,
                completion_audit_code_sha256=r.sha(r.HERE/'finalize_m2.py'))
    if gate['gate']=='PASS' and len(verified)!=26:raise RuntimeError('PARTIAL_COHORT_PASS_FORBIDDEN')
    r.save(r.HERE/'results/M2/gate_result.json',gate)
    print(dict(new_M2_gate=gate['gate'],scientific_verdict=gate['scientific_verdict'],eligible_mice=gate['eligible_mice']))


if __name__=='__main__':main()
