# Independent internal scientific/specification review 1

Mission: `P16-M1-VISUAL-DYNAMICS-PROTOCOL-FREEZE`.

Decision: **REPAIR_REQUIRED**. Open P0: **0**. Open P1: **3**. This review does not approve the current protocol freeze or Git closure. It is an internal independent-agent review, not independent-laboratory validation or external peer review.

## Exact reviewed identity and scope

- BASE: `2adb11a9fcd05cf1ea3cb4e120b5102400d6bb84`.
- `paper16_m1/M1_FREEZE_MANIFEST.json`: `62a82e8ed71b037854574c77ea78108ca4ed51e1af3076a56b0b6074636f8930`, 327 required payloads, independently checked by the saved-only command below. The manifest was unchanged at the end of review.
- Latest `OWNER_REQUEST.txt`: `b40a52e991971187f8d1a2f169945d99295630f58d35c1682bfc94605671444d`.
- `baseline.json`: `5172bae9341e35846f4e9c4a3e4e72eaad6ed1be4297eb8a80b8819afda62a6d`. All 346 rows were inspected; all rows with owner source-line references exactly match those owner lines. The six additional preservation/review/closure rows remain distinct.
- `ATOMIC_ACCEPTANCE.csv`: `8c7b9564a3072aa5e77ac766d5af0d5c71a8231d0e21f901ed546f8bb8e9d73e`; all 38 semantic groups reviewed.
- `REQUIREMENT_TRACE.csv`: `7735ed733407c12d87d21694b90580f44bb7bb70289cfb2f9e54e26b6452c4c8`. Its generic evidence descriptions are supplemented here by the concrete scientific and execution checks below; they are not treated as 346 executed tests.

Reviewed the current package's protocol, stimulus/source/QC, BO/FC transport, model equations, numerical policy, statistics, controls/sensitivities, access boundary, A1–A10 and reproduction documents; current root JSON/CSV; all current code and tests; saved source SDK definitions; metadata registration/repair lineage and receipts; M0 authoritative scientific handoff, source rights, evaluation/observation limitations and original role/source evidence. Historical superseded optional-family drafts are evidence, not current acceptance criteria.

Only this report was written by the reviewer. No NWB, real neural array, real fit, real neural likelihood/gradient, Final C/D execution, network acquisition, scientific-policy repair, or Git mutation was performed. Synthetic tests and saved stimulus/invalid-interval metadata arithmetic were permitted and used.

## P1 findings

### P1-01 — S08 retains a contradictory three-test correction

Location: `paper16_m1/controls.json:130`, S08 `RNG_replicates`.

The current co-normative control table says `MainHolm3/pairedsignflips`. The latest owner requires the five secondaries B4−B2, B4−B3, D−B4, C−B4 and D−S; the SAP, protocol JSON and statistical oracle correctly specify Holm5. The scientific protocol explicitly makes the JSON documents co-normative and requires conflicts to be repaired before neural execution. S08 cannot leave a smaller multiplicity family available to a future implementation or author.

Required repair: change the S08 reference to the same complete five-comparison family and add a cross-document/control-table consistency regression. Preserve this rejected candidate/report. Do not change the five comparisons, primary gate, test direction, alpha, or correction.

### P1-02 — The B selector silently ignores invalid input records

Location: `paper16_m1/code/analysis_oracles.py:18`, `select_lambda`.

The oracle filters records into the three recognized lambdas, then filters each into BO and FC means. It does not validate the complete incoming record set or enforce one fixed known protocol per mouse across the grid. Consequently, malformed records can be ignored while a valid policy choice is returned. This violates the current protocol's unknown-protocol source-failure rule and weakens the promised selection/support/finiteness gates.

Reviewer synthetic counterexamples, with no source data or model fitting:

