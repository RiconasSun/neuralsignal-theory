"""Reviewer-owned saved-result transcription only; no scientific imports/calculations."""
from pathlib import Path
import ast,csv,datetime,hashlib,json
R=Path(__file__).resolve().parents[4];E=Path(__file__).parent;used={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
lockpath=R/'paper15_manuscript/SOURCE_HASHES.json';lock=json.loads(lockpath.read_text())
def source(rel):
    path=R/rel;assert path.is_file() and path.suffix in ('.json','.csv','.md','.txt') and '/work/' not in '/'+rel
    h=sha(path);assert lock['hashes'][rel]==h,rel;used[rel]=h;return path
def read(rel):return json.loads(source(rel).read_text())
def table(rel):
    with source(rel).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def pick(d,keys):return {k:d[k] for k in keys if k in d}
order=['B4-B1','B4-B3','B4-B2','D-B4','C-B4','D-S'];labels={
 'B4-B1':'Combined own/other-unit history beyond measured nuisance baseline',
 'B4-B3':'Own history conditional on other-unit history and nuisances',
 'B4-B2':'Other-unit history conditional on own history and nuisances',
 'D-B4':'Selected discrete predictive model beyond combined history GLM',
 'C-B4':'Selected continuous-history representation beyond combined history GLM',
 'D-S':'Selected discrete model versus larger static mixture capacity guard'}
source('paper15_m1/STATISTICS_CONTROLS.md');source('paper15_m1/SCIENTIFIC_PROTOCOL.md');source('paper15_m1/FEATURE_MODELS.md');source('paper15_m1/SOURCE_QC.md')
cohort=table('paper15_m1/COHORT.csv');assert len(cohort)==20
devqc=table('paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv');finqc=table('paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv')
selection=read('paper15_r1/SELECTION_FREEZE.json');devstatus=read('paper15_r1/results/DEVELOPMENT_STATUS.json');devclaim=read('paper15_r1/results/CLAIM_TO_EVIDENCE_AUDIT.json');fclaim=read('paper15_final1/results/FINAL_CLAIM_TO_EVIDENCE_AUDIT.json');delivery=read('paper15_final1/results/FINAL_DELIVERY.json')
spec=read('paper15_final1/ONE_SHOT_D_SPECIFICATION.json');devsubjects=selection['subjects'];fsubjects=spec['primary_subjects'];assert len(devsubjects)==10 and len(fsubjects)==6
labs={r['subject']:r['lab'] for r in cohort};assert len({labs[s] for s in devsubjects})==8 and len({labs[s] for s in fsubjects})==4
case_defs={}
for i in range(1,12):
    st=read(f'paper15_final1/sensitivity_states/UCLA037/S{i:02}.json');case_defs[f'S{i:02}']=st['case']
result=dict(schema='P15_M7_RESULTS_LOCKED_CONSISTENCY_ORACLE_V1',mission='P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE',reviewer='/root/gradient_review',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),base='bdec0e19621cc8018abe11c5633ce76aff611443',source_lock_sha256=sha(lockpath),source_lock_entries=len(lock['hashes']),registered_contrast_order=order,contrast_meanings=labels,units='nats per actual scored nominal curated-release unit-bin;50ms except S04=100ms',original_cohort=dict(total=20,Development=12,Final_reserved=8,rows=cohort,analyzed_total=16,exclusions=[dict(subject='NYU-37',cohort='Development',reason='B epoch count31 below40;registered metadata trial/unit coverage',source='paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv'),dict(subject='CSHL059',cohort='Development',reason='Identity sync domain[0,1],zero covered A/B/E epochs;registered metadata trial/unit coverage',source='paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv'),dict(subject='NYU-21',cohort='Final',reason='Native wheel strict-order failure;16,485 equal adjacent timestamp pairs;no C neural extraction',source='paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv'),dict(subject='UCLA033',cohort='Final',reason='Six C-qualified units below frozen eight-unit minimum',source='paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv')]),selection=dict(source='paper15_r1/SELECTION_FREEZE.json',selected=selection['selected'],frozen_at=selection['frozen_at'],rule=selection['rule'],C_states_fit_on=selection['C_states_fit_on'],E_neural_access=selection['E_neural_access'],Final_neural_access=selection['Final_neural_access']),case_definitions=case_defs,cohorts={})
summary_keys=['contrast','n_mice','n_labs','equal_mouse_mean','CI95','CI_width','paired_sign_flip_p','Holm5_adjusted_p','test_side','median','IQR','SD','positive_mice','positive_fraction','mouse_effects','lab_means','equal_lab_mean','leave_one_mouse_out_means','leave_one_lab_out_means','lab_block_bootstrap_CI95','bootstrap_replicates','bootstrap_seed','lab_bootstrap_seed','status','exploratory','validated','heldout_animal_confirmation','inferential_assumption']
control_keys=['status','n_mice','subjects','observed_equal_mouse_mean','mouse_original','mouse_reference_medians','mean_degradation','mice_above_reference_median','descriptive_disruption_gate','p_reference','Holm4_reference_p','statistic','exact_mechanistic_null','validated']
for name,base,prefix,subjects in [('Development','paper15_r1','E',devsubjects),('Final','paper15_final1','D',fsubjects)]:
    mainpath=f'{base}/results/{prefix}_STATISTICS.json';sp=f'{base}/results/{prefix}_SENSITIVITY_SUMMARY.json';cp=f'{base}/results/{prefix}_CONTROL_SUMMARY.json'
    main=read(mainpath);sens=read(sp);control=read(cp);refs=read(f'{base}/REFERENCE_METADATA_FREEZE.json')
    csvmain=table(f'{base}/tables/'+('E_CONTRASTS.csv' if name=='Development' else 'FINAL_CONTRASTS.csv'))
    assert set(main)==set(order) and len(csvmain)==6
    for row in csvmain:
        r=main[row['contrast']];assert float(row['mean'])==r['equal_mouse_mean'] and ast.literal_eval(row['CI95'])==r['CI95'] and float(row['raw_p'])==r['paired_sign_flip_p']
        assert (float(row['Holm5_p']) if row['Holm5_p'] else None)==r.get('Holm5_adjusted_p')
    table(f'{base}/tables/'+('E_CONTROLS.csv' if name=='Development' else 'FINAL_CONTROLS.csv'));table(f'{base}/tables/'+('E_SENSITIVITIES.csv' if name=='Development' else 'FINAL_SENSITIVITIES.csv'))
    coverage=[]
    for row in refs['records']:
        coverage.append(dict(subject=row['subject'],suites={k:pick(v,['available','epochs','total_epochs','trial_ids']) for k,v in row['coverage'].items()}))
    # Copy every saved sensitivity panel without introducing a p-value or recomputing a CI.
    sen_order={k:{c:sens[k][c] for c in ['B4-B1','B4-B3','B4-B2']} for k in [f'S{i:02}' for i in range(1,12)]}
    record=dict(subjects=subjects,n_mice=len(subjects),n_labs=len({labs[s] for s in subjects}),labs={s:labs[s] for s in subjects},interpretation='Exploratory Development only' if name=='Development' else 'DESCRIPTIVE ONLY; six-mouse fallback frozen before D',main_source=mainpath,main={c:pick(main[c],summary_keys) for c in order},sensitivity_source=sp,sensitivities=sen_order,sensitivity_scope='B0–B4 refits only; only B4-B1/B4-B3/B4-B2 contrasts; no D/C/S sensitivity-refit credit',control_source=cp,controls={c:{n:pick(control[c][n],control_keys) for n in ['N1','N2','N3','N4']} for c in order},reference_coverage_source=f'{base}/REFERENCE_METADATA_FREEZE.json',reference_coverage=coverage,negative_or_unavailable_control_panels=[dict(contrast=c,suite=n,**pick(control[c][n],control_keys)) for c in order for n in ['N1','N2','N3','N4'] if control[c][n].get('descriptive_disruption_gate') is not True],all_five_secondary_Holm_nonsignificant=True)
    if name=='Final':record['verdicts']=read('paper15_final1/results/D_SCIENTIFIC_VERDICTS.json')
    result['cohorts'][name]=record
