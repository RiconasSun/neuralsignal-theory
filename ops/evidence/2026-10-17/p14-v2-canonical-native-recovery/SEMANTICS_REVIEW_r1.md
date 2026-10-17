# Independent canonical-native semantic review r1

Mission: P14-V2-CANONICAL-NATIVE-RECOVERY

Decision: ACCEPTED_SAVED_METADATA_AUDIT_SEMANTICS_ONLY. Open P0: 0. Open P1: 0. This review does not certify all 13 sessions, actual cohort capacity, source observation validity, M1 completeness or neural activation.

The reviewer inspected stable audit.py/test_audit.py, the registered canonical-native contract, relevant official documentary snapshots/receipts and the first three completed whitelisted metadata exports: CSHL049 (asset9e27ec60-e8d9-4dcf-a9a4-4b8acb6265ef), CSHL058 (assetd73bceb9-a019-4d1c-aa36-41edef0022a0), and CSHL060 (asset5a66e6f2-bf16-43b8-9c78-65875dd0c401). Review began while the bounded remaining metadata audit was in progress. No full-cohort capacity computation, new network request, raw cache/NWB read, neural value/shape access or raw behavioral signal access was performed by the reviewer. No implementation was edited.

## Canonical task and anatomy semantics

The task audit uses only canonical event, context and stimulus fields. Original runs and the chronological half cut are constructed before exclusions; neutral/nonprimary rows break runs. The 0.5-second window and registered finite event ordering, qualifying-run and context/half cell floors are preserved. Historical bwm/saturation flags and movement cannot change the computed task-validity masks. Task-valid windows remain explicitly distinct from observed, artifact-valid neural windows. No prediction feature is constructed from future feedback or outcomes by this metadata-only audit.

The unit audit follows canonical max_electrode row indices through canonical localization localized_entity entries to brain-region and probe labels, checks internal probe consistency, finite electrode coordinates, unique unit IDs/UUIDs and the registered provider quality criterion. Exact regional descendants are used, and the frozen historical probe is selected case-insensitively without pooling. Conflicting canonical localization tables raise instead of selecting a favorable mapping. These are metadata capacity checks, not physiological QC or proof of the exact historical converter/sorting writer. No historical unit/QC/atlas equality is required for this new route.

## Observation support is an inventory, not an automatic certificate

`support_inventory` never promotes a present field to PASS. Missing fields remain UNKNOWN; present observation/artifact fields require a later clock, scope and completeness review. Its null source_support_eligible is an unresolved status, not a zero-capacity count. The current run-level SOURCE_CONTRACT_INCONCLUSIVE output is a conservative preliminary source decision, not a general certificate engine. If authoritative evidence is found, it must receive independent semantic assessment before any source decision is changed; the inventory alone cannot reject or certify it.

In the three inspected exports, the available interval tables are trials and epochs. The inspected whitelisted metadata contains neither unit observation intervals nor canonical valid/observation interval tables, nor invalid/artifact/bad/saturation intervals. The available protocol/description/group-attribute prose does not supply probe/unit-specific recording support or complete artifact annotation. Thus recording support and artifact validity are UNKNOWN for those inspected sessions. This is absence of proof at inspected paths, not proof of no artifacts or that no support could exist elsewhere in the release.

The frozen official session-epochs implementation describes the active task epoch as 0 to passive-protocol start and a passive phase thereafter. The metadata epochs description agrees. These are behavioral protocol phases, not a demonstrated per-probe recording-duration, interruption or artifact-free certificate. The official unit-quality description lists sorting metrics; provider-good status does not certify continuous recording/artifact validity. General session start/end and canonical file existence are likewise insufficient. Source-specific complete annotation/negative-annotation evidence remains necessary under the prospectively reviewed contract.

## Movement version interpretation

The official converter documentation snapshot at54030ac4eb40a74978ac1f6ef6e966278b9d3f34 documents a direct firstMovement_times-to-wheel_movement_onset_time mapping and a trials source revision2025-05-06. The fields concern the same broad operational quantity, first detected wheel movement. That documentary mapping does not prove identical extraction/reprocessing procedure, thresholds, handling of missing events, actual converter writer or per-file source revision across the historical BWM metadata and released NWB. The inspected asset metadata identifies DANDI metadata-generation software; it does not establish the exact converter execution commit. General wheel synchronization documentation is not per-session synchronization certification.

The observed historical differences therefore remain preserved version/processing differences of unresolved exact cause. No clock fault, harmless uniform offset or equality under a larger tolerance is inferred. The former 794 discrepancies and old bridge remain unchanged; movement stays excluded from new primary eligibility/predictors and movement/arousal-independent claims remain withheld. No raw wheel signal was read to reconstruct the event.

## Independent tests and remaining review boundary

The reviewer independently reran all34 metadata/transport/canonical audit tests with warnings as errors, Requests/socket network denied and no real-cohort computation. All passed, including772 historical hashes. Transcript: SEMANTICS_REVIEW_TESTS_r1.txt. Tests cover original cut/run retention, canonical-only masks, task-epoch and empty-annotation noncertification, observation-versus-artifact distinction, anatomy mapping and existing range boundaries. They do not certify neural numerical models or actual observation-support evidence.

The complete 13-session outputs must be reviewed after the registered retrieval finishes. No conclusion about all13, a canonical eligible denominator, DATA_INSUFFICIENT, or source-wide annotation absence is granted here. A critical support unknown cannot be cured by source-wide re-enumeration. No thresholds, masks, hypotheses or scientific definitions were changed during review. No MERGE_ALLOWED or scientific/neural PASS is granted.

Reviewed implementation hashes:

- audit.py: 33b6092b6c32568a78af907501e664253751500eac9f645258265a773b57d956
- test_audit.py: 6d13b2ca207b5808e1c8b8a942f0874f5ff653eae71e50250d878098fdd6cd1f
- canonical contract: a358b70ce89f1b4702df203fdc36c0480194b0d511be5a7d0e3499c084386af7
- trials documentary snapshot receipt: source SHA256 b78237d572ee51414b0f659458f4cc61f34d156c910ffa56876d0a722fbf15b7
