# Independent internal P16 R3 M2 A-only preaccess review 1

Mission P16-M2-M5-NEURAL-QC-AND-DEVELOPMENT-R3; exact owner BASE/current candidate base8801b945004cda0dd7ecd9ddde1daaa507414a96. Candidate PREACCESS_FREEZE_2.json, revision2,28 files. This is an independent INTERNAL source/physiology preaccess review, not external peer review or M3-M5 certification.

**Decision: NOT_ACCEPTED_R3_A_ONLY_NEURAL_PREACCESS; open_P0=0; open_P1=1.** Do not issue ACCEPTED_R3_A_ONLY_NEURAL_PREACCESS or begin live neural access on this candidate. Preserve this failed review before repair. No frozen source/scientific file was changed by the reviewer.

## P1: the persisted48h deadline can reset across a normal machine reboot

transport.guard compares only current time.monotonic() with persisted start_monotonic/deadline_monotonic. run_m2.supervise persists start_UTC but neither guard nor the child supervisor checks elapsed UTC or an originating boot identity. time.monotonic has no portable persistent epoch across a Windows restart. The check now<start detects only some resets; if the new uptime is above the old start but below the old deadline, the old monotonic values appear valid.

A completed first source and its accepted first-source evidence can persist while the host is off/restarted. The remaining phase then loads the original stage and may receive almost a fresh48h despite more than48h already elapsed. This conflicts with the owner48h maximum and registered one deadline including reviews/no phase reset. The external Job correctly enforces the supplied deadline within its own current execution, but cannot make a previous-boot monotonic timestamp an absolute deadline.

Pure synthetic counterexample executed with ResourceWarning treated as error, exit0:

```python
stage = dict(start_monotonic=100., deadline_monotonic=172900.,
             start_UTC=(UTC_now - timedelta(hours=49)).isoformat(), no_reset=True)
with patch('paper16_dev_r3.transport.time.monotonic', return_value=200.):
    guard(stage)  # returns successfully, although the original48h is exhausted
```

No source, real stage claim or child was launched for this counterexample. This is a normal host-restart persistence defect, not a demand for protection against a malicious machine administrator or a new custody system.

Required narrow repair: durably bind/enforce the same original absolute wall deadline across phases and detect/reject a changed/unusable monotonic epoch (or otherwise use a demonstrably valid persistent remaining-time calculation). Check it before source requests and child launch, as well as during the existing supervision. An expired UTC deadline or reboot/stale-clock state must fail closed; do not reset/rebase/extend the authorized48h. Add regressions for an expired original wall deadline with apparently valid monotonic values, clock/boot discontinuity, and valid same-epoch phases. Preserve all current evidence and repair prospectively before real access. No scientific model/QC/source definition needs changing.

## Other completed review evidence; these do not offset the P1

Independently executed:

`paper16_m1\work\runtime\Scripts\python.exe -W error::ResourceWarning -m unittest paper16_dev_r3.test_neural paper16_dev_r3.test_transport paper16_dev_r3.test_controller paper16_dev_r3.test_integration -v`

29 unique tests passed in5.719s; process exit0. Tests used only owned synthetic HDF5/HTTP fixtures and local synthetic Windows child/grandchild processes. Actual named-Job membership/assignment-before-resume and deadline descendant termination passed, including the Windows venv launcher/base-child arrangement. The source tests show other-unit nonfinite canaries are not materialized, B/E finite-value changes do not alter A physiology, and full-row unpartitionable nonfinite selected-unit timestamps stop. Partial source/candidate captures, no retry, exact ranged response/ETag/length, request-before-budget denial, optional observation handling, gap-local ISIs, zero-count retention, exact A boundaries and lowest-eight common-support STOP were exercised.

I independently checked every28 frozen file's byte size/SHA plus the freeze manifest SHA and that run_m2.REVIEW_FILES is a subset of the exact reviewed table. All333 baseline rows match the original owner's nonempty lines and line numbers exactly. The110 semantic oracles supplement rather than replace those obligations; later unexecuted stages remain open.

