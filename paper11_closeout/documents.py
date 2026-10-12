"""Populate manuscript, supplement and A1-A10 from saved summary evidence."""
import argparse
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from build import Saved, REPORT, config_label, export_tables, table, write_json
from freeze import HERE, ROOT, sha


REFERENCES = [
    ('Boran E, Fedele T, Steiner A, Hilfiker P, Stieglitz L, Grunwald T, Sarnthein J. (2020). Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task. Scientific Data 7, 30.', 'https://doi.org/10.1038/s41597-020-0364-3', 'paper11/data_manifest/metadata/nm_description.json'),
    ('Boran E et al. (2019). Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load. Science Advances 5(3), eaav3687.', 'https://doi.org/10.1126/sciadv.aav3687', 'paper11/data_manifest/metadata/nm_description.json'),
    ('Dimakopoulos V, Megevand P, Stieglitz LH, Imbach L, Sarnthein J. (2022). Information flows from hippocampus to auditory cortex during replay of verbal working memory items. eLife 11, e78677.', 'https://doi.org/10.7554/eLife.78677', 'paper11/data_manifest/metadata/ds_description.json'),
    ('Niediek J, Bostrom J, Elger CE, Mormann F. (2016). Reliable Analysis of Single-Unit Recordings from the Human Brain under Noisy Conditions: Tracking Neurons over Hours. PLoS ONE 11, e0166598.', 'https://doi.org/10.1371/journal.pone.0166598', 'paper11/data_manifest/metadata/nm_readme.md'),
    ('Chandravadia N et al. (2020). A NWB-based dataset and processing pipeline of human single-neuron activity during a declarative memory task. Scientific Data.', 'https://doi.org/10.1038/s41597-020-0415-9', 'paper11/data_manifest/metadata/dandi_info.json'),
    ('Cao R, Brunner P, Brandmeir NJ, Willie JT, Wang S. (2025). A human single-neuron dataset for object recognition. Scientific Data 12, 79.', 'https://doi.org/10.1038/s41597-024-04265-1', 'paper11_v2/alt_cohort_audit1/FEASIBILITY_REPORT.md'),
    ('Kolibius LD et al. (2023). Hippocampal neurons code individual episodic memories in humans. Nature Human Behaviour 7, 1968-1979.', 'https://doi.org/10.1038/s41562-023-01706-6', 'paper11_v2/alt_cohort_audit1/FEASIBILITY_REPORT.md'),
    ('NEURALSIGNAL INSTITUTE. (2026). P11-v2 frozen predictive implementations and exploratory evidence. Repository snapshot 33dc10db016d69b656dd2491be041b1f6d15826c. Internal code/evidence record, not a peer-reviewed validation.', 'https://github.com/RiconasSun/neuralsignal-theory/tree/33dc10db016d69b656dd2491be041b1f6d15826c/paper11_v2', 'paper11_v2/protocol/protocol.json')
]

CLAIMS = {
 'C01': ('Cohort9patients23sessions592session-local units622train201dev trials', ['paper11_v2/results/R2_report/subject_session_coverage.csv','paper11_v2/protocol/r0_amendment1.json']),
 'C02': ('Mathematical definitions and causal model classes, not PLDS/SLDS physical mechanisms', ['paper11_v2/scripts/predictive_models.py','paper11_v2/scripts/predictive_models_code1.py','paper11_v2/scripts/r2_models.py']),
 'C03': ('Frozen bins, context, train-only transformations, optimizer and causal scoring', ['paper11_v2/scripts/r2_data.py','paper11_v2/scripts/predictive_models.py','paper11_v2/protocol/protocol.json']),
 'C04': ('Recorded220/108controlled cases,54causal checks, score/gradient verification', ['paper11_v2/results/R1_code1/QC.json','paper11_v2/results/R2/numerical_oracle.json']),
 'C05': ('All57configs,3887fits,complexity,threebaseline roles/oneSE/maxima/diagnostics', [REPORT+'all57configurations.csv',REPORT+'optimizer_diagnostics.csv','paper11_v2/results/R2/model_selection_manifest.json','paper11_v2/results/R2/baseline_selection.json']),
 'C06': ('Six saved contrasts,9patient effects, exploratory bootstrap/signflip/Holm', ['paper11_v2/results/R2/subject_statistics.json','paper11_v2/scripts/r2_statistics.py',REPORT+'patient_conditional_CIs.csv',REPORT+'session_conditional_CIs.csv']),
 'C07': ('Incomplete200x3nulls,8complete replicas2896savedfits,externalR2FAIL', ['paper11_v2/results/R2/QC.json','paper11_v2/results/R2/gate_result.json','paper11_v2/protocol/protocol.json']),
 'C08': ('Externaladmission/audit failures remain;R3notexecuted;noholdoutunlock', ['paper11_v2/results/R2/gate_result.json','paper11_v2/boundary_audit1/AUDIT_REPORT.md','paper11_v2/alt_cohort_audit1/FEASIBILITY_REPORT.md','paper11_v2/results/R0_schema1/final_validation_lock.json']),
 'C09': ('OriginalM4/NUM1/NUM2/NUM3failures;notphysicalregime/NAP/CWPvalidation', ['paper11/results/M4/gate_result.json','paper11/results/M4_amendment1/gate_result.json','paper11/results/M4_amendment2/gate_result.json','paper11/results/M4_amendment3/gate_result.json','paper11/results/M4_amendment3/NUMERICAL_LIMITATIONS.md','paper11_v2/protocol/protocol.json']),
 'C10': ('Primarysourceethics/license,clinical sampling,SUA/MUA/sessionlocalcaveats', ['paper11/data_manifest/metadata/nm_readme.md','paper11/data_manifest/metadata/nm_description.json']),
 'C11': ('Manuscriptcloseoutauthorization only;unknownadministrativedeclarations,scientificvalidationfalse', [])
}


