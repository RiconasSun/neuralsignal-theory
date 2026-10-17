# Independent source-reader review r2

Mission: P14-V2-EXPLORATORY-CONTEXT-DYNAMICS

Decision: ACCEPTED_FOR_BOUNDED_METADATA_AUDIT_ONLY.

Open P0: 0. Open P1: 0. Both prior P1 findings are resolved for this candidate. Preserve SOURCE_READER_REVIEW_r1 as unsuccessful historical review evidence.

The stable source reader now disables automatic redirects, validates HTTPS and approved host/asset-or-blob delivery paths before each request, bounds redirects and records each HTTP transaction against the prospective request budget. The new unapproved-host and wrong-blob regressions establish that only the original approved API endpoint is contacted in those failure cases. The successful two-hop synthetic case also proves both transactions are recorded. These are request-boundary controls for this bounded audit, not a new protected-data custody architecture.

Cached payload verification now requires exact start, requested length, Content-Range, nonempty ETag, asset identity, file size, actual payload length and SHA256. The equal-length different-offset payload-plus-receipt swap is rejected. Existing digest-corruption and changed-ETag regressions remain intact. No scientific criterion, source roster, metadata eligibility rule or dataset permission was changed by the repairs.

The reviewer independently ran `python -W error::ResourceWarning -m unittest paper14_v2.test_source_metadata -v`: **18 tests passed**. Transcript: REVIEWER_SOURCE_TESTS_r2.txt. The suite uses synthetic in-memory HDF5 objects and mocked range HTTP, plus verification of the 746 frozen historical source/metadata/document hashes. The reviewer made no network request, inspected no real NWB or real range cache, decoded no neural or raw behavioral signal values and made no implementation edit. Only synthetic temporary range caches were created by tests. SOURCE_TESTS_r3.txt independently agrees on 18 passing tests. The original r1 transcript's 14 tests and the subsequently corrected count remain preserved.

The whitelist admits only identity, unit provider curation/anatomy, electrode labels/coordinates and discrete task-event/invalid-time metadata. Neural datasets and raw continuous behavioral signals remain outside value access, and schema enumeration does not open their datasets or shapes. Opaque HDF5 transport remains explicitly disclosed as potentially containing uninterpreted adjacent bytes. This is a bounded trusted official-source reader, not proof against malicious administrators or adversarially rewritten source files.

Source registration and roster hashes are unchanged. The roster is still 13 historical candidate sessions, with no admitted canonical cohort. Actual canonical unit/electrode/atlas/probe mapping, provider curation, task-clock/annotation compatibility and eligible context-block coverage must be assessed from the bounded metadata audit and independently reviewed before source compatibility can pass. Full scientific/model/control registration and training-only neural QC remain separate downstream gates. This review grants neither neural activation nor late evaluation access, scientific protocol acceptance, cohort certification or full mission PASS.

Candidate hashes:

- source_metadata.py: ce50fd89d0616af006f8a9c7cad3420bce2f9fec17c9d836b6703682a1170625
- test_source_metadata.py: 0f0c075ab56e68c0581ae9c8ba9629db9f71eaa7ee1805c360d638edfc9eb055
- SOURCE_REGISTRATION.json: 3e4b923a51fc55de63922fcb6cf5fe17cc1fe29759a976d045b24a3d411fc990
- SOURCE_AUDIT_ROSTER.json: 642547d1c017d8eef3fa76833d48e2903ac79611c5e8ec299787318b64db1235
