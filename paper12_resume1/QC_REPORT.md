# Real M2 and M3 QC

Mission P12-M2-REAL-RESUME-1;new prospective track,base376ca01.

## Cohort Admission

All26frozen mice completed:8originalsession artifacts reused unchanged and
18newextractions. Both groups13/13eligible;minimum actual CA1/DG counts
development239/57,final235/76. Admission remains>=8mice/group and>=5units/ROI.

| Group | Mice | Candidate Units | Eligible CA1 | Eligible DG | Excluded |
|---|---:|---:|---:|---:|---:|
| Development | 13 | 10989 | 5413 | 1819 | 3757 |
| Final calibration | 13 | 9675 | 4771 | 1475 | 3429 |

The26-row disposition CSV reports exact metadata trial coverage and nonexclusive
rate/active-fraction/ISI rejection causes. Unit-level QC remains private. No
full-session rate/presence metric was used to select units. Source integrity
checks and train/cal physiological QC are distinct. Metadata trial counts are
not a claim of independently certified native recording continuity.

All18new source checkpoint sets were verified against locked IDs/ETags/ranges,
full opaque-body/envelope SHA256 and persistent attempt ledgers. Eight reuse
sessions have original ciphertext/key/provenance fingerprints;they were not
re-downloaded or subjected to a new source-cache audit. Thus "envelope SHA"
in the generic CSV includes original encrypted partition envelopes for reuse,
not an assertion of26new range-cache audits or independent whole-file hashes.

1244newHTTPrequests,0recorded transient failures,5186898920verified response bytes.
18old verified opaque blocks reused,including1old pending block newly reverified
and committed. Original pending/STOP/failure records remain unchanged.
Bytes are verified accepted response bodies,not total wire traffic/full NWB size.
ETag is object-version evidence,not an independent complete-file checksum.

## Native Isolation

Preflight NTFS/same-volume/custody DACL/checkpoint publication passed. Eight
original private artifact sets passed hash-only checks without decryption.
Fresh zero-capability AppContainer file/key/DACL/network/memory denial passed.
ActualM3roleproofalsoPASS:AppContainertrue,capabilitycount0,network10013,
source/key/DACL/custodian-memorydenied. The trusted controller/host is not the
scientific role or a malicious-administrator defense. Ordinary tool sandbox
was never substituted for the scientific isolation boundary.

Custodian full-session locked target vectors decoded:TRUE. Analysis-visible
data:developmentA/Bonly. Custodian created encrypted D counts under the existing
amendment;final evaluation values were not delivered to analysis or evaluated.
Do not misread this as globally zero decoding of final-period source values.

## Scientific Stop

M3smoke onmouse744912849/session766640955 completed126evaluations:
21configs x3seeds x2ROIs.6stationary exact estimates converge;120nonstationary
fits fail projected-gradient<=.001. All126optimizer_success flags aretrue,
but all120failed fits stopped on relative reduction of objective. FailedPG
range [.001749584006721426,.061066324748139805]. This is an observed mismatch
between optimizer stopping and the frozen acceptance rule,not proof of the
underlying numerical cause or evidence against a model family.

M3FAIL/INCONCLUSIVE;full13mouse evaluation,statisticaltests,M4,M5andfour
199-replica null suites were NOT EXECUTED. No dataset or threshold adjustment.
No regime preference,neural mechanism,NAP or CWP validation is supported.

## Preserved Diagnostics

Initial tool-sandbox fixture Temp permission failure preserved;workspace fixture
placement fixed without ACL changes. Wrapper failures preserved;scoped fallback
used. Independent-review missing-old-block/issuer/gate-binding findings fixed
prospectively before real requests or relevant model launches. InitialM2audit
and gate preserved;stronger source-denominator re-audit used saved artifacts only.
M3launch1public-metadata routing andlaunch2clone-default TypeError preserved;
both occurred before analysis process/fits. Launch2profilecleanupHRESULT0.
Code4actualchildexit2 after smoke numericalFAIL,not timeout or transport failure.
