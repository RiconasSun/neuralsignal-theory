# Independent R2 Scientific STOP Review

Review time:2026-10-11T20:46Z onwards. Mission:paper11-v2-r2.
Read-only sources/results/receipts/hash verification; no fitting, acquisition,
tests, report execution, null generation, selection or support reclassification.
Only this new review evidence file was written. Repository review templates and
review skill are absent; the explicit current contract governs this review.

## P0/P1 Findings

P0:none identified. P1:one unresolved factual documentation defect.

P1 at paper11_v2/R2_NUMERICAL_SCIENTIFIC_LIMITATIONS.md:24:
"All three selected families scored below the strongest baseline in all nine
patients" contradicts saved subject_statistics.json. For sub-05, discrete minus
baseline is +0.005950439231537041 and hybrid minus baseline is
+0.00614150817305209 nats/unit-bin. Continuous is negative in9/9patients;
discrete/hybrid are negative in8/9. All three patient-weighted means are below
baseline. Correct that sentence without changing any selected configuration,
contrast, criterion, fit or gate. Publication clearance awaits factual correction.

## Independently Checked Evidence

- Primary roster independently constructed from frozen23sessions and57configs:
  1exact stationary B0 seedNone plus56configs*3seeds per session =169;
  23*169=3887. Exact identity sets match; no missing/duplicate/failed seeds.
  All3887converged. Feature SHA, patient/session, development trial IDs and
  train/development unit-bin denominators match saved QC for every primary fit.
  QC totals:9patients,23sessions,592session-local units,622train/201dev trials.
- Six saved patient contrasts have9paired patients,10000bootstrap/seed20261011
  identities. Independent exhaustive512sign-flip arithmetic and Holm-six
  agree with stored values. No new intervals or inference were generated.
- Partial null evidence:2896saved converged fit records, no JSON parse failure.
  Exact roster345records in each bin-permutation replicate000..007; replicate008
  retains136valid unique subset records. Eight complete subject_results files.
  No completed null_summary/null_distributions artifacts or partial-null tail
  claims. Circular-shift and context controls are not completed evidence.
- External code2 receipt has exact frozen52asset identities:47documented support,
  5UNKNOWN_SUPPORT. Four first decoded TTLs are1.0; one99.0. These five retain
  one first-data-scalar receipt and no timestamp decode. All receipts restrict
  decoded paths to event data/timestamps and indices0/-1. No spike decoder,
  physiological unit eligibility or final evaluation is established.
- Across current R2-related registrations and artifact locks,10183unique paths
  matched current bytes:0missing,0mismatches,0conflicting recorded hashes.
  Source, preceding/archive, primary/null and report snapshots remain bound.
- Development report:9output hashes match;57configuration CSV rows and9/23/3887
  manifest coverage match. Both PNGs inspected:paired-gain forest uses saved CIs
  and0/.01references; nominal frontier includes all families/shared complexity.
  Documentation PASS is explicitly not scientific R2 PASS.
- Prior regression receipts:50unique passed in prior-regression.log plus the
  separate authorized eighteenth synthetic R1 test =51unique (R033,R118), exit0.
  Supplemental receipt is separate; original log retains its earlier failed
  transport/fixture guard attempt rather than laundering that attempt as PASS.

## Selection And Claim Scope

Frozen one-SE selected means:discrete -0.5471759733084931, continuous
-0.5680885963548558, hybrid -0.5462372511131538; strongest baseline
-0.5349213147416831. These are selected-model exploratory contrasts only.
Saved raw grid maxima differ:hybrid K4/lag5/ridge0.001 is -0.514053175318272;
discrete K4/ridge0.001 is -0.5153939231286009. Both exceed the baseline raw mean.
The newly added raw-grid distinction in LIMITATIONS and CLAIM_AUDIT matches the
frontier. It neither changes selection nor validates any grid configuration.
Never generalize the selected negative contrasts to all57configurations.

## Warning Ledger

warn_count=6; these are unresolved scientific/evidence limitations, not
administratively cleared by passing tests, reporting, review or a STOP verdict.

| ID | Unresolved Category | Requirement/Claim Boundary |
| --- | --- | --- |
| W01 | Null procedures incomplete | Q09OPEN;8/200count reps, partial ninth; no completed three-control validation |
| W02 | Five external boundary supports unknown | Q11BLOCKED; exact52retained, no exclusion or relaxed mapping |
| W03 | External physiological eligibility unknown | Q11BLOCKED;metadata patients/support are not train-only unit QC |
| W04 | Independent final validation absent | Q10OPEN/Q12BLOCKED; external60/40and spikes/final remain locked |
| W05 | ftol/one-iteration/global-optimum caveat | Optimizer success is not small-gradient/global-identifiability proof; design_rank is first-unit only |
| W06 | Exposed/postselection development inference | Exploratory patient-primary contrasts; not confirmatory or physical regime evidence |

