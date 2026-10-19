# Saved reproduction fixture correction

Classification: TEST_BUG. `SAVED_REPRODUCTION_1.log` and the complete diagnostic package at that point are preserved in `REJECTED_SAVED_REPRO_1_CANDIDATE.zip` with its hashed receipt.

The source `Journal.append` serializes each component immediately. `Inspector.record` separately deep-copies its receipt entry. The saved verifier used `rows.append` on the mutable emitted dictionary, so its first pending alias row changed when the local resolver later updated that dictionary. All33 immutable Inspector rows already exactly matched the native receipt and native JSONL. The in-memory emitter in the verifier now deep-copies at emission to model immediate serialization. The three-way equality assertion is retained unchanged and passes.

Only saved verifier fixture behavior changed. No source inspection code, registration, scientific definition, recorded source result or prereviewed test was edited. New synthetic float32-rotation regression retains the original schema failure even with valid alias, units and shapes. Second saved PowerShell reproduction passes without network or dataset values. No retry of the one-shot source inspection occurred.