1. Start with 28 finite BO/FC records at each registered lambda, all scores −1. Append `{lambda:99, mouse_id:999, protocol:UNKNOWN, logscore:NaN}`. The selector returns `1.0` instead of rejecting the off-grid/nonfinite/unknown-source record.
2. At every registered lambda supply 14 unique records: 3 BO, 10 FC and 1 UNKNOWN, all scores −1. The selector returns `1.0`; the unknown row satisfies the total-14 floor although only 13 recognized-protocol mice contribute to the means.
3. Changing the last original mouse's protocol to UNKNOWN at every known lambda also returns `1.0`; that mouse is silently removed from protocol means rather than producing a source compatibility failure.

Required repair: validate every incoming row before scoring: exact registered grid, known protocol, finite score and valid identity; enforce unique mouse×lambda records, identical admitted mouse support and invariant protocol mapping across candidates. Compute the admission floor only over admitted, validated records. Add negative tests for the demonstrated cases and a protocol-switch case. The .5/.5 protocol weighting, original .01/.1/1 grid, B1-only criterion, floors and stronger-ridge tie rule should remain unchanged. Future production source/role identity binding is still separately required; this component repair does not certify a production worker.

### P1-03 — Probe invalid-interval tags do not enforce the declared canonical identity tuple

Location: `paper16_m1/code/roster_metadata.py:24–39`, `invalid_rows`.

The pinned SDK source documents ordered `[scope, scope_id, label]`. Current global validation and especially probe validation instead convert each tag row into a set. The probe branch accepts any nonempty subset of the matching probe's numeric ID/name. It therefore accepts an absent scope ID, absent label, or reversed ID/label, despite the source contract's fail-closed identity semantics.

Reviewer synthetic counterexamples using `item={session_id:123,probe_id:7}` and `probes=[{id:7,name:probeA}]`:

- `['EcephysProbe','7']` is accepted and applies an interval.
- `['EcephysProbe','probeA']` is accepted and applies an interval.
- The canonical `['EcephysProbe','7','probeA']` also applies, so missing fields are indistinguishable from canonical input to this parser.

Required repair: retain and validate the ordered, exactly three-field tuple, checking the registered scope ID and corresponding known label before deciding applicability; reject missing, repeated, reversed, unknown, or mismatched identities. Preserve the executed reader versions and metadata receipts as execution history. Add focused negative tests and saved-only parity checks against all current observed tag rows. No metadata reacquisition is required by this finding.

This finding does **not** establish incorrect exclusions in the actual 55 saved tables. The independent saved-metadata check found all observed source tag tuples canonical, all source identities bound, zero discrepancies in complete-presentation masks and exactly seven exclusions. It addresses the guard's false acceptance of malformed input and its co-normative claim.

## Scientific and owner-completeness examination

The following conclusions are component observations, not an approval overriding the three P1 findings.

