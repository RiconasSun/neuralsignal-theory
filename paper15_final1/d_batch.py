"""One frozen Final D batch. Any interruption consumes the attempt permanently."""
import datetime
import os
import csv
import numpy as np
from .source import R,P,read,dump,sha,roster
from .calibration import claim_attempt,wheel
from .admission import verify_pre_D_gate
from .d_support import DContext,raw_D,main_arrays,case_arrays,FrozenPredictors,score_case
from .sensitivities import CASES
from .reference_evaluation import run_controls,control_summary,sensitivity_summary
from .final_statistics import analyze_final,claim_verdicts


def complete_saved_statistics(mouse_rows,case_rows,control_rows,specification):
    stats=analyze_final(mouse_rows,specification)
    sensitivities=sensitivity_summary(case_rows,specification['primary_subjects'])
    controls=control_summary(control_rows,specification['primary_subjects'])
    verdicts=claim_verdicts(stats,sensitivities,controls,specification)
    return stats,sensitivities,controls,verdicts


def run():
    gate=verify_pre_D_gate();spec=read(P/'ONE_SHOT_D_SPECIFICATION.json');seal=read(P/'FINAL_C_STATE_SEAL.json')
    claim=P/'D_BATCH_CLAIM.json'
    record=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',status='STARTED',attempt=1,D_batches=1,
        started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),process_id=os.getpid(),
        gate_sha256=sha(P/'PRE_D_GATE.json'),C_state_seal_sha256=sha(P/'FINAL_C_STATE_SEAL.json'),
        subjects=gate['subjects'],scientific_scope='DESCRIPTIVE ONLY')
    claim_attempt(claim,record)  # Exclusive create+fsync before the first neural D open.
    context=None;mouse_rows=[];case_rows=[];control_rows=[]
    labs={r['subject']:r['lab'] for r in roster()};reference=read(P/'REFERENCE_METADATA_FREEZE.json')
    try:
        context=DContext(claim,record['gate_sha256'],gate['subjects'])
        for subject in gate['subjects']:
            record.update(current_subject=subject,current_stage='AUTHORIZED_D_SOURCE_PROJECTION',D_neural_access_attempted=True)
            dump(claim,record)
            times,labels,source,metadata=raw_D(subject,context);wt,wp=wheel(source)
            record.setdefault('D_projection_completed_subjects',[]).append(subject)
            record['current_stage']='PREDICTION_SENSITIVITIES_AND_REGISTERED_REFERENCES'
            dump(claim,record)
            prep=read(P/'states'/(subject+'_C_PREPROCESSING.json'))
            arrays=main_arrays(times,labels,metadata,prep,wt,wp)
            ids=next(r['D_trial_ids'] for r in reference['records'] if r['subject']==subject)
            assert arrays['trial_ids'].tolist()==ids
            path=P/'work/D_exports'/(subject+'.npz');path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
            np.savez_compressed(path,**arrays)
            predictor=FrozenPredictors(subject,spec['family_subjects'])
            row=dict(subject=subject,lab=labs[subject],models=predictor.score(arrays),trial_ids=ids,
                D_export_sha256=sha(path),C_preprocessing_sha256=sha(P/'states'/(subject+'_C_PREPROCESSING.json')))
            dump(P/'results/D_mice'/(subject+'.json'),row);mouse_rows.append(row)
            for case in CASES:
                statepath=P/'sensitivity_states'/subject/(case['id']+'.json');state=read(statepath)
                panel=dict(subject=subject,lab=labs[subject],case=case['id'],C_state_sha256=sha(statepath),status=state['status'])
                if state['status']=='C_PREPROCESSING_SEALED':
                    values,thinning=case_arrays(subject,state,times,labels,wt,wp);scores,failed=score_case(subject,state,values)
                    panel.update(models=scores,numerically_unavailable_families=failed,thinning_D=thinning,trial_ids=values['trial_ids'].tolist())
                else:panel['unavailability_reasons']=state['unavailability_reasons']
                dump(P/'results/D_sensitivities'/subject/(case['id']+'.json'),panel);case_rows.append(panel)
            control=run_controls(subject,arrays,predictor,prep,next(r for r in reference['records'] if r['subject']==subject))
            crow=dict(subject=subject,lab=labs[subject],suites=control)
            dump(P/'results/D_controls'/(subject+'.json'),crow);control_rows.append(crow)
            print(subject,'frozen D models+11cases+scheduled reference suites sealed',flush=True)
        stats,sens,controls,verdicts=complete_saved_statistics(mouse_rows,case_rows,control_rows,spec)
        outputs={'D_STATISTICS.json':stats,'D_SENSITIVITY_SUMMARY.json':sens,'D_CONTROL_SUMMARY.json':controls,'D_SCIENTIFIC_VERDICTS.json':verdicts}
        for name,value in outputs.items():dump(P/'results'/name,value)
        record.update(status='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH',completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            mouse_count=len(mouse_rows),new_fits=0,result_hashes={n:sha(P/'results'/n) for n in outputs},
            confirmatory_validation=False,second_assessment_authorized=False,current_stage='COMPLETE')
        dump(claim,record)
    except Exception as exc:
        record.update(status='INTERRUPTED_OR_FAILED_IMMUTABLE_D_BATCH',error=type(exc).__name__+': '+str(exc),
            completed_mice=[r['subject'] for r in mouse_rows],completed_control_mice=[r['subject'] for r in control_rows],
            result_incomplete=True,scientific_verdict='INCONCLUSIVE REQUIRED GATE',retry_authorized=False)
        dump(claim,record)
        raise
    finally:
        if context is not None:context.active=False


if __name__=='__main__':run()
