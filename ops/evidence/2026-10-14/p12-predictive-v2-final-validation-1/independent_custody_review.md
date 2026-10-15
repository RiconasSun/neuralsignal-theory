# Independent custody prerelease review

Reviewer: separate agent `/root/final_custody_review`, read-only review requested by the human final-validation mission. No protected payload, key, count array or final score read; no fits, release, edits or experiments. Agent review is not an independent human custodian.

Decision: **HOLD — critical release gate is not implemented or verified.**

P1: `paper12_custody1/amendment.json` release rule requires independently enforceable authorization, exactly one evaluated final release and an append-only ledger. It explicitly prohibits self-asserted gate approval. `ROLE_POLICY1.json` retains this boundary. `paper12_m4offset1/launch_phase.py::native_run` strips the archived launcher's original guard prefix and relies on its caller. It is a restricted-process launcher, not a final-release controller. `paper12_predictive_v2/launch.py` authorizes development preflight only. No artifact-bound final entitlement/consumption controller or denial proof is present.

Required for a future separately registered implementation:

- Independent artifact-bound verification of frozen source/protocol, prerelease reviews and successful frozen C calibration.
- Atomic exclusive durable consumption of the unique D entitlement before any D decryption or analysis read.
- Fail-closed duplicate, concurrent, interrupted, tampered and mismatch handling; interruption must not reset entitlement.
- C-only export/runtime without D payload/key grants, followed by separately scoped D execution with frozen C states.
- Fresh actual native-principal access probes, ACL/manifest integrity and cleanup receipts.

Historical D non-exposure is supported within the registered threat model. All 13 final public M2 receipts match frozen gate SHA256 values, contain only C/D compartments, calibration-only QC, and false scientific-exposure/evaluation/raw-vector flags. `paper12_resume1/development.py` filters development mice and decrypts only A/B. Source, custody provenance and export/role manifests support restricted-role separation; public boolean flags alone are insufficient.

`paper12_custody1/custodian.py` previously decoded full-session target-unit timestamps under trusted custody and encrypted C/D separately. Therefore claim only D not exposed to the restricted scientific role, never D never decoded globally. No malicious-controller protection or independent human custodian is established. Fresh final access enforcement remains unverified.

No irreversible historical leakage was demonstrated. The missing prospective controller is an implementation gap. The human instruction says STOP on any critical prerequisite failure; do not release C or D in this mission.
