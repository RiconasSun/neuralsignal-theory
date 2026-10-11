# Paper 7 Environment Recovery Audit

Date: 2026-09-04

Purpose:

```text
Determine whether the Paper 7 high-fidelity ACT/iFOD2/SIFT2 structural pipeline can be unlocked autonomously on the current machine.
```

Observed local state:

```text
Windows host has Docker CLI installed.
WSL Ubuntu exists and starts.
Native Windows MRtrix3/FSL commands are not on PATH.
```

Autonomous recovery attempts:

| Attempt | Result | Interpretation |
|---|---|---|
| Native command lookup for MRtrix3/FSL | `mrconvert`, `dwi2response`, `dwi2fod`, `tckgen`, `tcksift2`, `tck2connectome`, `labelconvert`, `flirt`, `bet`, `eddy`, and `topup` were not found | Native toolchain is unavailable |
| Docker daemon check | Docker CLI exists, but daemon connection failed before startup attempt | Docker was not initially usable |
| WSL Ubuntu check | Ubuntu WSL2 starts and has `apt-get` and Python 3.12.3 | WSL itself is usable |
| WSL apt package check | `mrtrix3` candidate exists in Ubuntu noble/universe; `fsl` has no apt candidate in current source list | MRtrix3 may be installable with admin privileges; FSL is still unresolved |
| WSL apt install MRtrix3 | `sudo: a password is required` | Installation requires a human-provided sudo password |
| Docker Desktop startup attempt | Started Docker Desktop and waited for daemon; `docker version` did not return within the run window and was interrupted | Docker route is not currently available for autonomous execution |
| WSL user-space micromamba install | micromamba 2.9.0 installed under `/home/a5993/.local/bin` without sudo | User-space package route is available |
| WSL user-space MRtrix3 install | `mrtrix3 3.0.8` installed under `/home/a5993/mamba-envs/p7-neuro` | MRtrix3 blocker is partially resolved through WSL |
| WSL MRtrix DWI read/write smoke | `mrinfo` read HCP subject 100307 DWI and `mrconvert` generated `dwi.mif` | HCP DWI path and MRtrix I/O are functional |
| WSL full ACT/SIFT2 smoke attempt | full-volume response/FOD stage exceeded the interactive run window and was interrupted | Connectome was not generated; not a structural result |

Current blocker:

```text
Paper 7 cannot generate high-fidelity ACT/iFOD2/SIFT2 cohort connectomes in the current autonomous run. MRtrix3 is now available through WSL user-space micromamba and the FreeSurfer-5TT route runs through 5TT generation, but the final-route MSMT-CSD/tractography path has not produced a valid connectome.
```

Data blocker also remains:

```text
The current local HCP cache has 100 subject directories, but only 1 subject currently satisfies the complete local P7 modeling-input audit. The full Paper 7 cohort still requires additional complete HCP dMRI/T1w/tfMRI inputs or a revised, explicitly frozen smaller-scope cohort.
```

Allowed current claim:

```text
Paper 7 has a frozen protocol, dataset/toolchain audit, MRtrix ACT/SIFT2 command plan, environment recovery audit, and claim audit. WSL MRtrix3 can read/write HCP DWI files, but the high-fidelity structural hypothesis has not been tested.
```

Forbidden current claims:

```text
High-fidelity ACT/iFOD2/SIFT2 cohort connectomes were generated.
Subject-specific structural connectivity constrains brain-state dynamics.
Paper 7 refutes the structural hypothesis.
Paper 7 supports the structural hypothesis.
NAP is structurally grounded.
CWP is validated.
```