Public metadata-only checks reconcile28 unique original Development sessions/mice,5 BO/23 FC, original file IDs/ETags/sizes/probes/candidate ID lists versus frozen R2 and M0, and27 denied Final session IDs. For all1983 unique candidate certificates I independently followed provider unit peak channel -> channel probe -> probe session -> session specimen/mouse; verified the seven VISp acronyms, quality=good, amplitude_cutoff<=.1, presence_ratio>=.95 and isi_violations<=.5 and exact saved provider strings. These are upstream whole-session metadata screens, not executed A physiological admission. No real neural file or private other-paper source cache was opened.

Reviewed source/physiology implementation uses the exact selected-unit ragged slices and VectorIndex target identity, same-file canonical hard links, original root/clock/probe attributes, approved identity metadata and candidate peak-channel rows. The allowlist also blocks alternate h5py value APIs; storage chunk transport may contain unreturned bytes, a disclosed technical limitation, not unrestricted scientific access. Explicit unit observation intervals are intersected when present; incomplete/malformed/unknown observation representations stop. Absent optional intervals retain the original source-curated nominal-release observation limitation; no spike-extrema/file-existence support inference is substituted.

Original binary64 event/time preservation and half-open onset..220ms A QC windows are retained. Original A30-spike/20-occupied/.5-150Hz/20-pair/ISI<1.5ms fraction<=.02 rules, role/color A30/B8/E8 support floors, lowest-eight numeric IDs and one common-support check are retained. B/E source-observation metadata coverage is permitted by the frozen M1 rule; it is not B/E neural QC. Source errors cannot become physiological attrition.14/3BO/10FC remains the later actual cohort gate, not a result of synthetic tests.

The staged controller requires exact successful preaccess review/code/registration identities before real reads. It requires separately reviewed actual first-source receipts before remaining27, preserves source/candidate/phase claims and private native A captures, and denies Final and unknown phases.8GiB aggregate/512MiB source caps, bounded request/logical/row/memory safeguards, reserve-before-request/fsync partial ledger and no retry/redirect/bulk fallback are present. Raw/range/A files remain ignored/private. This is trusted-code compute containment; no OS principal isolation, third-party custodian or malicious-admin protection is claimed.

The R2_REUSE_VERIFICATION metadata/log records all28 accepted saved running inputs,19 R2 synthetic tests,357 R2 and492 prior hashes, and25182 source-valid scored bins. Its manifest/receipt identities agree and source_inputs calls only the pinned metadata utility and saved-state path, not the R2 acquisition. I did not reopen real running/neural arrays or replay R2 acquisition for this review. Saved running support is not represented as neural observation validity.

## Review boundaries

Only metadata/public-source documents and synthetic owned fixtures were read/run. No live source HTTP, real NWB/neural arrays, real B/E/Final neural observations, model likelihood, fitting, B selection, E assessment, Git mutation or approval creation was performed. No first-source or full-cohort M2 scientific PASS is issued; no M3-M5 readiness is certified. The next step is the bounded deadline repair and affected fresh review while live neural access remains closed.

## Complete frozen identity table

Every row below was freshly byte/hash checked against the supplied manifest; paths are repository-relative. The final row binds the manifest itself.

