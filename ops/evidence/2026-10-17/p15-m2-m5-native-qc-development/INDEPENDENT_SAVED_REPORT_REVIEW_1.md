# Independent saved-audit and reporting review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review: STATIC_AND_SYNTHETIC_REPAIR_REQUIRED. Open P0=0; open P1=4. This is not final mission review or approval to access any new data.

Scope: saved_audit.py, saved_verify.py, reproduce.ps1, report.py; narrow static inspection of imported pure/statistical and policy functions to trace behavior. No real saved reproduction was executed because ARCHIVE_FREEZE and E are unfinished. No actual neural/raw/A-cache/B/E/Final values were read. No fitting, network request, core mutation or interruption of the active fitting process occurred. Synthetic checks extracted AST functions/expressions into isolated dictionaries only.

Candidate SHA256 identities:
- `saved_audit.py`: `0b3843b0ca4d01192d604deb85c60ed4d6eec6a0b835d55bed1a0356360dc035`
- `saved_verify.py`: `d1ee58f7e546777d24ef118cb96088a7cba3f7e0c03e1888c4a9931155358acd`
- `reproduce.ps1`: `c9b8595d13038ef74881e82234c7ab8b910b3a80fb1bfe9fac184bb5acd76397`
- `report.py`: `1f117964177ef68744d5cbfe3953b0bb9554c8d6be45a4406e9d1d0543fcd037`

## P1-1 — Sensitivity numerical certificate is not independently checked

`saved_audit.py:15-43`: the sensitivity branch trusts its saved PG and only checks <=0.001 plus independent/status values. It never derives bounds, validates coefficient bounds, or recomputes projected gradient from the saved analytic gradient. The extracted function accepted an entirely synthetic NUMERICAL_PASS record with coefficient100, supplied bounds[-8,8], nonzero gradient1 and forged PG0. This is an audit-validator gap, not evidence that real fits failed. Repair with an independently reconstructed frozen coordinate/bounds schema (or verified complete serialized bounds), recomputed PG, finite/range/dimension checks and complete PASS-versus-failure consistency. Do not load A arrays or refit to do this.

## P1-2 — Mandatory QC and manifest completeness can be silently omitted

`saved_verify.py:31-57` checks hashes of listed ARCHIVE_FREEZE entries and globs whichever *_A_QC.json happen to exist; no required subject/key-set comparison rejects an omitted QC journal or an incomplete initial manifest. Empty/subset QC enumeration is consequently not independently ruled out. Require exact required native-QC subject identities, no duplicates/extras, and a complete allowed artifact manifest set excluding only explicit work/cache/self-receipt exclusions. A listed hash passing is not proof that every mandatory file was listed. The final actual archive freeze must be reviewed after construction.

## P1-3 — Selection cohort/configuration identity is self-declared

`saved_audit.py:67-101` checks candidate count37 and uses SELECTION_FREEZE.subjects to validate B and E, without independently requiring that subject list equal the admitted A-plan cohort or candidate definitions equal the exact registered groups. A truncated/reordered/repeated or substituted selection cohort/configuration list is not structurally rejected merely by the existing len37 and saved-score arithmetic. Bind selection subjects exactly to admitted()/A_FIT_PLAN subjects, compare the full registered unique groups/configurations and selected-family identities, and require E subjects/controls/case identities and exact result-hash key sets to agree. Preserve unavailable candidates and p=1 fixed-family slots; do not rescore B/E.

## P1-4 — Prompt4 readiness does not depend on mandatory Development gates

`report.py:17-100`: PROMPT_4_READY evaluates only bool(complete and dynamic_available). An isolated evaluation returns true even with production and baseline gates false. Make readiness explicitly conjunctive with completed source/QC, >=8 Development mice/4 labs, production implementation/numerical gate, primary B0/B1/B4 baseline availability, complete fixed attempts/selection, complete single E batch, saved audit/reproduction and reviewed archived evidence. Keep actual Final C/D and pre-D gates separately NOT_EXECUTED/REQUIRES_AUTHORIZATION. This report must never turn a Development handoff into actual Final readiness. BUG_COUNT/WARN_COUNT should come from reviewed evidence instead of unconditional constants.

## Frozen M1 conditional-rule guard

SCIENTIFIC_PROTOCOL.md lines25,39-45 and STATISTICS_CONTROLS.md distinguish valid negative/mixed/unavailable findings from implementation/integrity failures. Mandatory sensitivity/control coverage or nonpositive effects limit named positive claims; they must not become a new significance-based stopping rule or automatic scientific PASS. S02/S03 are capacity-conditional. Secondary-family unavailability does not erase a valid primary; any later primary-only Final path must be disclosed and separately authorized, not silently auto-promoted. Current report may state full-dynamic handoff unavailable, with a distinct conditional path requiring future reviewer/human authorization. It may not invent a new model or require every optimizer start to pass when the frozen global-family availability rule already preserves failed candidates.

## What currently works

PowerShell entrypoint runs the saved module without downloads. Static saved path denies socket network and np.load, recomputes numerical coordinate arithmetic, B mean/selection arithmetic, exact mouse-level E statistics, sensitivity summaries and finite reference summaries from saved aggregate records. It does not call fit/prepare/extract_role/run. Report explicitly distinguishes exploratory Development from held-out validation, retains failed/unavailable panels, discloses anatomy/clock/wheel/assumption limitations, and denies Final C/D authorization. These strengths do not close the four validator/readiness gaps above.

Synthetic evidence: `paper15_dev/work/independent_saved_report_review_1/synthetic_findings.json` (ignored scratch; preserve relevant result in mission evidence). No repair has been made by this reviewer. Re-review revised exact hashes before final report/archive acceptance.