Current golden denominator remains14,9VERIFIED. Q09/Q10OPEN;
Q11/Q12BLOCKED_HUMAN_INPUT;Q13OPEN pending saved-only score/PowerShell audit.
No missing requirement is waived or offset by extra reporting artifacts.
The running R2_saved_audit has registration only at this readback: no receipt,
row audit, test log or artifact lock yet. Its successful completion is NOT
assumed; saved-score numerical reproduction remains pending independent readback.

## Decision And Identity

bug_count=1(the documentation P1);warn_count=6.
Review decision:negative STOP documentation only, conditional on correcting
the P1 and receiving pending saved-audit evidence. No MERGE_ALLOWED, mission
PASS, scientific R2 PASS, preferred regime or R3 activation is authorized.
Current scientific state remains FAIL / DATA_INSUFFICIENT; regime INCONCLUSIVE.
WAIT_FOR_HUMAN_INPUT pertains only to future separately prospective authorized
recovery, never reclassification or resumption of this failed attempt.

Verified immutable identities:

- R2 gate SHA256:57fd2ac8b885ea2df331cdec9d285924e3329aad4160822951145cfa5f18fdb4
- R2 artifact lock:69e981f4378a9f3fb6f41e3ee7157f8ac5d45e95a0a9a1679d026c8c10b7a46a
- Code2 support gate:2a9c7327e8121c180dbec225122c5dcfec4a560dbf5617753e19975e2c6a7c3c
- A report manifest:4ae25d92c39e68b99c25ce96930b8dbd9ece55482a6e0a6967bba04be8356717
- External split:27fad80c753cfdef00977d056b379da5210f1e0247efba803a4e098e593e93e3

Promotion/push was not performed by this reviewer. Any later evidence or factual
documentation correction requires targeted readback; scientific warnings remain.

## Final Independent Supplement

The original review above is preserved as historical readback. This supplement
supersedes its unresolved-P1 and pending-Q13 findings only, not its warning ledger
or scientific-failure scope. No source, saved result, selection or gate was edited.

P1 resolved:LIMITATIONS now states negative patient-AVERAGED differences.
Discrete/hybrid are negative in8patients and positive for sub-05; continuous
is negative in9. The corrected statement matches saved differences, including
the two positive values recorded above. No remaining P0/P1 identified.

Actual saved CSV/JSON probabilities match exactly:

| Left Minus Right | Exact Raw p | Holm-Six p |
| --- | ---: | ---: |
| Discrete - Continuous | 0.00390625 | 0.0234375 |
| Discrete - Hybrid | 0.00390625 | 0.0234375 |
| Continuous - Hybrid | 0.00390625 | 0.0234375 |
| Discrete - Baseline | 0.01171875 | 0.0234375 |
| Continuous - Baseline | 0.00390625 | 0.0234375 |
| Hybrid - Baseline | 0.015625 | 0.0234375 |

Thus all SIX adjusted p-values are0.0234375, but only FOUR raw values are
0.00390625. Neither the raw-grid maxima nor these exploratory contrasts justify
changing frozen model selection or claiming external/regime validation.

Final saved-only audit readback:

- receipt.json records tests_exit_code0; locked tests.log reports59tests/OK.
- row_audit.json has6783SAVED_SCORE_VERIFIED entries, all refitted=false,
  all score/objective discrepancies exactly0.0;3887primary+2896partial-null rows.
- All6997original R2 artifact hashes independently match current bytes.
  All4saved-audit lock entries also match. No original gate identity changed.
- The A-report registration's3895snapshot paths independently match current
  bytes. This includes3887primary fits and8required A artifacts.
- Receipt SHA256:5646e168cb8fd8246b8e6c351d94102ec35f7ed7d4828c363a36106f1d69f4d4.
  R2 gate remains57fd2ac8b885ea2df331cdec9d285924e3329aad4160822951145cfa5f18fdb4.

Golden readback is10/14VERIFIED after Q13 verification, not14/14:
Q09/Q10remainOPEN;Q11/Q12remainBLOCKED_HUMAN_INPUT. The59tests are a final
saved-audit suite, distinct from the historical51unique prior regression cases.
This reviewer read existing audit evidence and did not execute tests or replay.

Final review decision:APPROVE PUBLICATION OF NEGATIVE STOP DOCUMENTATION ONLY.
bug_count=0;warn_count=6. W01..W06 remain scientifically unresolved, explicitly
retained and not administratively cleared. No MERGE_ALLOWED or mission PASS.
Scientific R2 remains FAIL / DATA_INSUFFICIENT; regime INCONCLUSIVE; R3 unexecuted.
Spikes/final locked, no cohort pruning, no resumed nulls or metadata reclassification.
Any recovery requires separate human-authorized prospective registration and
cannot erase this failure. No push/promotion performed by this reviewer.