|Acceptance groups|Independent examination and bounded conclusion|
|---|---|
|ACC-01–03, 06–09|The latest mandatory-D/C/S owner supersedes the earlier optional-family candidate. Original 55 mouse/session/probe identities and 28/27 roles match M0. Development is 5 BO/23 FC; Final remains 27 BO. Pilots/historical Allen overlaps remain Development. Single-probe seven-acronym VISp sampling and noncommercial academic terms are retained; no CC BY4.0 or independent-lab claim. Flash choice is source-based; unverifiable grating phase remains a preserved rejected/limited route.|
|ACC-04–05, 10–11|All 55 saved native stimulus tables contain 150 original IDs, 75 nominal colors each, native float64 times and positive source durations. Independent metadata arithmetic verified registered object identity fields, canonical observed invalid tags, complete-support masks and seven exclusions without calling the package's `evaluate`/`invalid_rows`. Duration extrema are .23351541708734658 to .2502306323715402 s. Original cuts precede exclusions; no role recutting occurs. Observation is explicitly curated nominal support, not raw packet continuity or absence of unannotated artifacts.|
|ACC-12–16|The late100–220 ms six-bin estimand avoids the uncertain actual offset;100 ms history is within the presentation, strictly past and reset. Saturated 12-cell color×time PSTH plus 12 nuisance features is a strong deterministic visual comparator. Original preceding-row/repetition semantics, causal running-parent end, missing flags, A/C-only shared scalers/activation and per-unit B0/scored-row initialization are explicit. B0–B4 likelihood, factorial, exposure, nested penalties and actual unit-bin denominator agree. Whole-session provider QC is disclosed separately from future A/C physiological rate/spikes/occupancy/within-window ISI/support admission; no D-quality selection is authorized. Native behavior/pupil mapping and actual physiology remain unexecuted gates.|
|ACC-17–22|D forward/backward, initial/transition logits and independent dual-number marginalization are consistent with the declared conditional HMM. S is one static state per presentation with three prior gates, not a per-bin IID mixture; both identity oracles are separate. C uses four finite100 ms exponential-history summaries with fixed tau40/100 ms, not a learned recurrent physical system. D/S β/δ penalties divided by U reproduce the average B4 objective at latent-zero parameters. D/S251 and C272 main maxima, D/S347/C368 sensitivity maxima and safe exponential-domain bounds follow the equations. Shared PSTH/B0 ±10 was prospectively revised before real fitting, with prior declaration/source/tests preserved. Joint D/S score can improve instantaneous dependence as well as history; the interpretation explicitly withholds pure past-information/state-mechanism claims.|
|ACC-23–24|Policy definitions retain B1-only B selection, protocol-balanced .5/.5 weighting, one lambda across models, all three latent seeds11/23/37 required and A/C-objective-only seed selection. The selector input guard needs P1-02. Budget arithmetic is consistent:2208 baseline unit optimizer attempts +440 C +330 D/S joint seeds +10560 eight-panel B1/B4/C unit attempts +2640 panel D/S seeds =16178;440 B0 analytic states are separate. 6000 optimizer pairs are separate from24P fixed-FD objective calls and3AD+3analytic checkpoint calls. External pre-evaluation/iteration/wall guards, real worker integration and feasibility remain required before real fits; SciPy options or these small fixtures do not certify them.|
|ACC-25–27|Primary B4−B1 two-sided test and positive interpretation, Holm5 secondaries, exact sign patterns through n16/99999 Monte Carlo thereafter, plus-one MC fraction, shared10000 whole-mouse bootstrap draws, linear quantiles, LOMO and own contrast CI lower>Δ are explicit. Null-symmetry/animal independence and bootstrap exchangeability are assumptions, not established by the data source. The primary gate and contrast-specific extra direction/N3 guards are implemented in the classifier. Twelve-Final coverage,6–11 descriptive fallback and <6 stop are prospective floors, not demonstrated power. The100 Gaussian/chi-square planning scenarios are hypothetical t-test/CI-resolution calculations, not empirical P16 variance or sign-flip/bootstrap power. No VALIDATED label is available. P1-01 remains a co-normative multiplicity contradiction.|
|ACC-28–30|All12 sensitivities and four bounded operators specify question, action, preservation/destruction, assumptions, coverage, randomness and consequences. Eight panels refit B1/B4/C/D/S under frozen lambda; rate/unit/anatomy restrictions use A/C/main IDs. N1's same-color/role/ordinal-block trajectory donors are only an approximate reference with residual running/adaptation/trial-gain limits. N2 preserves primary20 ms count boundaries and therefore B/D/S inputs but need not preserve exact-time C. N3 destroys stimulus phase and is not a conditional-history null; full-native-event support is explicitly required. N4 is deterministic coding stress, not a permutation test. No favorable redraw, recursive Poisson generator, forced degradation or physical persistence proof is permitted.|
|ACC-31–32, 38|Final C-only isolation is not silently granted by the protocol; any whole-record ragged decoding containing D requires future explicit owner authorization or a verified scoped index. Frozen C states and independent pre-D review precede separate authorization for exactly one D batch. M1 makes no real neural/fitting/Final permission and stops after archival freeze. Prompt3_ready means protocol handoff only.|
|ACC-33–35|Full expected-set checks reject missing/empty/duplicate/unsafe/tampered payloads. Saved reproduction blocks network, NWB and non-allowlisted NP loads; only metadata and small synthetic fixtures run. UTF8/PowerShell literal checks and prospective A1–A10 claim limits are present. Source certificate limitations remain explicit, especially the 48 parameter equality certificates whose raw strings cannot be independently re-decoded by saved-only replay.|
|ACC-36–37; REQ-341–346|Earlier rejected/interrupted reviews, source/parser failures, prospective normalization/bound revisions and candidate archives remain preserved. Current independent acceptance is withheld by this report. Normal origin/test push, actual full SHA/all-blob remote readback and clean-tree checks are future closure evidence and are not certified here. BASE preservation and byte-exact original daily suffix passed saved verification.|

