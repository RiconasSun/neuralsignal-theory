# Independent completed-M4 and prospective M5 E-only review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:21:37Z.
Reviewer: separate local reviewer agent; independent internal scientific/evidence/code review, not external peer review.
Decision: **ACCEPTED_FOR_M5_E_ONLY_EXPLORATORY_REPORTING**.
Open P0: **0**. Open P1: **0**.

This accepts the frozen development E-only export/scoring/reporting path after the independently checked completed M4 prerequisites. It does not release final D, authorize new fitting, certify unimplemented controls/sensitivities or final C calibration, validate scientific superiority, or establish full mission PASS. No approval file was created by this reviewer.

## Frozen candidate and fresh reproduction

Independently verified `paper13_ki_execution1/M5_E_IMPLEMENTATION_FREEZE.json` SHA256 **8f6ce6f0a85743950c3aeca93b06e0acfc0daa3808a47c4615a83d5be78ad4e2**, containing **2,131** hashes. Fresh execution of `& .\paper13_ki_execution1\reproduce_M5_E.ps1` returned exit **0**. Its saved-only verifier checked every current frozen hash and all **85** original protocol/source hashes, ran **93 synthetic tests**, and reconstructed ten complete development model bundles. Network connections are rejected inside the verifier's saved/synthetic execution block. No real fits or E/D scientific values were read by this reproduction.

Read the E implementation registration, original activation's M5/M6 clauses and frozen protocol, current `development_bundle.py`, `exploratory_E.py`, their tests/verifier, relevant unchanged family/baseline/source/prediction/statistics implementations, actual M4 saved fit/selection/action records and saved A/B states as permitted. Repository `ops/review.skill.md` is absent, consistent with the mission golden standards; this review applies the provided review directive and frozen scientific sources. Earlier reviews remain unchanged. Modules outside this freeze are outside this acceptance.

## Actual M4 numerical evidence

Independently reconciled the exact development roster: **10 mice x (27 D + 27 C) = 540 required new fits**, with the previous **390** baseline fits, hence **930** development fits. Every required key is present once; all 540 are PASS. Each has 16 coefficients, registered family/configuration/A partition/source identity, finite parameters within [-8,8], original D random start or C zero start, complete canonical request hash and preserved trajectory. All 540 external trajectory files match their embedded trajectory records and iteration counts. No failed or missing required candidate was pruned.

Checked **1,620** initial/first-callback/endpoint certificates, all-coordinate finite analytical/independent AD/fixed-step FD vectors, identical objective convention, fixed h=1e-4 and required error bounds. Fresh verifier maxima:

| Quantity | Maximum |
|---|---:|
| Endpoint projected gradient | 9.92840191745871e-6 |
| Independent AD relative gradient error | 6.245004513516506e-17 |
| Fixed h=1e-4 FD relative gradient error | 2.9721513026322727e-9 |
| Registered objective-call count per fit | 251 |

These satisfy PG<=.001, derivative-error<=1e-5 and the unchanged call/iteration caps. This audits saved full certificates and recomputes vector/error/identity relationships; it does not claim to rerun 540 optimizations or independently regenerate all their derivative vectors from neural data.

A separate offline `python -B -` inspection reconstructed each mouse's B4 A offset from the original A-selected B4 coefficients/ridge1 and saved A scaler. All ten offset hashes match the gate and every D/C request. Saved A counts/unit/epoch hashes, full data hashes including x/offset, initial-vector hashes and canonical request hashes match. Recomputed all C A-derived preprocessing states with the frozen tau/QR-seed policy; saved bytes/hashes match, including fixed Q and A count/hidden moments. D and C have the same original B4 offsets, without substituting B*.

The M4 action log contains **540 FIT_START, 540 FIT_COMPLETE, 90 D_B_SCORE and 270 C_B_SCORE** entries. Every required completion precedes the first dynamic B score, and no fitting event follows that first score. This supports the required all-candidate gate before model selection.

## Actual global B selection and static reuse

The independent offline inspection loaded only permitted saved A/B bundles and frozen coefficients/scalers. It recalculated **90 D + 270 C = 360** saved B candidate scores, each with the original 30 epochs, eight A-selected units and 25 scored bins (6,000 nominal unit-bins). Maximum discrepancy from saved scores and B4 gains was **0.0**. It separately chose D starts by minimum A objective with the frozen 1e-12/lower-seed tie rule, and reconstructed equal-mouse paired-difference means/SEs, eligible sets, best references and registered tie-priority selections without calling the production selection wrapper.

