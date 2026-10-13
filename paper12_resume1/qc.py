"""Trusted train/calibration QC aggregates, never decrypts final evaluation."""
from collections import Counter
import study as r
import verified_atomic as a
from preflight import guard,verify_reuse
from run_real import validate


def main():
    guard();verify_reuse();rows=[]
    animals={x['session_id']:x for x in r.load(r.ROOT/'paper12_curated_v1/locks/animals.json')}
    for path in sorted((r.HERE/'results/M2/sessions').glob('*.json')):
        receipt=r.load(path);sid=receipt['session_id']
        if receipt['artifact_study']=='paper12_custody1':
            root=r.OLD/'.private'/receipt['custody_artifact_namespace']/sid
        else:root=validate(receipt,animals[sid])
        audit=r.load(root/'private_provenance.json')['unit_QC']
        actual={roi:sum(x['eligible'] and x['subfield']==roi for x in audit) for roi in ('CA1','DG')}
        if actual!=receipt['eligible_unit_counts'] or len(audit)!=receipt['candidate_units']:
            raise RuntimeError('QC_RECEIPT_MISMATCH')
        failures=Counter();reason=Counter(x['reason'] for x in audit)
        for unit in audit:
            if unit['reason']=='FROZEN_PHYSIOLOGICAL_QC_REJECT':
                if not .1<=unit['rate_Hz']<=100:failures['rate_out_of_bounds']+=1
                if unit['active_trial_fraction']<.1:failures['active_fraction_below_threshold']+=1
                if unit['ISI_under_1ms_fraction']>.01:failures['ISI_fraction_above_threshold']+=1
                if unit['invalid_permitted_timestamps']:failures['invalid_permitted_timestamps']+=1
        rows.append(dict(session_id=sid,group=receipt['group'],QC_partition=receipt['qc_partition'],
            eligible_unit_counts=actual,candidate_units=len(audit),aggregate_reason_counts=dict(reason),
            nonexclusive_rejection_causes=dict(failures),final_values_read=False,
            unit_level_details_exported=False,QC_rule='train/cal only: .1-100 Hz, active>=.1, ISI<1ms fraction<=.01, no invalid permitted timestamps'))
    r.save(r.HERE/'results/M2/aggregate_QC_reasons.json',dict(rows=rows,scope='Custodian aggregate admission evidence, not analysis model-selection input'))
    print(dict(completed_QC_reports=len(rows),final_evaluation_access=False))


if __name__=='__main__':main()
