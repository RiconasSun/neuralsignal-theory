# P14 M0 — Context-dependent predictive dynamics: metadata feasibility

Mission `P14-CONTEXT-DYNAMICS-DATA-FEASIBILITY`; exact base `fae4fa316bbb499a86949d496e6ba4f36380e29f`.

**Scientific feasibility verdict: INCONCLUSIVE_METADATA.** Dynamic Routing is the leading metadata candidate, with **18 independent mouse candidates** satisfying the prospectively registered same-session, single-probe mPFC composite and paired-context metadata screen. This is an upper bound on a future physiologically eligible cohort, not an admitted neural cohort or scientific validation. No candidate is currently recommended for neural activation. Exact scratch-data licensing and per-candidate continuous movement/arousal availability/alignment remain unresolved.

M0 engineering completion is separate: saved metadata, deterministic accounting, synthetic regressions, independent internal review and ordinary Git archive are the acceptance objects. Final engineering/Git PASS is certified only by the executed external closure receipt, not by this precommit report. No spike timestamps, neural count arrays, raw signals, fitted models, predictive scores or final outcomes were accessed. M1–M7 remain inactive. Prompt 2/5 **cannot begin neural activation** on this evidence; a later protocol/source-resolution task requires separate instruction.

## Registered scope and chronology

The 52-item requirement baseline, exact owner attachment, JSON mission specification, original-input hashes and registration receipts are in `../ops/evidence/2026-10-16/p14-context-dynamics-data-feasibility/`. `REGISTRATION.json` fixed the estimand, anatomy and source-specific screens before new eligibility counts. The r2 pre-count clarification made explicit that the temporal cut uses all original runs and small runs cannot contribute observations. Additional-candidate, DR source, column-whitelist and observation-support policies were also recorded before their respective counts. No cutoff was chosen from neural performance; no neural performance exists in M0.

The new target is a within-population context interaction in the **predeclared ACAd/ACAv/PL/ILA composite**, including exact laminar descendants on one probe. MOs, orbital cortex, other regions and other probes are excluded. This changes the P14 estimand explicitly; it does not repair the original IBL/PFC coverage failure or imply a uniform fine-region effect. All four leaves are reported independently.

Minimum10 provider-good simultaneous units is an engineering feasibility screen for future fixed 2D, 20-coefficient readouts, not a power or physiological guarantee. Each context requires >=60 usable trials in each chronological whole-block half, >=2 qualifying runs overall and >=15 valid trials per contributing run. These are new source-specific rules, not inherited8/120 or20/400 thresholds. For clarity, the proposed half-second window contains five 100-ms bins: 60 trials provide **300 bins per context per half** and 120 trials provide 600 in total, before unit multiplicity. This restates the original registration arithmetic; no threshold, window, criterion or registration byte changed. The rejected r1 report incorrectly called that registration arithmetic an error; the original report and review are preserved.

## Coverage, including negative routes

| Source | Original independent denominator | Registered paired-context result | Interpretation |
|---|---:|---:|---|
| IBL original BWM snapshot |139mice;459sessions;699probes |8mPFC-composite mice |Below16; physiology/support still unconfirmed |
| KI001260 |41canonical mice;50sessions;74probes;43raw subject labels |Context-task global ceiling8; within-task labels/quality unresolved |Do not pool different tasks/sessions to manufacture paired contexts |
| AIND Dynamic Routing |85catalog mice;263sessions |34behavior-passing brainwide mice;18paired mPFC candidates |Capacity for8+8 before physiology; critical metadata/source gaps remain |
| Steinmetz2019 |Source-reported10mice;39sessions;92insertions |Regional/context inventory not downloaded |Global ceiling<16; early stop, not zero PFC coverage |

