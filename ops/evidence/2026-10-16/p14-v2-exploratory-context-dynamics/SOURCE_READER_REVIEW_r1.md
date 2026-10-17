# Independent source-reader review r1

Mission: P14-V2-EXPLORATORY-CONTEXT-DYNAMICS

Decision: CHANGES_REQUIRED_BEFORE_REAL_SOURCE_READS.

This is a narrow implementation/source-boundary review. It is not a source compatibility PASS, scientific protocol acceptance, cohort certification or neural-access approval. The reviewer inspected OWNER_MISSION.txt, all 85 baseline requirements, SOURCE_REGISTRATION.json, SOURCE_AUDIT_ROSTER.json, source_metadata.py, test_source_metadata.py and SOURCE_TESTS_r1.txt. No network request, real NWB/cache inspection, neural values, behavioral signal samples or unrelated historical neural bundles were accessed. No implementation edits were made.

## P1-001: Redirect destination is checked after network contact

`paper14_v2/source_metadata.py:105-108` passes `allow_redirects=True` and checks the resulting response/history hostnames only after Requests follows redirects. An unexpected Location can therefore already have been contacted before the allowlist check raises. This does not implement the registered official-delivery-only request boundary. Validate HTTPS, destination host and each redirect target before following it, using explicitly bounded manual redirects. Preserve range headers, exact response checks and bounded retry semantics. Regression must prove that a disallowed target receives zero requests, including an unapproved intermediate redirect, with no bulk response body consumed.

## P1-002: Cached bytes are not bound to their requested offset

`paper14_v2/source_metadata.py:87-91` verifies content digest, asset, size and byte length, but omits the receipt's `start` and `bytes_requested` fields. Copying an equal-length cached byte file together with its valid receipt from another offset of the same asset into the requested cache filename is accepted. The returned bytes then need not describe the requested HDF5 offset, violating exact-range provenance and potentially corrupting metadata interpretation. Require receipt coordinates to match the requested start/length and retain the exact response Content-Range binding. Add equal-length wrong-offset receipt/payload swap regression; ordinary digest corruption alone is insufficient coverage.

## Existing evidence and limits

The saved SOURCE_TESTS_r1 transcript reports **14 tests**, not 15, all passing. This review inspected the transcript and test definitions; it did not independently rerun them. Existing tests cover neural/raw-behavior read denial, whitelisted metadata reads, no neural dataset shapes in schema enumeration, external-link denial, bounded reads and several range/cache failures. Those passes do not cover the two P1 findings above.

The 13-session roster remains a historical candidate audit frame, not an admitted canonical cohort. Unit-to-electrode-to-atlas/probe mapping, source curation, task timing/annotation joins and adequate original context-block coverage still require actual canonical metadata evidence and a later scientific/source review. Training-only physiological QC, full model protocol and late neural outcome access remain inactive at this stage. Preserving the entire 85-item contract prevents an early reader review from being mistaken for scientific activation.

Candidate hashes at review:

- source_metadata.py: 5f664204a74ca319e521535418b8d21200271b0add29c2160a5e79b9abd7bb3d
- test_source_metadata.py: 7855d090c22d9c7e1bbf1d6db70d933dbd744f97685b2a71020119232c29cd63
- SOURCE_REGISTRATION.json: 3e4b923a51fc55de63922fcb6cf5fe17cc1fe29759a976d045b24a3d411fc990
- SOURCE_AUDIT_ROSTER.json: 642547d1c017d8eef3fa76833d48e2903ac79611c5e8ec299787318b64db1235

Open P0: 0. Open P1: 2. Return to engineering, preserve this unsuccessful review and obtain fresh review after repair and regression tests. No MERGE_ALLOWED or scientific PASS is granted.
