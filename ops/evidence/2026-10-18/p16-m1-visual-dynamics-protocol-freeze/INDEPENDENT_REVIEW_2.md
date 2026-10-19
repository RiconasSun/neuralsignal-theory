# Independent internal scientific/specification review 2

Mission: `P16-M1-VISUAL-DYNAMICS-PROTOCOL-FREEZE`.

Decision: **ACCEPTED_PROTOCOL_FREEZE_WITH_SOURCE_LIMITATIONS**. Open P0: **0**. Open P1: **0**.

The repaired candidate is acceptable for the owner's `M1_FROZEN_WITH_SOURCE_LIMITATIONS` scientific protocol handoff. Normal origin/test archival closure is permitted subject to the actual mission-only staging, full commit SHA, remote/all-blob readback and clean-tree gates. This report does not assert those future Git actions succeeded. It grants no neural access, real fitting, Final C/D, production-worker admission or automatic next mission. This is independent internal review, not external peer review or independent-laboratory scientific validation.

## Exact identity

- BASE: `2adb11a9fcd05cf1ea3cb4e120b5102400d6bb84`.
- Current `paper16_m1/M1_FREEZE_MANIFEST.json` SHA256: `a9e787ae990fda13eb0b1899b9dd2d7e57c039c7b33f6630f3729fd27c19cab6`; **334 required payloads**, all verified.
- Latest owner SHA256: `b40a52e991971187f8d1a2f169945d99295630f58d35c1682bfc94605671444d`.
- Baseline SHA256: `5172bae9341e35846f4e9c4a3e4e72eaad6ed1be4297eb8a80b8819afda62a6d`; **346 owner/closure rows**, with **38 semantic acceptance groups** reviewed in the complete first review.
- Preserved complete first review: `INDEPENDENT_REVIEW_1.md`, SHA256 `d587676f8568763711dd1be0b70dcd15952233e894cceff002ee6ba0e54333e8`, remains **REPAIR_REQUIRED/0P0/3P1** for the old candidate. It is not rewritten or retroactively accepted.

This re-review examined the exact repair delta, new regressions, source execution/validation lineage, archived rejected candidate, current manifest and unchanged scientific boundaries. The complete first review remains applicable to byte-identical surfaces; this report resolves its three findings and supplies fresh verification for the changed surfaces.

## Repair verification

|Prior finding|Independent resolution|
|---|---|
|P1-01: S08 incorrectly said Holm3|The sole controls JSON change is `MainHolm3/pairedsignflips` to `MainHolm5/pairedsignflips`. The new consistency test requires all five original secondaries and rejects Holm3 anywhere in the controls JSON. No comparison, alpha, test direction, primary gate or correction changed. **RESOLVED**.|
|P1-02: selector ignored invalid records|`select_lambda` now validates every incoming record before aggregation: required fields, numeric registered lambda, canonical numeric mouse identity, known BO/FC protocol and finite numeric score. It rejects duplicate mouse×lambda identities, changed per-mouse protocol mappings and unequal support across the grid. Original protocol floors, total14 floor, .5/.5 weighting, B1 score-only criterion and stronger-ridge tie remain. New negative regressions include the demonstrated off-grid/NaN, unknown-protocol,13known+1unknown, protocol-switch, duplicate and unequal-support cases. **RESOLVED**.|
|P1-03: invalid tags accepted incomplete/reordered identities|`invalid_rows` now requires a strictly increasing integer ragged index within bounds and exactly three ordered fields. Sessions require the exact registered session ID and known label; probes require the exact matching numeric ID and known probe name before determining applicability. Missing/repeated/reordered/mismatched identities and malformed indices are denied. A valid nonselected probe is recognized but does not apply its interval. All current observed source tag rows still pass offline with unchanged masks. **RESOLVED**.|

The reviewer independently reran the original adversarial examples outside the package's new test methods. All four selector cases were denied: off-grid UNKNOWN/NaN appended to valid data,13 known-protocol mice plus UNKNOWN satisfying14 rows, UNKNOWN replacing an otherwise valid mouse, and a per-lambda protocol switch. An unchanged valid all-tied grid still selects lambda1.0. Missing probe fields, reversed probe ID/name, mismatched probe label and an extra repeated session tag were each denied; a canonical other-probe interval was accepted as known and correctly not applied. No source data or model fitting was needed.

The stricter validation is an enforcement of the already registered source/selection policy. It is not a new scientific hyperparameter, an optimizer change or a changed outcome oracle. Future production code must still bind admitted source/role identities and enforce the hard compute guards; these component oracles alone do not certify that worker.

## Preserved candidate and unchanged surfaces

Compared the current manifest to the rejected candidate archive. Exactly six original payloads changed:

- `paper16_m1/controls.json`;
- `paper16_m1/code/analysis_oracles.py`;
- `paper16_m1/code/roster_metadata.py`;
- the two corresponding test modules;
- `paper16_m1/code/verify.py`.

Seven added payloads are the repair note, unchanged first review, rejected archive/receipt, pre-repair reader snapshot and before/after regression logs. The verifier AST is unchanged after excluding its enlarged `EXPECTED_PAYLOAD` tuple. The repair does not alter the mathematical objective/gradients, statistical algorithms, model features, numerical gates, source arrays/receipts, roster, source allocation, running/pupil rules, physiological QC, controls beyond the Holm typo, budgets or holdout boundaries.

