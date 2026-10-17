# Independent preliminary source review

Mission: `P14-M1-OPEN-RELEASE-RECOVERY`

Review scope: exact owner mission, prospective registration and baseline, saved public catalog pages, registered canonical identities and twelve saved Zarr descriptors. No external retrieval, neural values, continuous behavioral samples, fitting or outcome analysis was performed by this reviewer. This is preliminary guidance, not acceptance of a final mission candidate.

## Saved-source observations

- The NWB-specific catalog contains 63 records, including 53 public records covering 18 mice and 23 exact-date sessions.
- The two saved all-public Dynamic Routing catalog pages contain 595 unique asset identities; this wider catalog must remain distinct from the NWB-specific subset.
- Twelve registered latest-session descriptors expose target-region structure, probe/group identity, provider QC and CCF columns. Descriptor presence and dimensions establish neither target-region counts nor physiological admission.
- Eleven latest-session objects have no Zarr descriptor in the inspected listing route. Their HDF5-only status is an unresolved metadata-access route, not evidence of zero eligible units.

## Prospective upper-bound logic

A narrow anatomy/QC metadata audit may establish that the registered latest-version NWB route cannot support sixteen independent animals, without reading neural values or discrete trial events. Count a mouse as potentially eligible whenever any relevant exact session remains unresolved. Eliminate a mouse only if every relevant public session is affirmatively shown to lack ten qualifying ACAd/ACAv/PL/ILA units on any single probe. Preserve all session-level evidence and processing alternatives. Missing columns, decoding failures, unread HDF5 metadata and missing source flags remain unresolved.

An upper bound below sixteen would establish insufficiency only for that explicit NWB route. It cannot establish global Dynamic Routing insufficiency while public raw-only or other sorted assets remain unresolved. When those alternatives cannot be resolved under the registered bounded metadata-only methods, `SOURCE_OR_TIMING_INCONCLUSIVE` is supported; a global `OPEN_RELEASE_DATA_INSUFFICIENT` claim would require stronger evidence.

Passing anatomical metadata alone would not establish both-context coverage, original block/half trial counts, valid event timebases, support, full source provenance or actual physiological QC. All remain independent prerequisites. A split must not be declared frozen for an adequate cohort before the required complete metadata denominator is established. Historical scratch counts, masks and the separate incomplete 9/9 reservation must not substitute for canonical-source measurements.

## Contract preservation

The owner explicitly permits an applicable dataset-wide open license and does not require separately negotiated permission. Verified release-wide coverage plus relevant asset metadata is adequate for the rights gate; no per-file bespoke permission or researcher email should be invented. The owner permits at most one additional dataset, not an unlimited search. Stopping a disproved route at a sufficient necessary gate is appropriate provided the remaining requirements stay explicitly blocked and the wider public release is not falsely classified as exhausted.

Final scientific/source review remains pending a frozen candidate, saved-only reproduction and complete evidence/report.
