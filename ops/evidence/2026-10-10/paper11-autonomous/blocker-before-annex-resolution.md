# P11 M2 Blocker Evidence

candidate_exit: NEED_ENV
blocked requirements: R02/R03 exact observation provenance; R04-R08 and R13 full
paper reproduction depend on the scientific M2 gate. Complete manuscript R09
cannot be satisfied by the explicitly incomplete draft.

Observed: M2 count extraction passed actual data checks, but the exact per-unit
trial-array coverage inventory is unavailable. All 23 selected-session original
NIX sources are absent locally. Three provenance-recorded/pinned GIN endpoints
returned HTTP 403. Published derivative cardinality alone cannot prove exact
trial membership, uniqueness, units and schema. No neural coverage corruption is
demonstrated and DATA_INSUFFICIENT is not asserted.

Evidence: paper11/results/M2/coverage_audit.json, coverage_access_evidence.json,
gate_result.json, tests.txt, QC_REPORT.md; pinned source_audit converter blobs.
Latest true M2 gate is FAIL; execution NEED_ENV. Initial extraction-only PASS
is retained and superseded, never used to start M3.

Alternatives inspected: current workspace raw-file inventory; all primary
receipt/provenance files; pinned converter; Git tree for equivalent inventory;
NEMAR JSON metadata/availability report; exact 103-byte annex pointer via blob API;
GIN pinned source, DOI and upstream master aliases. No equivalent inventory or
documented usable storage mirror. Companion iEEG cannot supply sorted-unit array
coverage. Different-task DANDI cannot replace the frozen primary dataset.

Required missing item: 23 original NIX metadata sources with SHA256 matching
acquired subject *_sessions.tsv, or an authoritative equivalent exact coverage
inventory bound to those sources (not a manually invented inventory).
Restoration: provide original files under paper11/raw/NIX/; execute
paper11/scripts/reproduce-m2.ps1. The implemented audit checks metadata/schema only,
never loads spike values or array lengths. An inventory-only alternative needs a
prospective validator; it cannot silently skip integrity checks.

Self-check: safe local coverage/code tests complete; no source or available
session can derive absent array identities from aggregate counts. Replacing
missing coverage with zeros would weaken the approved real-observation contract.
Further model fitting would bypass the failed scientific gate. No remaining
safe autonomous analysis can unlock M3 without real coverage evidence.

Secondary tooling: CLI wrapper's unsupported approval flag was adapted without
changing sandbox/approval policy; configured model then rejected by installed
CLI. A subsequent external-model retry was blocked by auto-review for potential
workspace/neural payload disclosure. That path was not bypassed. Local apply_patch
implementation and real local tests completed instead. No need for external
model-service approval to restore the coverage dataset. A metadata-only request
initially flagged as possible whole-HDF5 download was replaced only after proving
the requested Git blob is an exact 103-byte pointer; no signal download occurred.

Scientific alternative: preserve conditional descriptive QC and publish no
preferred-regime claim until coverage is restored. No bin-width/holdout/ontology
amendment was made. Next step after unblock: rerun M2 and advance only on PASS.
