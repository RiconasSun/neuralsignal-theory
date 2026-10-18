# Independent stopped-execution reconciliation review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles. Scope: exact registered plan, stopped fit JSON records, saved numerical arithmetic and interruption/time-audit evidence. No real neural arrays, new model/likelihood/gradient/FD/AD evaluation, fitting, B/E/Final data or network was accessed. Only this report was written. All original fit evidence, including the STARTED residue, remains unchanged.

**Reconciliation/evidence review: no additional P0/P1 defect found. Scientific source-validity gate: FAIL; the known critical timing/input defect remains unresolved.** These are separate conclusions. The358 saved NUMERICAL_PASS labels describe the implemented rounded-input objectives and cannot clear the frozen-native scientific failure, complete the610-start plan, authorize a retry, or permit B selection/E/Final progression.

## Exact stopped ledger

The actual plan has10 fixed subjects,61 unique frozen configurations each,610 total, maximum732,zero retries. It retains L-BFGS-B2000/80000/40/1e-12/1e-6 and PG<=.001, independent AD<=1e-5 and all three FD steps1e-4,1e-5,1e-6<=1e-5. Source-generated configurations equal the saved plan exactly.

All359 actual fit JSON paths are unique planned pairs and exactly the first359 execution positions in the registered order: all130 baseline starts, then dynamic starts by original subject/configuration order. There are no extra fit records. Every record's subject/full configuration/family/attempt1, production-gate SHA and A-preprocessing JSON SHA match the frozen identities. Every fit byte size and SHA matches its sealed attempt row. Combined with five sealed source/plan/marker files,364 byte-size/SHA preservation checks passed.

| Ledger category | Count |
|---|---:|
| Planned | 610 |
| Attempted, original claims preserved | 359 |
| Completed, saved numerical PASS | 358 |
| Completed numerical FAIL | 0 |
| Interrupted original STARTED | 1 |
| Unattempted | 251 |
| Completed baseline | 130 |
| Completed dynamic | 228 |

The completed family counts are B0=10,B1=30,B2=30,B3=30,B4=30,D=90,C=60,S=78. One additional S claim is interrupted. KS046,PL033,SWC_043,SWC_038 each have61 completed records; CSH_ZAD_026 has49 completed plus1 STARTED; NYU-30,KS051,ZFM-01937,CSH_ZAD_019,UCLA035 each have13 completed baselines. The baseline completion marker's130 hashes/counts match the actual files. The dynamic log has228 completed lines; no dynamic-complete marker exists.

The interrupted pair is **CSH_ZAD_026 / S_k3_l1.0_s11**. Its original record has attempt1,status STARTED,578 finite initialization parameters,empty optimizer_history and no coefficients/PG/objective/independent endpoint/completed timestamp. Its SHA256 is `33f5db4a49cc4c82fc873abb6d1dc99e0aa86f2e77c62ba53e4a03e65345e582`. It is not a completed failure, successful endpoint or restartable absence. No in-memory progress is invented. The seal records Ctrl-C of session42960 and exit1; this review verifies the saved seal and residual/log evidence, rather than independently reobserving that past process exit.

## Saved numerical examination

The reviewer independently invoked only `saved_audit.numerical_record` on each of the358 completed records. Neural-file loading/network and Model objective/value/pre-bin likelihood methods were replaced with denial functions during this saved check. Every record passed replay of finite parameter/gradient arrays, coordinate AD absolute/scaled errors, all fixed-step FD absolute/scaled errors, objective equality, full-gradient norm, original-bound PG, bounds and recorded PASS classification. No derivative was evaluated.

Additional checks verified iteration/history length and numbering, finite saved callback objective/PG/gradient norms, callback call counts bounded by final counts, original iteration limit and nonexhaustion, plus8-unit exposure arithmetic. Completed records total47478 saved objective calls and43690 accepted iterations; these are completed-record totals and exclude unpublished interrupted in-memory work.

| Maximum over358 saved completed records | Value |
|---|---:|
| Projected gradient | 9.343555132028652e-6 |
| AD maximum scaled error | 5.598955736249248e-14 |
| Fixed-step FD maximum scaled error | 9.892619122421793e-9 |

This proves internal consistency of saved numerical evidence, not fresh raw-data reproduction, frozen-native input correctness or scientific fitness. The full-success `audit_fits/audit_all` was deliberately not called because this execution is incomplete and B/E artifacts are absent.

## Time/source defect and mandatory stop

The saved TIME_SERIALIZATION_AUDIT_1 has exactly the same10 subjects. It reports zero changed target-count cells,zero history cells and zero eligibility-mask differences for all10. Nevertheless five subjects have nonzero wheel nuisance differences: PL033,SWC_043,SWC_038,KS051,CSH_ZAD_019. The largest saved transformed-X absolute discrepancy is0.05892361851165395. Small timestamp serialization errors therefore do not establish semantic equality of causal sampled wheel inputs. Other small floating differences remain reported; this review adds no acceptance threshold or favorable-subject exemption.

The source/native audit itself was not regenerated here; its current JSON hash and summary arithmetic were checked. Frozen-native fidelity remains failed even though counts/history match and all completed implemented-objective numerical checks pass. No refit/source repair or inference that scientific results are unaffected is approved.

Saved flags deny B selection,E evaluation and Final neural access. SELECTION_FREEZE,B_CANDIDATE_SCORES and E_BATCH_CLAIM do not exist, consistent with stopping before these stages. Absence/flags are not treated as a universal forensic proof of all past accesses. No B/E/Final read was performed by this review. Existing component/synthetic approvals cannot override this failed scientific source gate. Original STARTED and all358 completed records must remain historical evidence; any future authorized recovery must account for all610 planned positions and cannot silently resume/retry this mission.

## Checked SHA256 identities

| Artifact/source | SHA256 |
|---|---|
| INTERRUPTION_SEAL.json | f87d5cc1362e597968e59b119c1a6eb50a6f8d8432faf0939429b47f324b7062 |
| TIME_SERIALIZATION_AUDIT_1.json | 6a682d4f54154f4c6899cda3f9a16496bf03b2e2cdafd03971a588800508a078 |
| paper15_dev/A_FIT_PLAN.json | 2a6af8f763950ef4136b291010d43e29e5360ebb6e6a628032ba75410c15e868 |
| paper15_dev/PRODUCTION_GATE.json (historical numerical gate) | 8347af5ac6fec33628869c7151fc2cbdf3461ae0a5049a2932acfccbeb108d28 |
| paper15_dev/results/BASELINE_ATTEMPTS_COMPLETE.json | b0cf11855f86796a6b0a0f4018beda8c8eaef79a03b73ac46f93e4a60d0c2d16 |
| paper15_dev/training.py | 1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d |
| paper15_dev/models.py | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_dev/saved_audit.py (used numerical_record only) | 19bfa45f0a7e77cedf9aefd74be469e9e2a24f0bf31e9ed26c6eb3b19abb1fde |
| numerical_record AST source segment, UTF8 | 79407ace109de23954c6be34d3284967c773f69b1dffde392bd12d0491209449 |

All359 individually checked fit hashes remain enumerated in the bound seal, including the interrupted hash above. The other preserved-artifact entries, especially neural array files, were not opened or independently rehashed by this reviewer. This review supports accurate stopped archival reconciliation only; the scientific gate remains FAIL and execution must remain stopped.
