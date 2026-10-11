# Controlled R0 Cohort Admission

Authorized minimum32usable trials/session, training>=24, development>=8,
>=5simultaneous hippocampal units and >=20training spikes/unit. The original
>=40trial failure remains immutable. Patient, not trial/unit, is independent.

| Patient | Eligible Sessions | Simultaneous Units Per Session | Training Trials | Development Trials |
| --- | --- | --- | --- | --- |
| sub-01 | 2 | 25,18 | 56 | 18 |
| sub-02 | 4 | 17,23,19,7 | 105 | 34 |
| sub-03 | 3 | 15,16,16 | 80 | 26 |
| sub-04 | 2 | 38,37 | 56 | 18 |
| sub-05 | 1 | 6 | 25 | 8 |
| sub-06 | 3 | 31,34,35 | 87 | 28 |
| sub-07 | 2 | 19,6 | 53 | 17 |
| sub-08 | 4 | 34,40,51,65 | 108 | 35 |
| sub-09 | 2 | 20,20 | 52 | 17 |
| Total | 23 | 592session-local units, not unique neurons | 622 | 201 |

Session identities, detailed denominators and raw-source hashes are in
results/R0_amendment1_code1/subject_table.csv and session_table.csv.
All counts are from permitted real primary training/development arrays only.
Training273847and development88480spikes refer to the frozen[-6,0)epoch.
No other MTL regions are pooled under hippocampus. Companion-unpaired
sub-08/ses-05 remains explicitly identified; primary source unit/trial alignment
was verified rather than inventing a paired iEEG recording.

## Sample-Size Sensitivity

| Usable Trial Minimum | Minimum Simultaneous Units | Patients | Sessions |
| --- | --- | --- | --- |
| 32 | 5 | 9 | 23 |
| 32 | 10 | 8 | 20 |
| 32 | 20 | 6 | 13 |
| 36 | 5 | 8 | 15 |
| 36 | 10 | 7 | 13 |
| 36 | 20 | 5 | 10 |
| 40 | 5 | 2 | 2 |
| 40 | 10 | 2 | 2 |
| 40 | 20 | 1 | 1 |

These are coverage sensitivities, not effect/power estimates. Leaving out one
patient leaves8; sessions and units never increase the patient denominator.
With n=6/7/8/9, theoretical minimum two-sided sign-flip p is
0.03125/0.015625/0.0078125/0.00390625; these are not observed p-values and do
not establish power, exchangeability or significance after multiplicity.

## Limits

21training-order exclusions and4low-training-count exclusions were preserved;
no sorting or score-informed re-admission. Nonmonotonic storage does not prove
physiologically invalid neurons. Published sorting used whole-session upstream
data; new train-only QC cannot undo that retrospective preprocessing. SU/MU
identity is unresolved, neuron identity across sessions is not assumed.
Explicit observation arrays support trial coverage under the published trial
convention, not a separately measured per-bin acquisition dropout mask.

R0 PASS means protocol/cohort admission under these disclosed boundaries.
It is not evidence for a discrete, continuous or hybrid regime, NAP or CWP.
Old primary test and frozen external60/40 final split remain locked.
