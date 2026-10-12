"""Saved public receipts only. Unknown physiology stays unknown, never zero."""
import csv
import json
from collections import Counter
import common as r
from aggregate4 import summarize


def main():
    registration=r.verify()
    animals=r.load(r.ROOT/'paper12_curated_v1/locks/animals.json')
    trials=r.load(r.ROOT/'paper12_curated_v1/locks/trials.json')
    records={};fingerprints={}
    for animal in animals:
        sid=animal['session_id']
        for kind in ('failures','sessions'):
            path=r.HERE/'results/M2'/kind/(sid+'.json')
            if path.exists():
                record=r.load(path)
                if kind=='sessions':
                    if record['source_etag']!=registration['sources'][sid]['etag']:
                        raise RuntimeError('SAVED_SOURCE_MISMATCH')
                    if record['recovery_registration_sha256']!=r.sha(r.HERE/'registration.json'):
                        raise RuntimeError('SAVED_REGISTRATION_MISMATCH')
                records[sid]=record;fingerprints[str(path.relative_to(r.HERE))]=r.sha(path)
                break
    gate,rows=summarize(animals,records)
    qc_path=r.HERE/'results/M2/aggregate_QC_reasons.json'
    qc={x['session_id']:x for x in r.load(qc_path)['rows']} if qc_path.exists() else {}
    for row in rows:
        sid=row['session_id'];record=records.get(sid,{})
        row['disposition']=record.get('recovery_disposition','FAILED_NEW_EXTRACTION' if 'error_code' in record else 'NOT_EXECUTED')
        row['candidate_units']=record.get('candidate_units')
        row['excluded_units']=record['candidate_units']-sum(record['eligible_unit_counts'].values()) if 'candidate_units' in record else None
        row['exclusion_reason_counts']=json.dumps(qc[sid]['aggregate_reason_counts'],sort_keys=True) if sid in qc else 'UNKNOWN_NOT_COMPLETED'
        row['nonexclusive_QC_rejection_causes']=json.dumps(qc[sid]['nonexclusive_rejection_causes'],sort_keys=True) if sid in qc else 'UNKNOWN_NOT_COMPLETED'
        row['QC_partition']=record.get('qc_partition','train' if row['group']=='development' else 'calibration')
        counts=Counter(t['partition'] for t in trials if t['session_id']==sid and t['metadata_admitted'])
        for part in ('train','validation','calibration','locked_evaluation'):row['metadata_valid_'+part]=counts[part]
        row['trial_count_scope']='Frozen stimulus metadata; not neural completeness certification'
        row['source_decoded_by_custodian']=record.get('source_full_session_decoded_by_custodian')
        row['analysis_final_exposure']=record.get('final_values_exposed_to_analysis',False)
        row['final_evaluated']=record.get('final_holdout_evaluated',False)
        row['observation_limitation']='Curated-release target units; native continuous recording support not independently certified; atlas peak-channel labels not independent histology'
        row['error_code']=record.get('error_code','')
    isolation=r.load(r.HERE/'results/isolation/native.json')
    preflight=r.load(r.HERE/'results/preflight_tests.json')
    if not isolation['mandatory_isolation_pass'] or not preflight['passed']:
        gate.update(gate='FAIL',scientific_verdict='INCONCLUSIVE')
    gate.update(mission='P12-M2-TRANSPORT-RECOVERY-1',receipt_sha256=fingerprints,
        registration_sha256=r.sha(r.HERE/'registration.json'),
        implementation_registration_sha256=r.sha(r.HERE/'implementation_registration.json'),
        native_isolation_pass=isolation['mandatory_isolation_pass'],
        transport_verdict='TRANSPORT_CHECKPOINT_PERMISSION_FAILURE' if any(x.get('error_type')=='PermissionError' for x in records.values()) else 'TRANSPORT_UNRECOVERABLE' if any('error_code' in x for x in records.values()) else 'COMPLETE' if len(records)==26 else 'IN_PROGRESS',
        engineering_success_is_not_biological_success=True,
        original_timeout_preserved_sha256=registration['original_timeout_sha256'],
        M3_M5_authorized_only_if_this_M2_passes=True)
    output=r.HERE/'results/M2';output.mkdir(parents=True,exist_ok=True)
    r.save(output/'gate_result.json',gate)
    r.save(r.HERE/'results/reuse_vs_new_manifest.json',dict(frozen_denominator=26,
        rows=[dict(session_id=x['session_id'],mouse_id=x['mouse_id'],group=x['group'],
            disposition=x['disposition'],status=x['status']) for x in rows],
        prior_progress_preserved='results/reuse_vs_new_current.json',
        unexecuted_not_discarded=True))
    with (output/'mouse_disposition.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print({k:v for k,v in gate.items() if k!='receipt_sha256'})


if __name__=='__main__':main()
