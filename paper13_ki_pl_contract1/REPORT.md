# Bounded PL data-contract decision

Scientific readiness: **PROTOCOL_READY_PENDING_NEURAL_QC**. The proposed target is A: local predictive activity of curated-release PL units in recording-supported aversive-task pre-tone epochs. This is a proposed, frozen contract; no study is activated and no animal has passed physiological QC.

| Scope, single PL probe, >=8raw labeled units | Independent mouse upper bound at120epochs |
|---|---:|
| Original raw anatomy |20|
| Original basic pre-tone |20|
| Original provider-active matched pre-tone |15|
| Proposed A after additional known LFP/manual exclusions |19|
| Provider-active after the same additional masks |15|
| Actually physiologically admitted |0|

The metadata-informed scientific reason for A is to test whether local discrete/continuous history representations add predictive information beyond rate/history/context in the available aversive-task population, without claiming state restriction. Choosing this target does not depend on predictive scores (none exist here). B instead asks a state-restricted question and is not interchangeable with A. It cannot support8development+8final at the unchanged120threshold; we do not lower either requirement or call B confirmed awake.

The source-backed NaN-empty saturation convention and the newly retrieved manual exclusion make a narrower contract defensible. Historical NWB quality formulas remain unknown, handled by explicit prospective operational training-only QC rather than pretending historical quality certification. The full proposal and stopping rules are in `PROPOSED_P13_V2.md`; exact25animal and6,155historical-basic-epoch dispositions are generated in `results/initial/`. No model fitting, real spike-value reading, cohort activation or final evaluation occurred. Original IBL M0 FAIL and prior KI INCONCLUSIVE are preserved, not reclassified.

See `QUALITY_PROVENANCE.md` for field semantics, reconstruction limits and future QC; `EPOCH_PROVENANCE.md` for intervals, masks, clocks and archive provenance; `CLAIM_AUDIT.md` for permitted claims. Run `reproduce.ps1` for saved-only tests, inventory validation and byte-identical output reconstruction. Evidence and independent review are under `ops/evidence/2026-10-15/p13-ki-pl-quality-epoch-resolution-1/`. Git closure is certified only by the actual external receipt, never by a planned push.

No essential metadata blocker remains for **this explicitly limited proposed target**. Historical formula/exporter or creator-hash gaps still prevent exact replication of published unit/state inclusion, which is not claimed. An optional shortest unsent source request is in the quality report. Future neural QC, complete numerical model tests and a separately authorized protocol activation remain mandatory before scientific execution. STOP after reviewed archive.
