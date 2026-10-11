# Claim Audit

| Claim | Evidence / Boundary | Verdict |
| --- | --- | --- |
| Prospective protocol before metadata acquisition | Registration UTC and source hashes | SUPPORTED |
| Complete OSF public inventory snapshot |43receipt requests,2,585files/14folders, no failed pages | SUPPORTED |
| OSF released immutable dataset version | Mutable public project; per-file version pin only | NOT_ESTABLISHED |
| All forbidden neural files fully checksum verified | ProviderSHAonly; no data bytes downloaded | FORBIDDEN / FALSE |
| Three standalone documentation checksums verified | Exact metadata/document access plan and receipts | SUPPORTED |
| Site/source independent of primary | Author-described WVU/WUSTL/Utah versus Zurich | SUPPORTED_LIMITED |
| Exact private patient nonoverlap verified | No private identifiers or reidentification | NOT_ESTABLISHED |
| Fifteen filename patient labels/46sessions | All public event file names, paired extensions grouped | SUPPORTED_LABELS_ONLY |
| Eleven patients could have>=5hippo units | Official Table1summary counts only, not session/unit mapping | POTENTIAL_ONLY |
| Eight full-eligibility patients certified | Boundaries/gaps/trials/unit map missing | NOT_ESTABLISHED |
| Published continuous recording proves no gaps | No inspected raw header/block witness | REJECTED |
| Microsecond exports prove acquisition synchronization | Scale alone is not clock validation | REJECTED |
| Figshare is admitted independent validation | One mixed archive inventory; physiology/coverage unknown | REJECTED |
| Original DANDI failure repaired or R2 nowPASS | All original gate/split hashes unchanged | REJECTED |
| Preferred regime/NAP/CWP validated | No model or final evaluation | FORBIDDEN |

Seven open warning categories: mutable-release/byte verification limits;15/16
identity/session mapping discrepancy;hippo unit dictionary missing;valid trials
and training activity unknown;native support/gaps missing;common-clock mapping
unverified;Figshare archive-only metadata. Tests are engineering evidence, not
scientific feasibility. No warning was removed by regrouping or weaker criteria.
