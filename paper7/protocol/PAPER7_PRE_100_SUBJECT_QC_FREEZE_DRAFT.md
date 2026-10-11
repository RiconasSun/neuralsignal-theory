# Paper 7 Pre-100-Subject QC Freeze Draft

Status: draft before final structural prediction.

This file records the QC decisions that must be frozen before Paper 7 may proceed from 10-subject engineering QC to any 100-subject structural prediction claim.

## Current Evidence

```text
10/10 HCP subjects completed the current FreeSurfer-5TT ACT/iFOD2/SIFT2 5k-streamline engineering QC route.
10/10 subjects generated fs_default84 84 x 84 SIFT2-weighted connectomes.
9/10 subjects cleared load-bearing tck2connectome node-assignment warnings after label conversion.
100307 remained a sparse/outlier connectome after 20k streamline-count sensitivity.
```

Evidence files:

```text
paper7/results/p7_e4_ten_subject_connectome_qc.json
paper7/results/p7_e4_ten_subject_connectome_qc_summary.json
paper7/results/p7_e5_labelconvert_connectome_qc.json
paper7/results/p7_e5_100307_streamline_20000_sensitivity.json
paper7/data_manifest/p7_e4_ten_subject_connectome_qc_summary.csv
paper7/data_manifest/p7_e5_labelconvert_connectome_qc_summary.csv
```

## Freeze Items Required Before 100-Subject Modeling

1. Final atlas:

```text
MRtrix fs_default84 label-converted FreeSurfer aparc+aseg, unless replaced before first 100-subject model run by a fully documented atlas plan.
```

2. Final streamline count:

```text
[DECISION REQUIRED BEFORE 100-SUBJECT RUN]
```

The 5k route is acceptable for engineering smoke only. It is not yet frozen as final scientific tractography density.

3. Subject exclusion rule:

```text
[DECISION REQUIRED BEFORE 100-SUBJECT RUN]
```

Candidate rule to freeze:

```text
Exclude a subject before modeling if fs_default84 tck2connectome reports load-bearing node-assignment warnings after the final streamline count is applied, or if nonzero edge count is below a preregistered threshold derived only from the 10-subject QC distribution excluding known outlier 100307.
```

4. Outlier handling:

```text
100307 cannot be silently included or excluded after seeing structural-prediction performance.
```

Permitted choices before the 100-subject run:

```text
A. Include all subjects, but mark 100307-style warnings as a preregistered QC covariate and run sensitivity excluding warning-positive subjects.
B. Exclude warning-positive subjects before modeling using a frozen rule.
C. Repair the atlas/registration route before any 100-subject modeling, then rerun 10-subject QC from scratch.
```

5. Primary endpoint:

```text
M3 true subject G_i must be compared against M1 no-structure and M2 group-mean structure at the subject level.
```

6. Nulls:

```text
swapped-subject G_j
rewired degree/weight-matched graph
distance-only graph
random graph prior
```

## Claim Boundary

The current P7 package supports:

```text
10-subject ACT/iFOD2/SIFT2 engineering QC feasibility.
```

It does not support:

```text
subject-specific structural grounding
structural prediction advantage
NAP structural grounding
CWP validation
```
