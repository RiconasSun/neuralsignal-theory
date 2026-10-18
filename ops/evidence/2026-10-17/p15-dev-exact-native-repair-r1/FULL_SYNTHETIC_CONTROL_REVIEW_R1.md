# Independent R1 full synthetic control integration review

Mission: P15-DEV-EXACT-NATIVE-REPAIR-R1. Reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles. **P0=0; P1=0 in this synthetic component/evidence review.** The saved R1 fixture establishes a complete successful4x999 production reference/prediction/journaling path. It does not certify actual cohort E results, current real A fits, full E admission or Final access.

No expensive fixture, model prediction, likelihood, derivative or optimization was rerun. The reviewer read public source/receipt files and only the four authorized synthetic journals under `paper15_r1/work/full_synthetic_reference_journals`. No actual fit record or real A/B/E/Final neural array was read. New output is this review, its saved-only diagnostic script and receipt.

## Independent saved verification

The reviewer executed `verify_full_synthetic_review_r1.py` with bundled Python, bytecode disabled, single BLAS/OMP threads and ResourceWarning as error. Exit0; it performed the following complete checks without calling any production likelihood or fit function. Array-file loading and socket connection entry points were denied.

- Fixture source SHA and all six recorded production runtime-source hashes match current bytes. ASTs of actual `run_controls`, `FrozenPredictors.score`, `control_arrays` and `build_model` match their previously reviewed mathematical implementations. The R1 loader/cache adaptations do not change these scoring operations.
- Each suite has2001 parsed events: one suite start, one original exposure,999 ordered replicate starts,999 ordered completions and one final suite completion. Exact chronological pairing, subject `SYNTHETIC_ONLY_150900`, all40 trial identities, full coverage and999 unique per-suite seeds were checked. There is no failure/retry event. All four suites complete999; total3996 reference bundles.
- Every seed was independently reconstructed from SHA256 of the registered `P15-M1|150107|suite|SYNTHETIC_ONLY_150900|E|replicate` string. Fresh local PCG64 instances regenerated all3996 mapping hashes using independent mapping-only code:40 nonzero temporal rotations for N1,two original-half20-epoch cyclic donor strata for N2/N3,and eight complete5-trial cyclic blocks for N4. Every hash matches the corresponding completed event.
- Every N1/N2/N4 model dictionary contains exactly B1,B2,B3,B4,D,C,S; N3 contains exactly B1/B4. No B0 reference output exists. The reference-output total is22977 family scores, excluding the four original-exposure calculations and constituent ensemble members. Every saved LL is finite with3200 scored nominal unit-bins:40epochs*10scorebins*8units.
- Every six-slot reference-effect vector was recomputed from saved model LLs and common denominators. N3's formal vector is B4 LL/unit-bin copied into six labeled slots; its separate wheel gain is (B4-B1)/unit-bins. Original-exposure effects match the integration receipt. No descriptive wheel gain substitutes for the formal N3 statistic.
- Each complete returned panel was reconstructed from its journal, all saved model scores/seeds/mapping hashes and frozen fixture labels. Canonical JSON SHA matched all four `SUITE_COMPLETE.summary_sha256` values. Receipt counts are therefore supported by every saved completed output and its returned-summary integrity, rather than count assertions alone.

The diagnostic generates synthetic mapping metadata only; it does not load the fixture's synthetic count tensors or independently recompute likelihoods. All observations above are saved-output/source-bound verification, not a second4x999 scientific execution.

## Actual production path and limits

The fixture creates40x20x8 synthetic Poisson counts and37 synthetic nuisance columns with PCG64 seed150900; production feature/history/C routines derive fixed scales/states. It uses actual `training.build_model`, initialized/perturbed synthetic parameters, actual `FrozenPredictors.score` and actual `run_controls`. D/S have original seeds11/23/37 and three members; the bound score code combines member joint log masses by logmeanexp at each bin before score-bin summation, checks mass finiteness and retains original nominal denominators. Member masses are not saved individually; this review source-verifies that path and does not claim an independent per-member likelihood replay.

The actual control path retains original synthetic current targets, recomputes H/C on surrogate counts with frozen original scales, supplies surrogate past assimilation only for D, and restricts N3 wheel replacement to design24:38. D scores the original current target before assimilation; S is the unchanged IID mixture. The fixture uses a deliberately constructed synthetic predictor via `__new__`, so real selected-fit loading, actual source/production gates and neural E extraction are not exercised. Its synthetic in-process file/socket denials are not represented as an OS custody sandbox.

This complete success-path coverage complements earlier interruption and mathematical unit checks. It does not clear a real scientific source failure, validate current main-fit convergence, establish real control coverage/exchangeability or release B/E/Final. Actual input/fit/selection/sensitivity/control gate reviews remain mandatory. Existing historical failures are not modified or reclassified.

## Exact identities

| Artifact/source | SHA256 |
|---|---|
| synthetic_control_integration.py | 2d1b290fc9928cdd31f082549776dcafdc0588d9e496dce94ec69800cf2a0924 |
| M5_FULL_SYNTHETIC_CONTROL_INTEGRATION.json | 28ea178b1859df56d0ce4f95aa814d4862aa6a145d6ce03dc28960d93ee32403 |
| verify_full_synthetic_review_r1.py | 7a6365618a3c905887fe82880b01125ac360e29db204aaa72c99b3e38db44d13 |
| FULL_SYNTHETIC_CONTROL_REVIEW_R1_RECEIPT.json | 3f9ebfb059964ea4b5042e7c5487b94d87b60cb2a0a53fb28bf085c466e40c37 |
| R1 synthetic N1.jsonl | f691a090bf7855c90943db6e43bcd3f51d85ef33812d4f3e77b31ed361430d6f |
| R1 synthetic N2.jsonl | ed1e946f34e8476a0decae7393b80afc9b08b19062bb9711c02e9e7218ceb120 |
| R1 synthetic N3.jsonl | 91a6762ef1eb348525eb883b2f390db1a722007ee79f07ff03652b680c78f617 |
| R1 synthetic N4.jsonl | cced87414f9e24530b043a4b95be68968b76bad639cddb7d78ef8381a5f35fee |
| paper15_r1/models.py | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_r1/training.py | 3fd665995463f3608e2c73fa30b8e1202e413b34daccb8480cb3e63c11d0ff8f |
| paper15_r1/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_r1/controls.py | 093bc970d429575b66e9032006060198377633212312e817bcbd2a278a431a35 |
| paper15_r1/evaluation.py | 83d80d0d05607e312a2bead824de1092e9a8490f06e1ba81447ec792c40bb472 |
| paper15_r1/evaluation_support.py | ae51af203734ad82451b01b91816a7e6e2ebd23b71bcea49504e0e47d0c7e189 |

The first four paths are relative to this evidence folder; journal paths refer only to the explicitly synthetic R1 work folder. The diagnostic receipt additionally records this review's Python executable SHA/version and NumPy version. Those describe the saved-only review runtime, not an invented retrospective executable hash for the original fixture run. Relevant future source changes require affected verification. Scientific cohort E control completion and whole-E admission remain unissued by this review.
