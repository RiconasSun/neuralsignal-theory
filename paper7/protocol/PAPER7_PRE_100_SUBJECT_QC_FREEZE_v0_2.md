# Paper 7 Pre-100-Subject QC Freeze v0.2

Date: 2026-09-04

Status:

```text
FROZEN_BEFORE_STRUCTURAL_PREDICTION
```

This file freezes the minimum QC/exclusion policy before Paper 7 may run any
100-subject structural prediction model. These rules use only engineering QC
from the 15-subject connectome inventory and do not use any transition
prediction outcome.

## Evidence Used

```text
paper7/results/p7_e5_labelconvert_connectome_qc.json
paper7/results/p7_e5_100307_streamline_20000_sensitivity.json
paper7/results/p7_e6_streaming_batch_10_2.json
paper7/results/p7_e6_streaming_batch_12_3.json
paper7/results/p7_e6_streaming_cleanup_audit.json
paper7/results/p7_e6_available_fsdefault_connectome_summary.json
```

Current available fs_default84 inventory:

```text
n = 15 subjects
nonzero_edges_min = 282
nonzero_edges_mean = 1037.6
nonzero_edges_max = 1148
```

Excluding known outlier 100307, the smoke/QC distribution is:

```text
n = 14 subjects
nonzero_edges_min = 1014
Q1 = 1075.0
median = 1102.0
Q3 = 1117.0
max = 1148
mean = 1091.5714
```

Subject 100307:

```text
5k fs_default84 nonzero_edges = 282
20k sensitivity nonzero_edges = 370
load-bearing tck2connectome warning persisted
```

## Frozen Connectome Representation

Primary engineering connectome for the next 100-subject build:

```text
MRtrix FreeSurfer-5TT ACT/iFOD2/SIFT2
MSMT-CSD generated on WSL ext4
MRtrix fs_default84 label-converted 84 x 84 matrix
5,000 streamlines for engineering-scale build
```

This remains a smoke-scale tractography count. It is acceptable for the next
pipeline-scale hypothesis test only if interpreted as a high-fidelity-route
engineering connectome, not as a final dense production tractogram.

## Frozen Exclusion Rules

Before any structural prediction model is run, exclude a subject from the
primary analysis if any of the following is true:

```text
1. fs_default84 connectome file is missing or empty.
2. fs_default84 connectome shape is not 84 x 84.
3. tck2connectome reports a load-bearing node-assignment/parcellation warning.
4. fs_default84 nonzero_edges < 800.
```

The `nonzero_edges < 800` threshold is deliberately below the observed
non-outlier minimum of 1014 in the current 14-subject QC distribution, while
still excluding the known 100307 failure at both 5k and 20k sensitivity.

## Frozen Handling of 100307

```text
100307 is excluded from the primary 100-subject structural prediction analysis.
```

Reason:

```text
The subject remains warning-positive and sparse after fs_default84 label
conversion and after 20k streamline sensitivity. Excluding it now prevents
post-hoc inclusion/exclusion based on structural prediction performance.
```

Allowed sensitivity:

```text
If needed, 100307 may be reported in a sensitivity appendix only, clearly marked
as QC-failed and excluded from primary gates.
```

## Frozen Cleanup Policy

For streaming 100-subject build:

```text
preserve fs_default84 connectome CSV
preserve fs_default84 assignments CSV
preserve nodes_fsdefault.mif
preserve nodes_fsdefault_dwi.mif
remove large generated intermediates after QC passes
remove raw DWI only if it was downloaded by that streaming run and keep_raw_dwi is false
```

This policy preserves auditable connectome outputs while preventing local disk
capacity from becoming the limiting factor.

## Claim Boundary

Allowed after this freeze:

```text
Paper 7 has a frozen pre-modeling QC/exclusion policy for scaling high-fidelity-route connectome generation.
```

Forbidden after this freeze:

```text
The structural hypothesis has been tested.
Subject-specific structure improves transition prediction.
100-subject structural connectome cohort is complete.
```