def render_equations(markdown, output):
    import re
    folder = output / 'equations'; folder.mkdir(exist_ok=True)
    for i, expression in enumerate(re.findall(r'\$\$(.*?)\$\$', markdown, re.S)):
        fig = plt.figure(figsize=(7.2,.55))
        fig.text(.03,.5,'$'+expression.strip()+'$',fontsize=13,ha='left',va='center')
        fig.savefig(folder/f'eq{i+1}.png',dpi=250,bbox_inches='tight',pad_inches=.08,facecolor='white')
        plt.close(fig)


def ci_label(value):
    low, high = json.loads(value)
    return f'[{low:.6f}, {high:.6f}]'


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', default=str(HERE/'output'))
    output = Path(parser.parse_args().output).resolve()
    if HERE not in output.parents: raise ValueError('Output outside closeout track')
    saved = Saved(); values = export_tables(saved,output/'tables')
    grid, stats, coverage, gate, patients, selected, raw, effects, optimizer = values
    headers=['Patient','Sessions','Session-local units','Train trials','Development trials']
    coverage_rows=[]
    for patient in patients:
        rows=[r for r in coverage if r['subject']==patient]
        coverage_rows.append([patient,len(rows)]+[sum(int(r[k]) for r in rows) for k in ['units','train_trials','validation_trials']])
    selected_table=table(['Model / role','Configuration','Mean score','Mean nominal parameters'],[
        [r['family']+(' (strongest reference)' if r['family']=='baseline' else ' (one-SE)'),config_label(r['config']),f"{r['mean']:.9f}",f"{r['total_parameters']:.3f}"] for r in selected])
    max_table=table(['Family','Raw maximum configuration','Development score','Mean nominal parameters'],[
        [family,config_label(row),f"{float(row['patient_weighted_dev_mean']):.9f}",f"{float(row['total_nominal_parameters']):.3f}"] for family,row in raw.items()])
    paired_table=table(['Patient','D-C','D-H','C-H','D-B','C-B','H-B'],[
        [p]+[f"{c['patient_differences'][p]:+.6f}" for c in stats['comparisons']] for p in patients])
    contrast_table=table(['Contrast','Mean effect','95% exploratory CI','Raw sign-flip p','Holm-six p','Patients'],[
        [c['left']+' minus '+c['right'],f"{c['mean']:+.6f}",f"[{c['ci'][0]:+.6f}, {c['ci'][1]:+.6f}]",
         f"{c['sign_flip']['p_value']:.8f}",f"{c['holm_p_value']:.8f}",9] for c in stats['comparisons']])
    refs='\n\n'.join(f'{i}. {text} [{url}]({url})' for i,(text,url,source) in enumerate(REFERENCES,1))
    text=(HERE/'manuscript.template.md').read_text(encoding='utf-8')
    replacements={'PATIENT_COVERAGE_TABLE':table(headers,coverage_rows),'SELECTED_TABLE':selected_table,
                  'RAW_MAX_TABLE':max_table,'PATIENT_EFFECTS_TABLE':paired_table,'CONTRASTS_TABLE':contrast_table,
                  'REFERENCES':refs,'ONE_ITERATION_COUNT':str(optimizer['one_iteration_records']),
                  'FTOL_COUNT':str(sum(n for message,n in optimizer['termination_messages'].items() if 'RELATIVE REDUCTION' in message))}
    for key,value in replacements.items(): text=text.replace('{{'+key+'}}',value)
    assert '{{' not in text
    (output/'manuscript.md').write_text(text,encoding='utf-8')
    render_equations(text,output)
    write_json(output/'references.json',[{'number':i,'reference':r[0],'url':r[1],'existing_verification_source':r[2],
          'source_sha256':saved.record['input_sha256'][r[2]],'new_metadata_search':False} for i,r in enumerate(REFERENCES,1)])
    supplementary=['# Supplementary Methods and Results',
       'This supplement belongs to P11-MANUSCRIPT-CLOSEOUT-1, not original R3. All results are copied from exposed development evidence; independent validation was not executed.',
       '## S1. Full Configuration Grid',
       'All 57 configurations are retained below. F = family, K/d = number of states/dimension, L = extra history lags, P = patient-weighted mean nominal coefficients INCLUDING shared offsets. Scores are development nats/unit-bin. Baseline names identify their distinct covariate sets. Full precision and training-objective seed policy remain in all57configurations.csv.',
       table(['Family','Ridge','K/d','L','P total','Development score'],[[r['family'],r['ridge'],r['size'] or '-',r['lags'] or '-',f"{float(r['total_nominal_parameters']):.3f}",f"{float(r['patient_weighted_dev_mean']):.9f}"] for r in grid]),
       '## S2. Complete Patient Scores',
       'The four columns reproduce the original selected/reference means. Baseline is combined ridge0.001, not the stationary one-SEbaseline. No model selection is repeated.',
       table(['Patient','Baseline','Discrete','Continuous','Hybrid'],[[p]+[f"{stats['means'][f]['patient_means'][p]:.9f}" for f in ['baseline','discrete','continuous','hybrid']] for p in patients]),
       '## S3. Full Patient Paired Effects',paired_table,
       '## S4. Saved Population Intervals and Tests',contrast_table,
       'All six contrasts use n=9patients;10000paired patient bootstrap replicas and512exact sign flips. Holm-six was applied once to the saved contrast set. These intervals condition on the selected configurations and do not repeat selection; they are not selection-adjusted confirmatory inference.',
       '## S5. Conditional Patient Intervals',
       '36descriptive intervals resample whole trials within each retained session and average sessions equally. They condition on the patient and are not independent-population CIs. No new resampling is performed.',
       table(['Family','Patient','Mean','Saved 95% CI'],[[r['family'],r['subject'],f"{float(r['mean']):.9f}",ci_label(r['ci'])] for r in saved.csv(REPORT+'patient_conditional_CIs.csv')]),
       '## S6. Conditional Session Intervals',
       '92descriptive whole-trial intervals below;23sessions per each of four selected/reference models. Trials, sessions and neurons are not independent patients.',
       table(['Family','Session','Mean','Saved 95% CI'],[[r['family'],r['session'],f"{float(r['mean']):.9f}",ci_label(r['ci'])] for r in saved.csv(REPORT+'session_conditional_CIs.csv')]),
       '## S7. Complete Session Coverage',
       table(['Session','Units','Train','Development'],[[r['key'],r['units'],r['train_trials'],r['validation_trials']] for r in coverage]),
       '## S8. Optimizer Diagnostics and Computational Cost',
       f"All {optimizer['records']}records remain in optimizer_diagnostics.csv, including all seeds. One-iteration records:{optimizer['one_iteration_records']}; largest recorded gradient infinity norm:{optimizer['gradient_max']:.12g}. First-unit design rank is not joint rank. Convergence does not mean small gradients or global optima.",
       table(['Termination message','Recorded fits'],list(optimizer['termination_messages'].items())),
       'The recorded fit_seconds=805.5225947985891 is cumulative training timing in the original environment. It is not a new speed benchmark. Penalization, bounds[-8,8],500iterations,ftol/gtol1e-5 are mathematical parts of the compared pipelines. Nominal coefficient budgets are unequal; the frontier reports that inequality rather than asserting exact complexity matching.',
       '## S9. Numerical, Null and External Failures',
       'OriginalM4/NUM1/NUM2/NUM3 failures are immutable. NUM2 failed a controlled proposal oracle before real data. NUM3 independent quadrature consistency is empirical; registered worst-replica-plus1.96SD-and-reference-sensitivity criterion failed at131072particles. None establishes that all numerical evaluators must fail. These are controlled algorithmic observations, not hippocampal experiments.',
       'The null plan required200replicas each of3types. Eight full count-permutation cohort replicas and2896savednullfits (including partial work) were preserved. No partial-null pvalue or completed full-null claim appears. Circular/task-event suites and external final validation were not executed. DANDI5unknown-support sessions were not deleted to pass. Subsequent OSF/Figshare admission audits were inconclusive.',
       '## S10. Evidence Traceability and Scope',
       'Each of the seven figure sidecars lists source paths andSHA256 plus render-code hash. build_inputs.json and claim_map.json bind the document to frozen sources. Saved-only reproduction regenerates tables/figures/document formatting; it neither refits models nor reproduces unexecuted controls/external evaluation. Author contributions/funding/competing-interest/submission declarations remain unprovided, explicitly disclosed in the main paper.',
       '## Supplementary References',refs]
    (output/'supplement.md').write_text('\n\n'.join(supplementary)+'\n',encoding='utf-8')
    claim_map={key:{'claim':claim,'evidence':{p:saved.record['input_sha256'][p] for p in paths},
              'scope':'exploratory/preserved records, not independent scientific validation'} for key,(claim,paths) in CLAIMS.items()}
    claim_map['C11']['evidence']={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE/'protocol.json',HERE/'mission.json']}
    write_json(output/'claim_map.json',claim_map)
    attachment_text = [
      ('A1','Frozen Protocol and Scope Change','The original v2protocol/grid/splits remain unchanged. This separately authorized manuscript protocol freezes saved evidence at33dc10d and never calls itself originalR3. Selection rules, priors, score definition and original unsuccessful gates are preserved. No new hypothesis-confirming experiment or final evaluation is registered.', ['paper11_v2/protocol/protocol.json','paper11_v2/protocol/r0_amendment1.json']),
      ('A2','Dataset Manifest','NEMARnm000363v1.0.0/pinnedb054fbef, companionds004752v1.0.1/pinned234fd4c0 is same-patient iEEG, not independent.9patients23sessions592session-local units;622train201development trials.23session coverage CSV has underlying feature/event hashes, copied without raw array access.Clinical sampling/SUA-MUA/source sorting limitations remain.', ['paper11_v2/results/R2_report/subject_session_coverage.csv','paper11/data_manifest/metadata/nm_description.json']),
      ('A3','Full Pipeline and Model Definitions','Historical path:source QC/anatomy -> training-only eligibility/count bins[-6,0) -> causal context/history -> train-fit candidates -> training-objective seed resolution -> frozen development one-SE selection -> saved statistics. Closeout path:read saved summary allowlist -> consistency checks -> tables/figures -> manuscript/PDF -> saved-only replay. No original pipeline is rerun. Model formulae in Section4reflect exact saved implementations.', ['paper11_v2/scripts/predictive_models.py','paper11_v2/scripts/predictive_models_code1.py','paper11_v2/scripts/r2_models.py','paper11_v2/scripts/r2_data.py']),
      ('A4','All Baselines and Model Configurations','21baseline+8discrete+12continuous+16hybrid configurations. Full57CSV and3887diagnostic records retained. Distinguish strongestcombined.001 comparator, stationaryone-SEbaseline, combined.01 shared offset, threefamilyone-SEselections and rawscoremaxima. No candidate, seed or poorly performing high-ridge result suppressed.', [REPORT+'all57configurations.csv','paper11_v2/results/R2/baseline_selection.json','paper11_v2/results/R2/model_selection_manifest.json']),
      ('A5','Holdout Audit','No oldtest, external spikes, physiological unit QC or final scores accessed. Frozen DANDI60/40lock SHA27fad80c753cfdef00977d056b379da5210f1e0247efba803a4e098e593e93e3 unchanged. R2FAIL/DATA_INSUFFICIENT andR3NOT_EXECUTED remain. The closeout reads lock metadata only; no new final split, cohort substitution or evaluation.', ['paper11_v2/results/R2/gate_result.json','paper11_v2/results/R0_schema1/final_validation_lock.json']),
      ('A6','Statistics','One equal-weight paired difference per nine independent patients, equal sessions within patient. Saved10000patientbootstraps/seed20261011,512sign-flips andHolm-six copied verbatim.36patient/92session whole-trial CIs descriptive. CIs condition on selected configurations, not selection-adjusted. No new statistics, resampling, hypotheses or effective subject denominator.', ['paper11_v2/results/R2/subject_statistics.json',REPORT+'patient_conditional_CIs.csv',REPORT+'session_conditional_CIs.csv']),
      ('A7','Incomplete Null and Falsification Record','Registered200replicas each for count-preserving bin permutation,circular shifts andevent/task timing. Only8full countcohortreplicas complete;2896savedfitrecords includepartialwork. No complete null suite or nullcalibratedpvalue. Strong event/drift/history baselines do not replace missing falsification. Independent final validation unexecuted.', ['paper11_v2/results/R2/QC.json','paper11_v2/protocol/protocol.json']),
      ('A8','QC and Leakage Audit','Existing QC tested anatomical eligibility, train-onlyunitselection/transforms, frozen trial split identity, causal known-context features, state/history resets and future-perturbation checks. Development was previously exposed; later freezes do not erase that. Clinical/source sorting and missing per-unit dropout masks remain. Allcloseoutinputsallowlisted summaries/code/documents; raw spikes/count arrays and data acquisition absent.', ['paper11_v2/results/R1_code1/QC.json','paper11_v2/results/R2/QC.json','paper11_v2/scripts/r2_data.py']),
      ('A9','Limitations and Failed Analyses','PreserveoriginalM4/NUM1/NUM2/NUM3integration/proposal failures. Tractable v2models change representation and cannot retrospectivelyvalidatePLDS/SLDS. Optimizerftol/bounds/one-iteration behavior notglobaloptima. Rankingselection-sensitive,smalln9,sourceSUA/MUAambiguous. Nulls incomplete,DANDIfailed,OSF/Figshareinconclusive. No physical regime/NAP/CWPvalidation.', ['paper11/results/M4_amendment3/NUMERICAL_LIMITATIONS.md','paper11_v2/results/R2/gate_result.json','paper11_v2/boundary_audit1/AUDIT_REPORT.md','paper11_v2/alt_cohort_audit1/FEASIBILITY_REPORT.md']),
      ('A10','One-command Saved-results Reproduction','Run reproduce.ps1 from this closeout directory. It verifies frozen source hashes, regenerates tables/seven figures/documents offline into a separate reproduction folder, validates full57/n9/claimboundaries and emits a reproducibility receipt. It does NOT obtain data/refit/bootstrap/null-test/unlock anything. Primary rendering uses Matplotlib; paginated PDFs use bundledReportLab. Exact runtimes/options are inREPRODUCTION.md.', [])]
    attachments=output/'attachments';attachments.mkdir(exist_ok=True)
    for number,title,body,inputs in attachment_text:
        evidence=table(['Frozen source','SHA256'],[[p,saved.record['input_sha256'][p]] for p in inputs]) if inputs else 'Scope and command are bound by closeout protocol/source manifests.'
        (attachments/(number+'.md')).write_text('# '+number+' '+title+'\n\n'+body+'\n\n'+evidence+'\n',encoding='utf-8')
    (output/'LIMITATIONS.md').write_text('# Final Limitations Report\n\nOriginalv1numerical gates failed;v2R2FAIL/DATA_INSUFFICIENT;originalR3NOTEXECUTED. No external scientific validation. Developmentdataexposed, n9patients. Fullnulls incomplete. Selectinglowcomplexityone-SEmodels and reportingrawmaxima answersdifferentquestions. Commonoffsetridge.01 differsstrongestbaseline.001. Tractablecontinuityisdeterministicrecurrence,notPLDS. Nominalcomplexitynotrank;optimizerconvergencenotglobaloptima. ClinicalSUA/MUA/sourcecuration/dropoutlimitationspersist. Authors/funding/competinginterestsunprovided;submissionreadinessrequiresapproval. MANUSCRIPT_COMPLETE nevermeans SCIENTIFIC_VALIDATION_PASS. No newscience/search/rescue authorized.\n',encoding='utf-8')
    print('Complete scholarly text, supplement, references, claim map and A1-A10 generated.')


if __name__ == '__main__':
    main()
