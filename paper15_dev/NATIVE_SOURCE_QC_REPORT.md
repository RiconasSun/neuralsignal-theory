# Native-source and A-only physiological QC report

M2_SOURCE_QC_PASS=true:10 Development mice from8 laboratories, each with8 A-qualified selected units. Original20 identities remain12Development/8Final. Neither excluded Development mouse was replaced. Native sorting2024-05-06/task2025-03-03; exact object UUID/key/ETag/size/time and selected probe/source identities are in SOURCE_FILE_FREEZE.json and source inventories.

The preserved results/NATIVE_COHORT_SOURCE_REPORT.csv is the original pre-physiology metadata snapshot: its NOT_RUN cells are historical, not current admission. This report and the physiological gate are current. The final integrated tables/COHORT_FINAL_NATIVE_QC.csv is produced with the completed Development report.

|Subject|Lab|Allocation|Native good MOp metadata|Valid role epochs|A-qualified units|Actual A admission / boundary|
|---|---|---|---:|---|---:|---|
|NYU-37|angelakilab|DEVELOPMENT|54|{'A': 83, 'B': 31, 'E': 41}|NOT_RUN_EXCLUDED_METADATA|False / REGISTERED_METADATA_TRIAL_OR_UNIT_COVERAGE|
|CSHL059|churchlandlab|DEVELOPMENT|57|{'A': 0, 'B': 0, 'E': 0}|NOT_RUN_EXCLUDED_METADATA|False / REGISTERED_METADATA_TRIAL_OR_UNIT_COVERAGE|
|UCLA037|churchlandlab_ucla|FINAL_RESERVED|214|{'C': 222, 'D': 171}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|KS046|cortexlab|DEVELOPMENT|42|{'A': 346, 'B': 116, 'E': 119}|35|True|
|DY_014|danlab|FINAL_RESERVED|57|{'C': 335, 'D': 218}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|PL033|hausserlab|DEVELOPMENT|21|{'A': 366, 'B': 121, 'E': 114}|16|True|
|SWC_043|hoferlab|DEVELOPMENT|18|{'A': 303, 'B': 102, 'E': 99}|9|True|
|ZFM-01576|mainenlab|FINAL_RESERVED|47|{'C': 601, 'D': 402}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|SWC_038|mrsicflogellab|DEVELOPMENT|38|{'A': 481, 'B': 156, 'E': 160}|27|True|
|NR_0027|steinmetzlab|FINAL_RESERVED|21|{'C': 484, 'D': 191}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|CSH_ZAD_026|zadorlab|DEVELOPMENT|84|{'A': 505, 'B': 151, 'E': 162}|56|True|
|NYU-30|angelakilab|DEVELOPMENT|22|{'A': 398, 'B': 135, 'E': 125}|18|True|
|UCLA033|churchlandlab_ucla|FINAL_RESERVED|21|{'C': 263, 'D': 154}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|KS051|cortexlab|DEVELOPMENT|44|{'A': 218, 'B': 71, 'E': 76}|26|True|
|DY_011|danlab|FINAL_RESERVED|25|{'C': 227, 'D': 154}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|ZFM-01937|mainenlab|DEVELOPMENT|20|{'A': 260, 'B': 85, 'E': 87}|12|True|
|CSH_ZAD_019|zadorlab|DEVELOPMENT|91|{'A': 363, 'B': 120, 'E': 115}|62|True|
|NYU-21|angelakilab|FINAL_RESERVED|51|{'C': 382, 'D': 246}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|
|UCLA035|churchlandlab_ucla|DEVELOPMENT|66|{'A': 547, 'B': 168, 'E': 172}|53|True|
|ZFM-01936|mainenlab|FINAL_RESERVED|86|{'C': 336, 'D': 224}|NOT_AUTHORIZED_FINAL|FINAL_METADATA_ONLY_C_PHYSIOLOGY_AND_WHEEL_PENDING|

Audit denominator:446 provider-good native-MOp candidate unit records on the10 actual A-read mice;314 A-qualified units;80 selected units. Independent M2 review recomputed every candidate metric and exact ranking/selected UUID. No other-probe or cross-session/mouse pooling.

NYU-37 has31 B epochs, below the frozen40. CSHL059 supplied wellformed identity sync[[0,0],[1,1]], yielding source-supported domain[0,1] and zero valid epochs under no extrapolation. This is registered per-mouse coverage exclusion, not a repaired clock or transfer of the old aggregate mask. Both preserve all native discrepancies and original candidate allocation.

QC uses A-only observed epoch exposure, rates/spike counts, within-epoch refractory pairs and original A-quarter coverage. Source-support gaps are excluded before binning and never converted into zero firing. Ranking is refractory fraction, descending A rate, unit UUID. B/E physiology, unit selection and scaling are forbidden. Actual native-versus-aggregate atlas/label differences are retained in METADATA_QC and metadata states.

Known saturation is applied only in its own selected-probe AP sample clock. Eleven additional annotations from other probes are retained and explicitly excluded rather than transferred. Unannotated artifact burden is unknown. Provider-good curated-release units are a sampling frame, not a lossless recording-quality certificate.

All20 native identity/task/anatomy/AP/sync/saturation metadata contracts were examined. The8 Final mice have structural task/anatomy potential only. Final wheel sample coverage, all Final neural observations, C physiology/coefficients and D outcomes were not decoded/computed. Metadata masks provisionally show support; they do not certify unexamined actual Final wheel values.

Protected boundary: full-record Development decoder may temporarily inspect timestamps for role classification but exports only the currently authorized role; unpartitionable nonfinite timestamps fail closed. M2 exports A only. Later B/E exports require their separate stage gates. Final neural files are never downloaded/decoded by this worker.

Independent review evidence: INDEPENDENT_PRE_NEURAL_REVIEW_1/2.md, INDEPENDENT_M2_ADMISSION_REVIEW.md, metadata/body ETag audits, exact A QC/source journals and source regression tests. Initial source/reader failures and partial files remain preserved; no historical scientific failure is reclassified.
