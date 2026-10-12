"""Trusted training/calibration-only QC reason counts; no neural value export."""
from collections import Counter
import common as r
import custodian as c
from run_recovery import guard,verify_completed


def main():
    registration=guard();c.require_custodian()
    rows=[]
    for path in sorted((r.HERE/'results/M2/sessions').glob('*.json')):
        receipt=r.load(path);sid=receipt['session_id']
        if sid not in registration['reuse']:verify_completed(receipt)
        private=r.OLD/'.private'/receipt['custody_artifact_namespace']/sid/'private_provenance.json'
        audit=r.load(private)['unit_QC']
        reasons=Counter(x['reason'] for x in audit)
        failures=Counter()
        for unit in audit:
            if unit['reason']!='FROZEN_PHYSIOLOGICAL_QC_REJECT':continue
            if not .1<=unit['rate_Hz']<=100:failures['rate_outside_frozen_bounds']+=1
            if unit['active_trial_fraction']<.1:failures['active_fraction_below_threshold']+=1
            if unit['ISI_under_1ms_fraction']>.01:failures['ISI_fraction_above_threshold']+=1
            if unit['invalid_permitted_timestamps']:failures['invalid_permitted_timestamps']+=1
        actual={roi:sum(x['eligible'] and x['subfield']==roi for x in audit) for roi in ('CA1','DG')}
        if actual!=receipt['eligible_unit_counts'] or len(audit)!=receipt['candidate_units']:
            raise RuntimeError('PRIVATE_PUBLIC_QC_MISMATCH')
        rows.append(dict(session_id=sid,group=receipt['group'],QC_partition=receipt['qc_partition'],
            aggregate_reason_counts=dict(reasons),nonexclusive_rejection_causes=dict(failures),
            eligible_unit_counts=actual,unit_level_details_exported=False,
            final_evaluation_values_read=False,source_vectors_read=False))
    r.save(r.HERE/'results/M2/aggregate_QC_reasons.json',dict(rows=rows,
        scope='Trusted custodian aggregate train/calibration QC report only; not scientific model selection input',
        implementation_sha256=r.sha(r.HERE/'custody_qc_report.py')))
    print(dict(completed_QC_reports=len(rows),final_holdout_evaluated=False))


if __name__=='__main__':main()
