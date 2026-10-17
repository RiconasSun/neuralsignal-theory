# P15 M1 protocol handoff

This mission freezes a predictive scientific contract, not scientific outcomes. Recommended scientific status is **M1_FROZEN_READY_FOR_M2** only after independent review and final protocol hash freeze; terminal archive PASS additionally requires actual origin/test/readback/clean proof. No real neural arrays, new pilot processing, scientific fits, scoring or C/D access occurred in M1.

| Requested field | Protocol meaning |
|---|---|
| SCIENTIFIC_PROTOCOL_FROZEN | Final reviewed timestamp/hashes are PROTOCOL_FREEZE.json; no backdated outcome registration |
| FROZEN_SOURCE | Native IBL BWM CC BY4;139mice/459sessions/699probes; sorting2024-05-06/task2025-03-03, exact collection/UUID-resolution policy |
| FROZEN_MICE | Exact20 metadata candidates; COHORT.csv byte-identical to M0; one fixed MOp session/probe per mouse |
| DEVELOPMENT_FINAL_ALLOCATION | Original12/8, both pilot mice permanentlyDevelopment; no reroll/replacement |
| PRIMARY_ESTIMAND | Equal-mouse mean B4−B1 LL gain, nats per actual scored nominal curated-release unit-bin |
| MODEL_FAMILIES | B0–B4 nested Poisson; conditional exact-forward HMM D; fixed-projection finite-timescale history C; capacity-controlled IID mixture S |
| STATISTICAL_PLAN | Prespecified one-sided primary sign enumeration with explicit symmetry/independence assumptions;10kwholemousebootstrap;Holm5secondary;LOMO/lab/precision/attrition rules |
| NUMERICAL_GATES | float64;PG<=.001;independentgradienterror<=1e-5;fixedFDscales all required;AD gate;bounded L-BFGS-B/seeds/no retry;production worker still needs separate implementation certification |
| FALSIFICATION_PLAN | 11finite sensitivity cases;4×999 destructive reference suites, known exchangeability limitations, no recursive Poisson generator; all failures/unavailable panels retained |
| OBSERVATION_CONTRACT | AP duration+provider sync+native events/wheel+known invalid/saturation masks; truezero retained; ordinary curated release with unknown other artifact burden |
| REMAINING_PHYSIOLOGICAL_QC | All20 not yet admitted;18nativeannotationequivalences unresolved;futureA/C-only rate/refractory/coverage/ranking/scales/masks and source checks required |
| PROMPT_3_READY | Protocol handoff ready after review; **real fitting not ready or authorized** until separately authorized native/QC and production implementation gates pass |
| BUG_COUNT / WARN_COUNT | Final reviewed archive counters in evidence/verdict.md; scientific limits are not fabricated results |
| GIT_COMMIT / REMOTE_VERIFICATION | Actual post-commit live SHA/changed-byte/clean receipt, never a predicted Git PASS |

Primary choices are 50ms bins,500ms strictly past history,8units,37nuisance features and fixed original whole-trial A/B/E (60/20/20) or C/D (60/40) cuts with adjacent guard trials removed. Native trial IDs are resolved under the frozen rule before future QC; old aggregate row IDs/masks are not silently reused. Source and physiological attrition remain possible. At least8Development and4Developmentlabs are required; Final8 is an inference candidate,6–7descriptiveonly,<6stopsfullcomparison. These floors do not prove power.

The primary positive label requires prespecified direction, .001gain resolution,95%interval/width<=.01,p<=.05,mouse/lab robustness and mandatory sensitivity/reference conditions. Statistical tests do not remove their assumptions. Unmeasured movements, sorting/anatomy uncertainty, finite-capacity restrictions, smallanimal/labdenominators and source-version discrepancies remain limitations. No mechanism, neural primitive, independent-lab replication, movement-independence or realtime forecast claim follows from M1.

Seventeen compact synthetic specification tests pass; three saved design tables reproduce offline. GLM derivatives are independently checked against autograd and all three fixed finite-difference scales; HMM conditional forward likelihood agrees with enumerated paths. Other tests cover causal indexing, strict-past wheel, resets/missing support, constraints, counts/nesting, IID versus persistent states, sign enumeration, Holm and finite reference transformations. Two review regressions cover S07 chunk/role RNG invariance and N2's exact past-wheel interval/tie rule. They do **not** certify a full real-data worker. One-command: `& .\paper15_m1\reproduce.ps1`, with pinned local runtime or `-Python` supplied. No data download or model fitting is hidden in reproduction.

Independent internal review, any unsuccessful review and corrections are kept in the mission evidence directory. The refused external CLI path and safe local continuation are preserved in EXECUTION_DEVIATIONS.md; this is not represented as a successful CLI implementation. P1–P14/M0 are unchanged. STOP after M1. A later mission must explicitly authorize its own QC/fitting/data access, and Prompt4 must explicitly authorize the one final assessment after pre-D gates.