| File | SHA256 |
|---|---|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/BOOTSTRAP.json |8b5a911d05aa1326c9316031903cbcb04764b8af0143a543715b87908365b56b|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/goldenstandards.md |9280d54528d22409a0f8e5434e8266400b2e28280c0b05f70afe56eded5f5151|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/OWNER_REQUEST.txt |898e7a534682d631546b9012765601f03851ff4c847dcf0930fde5946da288fe|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/R2_REUSE_VERIFICATION.json |4bcb0aa7123cd2ad5b93be8d0b8a217517700401bb2e74c5359505a909764c50|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/R2_SAVED_REUSE_1.log |6cfc9791824f6ec481a769ad064f678f6f08c4fcbb58a02ea1c118b4789686ed|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/REGISTRATION_ASSERTION_FAILURE_1.json |33a5889523fe442cfa897f43e6357fe320f9c27857d492b38683f9b1a62a3a14|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/REQUIREMENT_BASELINE.json |48adb70b27fb63230e38f74173d54afc022549c5bf71d80977b74d3ce8ca23a4|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/SYNTHETIC_PREACCESS_FINAL.log |67068647f9ae3f3abed0560b3b6e0b687801b05fc69df0094a6f5f638f3c86d8|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/TEST_DISCOVERY_NOTE.json |e8556144af9969ac98351623fd56a6404b0551c1049f41bdafad9d7466c6cb82|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/TOOLING_RECEIPT.json |2d06fced1372eb1898d9bf07ad2202ff154f6af302db1dd6bcbd13f9cf1934b2|
| ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/WINDOWS_SUPERVISOR_REGISTRATION.json |2d1c903b01215101ba3b6a2cb3e49ac1addd3cb629e322eed419f6ecaad881bf|
| paper16_dev_r3/.gitignore |49c03ed3cea6e6960d782305d5593f03f2a9d0ce92a8856864eac4e2dde9db01|
| paper16_dev_r3/ACCESS_REGISTRATION.json |46b82494acb60da70e8804bcad06e380690f57ac648d2568549989ef944f0cc9|
| paper16_dev_r3/core.py |38e50860d544b5ee15a2e681b0dc2b84c0187485234bd55c0ef37b3aa305f627|
| paper16_dev_r3/MISSION_SPEC.json |43f2235e364f310ae42f07a0274852c24c907cfb48dfd4e0ece26f52ceb6d6b9|
| paper16_dev_r3/neural_reader.py |d99a380fbec20efabec91f13060c3bbb5e9db9e182a911c6a12ac2deb6286be7|
| paper16_dev_r3/run_m2.py |cdf855e144415d70f1ccf1ff74bd2ed47709de9ff2485579b9c26c75383ee172|
| paper16_dev_r3/SEMANTIC_ACCEPTANCE.json |838fe8cbc4e69c8d0a9d7a7cc3156bfdbde48f882f3d846d1f3f0d5eb502410e|
| paper16_dev_r3/SOURCE_ACCESS_PLAN.md |4b69820d7988ba97a88629666613b9d3d329866c03fe86b0de8949301b10b149|
| paper16_dev_r3/SOURCE_CANDIDATE_CERTIFICATES.json |7ce107a03b3a5933dbd3d1eaee4753ba746ab7bfb1b6eea2f5fc59c6142e5df4|
| paper16_dev_r3/test_controller.py |9a7ed0a34f4c8791b17eb85a231c18861e9c60245f4820d20b089964bcce53e5|
| paper16_dev_r3/test_integration.py |ca54a17e72456ac98256364e34ad1e61ce1d296725ddf8b81b237812a31b3133|
| paper16_dev_r3/test_neural.py |9d148ea985e16a2e571064e448047d5700dac13f58a85f5a6485b08f15ab04ec|
| paper16_dev_r3/test_transport.py |c2f6eb1f48ccd63aba3335432c9488bc1325e3cabf8bc54a2ab0492d4a99a5ca|
| paper16_dev_r3/transport.py |0e5ee2594ef00d576af5718153f21fa25d684d154c7e39a41574ee6dc47b7c50|
| paper16_dev_r3/windows_job.py |8fbe70bb6083177ea5a57b64b77ec7902e6735d2add2010206d2e364f43058af|
| paper16_dev_r3/README.md |a629c5f25b77199d74ec586bc27fbecafdd8e64a350462274015e559de975ac1|
| paper16_dev_r3/PREACCESS_FREEZE_1.json |c4db2ac4941c140f20504bd6adf3028fafb872b6f676c9a7657aef1bd1a88eb5|
| paper16_dev_r3/PREACCESS_FREEZE_2.json |ebaa47301f3f3a9a0fb2872f8dcbb5fe86a9191c23c4a78728ec3b23921f06c2|
