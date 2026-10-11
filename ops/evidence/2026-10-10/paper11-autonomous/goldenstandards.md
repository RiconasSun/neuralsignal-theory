# P11 Autonomous Requirement Baseline

Frozen before new analysis code. Source: current user autonomous execution request.
Prechange commit: 9145c407cf383226f111752d6299c4b5c0a98303; clean test branch.
M0/M1 passed. origin/main absent; origin/test verified at prechange commit.
The new authorization supersedes manual approval between milestones, not the
scientific protocol or holdout lock. One active milestone; parallel preparatory
work cannot access holdout counts or claim completion of a dependent gate.

Actor: researcher. Outcome: auditable P11 package or documented scientific stop.
Flow: verify predecessors -> train-only smoke -> small cohort -> full cohort ->
tests/QC/claims/gate -> next milestone only on PASS -> review -> scoped test push.
Preserve Papers 1-10, protocol/freeze and actual trial partitions byte-for-byte.
No NAP/CWP validation or positive-result requirement.

| ID | Atomic requirement | Verification | Status |
| --- | --- | --- | --- |
| R01 | Verify M0/M1 and frozen inputs before M2 | Hashes and gate tests | VERIFIED |
| R02 | Training-only 100 ms integer counts with exposure and causal metadata | Boundary, zero-count, isolation and real-cohort tests | VERIFIED |
| R03 | Freeze feasibility decision without accessing validation/test timestamps | Access audit and input hashes | VERIFIED |
| R04 | All six frozen baselines with reset histories and train-only fits | Tests and real fits | VERIFIED |
| R05 | All three model families with matched causal covariates and marginal likelihood | Numerical, convergence and integration gates | BLOCKED_HUMAN_INPUT |
| R06 | Validation-only complexity selection; final holdout isolation | Frozen selections and access audit | IMPLEMENTED_UNVERIFIED |
| R07 | Subject-level statistics and all prespecified null/reproducibility tests | Real outputs and correction checks | BLOCKED_HUMAN_INPUT |
| R08 | Subject policy transfer and independent external compatibility audit | LOSO and frozen external manifest | BLOCKED_HUMAN_INPUT |
| R09 | Progressive figures/manuscript and A1-A10 with claim-safe missing results | Artifact and claim review | VERIFIED |
| R10 | Real logs, automated tests, QC, gate and instructions per milestone | Reproduction and provenance tests | VERIFIED |
| R11 | Stop on critical scientific failure/insufficiency; retain negative results | Gate routing and failure artifacts | VERIFIED |
| R12 | Preserve frozen holdouts, P1-P10 and forbidden-claim boundaries | Git diff and hash audit | VERIFIED |
| R13 | Final one-command PowerShell reproduction and scoped origin/test upload | Fresh replay, exact staging, remote match | IMPLEMENTED_UNVERIFIED |

baseline_requirement_count: 13. A critical failed gate leaves downstream items
unexecuted, not VERIFIED, and the complete-paper goal unachieved. Unit fixtures
are tests only, never experimental evidence. All load-bearing results must name
input/source identity and command. No baseline contraction to fit the outcome.

Closure: 8/13 verified. R10 covers all executed milestones; stopped future
milestones are not marked complete. R06 selection/holdout isolation partly
verified; complete regime selection blocked by M4. R13 scoped upload does not
establish full-paper reproduction. No baseline requirements altered.
