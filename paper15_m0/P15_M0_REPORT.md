# Paper 15 M0 — sensorimotor data feasibility

**Scientific verdict: FEASIBLE_INDEPENDENT_HOLDOUT.** Native IBL Brain Wide Map / **MOp** supports a credible next protocol stage: 20 independent metadata candidate mice, reserved as 12 development and 8 final, with successful real-spike feasibility tests in two prespecified development sessions. This is candidate feasibility, not physiological admission, powered confirmation, a model result or validated neurodynamics.

Mission: P15-SENSORIMOTOR-DATA-FIRST-M0. Exact base: `3f8e903d68c0990af1e1891c7444ff1210830f43`. Registration preceded fresh region counts; pilot identities and exact file inventory preceded payload access. Fifty-nine atomic requirements remain traceable in the evidence preservation matrix. Engineering M0_STATUS is certified by the reviewed verdict and actual Git handoff receipt, not by this scientific verdict alone.

## Exact denominators

Source roster: **139 mice, 459 sessions, 699 probe insertions, 12 labs**. Reused cluster table: **621,733 labeled units, 75,708 provider-good units**; trial table: **295,920 trials**. 107 mice have multiple source sessions. The screen keeps a single ranked probe/session per mouse; no units, probes, trials or repeated sessions become additional independent animals. Unknown Allen mapping affects 12,215 units source-wide; these never become target units. No unrecognized target-prefixed labels were silently joined.

| Distinct target | Anatomical mice / probe populations | Qualified probes at tier 8 | Independent mice at tiers 5 / 8 / 12 / 20 |
|---|---:|---:|---:|
| MOp | 23 / 37 | 31 | 20 / 20 / 20 / 19 |
| SSp-ul | 12 / 16 | 7 | 6 / 6 / 5 / 3 |
| SSp-bfd | 21 / 32 | 16 | 15 / 12 / 11 / 9 |
| SSp-ll | 12 / 13 | 5 | 6 / 5 / 3 / 3 |
| SSp-tr | 15 / 15 | 9 | 10 / 9 / 9 / 6 |
| SSp-n | 5 / 9 | 3 | 3 / 3 / 3 / 2 |
| SSp-m | 9 / 13 | 10 | 7 / 7 / 7 / 5 |
| SSp-un | 7 / 8 | 2 | 4 / 2 / 2 / 1 |
| SSs | 13 / 15 | 9 | 10 / 10 / 8 / 8 |

MOp was first in the registered anatomical order meeting the independent-design boundary (>=12 candidate mice, >=6 development and >=6 final). The fact that the resulting allocation is 12+8 does not reuse P14's old 8+8 floor. Eight units was registered as the primary local-population capacity screen; 5/12/20 are transparent capacity tiers. Same-probe MOp is never pooled with somatosensory regions. Exact **6,291 mouse × session × probe × region rows** (699×9), unit counts, task-window capacity and exclusions are in results/COVERAGE.csv; trial and tier tables expose every denominator. Candidate MOp allocation spans 11 labs. All selected rows have >=100 original paired-aggregate usable windows and >=40 per original chronological half.

The 23 anatomical MOp mice reduce to 20 with adequate good-unit capacity; 37 anatomical probes reduce to 31 tier-8 probes (29 sessions). Individual exclusions and duplicate-session reduction are visible in COVERAGE.csv / ALLOCATION.csv. Source lab, session and probe identities are preserved. Detailed native admission remains future work, not inferred for all 20 from the two pilots.

## Bounded real-spike pilot

| Frozen development mouse | EID / probe | Actual spikes | Native good MOp units | Native usable windows / chronological halves | Demo zero unit-bins |
|---|---|---:|---:|---|---:|
| CSH_ZAD_026 | 81a78eac-9d36-4f90-a73a-7eb3ad7f770b / probe01 | 34,166,347 | 84 | 940 / 492+448 | 7,500 / 8,400 |
| NYU-30 | 77e6dc6a-66ed-433c-b1a2-778c914f523c / probe00 | 25,836,824 | 22 | 761 / 383+378 | 1,745 / 2,200 |

