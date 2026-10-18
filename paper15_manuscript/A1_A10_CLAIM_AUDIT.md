# A1-A10 scientific evidence and claim audit

Mission: P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE. Scientific base: `bdec0e19621cc8018abe11c5633ce76aff611443`. This is an internal evidence audit, not evidence that the original confirmation criteria passed. Every original file listed below is hash-bound by SOURCE_HASHES.json. Publication tables retain source mappings in tables/SAVED_TABLE_SOURCE_MAP.json; original CSVs are copied without changing their bytes. All references are actual primary publications or official source/licence documentation.

|Attachment|Actual evidence|Manuscript and publication artifacts|Audit conclusion and limit|
|---|---|---|---|
|A1 Research question and protocol|paper15_m1/SCIENTIFIC_PROTOCOL.md; FEATURE_MODELS.md; STATISTICS_CONTROLS.md; PROTOCOL_FREEZE.json|Main1,2.4-2.9;SuppS3,S5-S7,S12;Figures1,3|Frozen predictive estimands and exact conjunctions retained. No new hypothesis or post-D tuning. Method Paper; no mechanism discovery.|
|A2 Source/licence/cohort|paper15_m0/SOURCE_REGISTRY.md,INPUT_PINS.json;paper15_m1/COHORT.csv;paper15_r1/tables/COHORT_FINAL_NATIVE_QC.csv;paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv|Main2.1-2.2,DataAvailability;SuppS1;Figure1;SOURCE_COHORT_IDENTITIES.csv;references/ATTRIBUTION.md|Native AWS/ONE identity and exact revisions retained; CC BY4.0 official registry verified. Global139 is not analyzed cohort.20original,10Dev+6Final admitted;four exclusions preserved.|
|A3 Source/recording/physiology|paper15_m1/SOURCE_QC.md;paper15_r1/metadata/*_task.json;paper15_final1/results/*_C_QC.json;FINAL_SOURCE_HEADER_FREEZE.json|Main2.3,3.1,4.4;SuppS2-S4;FINAL_SELECTED_UNIT_QC.csv;Figure7|Training/calibration-only physiology and upstream whole-session curation distinguished. Unknown artifacts,sorting,depth/anatomy limitations explicit; no lossless/artifact-free guarantee.|
|A4 Exact models/baselines|paper15_m1/FEATURE_MODELS.md,NUMERICAL_SELECTION.md,NUMERICAL_POLICY.json;paper15_r1/SELECTION_FREEZE.json|Main2.4-2.6;SuppS5-S8;DEVELOPMENT_B_SELECTION.csv;FINAL_NUMERICAL_CERTIFICATES.csv|All B0-B4/D/C/S equations,counts,bounds,seeds,ensemble and selected policies retained. C is fixed finite history; D/S masses ensembled. No capacity equivalence claim.|
|A5 Development/Final separation|paper15_r1/SELECTION_FREEZE.json;paper15_final1/states/*_C_PREPROCESSING.json;FINAL_C_STATE_SEAL.json;PRE_D_CANDIDATE.json;PRE_D_GATE.json|Main2.2,2.6-2.7;SuppS3,S14;Figure1|B selects;E exploratory;C calibration;D single report. Authorized low-level whole-record decoding distinguished from C scientific export. No independent custodian or administrator-proof claim.|
|A6 Effects/statistics|paper15_r1/results/E_STATISTICS.json;paper15_final1/results/D_STATISTICS.json;both contrast/mouse tables|Abstract;Main2.8,3.2-3.4;SuppS9,S13;Figures2-4,7;REGISTERED_CONTRAST_ORDER.csv|All12 cohort/contrast summaries retained;whole-mouse10kCI and original tests reproduced from saved effects only. Final DESCRIPTIVE ONLY;cohort,width and assumptions not met. Secondary Holm5 all nonsignificant;no equivalence.|
|A7 Sensitivities/references/failures|paper15_r1/results/E_SENSITIVITY_SUMMARY.json,E_CONTROL_SUMMARY.json;paper15_final1/results/D_SENSITIVITY_SUMMARY.json,D_CONTROL_SUMMARY.json;both per-mouse control folders|Main2.9,3.5;SuppS10-S12;Figures5-6;REFERENCE_MOUSE_COVERAGE.csv;all copied panels|All11 cases and4suites retained. Baseline-only fits never attributed toD/C/S. N3wheelLLdiagnostic;N4unavailableDev5/Final3;DevN1 andFinalD/D-S gate failures explicit.|
|A8 One-shot integrity|paper15_final1/D_BATCH_CLAIM.json;ONE_SHOT_D_SPECIFICATION.json;PRE_D_GATE.json;oldE/REAL_D_EXECUTION_RECEIPT.json and pre-D reviews|Main2.7;SuppS14;SOURCE_HASHES.json|One completed assessment,all registered transformations part of same batch. Manuscript code denies old worker imports,array loading and network. D rerun count0. Saved reproduction is not a second evaluation.|
|A9 Negatives/limits/prohibited claims|paper15_r1/DEVELOPMENT_REPORT.md;paper15_final1/FINAL_SCIENTIFIC_REPORT.md;D_SCIENTIFIC_VERDICTS.json;paper15_dev/STOP_REPORT.md|Abstract;Main3.2-3.5,Discussion,Limitations,Conclusion;SuppS4,S12-S15;AUTHOR_SCIENTIFIC_REVIEW.md|No confirmation,causal connectivity,all-movement independence,persistent biological state,model superiority,independent-lab/human/BCI/CWP/NAP claim. Earlier timestamp failure and unused fits remain visible.|
|A10 Reproducible archive|newreproduce.ps1,build.py,source.py,production.py,render.py,qa.py;requirements.txt;ENVIRONMENT.json;SOURCE_HASHES.json;SAVED_REPRODUCTION.json|MainCodeAvailability;SuppS16;REPRODUCIBILITY.md;all7figuretriplets,main/suppPDFs,sourceMD,tables,bibliography|Saved-result arithmetic/document rebuild only;no raw-data re-fit. Actual native command,visual inspection,independent review and Git/readback/clean have separate evidence gates. No external submission authorized.|

Source alias `oldE` denotes `ops/evidence/2026-10-18/p15-m6-independent-final-validation/`; all referenced receipts are included in the preserved source inventory.

## Load-bearing claim ledger

Each row is an allowed statement, not a new scientific criterion. Exact numerical values are in the linked source-key/table view; typographic rounding in figures does not replace the saved values.

|Claim ID|Claim being checked|Direct archived evidence|Location and limitation|
|---|---|---|---|
|C01|Global source139mice/459sessions/699insertions|M0SOURCE_REGISTRY;officialIBLrelease documentation|Main2.1;SuppS1;not eligible MOp denominator|
|C02|20original mice,12Dev/8Final|M1COHORT.csv byte-bound to M0allocation|Main2.2;Figure1;SuppS1cards|
|C03|Dev10mice/8labs;NYU-37 andCSHL059 excluded|R1COHORT_FINAL_NATIVE_QC.csv,DEVELOPMENT_REPORT|Main2.2,3.1;SuppS1;no replacement|
|C04|Final6mice/4labs;NYU-21 strict-order andUCLA033six-unit exclusions|FinalFINAL_SOURCE_AND_C_QC.csv;M6report|Abstract;Main2.2;Figure1;SuppS1/S2|
|C05|Eight selected release units per admitted mouse|C_QC results and source maps;R1QCtable|Main2.3,3.1;SuppS2;not complete cell population|
|C06|Final1360scored epochs/108800unit-bins|FinalINDIVIDUAL_MOUSE_EFFECTS primary denominators|Main3.1;SuppS9;equal-mouse weighting retained|
|C07|Devprimary0.1125291851306621,CI[0.06745810552609997,0.16368155129436163],p0.0009765625|R1E_STATISTICS B4-B1 andmouseeffects|Abstract;Main3.2;Figure2;SuppS9;exploratory|
|C08|Finalprimary0.08658239652342035,CI[0.04944033234175033,0.14110164811873427],p0.015625|FinalD_STATISTICS B4-B1 andmouseeffects|Abstract;Main3.2/Table1;Figure2;SuppS9;DESCRIPTIVE ONLY|
|C09|All6Finalprimaryeffectspositive;range0.0350064985-0.2151141990|FinalD_STATISTICS B4-B1.mouse_effects|Main3.2,3.6;Figure2;no new selection|
|C10|Finalprimarywidth0.09166131577698394>0.01and6<8|D_STATISTICS.CI_width;M1STATISTICS_CONTROLS|Abstract;Main3.2,Limitations;no criterion relaxation|
|C11|OwnB4-B3Final0.05208972400526927,p0.03125,Holm0.15625|D_STATISTICS B4-B3;FinalCONTRASTS|Main3.3/Table1;Figure3;conditional predictive ablation|
|C12|OtherB4-B2Final0.006353386392021677,p0.53125,Holm1|D_STATISTICS B4-B2;FinalCONTRASTS|Main3.3/Table1;no causal influence claim|
|C13|D-B4Final0.00235862122254638,p0.53125,Holm1|D_STATISTICS D-B4|Main3.4/Table1;no superiority|
|C14|C-B4Final0.00013410738971923112,p0.28125,Holm1|D_STATISTICS C-B4|Main3.4/Table1;no superiority|
|C15|D-SFinal0.0016697806796088692,p0.5625,Holm1|D_STATISTICS D-S|Main3.4/Table1;no persistent-state claim|
|C16|All five secondary CIs and raw/Holm values preserved in original order|Both cohort statistics andcontrastCSVs|Figure3;SuppS9;REGISTERED_CONTRAST_ORDER.csv;not equivalence|
|C17|n6sign grid64,minone-sided.015625,two-sided.03125,Holm5minimum.15625|M1test definition;pre-Dstatresolutionreceipt|Main2.8;SuppS9;resolution,not empirical power|
|C18|DevelopmentD-B4negative,Finaldescriptivepositive|R1E_STATISTICS andFinalD_STATISTICS D-B4|Main3.4,Discussion;no pooled/new difference test|
|C19|DevN1primary7/10failed8/10;N2=10/10|R1E_CONTROL_SUMMARY B4-B1|Main3.5;Figure5;SuppS11-S12|
|C20|FinalN1/N2primary6/6positive gates;Holm4.004each|FinalD_CONTROL_SUMMARY B4-B1|Main3.5;Figure5;doesnotclearconfirmation|
|C21|N4aggregateunavailableDev5/Final3|BothCONTROL_SUMMARY N4 andoriginalcoverage|Main3.5;Figure5;SuppS11;fixedp1slot|
|C22|D-B4N2failed;D-SN1/N2failed|FinalD_CONTROL_SUMMARY namedcontrasts|Main3.5;Figure5;SuppS12;no smallp rescue|
|C23|N3isB4wheelLLrelianceonly|M1STATISTICS_CONTROLS andboth summaries.statistic|Main2.9,3.5;Figure5;not allmovement/D/Cwheelnull|
|C24|All11sensitivitiesbaseline-only;FinalS03n4,S02n6|M1plan;FinalD_SENSITIVITY_SUMMARY andcaseplans|Main3.1,3.5;Figure6;SuppS10;noD/C/Scredit|
|C25|Mandatory9Finalcasespositive/min6forprimary/own/other|FinalD_SENSITIVITY_SUMMARY 27mandatoryrows|Main3.5;SuppS10;doesnotrepaircohort/precision|
|C26|S04uses100ms;othercases50ms|M1sensitivitydefinition andsavedcaseidentity|Figure6;SuppS10;per-bin scales not interchangeable|
|C27|Final72main+320sensitivityfitsallnumericPASS,noretry|FinalMAIN_ATTEMPTS,SENSITIVITY_ATTEMPTS and392certificates|Main2.6,3.1;SuppS8;engineeringnot scientificconfirmation|
|C28|Historical359+corrective1135+Final392=1886|R1ledger;Finaldelivery;oldfailureevidence|Main2.3,2.6;SuppS4;separateauthorizationsdisclosed|
|C29|B0-B4counts8/304/336/528/560;D3=584,C1=568,S4=587|M1FEATURE_MODELS;Bselectionnominalcounts;fitfreecounts|Main2.4-2.6;SuppS6;activecountsseparate|
|C30|Objective/T versus effect/(T*U)|M1FEATURE_MODELS;modelsource;DSTATSmouseexposures|Main2.4,2.6,2.8;SuppS6-S9;no normalization change|
|C31|CfixedDCTfinitehistory;D/Sensemblejointmasses|M1FEATURE_MODELS;R1SELECTION_FREEZE|Main2.5;SuppS6;not learnedrecurrentdynamics|
|C32|Finalheterogeneityandlabdiagnosticssaved|D_STATISTICS anddistribution/lab CSV|Main3.6;Figure7;SuppS13;no independent-labreplication|
|C33|Nativeanatomy/contactproxy;depthunavailable|BothANATOMY_LAYER_PROXY CSVs|Main3.6,4.4;Figure7;SuppS2/S13;no histologicaldistance|
|C34|Exact-native correctionfollowedsource failure|paper15_devSTOP_REPORT;R1DEVELOPMENT_REPORT andsourceaudit|Main2.3;SuppS4;oldfitsneverreused/relabeled|
|C35|ExactlyoneDassessmentandno manuscriptDreassessment|D_BATCH_CLAIM;pre-Dgate;sourcehashes;blockedimport/array/networkproduction|Main2.7;SuppS14;newreproreceipts;no rawfitreproclaim|
|C36|Unmeasuredmovement/artifacts/sorting/samplingremainlimitations|M0OBSERVATION_LIMITATIONS;M1SOURCE_QC;bothreports|MainDiscussion/Limitations;no causal/allmovement/biologicalstateclaim|

## Human review boundary

The internal audit checks support and consistency, not publication suitability, ethical approval or author consent. External submission requires the real authors to verify attribution, authorship/affiliations/ORCIDs if supplied, funding/conflicts, ethics/data-use obligations, statistical interpretation and journal requirements. No acceptance, independent peer review or endorsement is claimed. A question requiring new experiments remains a limitation/future study; it does not reopen D.
