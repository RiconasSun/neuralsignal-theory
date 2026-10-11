# A9. Limitations and Failed Analyses

Current limitation:

```text
The measured-physiology nuisance ladder has been run only as an HCP-YA WM smoke test, and the preregistered raw SameTransition > DifferentTransition gate failed.
```

Current failed or incomplete analyses:

```text
raw transition reproduction: failed under the preregistered same-vs-different endpoint
measured nuisance construction: completed for motion, respiration, cardiac/pulse, and combined rung
motion/physiology survival: not claimable because raw gate failed
timing / HRF / autocorrelation controls: not completed
label/window/phase/jitter nulls: not completed
direct external HCP WM transition replication: not completed because the HCP primary gate failed before a positive effect existed to replicate
convergent ds005795 measured-physiology extension: completed over all complete task-learning subjects, but it uses a different task and global signal endpoint
```

P8-v2 limitation:

```text
The signal-separation audit used 100 permutations as a smoke-level null, not a final high-precision permutation test. Metadata-only accuracy was 0.625, so timing/domain/run metadata explain part of the 0/2-back structure and must be treated as a serious competing explanation in any final P8-v2.
```

Forbidden current claims:

```text
physiology eliminated
motion fully excluded
neural origin proven
CWP validated
NAP validated
Paper 8 is complete as a full physiological validation paper
```

ds005795 limitation:

```text
The ds005795 extension has only five complete task-learning subjects in the audited manifest and is descriptive. It demonstrates nuisance relevance for global BOLD prediction, not physiology-robust CWP/NAP transition reproducibility.
```
