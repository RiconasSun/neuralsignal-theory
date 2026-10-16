# Independent P14 M0 scientific/source review r1

Mission: `P14-CONTEXT-DYNAMICS-DATA-FEASIBILITY`.
Exact BASE: `fae4fa316bbb499a86949d496e6ba4f36380e29f`.
Candidate payload-freeze SHA256: **fa4afef8e5d2102f045747298c088fecdd733b62d6ca2e6b7e4781dea7c78fb4**.
Decision: **REJECTED — NARROW DOCUMENTATION REPAIR REQUIRED**.
Open P0: **0**. Open P1: **1**.
Reviewer: separate internal scientific/source reviewer; not external peer review.

## P1 — The reported arithmetic erratum misstates the preserved registration

`paper14_m0/P14_M0_REPORT.md:15` calls the original registration's “600 scored bins” an arithmetic wording error. However, `paper14_m0/REGISTRATION.json:28` and the preserved `REGISTRATION_r1_BEFORE_COUNTS.json` both explicitly assign600 bins to **120 trials/context total**, and300 calibration bins to **60 trials/context/half**. With five100ms bins in the proposed half-second window, that original arithmetic is already correct. The report's attribution creates a false registration-history/criterion-change narrative precisely where the source-specific observation floor must remain auditable.

Remove the false error attribution and retain a plain clarification:60 trials/context/half yields300 bins,120/context total yields600, before unit multiplicity. Preserve both registration files and all actual60-trial/run/window/eligibility rules unchanged. No recomputation of neural outcomes, new dataset or threshold amendment is justified. Preserve this failed review and reviewed identities before the narrow correction and fresh candidate/review.

## Actual saved verification and source boundaries

Independently ran the native saved-only PowerShell reproduction:

`& .\paper14_m0\reproduce.ps1`

Actual exit0: **25 tests PASS,35 byte-identical deterministic result files,103 payload hashes,43 metadata files,25 original input hashes**, Python3.11.15/pandas3.0.5/NumPy2.4.6/Requests2.33.0, network denied. No neural array, fit or predictive score is part of this run. It regenerates metadata accounting in ignored work and does not refresh public sources. Independently verified the candidate freeze against CANDIDATE_IDENTITY and all103 payload entries; the52-item baseline and49-verified/3-open pre-review matrix are retained. REQ-049 review and051/052 actual Git/handoff remain pending; no final engineering PASS is certified.

Reviewed the scalar/event/anatomy/support column whitelist, exact metadata URLs/HEAD/ranges, ETag/size and decoded-output receipts, no SDK/NWB fallback, budget journal, preserved retrieval failures, threshold/clarification registrations and source registry. New DR decoded tables contain337 session rows,164778 trial rows and621423 unit-metadata rows, respectively6/19/12 permitted columns; forbidden neural-valued fields were not decoded. Schema inventory does not imply such columns' values were accessed. The source journal contains74 scripted requests/17171293 response bytes and two retained404 license failures; browser-discovery transport is explicitly unobservable, not falsely included. No new source, network call, old neural bundle, raw/count array, fit or score was accessed by this reviewer.

## Independent denominator and within-population checks

IBL retains139 independent mice/459 sessions/699 probes, with8 registered paired composite metadata candidates; repeated units/probes/sessions are not independent mice. Old/new295920 trial-row identities are verified before added covariate accounting. KI retains74 probe records/50 sessions/41 canonical animals from43 raw labels; Context-task8 is a source ceiling, not eight verified pairs. Reviewed aliases are reused without new merging. Cross-task overlap is described without making different populations interchangeable. Steinmetz's source-reported10-animal global ceiling is not a locally measured PFC cohort or a zero regional-coverage finding. Only two additional datasets were investigated.

DR's pinned catalog has263 sessions/85 mice, distinct from337 cached sessions and74 excluded outside-catalog sessions. The83 unspecified catalog sessions are retained as a stratum. Primary brainwide/behavior-pass is82 sessions/34 mice, then21 anatomy mice and18 same-probe paired metadata candidates. No single anatomical leaf reaches16; the ACAd/ACAv/PL/ILA composite was explicit before eligibility counting, rather than selected after leaf failure.

