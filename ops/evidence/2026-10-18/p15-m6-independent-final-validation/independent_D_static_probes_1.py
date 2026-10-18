"""Synthetic-only saved-score/report probes; never open D or model arrays."""
import copy,datetime,json,uuid
from pathlib import Path
from unittest.mock import patch
from paper15_final1.source import R,P,E,read,sha,roster
from paper15_final1.statistics import CONTRASTS
from paper15_final1.final_statistics import analyze_final,claim_verdicts,MANDATORY_CASES
from paper15_final1.reference_evaluation import control_summary,sensitivity_summary
from paper15_final1 import report

files=['d_support.py','admission.py','d_batch.py','reference_evaluation.py','reference_metadata.py','final_statistics.py','seal_C.py','report.py','anatomy_report.py','saved_verify.py','reproduce.ps1','test_D_boundary_statistics.py','synthetic_rehearsal.py']
hashes={n:sha(P/n) for n in files}
subjects=['SYNTHETIC_ONLY_'+str(i) for i in range(6)]
families={f:subjects[:] for f in ['B0','B1','B2','B3','B4','C','D','S']}
spec=dict(primary_subjects=subjects,family_subjects=families,contrast_subjects={c:subjects[:] for c in CONTRASTS},
    source_main_numerical_valid=True,confirmatory_assumptions_defensible=False,static_capacity_pair_valid=True,mandatory_descriptive_only=True)
bad_controls=[]
for i,s in enumerate(subjects):
    panel=dict(status='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE',replicates_completed=0,observed=[9.]*6,
        reference_effects=[[0.]*6 for _ in range(999)],original_model_scores={f:dict(LL=1000.,unit_bins=1000) for f in families},
        mapping_sha256=[],seeds=[])
    bad_controls.append(dict(subject=s,lab='fixture_lab'+str(i%4),suites={n:copy.deepcopy(panel) for n in ['N1','N2','N3','N4']}))
bad_result=control_summary(bad_controls,subjects)
assert bad_result['B4-B1']['N1']['observed_equal_mouse_mean']==9. and bad_result['B4-B1']['N1']['descriptive_disruption_gate']
bad_rows=[dict(subject=s,lab='fixture_lab'+str(i%4),trial_ids=list(range(60)),models={f:dict(LL=10.+(1 if f=='B4' else 0),unit_bins=1) for f in families}) for i,s in enumerate(subjects)]
bad_statistics=analyze_final(bad_rows,spec)
assert bad_statistics['B4-B1']['equal_mouse_mean']==1.

# Isolated report-schema fixture. All outcomes below are fabricated test values.
root=P/'work'/('INDEPENDENT_SYNTHETIC_REPORT_ONLY_'+uuid.uuid4().hex);root.mkdir(parents=True)
(root/'README_SYNTHETIC_ONLY.txt').write_text('Synthetic report-schema test only. No real D results or scientific evidence.\n')
(root/'D_BATCH_CLAIM.json').write_text('{}');(root/'FINAL_C_STATE_SEAL.json').write_text('{}')
original_roster=roster();qc=read(P/'results/FINAL_C_QC_GATE.json');meta=read(P/'results/FINAL_METADATA_GATE.json')
real_subjects=[r['subject'] for r in qc['subjects'] if r['admitted']]
sspec=copy.deepcopy(spec);sspec.update(primary_subjects=real_subjects,family_subjects={f:real_subjects[:] for f in families},contrast_subjects={c:real_subjects[:] for c in CONTRASTS})
labs={r['subject']:r['lab'] for r in original_roster}
rows=[dict(subject=s,lab=labs[s],models={f:dict(LL=-100.+(i+1 if f=='B4' else 0),unit_bins=1000) for f in families}) for i,s in enumerate(real_subjects)]
stats=analyze_final(rows,sspec)
case_rows=[dict(subject=s,lab=labs[s],case=f'S{j:02}',status='C_PREPROCESSING_SEALED',models=copy.deepcopy(rows[i]['models'])) for i,s in enumerate(real_subjects) for j in range(1,12)]
sens=sensitivity_summary(case_rows,real_subjects)
controls=copy.deepcopy(bad_result)
for panels in controls.values():
    panels['N4']=dict(status='UNAVAILABLE_MINIMUM_PAIRED_MICE',n_mice=3,p_reference=1.,Holm4_reference_p=1.)
