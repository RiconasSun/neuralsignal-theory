# P14 M1 source-contract audit — activation stopped

Mission `P14-M1-SOURCE-CONTRACT-AND-PROTOCOL-FREEZE`; exact base `9cb5568be20821f5487d8987ff484201ecc22632`.

**Scientific decision: SOURCE_RIGHTS_BLOCKED.** The public evidence does not establish the applicable rights for all eighteen frozen scratch-cache sessions. The owner-requested Phase1 stop is retained. A complete executable M1 scientific protocol is **not frozen**, and Prompt3 neural execution is not available for consideration on this checkpoint. This is a reviewed source/metadata checkpoint, not M1 scientific PASS or M2 authorization.

No neural values, raw behavioral signal samples, model fits, neural scores, or final assessment were accessed. No external inquiry was sent. All104 frozen M0 payload hashes remain unchanged, including M0's INCONCLUSIVE_METADATA verdict and all historical limitations. P1–P13 were not modified. Eighteen remains a metadata candidate upper bound; physiological eligibility is unmeasured.

## Rights evidence and its limits

The [Allen Institute terms](https://alleninstitute.org/legal/terms-of-use) describe research/noncommercial reuse, limited scholarly publication, attribution duties and restrictions on commercial redistribution for covered content. The [citation policy](https://alleninstitute.org/legal/citation-policy) describes source attribution. Neither inspected text explicitly identifies these exact scratch-cache objects. This audit does not infer their applicability from a website footer or public access.

The [pinned dr-datacube provider source](https://github.com/AllenNeuralDynamics/dr-datacube/tree/366809a4b2b3f39a7f36e054a4650dd79faadbe2) maps datacube v0.0.289 to CodeOcean asset `4491d1c4-400c-4e76-b81a-c437478f188b` and documents the anonymous scratch-cache option. Its private asset fallback is a separate route. The queried public metadata filters for that CodeOcean identifier/version returned no record; this does not prove the asset does not exist or has no license. No credentials, private asset data or SDK fallback were used.

Official public asset descriptions explicitly mark corresponding canonical `aind-open-data` assets CC-BY-4.0. A version-specific query across the eighteen selected mouse identities returned seven conversion-v0.0.289 assets. **Three** match the original selected session date:741137_2024-10-10,743199_2024-12-05 and759434_2025-02-04. The other four concern different dates for the same mice and cannot replace the original sessions. `results/CANONICAL_VERSION289_ASSETS.csv` records every match and mismatch. No animal/session was replaced.

The first bounded per-session queries reached their eight-record page limits for some sessions. These receipts are retained; no absence claim rests on those truncated results. The later processing-version-specific query returned seven records below its100record limit, and the returned processing metadata was independently checked for version0.0.289. No inference is made that this is the complete DR public release or that other assets do not exist.

Object metadata for the three exact-date canonical assets identifies Zarr serialization; the frozen scratch objects are HDF5 `.nwb` objects. Available S3 sizes, ETags, dates and metadata hashes are recorded. They do not establish byte identity, complete conversion lineage or a rights grant for every scratch object. The source record's `source_data` linkage is incomplete. A canonical asset's license and MIT-licensed conversion code are not silently transferred to another bucket. Current result: **0/18 scratch-object rights bases verified**, not eighteen denied licenses.

`SOURCE_REGISTRY.json` gives the evidence paths. `SOURCE_RIGHTS_18.csv` records original session/probe identities, scratch object fingerprints and any exact canonical counterpart. The specific unsent request is `DATA_OWNER_INQUIRY_UNSENT.md`. Rights for secondary noncommercial analysis/publication and source-specific attribution/redistribution must be established before activation.

## Exact eighteen-session measurement audit

`results/SESSION_COVERAGE_18.csv` contains one row for each original mouse/session/probe, with no cohort expansion. All eighteen scratch NWB object names are present in a complete316object listing. This is availability metadata, not a neural read or integrity proof of their contents.

All eighteen have original task-event metadata and source unit observation intervals supporting the retained M0 windows. Such intervals do not certify hardware continuity, behavioral/neural clock alignment or A/C-only physiological quality. Current provider tracking metadata has one matching entry for each session. The parser's ephys/sync assumptions and default video inference do not prove the actual frozen conversion had usable running, pupil or clock data.

For the three exact canonical counterparts, only consolidated Zarr **metadata** was read: attribute names, shapes and types. Running, lick and pupil-area descriptors are present and nonempty. No chunk, neural array, timestamp array or continuous behavioral sample was read. Those canonical descriptors neither prove equivalent contents in the scratch HDF5 files nor establish alignment quality. For the original scratch targets, continuous running/pupil presence, realized sampling frequency, interruptions and per-probe clock residuals remain **UNRESOLVED**. No session is called NOT_RECORDED merely because evidence is absent. A low-pass filter cutoff is not a sampling frequency.

The exact `npc_sessions` v0.0.289 tag resolves to `36e3c4b698181f7fc7bae3f61b218eabe5f0a549`. Static code describes sync-dependent ephys/event timing, running conversion, conditional video/eye processing, and invalid-interval handling. Dependency ranges in its pyproject do not pin every package actually used for each conversion. Current `npc_lims` tracking is separately pinned and explicitly distinguished from the historical runtime. Generic source contracts are not actual session clock-quality certificates.

An additional task-event limitation is preserved: **five** original usable trials across **four** sessions have `is_response=True` with nonfinite `response_time`; all flagged reward events have finite reward times. See `MISSING_RESPONSE_TIME_EVENTS.csv`. The versioned converter defines response_time as the first observed lick inside the response window and can warn when its behavior outcome flag disagrees with sync events. The four affected sessions are later than the documented historical pre-October2023 bug boundary, so that old bug is not asserted as their explanation. No missing event time was imputed from a future outcome flag; no original trial mask was altered.

## Scientific scope retained and work held

The narrower question—whether incremental prediction differs by scheduled context conditional on the task variables actually measured—could remain worthwhile. It cannot establish movement- or arousal-independent dynamics, even if a future interaction is significant. `INTERPRETATION_BOUNDARY.json` records this restriction. Current source rights and critical alignment evidence still prevent activation; narrowing language does not clear them.

The original anatomy, context definitions, six-block structure, populations and metadata masks remain unchanged. `results/RESERVED_ALLOCATION_9_9.csv` records the original proposed SHA256(`P14-V1|mouse_id`) deterministic9/9 identity reservation. It is locked as a metadata identity artifact in this archive, with no swap/refill policy, but is not an active scientific protocol. Neither arm has a measured physiological denominator. Actual selected unit identities, operational A/C-QC, complete model equations/counts/budgets, statistical/null definitions and final assessment policy have **not** been promoted into a complete M1 freeze after the source stop. Their original requirements remain individually blocked and traceable, not deleted or replaced by mock evidence.

The two intended primary interactions remain the owner's discrete and continuous aud-minus-vis incremental LL contrasts relative to mandatory B4, with equal-mouse paired two-sided inference. B0–B4, two-state causal HMM and two-dimensional continuous history remain requested scope. The inactive M0 proposal is preserved; it is not substituted for the complete M1 specification requested here. No P13 coefficient or failed self-exciting Bstar null was imported. No family is presumed superior.

The remaining protocol phases require source/clock resolution and a resumed M1 freeze before any Prompt3 consideration. Do not weaken missing-event/clock requirements, fill missing samples, switch dates, add MOs/orbital units, or call the canonical subset an eighteen-mouse replacement cohort.

## Verification and handoff

The simple source journal records85scripted HTTP attempts and6,537,665response bytes, within the registered100attempt/20MB/4MB-response limits. Eight initial sandbox connection failures were retained and successfully retried with the permitted network environment. The404OpenAPI lookup and503broad query remain evidence; narrower metadata filters resolved the factual queries. Browser discovery transport bytes are not observable and are not included in the measured script total. No external correspondence occurred.

Run `& .\paper14_m1\reproduce.ps1` from the repository root. It verifies every historical/new frozen hash, denies network, runs source/allocation/coverage oracles and recomputes the six saved metadata results in a fresh scratch directory. This is saved-only metadata reproduction; it does not validate unexecuted models or missing scientific gates. Independent internal source/metadata review and actual Git remote/clean receipts certify the checkpoint; neither constitutes external peer review or a completed M1 protocol.

**Stop after this M1 checkpoint.** Next required human action is to obtain source-owner clarification using the reviewed unsent inquiry, or separately authorize that correspondence. A rights answer alone never grants neural access: the remaining M1 source/clock/QC/model/statistical protocol and independent review must be completed before the owner can consider Prompt3.
