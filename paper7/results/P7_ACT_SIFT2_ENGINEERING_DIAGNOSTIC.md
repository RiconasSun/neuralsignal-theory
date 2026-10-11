# P7 ACT/SIFT2 Engineering Diagnostic

Status: `P7_HIGH_FIDELITY_ROUTE_PARTIAL_5TT_READY_TRACTOGRAPHY_NOT_READY`

## Findings

- HCP 100307 DWI, gradients, mask, aparc+aseg, wmparc, WM dtseries, and movement files are locally available for the current FreeSurfer-5TT route.
- WSL user-space MRtrix3 can generate DWI MIF, tissue response files, MSMT-CSD output files, FreeSurfer 5TT, DWI-grid 5TT, and DWI-grid parcellation intermediates.
- Initial MSMT-CSD WM FOD output was all zero under the completed smoke run, making ACT/iFOD2 tractography invalid.
- Explicit-shell MSMT-CSD was attempted but exceeded the interactive runtime window and was interrupted before a usable replacement FOD could be validated.
- Single-tissue CSD generated a nonzero diagnostic FOD, and diagnostic ACT/iFOD2/SIFT2/tck2connectome completed. This proves the MRtrix back half can execute, but it is not the frozen P7 final-route MSMT-CSD result and cannot support a structural hypothesis claim.

## Next Required Step

Resolve MSMT-CSD zero-FOD/runtime issue, then rerun checkpointed E2 until ACT/iFOD2/SIFT2 connectome_sift2_smoke.csv exists for 100307 before scaling to 3 subjects.

## Claim Boundary

P7 remains open. The high-fidelity structural hypothesis has not been tested and no subject-specific structural-grounding result is available.