Only two additional datasets were examined. The Steinmetz ceiling and release are supported by the [original study](https://www.nature.com/articles/s41586-019-1787-x) and [provider Figshare metadata](https://api.figshare.com/v2/articles/9598406). Its8.86GB neural/behavior archive was not downloaded. Its retrospective engagement states would also require explicit causality/measurement treatment.

IBL reused the frozen original aggregate and independently checked295920 old/new trial row identities before adding missing behavioral columns. Raw cluster metadata621733; provider-good globally75708. Provider-good is not new neural QC. The [official release documentation](https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html) and [task methods](https://www.nature.com/articles/s41586-025-09226-1) identify uncued prior-probability blocks. Context .2/.8 is the experimenter's schedule, not a measured mouse belief. Neutral .5 and unknown labels break runs before filtering.

KI uses only previously reviewed metadata for [001260/0.250911.0744](https://dandiarchive.org/dandiset/001260/0.250911.0744). Task strata have Attention4, Aversion6, Context8, Detection10, Opto3 and Passive10 independent mice (animal sets can overlap; never sum them). The cross-task overlap table is supplied, but different recording populations are not interchangeable contexts. Canonicalization retains the reviewed518804_1/_2 and560171_1/_2 alias reconciliation; no new identity merging was introduced. Source quality/schema and paired timing remain unknown, not passing. DANDI000473/P13 exposed final results are historical background only.

| Region | IBL raw-anatomical mice | IBL >=10good | IBL paired eligible | DR primary raw-anatomical mice | DR >=10good+coordinates+support | DR paired eligible |
|---|---:|---:|---:|---:|---:|---:|
| ACAd |18|11|6|20|14|14|
| ACAv |14|5|2|13|10|10|
| PL |16|11|6|15|12|12|
| ILA |9|8|4|12|11|11|
| Registered mPFC composite |24|19|8|21|18|18|

No single leaf reaches16DR mice. The composite is an explicit prospective sampling target, not a post-count pooling rescue. Per-mouse leaf composition and all population distributions are saved; most neurons may come from one leaf. Inference would concern this sampling target, not every medial PFC region.

## Dynamic Routing: exact denominator and source limits

The [official Dynamic Routing project](https://www.allenneuraldynamics.org/projects/dynamic-routing) supplies within-session auditory/visual rewarded-modality changes and prefrontal recording coverage. The pinned `dr-datacube` source is `366809a4b2b3f39a7f36e054a4650dd79faadbe2`, package0.1.1, public metadata cachev0.0.289. The five-mouse [capsule examples](https://github.com/AllenNeuralDynamics/conect-dev-capsule/tree/f31033a0a7c603621c5268d1c8138d449e3f9f69) describe task structure; they are not the full cohort denominator.

The263-session catalog has brainwide159sessions/48mice, templeton20/11, naive1/1 and **UNSPECIFIED83/33**. Only brainwide AND provider behavior-pass is primary:82sessions/34mice,420probe observations. Other strata are reported, never admitted. These mouse counts overlap across strata. The decoded cache has337sessions/107mice; **74cached sessions outside the pinned catalog are explicitly excluded**, not silently imported. All82primary sessions match session/trial/unit metadata; no primary session lacks unit records. Across all catalog sessions before behavior/context screening,46mice have target anatomy and42have>=10provider-good target units on one probe.

All18selected candidates have6original blocks (5switches), both reward contexts, the same counted units supported across all retained half-second windows and both halves, and14–378qualified metadata units. The minimum of each mouse's four context-half trial cells is63–81, exceeding the registered60floor. First5 scheduled trials per block are excluded irrespective of later reward/response; no instruction flags occur outside these first5 for the18selected sessions. Planned-opto or unknown-opto trials are excluded. Provider drift flags among selected good units are all true; this does not establish time-resolved neural stationarity. Every per-mouse/context count, block and temporal quartile is in `results/DR_selected_context_coverage.csv` and the complete coverage tables.

Catalog, event and unit mouse/session identities were checked. The same probe's cluster identity is unique. Finite CCFcoordinates and provider QC are required. Provider `obs_intervals` must contain every retained window; malformed, overlapping, missing or nonfinite intervals do not pass. These are recording-support annotations, not spike endpoints or hardware packet-completeness certificates. Original neural clocks and training-only physiology remain future gates.

DR's mutable scratch cache is **not** a fully checksummed immutable neural release. ETags, sizes, pinned provider source and exact decoded-column hashes identify this metadata snapshot. Whole object SHA256 values were not obtained from partial range reads. The exact scratch dataset license remains unresolved: public access and MIT-licensed capsule code are not a data license; a failed LICENSE lookup is retained. Do not claim an external custodian or approved final access architecture.

## Identifiability and future design

Both modalities' contexts contain all four stimulus labels in every selectedDR mouse. Both response and reward Boolean values occur in both contexts. IBL's8selected mice share 9 numeric signed-contrast values (IEEE signed zeros canonicalized to one zero level), both choices and both previous-choice/feedback outcomes. These are marginal support checks, **not matched probabilities, joint overlap, independence or causal identification**. No new overlap cutoff was tuned to admit candidates.

Context changes the reward rule by design. Passage of time/block order, learned expectation, licking/motor execution, reward history, arousal and changes in recording quality can still explain apparent prediction interactions. Measured poststimulus outcomes are descriptive nuisance checks here; future causal predictors may use an event only after its actual timestamp. Continuous running/pupil coverage and alignment have not been established for the exact18sessions. Genotype/sex/experiment-batch balance is not verified; a single selected lab labelNP3 does not remove batch confounding. See `CONTEXT_IDENTIFIABILITY.md` for source-specific measured/partial/unavailable status.

The **one conditional design option**, not an activated recommendation, is DR single-probe ACAd/ACAv/PL/ILA composite, auditory-reward versus visual-reward context, paired within mouse. `PROPOSED_M1_FREEZE.md` specifies the hypotheses, prospective9+9allocation proposal with8+8floor, training-only QC, B0–B4 and finite D/C representations, complexity accounting, difference-of-gains estimand, assumptions, null validation and one-shot final boundary. No effect, likelihood gain or model ranking was computed. There is no assumption that discrete dynamics win.

## Artifacts, reproducibility and review

`SOURCE_REGISTRY.json` supplies release/source/license scopes and recording-identity paths. `results/ALL_Context_Mouse_Region.csv` combines the IBL, DR and unresolved KI tables without turning unknowns into zeros; Steinmetz is explicitly an early-stop source with no invented local cells. `ELIGIBILITY_AND_EXCLUSIONS.md`, `results/EXCLUSIONS_NONEXCLUSIVE.csv`, full probe tables, block tables, missingness tables, unit distributions and composition supply denominators and exclusions. Selected populations are metadata rankings, **not development/final allocation**.

The retrieval journal records74scripted HTTP attempts and17,171,293response bytes, below160attempt/60MBbounds; two failed LICENSE attempts remain preserved. Browser discovery bytes are unavailable and excluded from this measured script total. Only whitelisted anatomy/identity/QC/support/event columns were decoded; full spike tables, NWB fallback, decoder outputs and neural columns were denied. No new dataset search follows the two-candidate limit.

Run `& .\paper14_m0\reproduce.ps1` from the repository root. Saved-only reproduction denies network, verifies original/new metadata and frozen source hashes, runs synthetic metadata/unit tests, independently checks mouse denominators and reruns the complete saved audit in a new directory before byte-comparing deterministic outputs. It does not rerun retrieval or any neural experiment. Early test-fixture failures, the rejected r1 review/report attribution and the descriptive warning/accounting correction are retained in the evidence directory. The signed-zero correction affects descriptive covariate categories only, not eligibility, anatomical counts, trial masks or the 18/8 mouse denominators. A new regression preserves missing contrast as unknown rather than zero. Provider-good/is_qc_pass is preexisting release-level, potentially full-session curation, not newly calculated C-only physiology. The independent review and final receipts identify the precise tested candidate; review is internal, not external peer review.

P1–P13, old M4 numerical failures, the P13 conditional Bstar failure and previous inconclusive scientific restrictions remain immutable. P13 finalD was exposed and cannot become new P14 confirmation. M0 completion is not completed neuroscience. **STOP after M0.**
