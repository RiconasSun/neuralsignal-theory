# A10. One-command Reproduction

Command:

```powershell
.\paper8\scripts\reproduce-paper8.ps1
```

Current implemented scope:

```text
E0 public dataset and measured-physiology availability audit
E1 HCP WM Physio_log download / existing-file confirmation
E1-E6 HCP measured-physiology ladder smoke
figure generation
P8-v2 signal-separation audit
P8-v2 figure generation
P8-final ds005795 manifest audit
P8-final ds005795 streaming nuisance ladder over all complete task-learning subjects
E8 claim audit
```

Expected behavior:

```text
If measured physiology files cannot be found or downloaded, the command records the exact blocker and does not substitute proxy nuisance regressors for true respiration/cardiac data.
If large HCP CIFTI/dlabel/EV/motion inputs are absent locally, the HCP raw ladder step writes p8_e1_e6_hcp_physio_ladder_preflight_blocker.json and returns an allowed nonzero preflight code. Existing HCP ladder result artifacts are then used for figure/package assembly rather than pretending that raw HCP CIFTI regeneration occurred.
For ds005795, the command streams only the five manifest-complete task-learning subjects and deletes each BOLD file after subject-level processing.
```

Current expected conclusion:

```text
P8_E1_E6_HCP_PHYSIO_SMOKE_RAW_GATE_FAILED
```

Expected extension result:

```text
PASS_DS005795_STREAMING_NUISANCE_LADDER
```

Expected claim boundary:

```text
The ds005795 extension is convergent nuisance-relevance evidence only. It does not rescue the failed HCP primary transition-reproducibility gate.
```
