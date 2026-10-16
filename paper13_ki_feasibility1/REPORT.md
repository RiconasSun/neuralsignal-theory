# KI/PFC bounded metadata feasibility

Mission: `P13-KI-PFC-METADATA-FEASIBILITY-1`.
Base: `54f4bb572c33b11937b1939b4e643fda5269f58c`.
Overall scientific decision: **INCONCLUSIVE_METADATA**. No cohort is scientifically admitted. No spike-array values, waveform/LFP/EMG signal samples, predictive scores or model fits were accessed. M1–M7 and final evaluation were not started. The old IBL M0 failure remains unchanged.

## Fixed sources and bounded scope

The two user-specified releases were audited separately: [DANDI001260/0.250911.0744](https://dandiarchive.org/dandiset/001260/0.250911.0744) and [DANDI000473/0.230417.1502](https://dandiarchive.org/dandiset/000473/0.230417.1502), both declaring CC-BY4.0. The [pfcmap source](https://github.com/hejDMC/pfcmap/tree/9ae52eddc47fbb590ef4e1b1949507334707a0f1) is pinned to `9ae52eddc47fbb590ef4e1b1949507334707a0f1`, BSD2-Clause. Its exact recording metadata workbook and15source/license/configuration files were preserved. The provider README points to preprocessing [Zenodo14205018](https://zenodo.org/records/14205018), CC-BY4.0; that documentation source concerns these same recordings, not another candidate dataset.

The [official PFC-map article](https://www.nature.com/articles/s41593-025-02190-z) describes anatomical registration to CCFv3, manual curation and unit screening, drift correction between acquisition clocks, saturation removal and3s pre-tone selections with sleep-like/lick exclusions. These are source methods, not newly established P13 physiological findings. The actual journal publication date is20January2026 despite2025in its DOI. P13 does not reproduce its firing metrics, clustering or conclusions.

`REGISTRATION.json` prospectively fixed metadata tiers5/8/10/20, region labels and source bounds before new KI header values. Tiers measure anatomical population availability, not good-unit admission. The analyst proposed8units and120three-second epochs as a modest future design, explicitly not a universal scientific cutoff; no old20unit/400trial admission was inherited. No recommendation was relaxed after observing these counts. All11provider PFC-associated labels and all task strata are retained, including MOs without claiming a universal PFC anatomical definition.

## Exact animal, session and probe denominator

| Release | Files/probes | DANDI raw subject labels | Reconciled independent animals | Session dates | Units in NWB tables |
|---|---:|---:|---:|---:|---:|
|001260|74|43|41|50|20,374|
|000473|25|25|25|25|9,408|
|Total, without pooling analyses|99|68|66|75|29,782|

The primary contains two animals exported with suffixed subject labels:518804_1/_2 and560171_1/_2. Original recording IDs, different recording dates and the public source workbook corroborate each pair as repeated recordings of one animal. Raw labels are retained alongside canonical identities. Multiple probes on one session are simultaneous populations, not extra animals; no probes were pooled for a tier. Across the two specified releases, no canonical animal, original session/probe identity or recording is shared in this metadata reconciliation. This is a public-identity check, not a private reidentification guarantee.

Primary task strata are separately retained: Passive10animals/13sessions/20probes; Context8/8/14; Detection10/12/15; Attention4/8/15; Opto3/3/4; Aversion6/6/6. Animals may appear in multiple strata, so these animal counts must not be summed. The secondary is25animals/25sessions/25probes, all Aversion. No passive/aversive or cross-release observations were pooled. No individual primary task stratum has16animals before anatomy or quality exclusions. This conclusion does not say that all possible future multi-context protocols are impossible; combining experimental settings would require an explicit new scientific design.

All99recording identities,66animal denominators,29,782unit identities/electrode mappings, basic epoch identities and308region×task×tier rows are saved. Schema metadata includes dataset names/shapes, but forbidden neural array values were never decoded. Unit-to-anatomy mapping uses the NWB DynamicTableRegion electrode row, preserving the original laminar label. Provider registration is not independently re-localized histology.

## Single-region coverage

These are raw anatomical upper bounds, before independent quality admission. Every number is a distinct animal with the tier on one probe.

| Candidate/task | Region | ≥5units | ≥8 | ≥10 | ≥20 | ≥8 plus ≥120 basic3s epochs | ≥8 plus ≥120 matched provider-active pure-tone epochs |
|---|---|---:|---:|---:|---:|---:|---:|
|001260 Passive|PL|5|5|5|5|5|4|
|001260 Passive|ILA|4|4|4|4|4|3|
|001260 Passive|ACAd|5|5|5|5|5|4|
|001260 Passive|ACAv|2|2|2|2|2|2|
|000473 Aversion|PL|20|20|20|20|20|15|
|000473 Aversion|ILA|14|13|13|10|13|9|
|000473 Aversion|ACAd|17|17|16|14|17|12|
|000473 Aversion|ACAv|1|0|0|0|0|0|

The complete table includes ORBm/ORBvl/ORBl/AId/AIv/FRP/MOs and every primary task, not just favorable regions. No primary Passive single region or pooled medial-PFC population can supply8+8animals because the entire Passive stratum has only10animals. This is an analyst-examined stratum, not a user-selected or explicitly registered exclusive primary route. It cannot establish release-wide pre-tone insufficiency. A broader nonaversive multi-context design remains unassessed, with quality/exclusion and scientific-context decisions unresolved; no observations were pooled or cohort admitted. A pooled-region design is neither needed nor justified as a substitute for the secondary PL anatomical upper bound. No region or cohort was formally selected and no mouse split was allocated.

## Genuine epochs, clocks and exclusions

Each pure-tone onset is identified from explicitly named kHz/puretone stimulus timestamp series; colored-noise and optogenetic events are not silently relabeled as pure tones. Basic candidate windows are[tone−3s,tone), finite, mutually nonoverlapping, within the LFP sampling start/rate/shape support inferred only from public headers, and outside supplied spike saturation intervals with the source's±1s padding. LFP samples and spike endpoints are never read to infer recording duration. Curated header support is not a hardware-packet completeness certificate or proof that every potential acquisition gap was annotated.

We inspected the1,928,203,597byte preprocessing ZIP using its central directory and selected only the documented `timeselections_quietactive/*__TSELprestim3__STATEactive[__all].h5` metadata members. The3,918entry directory and168interval-only members were obtained with1,641,805transport bytes, not a full archive download. Their99distinct recording IDs match this inventory. Interval endpoints and provenance attrs are retained; full archive MD5 and full NWB object checksums are **not locally verified**. Received-range SHA256s, immutable release/asset identities, object sizes/ETags where supplied and saved-metadata hashes are preserved. Zenodo's fixed content endpoint supplies no ETag, so its exact published record/path and declared checksum are recorded without pretending a full checksum was verified.

Provider-active windows are matched to actual basic pure-tone windows within1microsecond. Windows include noise-aligned selections in the original source; these are not counted as pure-tone matches. Four selected recording sources explicitly use `quietdet_src=ignore`; these cannot certify wakefulness. Other sources may borrow quiet masks from another simultaneous probe, which needs session-level clock and dependency accounting. The workbook has record-level usability/exclusion fields, including blank/ambiguous entries; absence of a run marker is not converted to PASS. Source creator hashes `c98dc19961b11cb802e1651aad425e7da11b69c2` and `6f731e4edbb569e332483055f5ab1f860f0c9263` are preserved, but neither resolved in the specified public pfcmap repository. The current visible script and historical interval creation must not be claimed byte-identical without that mapping.

The NWB `quality` metadata has two numeric columns described as“ISI violation, false positive rate.” The first column includes integer-valued summaries, not an established per-unit violation ratio; there is no categorical good flag. We do not infer the manuscript's ratio threshold from this undocumented transformation, read cumulative spike indices to reconstruct counts, or label all29,782units physiologically eligible. Precise eligible-unit schema/IDs and source preprocessing/QC provenance remain essential gaps. The detail and affected recording IDs are in `essential_metadata_gaps.json`.

Movement/lick event timestamp availability and public quiet/active selections were inspected; raw behavior samples were not loaded. The availability of a signal or historical mask does not establish causal movement covariates at every scoring bin. Future unit QC and scalers require training/calibration-only rules. Historical spike-derived state masks define a conditional curated-release estimand, not online outcome-independent sleep detection.

## Decisions and methods feasibility

- **001260: INCONCLUSIVE_METADATA.** Its Passive stratum is DATA_INSUFFICIENT, only10animals before regional screening; every other individual task stratum is also below16. These separate ceilings do not disprove a later explicitly defined multi-context pre-tone design. No such combination was scientifically evaluated or admitted here, and passive/aversive pooling remains forbidden. The corrected machine-readable audit distinguishes the stratum-level negative result from the broader candidate verdict.
- **000473: INCONCLUSIVE_METADATA.** PL has20raw anatomical animals and ACAd17at the8unit tier. However, quality admission is unresolved. Under the120epoch recommendation only15PL animals have sufficient matched provider-active pure-tone epochs, before fully verifying exclusion provenance.120was a proposal, not permission to declare biological impossibility at every other sample rule; it is not relaxed to rescue this mission.
- **Overall: INCONCLUSIVE_METADATA**, no `FEASIBLE_SINGLE_PFC_REGION` and no automatically promoted pooled design.

Rate/history/context Poisson models, exact-forward2state Poisson HMMs and low-dimensional fixed-timescale causal history readouts are analytically tractable candidates for verified data. This is a mathematical design assessment, not evidence of optimizer convergence or prediction. Nulls must preserve context/epoch/animal structure; aversive pre-tone prediction cannot establish passive or choice-related mechanisms. Existing CCPN numerical modules are not reused without separate mathematical/data-contract checks. No old recurrent rescue or crypto-custody machinery was introduced.

`design_proposal.md` gives the proposed anatomy, independent-mouse and unit/epoch minima, causal features, strong baseline families, complexity counts, partition logic, numerical/falsification gates and one-final-evaluation safeguards. It is conditional and **NOT AUTHORIZED FOR EXECUTION**. There is no admitted prospective P13-v2 roster or frozen final evaluation in this mission.

## Handoff and exact next evidence

Before any separate P13-v2 authorization, obtain a source-verifiable mapping from NWB quality columns to eligible unit identities; reconcile the public interval creator versions, record-level exclusions and `ignore` cases; and approve an explicit single-task secondary scientific estimand with justified epoch/admission/partition rules. Supplied masks were recovered where available; they are not simply reported as missing. No author was contacted and no additional dataset was searched. No private key, entitlement system or protected P12 source is needed.

Saved-only reproduction and independent internal review records are documented in the mission evidence. The original pre-review audit is retained in results/final/; corrected active outputs are in results/review1/, with identical numerical coverage/epoch counts and a corrected scope label. Commit/push/remote-readback/clean closure remains pending until the actual external Git receipt exists; this precommit report does not certify those future operations. A completed metadata audit does not equal a feasible scientific cohort or a completed P13 paper. No manuscript/PDF, final scores, hypothesis tests, biological nulls, causal mechanism, NAP/CWP proof, human validation, external-laboratory confirmation or journal submission is claimed.