verdicts=claim_verdicts(stats,sens,controls,sspec)
fixtures={'FINAL_METADATA_GATE.json':meta,'FINAL_C_QC_GATE.json':qc,
    'D_BATCH_CLAIM.json':dict(status='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH',D_projection_completed_subjects=real_subjects,D_neural_access_attempted=True),
    'D_STATISTICS.json':stats,'D_SENSITIVITY_SUMMARY.json':sens,'D_CONTROL_SUMMARY.json':controls,'D_SCIENTIFIC_VERDICTS.json':verdicts,
    'E_STATISTICS.json':{c:dict(equal_mouse_mean=0.,n_mice=10) for c in CONTRASTS}}
for r in qc['subjects']:
    if r['C_neural_access']:fixtures[r['subject']+'_C_QC.json']=read(P/'results'/(r['subject']+'_C_QC.json'))
def fixture_read(path):
    if Path(path).name not in fixtures:raise AssertionError('Unexpected fixture report read: '+str(path))
    return fixtures[Path(path).name]
def fixture_attempts(folder):return [dict(path='SYNTHETIC_ONLY_'+str(i),status='NUMERICAL_PASS') for i in range(72 if folder=='fits' else 320)]
with patch.object(report,'P',root),patch.object(report,'read',side_effect=fixture_read),patch.object(report,'attempts',side_effect=fixture_attempts),patch('paper15_final1.anatomy_report.build',return_value=({},b'')),patch('numpy.load',side_effect=PermissionError('Synthetic report probe denies array reads')),patch('socket.socket.connect',side_effect=PermissionError('Synthetic report probe denies network')):
    report.build()
delivery=read(root/'results/FINAL_DELIVERY.json')
required=['FINAL_SOURCE_PASS','FINAL_C_READER_SCOPE','FINAL_C_QC_PASS','FINAL_ELIGIBLE_MICE','FINAL_ELIGIBLE_LABS','FINAL_C_MODEL_CALIBRATION','FINAL_MAIN_FIT_ATTEMPTS','FINAL_SENSITIVITY_FIT_ATTEMPTS','PRE_D_INDEPENDENT_REVIEW','ONE_SHOT_D_EXECUTED','FINAL_PRIMARY_EFFECT','FINAL_PRIMARY_CI','FINAL_PRIMARY_P_VALUE','FINAL_SECONDARY_EFFECTS','FINAL_HOLM_ADJUSTED_RESULTS','FINAL_FALSIFICATION_RESULTS','DEVELOPMENT_FINAL_CONSISTENCY','SCIENTIFIC_PRIMARY_VERDICT','SCIENTIFIC_SECONDARY_VERDICTS','PROMPT_5_READY','BUG_COUNT','WARN_COUNT','GIT_COMMIT','REMOTE_VERIFICATION']
assert set(required)<=set(delivery) and delivery['SCIENTIFIC_PRIMARY_VERDICT']=='DESCRIPTIVE ONLY' and not delivery['confirmatory_validation']
assert all(v=='DESCRIPTIVE ONLY' for v in delivery['SCIENTIFIC_SECONDARY_VERDICTS'].values())
out=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),hashes=hashes,
    synthetic_controls_wrong_observed_and_zero_completed_missing_schedules_accepted=True,
    synthetic_wrong_main_unit_bin_exposure_accepted=True,synthetic_report_schema_completed=True,required_owner_fields_checked=len(required),
    synthetic_report_fixture=root.relative_to(P).as_posix(),real_report_executed=False,real_D_access=False,real_fits=0,raw_arrays_loaded=0,
    current_findings='Missing independent schedule/score/exposure/manifest validation in saved_verify; no D rerun is authorized')
(E/'D_STATIC_INDEPENDENT_PROBES_1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='hashes'},sort_keys=True))
