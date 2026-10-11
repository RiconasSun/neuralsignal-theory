# A3. Full Pipeline

Frozen planned chain:

```text
E0 public dataset audit
E1 raw transition reproduction
E2 measured nuisance construction
E3 nested nuisance ladder
E4 motion-specific falsification
E5 physiology-specific falsification
E6 timing / HRF / autocorrelation controls
E7 subject-level and external/convergent replication
E8 gate system / claim audit / reproduction
```

Current implemented:

```text
E0 dataset and measured-physiology availability audit
E1 HCP WM Physio_log download
E1-E6 HCP WM measured-physiology nuisance ladder smoke
P8-v2 signal-separation audit
P8-final ds005795 manifest audit
P8-final ds005795 streaming nuisance ladder over all complete task-learning subjects
figure generation
E8 claim audit
```

Current executed ladder:

```text
HCP WM CIFTI dtseries + aparc dlabel
WM block EVs for 0bk_* and 2bk_*
Movement_Regressors.txt
tfMRI_WM_*_Physio_log.txt
aparc68 transition vector extraction
N0/N1/N2/N3/N4 residualization ladder
same-vs-different transition similarity
leave-one-run-out 0bk/2bk classification diagnostic
```

Current ds005795 convergent extension:

```text
public manifest audit
complete task-learning subject selection
streaming BOLD download
TR-aligned cardiac/respiration feature extraction
global BOLD signal transition prediction
N0/N1/N2/N3 nuisance prediction ladder
BOLD deletion after each subject
claim-boundary audit
```

The ds005795 extension uses a different task design and a global signal endpoint. It is not a direct replication of the HCP WM SameTransition > DifferentTransition analysis.
