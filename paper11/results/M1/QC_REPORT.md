# P11 M1 Real Data Eligibility Audit

Gate: PASS for acquisition/anatomy/alignment/QC coverage only. Scientific regime
verdict: NOT_EVALUATED. M2-M7 were not executed. No NAP/CWP validation.

## Observed Coverage

Pinned sources: nm000363 v1.0.0 at b054fbef57f9c4fb93477ecc5c88c6114dbc5662;
ds004752 v1.0.1 at 234fd4c04dea66ab9b0fd5ddbf4ec51f56b6ad02.
221 real files / 39,259,790 bytes acquired. Every downloaded file equals its
pinned repository Git blob and has a local SHA256 acquisition receipt.

| Quantity | Observed |
| --- | ---: |
| Subjects audited / meeting coverage | 9 / 9 |
| Sessions audited / eligible populations | 37 / 23 |
| Sorted session-local units audited | 1526 |
| Explicit hippocampal labels | 676 |
| Unit-QC passing hippocampal units, including small populations | 630 |
| Primary-analysis eligible units in eligible sessions | 613 |
| Companion-paired sessions | 36 |
| Unpaired sessions | 1 |

Anatomical source labels additionally identify 401 amygdala, 421 parahippocampal
gyrus and 28 fusiform gyrus units. These are never pooled with the hippocampal
primary. Parahippocampal atlas labels are preserved rather than silently relabeled
as entorhinal cortex from the dataset's broad description.

All nine subjects have at least one session with >=40 metadata-valid trials and
>=5 hippocampal sorted units satisfying the frozen unit QC. Subject-05 has only
one eligible session with six units; the cohort gate does not establish that
each subject supports cross-session reproducibility or strong model fitting.
Unit counts are session-local observations, not 613 distinct persistent neurons.
The 17 additional QC-passing units lie in sessions below the population threshold.
They are retained in QC but excluded from the primary analysis manifest.

## Alignment and Exclusions

All present paired trial records were checked for trial ID, set size, probe,
match, correctness, artifact and response time. Paired electrode mappings were
checked for contact ID, coordinates, anatomical region and hemisphere.
sub-08/ses-05 is explicitly unpaired; its spikes can enter primary analysis,
but it cannot enter paired spike/iEEG analysis. No iEEG signal data were pooled
or downloaded. Incorrect trials are retained when metadata-valid.

Seven source sessions have no unit files. Other sessions fail trial coverage
or the population unit threshold. Artifact flags, invalid/missing epoch/task
metadata, full-array coverage, coordinates and training-only spike counts are
reported in trial_alignment_qc.json, session_qc.csv and unit_qc.csv rather than
discarding their negative records. Session-specific exclusions remain visible.

## Frozen Holdouts and Claims

37 actual session manifests were frozen before spike timestamps were parsed.
Chronological 60/20/20 whole-trial assignment follows M0. Sessions with fewer
than forty valid trials have empty analysis partitions; their QC is still retained.
Immutable split SHA256:
d66ff7cc5dcadf3e0b7f18bfddcb50f3baa8fe59fc28b999910b3b66bd3e1eaa.

Training QC parses only explicitly hippocampal units from training trials.
Validation/test timestamps and unit fields are not decoded. Downloaded whole
files include heldout bytes; hashing those bytes verifies provenance, not a
predictive evaluation or count inspection. Source total-spike fields do not
select units. Boundary [-6,0) seconds is used for aggregate QC counts only;
100-ms count features and dynamical models remain unimplemented until later gates.

SU versus MU is not distinguished upstream, and upstream sorting was session-wide.
Epilepsy clinical sampling and sparse/small populations remain scientific limits.
DANDI anatomy/task compatibility is not tested here. No regime preference,
predictive performance or external replication follows from M1 PASS.

## Tests and Reproduction

Offline PowerShell reproduction passed 22 tests, zero skips. Tests cover real
source checksums, actual immutable splits, M0 integrity, anatomy separation,
companion mismatch refusal, session-scoped identities, frozen coverage thresholds,
population-qualified unit membership, raw Git exclusion and heldout timestamp
isolation. A CSV report-reader regression was discovered after extending the
membership check, fixed without weakening the test, and its FAIL gate retained
under attempts/01-csv-reader-regression/. No freeze or holdout was rewritten.

See ../../REPRODUCE_M1.md. Derived QC and split data follow CC-BY-SA-4.0;
DERIVED_DATA_LICENSE.txt preserves the source license. Raw bytes remain local.
