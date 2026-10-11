# Controlled R0 Actual QC

R0-TRIAL-1 registered before fresh NIX reads. Real source QC passed for9patients,
23sessions,592simultaneously recorded session-local hippocampal units summed
across sessions,622training and201development validation trials. Actual preprobe
counts:273847training spikes and88480validation spikes. No oldtest dataset values
or external spike arrays read. No physical regime/model score evaluated.

9amendment tests pass. Real PowerShell saved-output replay returned0 and checked
frozen source/failure/feature identities. Original40trial gate remainsFAIL in
results/R0_final, and original metadata/parser failures remain unchanged.
No old scripts or old negative gates rerun/rewritten by this amendment.

Fresh selection differs from v1's613units:21units fail the prospectively frozen
training timestamp monotonicity check;4additional anatomy candidates have<20
training spikes, as before. This is a conservative input-order admission rule,
not evidence that unordered spike arrays represent invalid physiological units.
All exclusions are retained per-unit; do not silently sort/re-admit or infer a
biological quality defect. Units already cleared by training retain zero-rate
validation arrays; validation activity never selects units. Common-unit bin
counts exactly match cryptographically pinned M2 features.

Simultaneous units are6-65per session. Unit identity does not transfer across
sessions. SU/MU labels are unresolved upstream. The unpaired sub-08/ses-05 remains
explicitly unpaired to companion iEEG; primary spike-relative probe clock/source
unit identities are verified, not inferred persistent neuron identity.

Trial-count sensitivity with fixed5unit minimum:32 =>9patients/23sessions;
36 =>8patients/15sessions;40 =>2patients/2sessions. Unit-minimum sensitivity at
32trials:5=>9patients,10=>8patients,20=>6patients. Leave-one-patient-out leaves8,
but this is sample coverage, not a predictive robustness/power result.
Patientwise complete table:paper11_v2/results/R0_amendment1/subject_table.csv;
session counts/units/bin denominators:session_table.csv; allcases:cohort.json.

NIX observation array presence/schema, including empty arrays, are freshly
verified for allowed units/trials under published8s epochs. This is not a
per-bin acquisition-dropout certificate. Source and metadata checksums and
trial clocks are pinned; upstream full-session sorting remains a limitation.
Old holdout IDs are used only as deny-list guards. Tests poison oldtest access.
