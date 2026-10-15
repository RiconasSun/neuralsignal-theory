# Independent archival-regression review addendum

Mission: `P12-REAL-D-SINGLE-APPROVER-AMEND-1`.

Decision: continue **APPROVE_ENGINEERING_ARCHIVE_ONLY / HOLD_REAL_D**. No P0/P1 found in this narrow saved-QA addition. Canonical `engineering_final_review.md` remains byte-unchanged at SHA256 `09f219ee2abac2c7a01ca0167aa68492d6aecac699e97ab46c39d2ffc26658cb`; its scope, three human-blocked requirements and actual subsequent Git gates remain unchanged.

Reviewed only the prospectively registered archive regression, appended saved wrapper, QA snapshot and actual reproduction evidence; no experiments, fits, protected real asset reads, signing, release or Git operation was performed by this reviewer.

`verify_failure_archive.py` checks the exact outside-tree 73-file manifest, actual byte hashes, preserved invalid old inventory and original 72 payload records. It explicitly requires the old empty-file self hash to differ from the corrected actual-inventory hash; it cannot report the original inventory as a valid 73/73 record. Its four meaningful saved-only tests cover actual acceptance, missing entry, corrupted hash and self-reference/traversal rejection. Checks use explicit failure conditions and unittest assertions, without an optimization-disabled Python `assert` gate. The wrapper invokes these tests and rejects nonzero exit status. No production, cryptographic oracle, scientific threshold or completed synthetic result changed.

Exact bindings:

- Regression registration SHA256: `8874c6f374ee809fbbf92a667b26cdd64066009a8f301a8e48df575577c9d4b1`.
- `verify_failure_archive.py`: `5fe8c6d4c5997831628198983ec35267ff3e7f978d449c521aadf28ba30516e4`.
- Updated saved wrapper: `ed4b55412809bdc317bd043c4001a721314c21dce45333315cf170b67d886140`.
- QA revision-5 snapshot: `0aab9500703c4d112271f492d951f69e738bdfaa77e77410a8f3644acfefde25`; all 11 helper hashes independently match.
- Current complete saved log: `d0c22ca8f19145d4b0d7fc942d899d4ee33926fb29f01b19aa3e9c6c19bf307d`.
- Actual saved subprocess receipt: `285951e4fc07169c1179784b5bda42880a12704b2ce0c1732ec9f8a60d8f4da4`; records exit 0, QA revision 5 and the matching log hash, ending at `2026-10-15T20:39:02.493544+00:00`.

The new log retains the four prior saved checks, including 1,387 signed artifacts, and records all four archive regressions PASS plus the explicit `INVALID_SELF_ENTRY_PRESERVED` result. This reviewer inspected the completed execution evidence without rerunning it.

The QA revision-4 snapshot and successful log/receipt referred to by the unchanged final review are now preserved as `QA_SOURCE_SNAPSHOT_r4.json` (`0f4d829bc135ddee7f0fda2def71a8272fd6c024c8e3828353bb7d253c70205c`), `saved_reproduction_QA4_pass.log` (`14bff58b0a80c51591f21bbb4410eba9809aeaf95c0a59798dda98497bdbee90`) and `saved_reproduction_QA4_pass_receipt.json` (`6603f70c901c4ed1aff5ac65d016ce63438b9a7477d8760e71c1499ccad2418a`). These preserved bytes independently match those prior review bindings. The earlier failed invocation remains historical. The outside-tree corrected manifest remains unchanged at `257bb4e4581978dceeecc5c9daf95684b1b483f5c921ac663cead090b77737ff`.

No full scientific rerun is required by this saved-QA-only addition. Update closure documentation and manifests to identify QA revision 5, these four additional regressions and this addendum, then complete exact staging/normal origin-test push/remote readback/clean evidence. Genuine owner setup and actual protected public import remain blocked; no overall mission PASS, REAL readiness/signature/release/evaluation or scientific validation is granted.