Independent recount from saved trial/unit metadata, without calling the implementation's block/support helpers, confirms **18 original mouse/session/probe populations**, six original blocks each, **72 context-half cells** with63–158 observations, and **14–378** qualified same-probe units. Every retained window in both contexts/halves is contained in each counted unit's provider support intervals. Recomputed scheduled within-block positions match the source field everywhere in the selected sessions (zero mismatches). Selected unit identity fields are present and session/probe/animal identities match. No context-specific unit list, cross-probe pooling, fabricated physiological admission or outcome-dependent animal ranking was identified.

## Scientific assessment and precise interpretation limits

**INCONCLUSIVE_METADATA is appropriate.** DR18 is an upper bound before prospective physiological QC, not an admitted neural cohort or a recommendation for activation. Exact scratch-data license and per-candidate continuous running/pupil availability/alignment remain critical unresolved metadata. Source ETags/pinned code/decoded hashes do not make a mutable scratch bucket a fully immutable neural release; public access/code licensing do not supply the missing dataset license. Observation intervals are provider recording-support annotations, not hardware packet-completeness or new spike-endpoint measurements.

Context labels are experimentally scheduled, not measured mouse belief or neural-inferred states. Repetition of both contexts and marginal stimulus/response/reward support does not eliminate drift/order, reward-rule, motor/arousal, stimulus or batch confounding or establish joint overlap/causal identification. Current response/reward outcomes are descriptive checks; later causal predictors may use them only after actual timestamps. P13 exposed final observations and fitted results are not new P14 confirmation. No dynamics/ontology/CWP/NAP conclusion is supported by metadata.

Two precision limitations should remain explicit in the narrow prospective revision and later M1 freeze:

- Current IBL common-support output counts **10 string encodings but9 distinct numeric signed-contrast values**, because -0.0 and0.0 stringify differently. Independently confirmed this for all eight selected mice. Existing report language discloses strings and no admission threshold uses this diagnostic; it must not be interpreted as ten physical numeric contrast levels. Canonicalizing numeric zero before display/grouping is a nonsemantic reporting correction and should receive a regression and fresh saved-output comparison.
- Provider-good/is_qc_pass is preexisting source/release-level curation, potentially computed across the full session, not new A/C-only physiological QC. The inactive proposal's future prohibition on D-derived unit selection must distinguish retaining that frozen provider filter from any **newly calculated** calibration-only QC, and disclose the resulting selection condition. M0 supplies no claim that provider QC was derived only on C and grants no future neural access. This is a future protocol/interpretation boundary, not an already passed physiological gate.

The inactive M1 specification otherwise preserves a conditional18-candidate9+9 proposal/8+8 surviving floor, same-population contexts, calibration/scoring separation, strong context/history/nuisance baselines, matched nominal D/C readout accounting, explicit assumptions and finite null-definition/validation prerequisites. Open QC/null/source definitions are honestly future freeze requirements, not implemented experiments. Prompt2 cannot use this M0 verdict to activate neural M1–M7. No automatic continuation or new dataset search is authorized.

## Exact upstream whitespace preservation

The three named upstream README snapshots in WHITESPACE_CLASSIFICATION have exact hashes in both metadata and payload freezes; independently checked all three. Preserving their native whitespace is appropriate source-evidence handling. A later Git gate may exempt only those exact hash-bound files while checking every other mission file normally and preserving complete index/remote byte checks. This is not permission to normalize source evidence, waive other diagnostics or claim an unexecuted stage/push/readback. The actual Git receipt remains a separate future gate after the P1 repair/review.

No additional P0/P1 scientific denominator, unauthorized-access or false-feasible-verdict defect was identified. The report-history P1 prevents accepting the current frozen candidate; its repair must not alter thresholds or hide unknown metadata. Only this review and the requested machine-readable review JSON are written. Failed experiments/reviews, existing P1–P13 history and the current inconclusive scientific verdict remain unchanged.
