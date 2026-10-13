"""Public receipts only; incomplete physiology never classified insufficient."""
import csv
import json
from collections import Counter
import study as r
import verified_atomic
from aggregate4 import summarize


def main():
    r.verify()
    animals=r.load(r.ROOT/'paper12_curated_v1/locks/animals.json')
    trials=r.load(r.ROOT/'paper12_curated_v1/locks/trials.json')
    records={};hashes={}
    for animal in animals:
        sid=animal['session_id']
        for kind in ('failures','sessions'):
            path=r.HERE/'results/M2'/kind/(sid+'.json')
            if path.exists():
                records[sid]=r.load(path);hashes[path.relative_to(r.HERE).as_posix()]=r.sha(path);break
    gate,rows=summarize(animals,records)
    qpath=r.HERE/'results/M2/aggregate_QC_reasons.json'
    qc={x['session_id']:x for x in r.load(qpath)['rows']} if qpath.exists() else {}
    for row in rows:
        sid=row['session_id'];receipt=records.get(sid,{})
        row.update(disposition=receipt.get('recovery_disposition','FAILED_NEW_EXTRACTION' if 'error_code' in receipt else 'NOT_EXECUTED'),
            candidate_units=receipt.get('candidate_units'),excluded_units=(receipt['candidate_units']-sum(receipt['eligible_unit_counts'].values())) if 'eligible_unit_counts' in receipt else None,
            exclusion_reasons=json.dumps(qc[sid]['aggregate_reason_counts'],sort_keys=True) if sid in qc else 'UNKNOWN',
            QC_rejection_causes=json.dumps(qc[sid]['nonexclusive_rejection_causes'],sort_keys=True) if sid in qc else 'UNKNOWN',
            QC_partition=receipt.get('qc_partition','train' if row['group']=='development' else 'calibration'),
            source_integrity='ETag/range/body/envelope SHA verified; no independent whole-file SHA' if 'eligible_unit_counts' in receipt else 'INCOMPLETE_OR_UNASSESSED',
            custodian_decoded=receipt.get('source_full_session_decoded_by_custodian'),
            analysis_final_exposed=receipt.get('final_values_exposed_to_analysis',False),
            final_evaluation_performed=receipt.get('final_holdout_evaluated',False),error_code=receipt.get('error_code',''),
            observation_limitations='Curated release only; native continuity not independently certified; peak-channel atlas labels are not independent histology')
        counts=Counter(t['partition'] for t in trials if t['session_id']==sid and t['metadata_admitted'])
        for part in ('train','validation','calibration','locked_evaluation'):row['valid_metadata_'+part]=counts[part]
    pre=r.load(r.HERE/'results/preflight.json') if (r.HERE/'results/preflight.json').exists() else {}
    iso=r.load(r.HERE/'results/isolation.json') if (r.HERE/'results/isolation.json').exists() else {}
    gate.update(mission=r.ID,registration_sha256=r.sha(r.HERE/'registration.json'),receipt_sha256=hashes,
        preflight_pass=pre.get('passed',False),native_isolation_pass=iso.get('mandatory_isolation_pass',False),
        analysis_visible_neural_data=False,final_evaluation_exposure=False,
        engineering_success_not_biological_success=True,
        M3_M5='NOT_EXECUTED' if gate['gate']!='PASS' else 'AUTHORIZED_PENDING_EXECUTION')
    if not gate['preflight_pass'] or not gate['native_isolation_pass']:
        gate.update(gate='FAIL',scientific_verdict='INCONCLUSIVE',engineering_blocker='ENVIRONMENT_OR_ISOLATION_NOT_VERIFIED')
    elif any('error_code' in x for x in records.values()):
        gate['engineering_blocker']='REAL_EXTRACTION_OR_TRANSPORT_FAILED'
    r.save(r.HERE/'results/M2/gate_result.json',gate)
    with (r.HERE/'results/M2/mouse_disposition.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print({k:v for k,v in gate.items() if k!='receipt_sha256'})


if __name__=='__main__':main()