Independently read the archived old manifest and verified all its327 payloads against their original hashes and byte counts: **zero mismatches**. The old manifest is exactly `62a82e8ed71b037854574c77ea78108ca4ed51e1af3076a56b0b6074636f8930`. The preserved reader snapshot is byte-identical to the original reader, SHA256 `347ff6668427aa5ca2a3bc386bde46ebfd3d931399cb6abc3cd79f3ff24c27eb`. Its historical execution receipts remain historical executions of that source, not executions of the new stricter validator. `CURRENT_REVIEW_REPAIRS.md` states this distinction and grants no reacquisition. No new source acquisition occurred in this review.

The earlier complete scientific examination remains accepted on these unchanged surfaces:

- All55 original source-bound mice and one-probe VISp populations;28 Development,27 Final;5 BO/23 FC Development and27 BO Final; pilots and historical Allen overlaps remain Development. This is BO-targeted within-source transport, not IID same-protocol or independent-lab replication.
- Source terms remain noncommercial academic conditions, not CC BY4.0. Native nominal±1 flashes,150 original presentations/75 per color, float64 identities and all known-invalid exclusions remain source-based. The seven excluded presentations remain excluded.
- Strong saturated color×time B1 plus fixed adaptation/session/running nuisance terms; strict-past100 ms history and late100–220 ms six-bin target; original chronological cuts before exclusions; A/C-only scalers, QC, unit ranking and initialization; identical unit-bin exposure/masks in comparisons.
- Mandatory B0–B4/C/D/S definitions, D causal forward scoring, presentation-static S versus separate IID oracle, fixed C kernels, matched D/S251 parameter maxima, normalized D/S penalties and prospective shared±10 PSTH/B0 box. Joint latent prediction may model instantaneous dependence and does not establish extra past information, causal connectivity or physical persistent states.
- Primary and five Holm-corrected secondaries, equal-mouse inference, symmetry/exchangeability assumptions,10000 bootstrap draws, LOMO, own meaningful-effect CI requirement, explicit coverage/fallback and no VALIDATED category. The100 planning scenarios remain hypothetical, not empirical P16 power.
- All12 sensitivities/four bounded operators, N1 approximate-donor exchangeability limits, N2 count versus exact-time C distinction, N3 stimulus-destroying/full-native-support restriction and N4 deterministic coding stress. No favorable replacement, recursive Poisson generation or post-result family removal.
- Original16178 future optimizer-attempt ceiling, three required seeds11/23/37, fixed PG/AD/FD gates, separate diagnostic-call accounting and future external guards/wall limits. The small fixtures do not establish real feasibility.
- Final C-scoped reader requirement and future explicit owner exception before any whole-record D-containing decode; frozen C states/pre-D review/separate authorization for one D. Prompt3_ready is protocol handoff only. M1 stops at the reviewed archive.

## Fresh independent saved-only verification

Executed native Windows PowerShell from the repository root:

```powershell
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -ExecutionPolicy Bypass -File 'paper16_m1/reproduce.ps1'
```

Observed **exit0, all51 tests PASS**, including the three added regression methods. Full334 hash checks and saved55 metadata validation passed, with63 preserved metadata attempts/8 failed parser receipts,7 excluded presentations,100 hypothetical scenarios and36252 preserved original BASE paths. The six synthetic D/S fits and full251-coordinate AD test passed again; the largest synthetic PG was1.65e-6, AD scaled error9.24e-17 and frozen-h1e-5 FD scaled error1.91e-11. No thresholds were relaxed and no required test was removed.

These are source-metadata/synthetic mathematical checks, not neural prediction or Final execution. Network, NWB and non-allowlisted array loads remained blocked by the saved reproduction guard. The48 original parameter-equality certificates still do not retain independently re-decodable raw parameter strings; that limitation remains explicit. Real physiology, native behavior mapping, production integration/counters and Final permissions remain future gates rather than being relabeled passed.

## Current checked hashes

The334-entry verified manifest is the full identity binding. Changed components additionally checked:

|Path|SHA256|
|---|---|
|paper16_m1/controls.json|5ea6b238ad854e7cbff62985a2a79aa36cc7d9957056f4cd7c435df7ce5961a7|
|paper16_m1/code/analysis_oracles.py|edac31bc982630808ef999b1fc93ff3f6e52ca049df288cb89a55bc1e18452be|
|paper16_m1/code/roster_metadata.py|c50c3b913761f3e827415cc6528a0ade17ff14ae889b964cef4d9d08647c93a1|
|paper16_m1/code/test_analysis.py|0b13dd081d8a2e01d20e3f0f011c61119fc524a7c9d6e475476b258ccf957b8a|
|paper16_m1/code/test_roster_metadata.py|55e68eb38572c1c9c6814ec525dadc97be7cd8315cecc60b6a0d4945c7f5f17f|
|paper16_m1/code/verify.py|48774c06c18454ff47ac3033ec1a8c3a12b935cb6a351531bdf49a9c0078095c|
|CURRENT_REVIEW_REPAIRS.md in this evidence folder|3815c87226bd90e48a6c1dbb147fe07fe0aa83474b3699fbdcedbd110181e2b2|

No unresolved P0/P1 remains within the current M1 contract. All reviewer writes are restricted to this unique second report; original review and historical packages were not modified. Reviewer writers are **COMPLETE/quiescent** after sealing. Actual Git closure remains the root agent's subsequent evidence gate; stop after that M1 closure.
