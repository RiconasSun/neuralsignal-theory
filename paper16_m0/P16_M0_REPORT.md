# Paper16 bounded data-first M0 assessment

Mission `P16-VISUAL-CORTEX-DATA-FIRST-M0`. Exact BASE `bf0e948f57dc49d7c315170c67b9911f72d92530`. Scientific feasibility verdict **FEASIBLE_INDEPENDENT_HOLDOUT**. This is an M0 assessment,not a completed paper,physiological admission,model result or confirmatory validation. Engineering closure requires the independent final review and executed Git readback/clean receipt;precommit files do not certify a future SHA.

Primary proposed question **A**,history increment beyond strong causal visual stimulus/rate/time/measured-behavior baselines. B repetition-context differences and C discrete/continuous representations remain prospective secondary possibilities,not active experiments. Title/dataset/hypotheses are not a definitive M1 freeze. The old Transcriptomic/Gene Mapping topic and distinct Closed-Loop roadmap are retained in HISTORICAL_ROADMAP.md.

## Source rights and exact identity

Only CandidateA activated. B/C unassessed,not failed. Official Allen warehouse manifest projected on2026-10-18,all source bodies/queries/SHA256 receipts in metadata/. Exact two NWB file IDs/ETags/byte lengths/currentHEAD are frozen in results/PILOT_OBJECT_FREEZE.json,complete-transfers SHA256 in per-session receipts. Official SDK v2.16.2 source commit a9b5c685396126d9748f1ccecf7c00f440569f69 defines source conventions;actual reader is PyNWB3.1.3,not an executed SDK installation. NWB version/schema compatibility is only established for completed pilots. Last-Modified does not prove release generation.