The resulting global choices match:

- **D:** p=.9, ridge=.1; each mouse's start selected solely from its A objectives.
- **C:** tau=(.1,.3), ridge=1, projection seed=23, shared globally across mice.
- **S:** p=.5, ridge=.1, reusing existing development HMM fits; zero additional fits and A-only start selection.

B*=B2 remains the original strongest-baseline guard. B4 remains the shared offset. These B results are development selection evidence, not an independent-mouse validation or a temporal/causal conclusion.

## Complete development bundle

`development_bundle.gates()` enforces the reviewed upstream source/approval identities, complete baseline/family rosters and numerical certificates before E. `build()` retains the original eight selected units and training-state identity, all five globally selected baselines with A-only chosen starts/scalers, selected D/S requests and starts, and globally selected C projection/state. Selected scaler bytes are checked against the fit identity; report-only D/S state ordering does not change prediction parameters. The independent reconstruction checked baseline theta/request identities and chosen family configurations for all ten bundles. Synthetic tests separately cover A-objective ties, global C seed, forbidden final/wrong partitions, corrupted selected scalers and incomplete family gates.

## E authority, export and reporting boundary

The original direct owner activation expressly authorizes development E exploratory reporting after required preceding gates. This authority comes from that activation and frozen stage contract. The later full-record decoding reply resolved the pre-M2 raw-ingest ambiguity; neither that reply nor the r5 M2 certificate is treated as a standalone E permission. Fresh E-specific independent approval is still required by `exploratory_E.approved()` before the runner opens models/source. At review time **M5_E_APPROVAL.json and real M5_EXPLORATORY_RESULTS.json do not exist**; acceptance has not been converted into access by the reviewer.

The reviewed runner iterates the frozen allocation and admitted development roster, never final-role records. Its adapter requires 30 frozen E windows, complete M4 PASS and canonical saved A QC/selected units before source use. Only the original eight units are read/exported; ID rows are checked. The trusted decoder's full-record transient decoding remains subject to the owner's permission and nonfinite/unassignable SOURCE_INTEGRITY_STOP. It exports selected E windows only and computes no full-record quality statistic or final-D outcome summary. Failed unit exports retain durable start/complete/error events; interrupted journal/file states cannot silently overwrite or retry the export. Completed reuse checks source-freeze/result/state hashes.

Scoring uses the frozen complete A model bundle and A scalers with original event metadata. There is no E unit QC/ranking, parameter fitting, scaler estimation, ridge/seed/configuration selection or update to M3/M4 selection. All five baselines, D, C, S and B* alias are retained; every mouse has 6,000 scored nominal unit-bins. Per-bin joint likelihoods, complete model/state identities, all six mouse effects and registered statistics are saved. The already reviewed exact-statistics r2 code is hash-bound here; its exact-inclusive integer sign tails, separate Holm3 families, joint 10,000 mouse bootstrap/seed130041/linear quantiles, direction/LOMO summaries and explicit absence of final claim classification remain intact.

Tests cover denial before E approval/M4 completion, final role/wrong epoch count/unit tampering before source, synthetic E-only export without QC/scaling, source STOP retention, full-model scoring parity, exact statistics and guard/denominator behavior. The result explicitly labels E **EXPLORATORY_DEVELOPMENT_ONLY_NOT_FINAL_VALIDATION**, with no selection change/new fits/final-D outcomes. A local `M5: PASS` denotes completion of this exploratory stage and cannot be promoted into a scientific claim or whole-mission completion.

## Acceptance limits

No network, raw neural source, E/final-D count/value, new real fit or new real E/D score was accessed during this review. The independent audit commands used saved A/B evidence and synthetic arrays only; no final C neural values were interpreted. Only this new review file is written by the reviewer, apart from the reproduction tests' ignored synthetic work artifacts.

**0 open P0/P1** were found for the frozen M4 evidence and prospective E-only scope. The parent may bind this actual review to an E-only approval and execute that stage within the original authorization. Preserve all mixed/negative E results, do not retune, and keep final C calibration, controls/sensitivities, final release review, exactly-one-D assessment and scientific interpretation gates separate. No unimplemented stage, manuscript, scientific superiority, full mission PASS or prospective Git push/readback/clean status is certified here.