## Independently executed verification

Executed from the repository root using native Windows PowerShell:

```powershell
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -ExecutionPolicy Bypass -File 'paper16_m1/reproduce.ps1'
```

Observed exit0, all48 tests PASS, 327 hash-bound files, 55 original stimulus tables,63 metadata attempts,8 preserved parser failures,7 excluded presentations,100 hypothetical scenarios and36252 original BASE paths. This run did not create a reviewer evidence log; the observed command results are recorded in this report and the frozen package contains the earlier independent replay receipts. No test outcome is substituted for the three additional negative counterexamples above.

The six synthetic D/S seed fits returned PG8.17e-7 to1.65e-6, maximum independent AD scaled coordinate error9.24e-17 and maximum frozen-h1e-5 FD scaled coordinate error1.91e-11. Initial/intermediate/endpoint and all four fixed FD scales passed; the full251-coordinate primary-capacity AD test also passed. This is evidence for the synthetic mathematical implementation, not real numerical convergence, biological effects or future production admission.

Additional reviewer-only saved/synthetic arithmetic confirmed:

- Exact owner-line/baseline mapping, cohort protocol counts, all55 metadata object identity fields and all observed source-invalid canonical tags.
- Independently reconstructed masks match every saved mask coordinate; total exclusions7. Minimum color counts across all55 tables are A/C37, B9, E8, D22.
- Seven current receipts retain observed parameters, while48 retain execution-backed compressed equality certificates. This limitation is not upgraded to independent raw-string replay.
- The actual63 attempts comprise the first55 jobs, seven registered targeted parser repairs and one final source-semantic repair; all8 failed receipts remain. Transport8,979,528 bytes and original cumulative per-object/global reservation ceilings passed reproduction.

## Checked source hashes

These hashes supplement the verified full327-entry manifest; they do not replace it.

|Path under paper16_m1|SHA256|
|---|---|
|protocol.json|36d074bdf8af121346d444a1f3b2eaf0b235c1327e88701d33863ad6c7f85746|
|controls.json|5d090207c81326e82e4978e0068f312c0fcedf18fa9eb8007f138e6af6010e2f|
|NUMERICAL_POLICY.json|9409657df46117ef20cfbde078898aa5346d448b974a5e86f3997238d07b49b8|
|code/analysis_oracles.py|ebd8c4007f704a627e0cbfd14c1a9ce377d31296044af30bd8697f2fd876b494|
|code/dynamics.py|e20ec86148de14003968de381602da4b038e82ff610cf6a621b396f588c667e2|
|code/spec.py|2e8daa11c9205893c24309f34379218847000d0a6895de8c5ea62eb2f644d01f|
|code/roster_metadata.py|347ff6668427aa5ca2a3bc386bde46ebfd3d931399cb6abc3cd79f3ff24c27eb|
|code/verify.py|7fd17da8b5319b1ed5b4bbc5670d3957d634cbae0c22560796dce6dad9a067dd|
|code/planning.py|b77b0698e2026f1b631b136ec00a2e2ca04a1c0e4c0459568bc6bb4943e783d9|

`ROSTER_METADATA_FINAL.json` SHA256 is `b818dbe13db0ca9af55686f02c05c472bccc867d8c9612da1e1c48b235d0120f`; `SOURCE_METADATA_REGISTRATION.json` is `d82eff0060123fe21f505357f097e5a351c6dd8db6fc9bb24eb56595f539efb2`.

No additional P0/P1 was established by this complete internal review. Repair the three findings, preserve this unsuccessful review/candidate, bind the new bytes and run affected regressions plus saved reproduction before an independent re-review. No real neural experiment or Final access is needed for these repairs. Reviewer writers are COMPLETE after sealing this report.
