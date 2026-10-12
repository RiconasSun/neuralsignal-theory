# Evidence-Bounded Claim Audit

| Claim | Evidence | Allowed interpretation |
|---|---|---|
| Prospective policy precedes recovery | registration.json, implementation_registration.json | Same 26 source identities, no protocol redesign |
| Previous failures preserved | registration.prior_sha256 and original_timeout_sha256 | No retrospective PASS |
| Eight artifacts reused unchanged | Private reuse issuer binding, public reuse receipts | No re-extraction or reselection |
| Synthetic code verification | results/preflight_tests.json/log | 24 regression tests; not biology |
| Native access isolation works in tested scope | results/isolation/native.json | Synthetic native role denials; not host-admin defense |
| Network responses received correctly | results/transport/779839471.json, checkpoint audits | Version/range/length checked; not whole-file checksum |
| Atomic checkpoint commit failed | Sanitized failure, private original diagnostic SHA | Local WinError 5, not another timeout |
| Marker integrity audit corrected | checkpoint_audit_verified2.json | Initial overstatement retained, not silently cleared |
| Rename failure reproducible intermittently | checkpoint_audit.json, all 20 trials | 1/20 failure; cause not established |
| Known cohort eligibility 4/4 | M2/gate_result.json, mouse_disposition.csv | Only completed QC; cannot infer full cohort insufficiency |
| Per-mouse reasons use permitted QC | aggregate_QC_reasons.json | Train/calibration aggregate reporting, not model inputs |
| Custodian decoded target vectors | Success/failure receipts | Includes full-session permitted custody decoding; not analysis access |
| Final analysis exposure and evaluation absent | Receipts, native boundary, gate | No final release or score; no claim source never decoded |
| Saved replay succeeds if recorded | replay receipt and verified manifests | Public outputs/tests only, not new experiments |
| Predictive regime or neural primitives | No supporting experiment | Not assessed; no NAP/CWP claim |

The following are explicitly incomplete: 17 source extractions, full physiological
admission, real baseline/model fitting, all mandatory null procedures, independent
final evaluation and biological interpretation. Engineering proof cannot fill
these gaps. Original P1-P11 and archived P12 tracks remain untouched.