table('paper15_r1/tables/E_MOUSE_EFFECTS.csv');table('paper15_final1/tables/FINAL_DISTRIBUTION_AND_LAB_DIAGNOSTICS.csv')
source('paper15_r1/DEVELOPMENT_REPORT.md');source('paper15_final1/FINAL_SCIENTIFIC_REPORT.md')
read('paper15_r1/results/MAIN_SAVED_VERIFICATION.json');read('paper15_r1/results/SENSITIVITY_SAVED_VERIFICATION.json');read('paper15_final1/FINAL_C_STATE_SEAL.json');read('paper15_final1/D_BATCH_CLAIM.json')
result['numerical_policy_source']='paper15_m1/NUMERICAL_POLICY.json';result['numerical_policy']=read(result['numerical_policy_source'])
result['attempt_ledger']=dict(historical_original_attempts=359,historical_rounded_input_completed_numerical_PASS=358,historical_interrupted_STARTED=1,historical_unattempted_of_original610=251,historical_status='STOP_SOURCE_IMPLEMENTATION_DEFECT;not reused/relabelled as corrected fits',separately_authorized_R1=dict(main=610,sensitivity=525,total_new=1135,numerical_PASS=1135,cumulative_after=1494,absolute_main_cap=732,absolute_sensitivity_cap=660,cohort_main_cap=610,cohort_sensitivity_cap=550),Final=dict(main_C=72,sensitivity_C=320,total_new=392,numerical_PASS=392,absolute_main_cap=96,absolute_sensitivity_cap=440,cohort_sensitivity_cap=330,cumulative_after=1886,D_batches=1,new_D_fits=0),retrospective_original_ceiling_compliance_claim=False,sources=['paper15_r1/results/DEVELOPMENT_STATUS.json','paper15_r1/DEVELOPMENT_REPORT.md','paper15_final1/results/FINAL_DELIVERY.json','paper15_final1/FINAL_C_STATE_SEAL.json','paper15_final1/D_BATCH_CLAIM.json'])
assert devstatus['NEW_MAIN_ATTEMPTS']==610 and devstatus['NEW_SENSITIVITY_ATTEMPTS']==525 and devstatus['TOTAL_CUMULATIVE_ATTEMPTS']==1494 and delivery['cumulative_attempts']==1886
result['reference_counts']=dict(Development=dict(available_suites=devclaim['valid_reference_suites'],unavailable_suites=devclaim['unavailable_reference_suites'],replicate_bundles=devclaim['reference_replicate_bundles'],reference_fits=0),Final=dict(available_suites=21,unavailable_suites=3,replicate_bundles=spec['expected_reference_bundles'],reference_fits=0))
result['claim_restrictions']=[
 'Every Development result remains exploratory; every available Final comparison remains DESCRIPTIVE ONLY.',
 'Original20 animals:12Development/8Final;10Development8labs and6Final4labs admitted;four exclusions are retained and never replaced.',
 'No independent-laboratory replication; equal-lab and lab-block summaries are dependence diagnostics.',
 'Mouse is the unit of inference; actual scored nominal curated-release unit-bin denominators; no pooled unit/trial inference.',
 'Final primary CI width0.09166131577698394 exceeds frozen0.01 precision gate; n6 fails n8 positive-claim floor; symmetry/independence unestablished.',
 'Development primary N1 gate failed7/10<8/10; N2passed10/10. Final primary N1/N2passed6/6; this cannot override the descriptive verdict.',
 'All five secondary Holm5 tests are nonsignificant in both cohorts. Final raw minimum two-sided p2/64 and Holm5 minimum0.15625 are discrete resolution facts,not power or equivalence.',
 'Development D-B4 mean is negative; Final descriptive mean is positive. No pooled/new contrast,mechanistic transition or superiority follows.',
 'All11 sensitivity cases/33panels per cohort are baseline-only. Development S02n9/S03n6;Final S02n6/S03n4. Final S03 aggregate unavailable; no D/C/S sensitivity robustness.',
 'N4 aggregate unavailable in both cohorts:5Development/3Final mice below6; corresponding drift-independent/persistent-state restrictions retained.',
 'N3 formal statistic is B4LL/Q wheel reliance diagnostic copied across contrast slots; separate B4-B1 gain descriptive. No independent D/C wheel null or all-movement independence.',
 'Finite references are destructive diagnostics,not assumption-free exact mechanistic/causal/population nulls. False disruption conjunctions remain false despite a small reference p.',
 'No causal connectivity/motor-command mechanism,biological discrete-state finding,CWP/NAP proof,human/BCI validation,independent-lab replication or all-movement independence.',
 'C model name versus Final calibration partition C and D model name versus assessment partition D must be disambiguated in every text/legend.',
 'Source restrictions include curated provider whole-session labels,known selected-probe saturation masks,strict-past native precision,observational wheel confounding,and contact/atlas proxies; no histological-depth claim.',
 'No new scientific analysis,selection,model evaluation,fit,hypothesis test or second Final D assessment is permitted in M7.'
]
result['methods_inference']=dict(primary='B4-B1 one-sided exhaustive sign-flip',secondary='fixed5 two-sided sign-flip with Holm5',bootstrap='saved10000 whole-mouse percentile draws,PCG64seed150101;not recomputed here',lab_bootstrap='saved10000 lab-block diagnostic draws,seed150102;not independent lab replication',Final_sign_assignments=64,Final_min_primary_p=0.015625,Final_min_secondary_raw_p=0.03125,Final_min_Holm5_p=0.15625,source='paper15_m1/STATISTICS_CONTROLS.md')
result['source_hashes']=used
result['checks']=dict(used_old_sources_match_frozen_SOURCE_HASHES=True,old_source_hashes_checked=len(used),saved_main_JSON_CSV_pairs_exact=12,registered_contrast_order_preserved=True,sensitivity_panels_copied=66,control_panels_copied=48,source_arrays_read=0,scientific_modules_imported_or_executed=0,new_predictions_or_LLs_or_ADFD=0,new_fits=0,new_hypothesis_tests=0,new_D_assessments=0)
target=E/'RESULTS_CONSISTENCY_ORACLE.json'
with target.open('x',encoding='utf8') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps(dict(oracle_sha256=sha(target),used_sources=len(used),main_rows=12,sensitivity_panels=66,control_panels=48),indent=2))
