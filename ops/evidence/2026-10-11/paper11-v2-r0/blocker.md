# Blocker Evidence

candidate_exit:WAIT_FOR_HUMAN_INPUT
blocked_requirement:R0-02 prospective eligibility meaning and R0-08 cohort gate
observed_blocker:registered minimum40usable trials/session admits at most2
development subjects after protected old test exclusion, below minimum8.
evidence:paper11_v2/results/R0_final/gate_result.json and registration.json;
original split file opaque hash and allowlisted partition trial IDs; no counts.

Autonomous alternatives completed: all87 external files audited metadata-only,
actual schema/phase/patient-parser failures fixed in append-only versions,
36independent candidate external patients locked; frozen old train/validation
trial coverage audited; duplicate sessions grouped by patient; oldtest overlap
checks; archive integrity;20tests; PowerShell negative-result reproduction.
External candidate coverage cannot replace the development cohort condition.
Combining sessions as independent subjects or including old test violates the
contract. Recovering/installing software cannot create additional usable
trial IDs in this pinned cohort. No install/auth/CLI workaround can solve it.

Material decision:initial minimum valid-trial denominator was under-specified;
conservative usable-trial meaning has been retained, not changed to get PASS.
A lower criterion changes the registered acceptance oracle and requires human
approval. Original and schema-only R0 evidence must stay separate from the
combined failed gate. Original v1 evidence is immutable.

Exact minimal action:decide to retain the criterion and stop, or authorize a
separately registered v2 usable-trial amendment (for example minimum32 with
>=24train/>=8validation) before neural/model outcome access. The latter is only
a metadata upper-bound9patient alternative, not a power/QC/PASS guarantee.
Next step after approval:prospective amendment, rerun combined R0 integrity and
adequacy gate, then R1 only if every R0 requirement passes. No final unlock.