[Allen terms](https://alleninstitute.org/legal/terms-use/) permit the intended noncommercial research/copying/distribution and attributed academic publication,subject to their conditions,including Freedom to Innovate;commercial redistribution needs separate permission. This is **not CC BY4.0**. [Official registry](https://registry.opendata.aws/allen-brain-observatory/) points to those terms;[citation policy](https://alleninstitute.org/legal/citation-policy/) applies. Data terms are separate from SDK license. No raw-neural Git redistribution or external correspondence. Cite Siegle,Jia,Durand etal.(2021),[Survey of spiking in the mouse visual system reveals functional hierarchy](https://doi.org/10.1038/s41586-020-03171-x),plus Allen dataset/software provenance.

## Actual denominators and anatomy

Source **58 mice/58sessions/332probes/123224channels/135275unfiltered unit IDs**. VISp anatomy in56mice. Do not substitute the tutorial's differently filtered unit denominator. Tiers use same-probe quality good,finite valid-domain metrics,amplitude cutoff<=.1,presence ratio>=.95,ISI violations<=.5,inclusive,and finite positive acquisition rate. Values were registered before first eligibility count;source-validity additions explicitly clarified in revision2 after failed preaccess review,without threshold changes. One invalid probe acquisition rate remains reported;no source-domain invalid metric rows. Whole-session source QC is screening,not future A/C physiological admission.

| Tier units | Mice | Sessions | Probe populations |
|---|---:|---:|---:|
| 12 | 55 | 55 | 56 |
| 20 | 52 | 52 | 53 |
| 5 | 55 | 55 | 56 |
| 8 | 55 | 55 | 56 |

One earliest eligible session per mouse,and maximal qualified VISp probe within it,numeric ties. No probe/session/mouse pooling. Selected55populations contain3615metadata-qualified units,min14,median68,max126. Full tables retain all58mice/all332probes,unselected/excluded rows,IDs,sex/genotype/session type,source eye-tracking flags and available stimulus-family metadata. Official Structure ontology verifies385VISp and all six registered layer descendants,and every used channel structure ID. Atlas/peak-channel membership is a proxy,not histological certainty.

## Prospective roles and contamination boundaries

All26oldP12roster mice conservatively treated exposed;13historical Final mice protected across all sessions. All26source mappings verified against complete session/specimen/donor roster;23overlap the selected55. Historical session protection was repaired to whole-mouse protection before counting. Original failure/cross-session synthetic counterexamples and registration1 remain immutable in evidence. No old worker imported or old neural outcome reopened. P11was a distinct human source;later KI/IBL/other-source tracks do not provide new Allen Visual Coding outcome evidence. Bounded source-history search and conservatism do not establish biological independence across laboratories.

Frozen allocation **28Development/27prospective Final**;all Final are fresh relative to the historical Allen roster. Dev has5BO/23FC;Final27BO. Sex Dev22M/6F,Final22M/5F. Genotype composition remains in all-mouse table. **This is not evidence of IID8+8 within the same protocol.** Proposed primary shared-grating conditional estimand and BO-targeted heldout transport require explicit M1 compatibility/precision rules. No reroll to improve balance after pilot outcomes. Entire pilot mice remain Development. No Final spike access,calibration,QC,scoring or D.

## Bounded real source execution

| Mouse | Session | Probe | Declared bytes | Transfer | Pilot |
|---|---|---|---:|---|---|
| 739783171 | 760345702 | 810753199 | 1960982972 | COMPLETE | COMPLETE |
| 811322619 | 829720705 | 832129154 | 1679648916 | COMPLETE | COMPLETE |

Both objects selected by metadata size before spikeGET;planned3640631888NWBbytes. Payload ledger includes actual newly acquired metadata and conservatively reserves full object bytes before each GET. It never refunds failures/crashes. Exclusive durable attempt prevents duplicate GET;no replacement/retry. Read only first8numeric qualified VISp unit IDs per pilot using lazy PyNWB ragged row access;no other region's spike arrays,no fits or likelihoods. Raw NWB remains ignored local work. Per-unit finite/order/duplicate/binary64 SHA certificates,events/countexamples and complete attempts preserve negative findings.

2/2pilots completed. REAL_SPIKE_PILOT_PASS=True;STIMULUS_SPIKE_ALIGNMENT_PASS=True. Interpretation is curated-release elapsed-clock agreement,not fresh raw/AP or absolute calendar synchronization proof. See alignment and source-compatibility reports for exact successful and failed panels.

## Stimulus and strong-baseline feasibility

| Session | Native family | Valid/original | Conditions | Repeated conditions | Repetitions minâ€“max |
|---|---|---:|---:|---:|---:|
| 760345702 | drifting_gratings_presentations | 630/630 | 41 | 41 | 15â€“30 |
| 760345702 | flashes_presentations | 150/150 | 2 | 2 | 75â€“75 |
| 760345702 | gabors_presentations | 3645/3645 | 243 | 243 | 15â€“15 |
| 760345702 | natural_movie_one_presentations | 18000/18000 | 900 | 900 | 20â€“20 |
| 760345702 | natural_movie_three_presentations | 36000/36000 | 3600 | 3600 | 10â€“10 |
| 760345702 | natural_scenes_presentations | 5950/5950 | 119 | 119 | 50â€“50 |
| 760345702 | spontaneous_presentations | 15/15 | 1 | 1 | 15â€“15 |
| 760345702 | static_gratings_presentations | 6000/6000 | 121 | 121 | 44â€“189 |
| 829720705 | dot_motion_presentations | 420/420 | 28 | 28 | 15â€“15 |
| 829720705 | drifting_gratings_75_repeats_presentations | 600/600 | 8 | 8 | 75â€“75 |
| 829720705 | drifting_gratings_contrast_presentations | 540/540 | 36 | 36 | 15â€“15 |
| 829720705 | flashes_presentations | 150/150 | 2 | 2 | 75â€“75 |
| 829720705 | gabors_presentations | 3645/3645 | 243 | 243 | 15â€“15 |
| 829720705 | natural_movie_one_more_repeats_presentations | 54000/54000 | 900 | 900 | 60â€“60 |
| 829720705 | natural_movie_one_shuffled_presentations | 18000/18000 | 900 | 900 | 20â€“20 |
| 829720705 | spontaneous_presentations | 6/6 | 1 | 1 | 6â€“6 |

Full family table and per-pilot JSON retain every native family,condition scalar columns/values,repeats,original IDs/order,positive gaps/overlap,durations,blank/NaN parameters,first64valid examples and behavior missingness. Condition metadata str is not causal timestamp serialization;all native start/stop/ID arrays are lossless npz. Nonpilot family presence is source metadata only;their trial/physiological coverage is untested.

Gratings offer orientation/contrast/frequency/phase and onset/offset controls;gabors need position/size;static/natural images need exact image identity;movies require frame/repeat/order and adaptation/drift controls;motion requires direction/speed. Strong B1 must handle these and measured running/pupil availability before attributing any increment to local history. A future movie frame is online only if its predetermined schedule is actually available;otherwise an analysis is offline conditional. Missing behavior cannot be filled with future samples or indefinitecarryforward. No family was selected on neural scores.

## Scientific scope and stopping decision

M0 no B0-B4/D/C/S fitting,hyperparameter selection,null simulation,effect size,power,heldout likelihood or numerical-convergence assessment. The21synthetic regression tests validate source/time/access primitives,not model scientific acceptance. Eight+eight and20aspirational are metadata-capacity concepts,not power/admission guarantees. Future M1 must freeze exact physiological,quantitative precision,causal feature,numerical,inference and falsification rules before model outcomes. No P15 bins/horizons/features/grid/solver thresholds copied. No P13 unstable B* null reused. Single source/recording-anatomy/curated-support/protocol/sex/genotype/behavior limitations remain. No mechanism,independent-lab replication,discrete superiority,confirmation or CWP/NAP claim.

PROMPT_2_READY=True,conditional only on separately authorized complete M1 registration;no automatic activation. Stop after reviewed M0 archive. Saved-only command: `& .\paper16_m0\reproduce_saved.ps1`;it validates source metadata,archived certificates/native events/count aggregates and synthetic regressions,never redownloads or reopens real spike NWB. Source execution and saved-results reproduction are separate evidence levels.

## Cross-protocol stimulus identity boundary

Saved real-pilot metadata confirms four shared (orientation,temporal_frequency,spatial_frequency,contrast) tuples: orientations0/45/90/135degrees,2Hz,0.04cycles/degree,contrast0.8. This is partial parameter support,not complete physical-stimulus equivalence or Final coverage. BO grating table has630presentations;FC75-repeat table600 and contrast table540. The released phase field contains large constant vector values that differ by table. It is retained as source metadata and **not interpreted as verified phase at onset**. Future M1 must validate phase/condition/PSTH controls and source semantics before attributing history gain beyond strong measured stimulus baselines. No phase repair,clock correction or extra experiment was performed. Source-file and original parameter values remain immutable. See results/COMMON_GRATING_PARAMETER_SUPPORT.json.

Pupil is available in both pilots but nonfinite ellipse-fit values occur41774/287764(14.52%) and23816/299738(7.95%). Running values are finite in364957/366223source intervals;strict native positive gap counts183221/183215 include arbitrarily small positive separations and are **not dropout counts** or proof of complete coverage. No tolerance,imputation or future sample was introduced. Future M1 needs explicit causal covariate support/missingness rules.

## Saved-only integrity repair

Initial21synthetic source/time/access tests remain preserved. Final saved-only reproduction now has27tests,including6negative integrity regressions. It requires the exact complete74file scientific package and recomputes source denominators/tiers/roles/size-selected pilots,mouse/probe/stimulus tables,attempt-transfer-certificate/event/count links,common grating support and all quantitative status gates. Empty/incomplete manifests and99999/false status counterexamples are rejected. It checks saved count aggregates/certificates;it does not independently recount raw spikes from absent raw NWB. Original failed reproduction/review/counterexample preserved;no real pilot/model/Final replay.

Both pilots also have150uniform flashes:two colors(-1,+1),75presentations each,matching source parameter records including zero phase vectors. This offers an interpretable phase-independent strong-baseline design route for proposed questionA within the original registered family assessment. It is not a new experiment or result-driven activation;M1must separately choose/freeze its final stimulus estimand and precision.
