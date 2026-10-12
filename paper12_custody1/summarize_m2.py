"""Aggregate only public eligibility counts,never private calibration unit details."""
from collections import Counter
import csv
import register as r


def main():
    r.verify()
    old=r.ROOT/'paper12_curated_v1'
    animals=r.load(old/'locks/animals.json')
    success=r.HERE/'results/M2/transport1/sessions'
    failure=r.HERE/'results/M2/transport1/failures'
    rows=[];eligible=Counter();completed=Counter();decoded=False
    critical=False
    for a in animals:
        sid=a['session_id'];path=success/(sid+'.json');bad=failure/(sid+'.json')
        record=r.load(path) if path.exists() else r.load(bad) if bad.exists() else None
        row={'mouse_id':a['mouse_id'],'session_id':sid,'group':a['group'],
             'metadata_potential_CA1':a['anatomical_potential_units']['CA1'],
             'metadata_potential_DG':a['anatomical_potential_units']['DG'],
             'eligible_CA1':'NOT_ASSESSED','eligible_DG':'NOT_ASSESSED',
             'actually_eligible_mouse':'NOT_ASSESSED','status':'NOT_EXECUTED',
             'source_full_session_decoded_by_custodian':False,'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False}
        if record:
            decoded |= record['source_full_session_decoded_by_custodian']
            row['source_full_session_decoded_by_custodian']=record['source_full_session_decoded_by_custodian']
            if record['final_values_exposed_to_analysis'] or record['final_holdout_evaluated']:
                raise RuntimeError('CUSTODY_BOUNDARY_VIOLATED')
            if path.exists():
                if record['mouse_id']!=a['mouse_id'] or record['group']!=a['group']:
                    raise RuntimeError('FROZEN_COHORT_IDENTITY_CHANGED')
                completed[a['group']]+=1;eligible[a['group']]+=record['eligible_mouse']
                row.update({'eligible_CA1':record['eligible_unit_counts']['CA1'],'eligible_DG':record['eligible_unit_counts']['DG'],
                            'actually_eligible_mouse':record['eligible_mouse'],'status':'QC_COMPLETED'})
            else:
                row['status']='EXTRACTION_FAILED';critical=True
        rows.append(row)
    if critical:
        gate='FAIL';verdict='INCONCLUSIVE';reason='SOURCE_EXTRACTION_INTEGRITY_FAILED'
    elif completed['development']==13 and completed['final']==13:
        ok=eligible['development']>=8 and eligible['final']>=8
        gate='PASS' if ok else 'FAIL';verdict='COHORT_ADMISSION_PASS' if ok else 'DATA_INSUFFICIENT';reason='FROZEN_PHYSIOLOGICAL_QC'
    else:
        gate='NOT_COMPLETE';verdict='NOT_ASSESSED';reason='COHORT_EXTRACTION_PENDING'
    result={'gate':gate,'scientific_verdict':verdict,'reason':reason,'candidate_development_mice':13,'candidate_final_mice':13,
            'completed_QC':dict(completed),'verified_eligible_to_date':dict(eligible),
            'source_full_session_decoded_by_custodian':decoded,'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False,
            'original_M2_reclassified':False,'full_study_validated':False,'unit_QC_detail':'Private;not a development selection input'}
    out=r.HERE/'results/M2';out.mkdir(exist_ok=True,parents=True)
    with (out/'mouse_denominator.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    r.save(out/'current_gate_result.json',result)
    print(result)


if __name__=='__main__':main()
