# P16 M1 protocol handoff

Mission: `P16-M1-VISUAL-DYNAMICS-PROTOCOL-FREEZE`.
Base: `2adb11a9fcd05cf1ea3cb4e120b5102400d6bb84`.
Scientific status: **M1_FROZEN_WITH_SOURCE_LIMITATIONS**.

The primary study compares B4 with B1 on nominal flashes. B0–B4, D, C and S are registered; five secondary comparisons form a Holm family. Native stimulus metadata have been checked for all 55 original candidates. Physiological admission, native behavior mapping, production workers and real model fitting remain future work.

`Prompt3_ready` means the protocol can be handed to a separately authorized native-QC and engineering mission. It grants no current neural fitting or Final C/D access and does not start the next mission.

Read [the protocol](M1_SCIENTIFIC_PROTOCOL.md), [equations](FEATURE_AND_MODEL_EQUATIONS.md), [statistics](STATISTICAL_ANALYSIS_PLAN.md), [source contract](STIMULUS_CONTRACT.md), [numerical policy](NUMERICAL_POLICY.json), [controls](controls.json) and [holdout boundary](EVALUATION_BOUNDARY.md). The exact roster and stage distinctions are in `FROZEN_COHORT.csv` and `SOURCE_VALIDITY_MATRIX.csv`.

Evidence is in `ops/evidence/2026-10-18/p16-m1-visual-dynamics-protocol-freeze/`. The earlier evidence folder retains the superseded candidate and all failed or interrupted reviews.

Run saved-only reproduction from the repository root in Windows PowerShell:

```powershell
& .\paper16_m1\reproduce.ps1
```

Required versions: Python 3.11.15, NumPy 2.4.6, SciPy 1.16.3, h5py 3.16.0 and requests 2.32.5. The ignored local `work/runtime` is one installed environment. On another host, install the pinned requirements in a separate environment and pass `-Python <full-python.exe>`.

Reproduction is offline. It checks saved metadata and small synthetic mathematical fixtures; it never invokes live acquisition or opens NWB/neural arrays. Source execution and saved-certificate reproduction are separate evidence levels.

Archive hashes assume the trusted versioned Git candidate. They reject incomplete or corrupt payloads; they do not authenticate a maliciously rewritten verifier and manifest or protect against administrators. No new cryptographic custody system or third party is claimed.

Stop after the reviewed M1 archive. No automatic Prompt 3 or Final evaluation.
