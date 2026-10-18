# Independent full synthetic control integration review

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles. Scope: the saved successful synthetic fixture and its four explicitly synthetic journals, plus their bound production scoring sources. **P0=0; P1=0 in this evidence/component scope.** The evidence establishes completion of the full synthetic4x999 prediction/reference/journaling path. It does not replace real cohort E control results, numerical fit admission, or the complete independent E gate.

No expensive fixture was rerun. No likelihood, gradient, fit, real A/B/E/Final array or network operation was executed by the reviewer. Review execution read only the identified public sources/receipt and the four authorized `paper15_dev/work/full_synthetic_reference_journals/N1..N4.jsonl` files; additional checks regenerated synthetic mapping metadata and performed saved scalar arithmetic. Only this review report was written.

## Independently verified saved evidence

All fixture, receipt-source and four journal SHA256 bindings match current bytes. Each journal identifies subject `SYNTHETIC_ONLY_150900`, has exactly2001 JSON events, one original exposure,999 ordered replicate starts,999 completed replicates and one final suite completion. Exact start/original/complete ordering was checked, including every later start/complete pair. No failed/retry event appears. Each suite has999 distinct seeds, the original40 trial IDs and full40-epoch coverage. The combined denominator is **3996 completed bundles**, with22977 reference family-score outputs (three suites*999*7 plus999*2).

Every seed was independently recomputed from the frozen SHA256 string schedule `P15-M1|150107|suite|SYNTHETIC_ONLY_150900|E|replicate`. Using PCG64 at those seeds, the reviewer independently regenerated all3996 mapping hashes: N1's40 nonzero temporal rotations; N2/N3's two20-epoch original-half strata and nonzero cyclic donors; N4's eight complete5-trial blocks and nonzero block shift. All mapping hashes matched. This was mapping-only checking, not a replay of likelihood evaluations.

Every completed model dictionary contains exactly B1,B2,B3,B4,D,C,S for N1/N2/N4, and exactly B1,B4 for N3; B0 never enters a reference bundle. All saved likelihoods are finite and have3200 nominal scored unit-bins (40epochs*10scorebins*8units). All six reference effects were independently reconstructed from saved model LLs and equal denominators. N3 instead has six copies of B4 LL/unit-bin; its separate wheel gain equals (B4-B1)/unit-bins. All original effects likewise match receipt values.

For each suite the reviewer reconstructed the complete returned summary dictionary from journal fields, saved scores, frozen labels and known fixture metadata, including all seeds, mapping hashes, wheel gains and target/filter declarations. Its canonical JSON SHA256 exactly matched `SUITE_COMPLETE.summary_sha256`. Thus the successful-loop aggregate is bound to all saved replicate outputs, not merely the receipt's asserted count. Both independent saved-check commands exited0.

## Actual source path and mathematical meaning

The fixture creates40x20x8 synthetic Poisson counts and37 synthetic nuisance columns with fixed PCG64 seed150900, constructs real production causal histories, design scales and C states, and instantiates actual models through `training.build_model`. Coefficients are initialized and perturbed synthetically; no optimizer or real coefficient file is used. It calls the actual `FrozenPredictors.score` and `run_controls` without mocking scoring/reference functions. It bypasses the predictor's real-selection loading constructor deliberately, so real fit/gate validation is not exercised or certified here.

D and S each have three configured members with seeds11/23/37. The bound `FrozenPredictors.score` actually constructs each member's `prebin_logmasses`, checks finite mass and combines the three joint predictive masses by logmeanexp per bin before score-bin summation. The baseline/C families use their corresponding actual model path. The journal stores final ensemble LLs, not each member's per-bin mass, so this review source-verifies that executed path and does not claim an independent numerical replay of every member likelihood.

The bound `control_arrays` preserves original synthetic targets and task columns, recomputes surrogate histories/C with fixed original scales, and restricts N3 to wheel coordinates24:38. The bound D implementation scores `self.y` before updating the filter with surrogate counts; S remains an IID mixture. These unchanged source identities are the accepted E mathematical review3 surface. Complete successful execution exercises the downstream loop and summary/journal completion omitted by the earlier interruption and mocked assembly tests; it does not add a new scientific model or analysis.

The fixture replaces `np.load` and the used socket connection entry points with denial functions and has no optimizer, data-extraction or network call. Its source/receipt support synthetic-only execution. These in-process denials are not claimed as an operating-system custody sandbox or a substitute for actual E access review.

## Exact checked identities

| Artifact/source | SHA256 |
|---|---|
| synthetic_control_integration.py | 0e323f4ffffc2316692f84383b41e43277892b8e28a00fbb79f1c95edefd5f37 |
| M5_FULL_SYNTHETIC_CONTROL_INTEGRATION.json | 9afaa07f6e3e209a01f0a90e1df37ad287974587139430416e51fa7ba2b425bd |
| synthetic N1.jsonl | f691a090bf7855c90943db6e43bcd3f51d85ef33812d4f3e77b31ed361430d6f |
| synthetic N2.jsonl | ed1e946f34e8476a0decae7393b80afc9b08b19062bb9711c02e9e7218ceb120 |
| synthetic N3.jsonl | 91a6762ef1eb348525eb883b2f390db1a722007ee79f07ff03652b680c78f617 |
| synthetic N4.jsonl | cced87414f9e24530b043a4b95be68968b76bad639cddb7d78ef8381a5f35fee |
| paper15_dev/models.py | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_dev/training.py | 1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/controls.py | 093bc970d429575b66e9032006060198377633212312e817bcbd2a278a431a35 |
| paper15_dev/evaluation.py | 83d80d0d05607e312a2bead824de1092e9a8490f06e1ba81447ec792c40bb472 |
| paper15_dev/evaluation_support.py | 01fe5bf8fb3000f4d53cf8b133de23ea6d2f26c2a82b00a07d93e500fd9062a8 |

The fixture/receipt paths in this table are under this evidence folder; the four journal identities refer only to the explicitly synthetic work folder above. Preserve preceding failed/partial reviews. Real control coverage, unavailable mice/cases, donor imbalance limitations, fit gates and one-shot E authorization remain separate obligations; no Final or whole-E authorization is granted by this review.