Both are permanently development across all sessions. The official ONE unsigned public S3 downloader and ALF reader loaded only frozen files. Timestamps are finite and ordered; cluster IDs, UUIDs, provider labels, probe association and channel-linked anatomy are verified. The native good MOp cluster sets agree with old metadata for both pilots. NYU-30 has 102 annotation differences overall, including layers and non-MOp regions; no layer-level claim is made. Full difference tables are retained.

Observation support comes from AP acquisition metadata plus original monotone probe-to-session synchronization, independently of detected spike extent. Native task windows lie inside recorded support, wheel covers all usable windows, and strict-past wheel lookup is demonstrated. Known saturation intervals are mapped to session time and overlapping windows excluded. Ten fixed eligible trials per pilot illustrate half-open 50 ms bin counting and preserved zero bins. Synthetic invalid-window tests prove missing/bad observations stay a validity mask, not zero counts.

Old aggregate and native movement/trial versions differ. Old bwm/saturation masks were not transferred. Native usable counts use the prospectively frozen structural/known-artifact policy, whereas metadata candidates use the paired historical aggregate policy. These are separate denominators, not retrospective recovery of P14. See SOURCE_REGISTRY.md and OBSERVATION_LIMITATIONS.md for complete differences, durations, clock conventions and artifact burden limitations.

Total payload: **762,373,609 bytes / 24 files / two sessions**, below registered 1.2 GB total and 450 MB/file bounds. All file receipts have verified size, MD5 against single-part S3 ETag, and SHA256. Raw AP/LFP, videos, waveforms, whole-cohort spikes and final-reserved neural outcomes were not requested. Initial local setup/API/parser failures and their fixes are preserved in FAILURE_AND_REPAIR_LOG.md; none altered data eligibility, pilot selection or scientific thresholds.

## Scientific recommendation

Choose **local MOp history's predictive increment beyond measured task, movement and rate nuisances** as the one primary question. It matches real source features without relying on a winner among discrete/continuous representations. The proposed M1 specification assesses B0–B4, compact D/C and conditional static-mixture controls; it implements none. All eventual covariates must be known before the prediction bin. Offline movement-aligned conditioning cannot be marketed as real-time forecasting. Wheel adjustment does not exhaust body/face movement, and observational gains cannot establish a mechanism.

Reserve the eight listed final mice, use whole-trial blocked development partitions and future disjoint calibration/scoring within final mice, equal-mouse aggregation and paired mouse-level inference. An 8-mouse exact sign-flip minimum p of 0.0078125 for one two-sided contrast is a discreteness fact, not power analysis. M1 must justify its complete hypothesis family, effect precision, multiplicity, coverage and positive-claim rules before any fits. Physiological QC and native annotation revalidation can reduce the candidate sample. No confirmatory scientific claim exists yet.

Candidate A is useful, so conditional B/C searches were not activated. P1–P14 files and all failures are preserved; P14 remains ARCHIVED / SOURCE CONTRACT INCONCLUSIVE. Old P13/P14 exposed outcomes are not fresh confirmation. No cryptographic custody architecture was added.

## Delivery and boundaries

- Selected dataset/region: native IBL BWM, exact pinned pilot objects / MOp.
- CANDIDATE_INDEPENDENT_MICE: 20; physiologically admitted full-cohort mice: 0.
- SPIKE_ACCESS_PILOT_PASS: true for exactly two development sessions.
- SOURCE_OBSERVATION_CONTRACT: conventional curated ALF + acquisition-header duration + provider clock + known-invalid masking, with unknown other artifact burden disclosed.
- PROPOSED_HOLDOUT_DESIGN: 12 development / 8 reserved final candidates; final calibration/scoring not authorized in M0.
- PROMPT_2_READY: true for separately authorized protocol freezing, **not** full study activation.
- Predictive fits / model scores / reserved final neural access: 0 / 0 / false.

One-command saved-only reproduction: `& .\paper15_m0\reproduce.ps1`. On a new host provide `-Python` pointing to Python 3.11+ with the pinned numerical dependencies in requirements.txt. It denies network, regenerates five metadata outputs byte-for-byte and rechecks both counting fixtures from small saved timestamp fragments, without reading large cached neural arrays. This is saved evidence reproduction; it does not falsely claim a new provider download or all-mouse physiology audit. Independent internal review and Git verification are recorded separately. STOP after M0; M1–M7 remain inactive.
